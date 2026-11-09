import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from evaluation.inspector import inspect
from evaluation.oracle import ContractFailure, Oracle, State, request, schedule
from evaluation.review import CRITERIA, template, validate_review
from evaluation.runner import execute_phase, grade
from evaluation.sandbox import Unavailable, WorkerFailure, decode_json
from evaluation.staging import first_answer_from, reveal, start
from tests.control_service import Service
from tests.make_controls import source


ANSWER = {"task_id": "E1", "code": "class Service: pass", "explanation": "An authored explanation."}


class OracleTests(unittest.TestCase):
    def overlapping(self, reverse=False):
        oracle, state = Oracle(), State()
        requests = [request("left", "A", 60), request("right", "A", 60)]
        replies = [None, None]
        for i in ([1, 0] if reverse else [0, 1]):
            replies[i] = state.apply(requests[i])
        oracle.observe(requests, replies, concurrent=True)
        oracle.inspect(state.snapshot())
        return oracle, state, requests, replies

    def test_both_serial_winners_are_accepted(self):
        self.overlapping(False)
        self.overlapping(True)

    def test_both_accept_or_both_reject_fail(self):
        requests = [request("x", "A", 60), request("y", "A", 60)]
        for status, remaining in [("accepted", 40), ("rejected", 100)]:
            with self.subTest(status=status), self.assertRaises(ContractFailure):
                Oracle().observe(requests, [{"status": status, "remaining": remaining}] * 2, True)

    def test_full_schedule_both_orders(self):
        for reverse in (False, True):
            oracle, state = Oracle(), State()
            for name, requests, concurrent in schedule("test"):
                replies = [None] * len(requests)
                order = reversed(range(len(requests))) if reverse and concurrent else range(len(requests))
                for i in order:
                    replies[i] = state.apply(requests[i])
                oracle.observe(requests, replies, concurrent)
                oracle.inspect(state.snapshot())
            self.assertEqual(state.accounts, {"A": 0, "B": 0})
            self.assertEqual(len(state.ledger), 4)
            self.assertEqual(len(state.decisions), 6)

    def test_rejected_historical_remaining_after_spend(self):
        oracle, state, requests, replies = self.overlapping()
        spend = request("spend", "A", 40)
        oracle.observe([spend], [state.apply(spend)])
        with self.assertRaises(ContractFailure):
            oracle.observe([requests[1]], [{"status": "rejected", "remaining": 0}])
        oracle.observe([requests[1]], [replies[1]])

    def test_accepted_historical_remaining_after_spend(self):
        oracle, state, requests, replies = self.overlapping()
        spend = request("spend", "A", 40)
        oracle.observe([spend], [state.apply(spend)])
        with self.assertRaises(ContractFailure):
            oracle.observe([requests[0]], [{"status": "accepted", "remaining": 0}])
        oracle.observe([requests[0]], [replies[0]])

    def test_global_key_mismatch_changes_nothing(self):
        oracle, state, _, _ = self.overlapping()
        before = state.snapshot()
        oracle.observe([request("left", "B", 60)], [{"status": "payload_mismatch", "remaining": None}])
        oracle.inspect(before)
        altered = copy.deepcopy(before)
        altered["accounts"][1][1] = 40
        with self.assertRaises(ContractFailure):
            oracle.inspect(altered)

    def test_no_reply_only_pass(self):
        oracle, state, _, _ = self.overlapping()
        base = state.snapshot()
        for mutation in ("missing_ledger", "lost_rejection", "rejected_ledger", "wrong_balance", "duplicate_row", "extra_account"):
            bad = copy.deepcopy(base)
            if mutation == "missing_ledger":
                bad["ledger"] = []
            elif mutation == "lost_rejection":
                bad["decisions"] = bad["decisions"][:1]
            elif mutation == "rejected_ledger":
                bad["ledger"].append(["right", "A", 60])
            elif mutation == "wrong_balance":
                bad["accounts"][0][1] = -20
            elif mutation == "duplicate_row":
                bad["ledger"] *= 2
            else:
                bad["accounts"].append(["C", 100])
            with self.subTest(mutation=mutation), self.assertRaises(ContractFailure):
                oracle.inspect(bad)

    def test_reply_shape_and_types(self):
        for reply in ({"status": "accepted", "remaining": True},
                      {"status": "accepted", "remaining": 99.0},
                      {"status": "accepted", "remaining": 99, "extra": 1},
                      {"status": "error", "remaining": None},
                      {"status": "payload_mismatch", "remaining": 99}, None):
            with self.subTest(reply=reply), self.assertRaises(ContractFailure):
                Oracle().observe([request("x", "A", 1)], [reply])


class SQLiteInspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite3"
        Service(self.path)

    def sql(self, statement):
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute(statement)

    def test_trusted_control_against_independent_model(self):
        for reverse in (False, True):
            path = Path(self.temp.name) / f"control-{reverse}.sqlite3"
            oracle = Oracle()
            for _, requests, concurrent in schedule("control"):
                replies = [None] * len(requests)
                order = list(range(len(requests)))
                if concurrent and reverse:
                    order.reverse()
                for i in order:
                    replies[i] = Service(path).apply(requests[i])
                oracle.observe(requests, replies, concurrent)
                oracle.inspect(inspect(path))

    def test_authored_fault_controls_have_the_expected_failure(self):
        expected_phases = {
            "missing_ledger": "overlap", "lost_rejection": "overlap",
            "ignore_mismatch": "amount_mismatch_first", "account_scoped_key": "overlap",
            "historical_remaining": "historical_replays_after_spend",
            "reset_on_init": "overlap", "always_reject": "overlap", "overdraw": "overlap",
        }
        for control, expected in expected_phases.items():
            with self.subTest(control=control):
                # Only our fixed authored control factory is executed here. This is
                # not a path for running user-supplied answers without isolation.
                namespace = {"__name__": "authored_control"}
                exec(compile(source(control), "<authored-control>", "exec"), namespace)
                path = Path(self.temp.name) / f"{control}.sqlite3"
                oracle = Oracle()
                failed_phase = None
                for name, requests, concurrent in schedule("control"):
                    replies = [namespace["Service"](path).apply(item) for item in requests]
                    try:
                        oracle.observe(requests, replies, concurrent)
                        oracle.inspect(inspect(path))
                    except ContractFailure:
                        failed_phase = name
                        break
                self.assertEqual(failed_phase, expected)

    def test_views_cannot_fake_public_tables(self):
        self.sql("DROP TABLE ledger")
        self.sql("CREATE VIEW ledger AS SELECT key,account,amount FROM decisions")
        with self.assertRaisesRegex(ValueError, "real ordinary table"):
            inspect(self.path)

    def test_schema_primary_key_is_checked(self):
        self.sql("DROP TABLE ledger")
        self.sql("CREATE TABLE ledger(key TEXT, account TEXT, amount INTEGER)")
        with self.assertRaisesRegex(ValueError, "primary key"):
            inspect(self.path)

    def test_missing_column(self):
        self.sql("DROP TABLE ledger")
        self.sql("CREATE TABLE ledger(key TEXT PRIMARY KEY, account TEXT)")
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            inspect(self.path)

    def test_row_bound(self):
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.executemany("INSERT INTO ledger VALUES (?, 'A', 1)", [(str(i),) for i in range(100)])
        with self.assertRaisesRegex(ValueError, "row bound"):
            inspect(self.path)

    def test_missing_database_not_created(self):
        absent = Path(self.temp.name) / "absent.sqlite3"
        with self.assertRaisesRegex(ValueError, "database missing"):
            inspect(absent)
        self.assertFalse(absent.exists())

    def test_database_is_opened_read_only(self):
        before = self.path.read_bytes()
        inspect(self.path)
        self.assertEqual(self.path.read_bytes(), before)


class ReportingTests(unittest.TestCase):
    def test_unavailable_never_runs_candidate(self):
        with patch("evaluation.runner.Sandbox", side_effect=Unavailable("no sandbox")):
            result = grade(ANSWER)
        self.assertEqual(result["formal_status"], "unavailable")
        self.assertEqual(result["repetitions"], [])

    def test_alternative_is_review_required_without_execution(self):
        answer = {"task_id": "E1", "alternative_format": True,
                  "alternative": "A transactional partitioned store.", "explanation": "Review it."}
        with patch("evaluation.runner.Sandbox") as sandbox:
            result = grade(answer)
        sandbox.assert_not_called()
        self.assertEqual(result["formal_status"], "review_required")

    def test_invalid_answer(self):
        for answer in ({}, {**ANSWER, "task_id": "E2"}, {**ANSWER, "explanation": ""},
                       {**ANSWER, "code": None}, {**ANSWER, "alternative_format": "true"}):
            self.assertEqual(grade(answer)["formal_status"], "invalid")

    def test_strict_json(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                decode_json(raw)

    def test_review_binding_quotes_and_no_automatic_quality_label(self):
        form = template(ANSWER)
        self.assertTrue(validate_review(ANSWER, form))
        form["reviewer"] = "Example independent reviewer"
        form["independence_declaration"] = "Authored test declaration, not an actual review."
        for entry in form["criteria"].values():
            entry.update(assessment="unsupported", reason="No supporting discussion.")
        self.assertEqual(validate_review(ANSWER, form), [])
        form["criteria"]["atomicity"].update(assessment="supported", quotes=["fabricated quote"])
        self.assertTrue(validate_review(ANSWER, form))
        self.assertTrue(validate_review({**ANSWER, "explanation": "Changed"}, form))

    def test_stages_hide_reveal_then_preserve_first_answer(self):
        initial = start()
        self.assertNotIn("deadlock", initial["view"])
        self.assertNotIn("F6.", initial["view"])
        shown = reveal(initial, copy.deepcopy(ANSWER))
        self.assertIn("F6.", shown["view"])
        self.assertEqual(first_answer_from(shown), ANSWER)
        shown["first_answer"]["code"] = "tampered"
        with self.assertRaises(ValueError):
            first_answer_from(shown)

    def test_barrier_releases_only_after_both_acknowledge(self):
        events = []
        class Channel:
            def __init__(self, number):
                self.number, self.read_count, self.returncode = number, 0, None
            def read(self, deadline=None):
                self.read_count += 1
                events.append((self.number, "read", self.read_count))
                return [{"ready": True}, {"armed": True}, {"reply": {"status": "accepted", "remaining": 0}}][self.read_count - 1]
            def send(self, command):
                events.append((self.number, command["op"]))
            def close(self):
                events.append((self.number, "close"))
            def stop(self):
                self.returncode = 0
        class FakeSandbox:
            def worker(self, state, candidate):
                channel = Channel(len(channels))
                channels.append(channel)
                return channel
        channels = []
        evidence = {}
        execute_phase(FakeSandbox(), None, None, [request("a", "A", 1)] * 2, True, evidence)
        first_go = min(events.index((i, "go")) for i in (0, 1))
        self.assertTrue(all(events.index((i, "read", 2)) < first_go for i in (0, 1)))
        self.assertEqual(evidence["armed"], [0, 1])
        self.assertEqual(evidence["terminal_codes"], [0, 0])


if __name__ == "__main__":
    unittest.main()
