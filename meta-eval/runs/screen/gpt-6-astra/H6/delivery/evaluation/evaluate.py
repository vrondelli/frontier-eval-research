"""Run a supplied summarize.py as a subprocess. No third-party dependencies."""
import argparse
from collections import Counter
from decimal import Decimal, DecimalException
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from cases import build_cases


def reject_constant(value):
    raise ValueError(f'non-JSON number: {value}')


def parse_output(raw):
    # Decimal parsing is exact and independent of the active precision context.
    # Do not perform Decimal arithmetic or convert through float.
    return json.loads(raw, parse_int=Decimal, parse_float=Decimal,
                      parse_constant=reject_constant)


def judge(case, returncode, output):
    if case.expected is None:
        if returncode == 0:
            return False, 'invalid input exited zero'
        if output is None:
            return True, 'invalid input rejected without output'
        try:
            value = parse_output(output)
        except (ValueError, UnicodeError, DecimalException, RecursionError) as exc:
            return False, f'failure output is not a JSON error envelope: {exc}'
        if not isinstance(value, dict) or 'stock_reports' in value:
            return False, 'failure wrote a results object or a non-envelope value'
        return True, 'invalid input rejected with a non-result envelope'
    if returncode != 0:
        return False, f'valid input exited {returncode}'
    if output is None:
        return False, 'missing output file'
    try:
        value = parse_output(output)
    except (ValueError, UnicodeError, DecimalException, RecursionError) as exc:
        return False, f'invalid output JSON: {exc}'
    if not isinstance(value, dict) or not isinstance(value.get('stock_reports'), dict):
        return False, 'missing stock_reports object'
    reports = value['stock_reports']
    if reports.keys() != case.expected.keys():
        return False, 'report identifiers differ from input identifiers'
    for key, expected in case.expected.items():
        actual = reports[key]
        if not isinstance(actual, Decimal) or not actual.is_finite() or actual != expected:
            return False, f'incorrect integer result for {key!r}'
    return True, 'exact results matched'


def run_suite(candidate, *, python=sys.executable, timeout=10.0, work_dir=None, cases=None):
    candidate = Path(candidate).resolve()
    if not candidate.is_file():
        raise ValueError(f'candidate script does not exist: {candidate}')
    cases = build_cases() if cases is None else cases
    records = []
    with tempfile.TemporaryDirectory(prefix='numeric export evaluation ',
                                     dir=Path.cwd() if work_dir is None else Path(work_dir).resolve()) as root:
        for index, case in enumerate(cases):
            folder = Path(root) / f'{index:03d} {case.name}'
            folder.mkdir()
            source = folder / 'input data.json'
            destination = folder / 'output data.json'
            source.write_bytes(case.raw.encode('utf-8'))
            command = [str(python), str(candidate), str(source), str(destination)]
            started = time.monotonic()
            returncode = None
            try:
                completed = subprocess.run(command, cwd=candidate.parent, capture_output=True,
                                           timeout=timeout, check=False)
                returncode = completed.returncode
                output = destination.read_bytes() if destination.is_file() else None
                passed, reason = judge(case, returncode, output)
                stderr = completed.stderr.decode('utf-8', errors='replace')[-2000:]
            except subprocess.TimeoutExpired:
                passed, reason, stderr = False, f'exceeded {timeout:g}s resource budget', ''
            except OSError as exc:
                passed, reason, stderr = False, f'CLI execution or output read failed: {exc}', ''
            records.append({'name': case.name, 'category': case.category,
                            'valid_input': case.expected is not None, 'passed': passed,
                            'reason': reason, 'returncode': returncode,
                            'seconds': round(time.monotonic() - started, 4),
                            'command': command, 'stderr_tail': stderr})
    passed_count = sum(record['passed'] for record in records)
    return {'all_passed': passed_count == len(records), 'passed': passed_count,
            'total': len(records), 'case_pass_fraction': passed_count / len(records),
            'categories': {category: {
                'passed': sum(r['passed'] for r in records if r['category'] == category),
                'total': count,
            } for category, count in sorted(Counter(r['category'] for r in records).items())},
            'cases': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path, help='path to implemented summarize.py')
    parser.add_argument('--python', default=sys.executable, help='candidate Python interpreter')
    parser.add_argument('--timeout', type=float, default=10.0, help='per-command seconds (resource budget)')
    parser.add_argument('--report', type=Path, help='optional machine-readable JSON report')
    parser.add_argument('--work-dir', type=Path, help='parent for temporary input/output directories')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    try:
        report = run_suite(args.candidate, python=args.python, timeout=args.timeout, work_dir=args.work_dir)
    except ValueError as exc:
        parser.error(str(exc))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"{report['passed']}/{report['total']} cases passed")
    for record in report['cases']:
        if not record['passed']:
            print(f"FAIL {record['name']}: {record['reason']}")
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
