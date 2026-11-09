"""Portable tests run only authored, trusted controls outside the Linux sandbox.

The production CLI has no bypass. One separate test exercises real bubblewrap
when supported; absence is a skip, never an executable correctness pass.
"""
import json
from pathlib import Path
import queue
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import evaluator
from inspector import inspect
from oracle import Model, OVERLAP, compare_trace, expected_trace
import review

ROOT = Path(__file__).resolve().parent
REFERENCE = (ROOT / "examples/reference_service.py").read_text(encoding="utf-8")


def answer(code=REFERENCE):
    return {"task_id": "E1", "code": code, "explanation": "Authored test control, not model performance."}


def trusted_command(state, candidate, probe=False):
    """Only patched inside this test module; never used for supplied answers."""
    assert not probe
    return [sys.executable, "-I", "-B", str(ROOT / "worker.py"), str(candidate), str(state / "ledger.sqlite")]


def trusted_grade(code):
    with patch.object(evaluator.Sandbox, "check", return_value=(True, "TRUSTED CONTROL; NO ISOLATION QUALIFICATION")), \
         patch.object(evaluator.Sandbox, "command", side_effect=trusted_command):
        return evaluator.grade(answer(code))


class OracleTests(unittest.TestCase):
    def test_both_serial_outcomes(self):
        for winner in (0, 1):
            result = compare_trace(expected_trace(winner))
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["overlap_winner"], OVERLAP[winner]["key"])

    def test_overspend_and_both_rejected_fail(self):
        for replies in ([{"status": "accepted", "remaining": 40}] * 2,
                        [{"status": "rejected", "remaining": 100}] * 2):
            trace = expected_trace(0)
            trace[0]["replies"] = replies
            self.assertEqual(compare_trace(trace)["status"], "fail")

    def test_reply_only_success_does_not_pass_wrong_disk(self):
        for table in ("accounts", "decisions", "ledger"):
            trace = expected_trace(0)
            trace[0]["snapshot"][table] = []
            self.assertEqual(compare_trace(trace)["status"], "fail")

    def test_historical_rejection_is_not_current_remaining(self):
        model = Model()
        model.apply(OVERLAP[0])
        rejected = model.apply(OVERLAP[1])
        model.apply({"key": "rest", "account": "A", "amount": 40})
        self.assertEqual(model.apply(OVERLAP[1]), rejected)
        self.assertEqual(rejected, {"status": "rejected", "remaining": 40})

    def test_cannot_mix_serial_histories(self):
        trace = expected_trace(0)
        trace[3] = expected_trace(1)[3]
        self.assertEqual(compare_trace(trace)["status"], "fail")

    def test_partial_or_empty_trace_cannot_pass(self):
        for trace in ([], expected_trace(0)[:1]):
            self.assertEqual(compare_trace(trace)["status"], "fail")
        self.assertEqual(compare_trace(expected_trace(0)[:1], complete=False)["status"], "consistent_prefix")
        self.assertEqual(compare_trace([], complete=False)["status"], "fail")


