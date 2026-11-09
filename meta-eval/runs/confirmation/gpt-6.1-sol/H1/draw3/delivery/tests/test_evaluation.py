import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evaluate
import stages
from inspect_state import inspect, fault
from oracle import Model, advance, batches, compare_snapshot, valid_reply
from tests.controls import answer, BAD


class OracleTests(unittest.TestCase):
    def test_both_serial_outcomes(self):
        requests = next(batches("x"))[1]
        for replies, winner in (([{"status": "accepted", "remaining": 40},
                                 {"status": "rejected", "remaining": 40}], 0),
                                ([{"status": "rejected", "remaining": 40},
                                  {"status": "accepted", "remaining": 40}], 1)):
            model = advance(Model(), requests, replies)
            self.assertEqual(model.accounts, {"A": 40, "B": 100})
            self.assertEqual(list(model.ledger), [requests[winner]["key"]])

    def test_double_accept_and_double_reject_fail(self):
        requests = next(batches("x"))[1]
        for status in ("accepted", "rejected"):
            with self.assertRaises(ValueError):
                advance(Model(), requests, [{"status": status, "remaining": 40}] * 2)

    def test_global_identity_and_historical_rejection(self):
        model = Model()
        left = {"key": "left", "account": "A", "amount": 60}
        rejected = dict(left, key="rejected")
        model.apply(left)
        historical = model.apply(rejected)
        model.apply(dict(left, key="tail", amount=40))
        before = copy.deepcopy(model.snapshot())
        self.assertEqual(model.apply(rejected), historical)
        self.assertEqual(model.apply(left), {"status": "accepted", "remaining": 40})
        for request in (dict(rejected, account="B"), dict(left, amount=61)):
            self.assertEqual(model.apply(request), {"status": "payload_mismatch", "remaining": None})
        self.assertEqual(model.snapshot(), before)

    def test_exact_reply_contract(self):
        for value in ({"status": "accepted", "remaining": True},
                      {"status": "accepted", "remaining": 40.0},
                      {"status": "accepted", "remaining": -1},
                      {"status": "payload_mismatch", "remaining": 0},
                      {"status": "rejected", "remaining": 0, "extra": 1}, [], None):
            self.assertFalse(valid_reply(value))

    def test_every_public_table_is_compared(self):
        model = Model()
        for table in ("accounts", "decisions", "ledger"):
            observed = model.snapshot()
            observed[table].append({"unwanted": "row"})
            with self.assertRaises(ValueError):
                compare_snapshot(model, observed)


class SimulatedSandbox:
    """Harness tests only. Runs a trusted model, never candidate Python."""
    def __init__(self, directory, defect=None, reverse=False):
        self.model = Model()
        self.defect = defect
        self.reverse = reverse
        self.injected = False

    def preflight(self):
        pass

    def fault(self, action, event):
        self.injected = action == "install"
        event["fault_" + action] = {"fault": action}

    def batch(self, requests, event, allow_error=False):
        if self.injected:
            if self.defect == "partial_commit":
                self.model.accounts["B"] = 0
            if self.defect == "error_decision":
                raise evaluate.CandidateFailure("database error was reported as a business decision")
            return None
        replies = [None] * len(requests)
        order = reversed(range(len(requests))) if self.reverse else range(len(requests))
        for index in order:
            request = requests[index]
            if self.defect == "historical" and request["key"] in self.model.decisions:
                replies[index] = self.model.apply(request)
                if replies[index]["status"] != "payload_mismatch":
                    replies[index]["remaining"] = self.model.accounts[request["account"]]
            else:
                replies[index] = self.model.apply(request)
        event["replies"] = replies
        if self.defect == "lost_rejection":
            self.model.decisions = {k: v for k, v in self.model.decisions.items() if v["status"] != "rejected"}
        if self.defect == "missing_ledger":
            self.model.ledger.clear()
        if self.defect == "double_accept" and event["name"] == "overlap":
            replies[1] = {"status": "accepted", "remaining": 40}
        return replies

    def inspect(self, event):
        snapshot = self.model.snapshot()
        event["inspection"] = {"snapshot": snapshot}
        return snapshot


