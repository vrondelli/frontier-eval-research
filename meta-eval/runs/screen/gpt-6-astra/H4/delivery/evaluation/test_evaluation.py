"""Self-checks for the evaluator; includes positive and intentional negative controls."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from cases import build_cases
import control_solution
from grade import audit, evaluate, PROTECTED
from oracle import expected, half_away
from test_fares import check_result

HERE = Path(__file__).resolve().parent
CASES = build_cases()
MUTATION_RESULTS = []
MUTATIONS = [
    'trim_strings', 'unicode_digits', 'optional_hyphen', 'dollar_anchor',
    'zero_fare', 'zero_baggage', 'reject_negative_voucher',
    'exclusive_cutoff', 'calendar_validation', 'date_component_comparison',
    'class_boundary', 'omit_baggage', 'uncapped_rebate', 'rebate_per_component',
    'rebate_rounded', 'quarter_nearest', 'exact_quarter_advanced', 'no_quarter_rounding',
    'omit_handling', 'early_rounding', 'priority_surcharged', 'voucher_before_surcharge',
    'voucher_added', 'negative_clamped', 'half_even', 'binary_float', 'truncate_minor',
    'decimal_context_loss', 'excluded_in_mean', 'mean_half_even', 'mean_truncated',
    'sort_exclusions', 'duplicate_exclusion', 'all_class_keys', 'extra_key', 'float_result', 'bool_result',
]

SUBMITTED_TEST = '''import unittest
from fares import settle_fares

class ManualCheck(unittest.TestCase):
    def test_adult(self):
        # C=200, rebate=18, Q=182, subtotal=5+.12*182+2=28.84.
        # 28.84*1.07=30.8588 -> 3086 minor units.
        records = [dict(passenger='a', fare='100', baggage='100', passcode='19000',
                        sailed='2025-06-20', voucher='0')]
        self.assertEqual(settle_fares(records), dict(total_minor=3086, billed=1,
            excluded=[], fares={'a': 3086}, per_class={'adult': 3086}, mean_minor=3086))
'''


def prepare(directory, solution=True):
    original = HERE.parent / 'input' / 'workspace'
    for name in PROTECTED:
        shutil.copyfile(original / name, directory / name)
    source = HERE / 'control_solution.py' if solution else original / 'fares.py'
    shutil.copyfile(source, directory / 'fares.py')
    (directory / 'test_fares.py').write_text(SUBMITTED_TEST, encoding='utf-8')


class EvaluationChecks(unittest.TestCase):
    def tearDown(self):
        control_solution.MUTATION = None

    def test_literal_gold_matches_independent_oracle(self):
        for case in CASES:
            with self.subTest(case=case.name):
                self.assertEqual(expected(case.records), case.expected)

    def test_half_away_integer_arithmetic(self):
        for numerator, denominator, answer in [(1, 2, 1), (-1, 2, -1), (5, 2, 3), (-5, 2, -3),
                                                (249, 100, 2), (-249, 100, -2), (0, 7, 0)]:
            self.assertEqual(half_away(Fraction(numerator, denominator)), answer)

    def test_unique_names_and_identifiers(self):
        self.assertEqual(len(CASES), len({c.name for c in CASES}))
        self.assertEqual({c.rule for c in CASES}, set('KVDTWR'))
        for case in CASES:
            self.assertEqual(len(case.records), len({r['passenger'] for r in case.records}))

    def test_positive_control(self):
        control_solution.MUTATION = None
        for case in CASES:
            with self.subTest(case=case.name):
                check_result(self, control_solution.settle_fares(copy.deepcopy(case.records)), case.expected)

    def test_mutation_sensitivity(self):
        MUTATION_RESULTS.clear()
        for mutation in MUTATIONS:
            control_solution.MUTATION = mutation
            killed_by = None
            reason = None
            for case in CASES:
                try:
                    check_result(self, control_solution.settle_fares(copy.deepcopy(case.records)), case.expected)
                except Exception as exc:
                    killed_by = case.name
                    reason = f'{type(exc).__name__}: {exc}'[:300]
                    break
            MUTATION_RESULTS.append(dict(mutation=mutation, killed_by=killed_by, reason=reason))
            with self.subTest(mutation=mutation):
                self.assertIsNotNone(killed_by, 'Faulty variant survived the entire evaluation')

    def test_positive_runner_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix='.control-', dir=HERE) as temporary:
            directory = Path(temporary)
            self.assertTrue(directory.resolve().is_relative_to(HERE))
            prepare(directory)
            report = evaluate(directory)
            self.assertTrue(report['automated_pass'], report)
            self.assertEqual(report['behavioral_score'], 1)
            self.assertEqual(report['behavior']['run'], len(CASES) + 1)
            self.assertEqual(report['submitted_tests']['run'], 1)

    def test_skeleton_runner_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix='.control-', dir=HERE) as temporary:
            directory = Path(temporary)
            self.assertTrue(directory.resolve().is_relative_to(HERE))
            prepare(directory, solution=False)
            report = evaluate(directory)
            self.assertFalse(report['automated_pass'])
            self.assertFalse(report['behavior']['passed'])
            self.assertEqual(report['behavioral_score'], 0)

    def test_empty_submitted_suite_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='.control-', dir=HERE) as temporary:
            directory = Path(temporary)
            self.assertTrue(directory.resolve().is_relative_to(HERE))
            prepare(directory)
            (directory / 'test_fares.py').write_text('import unittest\n', encoding='utf-8')
            report = evaluate(directory)
            self.assertTrue(report['behavior']['passed'])
            self.assertFalse(report['submitted_tests']['passed'])
            self.assertFalse(report['automated_pass'])

    def test_integrity_and_import_audit(self):
        with tempfile.TemporaryDirectory(prefix='.control-', dir=HERE) as temporary:
            directory = Path(temporary)
            self.assertTrue(directory.resolve().is_relative_to(HERE))
            prepare(directory)
            self.assertTrue(audit(directory)['passed'])
            (directory / 'README.md').write_text('changed', encoding='utf-8')
            self.assertFalse(audit(directory)['passed'])
            shutil.copyfile(HERE.parent / 'input' / 'workspace' / 'README.md', directory / 'README.md')
            (directory / 'test_fares.py').write_text('from farelib import parse_fare\n', encoding='utf-8')
            self.assertFalse(audit(directory)['passed'])
            (directory / 'test_fares.py').unlink()
            self.assertFalse(audit(directory)['passed'])

    def test_original_inputs_unchanged(self):
        manifest = json.loads((HERE.parent / 'MANIFEST.json').read_text(encoding='utf-8'))
        for entry in manifest['files']:
            path = HERE.parent / entry['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'], entry['path'])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EvaluationChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(schema_version='ferry-evaluation-validation/v1', python=sys.version,
                  self_checks_run=result.testsRun, passed=result.wasSuccessful(),
                  behavioral_cases=len(CASES) + 1, mutations=MUTATION_RESULTS,
                  failures=[{'test': str(t), 'traceback': trace} for t, trace in result.failures + result.errors])
    (HERE / 'validation_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
