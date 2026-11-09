import copy
import json
from pathlib import Path
import tempfile
import unittest

from cases import build_cases
from grader import grade, oracle
from reference import InvalidInput, expected
from reporting import validate_report
from run import run, temporary_directory


class OracleAndGraderTests(unittest.TestCase):
    def setUp(self):
        self.cases = {c.name: c for c in build_cases()}

    def test_all_fixtures_and_independent_anchors(self):
        for case in self.cases.values():
            with self.subTest(case=case.name):
                answer = oracle(case)
                if case.valid:
                    self.assertLessEqual(len(case.raw), 8192)
                    self.assertIsNotNone(case.anchor)
                    self.assertEqual(answer, case.anchor)

    def test_determinism_and_seed_variation(self):
        self.assertEqual(build_cases(1), build_cases(1))
        self.assertNotEqual(build_cases(1)[-1].raw, build_cases(2)[-1].raw)

    def test_exact_byte_boundary(self):
        self.assertEqual(len(self.cases["exact_byte_limit"].raw), 8192)
        raw = self.cases["oversize_utf8"].raw
        self.assertGreater(len(raw), 8192)
        self.assertLessEqual(len(raw.decode("utf-8")), 8192)

    def test_acceptable_output_forms(self):
        case = self.cases["binary_precision"]
        for raw in [b'{"stock_reports":{"quantity":2}}', b'{"stock_reports":{"quantity":2.0}}',
                    b'{"diagnostic":{"x":true},"stock_reports":{"quantity":20e-1}}']:
            self.assertTrue(grade(case, oracle(case), 0, raw)[0])
        huge = self.cases["signed_huge_max"]
        self.assertTrue(grade(huge, oracle(huge), 0, b'{"stock_reports":{"quantity":-1e400}}')[0])

    def test_incorrect_outputs(self):
        case = self.cases["binary_precision"]
        for raw in [None, b'{}', b'[]', b'{"stock_reports":[]}', b'{"stock_reports":{}}',
                    b'{"stock_reports":{"quantity":true}}', b'{"stock_reports":{"quantity":"2"}}',
                    b'{"stock_reports":{"quantity":2.00000000000000000000000001}}',
                    b'{"stock_reports":{"quantity":3}}', b'{"stock_reports":{"quantity":2,"extra":0}}',
                    b'{"stock_reports":{"quantity":NaN}}', b'\xff', b'not json']:
            with self.subTest(raw=raw):
                self.assertFalse(grade(case, oracle(case), 0, raw)[0])

    def test_float_rounded_output_is_rejected(self):
        case = self.cases["unbounded_integer"]
        raw = json.dumps({"stock_reports": {"quantity": float(2**100 + 19)}}).encode()
        self.assertFalse(grade(case, oracle(case), 0, raw)[0])

    def test_invalid_failure_contract(self):
        case = self.cases["empty_max"]
        for code, raw, passes in [(2, None, True), (1, b'{"error":"bad"}', True),
                                  (0, None, False), (0, b'{"error":"bad"}', False),
                                  (1, b'{"stock_reports":{}}', False),
                                  (1, b'{"stock_reports":{"x":1}}', False),
                                  (1, b'broken', False)]:
            self.assertEqual(grade(case, None, code, raw)[0], passes)

    def test_oracle_fixture_disagreement_is_harness_error(self):
        from cases import Case
        with self.assertRaises(AssertionError):
            oracle(Case("bad", ("JSON",), b"{}", True))
        with self.assertRaises(AssertionError):
            oracle(Case("bad", ("JSON",), self.cases["singleton"].raw, False))


class RunnerTests(unittest.TestCase):
    def candidate(self, root, source):
        directory = Path(root) / "candidate"
        directory.mkdir()
        (directory / "summarize.py").write_text(source, encoding="utf-8")
        return directory

    def test_timeout(self):
        with temporary_directory() as tmp:
            candidate = self.candidate(tmp, "import time\ntime.sleep(30)\n")
            report = run(candidate, timeout=0.2, selected=["singleton"])
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["cases"][0]["reason"], "command timed out")

    def test_clean_cwd_environment_and_input_paths(self):
        source = '''import os, sys, json
from pathlib import Path
assert "EVAL_SECRET_TEST" not in os.environ
assert " " in sys.argv[1] and "空" in sys.argv[2]
assert Path("README.md").is_file()
assert not Path("already_ran").exists()
Path("already_ran").write_text("yes")
Path(sys.argv[2]).write_text(json.dumps({"stock_reports":{"quantity":0}}))
'''
        import os
        old = os.environ.get("EVAL_SECRET_TEST")
        os.environ["EVAL_SECRET_TEST"] = "should-not-be-inherited"
        try:
            with temporary_directory() as tmp:
                candidate = self.candidate(tmp, source)
                for _ in range(2):
                    report = run(candidate, selected=["singleton"])
                    self.assertEqual(report["status"], "pass")
                    self.assertFalse((candidate / "already_ran").exists())
        finally:
            if old is None:
                os.environ.pop("EVAL_SECRET_TEST", None)
            else:
                os.environ["EVAL_SECRET_TEST"] = old

    def test_stream_and_output_limits(self):
        for source, reason in [
            ('print("x" * 70000)', "diagnostic stream exceeds 64 KiB limit"),
            ('import pathlib,sys; pathlib.Path(sys.argv[2]).write_bytes(b" " * 2200000)', "output exceeds 2 MiB limit"),
        ]:
            with temporary_directory() as tmp:
                candidate = self.candidate(tmp, source)
                report = run(candidate, selected=["singleton"])
                self.assertFalse(report["cases"][0]["passed"])
                self.assertEqual(report["cases"][0]["reason"], reason)

    def test_reports_validate_and_mutations_fail_validation(self):
        with temporary_directory() as tmp:
            candidate = self.candidate(tmp, "raise SystemExit(2)")
            report = run(candidate, selected=["empty_max"])
            validate_report(report)
            for key, value in [("score", 3), ("status", "bogus"), ("schema_version", "bad"),
                               ("candidate_sha256", "bad"), ("counts", {"total": 2, "passed": 2, "failed": 0})]:
                wrong = copy.deepcopy(report)
                wrong[key] = value
                with self.assertRaises(ValueError):
                    validate_report(wrong)

    def test_unknown_case_and_missing_candidate_are_harness_errors(self):
        with temporary_directory() as tmp:
            with self.assertRaises(ValueError):
                run(tmp)
            with self.assertRaises(ValueError):
                run(tmp, selected=["does-not-exist"])


if __name__ == "__main__":
    unittest.main()