class InterfaceTests(unittest.TestCase):
    def test_alternative_is_review_required_without_execution(self):
        with patch.object(evaluator.Sandbox, "check", side_effect=AssertionError("must not execute")):
            result = evaluator.grade({"task_id": "E1", "alternative_format": True,
                                      "alternative": "A transactional partitioned service", "explanation": "Review this architecture"})
        self.assertEqual(result["status"], "review_required")

    def test_invalid_answers_do_not_execute(self):
        for value in ([], {}, dict(answer(), task_id="E2"), dict(answer(), explanation=""),
                      dict(answer(), alternative_format="true"), dict(answer(), code="")):
            with patch.object(evaluator.Sandbox, "check", side_effect=AssertionError("must not execute")):
                self.assertEqual(evaluator.grade(value)["status"], "invalid")

    def test_unavailable_has_no_fallback(self):
        with patch.object(evaluator.Sandbox, "check", return_value=(False, "missing sandbox")), \
             patch.object(evaluator, "Worker", side_effect=AssertionError("must not execute")):
            self.assertEqual(evaluator.grade(answer())["status"], "unavailable")

    def test_strict_json(self):
        for value in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                evaluator.strict_json(value)

    def test_reply_validation_types(self):
        for reply in ({"status": "accepted", "remaining": True},
                      {"status": "accepted", "remaining": -1},
                      {"status": "rejected", "remaining": 1.0},
                      {"status": "payload_mismatch", "remaining": 0},
                      {"status": "error", "remaining": None},
                      {"status": "accepted", "remaining": 40, "extra": 1}):
            with self.assertRaises(evaluator.EvaluationError):
                evaluator.validate_reply({"event": "result", "reply": reply})

    def test_reference_json_matches_authored_source(self):
        reference = json.loads((ROOT / "examples/E1.json").read_text(encoding="utf-8"))
        self.assertEqual(reference["code"], REFERENCE)

    def test_reply_deadline_uses_arrival_time(self):
        worker = object.__new__(evaluator.Worker)
        worker.lines = queue.Queue()
        worker.overflow = threading.Event()
        worker.transcript = []
        deadline = time.monotonic() - 1
        worker.lines.put((deadline - 0.1, b'{"event":"ready"}\n'))
        self.assertEqual(worker.receive(deadline), {"event": "ready"})
        worker.lines.put((deadline + 0.1, b'{"event":"ready"}\n'))
        with self.assertRaisesRegex(evaluator.EvaluationError, "six-second"):
            worker.receive(deadline)


class ReviewTests(unittest.TestCase):
    def completed(self):
        submitted = answer()
        form = review.template(submitted)
        form["reviewer_id"] = "authored-control"
        form["independence_declaration"] = "Test fixture only; no actual independent review."
        for item in form["criteria"].values():
            item.update(rating=1, evidence=[{"field": "explanation", "quote": "Authored test control"}], rationale="Test fixture rationale")
        return submitted, form

    def test_bound_form_and_digest_match_grade(self):
        submitted, form = self.completed()
        self.assertEqual(review.validate(submitted, form), [])
        with patch.object(evaluator.Sandbox, "check", return_value=(False, "test")):
            self.assertEqual(evaluator.grade(submitted)["answer_sha256"], form["answer_sha256"])

    def test_changed_answer_or_invented_quote_fails(self):
        submitted, form = self.completed()
        self.assertTrue(review.validate(dict(submitted, explanation="Changed"), form))
        form["criteria"][review.CRITERIA[0]]["evidence"][0]["quote"] = "Never written"
        self.assertTrue(review.validate(submitted, form))

    def test_missing_independence_or_criterion_fails(self):
        submitted, form = self.completed()
        form["independence_declaration"] = ""
        self.assertTrue(review.validate(submitted, form))
        del form["criteria"][review.CRITERIA[0]]
        self.assertTrue(review.validate(submitted, form))

    def test_unfilled_template_is_invalid(self):
        self.assertTrue(review.validate(answer(), review.template(answer())))


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "ledger.sqlite"
        namespace = {}
        exec(REFERENCE, namespace)
        self.service = namespace["Service"](str(self.path))

    def tearDown(self):
        self.service.db.close()
        self.temp.cleanup()

    def test_independent_read(self):
        self.service.apply(OVERLAP[0])
        self.assertEqual(inspect(self.path)["accounts"], [["A", 40], ["B", 100]])

    def test_views_rejected(self):
        self.service.db.execute("DROP TABLE ledger")
        self.service.db.execute("CREATE VIEW ledger AS SELECT key,account,amount FROM decisions")
        with self.assertRaisesRegex(ValueError, "real table"):
            inspect(self.path)

    def test_row_limit(self):
        self.service.db.executemany("INSERT INTO ledger VALUES (?,?,?)", [(str(i), "A", 1) for i in range(100)])
        with self.assertRaisesRegex(ValueError, "fewer than 100"):
            inspect(self.path)

    def test_sidecar_symlink_rejected(self):
        link = Path(str(self.path) + "-wal")
        try:
            link.symlink_to(self.path)
        except OSError:
            self.skipTest("host cannot create symlinks")
        try:
            with self.assertRaisesRegex(ValueError, "symlinks"):
                inspect(self.path)
        finally:
            link.unlink()


