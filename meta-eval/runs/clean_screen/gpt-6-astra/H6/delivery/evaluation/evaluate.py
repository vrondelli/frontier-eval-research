#!/usr/bin/env python3
"""Black-box evaluation of the stock-adjustment export CLI (standard library)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile


@dataclass(frozen=True)
class Case:
    name: str
    group: str
    raw: bytes
    expected: dict[str, Decimal] | None  # None means invalid input.


def document(rows):
    """Rows contain raw JSON numeric tokens, preserving their original encoding."""
    return '{"adjustment_sheets":{' + ','.join(
        json.dumps(key, ensure_ascii=False) + ':{"stat":' + json.dumps(stat)
        + ',"turns":[' + ','.join(values) + ']}'
        for key, stat, values in rows
    ) + '}}'


def cases(seed=20261108):
    result = []

    def valid(name, group, rows, expected):
        result.append(Case(name, group, document(rows).encode('utf-8'),
                           {k: Decimal(str(v)) for k, v in expected.items()}))

    def invalid(name, raw):
        result.append(Case(name, 'validation',
                           raw if isinstance(raw, bytes) else raw.encode('utf-8'), None))

    valid('illustrative-example', 'semantics', [
        ('warehouse-sample-1-0', 'net_units', ['4', '-3', '4']),
        ('warehouse-sample-1-1', 'event_count', ['0', '-2', '-2']),
        ('warehouse-sample-1-2', 'largest_adjustment', ['-9', '-3', '-4']),
    ], {'warehouse-sample-1-0': 5, 'warehouse-sample-1-1': 3, 'warehouse-sample-1-2': -3})
    valid('empty-identities-and-repetitions', 'semantics', [
        ('zero-net', 'net_units', []), ('zero-count', 'event_count', []),
        ('repetitions', 'event_count', ['8'] * 17),
        ('sum-repetitions', 'net_units', ['-8'] * 17),
        ('negative-max', 'largest_adjustment', ['-91', '-2', '-11']),
        ('singleton', 'largest_adjustment', ['-77']),
        ('signed-max', 'largest_adjustment', ['-999', '0', '2']),
    ], {'zero-net': 0, 'zero-count': 0, 'repetitions': 17,
        'sum-repetitions': -136, 'negative-max': -2, 'singleton': -77, 'signed-max': 2})
    keys = ['é/仓库🚚', ' ', 'quote"slash\\line\n', '__proto__', 'stock_reports', '0']
    valid('opaque-identifiers', 'identifiers',
          [(k, 'net_units', [str(i)]) for i, k in enumerate(keys)],
          {k: i for i, k in enumerate(keys)})
    valid('integral-number-encodings', 'exactness', [
        ('net', 'net_units', ['1.0', '2e3', '-35E+1', '100e-2', '-0.000']),
        ('count', 'event_count', ['1.0', '0e9', '-2.000']),
        ('max', 'largest_adjustment', ['-2e2', '-1.0', '-10.00']),
    ], {'net': 1652, 'count': 3, 'max': -1})
    valid('float-integer-boundary', 'exactness', [
        ('sum', 'net_units', ['9007199254740993', '-9007199254740992']),
        ('max', 'largest_adjustment', ['9007199254740992', '9007199254740993']),
        ('decimal', 'net_units', ['9007199254740993.0']),
    ], {'sum': 1, 'max': '9007199254740993', 'decimal': '9007199254740993'})
    huge = '9' * 90
    valid('decimal-context-cancellation', 'exactness', [
        ('net', 'net_units', [huge, '1', '-' + huge]),
        ('max', 'largest_adjustment', ['-' + huge, '-' + str(int(huge) - 1)]),
    ], {'net': 1, 'max': '-' + str(int(huge) - 1)})
    valid('exceeds-float-range', 'exactness', [
        ('net', 'net_units', ['1e400', '9', '-1e400']),
        ('max', 'largest_adjustment', ['-2e400', '-1e400']),
        ('count', 'event_count', ['1e400', '-1e400']),
    ], {'net': 9, 'max': '-1e400', 'count': 2})
    valid('large-exponent', 'exactness', [
        ('net', 'net_units', ['1e100000', '-1e100000', '7']),
        ('max', 'largest_adjustment', ['1e100000', '1e99999']),
    ], {'net': 7, 'max': '1e100000'})
    long_integer = '7' * 6000
    valid('integer-token-over-python-default-limit', 'exactness',
          [('long', 'net_units', [long_integer])], {'long': long_integer})

    rng = random.Random(seed)
    for batch in range(16):
        rows, expected = [], {}
        for i in range(rng.randint(1, 14)):
            key = f'generated-{batch}-{i}-{rng.randrange(1000000)}'
            stat = rng.choice(['net_units', 'event_count', 'largest_adjustment'])
            values = [rng.randint(-100000, 100000)
                      for _ in range(rng.randint(1 if stat == 'largest_adjustment' else 0, 22))]
            rows.append((key, stat, [str(x) for x in values]))
            expected[key] = (sum(values) if stat == 'net_units' else
                             len(values) if stat == 'event_count' else max(values))
        valid(f'generated-{batch:02}', 'generalization', rows, expected)

    # UTF-8 byte boundary, not a character-count boundary; trailing JSON whitespace is legal.
    raw = document([('边界', 'net_units', ['17'])]).encode('utf-8')
    result.append(Case('exactly-8192-bytes', 'boundaries', raw + b' ' * (8192-len(raw)),
                       {'边界': Decimal(17)}))
    valid('long-array', 'boundaries', [('many', 'event_count', ['0'] * 3500)], {'many': 3500})
    valid('many-identifiers', 'boundaries',
          [(f'id-{i}', 'net_units', [str(i)]) for i in range(100)],
          {f'id-{i}': i for i in range(100)})

    for name, raw in [
        ('empty-file', ''), ('malformed-json', '{'),
        ('trailing-document', '{"adjustment_sheets":{}} {}'),
        ('trailing-comma', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1,]}}}'),
        ('invalid-utf8', b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[]}}}'),
        ('root-null', 'null'), ('root-array', '[]'), ('root-number', '1'),
        ('missing-sheets', '{}'), ('empty-sheets', '{"adjustment_sheets":{}}'),
        ('sheets-array', '{"adjustment_sheets":[]}'), ('sheets-null', '{"adjustment_sheets":null}'),
        ('top-extra', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]}},"extra":1}'),
        ('empty-id', document([('', 'net_units', [])])),
        ('duplicate-root', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]}},"adjustment_sheets":{"b":{"stat":"net_units","turns":[]}}}'),
        ('duplicate-id', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1]},"a":{"stat":"net_units","turns":[2]}}}'),
        ('escaped-duplicate-id', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]},"\\u0061":{"stat":"net_units","turns":[]}}}'),
        ('duplicate-stat', '{"adjustment_sheets":{"a":{"stat":"net_units","stat":"net_units","turns":[]}}}'),
        ('duplicate-turns', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[],"turns":[1]}}}'),
    ]:
        invalid(name, raw)
    for name, sheet in [
        ('sheet-null', 'null'), ('sheet-array', '[]'), ('sheet-number', '1'),
        ('missing-stat', '{"turns":[]}'), ('missing-turns', '{"stat":"net_units"}'),
        ('unknown-stat', '{"stat":"sum","turns":[]}'),
        ('case-sensitive-stat', '{"stat":"NET_UNITS","turns":[]}'),
        ('stat-number', '{"stat":1,"turns":[]}'),
        ('extra-sheet-property', '{"stat":"net_units","turns":[],"extra":0}'),
        ('turns-null', '{"stat":"net_units","turns":null}'),
        ('turns-object', '{"stat":"net_units","turns":{}}'),
        ('turns-string', '{"stat":"net_units","turns":"123"}'),
        ('empty-largest', '{"stat":"largest_adjustment","turns":[]}'),
    ]:
        # A valid first row exposes programs that write results before validating later rows.
        invalid(name, '{"adjustment_sheets":{"good":{"stat":"net_units","turns":[4]},"bad":' + sheet + '}}')
    bad_values = ['true', 'false', 'null', '"1"', '[]', '{}', '1.5', '1e-1',
                  '1.0000000000000000000000000000000001', 'NaN', 'Infinity', '-Infinity']
    for stat in ['net_units', 'event_count', 'largest_adjustment']:
        for i, token in enumerate(bad_values):
            invalid(f'{stat}-invalid-item-{i:02}', document([
                ('good', 'net_units', ['42']), ('bad', stat, ['1', token])]))
    assert len({c.name for c in result}) == len(result)
    assert all(len(c.raw) <= 8192 for c in result)
    return result


def reject_constant(token):
    raise ValueError(f'Non-JSON constant: {token}')


def read_output(path):
    # Decimal construction and equality are exact and independent of context precision.
    return json.loads(path.read_text(encoding='utf-8'), parse_int=Decimal,
                      parse_float=Decimal, parse_constant=reject_constant)


def judge(case, returncode, output_path):
    if case.expected is None:
        if returncode == 0:
            return False, 'Invalid input exited zero'
        if not output_path.exists() or not output_path.read_bytes().strip():
            return True, 'Rejected without results'
        try:
            output = read_output(output_path)
        except (ValueError, OSError, UnicodeError, ArithmeticError):
            return False, 'Failure wrote malformed output instead of a non-result error envelope'
        if not isinstance(output, dict) or 'stock_reports' in output:
            return False, 'Failure wrote results or did not write a non-result error envelope'
        return True, 'Rejected with a non-result error envelope'
    if returncode != 0:
        return False, f'Valid input exited {returncode}'
    try:
        output = read_output(output_path)
    except (ValueError, OSError, UnicodeError, ArithmeticError) as exc:
        return False, f'Missing or invalid output JSON: {type(exc).__name__}'
    if not isinstance(output, dict) or not isinstance(output.get('stock_reports'), dict):
        return False, 'Output must contain the stock_reports object'
    reports = output['stock_reports']
    if reports.keys() != case.expected.keys():
        return False, 'Output identifiers do not exactly match input identifiers'
    for key, expected in case.expected.items():
        actual = reports[key]
        if not isinstance(actual, Decimal) or not actual.is_finite() or actual != expected:
            return False, f'Incorrect exact integer for identifier {key!r}'
    return True, 'Exact expected results'


def evaluate(candidate, python=sys.executable, timeout=5.0, seed=20261108):
    candidate = Path(candidate).resolve()
    if not candidate.is_file():
        raise ValueError(f'Candidate does not exist: {candidate}')
    records = []
    with tempfile.TemporaryDirectory(prefix='numeric export evaluation ', dir=Path.cwd()) as root:
        for case in cases(seed):
            directory = Path(root) / case.name
            directory.mkdir()
            source = directory / 'input data.json'
            output = directory / 'output report.json'
            source.write_bytes(case.raw)
            command = [str(python), str(candidate), str(source), str(output)]
            record = {'name': case.name, 'group': case.group,
                      'valid_input': case.expected is not None,
                      'input_sha256': hashlib.sha256(case.raw).hexdigest(),
                      'input_bytes': len(case.raw), 'command': command}
            try:
                run = subprocess.run(command, cwd=candidate.parent, capture_output=True,
                                     timeout=timeout, check=False)
                passed, reason = judge(case, run.returncode, output)
                record.update(returncode=run.returncode,
                              stdout=run.stdout[:2000].decode('utf-8', errors='replace'),
                              stderr=run.stderr[:2000].decode('utf-8', errors='replace'))
            except subprocess.TimeoutExpired:
                passed, reason = False, f'Exceeded per-case timeout of {timeout:g}s'
            except OSError as exc:
                raise RuntimeError(f'Cannot launch candidate: {exc}') from exc
            record.update(passed=passed, reason=reason)
            records.append(record)
    groups = {}
    for record in records:
        group = groups.setdefault(record['group'], {'passed': 0, 'total': 0})
        group['total'] += 1
        group['passed'] += int(record['passed'])
    return {'evaluation_version': 1, 'candidate': str(candidate), 'seed': seed,
            'timeout_seconds': timeout, 'passed': all(r['passed'] for r in records),
            'passed_cases': sum(r['passed'] for r in records), 'total_cases': len(records),
            'groups': groups, 'cases': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path, help='Path to submitted summarize.py')
    parser.add_argument('--python', default=sys.executable, help='Candidate Python interpreter')
    parser.add_argument('--timeout', type=float, default=5.0, help='Seconds per CLI invocation')
    parser.add_argument('--seed', type=int, default=20261108)
    parser.add_argument('--report', type=Path, default=Path('evaluation-report.json'))
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    try:
        report = evaluate(args.candidate, args.python, args.timeout, args.seed)
    except (ValueError, RuntimeError) as exc:
        parser.exit(2, f'Evaluation setup error: {exc}\n')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(f"{report['passed_cases']}/{report['total_cases']} cases passed; report: {args.report}")
    for record in report['cases']:
        if not record['passed']:
            print(f"FAIL {record['name']}: {record['reason']}")
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
