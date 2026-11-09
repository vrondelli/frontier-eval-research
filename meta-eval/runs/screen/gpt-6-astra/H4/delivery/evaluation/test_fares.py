"""External unittest suite. No farelib import; expectations come from the rules."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

from cases import build_cases

HERE = Path(__file__).resolve().parent
CANDIDATE = Path(os.environ.get('FERRY_CANDIDATE_DIR', HERE.parent / 'input' / 'workspace')).resolve()
CASES = build_cases()


def load_candidate(directory):
    sys.path.insert(0, str(directory))
    spec = importlib.util.spec_from_file_location('_evaluated_fares', directory / 'fares.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.settle_fares


def check_result(test, actual, expected):
    test.assertIs(type(actual), dict, 'Return value must be a dict')
    test.assertEqual(set(actual), set(expected), 'Exact top-level keys')
    for key in ('total_minor', 'billed', 'mean_minor'):
        test.assertIs(type(actual[key]), int, f'{key} must be int, not bool/float/Decimal')
    test.assertIs(type(actual['excluded']), list)
    for identifier in actual['excluded']:
        test.assertIs(type(identifier), str)
    for key in ('fares', 'per_class'):
        test.assertIs(type(actual[key]), dict)
        for identifier, amount in actual[key].items():
            test.assertIs(type(identifier), str)
            test.assertIs(type(amount), int, f'{key}[{identifier!r}] must be int')
    test.assertEqual(actual, expected)


class FerryEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settle = staticmethod(load_candidate(CANDIDATE))

    def test_repeated_calls(self):
        """No earlier calls may change a later result or a returned prior result."""
        first = self.settle(copy.deepcopy(CASES[1].records))
        snapshot = copy.deepcopy(first)
        check_result(self, first, CASES[1].expected)
        check_result(self, self.settle([]), CASES[0].expected)
        self.assertEqual(first, snapshot)
        check_result(self, self.settle(copy.deepcopy(CASES[1].records)), CASES[1].expected)


def make_test(case):
    def test(self):
        check_result(self, self.settle(copy.deepcopy(case.records)), case.expected)
    test.__doc__ = f'Rule {case.rule}: {case.rationale}'
    return test


for case in CASES:
    setattr(FerryEvaluation, 'test_' + case.name, make_test(case))


def run(report_path):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FerryEvaluation)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    failures = [{'test': str(test), 'traceback': trace} for test, trace in result.failures + result.errors]
    report = dict(planned=len(CASES) + 1, run=result.testsRun, failures=failures,
                  passed=result.wasSuccessful() and result.testsRun == len(CASES) + 1)
    Path(report_path).write_text(json.dumps(report, indent=2), encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    CANDIDATE = args.candidate.resolve()
    raise SystemExit(run(args.report))
