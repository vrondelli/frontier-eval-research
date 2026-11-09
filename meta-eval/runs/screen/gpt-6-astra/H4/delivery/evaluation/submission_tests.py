"""Run the submitted test_fares.py in a separate process, with a test count."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest


def main():
    candidate, report = map(Path, sys.argv[1:])
    sys.path.insert(0, str(candidate))
    try:
        spec = importlib.util.spec_from_file_location('_submitted_tests', candidate / 'test_fares.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        data = dict(run=result.testsRun, skipped=len(result.skipped),
                    passed=result.wasSuccessful() and result.testsRun > len(result.skipped),
                    failures=[{'test': str(t), 'traceback': trace} for t, trace in result.failures + result.errors])
    except Exception as exc:
        data = dict(run=0, passed=False, error=f'{type(exc).__name__}: {exc}')
    report.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return 0 if data['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
