"""Reproducible authored-control verification, with optional required sandbox."""
import hashlib
import io
from pathlib import Path
import platform
import sys
import time
import unittest

from .controls import negative_controls, positive_controls, reference_answer
from .grader import grade
from .schema import validate_report


def verify(sandbox=False):
    start = time.monotonic()
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('e1eval.test_eval')
    tests = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    result = {'schema_version': 'e1-verification/v1', 'verified': tests.wasSuccessful(),
              'scope': 'sandbox_and_trusted_controls' if sandbox else 'trusted_authored_controls',
              'python': sys.version, 'platform': platform.platform(),
              'unit_tests': {'run': tests.testsRun, 'failures': len(tests.failures),
                             'errors': len(tests.errors), 'log': output.getvalue()},
              'controls': [], 'sandbox_probe': None, 'sandbox_reports': [],
              'limitations': ['Authored controls are not fresh model performance.',
                              'Finite schedules do not establish all interleavings, throughput, or latency quality.',
                              'Explanation quality requires independent human review.']}
    for expected, controls in [('pass', positive_controls()), ('fail', negative_controls())]:
        for name, answer in controls.items():
            report = grade(answer, _trusted_control=True)
            validate_report(report)
            correct = report['status'] == expected
            result['controls'].append({'name': name, 'expected': expected, 'matched': correct, 'report': report})
            result['verified'] = result['verified'] and correct
    probe = grade(reference_answer())
    validate_report(probe)
    result['sandbox_probe'] = probe
    if probe['status'] == 'unavailable':
        result['limitations'].append('Linux sandbox execution unavailable on this host; trusted-control mode is not isolation evidence.')
    if sandbox:
        result['verified'] = result['verified'] and probe['status'] == 'pass'
        if probe['status'] == 'pass':
            for expected, controls in [('pass', positive_controls()), ('fail', negative_controls())]:
                for name, answer in controls.items():
                    report = grade(answer)
                    validate_report(report)
                    correct = report['status'] == expected
                    result['sandbox_reports'].append({'name': name, 'expected': expected, 'matched': correct, 'report': report})
                    result['verified'] = result['verified'] and correct
    elif probe['status'] not in ('pass', 'unavailable'):
        result['verified'] = False
    result['source_sha256'] = {str(path.relative_to(Path(__file__).parent)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(Path(__file__).parent.rglob('*'))
                                if path.is_file() and '__pycache__' not in path.parts}
    result['elapsed_seconds'] = round(time.monotonic() - start, 3)
    return result