class HarnessTests(unittest.TestCase):
    def test_three_repetitions_both_winners(self):
        for reverse in (False, True):
            status, repetitions, reason = evaluate.exercise(
                lambda directory: SimulatedSandbox(directory, reverse=reverse), "control")
            self.assertEqual(status, "passed")
            self.assertIsNone(reason)
            self.assertEqual(len(repetitions), 3)
            self.assertEqual([len(r["checks"]) for r in repetitions], [13] * 3)

    def test_negative_controls(self):
        for defect, expected in (("double_accept", "overlap"),
                                 ("lost_rejection", "overlap"),
                                 ("missing_ledger", "overlap"),
                                 ("historical", "historical_replays"),
                                 ("partial_commit", "database_error_rollback"),
                                 ("error_decision", "database_error_rollback")):
            with self.subTest(defect=defect):
                status, repetitions, _ = evaluate.exercise(
                    lambda directory: SimulatedSandbox(directory, defect=defect), "control")
                self.assertEqual(status, "failed")
                failures = [c["name"] for c in repetitions[0]["checks"] if c.get("status") == "failed"]
                self.assertIn(expected, failures)

    def test_alternative_is_not_executed_or_scored(self):
        with patch.object(evaluate, "exercise", side_effect=AssertionError("must not run")):
            result = evaluate.grade({"task_id": "E1", "alternative_format": True,
                                     "alternative": "Per-account actor with durable deduplication.",
                                     "explanation": "Needs independent architectural review."})
        self.assertEqual(result["status"], "review_required")
        self.assertEqual(result["formal_status"], "not_run")

    def test_explanation_is_not_graded_by_presence(self):
        with patch.object(evaluate, "exercise", return_value=("passed", [], None)):
            result = evaluate.grade(answer())
        self.assertEqual(result["overall_status"], "formal_pass_review_pending")
        self.assertEqual(result["explanation_status"], "review_pending")

    def test_invalid_answers(self):
        for value in ([], {}, dict(answer(), task_id="E2"), dict(answer(), code=1),
                      dict(answer(), explanation=" "), dict(answer(), alternative_format="true"),
                      dict(answer(), alternative_format=True, alternative="")):
            with patch.object(evaluate, "exercise", side_effect=AssertionError("must not run")):
                self.assertEqual(evaluate.grade(value)["status"], "invalid")

    def test_unavailability_is_not_failure_or_pass(self):
        class Unsupported(SimulatedSandbox):
            def preflight(self):
                raise evaluate.Unavailable("test environment unsupported")
        with patch.object(evaluate, "Sandbox", Unsupported):
            # Constructor shape differs; use a separate factory at the exercise seam.
            status, _, reason = evaluate.exercise(lambda directory: Unsupported(directory))
        self.assertEqual(status, "unavailable")
        self.assertIn("unsupported", reason)

    def test_strict_json(self):
        for raw in ('{"a":1,"a":2}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                evaluate.parse_json(raw)


class StageTests(unittest.TestCase):
    def test_initial_withholds_reveal_and_seals_first_answer(self):
        initial = stages.start()
        self.assertNotIn("F6.", initial["view"]["prompt"])
        self.assertNotIn("deadlock retries", initial["view"]["prompt"])
        first = {"task_id": "E1", "explanation": "Invalid first answers remain evidence."}
        revealed = stages.reveal(initial, first)
        self.assertIn("F6.", revealed["view"]["prompt"])
        self.assertEqual(revealed["first_answer"], first)
        with patch.object(stages, "grade", return_value={"status": "failed"}):
            result = stages.finish(revealed, answer())
        self.assertEqual(result["staged"]["first_answer"], first)

    def test_tamper_and_wrong_stage_rejected(self):
        initial = stages.start()
        tampered = copy.deepcopy(initial)
        tampered["view"]["prompt"] = "changed"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            stages.reveal(tampered, answer())
        with self.assertRaisesRegex(ValueError, "revealed state"):
            stages.finish(initial, answer())
        revealed = stages.reveal(initial, answer())
        tampered = copy.deepcopy(revealed)
        tampered["first_answer"]["explanation"] = "changed"
        tampered = stages.seal({k: v for k, v in tampered.items() if k != "state_sha256"})
        with self.assertRaisesRegex(ValueError, "lineage"):
            stages.finish(tampered, answer())

    def test_wrong_case_lineage(self):
        revealed = stages.reveal(stages.start(), answer())
        payload = {k: v for k, v in revealed.items() if k != "state_sha256"}
        payload["case_id"] = "other case"
        with self.assertRaisesRegex(ValueError, "lineage"):
            stages.finish(stages.seal(payload), answer())


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self.directory.name) / "ledger.sqlite")
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.executescript('''
                CREATE TABLE accounts(account TEXT PRIMARY KEY, remaining INTEGER);
                CREATE TABLE decisions(key TEXT PRIMARY KEY, account TEXT, amount INTEGER,
                    status TEXT, remaining INTEGER);
                CREATE TABLE ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
                INSERT INTO accounts VALUES ('A',100),('B',100);
            ''')

    def tearDown(self):
        self.directory.cleanup()

    def test_valid_tables_and_fault_installation(self):
        self.assertEqual(inspect(self.path), Model().snapshot())
        fault(self.path, "install")
        with closing(sqlite3.connect(self.path)) as connection, connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO ledger VALUES ('x','A',1)")
        fault(self.path, "remove")
        self.assertEqual(inspect(self.path), Model().snapshot())

    def test_view_not_allowed(self):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.executescript("DROP TABLE ledger; CREATE VIEW ledger AS SELECT 'x' AS key,'A' AS account,1 AS amount;")
        with self.assertRaisesRegex(ValueError, "real table"):
            inspect(self.path)

    def test_wrong_schema_not_allowed(self):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.executescript("DROP TABLE ledger; CREATE TABLE ledger(key TEXT,account TEXT,amount INTEGER);")
        with self.assertRaisesRegex(ValueError, "primary key"):
            inspect(self.path)

    def test_row_cap(self):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.executemany("INSERT INTO ledger VALUES (?,'A',1)", [(str(i),) for i in range(100)])
        with self.assertRaisesRegex(ValueError, "row limit"):
            inspect(self.path)

    def test_stored_type(self):
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("UPDATE accounts SET remaining='bad' WHERE account='A'")
        with self.assertRaisesRegex(ValueError, "stored SQLite type"):
            inspect(self.path)

    @unittest.skipUnless(sys.platform == "linux", "symlink permissions vary on Windows")
    def test_symlink_sidecar(self):
        Path(self.path + "-wal").symlink_to("/etc/passwd")
        with self.assertRaisesRegex(ValueError, "regular files"):
            inspect(self.path)


