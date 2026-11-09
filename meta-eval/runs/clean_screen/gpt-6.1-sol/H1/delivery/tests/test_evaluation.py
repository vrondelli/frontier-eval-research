import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evaluator
import staged
from e1eval.inspect_db import inspect
from e1eval.oracle import Model, expected_primary, judge_primary, primary_plan
from e1eval.runner import Sandbox, Unavailable, inspect_state, strict_json

REFERENCE = Path(__file__).parent / "fixtures/reference_service.py"


def answer(code=None):
    return {"task_id": "E1", "code": REFERENCE.read_text(encoding="utf-8") if code is None else code,
            "explanation": "Authored control; explanation requires separate independent review."}


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.plan = primary_plan("test")
        self.outcomes = expected_primary(self.plan)

    def test_both_serial_winners_pass(self):
        for expected in self.outcomes:
            with self.subTest(order=expected["serial_order"]):
                self.assertTrue(judge_primary(self.plan, expected["replies"], expected["snapshot"])["passed"])

    def test_replies_and_disk_cannot_select_different_winners(self):
        self.assertFalse(judge_primary(self.plan, self.outcomes[0]["replies"], self.outcomes[1]["snapshot"])["passed"])

    def test_wrong_results_and_disk_mutations_fail(self):
        base = self.outcomes[0]
        mutations = {
            "both_accept": lambda x: x["replies"][1].update(status="accepted"),
            "both_reject": lambda x: x["replies"][0].update(status="rejected"),
            "replay_changes_remaining": lambda x: x["replies"][2].update(remaining=0),
            "rejected_retry_becomes_accept": lambda x: x["replies"][3].update(status="accepted"),
            "mismatch_accepted": lambda x: x["replies"][4].update(status="accepted"),
            "account_conflict_ignored": lambda x: x["replies"][5].update(status="accepted"),
            "B_affected": lambda x: x["replies"][-1].update(status="rejected"),
            "negative_allowance": lambda x: x["snapshot"]["accounts"][0].__setitem__(1, -20),
            "lost_rejection": lambda x: x["snapshot"]["decisions"].pop(),
            "missing_ledger": lambda x: x["snapshot"]["ledger"].pop(),
            "extra_ledger": lambda x: x["snapshot"]["ledger"].append(["extra", "A", 60]),
            "mismatch_writes": lambda x: x["snapshot"]["decisions"].append(["extra", "A", 61, "rejected", 40]),
            "float_remaining": lambda x: x["replies"][0].update(remaining=40.0),
            "extra_reply_field": lambda x: x["replies"][0].update(debug=True),
            "no_replies": lambda x: x["replies"].clear(),
        }
        for name, mutate in mutations.items():
            with self.subTest(control=name):
                observed = copy.deepcopy(base)
                mutate(observed)
                self.assertFalse(judge_primary(self.plan, observed["replies"], observed["snapshot"])["passed"])

    def test_model_keeps_historical_accept_and_rejection(self):
        model = Model()
        accepted = {"key": "yes", "account": "A", "amount": 60}
        rejected = {"key": "no", "account": "A", "amount": 70}
        yes, no = model.apply(accepted), model.apply(rejected)
        model.apply({"key": "drain", "account": "A", "amount": 40})
        self.assertEqual(yes, model.apply(accepted))
        self.assertEqual(no, model.apply(rejected))
        self.assertEqual({"status": "rejected", "remaining": 40}, no)


