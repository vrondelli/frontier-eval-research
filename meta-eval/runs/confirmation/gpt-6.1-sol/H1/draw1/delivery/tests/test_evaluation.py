from contextlib import closing
import copy
import json
import os
import queue
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import staged
from controls.fixtures import EXPLANATION, NEGATIVE_CONTROLS, source
from e1eval.cli import evaluate, load_answer, validate_answer
from e1eval.isolation import Unavailable, Worker, preflight, sandbox_command
from e1eval.oracle import ContractError, Model, check_reply, check_snapshot, inspect_database, overlap_model
from e1eval.suite import run_trial
from tests.trusted_transport import TrustedWorker


class OracleTests(unittest.TestCase):
    def test_both_serial_winners(self):
        requests = [{"key": "one", "account": "A", "amount": 60},
                    {"key": "two", "account": "A", "amount": 60}]
        for winner in (0, 1):
            replies = [{"status": "rejected", "remaining": 40} for _ in requests]
            replies[winner] = {"status": "accepted", "remaining": 40}
            model, order = overlap_model(requests, replies)
            self.assertEqual(order[0], winner)
            self.assertEqual(model.accounts["A"], 40)
        for replies in ([{"status": "accepted", "remaining": 40}] * 2,
                        [{"status": "rejected", "remaining": 100}] * 2):
            with self.assertRaises(ContractError):
                overlap_model(requests, replies)

    def test_strict_json_reply(self):
        for reply in ({"status": "accepted", "remaining": True},
                      {"status": "accepted", "remaining": 1.0},
                      {"status": "accepted", "remaining": 1, "extra": 0},
                      None, "accepted"):
            with self.assertRaises(ContractError):
                check_reply(reply, {"status": "accepted", "remaining": 1})

    def test_historical_rejection_and_global_key(self):
        model = Model()
        model.apply({"key": "first", "account": "A", "amount": 60})
        req = {"key": "reject", "account": "A", "amount": 60}
        original = model.apply(req)
        model.apply({"key": "drain", "account": "A", "amount": 40})
        self.assertEqual(model.apply(req), original)
        self.assertEqual(original, {"status": "rejected", "remaining": 40})
        before = copy.deepcopy(model.snapshot())
        self.assertEqual(model.apply({**req, "account": "B"}),
                         {"status": "payload_mismatch", "remaining": None})
        check_snapshot(model.snapshot(), before)


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.database = Path(self.temp.name) / "ledger.sqlite"
        namespace = {}
        exec(source("reference"), namespace)
        self.service = namespace["Service"](str(self.database))

    def tearDown(self):
        self.temp.cleanup()

    def test_independent_state_and_missing_ledger(self):
        model = Model()
        request = {"key": "x", "account": "A", "amount": 100}
        check_reply(self.service.apply(request), model.apply(request))
        check_snapshot(inspect_database(self.database), model.snapshot())
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("DELETE FROM ledger")
        with self.assertRaises(ContractError):
            check_snapshot(inspect_database(self.database), model.snapshot())

    def test_views_are_not_independent_ledger(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("DROP TABLE ledger")
            db.execute("CREATE VIEW ledger AS SELECT key,account,amount FROM decisions")
        with self.assertRaisesRegex(ContractError, "ordinary table"):
            inspect_database(self.database)

    def test_row_bound(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.executemany("INSERT INTO ledger VALUES (?, 'A', 1)", [(str(i),) for i in range(100)])
        with self.assertRaisesRegex(ContractError, "row bound"):
            inspect_database(self.database)

    def test_sidecar_symlink_rejected(self):
        link = Path(str(self.database) + "-journal")
        try:
            link.symlink_to(self.database)
        except OSError:
            self.skipTest("host does not permit symlink creation")
        with self.assertRaisesRegex(ContractError, "regular files"):
            inspect_database(self.database)

    def test_reference_rolls_back_database_errors(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("CREATE TRIGGER reject_ledger BEFORE INSERT ON ledger BEGIN SELECT RAISE(ABORT, 'injected'); END")
        before = inspect_database(self.database)
        with self.assertRaises(sqlite3.Error):
            self.service.apply({"key": "error", "account": "A", "amount": 10})
        check_snapshot(inspect_database(self.database), before)


class EnvelopeTests(unittest.TestCase):
    def test_reply_deadline_is_measured_from_send(self):
        worker = Worker.__new__(Worker)
        worker.events = queue.Queue()
        worker.deadline = time.monotonic() - 1
        worker.events.put((worker.deadline - 0.1, {"event": "result", "reply": {}}))
        self.assertEqual(worker.receive("result")["reply"], {})
        worker.events.put((worker.deadline + 0.1, {"event": "result", "reply": {}}))
        with self.assertRaisesRegex(ContractError, "deadline"):
            worker.receive("result")
        with self.assertRaisesRegex(ContractError, "timed out"):
            worker.receive("result")

    def test_alternative_is_review_required_without_execution(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / "answer.json"
            path.write_text(json.dumps({"task_id": "E1", "alternative_format": True,
                                        "alternative": "A different interface", "explanation": "Review this."}))
            with patch("e1eval.cli.preflight", side_effect=AssertionError("must not run")):
                report = evaluate(path)
            self.assertEqual(report["formal_status"], "not_executed")
            self.assertEqual(report["status"], "review_required")
            self.assertEqual(report["trials"], [])

    def test_invalid_answers(self):
        for answer in ({}, {"task_id": "E2"}, {"task_id": "E1", "code": "pass", "explanation": ""},
                       {"task_id": "E1", "alternative_format": "yes", "explanation": "x"},
                       {"task_id": "E1", "alternative_format": True, "explanation": "x"}):
            with self.assertRaises(ValueError):
                validate_answer(answer)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / "answer.json"
            for raw in ('{"task_id":"E1","task_id":"E2"}', '{"n":NaN}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    load_answer(path)

    def test_unavailable_never_executes_candidate(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / "answer.json"
            marker = Path(directory) / "MUST_NOT_EXIST"
            code = f"from pathlib import Path\nPath({str(marker)!r}).touch()"
            path.write_text(json.dumps({"task_id": "E1", "code": code, "explanation": "x"}))
            with patch("e1eval.cli.preflight", side_effect=Unavailable("test unavailable")):
                report = evaluate(path)
            self.assertEqual(report["formal_status"], "unavailable")
            self.assertFalse(marker.exists())

    def test_sandbox_requires_linux(self):
        with patch("e1eval.isolation.sys.platform", "win32"):
            with self.assertRaises(Unavailable):
                sandbox_command("state", "candidate", "probe")


class StagingTests(unittest.TestCase):
    def test_fixed_reveal_and_binding(self):
        initial = staged.start()
        self.assertNotIn("a few accounts dominate", initial["view"])
        first = json.dumps({"task_id": "E1", "explanation": "First design."}).encode()
        revealed = staged.reveal(initial, first)
        self.assertIn("a few accounts dominate", revealed["view"])
        staged.check_state(revealed, "revealed")
        self.assertEqual(revealed["first_answer"]["explanation"], "First design.")
        revealed["first_answer"]["explanation"] = "Changed"
        with self.assertRaises(ValueError):
            staged.check_state(revealed, "revealed")

    def test_reveal_rejects_changed_initial_view(self):
        state = staged.start()
        state["view"] += "future hint"
        state = staged.seal({k: v for k, v in state.items() if k != "state_sha256"})
        with self.assertRaises(ValueError):
            staged.check_state(state, "initial")


class TrustedControlTests(unittest.TestCase):
    """Real separate processes, using only predeclared authored control names."""

    def test_positive_controls_three_trials_each(self):
        for name in ("reference", "exclusive_valid"):
            for index in range(3):
                with self.subTest(control=name, trial=index), tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
                    report = run_trial(Path(directory), name, TrustedWorker, index)
                    self.assertEqual(report["status"], "pass", report)
                    self.assertEqual(report["barrier"]["armed"], 2)
                    self.assertEqual(len(report["terminal_codes"]), 3)

    def test_negative_controls(self):
        for name in NEGATIVE_CONTROLS:
            with self.subTest(control=name), tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
                report = run_trial(Path(directory), name, TrustedWorker)
                self.assertEqual(report["status"], "fail", report)
                self.assertTrue(report.get("error") or report.get("inspection_error"), report)
                self.assertEqual(report["barrier"]["armed"], 2, report)
                self.assertNotIn("timed out", str(report))


class IsolatedIntegrationTests(unittest.TestCase):
    def test_bubblewrap_controls(self):
        if sys.platform != "linux":
            self.skipTest("Linux bubblewrap required; trusted control tests are separate")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            candidate = root / "candidate.py"
            candidate.write_text(source("reference"), encoding="utf-8")
            probe = root / "probe"
            probe.mkdir()
            try:
                preflight(probe, candidate)
            except Unavailable as exc:
                self.skipTest(str(exc))
            for name in ("reference", "exclusive_valid", *NEGATIVE_CONTROLS):
                candidate.write_text(source(name), encoding="utf-8")
                for index in range(3):
                    with self.subTest(control=name, trial=index):
                        state = root / f"{name}-{index}"
                        state.mkdir()
                        report = run_trial(state, candidate, Worker, index)
                        self.assertEqual(report["status"], "fail" if name in NEGATIVE_CONTROLS else "pass", report)


if __name__ == "__main__":
    unittest.main()

