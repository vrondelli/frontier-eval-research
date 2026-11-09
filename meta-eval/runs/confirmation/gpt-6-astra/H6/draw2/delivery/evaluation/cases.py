"""Deterministic, public-contract probes. Expected values are number tokens."""
import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Case:
    name: str
    category: str
    data: bytes
    expected: dict | None  # None means invalid input.


def document(rows):
    parts = []
    for name, stat, tokens in rows:
        parts.append(json.dumps(name, ensure_ascii=False) + ': {"stat":' +
                     json.dumps(stat) + ',"turns":[' + ','.join(tokens) + ']}')
    return ('{"adjustment_sheets":{' + ','.join(parts) + '}}').encode('utf-8')


def build_cases():
    cases = []

    def valid(name, category, rows):
        # Rows carry a separately specified expected numeric token.
        cases.append(Case(name, category, document([r[:3] for r in rows]),
                          {r[0]: r[3] for r in rows}))

    def invalid(name, value, raw=False):
        data = value if raw else json.dumps(value, ensure_ascii=False).encode('utf-8')
        cases.append(Case(name, 'invalid', data, None))

    example = Path(__file__).resolve().parents[1] / 'input/workspace/example.json'
    cases.append(Case('published_example', 'basic', example.read_bytes(), {
        'warehouse-sample-1-0': '5', 'warehouse-sample-1-1': '3',
        'warehouse-sample-1-2': '-3'}))
    valid('identities_and_repetitions', 'basic', [
        ('empty sum', 'net_units', [], '0'), ('empty count', 'event_count', [], '0'),
        ('repeat', 'event_count', ['8', '8', '-8', '0', '8'], '5'),
        ('signed maximum', 'largest_adjustment', ['-9', '-3', '-4'], '-3'),
        ('single', 'largest_adjustment', ['-17'], '-17')])
    valid('identifiers', 'basic', [
        ('零 😀', 'net_units', ['4', '-7'], '-3'),
        (' quote"\\\n', 'event_count', ['1'], '1'),
        ('__proto__', 'largest_adjustment', ['0', '-1'], '0'),
        ('A', 'net_units', ['1'], '1'), ('a', 'net_units', ['2'], '2')])
    valid('integral_number_encodings', 'numeric', [
        ('sum', 'net_units', ['1.0', '2e1', '120e-1', '-3.000', '-0.0'], '30'),
        ('count', 'event_count', ['0e-5000', '-0', '10.00e-1'], '3'),
        ('max', 'largest_adjustment', ['-10e-1', '-2.0', '-30e-1'], '-1')])
    valid('binary64_boundary', 'numeric', [
        ('sum', 'net_units', ['9007199254740993.0', '-9007199254740992'], '1'),
        ('max', 'largest_adjustment', ['9007199254740992', '9007199254740993e0'], '9007199254740993'),
        ('count', 'event_count', ['9007199254740993.0'], '1')])
    valid('cancellation_and_order', 'numeric', [
        ('forward', 'net_units', ['1e300', '1', '-1e300'], '1'),
        ('reverse', 'net_units', ['-1e300', '1e300', '1'], '1'),
        ('negative', 'largest_adjustment', ['-1e300', '-2e300'], '-1e300')])
    valid('beyond_float_range', 'numeric', [
        ('sum', 'net_units', ['1e400', '2e400', '-1e400'], '2e400'),
        ('max', 'largest_adjustment', ['-1e400', '-2e400'], '-1e400'),
        ('count', 'event_count', ['1e400', '-1e400'], '2')])
    valid('beyond_decimal_default_precision', 'numeric', [
        ('sum', 'net_units', ['123456789012345678901234567890123456789.0', '1'],
         '123456789012345678901234567890123456790'),
        ('max', 'largest_adjustment', ['123456789012345678901234567890123456788',
                                     '123456789012345678901234567890123456789.0'],
         '123456789012345678901234567890123456789')])
    long_integer = '1' + '0' * 4999 + '7'
    valid('long_integer_literal', 'numeric', [('long', 'net_units', [long_integer], long_integer)])
    valid('long_integral_decimal', 'numeric', [('long', 'largest_adjustment', [long_integer + '.0'], long_integer)])
    valid('large_result', 'numeric', [('sum', 'net_units', ['1e5000', '1'], '1' + '0' * 4999 + '1')])
    valid('compact_extreme_exponent', 'numeric', [
        ('count', 'event_count', ['1e1000000000', '-1e1000000000'], '2'),
        ('max', 'largest_adjustment', ['-1e1000000000', '-2e1000000000'], '-1e1000000000')])
    valid('many_rows', 'generalization', [
        (f'row-{i}', 'net_units', [str(i), '-1'], str(i - 1)) for i in range(75)])
    valid('long_array', 'generalization', [('events', 'event_count', ['-1'] * 2000, '2000')])
    # Constructive expected values use Python integer arithmetic only, never candidate output.
    rng = random.Random(728193)
    for n in range(16):
        values = [rng.randint(-10**35, 10**35) for _ in range(rng.randint(1, 20))]
        values += [values[0], 0]
        tokens = [str(v) + ('.000' if i % 3 == 0 else 'e0' if i % 3 == 1 else '')
                  for i, v in enumerate(values)]
        valid(f'generated_{n:02}', 'generalization', [
            (f'net-{n}', 'net_units', tokens, str(sum(values))),
            (f'count-{n}', 'event_count', tokens, str(len(values))),
            (f'max-{n}', 'largest_adjustment', tokens, str(max(values)))])
    boundary = document([('é', 'net_units', ['2'],)])
    cases.append(Case('exactly_8192_bytes', 'basic', boundary + b' ' * (8192 - len(boundary)), {'é': '2'}))

    for name, value in [
        ('root_array', []), ('root_null', None), ('missing_sheets', {}),
        ('extra_root_key', {'adjustment_sheets': {'x': {'stat': 'net_units', 'turns': []}}, 'extra': 1}),
        ('empty_sheets', {'adjustment_sheets': {}}),
        ('sheets_array', {'adjustment_sheets': []}),
        ('sheets_null', {'adjustment_sheets': None}),
        ('empty_identifier', {'adjustment_sheets': {'': {'stat': 'net_units', 'turns': []}}})]:
        invalid(name, value)
    for name, row in [
        ('row_array', []), ('row_null', None), ('row_scalar', 1),
        ('missing_stat', {'turns': []}), ('missing_turns', {'stat': 'net_units'}),
        ('unknown_stat', {'stat': 'sum', 'turns': []}),
        ('stat_case', {'stat': 'NET_UNITS', 'turns': []}),
        ('stat_type', {'stat': 1, 'turns': []}),
        ('extra_row_key', {'stat': 'net_units', 'turns': [], 'extra': 0}),
        ('turns_null', {'stat': 'net_units', 'turns': None}),
        ('turns_object', {'stat': 'event_count', 'turns': {}}),
        ('turns_string', {'stat': 'net_units', 'turns': '123'}),
        ('empty_max', {'stat': 'largest_adjustment', 'turns': []})]:
        invalid(name, {'adjustment_sheets': {'x': row}})
    bad_tokens = [('true', 'true'), ('false', 'false'), ('null', 'null'),
                  ('string', '"1"'), ('array', '[]'), ('object', '{}'),
                  ('fraction', '1.5'), ('tiny_fraction', '1e-400'),
                  ('rounded_fraction', '1.00000000000000000000000000000000000001'),
                  ('large_fraction', '9007199254740992.5')]
    for stat in ('net_units', 'event_count', 'largest_adjustment'):
        for label, token in bad_tokens:
            invalid(f'{stat}_{label}', document([('good', 'net_units', ['7']),
                                                 ('bad', stat, ['1', token])]), raw=True)
    for name, raw in [
        ('duplicate_root', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[]}},"adjustment_sheets":{"y":{"stat":"net_units","turns":[]}}}'),
        ('duplicate_identifier', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[1]},"x":{"stat":"net_units","turns":[2]}}}'),
        ('escaped_duplicate_identifier', r'{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]},"\u0061":{"stat":"net_units","turns":[]}}}'),
        ('duplicate_stat', '{"adjustment_sheets":{"x":{"stat":"event_count","stat":"net_units","turns":[1]}}}'),
        ('duplicate_turns', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[1],"turns":[1]}}}'),
        ('truncated_json', '{"adjustment_sheets":'), ('trailing_document', '{} {}'),
        ('empty_file', ''), ('nan', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[NaN]}}}'),
        ('infinity', '{"adjustment_sheets":{"x":{"stat":"event_count","turns":[Infinity]}}}')]:
        invalid(name, raw.encode('utf-8'), raw=True)
    invalid('invalid_utf8', b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[]}}}', raw=True)
    assert len({case.name for case in cases}) == len(cases)
    assert all(len(case.data) <= 8192 for case in cases)
    return cases