class AdmissionTests(unittest.TestCase):
    def test_alternative_does_not_execute(self):
        data = {"task_id": "E1", "alternative_format": True, "alternative": "A partitioned durable actor service",
                "explanation": "Details for review"}
        with patch("evaluator.run_code", side_effect=AssertionError("must not execute")):
            result = evaluator.grade(json.dumps(data).encode())
        self.assertEqual("review_required", result["formal_status"])
        self.assertFalse(result["executable_ran"])

    def test_invalid_answers_do_not_execute(self):
        cases = [b"[]", b"{", b'{"task_id":"E1","task_id":"E1"}',
                 json.dumps(dict(answer(), task_id="E2")).encode(),
                 json.dumps(dict(answer(), explanation=" ")).encode(),
                 json.dumps(answer("not python !")).encode(),
                 json.dumps(dict(answer(), alternative_format="true")).encode(),
                 json.dumps(dict(answer(), code="x" * (128 * 1024 + 1))).encode(),
                 b"x" * (1024 * 1024 + 1), b"\xff"]
        with patch("evaluator.run_code", side_effect=AssertionError("must not execute")):
            for data in cases:
                with self.subTest(data=data[:60]):
                    self.assertEqual("invalid_output", evaluator.grade(data)["formal_status"])

    def test_nan_and_duplicate_keys_are_invalid_json(self):
        for data in ('{"x": NaN}', '{"x":1,"x":2}', '{"x": Infinity}', '{"x":1e999}'):
            with self.assertRaises(ValueError):
                strict_json(data)

    def test_unavailable_is_neither_pass_nor_fail(self):
        with patch("evaluator.run_code", side_effect=Unavailable("test host")):
            report = evaluator.grade(json.dumps(answer()).encode())
        self.assertEqual("unavailable", report["formal_status"])
        self.assertFalse(report["executable_ran"])

    def test_all_three_repetitions_required(self):
        for results, status in (([{"passed": True}] * 3, "pass"),
                                ([], "fail"), ([{"passed": True}] * 2, "fail"),
                                ([{"passed": True}, {"passed": False}, {"passed": True}], "fail")):
            with patch("evaluator.run_code", return_value=results):
                report = evaluator.grade(json.dumps(answer()).encode())
            self.assertEqual(status, report["formal_status"])
            self.assertEqual("pending", report["review"]["status"])

    def test_review_template_binds_exact_answer(self):
        raw = json.dumps(answer()).encode()
        form = evaluator.review_template(raw)
        self.assertEqual(evaluator.digest(raw), form["answer_sha256"])
        self.assertEqual(7, len(form["criteria"]))
        self.assertTrue(all(x["judgment"] == "unresolved" for x in form["criteria"].values()))

    def test_review_validation_requires_binding_coverage_and_real_quotes(self):
        raw = json.dumps(answer()).encode()
        form = evaluator.review_template(raw)
        form.update(reviewer="independent-reviewer-1", independence_declaration="Not the author")
        for criterion in form["criteria"].values():
            criterion.update(judgment="supported", reason="Specific review rationale",
                             evidence_quotes=["Authored control"])
        self.assertEqual("review_form_valid", evaluator.validate_review(raw, form)["status"])
        for mutation in ("hash", "quote", "criterion", "reviewer", "reason"):
            invalid = copy.deepcopy(form)
            if mutation == "hash":
                invalid["answer_sha256"] = "wrong"
            elif mutation == "quote":
                invalid["criteria"]["atomicity"]["evidence_quotes"] = ["invented nonexistent quote"]
            elif mutation == "criterion":
                del invalid["criteria"]["atomicity"]
            elif mutation == "reviewer":
                invalid["reviewer"] = ""
            else:
                invalid["criteria"]["atomicity"]["reason"] = ""
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                evaluator.validate_review(raw, invalid)


class StagedTests(unittest.TestCase):
    def test_reveal_is_hidden_until_first_answer_is_preserved(self):
        initial = staged.initial_state("case-1")
        self.assertNotIn("F6.", initial["view"]["prompt"])
        self.assertNotIn("hot-account", initial["view"]["prompt"])
        raw = json.dumps(answer()).encode()
        revealed = staged.reveal(initial, raw)
        self.assertIn("F6.", revealed["view"]["prompt"])
        self.assertEqual(evaluator.digest(raw), revealed["first_answer_sha256"])
        with patch("evaluator.grade", return_value={"formal_status": "unavailable"}):
            result = staged.finish(revealed, raw)
        self.assertEqual(answer(), result["staged_evidence"]["first_answer"])

    def test_changed_lineage_is_rejected(self):
        initial = staged.initial_state("case-1")
        raw = json.dumps(answer()).encode()
        revealed = staged.reveal(initial, raw)
        with self.assertRaises(ValueError):
            staged.finish(initial, raw)
        for field in ("first_answer", "first_answer_sha256", "parent_state_sha256", "view"):
            changed = copy.deepcopy(revealed)
            changed[field] = "changed"
            with self.subTest(field=field), self.assertRaises(ValueError):
                staged.finish(changed, raw)


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "ledger.sqlite"

    def make_db(self):
        db = sqlite3.connect(self.path)
        db.executescript("""
            CREATE TABLE accounts(account TEXT PRIMARY KEY,remaining INTEGER);
            CREATE TABLE decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER);
            CREATE TABLE ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER);
            INSERT INTO accounts VALUES('A',100),('B',100);
        """)
        db.commit()
        return db

    def test_reads_real_tables(self):
        self.make_db().close()
        self.assertEqual(Model().snapshot(), inspect(self.path))

    def test_inspector_subprocess_observes_the_same_state(self):
        self.make_db().close()
        self.assertEqual({"snapshot": Model().snapshot()}, inspect_state(self.path.parent))

    def test_views_are_rejected(self):
        with self.make_db() as db:
            db.execute("DROP TABLE ledger")
            db.execute("CREATE VIEW ledger AS SELECT key,account,amount FROM decisions")
        db.close()
        with self.assertRaisesRegex(ValueError, "real"):
            inspect(self.path)

    def test_missing_primary_key_is_rejected(self):
        with self.make_db() as db:
            db.execute("DROP TABLE ledger")
            db.execute("CREATE TABLE ledger(key TEXT,account TEXT,amount INTEGER)")
        db.close()
        with self.assertRaisesRegex(ValueError, "schema"):
            inspect(self.path)

    def test_type_row_and_corrupt_file_limits(self):
        db = self.make_db()
        db.execute("UPDATE accounts SET remaining='not an integer' WHERE account='A'")
        db.commit()
        with self.assertRaisesRegex(ValueError, "type"):
            inspect(self.path)
        db.execute("UPDATE accounts SET remaining=100")
        db.executemany("INSERT INTO ledger VALUES (?, 'A', 1)", [(str(i),) for i in range(100)])
        db.commit()
        db.close()
        with self.assertRaisesRegex(ValueError, "row limit"):
            inspect(self.path)
        self.path.write_bytes(b"not sqlite")
        with self.assertRaises(sqlite3.DatabaseError):
            inspect(self.path)

    def test_missing_database_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            inspect(self.path)

    def test_symlink_sidecar_is_rejected(self):
        self.make_db().close()
        sidecar = Path(str(self.path) + "-wal")
        try:
            sidecar.symlink_to(self.path)
        except OSError:
            self.skipTest("host cannot create symlinks")
        with self.assertRaisesRegex(ValueError, "regular"):
            inspect(self.path)


class LinuxIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            Sandbox()
        except Unavailable as exc:
            raise unittest.SkipTest(str(exc))

    def grade_code(self, code):
        return evaluator.grade(json.dumps(answer(code)).encode())

    def test_authored_reference_in_real_sandbox(self):
        result = self.grade_code(REFERENCE.read_text(encoding="utf-8"))
        self.assertEqual("pass", result["formal_status"], json.dumps(result, indent=2))
        self.assertEqual(3, len(result["repetitions"]))
        self.assertTrue(all(r["both_armed_before_release"] for r in result["repetitions"]))
        self.assertTrue(all(len(r["workers"]) == 9 for r in result["repetitions"]))

    def test_executed_negative_controls(self):
        source = REFERENCE.read_text(encoding="utf-8")
        controls = {
            "amount_conflict_ignored": source.replace("(account, amount) != old[:2]", "account != old[0]"),
            "rejections_not_durable": source.replace(
                '            db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))',
                '            if status == "accepted":\n                db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))'),
            "reinitialize_balance": source.replace("INSERT OR IGNORE INTO accounts", "INSERT OR REPLACE INTO accounts"),
            "fabricated_acceptance": 'class Service:\n def __init__(self,path): pass\n def apply(self,r): return {"status":"accepted","remaining":40}\n',
            "read_before_transaction_loses_update": source + '''
CorrectService = Service
class Service(CorrectService):
    def apply(self, request):
        import pathlib, time
        db = self._connect()
        try:
            old = db.execute('SELECT key FROM decisions WHERE key=?', (request['key'],)).fetchone()
            if old or request['account'] != 'A' or request['amount'] != 60:
                return super().apply(request)
            remaining = db.execute("SELECT remaining FROM accounts WHERE account='A'").fetchone()[0]
            pathlib.Path('/state/race-' + request['key']).touch()
            deadline = time.monotonic() + 3
            while len(list(pathlib.Path('/state').glob('race-*'))) < 2:
                if time.monotonic() > deadline:
                    raise RuntimeError('control rendezvous failed')
                time.sleep(.005)
            db.execute('BEGIN IMMEDIATE')
            remaining -= 60
            db.execute("UPDATE accounts SET remaining=? WHERE account='A'", (remaining,))
            db.execute('INSERT INTO ledger VALUES (?,?,?)', (request['key'], 'A', 60))
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (request['key'], 'A', 60, 'accepted', remaining))
            db.commit()
            return {'status':'accepted', 'remaining':remaining}
        finally:
            db.close()
''',
        }
        for name, code in controls.items():
            with self.subTest(control=name):
                self.assertEqual("fail", self.grade_code(code)["formal_status"])

    def test_network_and_filesystem_isolation(self):
        source = REFERENCE.read_text(encoding="utf-8")
        assertion = '''
import os, socket
assert not os.path.exists('/app/evaluator.py')
assert not os.path.exists('/app/oracle.py')
assert not os.path.exists('/state/../input/E1.md')
assert 'E1_PARENT_SECRET' not in os.environ
try:
    socket.create_connection(('1.1.1.1', 443), timeout=0.1)
except OSError:
    pass
else:
    raise RuntimeError('network unexpectedly available')
try:
    open('/app/candidate.py', 'w')
except OSError:
    pass
else:
    raise RuntimeError('candidate mount is writable')
'''
        with patch.dict("os.environ", {"E1_PARENT_SECRET": "not-for-candidate"}):
            self.assertEqual("pass", self.grade_code(assertion + source)["formal_status"])


if __name__ == "__main__":
    unittest.main()
