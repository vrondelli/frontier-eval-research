import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cases import Case, build_cases
from evaluate import judge, run_suite


class EvaluationTests(unittest.TestCase):
    def test_spec_case_invariants(self):
        cases = build_cases()
        self.assertGreaterEqual(len(cases), 80)
        self.assertEqual(len(cases), len({c.name for c in cases}))
        self.assertTrue(all(len(c.raw.encode('utf-8')) <= 8192 for c in cases))
        limit = next(c for c in cases if c.name == 'exact-byte-limit')
        self.assertEqual(len(limit.raw.encode('utf-8')), 8192)
        # Hand-calculated anchors guard against obvious fixture/oracle mistakes.
        self.assertEqual(next(c for c in cases if c.name == 'integral-number-encodings').expected['decimal'], 124)
        self.assertEqual(next(c for c in cases if c.name == 'binary64-integer-boundary').expected['sum'], 1)

    def test_valid_output_encodings_and_metadata(self):
        case = Case('check', 'test', '', {'x': 123})
        for number in ['123', '123.0000', '1.23e2', '12300e-2']:
            with self.subTest(number=number):
                raw = '{"stock_reports":{"x":' + number + '},"diagnostics":["ok"]}'
                self.assertTrue(judge(case, 0, raw)[0])
        for number in ['true', '"123"', '123.00000000000000000000000001', 'null', 'NaN']:
            with self.subTest(number=number):
                self.assertFalse(judge(case, 0, '{"stock_reports":{"x":' + number + '}}')[0])
        for raw in [None, '{}', '[]', '{"stock_reports":[]}',
                    '{"stock_reports":{}}', '{"stock_reports":{"x":123,"extra":0}}']:
            self.assertFalse(judge(case, 0, raw)[0])
        self.assertFalse(judge(case, 1, '{"stock_reports":{"x":123}}')[0])
        self.assertFalse(judge(case, 0, '[' * 2000 + '0' + ']' * 2000)[0])
        self.assertFalse(judge(case, 0, '{"stock_reports":{"x":1e999999999999999999999}}')[0])

    def test_output_exactness_without_float_or_decimal_rounding(self):
        expected = 10 ** 400 + 1
        case = Case('exact', 'test', '', {'x': expected})
        self.assertTrue(judge(case, 0, '{"stock_reports":{"x":' + str(expected) + '}}')[0])
        self.assertFalse(judge(case, 0, '{"stock_reports":{"x":1e400}}')[0])
        huge = Case('huge', 'test', '', {'x': 10 ** 5000})
        self.assertTrue(judge(huge, 0, '{"stock_reports":{"x":1e5000}}')[0])

    def test_failure_contract(self):
        case = Case('bad', 'test', '', None)
        for raw in [None, '{"error":"invalid"}', '{}']:
            self.assertTrue(judge(case, 2, raw)[0])
            self.assertFalse(judge(case, 0, raw)[0])
        for raw in ['{"stock_reports":{}}', '{"stock_reports":{"first-valid":5}}',
                    '{"error":"invalid","stock_reports":{}}', '[]', '{', '']:
            self.assertFalse(judge(case, 2, raw)[0])

    def test_real_cli_positive_control_and_report(self):
        with tempfile.TemporaryDirectory(prefix='evaluation self test ', dir=Path.cwd()) as root:
            root = Path(root)
            candidate = root / 'control with spaces.py'
            candidate.write_text(Path(__file__).with_name('control_cli.py').read_text(encoding='utf-8'), encoding='utf-8')
            report_path = root / 'report.json'
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / 'evaluate.py'),
                       str(candidate), '--report', str(report_path), '--work-dir', str(root)]
            proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            report = json.loads(report_path.read_text(encoding='utf-8'))
            self.assertTrue(report['all_passed'])
            self.assertEqual(report['total'], len(build_cases()))

    def test_real_cli_mutants_are_detected(self):
        probes = {
            'float': ['binary64-integer-boundary', 'beyond-finite-float'],
            'duplicates': ['duplicate-root', 'escaped-duplicate-row'],
            'count-unvalidated': ['event_count-true', 'event_count-near-integral'],
            'deduplicate': ['identities-repetitions-and-sign'],
            'max-zero': ['illustrative-example'],
            'partial': ['empty-maximum', 'net_units-true'],
        }
        source = Path(__file__).with_name('control_cli.py').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='mutation checks ', dir=Path.cwd()) as root:
            for mode, names in probes.items():
                with self.subTest(mode=mode):
                    candidate = Path(root) / f'{mode}.py'
                    candidate.write_text(source.replace("MODE = 'correct'", f'MODE = {mode!r}'), encoding='utf-8')
                    report = run_suite(candidate, cases=[c for c in build_cases() if c.name in names], work_dir=root)
                    self.assertEqual(report['passed'], 0, report)

    def test_timeout_and_missing_output_fail(self):
        case = Case('smoke', 'test', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[]}}}', {'x': 0})
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            candidate = Path(root) / 'empty.py'
            candidate.write_text('pass\n', encoding='utf-8')
            self.assertFalse(run_suite(candidate, cases=[case], work_dir=root)['all_passed'])
            candidate.write_text('import time\ntime.sleep(5)\n', encoding='utf-8')
            report = run_suite(candidate, cases=[case], timeout=0.1, work_dir=root)
            self.assertFalse(report['all_passed'])
            self.assertIn('resource budget', report['cases'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
