import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import controls
import evaluate
from inspect_db import inspect
from isolation import ExecutionFailure, Unavailable, check_available, strict_json, sandbox_command
from oracle import Model, exact, matching_snapshot, serial_candidates
import staged


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.left = evaluate.request("left", "A", 60)
        self.right = evaluate.request("right", "A", 60)

    def test_both_overlap_orders_and_wrong_replies(self):
        for order in ((0, 1), (1, 0)):
            model, replies = Model(), [None, None]
            requests = [self.left, self.right]
            for i in order:
                replies[i] = model.apply(requests[i])
            candidates = serial_candidates(Model(), requests, replies)
            self.assertEqual(len(matching_snapshot(candidates, model.snapshot())), 1)
        both = [{"status": "accepted", "remaining": 40}] * 2
        self.assertEqual(serial_candidates(Model(), [self.left, self.right], both), [])

    def test_history_global_identity_and_no_side_effect_on_mismatch(self):
        model = Model()
        accepted = model.apply(self.left)
        rejected = model.apply(self.right)
        model.apply(evaluate.request("later", "A", 10))
        self.assertEqual(model.apply(self.left), accepted)
        self.assertEqual(model.apply(self.right), rejected)
        before = model.snapshot()
        for change in (evaluate.request("left", "B", 60), evaluate.request("right", "A", 1)):
            self.assertEqual(model.apply(change), {"status": "payload_mismatch", "remaining": None})
            self.assertEqual(model.snapshot(), before)
        self.assertEqual(model.apply(evaluate.request("B100", "B", 100)), {"status": "accepted", "remaining": 0})

    def test_concurrent_duplicate_has_one_debit(self):
        expected = {"status": "accepted", "remaining": 40}
        candidates = serial_candidates(Model(), [self.left, self.left], [expected, expected])
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].accounts["A"], 40)
        self.assertEqual(len(candidates[0].ledger), 1)

    def test_inspector_oracle_catches_plausible_reply_with_wrong_disk(self):
        model = Model()
        model.apply(self.left)
        model.apply(self.right)
        good = model.snapshot()
        for table in ("accounts", "decisions", "ledger"):
            bad = copy.deepcopy(good)
            bad[table].pop()
            self.assertEqual(matching_snapshot([model], bad), [])
        bad = copy.deepcopy(good)
        bad["accounts"][0][1] = -20
        self.assertEqual(matching_snapshot([model], bad), [])

    def test_strict_json_and_reply_types(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(raw)
        self.assertFalse(exact({"remaining": True}, {"remaining": 1}))
        self.assertFalse(exact({"remaining": 40.0}, {"remaining": 40}))
        self.assertFalse(exact({"status": "accepted", "remaining": 40, "extra": 1},
                               {"status": "accepted", "remaining": 40}))


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite"
        self.con = sqlite3.connect(self.path)
        self.addCleanup(self.con.close)
        for sql in ("CREATE TABLE accounts(account TEXT PRIMARY KEY, remaining INTEGER)",
                    "CREATE TABLE decisions(key TEXT PRIMARY KEY, account TEXT, amount INTEGER, status TEXT, remaining INTEGER)",
                    "CREATE TABLE ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER)",
                    "INSERT INTO accounts VALUES('A',100),('B',100)"):
            self.con.execute(sql)
        self.con.commit()

    def test_initial_snapshot_and_read_only(self):
        before = self.path.read_bytes()
        self.assertEqual(inspect(self.path), Model().snapshot())
        self.assertEqual(before, self.path.read_bytes())

    def test_reject_view(self):
        self.con.execute("DROP TABLE ledger")
        self.con.execute("CREATE VIEW ledger AS SELECT 'x' AS key, 'A' AS account, 60 AS amount")
        self.con.commit()
        with self.assertRaisesRegex(ValueError, "real table"):
            inspect(self.path)

    def test_reject_missing_pk(self):
        self.con.execute("DROP TABLE ledger")
        self.con.execute("CREATE TABLE ledger(key TEXT, account TEXT, amount INTEGER)")
        self.con.commit()
        with self.assertRaisesRegex(ValueError, "primary key"):
            inspect(self.path)

    def test_reject_row_limit(self):
        self.con.executemany("INSERT INTO ledger VALUES(?, 'A', 1)", [(str(i),) for i in range(100)])
        self.con.commit()
        with self.assertRaisesRegex(ValueError, "row limit"):
            inspect(self.path)

    def test_reject_sidecar_directory(self):
        Path(str(self.path) + "-wal").mkdir()
        with self.assertRaisesRegex(ValueError, "regular files"):
            inspect(self.path)


class EvaluationTests(unittest.TestCase):
    def test_sandbox_command_and_preflight_fail_closed(self):
        with patch("isolation.sys.platform", "linux"), \
             patch("isolation.shutil.which", return_value="/usr/bin/bwrap"), \
             patch("isolation.Path.is_file", return_value=True), \
             patch("isolation.Path.exists", return_value=True):
            cmd = sandbox_command(Path("state"), Path("candidate.py"), ["/worker.py"])
            for flag in ("--unshare-all", "--clearenv", "--die-with-parent", "--new-session"):
                self.assertIn(flag, cmd)
            self.assertEqual(cmd[-4:], ["/usr/bin/python3", "-I", "-S", "/worker.py"])
            self.assertNotIn("oracle.py", " ".join(cmd))
            self.assertNotIn("controls.py", " ".join(cmd))
            with patch("isolation.subprocess.run") as run:
                run.return_value.returncode = 1
                run.return_value.stdout = b""
                with self.assertRaises(Unavailable):
                    check_available(Path("state"), Path("candidate.py"))

    def test_unavailable_never_executes_candidate(self):
        malicious = {"task_id": "E1", "code": "raise RuntimeError('must not run')", "explanation": "test"}
        with patch("evaluate.check_available", side_effect=Unavailable("test host")), patch("evaluate.run_requests") as run:
            result = evaluate.evaluate(malicious)
            self.assertEqual(result["formal_status"], "unavailable")
            self.assertEqual(result["repetitions"], [])
            run.assert_not_called()

    def test_alternative_and_invalid_are_distinct(self):
        with patch("evaluate.check_available") as preflight:
            alt = {"task_id": "E1", "alternative_format": True, "alternative": "A different architecture", "explanation": "explain"}
            self.assertEqual(evaluate.evaluate(alt)["formal_status"], "review_required")
            for invalid in ([], {}, {"task_id": "E1", "code": "broken (", "explanation": "x"},
                            {"task_id": "E1", "code": "pass", "explanation": ""}):
                self.assertEqual(evaluate.evaluate(invalid)["formal_status"], "invalid")
            preflight.assert_not_called()

    def test_driver_three_runs_both_orders(self):
        # This is a driver fixture, not an execution of submitted Python.
        state_models = {}
        def fake_run(state, candidate, requests, record):
            model = state_models.setdefault(str(state), Model())
            requests = list(requests)
            order = list(range(len(requests)))
            if int(state.name.split('-')[-1]) % 2:
                order.reverse()
            replies = [None] * len(requests)
            for i in order:
                replies[i] = model.apply(requests[i])
            record["replies"] = replies
            record["terminal_codes"] = [0] * len(requests)
            return replies
        with patch("evaluate.check_available"), patch("evaluate.run_requests", fake_run), \
             patch("evaluate.observe", lambda state: state_models[str(state)].snapshot()):
            result = evaluate.evaluate(controls.answer())
        self.assertEqual(result["formal_status"], "pass")
        self.assertEqual(result["overall_status"], "formal_pass_review_pending")
        self.assertEqual(len(result["repetitions"]), 3)
        self.assertTrue(all(len(run["checks"]) == 14 for run in result["repetitions"]))

    def test_error_is_failure_not_rejection_and_all_runs_attempted(self):
        with patch("evaluate.check_available"), \
             patch("evaluate.run_requests", side_effect=ExecutionFailure("OperationalError")), \
             patch("evaluate.observe", side_effect=ExecutionFailure("no database")):
            result = evaluate.evaluate(controls.answer())
        self.assertEqual(result["formal_status"], "fail")
        self.assertEqual(len(result["repetitions"]), 3)
        self.assertTrue(all("OperationalError" in r["reason"] for r in result["repetitions"]))

    def test_all_control_sources_compile_without_running(self):
        for name in controls.CONTROLS:
            with self.subTest(control=name):
                self.assertEqual(evaluate.validate_answer(controls.answer(name)), "executable")

    def test_independent_inspector_subprocess(self):
        # Uses a trusted fixture DB, not native execution of a submission.
        from isolation import observe
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            con = sqlite3.connect(state / "ledger.sqlite")
            con.executescript("CREATE TABLE accounts(account TEXT PRIMARY KEY,remaining INTEGER);"
                              "INSERT INTO accounts VALUES('A',100),('B',100);"
                              "CREATE TABLE decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER);"
                              "CREATE TABLE ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER);")
            con.close()
            self.assertEqual(observe(state), Model().snapshot())


class ReviewTests(unittest.TestCase):
    def test_binding_coverage_quotes_and_unresolved(self):
        answer = controls.answer()
        review = evaluate.review_template(answer, "abc")
        review.update(reviewer="test reviewer", independence_declaration="authored unit fixture", comparison_repertoire="none")
        for row in review["criteria"]:
            row["rationale"] = "Unresolved pending independent review."
        self.assertEqual(evaluate.validate_review(answer, "abc", review)["status"], "review_structure_valid")
        for change in ("hash", "quote", "coverage"):
            bad = copy.deepcopy(review)
            if change == "hash":
                bad["answer_sha256"] = "other"
            elif change == "quote":
                bad["criteria"][0].update(judgment="supported", evidence_quote="fabricated quote")
            else:
                bad["criteria"].pop()
            with self.assertRaises(ValueError):
                evaluate.validate_review(answer, "abc", bad)


class StageTests(unittest.TestCase):
    def test_initial_withholds_reveal_and_preserves_first_response(self):
        self.assertNotIn("deadlock", staged.initial_view()["prompt"])
        self.assertNotIn("F6.", staged.initial_view()["prompt"])
        self.assertIn("F6.", staged.full_view()["prompt"])
        for first in ({"explanation": "first"}, None, []):
            with self.subTest(first=first), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)
                staged.start(path / "0.json")
                staged.write_new(path / "first.json", first)
                staged.reveal(path / "0.json", path / "first.json", path / "1.json")
                state = staged.load_state(path / "1.json", "revealed")
                self.assertEqual(state["first_answer"], first)
                with self.assertRaises(FileExistsError):
                    staged.start(path / "0.json")
                state["view"]["prompt"] += "tampered"
                (path / "bad.json").write_text(json.dumps(state), encoding="utf-8")
                with self.assertRaises(ValueError):
                    staged.load_state(path / "bad.json", "revealed")

    def test_finish_binds_final_answer_and_retains_first(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            staged.start(path / "0.json")
            first = {"task_id": "E1", "explanation": "before the reveal"}
            staged.write_new(path / "first.json", first)
            staged.reveal(path / "0.json", path / "first.json", path / "1.json")
            final = {"task_id": "E1", "alternative_format": True, "alternative": "Alternative design", "explanation": "after the reveal"}
            staged.write_new(path / "final.json", final)
            result = staged.finish(path / "1.json", path / "final.json", path / "out.json",
                                   evaluate.load_answer, evaluate.evaluate)
            self.assertEqual(result["formal_status"], "review_required")
            self.assertEqual(result["staged_evidence"]["first_answer"], first)
            self.assertEqual(result["answer_sha256"], evaluate.load_answer(path / "final.json")[1])


class IsolatedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "state").mkdir()
            (root / "candidate.py").write_text("pass", encoding="utf-8")
            try:
                check_available(root / "state", root / "candidate.py")
            except Unavailable as exc:
                raise unittest.SkipTest(str(exc))

    def test_reference_and_negative_implementation_controls(self):
        for control in controls.CONTROLS:
            with self.subTest(control=control):
                result = evaluate.evaluate(controls.answer(control))
                expected = "pass" if control == "reference" else "fail"
                self.assertEqual(result["formal_status"], expected, result)
                self.assertEqual(len(result["repetitions"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
