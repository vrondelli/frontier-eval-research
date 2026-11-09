"""Portable oracle/harness tests use ONLY authored controls, never user submissions.

Real isolated execution tests skip if the declared Linux runtime is unavailable.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
import threading
import unittest
from unittest.mock import patch

import controls
import evaluate
import stages
from inspect_db import inspect
from oracle import Model, branches, match_pair, match_sequence
from sandbox import CandidateError, Unavailable, available


class TrustedFixtureWorker:
    """Test-only synchronous adapter. No production fallback uses this class."""
    barrier = []

    def __init__(self, source, state):
        scope = {}
        # ONLY generated authored controls are ever provided by the tests below.
        exec(Path(source).read_text(encoding="utf-8"), scope)
        self.service = scope["Service"](str(state / "ledger.sqlite"))
        self.queue = [{"event": "ready"}]

    def send(self, value):
        if value["op"] == "arm":
            self.request = value["request"]
            self.queue.append({"event": "armed"})
            self.barrier.append("arm")
        else:
            self.barrier.append(value["op"])
            item = self.request if value["op"] == "go" else value["request"]
            try:
                self.queue.append({"event": "reply", "value": self.service.apply(item)})
            except Exception as exc:
                self.queue.append({"event": "error", "type": type(exc).__name__})

    def receive(self, deadline=None):
        return self.queue.pop(0)

    def close(self):
        return {"returncode": 0, "test_only_synchronous_adapter": True}


def trusted_case(answer, case):
    with TemporaryDirectory(dir=evaluate.ROOT) as directory:
        root = Path(directory)
        source = root / "candidate.py"
        source.write_text(answer["code"], encoding="utf-8")
        with patch.object(evaluate, "Worker", TrustedFixtureWorker), \
             patch.object(evaluate, "read_state", lambda state: inspect(state / "ledger.sqlite")):
            return evaluate.run_case(source, root / "state", case)


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.pair = [evaluate.request("x"), evaluate.request("y")]

    def test_both_race_winners_allowed(self):
        for branch in branches(self.pair):
            self.assertTrue(match_pair(self.pair, branch["replies"], branch["model"].snapshot()))
            self.assertEqual(sorted(reply["status"] for reply in branch["replies"]), ["accepted", "rejected"])
            self.assertEqual(branch["model"].accounts, {"A": 40, "B": 100})

    def test_rejection_history_survives_later_spend(self):
        model = Model()
        model.apply(self.pair[0])
        decision = model.apply(self.pair[1])
        model.apply(evaluate.request("drain", amount=40))
        self.assertEqual(model.apply(self.pair[1]), decision)
        self.assertEqual(decision, {"status": "rejected", "remaining": 40})
        self.assertEqual(model.accounts["A"], 0)

    def test_conflicts_never_change_state(self):
        for amount in (60, 101):
            model = Model()
            original = evaluate.request("key", amount=amount)
            model.apply(original)
            before = model.snapshot()
            for changed in (evaluate.request("key", amount=amount + 1),
                            evaluate.request("key", "B", amount)):
                self.assertEqual(model.apply(changed), {"status": "payload_mismatch", "remaining": None})
                self.assertEqual(model.snapshot(), before)

    def test_same_key_branches(self):
        for second in (evaluate.request("key"), evaluate.request("key", amount=80),
                       evaluate.request("key", "B")):
            for branch in branches([evaluate.request("key"), second]):
                self.assertEqual(len(branch["model"].ledger), 1)
                self.assertEqual(len(branch["model"].decisions), 1)

    def test_forged_reply_and_tampered_ledger_rejected(self):
        for branch in branches(self.pair):
            snapshot = branch["model"].snapshot()
            self.assertFalse(match_pair(self.pair, [{"status": "accepted", "remaining": 40}] * 2, snapshot))
            snapshot["ledger"] = []
            self.assertFalse(match_pair(self.pair, branch["replies"], snapshot))

    def test_reply_must_match_its_own_serial_state(self):
        first, second = branches(self.pair)
        self.assertFalse(match_pair(self.pair, first["replies"], second["model"].snapshot()))

    def test_boolean_integer_and_real_are_distinct(self):
        branch = branches(self.pair)[0]
        for wrong in (True, 40.0):
            replies = [dict(reply) for reply in branch["replies"]]
            replies[0]["remaining"] = wrong
            self.assertFalse(match_pair(self.pair, replies, branch["model"].snapshot()))

    def test_extra_state_and_mutated_decision_rejected(self):
        branch = branches(self.pair)[0]
        snapshot = branch["model"].snapshot()
        snapshot["decisions"][1][-1] = 0
        self.assertFalse(match_pair(self.pair, branch["replies"], snapshot))
        snapshot = branch["model"].snapshot()
        snapshot["accounts"].append(["C", 100])
        self.assertFalse(match_pair(self.pair, branch["replies"], snapshot))

    def test_insufficient_first_request_is_a_durable_decision(self):
        model = Model()
        reply = model.apply(evaluate.request("too-large", amount=101))
        self.assertEqual(reply, {"status": "rejected", "remaining": 100})
        self.assertEqual(len(model.decisions), 1)
        self.assertEqual(model.ledger, {})


class HarnessTests(unittest.TestCase):
    def test_authored_reference_all_scenarios(self):
        for case in evaluate.scenarios():
            with self.subTest(case=case["name"]):
                report = trusted_case(controls.answers()["reference"], case)
                self.assertEqual(report["status"], "pass", report)
                self.assertEqual(len(report["checkpoints"]), 3)
        self.assertEqual(TrustedFixtureWorker.barrier[:4], ["arm", "arm", "go", "go"])

    def test_each_defective_control_fails(self):
        for name, answer in controls.answers().items():
            if name in ("reference", "alternative"):
                continue
            with self.subTest(control=name):
                report = trusted_case(answer, evaluate.scenarios()[0])
                self.assertEqual(report["status"], "fail", report)

    def test_alternative_does_not_execute(self):
        with patch.object(evaluate, "available", side_effect=AssertionError("must not execute")):
            report = evaluate.evaluate(controls.answers()["alternative"])
        self.assertEqual(report["formal_status"], "review_required")

    def test_unavailable_never_runs_candidate(self):
        answer = {"task_id": "E1", "code": 'raise RuntimeError("MUST NOT EXECUTE")', "explanation": "text"}
        with patch.object(evaluate, "available", side_effect=Unavailable("unsupported")), \
             patch.object(evaluate, "Worker", side_effect=AssertionError("must not execute")):
            report = evaluate.evaluate(answer)
        self.assertEqual(report["formal_status"], "unavailable")

    def test_invalid_envelopes(self):
        valid = controls.answers()["reference"]
        for answer in (None, [], {}, {**valid, "task_id": "E2"}, {**valid, "explanation": ""},
                       {**valid, "code": "class broken("}, {**valid, "alternative_format": "yes"}):
            with self.subTest(answer_type=type(answer).__name__):
                self.assertEqual(evaluate.evaluate(answer)["formal_status"], "invalid")

    def test_transport_rejects_ambiguous_json(self):
        for text in ('{"task_id":"E1","task_id":"E2"}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                evaluate.strict_json(text)

    def test_protocol_error_is_not_business_rejection(self):
        class Broken(TrustedFixtureWorker):
            def send(self, value):
                if value["op"] == "go":
                    self.queue.append({"event": "error", "message": "database locked"})
                else:
                    super().send(value)
        with TemporaryDirectory(dir=evaluate.ROOT) as directory:
            root = Path(directory)
            source = root / "candidate.py"
            source.write_text(controls.answers()["reference"]["code"], encoding="utf-8")
            with patch.object(evaluate, "Worker", Broken):
                report = evaluate.run_case(source, root / "state", evaluate.scenarios()[0])
        self.assertEqual(report["status"], "fail")
        self.assertIn("apply failed", report["error"])


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(dir=evaluate.ROOT)
        self.root = Path(self.directory.name)
        self.path = self.root / "ledger.sqlite"

    def tearDown(self):
        self.directory.cleanup()

    def reference(self):
        scope = {}
        exec(controls.REFERENCE.read_text(encoding="utf-8"), scope)
        return scope["Service"](str(self.path))

    def test_real_sql_and_subprocess_inspection(self):
        service = self.reference()
        item = evaluate.request("accepted")
        service.apply(item)
        model = Model()
        model.apply(item)
        self.assertEqual(inspect(self.path), model.snapshot())
        self.assertEqual(evaluate.read_state(self.root), model.snapshot())

    def test_real_threaded_reference_race(self):
        scope = {}
        exec(controls.REFERENCE.read_text(encoding="utf-8"), scope)
        services = [scope["Service"](str(self.path)) for _ in range(2)]
        pair = [evaluate.request("x"), evaluate.request("y")]
        barrier = threading.Barrier(2)
        def apply(i):
            barrier.wait(timeout=5)
            return services[i].apply(pair[i])
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(apply, range(2)))
        self.assertTrue(match_pair(pair, replies, inspect(self.path)))

    def test_views_cannot_spoof_tables(self):
        self.reference()
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE ledger")
            db.execute("CREATE VIEW ledger AS SELECT key,account,amount FROM decisions")
        db.close()
        with self.assertRaisesRegex(ValueError, "real table"):
            inspect(self.path)

    def test_missing_pk_rejected(self):
        self.reference()
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE ledger")
            db.execute("CREATE TABLE ledger(key TEXT,account TEXT,amount INTEGER)")
        db.close()
        with self.assertRaisesRegex(ValueError, "primary key"):
            inspect(self.path)

    def test_extra_implementation_columns_allowed(self):
        self.reference()
        with sqlite3.connect(self.path) as db:
            db.execute("ALTER TABLE ledger ADD COLUMN nonvirtual_note TEXT")
        db.close()
        self.assertEqual(inspect(self.path), Model().snapshot())

    def test_inspection_row_bound(self):
        self.reference()
        with sqlite3.connect(self.path) as db:
            db.executemany("INSERT INTO ledger VALUES (?,?,?)", [(str(i), "A", 1) for i in range(100)])
        db.close()
        with self.assertRaisesRegex(ValueError, "row bound"):
            inspect(self.path)

    def test_missing_or_corrupt_database(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            inspect(self.path)
        self.path.write_bytes(b"not a database")
        with self.assertRaises(sqlite3.DatabaseError):
            inspect(self.path)

    def test_symlink_rejected_if_supported(self):
        target = self.root / "other.sqlite"
        target.write_bytes(b"")
        try:
            self.path.symlink_to(target)
        except OSError:
            self.skipTest("symlink creation unavailable on host")
        with self.assertRaisesRegex(ValueError, "non-symlink"):
            inspect(self.path)


class IsolatedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            available()
        except Unavailable as exc:
            raise unittest.SkipTest(str(exc))

    def test_all_authored_controls_in_real_sandbox(self):
        for name, answer in controls.answers().items():
            with self.subTest(control=name):
                expected = "pass" if name == "reference" else "review_required" if name == "alternative" else "fail"
                self.assertEqual(evaluate.evaluate(answer)["formal_status"], expected)


class StageTests(unittest.TestCase):
    def test_reveal_seals_first_answer_and_withholds_hot_account(self):
        state = stages.start()
        self.assertNotIn("F6.", state["view"])
        self.assertNotIn("deadlock", state["view"])
        for i in range(1, 6):
            self.assertIn(f"F{i}.", state["view"])
        first = controls.answers()["alternative"]
        revealed = stages.reveal(state, first)
        self.assertEqual(revealed["first_answer_sha256"], stages.digest(first))
        self.assertIn("F6.", revealed["view"])
        result = stages.finish(revealed, first)
        self.assertEqual(result["formal_status"], "review_required")
        self.assertEqual(result["staging"]["first_answer"], first)

    def test_invalid_first_output_is_retained(self):
        first = {"bad": "response"}
        revealed = stages.reveal(stages.start(), first)
        result = stages.finish(revealed, controls.answers()["alternative"])
        self.assertEqual(result["staging"]["first_answer"], first)

    def test_state_tampering_and_wrong_phase_rejected(self):
        state = stages.start()
        with self.assertRaises(ValueError):
            stages.reveal({**state, "view": "changed"}, {})
        revealed = stages.reveal(state, {"original": "answer"})
        with self.assertRaises(ValueError):
            stages.reveal(revealed, {})
        changed = {**revealed, "first_answer": {"different": "answer"}}
        # Even a rehashed outer state must satisfy first-response and fixed-view bindings.
        changed = stages.seal({k: v for k, v in changed.items() if k != "state_sha256"})
        with self.assertRaises(ValueError):
            stages.finish(changed, controls.answers()["alternative"])


if __name__ == "__main__":
    unittest.main()
