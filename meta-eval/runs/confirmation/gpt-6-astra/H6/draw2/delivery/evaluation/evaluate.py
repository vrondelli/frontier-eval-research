"""Run a submitted summarize.py as a subprocess against local contract probes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from cases import build_cases
from numbers_exact import Number, loads


def check_output(case, returncode, output_path):
    if case.expected is not None and returncode != 0:
        return f'valid input exited {returncode}'
    if case.expected is None and returncode == 0:
        return 'invalid input exited zero'
    if not output_path.exists():
        return 'missing output file' if case.expected is not None else None
    try:
        text = output_path.read_bytes().decode('utf-8')
        if case.expected is None and not text.strip():
            return None  # No result was emitted.
        output = loads(text)
    except (ValueError, OSError, RecursionError) as error:
        return f'output is not an unambiguous UTF-8 JSON document: {str(error)[:200]}'
    if not isinstance(output, dict):
        return 'output must be an object (results or an error envelope)'
    if case.expected is None:
        return 'invalid input wrote stock_reports' if 'stock_reports' in output else None
    reports = output.get('stock_reports')
    if not isinstance(reports, dict):
        return 'stock_reports is missing or is not an object'
    if set(reports) != set(case.expected):
        return 'stock_reports identifiers do not exactly match the input identifiers'
    for key, expected in case.expected.items():
        actual = reports[key]
        if not isinstance(actual, Number) or not actual.integral:
            return f'{key!r}: result is not a mathematical integer JSON number'
        if actual != Number.parse(expected):
            return f'{key!r}: incorrect exact numeric value'
    return None


def run_suite(command, cwd, cases=None, timeout=5.0):
    cases = build_cases() if cases is None else cases
    results = []
    # The CLI must handle spaces in both filenames and directories.
    with tempfile.TemporaryDirectory(prefix='numeric export evaluation ', dir=Path.cwd()) as temp:
        for index, case in enumerate(cases):
            directory = Path(temp) / f'{index:03} {case.name}'
            directory.mkdir()
            source = directory / 'input data.json'
            target = directory / 'output data.json'
            source.write_bytes(case.data)
            invocation = [*command, str(source), str(target)]
            started = time.monotonic()
            returncode = None
            stdout = stderr = ''
            try:
                process = subprocess.run(invocation, cwd=cwd, capture_output=True,
                                         timeout=timeout)
                returncode = process.returncode
                stdout = process.stdout.decode('utf-8', errors='replace')[-2000:]
                stderr = process.stderr.decode('utf-8', errors='replace')[-2000:]
                reason = check_output(case, returncode, target)
            except subprocess.TimeoutExpired:
                reason = f'command exceeded evaluator timeout ({timeout:g}s)'
            except OSError as error:
                reason = f'command could not run: {error}'
            results.append({
                'name': case.name, 'category': case.category,
                'expected_valid': case.expected is not None,
                'input_bytes': len(case.data), 'passed': reason is None,
                'input_sha256': hashlib.sha256(case.data).hexdigest(),
                'reason': reason, 'returncode': returncode,
                'seconds': round(time.monotonic() - started, 4),
                'stdout_tail': stdout, 'stderr_tail': stderr,
            })
    groups = {}
    for result in results:
        group = groups.setdefault(result['category'], {'passed': 0, 'total': 0})
        group['total'] += 1
        group['passed'] += int(result['passed'])
    passed = sum(result['passed'] for result in results)
    root = Path(__file__).resolve().parents[1]
    sources = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (
        'input/task.txt', 'input/workspace/README.md', 'input/workspace/input.schema.json',
        'input/workspace/output.schema.json', 'input/workspace/example.json')}
    return {'evaluation_version': 1, 'command': command, 'cwd': str(cwd),
            'evaluator_python': sys.version, 'source_sha256': sources,
            'timeout_seconds_per_case': timeout, 'passed': passed,
            'total': len(results), 'all_passed': passed == len(results),
            'categories': groups, 'cases': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True,
                        help='path to the submitted summarize.py')
    parser.add_argument('--python', default=sys.executable,
                        help='Python executable used to launch the candidate')
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--report', type=Path, default=Path('evaluation-report.json'))
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    if not candidate.is_file():
        parser.error(f'candidate does not exist: {candidate}')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    report = run_suite([args.python, str(candidate)], candidate.parent, timeout=args.timeout)
    report['candidate_sha256'] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"{report['passed']}/{report['total']} probes passed; report: {args.report}")
    for case in report['cases']:
        if not case['passed']:
            print(f"FAIL {case['name']}: {case['reason']}")
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
