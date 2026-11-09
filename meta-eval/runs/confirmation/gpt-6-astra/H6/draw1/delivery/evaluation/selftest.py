"""Exercise the evaluator with actual subprocess controls and direct judge tests."""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest

from evaluate import Case, ExactNumber, cases, judge, run


# Independent, bounded test control, not a general production implementation.
# Precision 20000 covers this corpus; it does not bound legal task inputs.
CONTROL = r'''
import json
from decimal import Decimal, localcontext
from pathlib import Path
import sys

MODE = __MODE__
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

def pairs(items):
    out = {}
    for key, value in items:
        if key in out and MODE != 'duplicates':
            raise ValueError('duplicate')
        out[key] = value
    return out

def reject(token):
    raise ValueError(token)

def main():
    target = Path(sys.argv[2])
    reports = {}
    try:
        numeric = float if MODE == 'float' else Decimal
        data = json.loads(Path(sys.argv[1]).read_bytes().decode('utf-8'),
                          parse_int=numeric, parse_float=numeric,
                          parse_constant=reject, object_pairs_hook=pairs)
        if not isinstance(data, dict) or set(data) != {'adjustment_sheets'}:
            raise ValueError('root')
        sheets = data['adjustment_sheets']
        if not isinstance(sheets, dict) or not sheets:
            raise ValueError('sheets')
        for key, row in sheets.items():
            if not key or not isinstance(row, dict):
                raise ValueError('row')
            if MODE != 'extra-fields' and set(row) != {'stat', 'turns'}:
                raise ValueError('fields')
            stat, values = row['stat'], row['turns']
            if stat not in ['net_units', 'event_count', 'largest_adjustment']:
                raise ValueError('stat')
            if not isinstance(values, list):
                raise ValueError('turns')
            if stat == 'largest_adjustment' and not values:
                if MODE == 'empty-max':
                    reports[key] = Decimal(0)
                    continue
                raise ValueError('empty')
            checked = []
            for value in values:
                if MODE == 'booleans' and isinstance(value, bool):
                    value = Decimal(int(value))
                if MODE == 'skip-count-validation' and stat == 'event_count':
                    checked.append(value)
                    continue
                if not isinstance(value, (Decimal, float)):
                    raise ValueError('number')
                if MODE == 'truncate':
                    value = Decimal(int(value))
                if isinstance(value, Decimal):
                    if not value.is_finite() or value != value.to_integral_value():
                        raise ValueError('integer')
                    if MODE == 'integer-lexemes' and value.as_tuple().exponent < 0:
                        raise ValueError('decimal encoding')
                elif not value.is_integer():
                    raise ValueError('integer')
                checked.append(value)
            with localcontext() as context:
                context.prec = 28 if MODE == 'decimal28' else 20000
                if stat == 'net_units':
                    answer = sum(checked)
                elif stat == 'event_count':
                    answer = len(set(checked)) if MODE == 'distinct-count' else len(checked)
                else:
                    answer = max(abs(v) for v in checked) if MODE == 'absolute-max' else max(checked)
            reports[key] = answer
        if MODE == 'missing-key':
            reports.pop(next(iter(reports)))
        def number(value):
            if MODE == 'decimal-output':
                return str(int(value)) + '.0'
            if MODE == 'plain-output':
                return str(int(value))
            return format(Decimal(value), 'E')
        target.write_text('{"stock_reports":{' + ','.join(
            json.dumps(k) + ':' + number(v) for k, v in reports.items())
            + '},"diagnostic":{"ratio":0.5,"ok":true}}', encoding='utf-8')
        return 0
    except Exception:
        target.write_text('{"stock_reports":{}}' if MODE == 'failure-results'
                          else '{"error":"invalid input"}', encoding='utf-8')
        return 0 if MODE == 'zero-exit' else 1

raise SystemExit(main())
'''


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.valid = Case('test', 'test', b'', {'x': '9007199254740993', 'z': '0'})
        self.invalid = Case('bad', 'test', b'', None)

    def test_equivalent_number_encodings_and_metadata(self):
        for token in ['9007199254740993', '9007199254740993.0', '90071992547409930e-1']:
            raw = ('{"stock_reports":{"x":' + token + ',"z":-0e999},'
                   '"metadata":{"number":0.125,"bool":true}}').encode()
            self.assertTrue(judge(self.valid, 0, raw)[0])

    def test_wrong_results_and_types(self):
        for value in ['9007199254740992', '9007199254740993.1', 'true',
                      '"9007199254740993"', 'null', '[]', '{}', 'NaN', 'Infinity']:
            raw = ('{"stock_reports":{"x":' + value + ',"z":0}}').encode()
            self.assertFalse(judge(self.valid, 0, raw)[0], value)

    def test_shape_keys_exit_and_missing_output(self):
        for raw in [b'{}', b'[]', b'{"stock_reports":[]}',
                    b'{"stock_reports":{"x":9007199254740993}}',
                    b'{"stock_reports":{"x":9007199254740993,"z":0,"extra":1}}',
                    b'not JSON', b'\xff', None]:
            self.assertFalse(judge(self.valid, 0, raw)[0])
        self.assertFalse(judge(self.valid, 1, b'{"stock_reports":{"x":9007199254740993,"z":0}}')[0])

    def test_error_output_policy(self):
        for raw in [None, b'', b' \n', b'{"error":"bad input"}',
                    b'{"stock_reports":null,"error":"bad input"}']:
            self.assertTrue(judge(self.invalid, 1, raw)[0])
        for raw in [b'{"stock_reports":{}}', b'{"stock_reports":{"partial":1}}',
                    b'{"stock_reports":{},"error":"failed"}', b'{"stock_reports":']:
            self.assertFalse(judge(self.invalid, 1, raw)[0])
        self.assertFalse(judge(self.invalid, 0, None)[0])

    def test_no_digit_conversion_limit_or_float_rounding_in_judge(self):
        case = Case('big', 'test', b'', {'x': '1e5000'})
        self.assertTrue(judge(case, 0, b'{"stock_reports":{"x":1e5000}}')[0])
        self.assertTrue(judge(case, 0, b'{"stock_reports":{"x":1' + b'0' * 5000 + b'}}')[0])
        self.assertFalse(judge(case, 0, b'{"stock_reports":{"x":9e4999}}')[0])

    def test_exponents_outside_decimal_library_limits(self):
        case = Case('zero', 'test', b'', {'x': '0'})
        self.assertTrue(judge(case, 0, b'{"stock_reports":{"x":-0.0e' + b'9' * 5000 + b'}}')[0])
        self.assertFalse(judge(case, 0, b'{"stock_reports":{"x":1e-' + b'9' * 5000 + b'}}')[0])
        self.assertEqual(ExactNumber.parse('100e99999999999999999999'),
                         ExactNumber.parse('1e100000000000000000001'))

    def test_canonical_number_comparison_against_decimal(self):
        tokens = ['0', '-0', '0.00e-900', '1', '1.00', '10e-1', '0.1e1',
                  '-100', '-1e2', '1e400', '10e399', '1e-400', '2', '0.5', '5e-1']
        for left in tokens:
            for right in tokens:
                self.assertEqual(ExactNumber.parse(left) == ExactNumber.parse(right),
                                 Decimal(left) == Decimal(right))

    def test_fixture_sizes_names_and_exact_expected_integers(self):
        corpus = cases()
        self.assertEqual(len(corpus), len({c.name for c in corpus}))
        self.assertEqual(max(len(c.payload) for c in corpus), 8192)
        for case in corpus:
            self.assertLessEqual(len(case.payload), 8192)
            if case.expected is not None:
                for value in case.expected.values():
                    d = Decimal(value)
                    self.assertTrue(d.is_finite() and d == d.to_integral_value())