class TrustedProcessControls(unittest.TestCase):
    def assert_fails(self, code):
        result = trusted_grade(code)
        self.assertEqual(result["status"], "fail", json.dumps(result)[:1000])
        self.assertEqual(len(result["repetitions"]), 3)
        return result

    def test_positive_three_repetitions(self):
        result = trusted_grade(REFERENCE)
        self.assertEqual(result["status"], "pass", json.dumps(result)[:2000])
        self.assertEqual(result["overall_status"], "formal_pass_review_pending")
        self.assertEqual(len(result["repetitions"]), 3)
        for rep in result["repetitions"]:
            self.assertTrue(all(worker["terminal_code"] == 0 for obs in rep["observations"] for worker in obs["workers"]))

    def test_missing_ledger(self):
        self.assert_fails(REFERENCE.replace('self.db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))', 'pass'))

    def test_replay_debits_twice(self):
        self.assert_fails(REFERENCE.replace('                self.db.commit()\n                return result',
                                          '                self.db.execute("UPDATE accounts SET remaining=remaining-1 WHERE account=?", (account,))\n                self.db.commit()\n                return result'))

    def test_reinitialization_resets_balances(self):
        self.assert_fails(REFERENCE.replace("INSERT OR IGNORE INTO accounts", "INSERT OR REPLACE INTO accounts"))

    def test_lost_rejected_decision(self):
        self.assert_fails(REFERENCE.replace('self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))',
                                          'if status == "accepted":\n                self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))'))

    def test_replay_returns_current_balance(self):
        self.assert_fails(REFERENCE.replace('"remaining": old[3]',
                                          '"remaining": self.db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]'))

    def test_mismatch_not_checked(self):
        self.assert_fails(REFERENCE.replace('if old[:2] != (account, amount):', 'if False:'))

    def test_exception_is_not_business_rejection(self):
        code = 'class Service:\n def __init__(self,path): pass\n def apply(self,request): raise RuntimeError("database unavailable")\n'
        result = self.assert_fails(code)
        self.assertIn("RuntimeError", result["repetitions"][0]["assessment"]["reason"])

    def test_boolean_remaining_does_not_equal_one(self):
        self.assert_fails(REFERENCE.replace('return {"status": status, "remaining": remaining}',
                                          'return {"status": status, "remaining": True}'))

    def test_oversized_stdout_bounded(self):
        self.assert_fails('print("x" * 70000, flush=True)\n' + REFERENCE)

    def test_duplicate_json_worker_output_rejected(self):
        self.assert_fails('print(\'{"event":"ready","event":"armed"}\', flush=True)\n' + REFERENCE)

    def test_forced_read_check_write_race(self):
        # A file barrier makes this unsafe control deterministic without relying
        # on the host scheduling two SQLite reads within a sleep interval.
        code = REFERENCE.replace('        self.db.execute("BEGIN IMMEDIATE")\n        try:\n            old', '        try:\n            old')
        code = code.replace('            status = "rejected"',
                            '            import pathlib, time\n'
                            '            marker = pathlib.Path(self.db.execute("PRAGMA database_list").fetchone()[2]).parent\n'
                            '            if amount == 60 and key.startswith("overlap-"):\n'
                            '                (marker / key).touch()\n'
                            '                deadline = time.monotonic() + 3\n'
                            '                while len(list(marker.glob("overlap-*"))) < 2:\n'
                            '                    if time.monotonic() > deadline: raise RuntimeError("test barrier timeout")\n'
                            '                    time.sleep(0.005)\n'
                            '            status = "rejected"')
        self.assert_fails(code)


class RealSandboxIntegration(unittest.TestCase):
    def test_reference_in_real_isolation(self):
        available, reason = evaluator.Sandbox.check()
        if not available:
            self.skipTest(reason)
        result = evaluator.grade(answer())
        self.assertEqual(result["status"], "pass", json.dumps(result)[:2000])


if __name__ == "__main__":
    unittest.main(verbosity=2)
