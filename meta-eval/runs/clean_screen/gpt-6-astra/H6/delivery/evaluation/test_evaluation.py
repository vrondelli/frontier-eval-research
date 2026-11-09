"""Evaluator self-tests, including real subprocesses and deliberate regressions."""

from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import evaluate


# Test-only CLI fixture. It is generated in a temporary directory, never installed
# into the task workspace or presented as the candidate's solution.
FIXTURE = r'''
import json
from decimal import Decimal
import sys

MODE = "correct"
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

def pairs(items):
    result = {}
    for key, value in items:
        if key in result and MODE != "duplicates":
            raise ValueError("duplicate")
        result[key] = value
    return result

def constant(value):
    raise ValueError("constant")

reports = {}
try:
    with open(sys.argv[1], "rb") as stream:
        raw = stream.read()
    assert len(raw) <= 8192
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                     parse_int=Decimal, parse_float=Decimal, parse_constant=constant)
    assert isinstance(obj, dict) and set(obj) == {"adjustment_sheets"}
    sheets = obj["adjustment_sheets"]
    assert isinstance(sheets, dict) and sheets
    for key, sheet in sheets.items():
        assert key and isinstance(sheet, dict) and set(sheet) == {"stat", "turns"}
        stat, values = sheet["stat"], sheet["turns"]
        assert stat in ("net_units", "event_count", "largest_adjustment")
        assert isinstance(values, list)
        assert stat != "largest_adjustment" or values
        if not (MODE == "count-skips-validation" and stat == "event_count"):
            assert all(isinstance(v, Decimal) and v.is_finite()
                       and v == v.to_integral_value() for v in values)
        if MODE == "count-skips-validation" and stat == "event_count":
            answer = len(values)
        else:
            values = [int(v) for v in values]
            if MODE == "float":
                values = [int(float(v)) for v in values]
            answer = (sum(values) if stat == "net_units" else
                      len(set(values)) if stat == "event_count" and MODE == "unique-count" else
                      len(values) if stat == "event_count" else
                      max(values, key=abs) if MODE == "absolute-max" else max(values))
        reports[key] = answer
    if MODE == "missing-key":
        reports.pop(next(iter(reports)))
    if MODE == "extra-key":
        reports["invented"] = 1
    if MODE == "boolean-output":
        reports = {k: True for k in reports}
    if MODE == "constant":
        reports = {"warehouse-sample-1-0": 5, "warehouse-sample-1-1": 3,
                   "warehouse-sample-1-2": -3}
    with open(sys.argv[2], "w", encoding="utf-8") as stream:
        if MODE == "exponent-output":
            stream.write('{"stock_reports":{' + ','.join(
                json.dumps(k) + ':' + str(v) + 'e0' for k,v in reports.items())
                + '},"diagnostics":{"ok":true}}')
        else:
            json.dump({"stock_reports": reports, "diagnostics": "allowed"}, stream)
except Exception:
    if MODE == "partial-write":
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump({"stock_reports": reports}, stream)
    sys.exit(1)
'''


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='evaluation self test ', dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'output.json'

    def fixture(self, mode='correct'):
        candidate = self.root / 'candidate CLI.py'
        candidate.write_text(FIXTURE.replace('MODE = "correct"', f'MODE = {mode!r}'), encoding='utf-8')
        return candidate

    def run_case(self, mode, name):
        case = next(c for c in evaluate.cases() if c.name == name)
        candidate = self.fixture(mode)
        source = self.root / 'input data.json'
        source.write_bytes(case.raw)
        if self.output.exists():
            self.output.unlink()
        run = subprocess.run([sys.executable, str(candidate), str(source), str(self.output)],
                             capture_output=True, timeout=10)
        return evaluate.judge(case, run.returncode, self.output)

    def test_full_harness_through_actual_cli(self):
        report = self.root / 'report.json'
        run = subprocess.run([sys.executable, str(Path(evaluate.__file__)), str(self.fixture()),
                              '--report', str(report)], capture_output=True, text=True, timeout=90)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        data = json.loads(report.read_text(encoding='utf-8'))
        self.assertTrue(data['passed'])
        self.assertEqual(data['passed_cases'], len(evaluate.cases()))
        self.assertTrue(all(' ' in row['command'][-1] for row in data['cases']))

    def test_rejects_behavioral_mutations(self):
        for mode, name in [
            ('unique-count', 'empty-identities-and-repetitions'),
            ('absolute-max', 'illustrative-example'),
            ('float', 'float-integer-boundary'),
            ('count-skips-validation', 'event_count-invalid-item-00'),
            ('duplicates', 'escaped-duplicate-id'),
            ('partial-write', 'missing-stat'),
            ('missing-key', 'opaque-identifiers'),
            ('extra-key', 'opaque-identifiers'),
            ('boolean-output', 'illustrative-example'),
            ('constant', 'generated-00'),
        ]:
            with self.subTest(mode=mode):
                self.assertFalse(self.run_case(mode, name)[0])

    def test_accepts_exponent_output_and_metadata(self):
        self.assertTrue(self.run_case('exponent-output', 'float-integer-boundary')[0])
        self.assertTrue(self.run_case('exponent-output', 'large-exponent')[0])

    def test_output_checker_is_exact_and_encoding_independent(self):
        case = evaluate.Case('check', 'checker', b'', {'x': Decimal('9007199254740993')})
        for value in ['9007199254740993', '9007199254740993.0', '90071992547409930e-1']:
            self.output.write_text('{"stock_reports":{"x":' + value + '},"extra":true}', encoding='utf-8')
            self.assertTrue(evaluate.judge(case, 0, self.output)[0])
        for value in ['9007199254740992', 'true', '"9007199254740993"', 'null', 'NaN', '1.1']:
            self.output.write_text('{"stock_reports":{"x":' + value + '}}', encoding='utf-8')
            self.assertFalse(evaluate.judge(case, 0, self.output)[0])

    def test_failure_output_rules(self):
        case = evaluate.Case('bad', 'checker', b'null', None)
        self.assertTrue(evaluate.judge(case, 1, self.output)[0])
        for payload, accepted in [('{"error":"bad input"}', True),
                                  ('{"stock_reports":{}}', False),
                                  ('{"stock_reports":{"a":2}}', False),
                                  ('{"stock_reports":{', False)]:
            self.output.write_text(payload, encoding='utf-8')
            self.assertEqual(evaluate.judge(case, 1, self.output)[0], accepted)
        self.assertFalse(evaluate.judge(case, 0, self.output)[0])

    def test_cases_stay_within_input_domain_and_are_reproducible(self):
        suite = evaluate.cases()
        self.assertEqual(suite, evaluate.cases())
        self.assertNotEqual(suite, evaluate.cases(17))
        self.assertTrue(all(len(c.raw) <= 8192 for c in suite))
        boundary = next(c for c in suite if c.name == 'exactly-8192-bytes')
        self.assertEqual(len(boundary.raw), 8192)

    def test_failure_exit_and_report(self):
        report = self.root / 'report.json'
        candidate = self.root / 'always fail.py'
        candidate.write_text('raise SystemExit(1)\n', encoding='utf-8')
        run = subprocess.run([sys.executable, str(Path(evaluate.__file__)), str(candidate),
                              '--report', str(report)], capture_output=True, timeout=90)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(report.read_text())['passed'])


if __name__ == '__main__':
    unittest.main()