def exercise_controls(*, full_mutations=False):
    records = []
    corpus = cases()
    mutants = {
        'float': 'decimal-cancellation',
        'decimal28': 'beyond-decimal-default-precision',
        'integer-lexemes': 'integral-encodings',
        'distinct-count': 'repeated-events',
        'absolute-max': 'example',
        'empty-max': 'empty-largest',
        'booleans': 'net_units-rejects-true',
        'truncate': 'net_units-rejects-fraction',
        'skip-count-validation': 'event_count-rejects-fraction',
        'duplicates': 'escaped-duplicate-identifier',
        'extra-fields': 'row-extra',
        'missing-key': 'identifier-preservation',
        'failure-results': 'invalid-row-last',
        'zero-exit': 'root-null',
    }
    with tempfile.TemporaryDirectory(prefix='numeric control scripts ', dir=Path.cwd()) as temporary:
        folder = Path(temporary)
        for mode in ['exact', 'plain-output', 'decimal-output'] + list(mutants):
            candidate = folder / (mode + ' summarize.py')
            candidate.write_text(CONTROL.replace('__MODE__', repr(mode)), encoding='utf-8')
            selected = ([case for case in corpus if case.name == mutants[mode]]
                        if mode in mutants and not full_mutations else corpus)
            report = run(candidate, selected=selected)
            failed = [row['name'] for row in report['cases'] if not row['passed']]
            if mode in mutants:
                assert mutants[mode] in failed, f'Mutant {mode} escaped its discriminating probe'
            else:
                assert report['passed'], f'Positive control {mode} failed: {failed}'
            records.append({'control': mode, 'expected': 'fail' if mode in mutants else 'pass',
                            'passed_cases': report['passed_cases'],
                            'total_cases': report['total_cases'], 'failed_cases': failed})
            print(f'{mode}: {report["passed_cases"]}/{report["total_cases"]}', flush=True)

        # Actual runner behavior, beyond semantic mutations.
        probe = corpus[0]
        for name, source in {
            'no-output': 'raise SystemExit(0)',
            'crash': 'raise RuntimeError("control crash")',
            'timeout': 'import time\ntime.sleep(10)',
            'malformed-output': 'import pathlib,sys\npathlib.Path(sys.argv[2]).write_text("{")',
        }.items():
            candidate = folder / (name + '.py')
            candidate.write_text(source, encoding='utf-8')
            report = run(candidate, timeout=0.2 if name == 'timeout' else 10, selected=[probe])
            assert not report['passed'], f'Runner accepted {name}'
            if name == 'timeout':
                assert 'timeout' in report['cases'][0]['reason']
            records.append({'control': name, 'expected': 'fail',
                            'reason': report['cases'][0]['reason']})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--full-mutations', action='store_true',
                        help='Run each faulty control on the full corpus (slower)')
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(JudgeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    records = exercise_controls(full_mutations=args.full_mutations)
    report = {'passed': True, 'judge_tests': result.testsRun, 'corpus_size': len(cases()),
              'controls': records}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Evaluator self-test passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
