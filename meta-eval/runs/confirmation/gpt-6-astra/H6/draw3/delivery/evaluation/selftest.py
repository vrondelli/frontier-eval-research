"""Verify the evaluator with legal controls, defective CLIs, and judge probes."""
from dataclasses import replace
from pathlib import Path
import json
import sys
import tempfile
import unittest

from cases import build_cases, valid
from run_eval import evaluate, judge


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.case = valid("probe", [("x", "net_units", [9007199254740993])])

    def test_exact_numeric_encodings(self):
        for number in ("9007199254740993", "9007199254740993.000", "90071992547409930e-1"):
            payload = ('{"stock_reports":{"x":' + number + '},"diagnostic":true}').encode()
            self.assertTrue(judge(self.case, 0, payload)[0])

    def test_wrong_outputs(self):
        for payload in (b'{"stock_reports":{"x":9007199254740992}}',
            b'{"stock_reports":{"x":9007199254740993.0000000000000001}}',
            b'{"stock_reports":{"x":"9007199254740993"}}',
            b'{"stock_reports":{"x":true}}', b'{"stock_reports":{"x":NaN}}',
            b'{"stock_reports":{"x":1e999999}}', b'{"stock_reports":{}}',
            b'{"stock_reports":{"wrong":9007199254740993}}',
            b'{"stock_reports":{"x":9007199254740993,"extra":0}}',
            b'{"stock_reports":{"x":9007199254740993,"x":9007199254740992}}',
            b'[]', b'{', b'', None):
            self.assertFalse(judge(self.case, 0, payload)[0], repr(payload))
        self.assertFalse(judge(self.case, 1, b'{"stock_reports":{"x":9007199254740993}}')[0])

    def test_unbounded_exponent_spelling(self):
        zero = valid("zero", [("x", "net_units", [])])
        self.assertTrue(judge(zero, 0, b'{"stock_reports":{"x":-0.0e999999999999999999999999}}')[0])
        self.assertFalse(judge(zero, 0, b'{"stock_reports":{"x":1e-999999999999999999999999}}')[0])
        self.assertFalse(judge(self.case, 0, b'{"stock_reports":{"x":1e999999999999999999999999}}')[0])

    def test_failure_protocol(self):
        invalid = replace(self.case, expected=None)
        for output in (None, b'', b' \n', b'{"error":"invalid"}', b'{"stock_reports":null,"error":"bad"}'):
            self.assertTrue(judge(invalid, 2, output)[0])
        for output in (b'{"stock_reports":{}}', b'{"stock_reports":{"x":0}}'):
            self.assertFalse(judge(invalid, 1, output)[0])
        self.assertFalse(judge(invalid, 0, None)[0])

    def test_case_integrity(self):
        cases = build_cases()
        self.assertTrue(all(len(c.payload) <= 8192 for c in cases))
        self.assertEqual(max(len(c.payload) for c in cases), 8192)
        self.assertGreater(sum(c.expected is None for c in cases), 50)


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(JudgeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    cases = build_cases()
    by_name = {c.name: c for c in cases}
    controls = {
        "float": ["beyond_binary64", "exact_decimal_cancellation", "overflow_exponents"],
        "decimal_context": ["decimal_precision", "exact_integer_cancellation"],
        "strict_int": ["integral_spellings_net_units"],
        "bool": ["invalid_item_net_units_0"],
        "duplicates": ["duplicate_identifier", "duplicate_root", "duplicate_stat"],
        "deduplicate": ["signed_and_repeated"],
        "max_zero": ["signed_and_repeated"],
        "count_skips_validation": ["invalid_item_event_count_6"],
        "partial": ["invalid_item_net_units_6"],
        "empty_results_error": ["invalid_root_0"],
        "success_error": ["invalid_root_0"],
        "example_only": ["empty_identities"],
        "wrong_keys": ["singleton_and_zero"],
        "strings": ["provided_example"],
    }
    summary = {"judge_tests": result.testsRun, "positive_controls": {}, "negative_controls": {}}
    source = (Path(__file__).parent / "control_cli.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="evaluation controls ", dir=Path.cwd()) as folder:
        for mode in ("correct", "legal_alternative", *controls):
            candidate = Path(folder) / (mode + " summarize.py")
            candidate.write_text(source.replace('MODE = "correct"', 'MODE = ' + repr(mode)), encoding="utf-8")
            chosen = cases if mode in ("correct", "legal_alternative") else [by_name[n] for n in controls[mode]]
            report = evaluate(candidate, cases=chosen)
            if mode in ("correct", "legal_alternative"):
                summary["positive_controls"][mode] = {"passed": report["passed"], "total": report["total"]}
                if not report["all_passed"]:
                    print(json.dumps(report, indent=2))
                    return 1
            else:
                failures = [r["name"] for r in report["results"] if not r["passed"]]
                summary["negative_controls"][mode] = failures
                if not failures:
                    print("UNDETECTED MUTANT:", mode)
                    return 1
            print(f"{mode}: {report['passed']}/{report['total']} passed", flush=True)
        # Exercise operational failures through real subprocesses as well.
        for mode, body, expected_reason in [
            ("timeout", "import time; time.sleep(10)", "CLI timeout"),
            ("no_output", "pass", "missing output file"),
            ("crash", "raise RuntimeError('control crash')", "valid input exited 1"),
        ]:
            candidate = Path(folder) / (mode + ".py")
            candidate.write_text(body, encoding="utf-8")
            report = evaluate(candidate, timeout=0.2 if mode == "timeout" else 5, cases=[cases[0]])
            assert not report["all_passed"], mode
            assert report["results"][0]["reason"] == expected_reason, report
            summary["negative_controls"][mode] = [report["results"][0]["reason"]]
    output = Path(__file__).parent / "selftest-report.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("Evaluator self-tests passed; report:", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