@unittest.skipUnless(sys.platform == "linux", "live candidate execution requires Linux isolation")
class SandboxIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            try:
                evaluate.Sandbox(directory, "").preflight()
            except evaluate.Unavailable as error:
                raise unittest.SkipTest(str(error))

    def test_authored_service_and_defective_controls(self):
        result = evaluate.grade(answer())
        self.assertEqual(result["status"], "passed", json.dumps(result, indent=2))
        for name, source in BAD.items():
            with self.subTest(control=name):
                result = evaluate.grade(answer(source))
                self.assertEqual(result["status"], "failed", json.dumps(result, indent=2))

    def test_hang_output_flood_import_failure_and_crash(self):
        controls = [
            'class Service:\n def __init__(self,p):\n  while True: pass',
            'print("x"*70000)\nclass Service: pass',
            'raise RuntimeError("import failed")',
            'import os\nos._exit(12)',
        ]
        for source in controls:
            self.assertEqual(evaluate.grade(answer(source))["status"], "failed")

    def test_sandbox_has_no_workspace_or_environment_secrets(self):
        # Candidate assertions execute only inside the production sandbox.
        source = '''import os, socket
assert "E1_TEST_SECRET" not in os.environ
assert not os.path.exists("/oracle.py")
assert not os.path.exists("/evaluate.py")
assert not os.path.exists("/input/E1.md")
assert not os.path.exists("/inspect_state.py")
try:
    open("/worker.py", "a").write("bad")
    raise AssertionError("worker is writable")
except OSError:
    pass
try:
    socket.create_connection(("1.1.1.1", 80), timeout=0.1)
    raise AssertionError("network reachable")
except OSError:
    pass
'''
        with patch.dict("os.environ", {"E1_TEST_SECRET": "must-not-leak"}):
            self.assertEqual(evaluate.grade(answer(source + answer()["code"]))["status"], "passed")


if __name__ == "__main__":
    unittest.main()
