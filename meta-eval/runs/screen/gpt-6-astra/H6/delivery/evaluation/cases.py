"""Public-spec probes. Expected values use Python integers, never binary floats."""
from dataclasses import dataclass
import json
import random
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class Case:
    name: str
    category: str
    raw: str
    expected: dict[str, int] | None  # None means invalid input.


def sheet(stat, tokens):
    return '{"stat":' + json.dumps(stat) + ',"turns":[' + ','.join(tokens) + ']}'


def document(rows):
    return '{"adjustment_sheets":{' + ','.join(
        json.dumps(key, ensure_ascii=False) + ':' + value for key, value in rows
    ) + '}}'


def build_cases():
    cases = []

    def valid(name, category, rows):
        cases.append(Case(name, category, document([
            (key, sheet(stat, tokens)) for key, stat, tokens, _ in rows
        ]), {key: expected for key, _, _, expected in rows}))

    valid('illustrative-example', 'basic', [
        ('warehouse-sample-1-0', 'net_units', ['4', '-3', '4'], 5),
        ('warehouse-sample-1-1', 'event_count', ['0', '-2', '-2'], 3),
        ('warehouse-sample-1-2', 'largest_adjustment', ['-9', '-3', '-4'], -3),
    ])
    valid('identities-repetitions-and-sign', 'basic', [
        ('empty sum', 'net_units', [], 0),
        ('empty count', 'event_count', [], 0),
        ('duplicates', 'event_count', ['7'] * 17, 17),
        ('negative maximum', 'largest_adjustment', ['-100', '-2', '-20'], -2),
        ('single', 'largest_adjustment', ['-7'], -7),
        ('zero maximum', 'largest_adjustment', ['-8', '0', '-3'], 0),
    ])
    valid('unicode-and-special-identifiers', 'identifiers', [
        (key, 'net_units', [str(i), '3'], i + 3)
        for i, key in enumerate(['雪📦', 'a b', 'quote"slash\\', '\n',
                                  '__proto__', 'stock_reports', 'é', 'e\u0301'])
    ])
    valid('integral-number-encodings', 'numeric', [
        ('decimal', 'net_units', ['1.0', '-2.000', '1.2300e2', '1e-0', '-0.0', '1000e-3'], 124),
        ('count', 'event_count', ['1E+2', '0e-999', '-0', '2.000'], 4),
        ('max', 'largest_adjustment', ['-2.0', '-1e0', '-3.00'], -1),
    ])
    valid('binary64-integer-boundary', 'numeric', [
        ('sum', 'net_units', ['9007199254740993', '-9007199254740992'], 1),
        ('max', 'largest_adjustment', ['9007199254740992', '9007199254740993'], 9007199254740993),
        ('decimal', 'net_units', ['9007199254740993.0', '-9007199254740992.0'], 1),
    ])
    big = 10 ** 400
    valid('beyond-finite-float', 'numeric', [
        ('cancel', 'net_units', ['1e400', '7', '-1e400'], 7),
        ('sum', 'net_units', ['1e400', '1'], big + 1),
        ('negative', 'largest_adjustment', ['-1e401', '-1e400'], -big),
        ('count', 'event_count', ['1e400', '-1e400'], 2),
    ])
    valid('decimal-context-precision', 'numeric', [
        ('sum', 'net_units', ['1e100', '1', '-1e100'], 1),
        ('adjacent', 'largest_adjustment', [str(10 ** 90), str(10 ** 90 + 1) + '.0'], 10 ** 90 + 1),
    ])
    valid('long-integer-token', 'numeric', [
        ('long', 'net_units', ['9' * 5000], 10 ** 5000 - 1),
    ])
    valid('long-coefficient-with-negative-exponent', 'numeric', [
        ('scaled', 'net_units', ['1' + '0' * 4500 + 'e-4500', '2'], 3),
    ])
    valid('many-sheets', 'generalization', [
        (f'row-{i}', 'net_units', [str(i), '-5'], i - 5) for i in range(70)
    ])
    rng = random.Random(671903)
    for batch in range(8):
        rows = []
        for index in range(9):
            stat = ['net_units', 'event_count', 'largest_adjustment'][index % 3]
            values = [rng.randrange(-10 ** 24, 10 ** 24) for _ in range(rng.randrange(1, 12))]
            tokens = [str(value) + ('.0' if j % 2 else '') for j, value in enumerate(values)]
            expected = sum(values) if stat == 'net_units' else len(values) if stat == 'event_count' else max(values)
            rows.append((f'batch-{batch}/sheet-{index}', stat, tokens, expected))
        valid(f'generated-{batch}', 'generalization', rows)
    raw = document([('limit-雪', sheet('net_units', ['1']))])
    raw += ' ' * (8192 - len(raw.encode('utf-8')))
    cases.append(Case('exact-byte-limit', 'boundary', raw, {'limit-雪': 1}))

    good = ('first-valid', sheet('net_units', ['2', '3']))

    def invalid(name, raw, category='schema'):
        cases.append(Case(name, category, raw, None))

    for name, raw in [
        ('root-array', '[]'), ('root-null', 'null'), ('root-scalar', '42'),
        ('missing-sheets', '{}'), ('empty-sheets', '{"adjustment_sheets":{}}'),
        ('sheets-array', '{"adjustment_sheets":[]}'),
        ('sheets-null', '{"adjustment_sheets":null}'),
        ('top-extra', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[]}},"extra":1}'),
    ]:
        invalid(name, raw)
    for name, value in [
        ('row-null', 'null'), ('row-array', '[]'), ('row-string', '"x"'),
        ('missing-stat', '{"turns":[]}'), ('missing-turns', '{"stat":"net_units"}'),
        ('unknown-stat', '{"stat":"sum","turns":[]}'),
        ('stat-wrong-case', '{"stat":"NET_UNITS","turns":[]}'),
        ('stat-null', '{"stat":null,"turns":[]}'),
        ('row-extra', '{"stat":"net_units","turns":[],"extra":0}'),
        ('turns-null', '{"stat":"net_units","turns":null}'),
        ('turns-object', '{"stat":"net_units","turns":{}}'),
        ('turns-string', '{"stat":"net_units","turns":"123"}'),
        ('empty-maximum', sheet('largest_adjustment', [])),
    ]:
        invalid(name, document([good, ('bad', value)]))
    invalid('empty-identifier', document([good, ('', sheet('event_count', []))]))
    # All operations must validate every measurement, even when only counting.
    bad_tokens = {
        'true': 'true', 'false': 'false', 'null': 'null', 'string': '"1"',
        'array': '[1]', 'object': '{}', 'fraction': '1.5',
        'rounded-fraction': '9007199254740992.5',
        'tiny-fraction': '1e-400',
        'near-integral': '1.' + '0' * 80 + '1',
    }
    for stat in ['net_units', 'event_count', 'largest_adjustment']:
        for name, token in bad_tokens.items():
            invalid(f'{stat}-{name}', document([good, ('bad', sheet(stat, ['3', token]))]), 'invalid-numeric')
    for name, raw in [
        ('duplicate-root', '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[]}},"adjustment_sheets":{"y":{"stat":"net_units","turns":[]}}}'),
        ('duplicate-row', document([good, good])),
        ('escaped-duplicate-row', '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[]},"\\u0061":{"stat":"event_count","turns":[]}}}'),
        ('duplicate-stat', document([('x', '{"stat":"net_units","stat":"event_count","turns":[]}')])),
        ('duplicate-turns', document([('x', '{"stat":"net_units","turns":[],"turns":[1]}')])),
        ('escaped-duplicate-member', document([('x', '{"stat":"net_units","turns":[],"tur\\u006es":[1]}')])),
    ]:
        invalid(name, raw, 'duplicates')
    for name, raw in [
        ('truncated', '{"adjustment_sheets":'),
        ('trailing-document', document([good]) + '{}'),
        ('trailing-comma', '{"adjustment_sheets":{},}'),
        ('leading-zero', document([('x', sheet('net_units', ['01']))])),
        ('nan', document([('x', sheet('event_count', ['NaN']))])),
        ('infinity', document([('x', sheet('net_units', ['Infinity']))])),
        ('negative-infinity', document([('x', sheet('largest_adjustment', ['-Infinity']))])),
    ]:
        invalid(name, raw, 'json')
    assert len({c.name for c in cases}) == len(cases)
    assert all(len(c.raw.encode('utf-8')) <= 8192 for c in cases)
    return cases
