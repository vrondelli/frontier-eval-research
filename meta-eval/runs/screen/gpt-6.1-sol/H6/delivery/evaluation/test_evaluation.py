"""Self-tests for the oracle, runner and sensitivity to faulty CLIs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import evaluate as grader

HERE = Path(__file__).resolve().parent
CONTROL = HERE / "control_cli.py"


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case.name: case for case in grader.make_cases()}

    def test_reference_cli_passes_every_case(self):
        report = grader.evaluate([sys.executable, str(CONTROL), "reference"], cases=list(self.cases.values()))
        failures = [result for result in report["cases"] if not result["passed"]]
        self.assertTrue(report["success"], json.dumps(failures, indent=2))

    def test_equivalent_output_encodings_and_metadata(self):
        probes = [case for case in self.cases.values() if case.expected is not None]
        report = grader.evaluate([sys.executable, str(CONTROL), "equivalent"], cases=probes)
        self.assertTrue(report["success"], [r for r in report["cases"] if not r["passed"]])

    def test_mutants_are_rejected_by_relevant_probes(self):
        probes = {
            # Some Python versions use compensated float summation, so mere
            # cancellation is not a guaranteed failure of this particular mutant.
            "float": ["binary64_integer_boundary", "exponent_overflow_cancellation"],
            "decimal_context": ["decimal_context_cancellation"],
            "unique_events": ["repetitions_are_events"],
            "absolute_max": ["public_example"],
            "boolean": ["net_units_boolean_true", "event_count_boolean_false", "largest_adjustment_boolean_true"],
            "empty_max": ["empty_maximum"],
            "drop_row": ["all_sheets_and_order"],
            "duplicates": ["duplicate_identifier", "duplicate_root", "duplicate_stat", "escaped_duplicate_identifier"],
            "ignore_size": ["8193_bytes", "utf8_bytes_not_characters"],
            "empty_failure": ["late_invalid_sheet"],
            "partial_failure": ["late_invalid_sheet", "late_invalid_value"],
        }
        for mode, names in probes.items():
            for name in names:
                with self.subTest(mode=mode, case=name):
                    result = grader.run_case(self.cases[name], [sys.executable, str(CONTROL), mode], None, 10)
                    self.assertFalse(result["passed"], result)

    def test_number_comparison_is_exact_and_unbounded(self):
        canonical = grader.integer_identity
        number = grader.Number
        for left, right in [("1", "1.0"), ("1000", "1e3"), ("1", "0.001e3"),
                            ("0", "-0e999999999999999999999"),
                            ("3e999999999999999999999", "30e999999999999999999998")]:
            self.assertEqual(canonical(number(left)), canonical(number(right)))
        self.assertNotEqual(canonical(number("9007199254740993")), canonical(number("9007199254740992")))
        for token in ["1e-4000", "9007199254740992.5", "1.00000000000000000001"]:
            with self.assertRaises(ValueError):
                canonical(number(token))
        for token in [True, 1, "1", None]:
            with self.assertRaises(ValueError):
                canonical(token)

    def test_output_contract(self):
        case = grader.Case("checker", "unit", b"", {"x": "9007199254740993"})
        good = b'{"stock_reports":{"x":90071992547409930e-1},"diagnostic":{"fraction":0.125}}'
        self.assertIsNone(grader.judge_output(case, 0, good))
        for output in [b'{"stock_reports":{"x":9007199254740992}}',
                       b'{"stock_reports":{"x":true}}', b'{"stock_reports":{"x":"9007199254740993"}}',
                       b'{"stock_reports":{"x":9007199254740993,"extra":0}}',
                       b'{"stock_reports":{}}', b'{}', b'[]', b'{"stock_reports":{"x":NaN}}',
                       b'{"stock_reports":{"x":9007199254740993.5}}', good + b'{}']:
            with self.subTest(output=output):
                self.assertIsNotNone(grader.judge_output(case, 0, output))
        self.assertIsNotNone(grader.judge_output(case, 1, good))
        self.assertIsNotNone(grader.judge_output(case, 0, None))

    def test_failure_contract(self):
        case = grader.Case("invalid", "unit", b"", None)
        for output in [None, b"", b'{"error":"bad input"}']:
            self.assertIsNone(grader.judge_output(case, 2, output))
        for output in [b'{"stock_reports":{}}', b'{"stock_reports":{"good":1}}', b'not json']:
            self.assertIsNotNone(grader.judge_output(case, 2, output))
        self.assertIsNotNone(grader.judge_output(case, 2, b'{"stock_reports":{},"stock_reports":null,"error":"bad"}'))
        self.assertIsNotNone(grader.judge_output(case, 0, None))

    def test_always_reject_cannot_earn_passing_score(self):
        report = grader.evaluate([sys.executable, str(CONTROL), "always_reject"],
                                 cases=[self.cases["public_example"], self.cases["root_null"]])
        self.assertFalse(report["success"])
        self.assertEqual(report["score"], 0)
        self.assertEqual(report["passed"], 1)

    def test_timeout_and_missing_executable_fail(self):
        case = self.cases["public_example"]
        timed = grader.run_case(case, [sys.executable, "-c", "import time; time.sleep(1)"], None, 0.05)
        self.assertFalse(timed["passed"])
        self.assertIn("exceeded", timed["reason"])
        missing = grader.run_case(case, [str(HERE / "missing-executable")], None, 1)
        self.assertFalse(missing["passed"])
        self.assertIn("could not execute", missing["reason"])

    def test_cli_report_and_exit_status(self):
        with tempfile.TemporaryDirectory(prefix="eval report ", dir=HERE) as temp:
            report_path = Path(temp) / "report.json"
            process = subprocess.run([sys.executable, str(HERE / "evaluate.py"),
                                      "--report", str(report_path), "--case", "public_example", "--command",
                                      sys.executable, str(CONTROL), "drop_row"], capture_output=True, timeout=60)
            self.assertEqual(process.returncode, 1, process.stderr)
            self.assertEqual(json.loads(process.stdout), json.loads(report_path.read_text(encoding="utf-8")))
            self.assertFalse(json.loads(process.stdout)["success"])


if __name__ == "__main__":
    unittest.main()
