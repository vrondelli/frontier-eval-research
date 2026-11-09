"""Black-box evaluation of the warehouse numeric export CLI (stdlib only)."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import time


@dataclass(frozen=True)
class Case:
    name: str
    category: str
    payload: bytes
    expected: dict[str, str] | None  # None means invalid input.


@dataclass(frozen=True)
class ExactNumber:
    """Canonical decimal coefficient * 10**exponent, without expanding powers.

    Avoids binary rounding, Decimal exponent bounds, and int digit limits.
    JSON's decoder supplies valid numeric lexemes to this callback.
    """
    coefficient: str
    exponent: int

    @classmethod
    def parse(cls, token: str):
        match = re.fullmatch(r'(-?)(0|[1-9][0-9]*)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?', token)
        if match is None:
            raise ValueError('Invalid JSON number')
        sign, whole, fraction, exp_text = match.groups()
        fraction = fraction or ''
        digits = (whole + fraction).lstrip('0')
        if not digits:
            return cls('0', 0)
        exp_digits = (exp_text or '0').lstrip('+-')
        exponent = 0
        for start in range(0, len(exp_digits), 1000):
            chunk = exp_digits[start:start + 1000]
            exponent = exponent * 10**len(chunk) + int(chunk)
        if exp_text and exp_text.startswith('-'):
            exponent = -exponent
        trimmed = digits.rstrip('0')
        exponent += len(digits) - len(trimmed) - len(fraction)
        return cls(sign + trimmed, exponent)


def document(rows):
    """Build raw JSON without converting numeric lexemes through float."""
    return ('{"adjustment_sheets":{' + ','.join(
        json.dumps(key, ensure_ascii=False) + ':{"stat":' + json.dumps(stat)
        + ',"turns":[' + ','.join(values) + ']}'
        for key, stat, values in rows) + '}}').encode('utf-8')


def cases() -> list[Case]:
    result = []

    def valid(name, category, rows, expected):
        result.append(Case(name, category, document(rows), expected))

    def invalid(name, payload, category='validation'):
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        result.append(Case(name, category, payload, None))

    valid('example', 'operations', [
        ('warehouse-sample-1-0', 'net_units', ['4', '-3', '4']),
        ('warehouse-sample-1-1', 'event_count', ['0', '-2', '-2']),
        ('warehouse-sample-1-2', 'largest_adjustment', ['-9', '-3', '-4']),
    ], {'warehouse-sample-1-0': '5', 'warehouse-sample-1-1': '3',
        'warehouse-sample-1-2': '-3'})
    valid('empty-identities', 'operations', [
        ('sum', 'net_units', []), ('count', 'event_count', []),
    ], {'sum': '0', 'count': '0'})
    valid('repeated-events', 'operations', [
        ('count', 'event_count', ['7'] * 37),
        ('sum', 'net_units', ['-4'] * 19),
        ('max', 'largest_adjustment', ['-8', '-2', '-8']),
    ], {'count': '37', 'sum': '-76', 'max': '-2'})
    valid('identifier-preservation', 'structure', [
        (key, 'net_units', [str(i)]) for i, key in enumerate(
            [' ', '0', 'stock_reports', '__proto__', 'a/b', 'é仓📦', 'quote"\\\n'])
    ], {key: str(i) for i, key in enumerate(
        [' ', '0', 'stock_reports', '__proto__', 'a/b', 'é仓📦', 'quote"\\\n'])})
    valid('integral-encodings', 'numeric', [
        ('sum', 'net_units', ['1.0', '20e-1', '-3.000', '0e-1000', '-0.0']),
        ('count', 'event_count', ['1e3', '-20.0', '100e-2']),
        ('max', 'largest_adjustment', ['-30e-1', '-2.000', '-10e2']),
    ], {'sum': '0', 'count': '3', 'max': '-2'})
    valid('binary64-cancellation', 'numeric', [
        ('sum', 'net_units', ['9007199254740993', '-9007199254740992']),
        ('max', 'largest_adjustment', ['9007199254740992', '9007199254740993']),
    ], {'sum': '1', 'max': '9007199254740993'})
    valid('decimal-cancellation', 'numeric', [
        ('sum', 'net_units', ['9007199254740993.0', '-9007199254740992.0']),
        ('max', 'largest_adjustment', ['-9007199254740993.0', '-9007199254740992.0']),
    ], {'sum': '1', 'max': '-9007199254740992'})
    huge = '123456789012345678901234567890123456789012345678901234567890'
    valid('beyond-decimal-default-precision', 'numeric', [
        ('sum', 'net_units', [huge, '1', '-' + huge]),
        ('max', 'largest_adjustment', ['-' + huge, '-' + str(int(huge) - 1)]),
    ], {'sum': '1', 'max': '-' + str(int(huge) - 1)})
    valid('exponents-beyond-float-range', 'numeric', [
        ('sum', 'net_units', ['1e400', '3', '-1e400']),
        ('max', 'largest_adjustment', ['-1e401', '-1e400']),
        ('count', 'event_count', ['1e400', '-1e400']),
    ], {'sum': '3', 'max': '-1e400', 'count': '2'})
    valid('large-integral-exponent', 'numeric', [
        ('sum', 'net_units', ['1e5000', '1e5000']),
        ('count', 'event_count', ['1e5000']),
    ], {'sum': '2e5000', 'count': '1'})
    # This legal input exceeds Python's usual 4300-digit int conversion limit.
    giant = '9' * 5000
    valid('long-integer-token', 'numeric', [
        ('max', 'largest_adjustment', [giant]),
    ], {'max': giant})
    valid('long-fractional-zero-tail', 'numeric', [
        ('sum', 'net_units', ['2.' + '0' * 1000, '-1']),
    ], {'sum': '1'})

    rng = random.Random(20261108)
    for index in range(16):
        rows, expected = [], {}
        for j in range(rng.randint(1, 9)):
            stat = rng.choice(['net_units', 'event_count', 'largest_adjustment'])
            values = [rng.randint(-10**35, 10**35)
                      for _ in range(rng.randint(1 if stat == 'largest_adjustment' else 0, 25))]
            key = f'generated-{index}-{j}-仓'
            tokens = [str(v) + rng.choice(['', '.0', 'e0', '00e-2']) for v in values]
            answer = (sum(values) if stat == 'net_units' else
                      len(values) if stat == 'event_count' else max(values))
            rows.append((key, stat, tokens))
            expected[key] = str(answer)
        valid(f'generated-{index:02}', 'generalization', rows, expected)

    rows = [(f'row-{i}', 'net_units', [str(i), '-1']) for i in range(100)]
    valid('many-identifiers', 'structure', rows, {f'row-{i}': str(i-1) for i in range(100)})
    valid('many-turns', 'structure', [('events', 'event_count', ['0'] * 2000)], {'events': '2000'})
    boundary = document([('仓📦', 'net_units', ['1', '-1'])])
    result.append(Case('exact-8192-byte-input', 'structure',
                       boundary + b' ' * (8192 - len(boundary)), {'仓📦': '0'}))

    for name, payload in {
        'root-null': 'null', 'root-array': '[]', 'root-number': '1',
        'root-string': '"x"', 'root-boolean': 'true',
        'missing-sheets': '{}', 'empty-sheets': '{"adjustment_sheets":{}}',
        'sheets-array': '{"adjustment_sheets":[]}',
        'sheets-null': '{"adjustment_sheets":null}',
        'root-extra': '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]}},"extra":0}',
        'empty-identifier': '{"adjustment_sheets":{"":{"stat":"net_units","turns":[]}}}',
    }.items():
        invalid(name, payload)

    for name, row in {
        'row-null': 'null', 'row-array': '[]', 'row-number': '2',
        'row-empty': '{}', 'missing-stat': '{"turns":[]}',
        'missing-turns': '{"stat":"net_units"}',
        'unknown-stat': '{"stat":"sum","turns":[1]}',
        'wrong-stat-case': '{"stat":"NET_UNITS","turns":[1]}',
        'stat-null': '{"stat":null,"turns":[]}',
        'row-extra': '{"stat":"net_units","turns":[],"extra":1}',
        'turns-null': '{"stat":"net_units","turns":null}',
        'turns-object': '{"stat":"net_units","turns":{}}',
        'turns-string': '{"stat":"net_units","turns":"123"}',
        'turns-number': '{"stat":"net_units","turns":1}',
        'empty-largest': '{"stat":"largest_adjustment","turns":[]}',
    }.items():
        invalid(name, '{"adjustment_sheets":{"a":' + row + '}}')

    # Every branch must validate every measurement, even event_count.
    bad_tokens = {
        'true': 'true', 'false': 'false', 'null': 'null', 'string': '"1"',
        'array': '[]', 'object': '{}', 'fraction': '1.5',
        'near-integer': '1.00000000000000000000000000000000001',
        'large-fraction': '9007199254740992.5',
        'tiny-nonzero': '1e-400', 'negative-fraction': '-2.1',
    }
    for stat in ['net_units', 'event_count', 'largest_adjustment']:
        for name, token in bad_tokens.items():
            invalid(f'{stat}-rejects-{name}', document([('a', stat, ['0', token, '2'])]),
                    'numeric-validation')

    for name, payload in {
        'duplicate-top-level': '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]}},"adjustment_sheets":{"b":{"stat":"net_units","turns":[]}}}',
        'duplicate-identifier': '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1]},"a":{"stat":"net_units","turns":[2]}}}',
        'duplicate-stat': '{"adjustment_sheets":{"a":{"stat":"event_count","stat":"net_units","turns":[2]}}}',
        'duplicate-turns': '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1],"turns":[2]}}}',
        'escaped-duplicate-identifier': r'{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]},"\u0061":{"stat":"net_units","turns":[]}}}',
        'escaped-duplicate-member': r'{"adjustment_sheets":{"a":{"stat":"net_units","turns":[],"\u0074urns":[1]}}}',
    }.items():
        invalid(name, payload, 'duplicates')

    for name, token in {'nan': 'NaN', 'infinity': 'Infinity', 'negative-infinity': '-Infinity',
                        'leading-zero': '01', 'plus-sign': '+1', 'bare-dot': '1.',
                        'incomplete-exponent': '1e'}.items():
        invalid(name, document([('a', 'net_units', [token])]), 'json')
    invalid('trailing-comma', '{"adjustment_sheets":{},}', 'json')
    invalid('truncated-json', '{"adjustment_sheets":', 'json')
    invalid('two-json-documents', document([('a', 'net_units', ['1'])]) + b'{}', 'json')
    invalid('invalid-utf8', b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[]}}}', 'json')
    for bad_first in [False, True]:
        rows = [('good', 'net_units', ['4', '5']), ('bad', 'largest_adjustment', [])]
        if bad_first:
            rows.reverse()
        invalid('invalid-row-' + ('first' if bad_first else 'last'), document(rows), 'atomicity')
    assert len({case.name for case in result}) == len(result)
    assert all(len(case.payload) <= 8192 for case in result)
    return result


def reject_constant(token):
    raise ValueError('Non-JSON numeric constant: ' + token)


def read_output(raw: bytes):
    return json.loads(raw.decode('utf-8'), parse_int=ExactNumber.parse, parse_float=ExactNumber.parse,
                      parse_constant=reject_constant)


def judge(case: Case, returncode: int, output: bytes | None) -> tuple[bool, str]:
    if case.expected is None:
        if returncode == 0:
            return False, 'Invalid input exited zero'
        if output is None or not output.strip():
            return True, 'Rejected without results'
        try:
            parsed = read_output(output)
        except (ValueError, ArithmeticError, RecursionError):
            return False, 'Failure left a nonempty malformed output artifact'
        if not isinstance(parsed, dict):
            return False, 'Failure output is not a non-result error envelope'
        if isinstance(parsed.get('stock_reports'), dict):
            return False, 'Failure wrote a results object (including partial or empty)'
        return True, 'Rejected with a non-result envelope'
    if returncode != 0:
        return False, f'Valid input exited {returncode}'
    if output is None:
        return False, 'Missing output file'
    try:
        parsed = read_output(output)
    except (ValueError, ArithmeticError, RecursionError) as exc:
        return False, f'Output is not valid UTF-8 JSON: {type(exc).__name__}'
    if not isinstance(parsed, dict) or not isinstance(parsed.get('stock_reports'), dict):
        return False, 'Missing stock_reports object'
    actual = parsed['stock_reports']
    if set(actual) != set(case.expected):
        return False, 'Output identifiers do not match input identifiers exactly'
    for key, expected in case.expected.items():
        value = actual[key]
        if not isinstance(value, ExactNumber):
            return False, f'{key!r}: result must be a JSON integer number'
        if value != ExactNumber.parse(expected):
            return False, f'{key!r}: wrong exact mathematical value'
    return True, 'Exact results verified'


def run(candidate: Path, *, python=sys.executable, timeout=10.0, selected=None):
    candidate = candidate.resolve()
    if not candidate.is_file():
        raise ValueError(f'Candidate script does not exist: {candidate}')
    results = []
    with tempfile.TemporaryDirectory(prefix='numeric export evaluation ', dir=Path.cwd()) as temporary:
        for case in cases() if selected is None else selected:
            folder = Path(temporary) / case.name
            folder.mkdir()
            source, target = folder / 'input data.json', folder / 'output data.json'
            source.write_bytes(case.payload)
            start = time.monotonic()
            command = [str(python), str(candidate), str(source), str(target)]
            record = {'name': case.name, 'category': case.category,
                      'valid_input': case.expected is not None, 'command': command}
            try:
                completed = subprocess.run(command, cwd=candidate.parent, capture_output=True,
                                           timeout=timeout, check=False)
                output = target.read_bytes() if target.is_file() else None
                passed, reason = judge(case, completed.returncode, output)
                record.update(returncode=completed.returncode,
                              stdout=completed.stdout.decode('utf-8', errors='replace')[:2000],
                              stderr=completed.stderr.decode('utf-8', errors='replace')[:2000])
            except subprocess.TimeoutExpired:
                passed, reason = False, f'Exceeded per-case timeout ({timeout:g}s)'
            except OSError as exc:
                passed, reason = False, f'Execution or output I/O failed: {exc}'
            record.update(passed=passed, reason=reason,
                          seconds=round(time.monotonic() - start, 4))
            results.append(record)
    total, passed = len(results), sum(row['passed'] for row in results)
    categories = {}
    for row in results:
        stats = categories.setdefault(row['category'], {'passed': 0, 'total': 0})
        stats['total'] += 1
        stats['passed'] += int(row['passed'])
    return {'evaluation': 'numeric-export-v1', 'candidate': str(candidate),
            'passed': passed == total, 'passed_cases': passed, 'total_cases': total,
            'categories': categories, 'cases': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path, nargs='?', help='Path to summarize.py')
    parser.add_argument('--python', default=sys.executable, help='Candidate Python executable')
    parser.add_argument('--timeout', type=float, default=10.0, help='Seconds per CLI invocation')
    parser.add_argument('--report', type=Path, help='Write detailed JSON results')
    parser.add_argument('--list', action='store_true', help='List cases without running a candidate')
    args = parser.parse_args()
    if args.list:
        for case in cases():
            print(f'{case.name}\t{case.category}\t{"valid" if case.expected is not None else "invalid"}')
        return 0
    if args.candidate is None or args.timeout <= 0:
        parser.error('Provide a candidate script and a positive timeout')
    try:
        report = run(args.candidate, python=args.python, timeout=args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{report["passed_cases"]}/{report["total_cases"]} cases passed')
    for row in report['cases']:
        if not row['passed']:
            print(f'FAIL {row["name"]}: {row["reason"]}')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
