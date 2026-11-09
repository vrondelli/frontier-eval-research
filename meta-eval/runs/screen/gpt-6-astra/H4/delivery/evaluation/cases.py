"""Cases derived solely from rules K/V/D/T/W/R in input/task.txt."""
from dataclasses import dataclass
from random import Random

from oracle import expected


@dataclass
class Case:
    name: str
    rule: str
    records: list
    expected: dict
    rationale: str


def row(passenger='p', **overrides):
    record = dict(passenger=passenger, fare='100', baggage='100',
                  passcode='19000', sailed='2025-06-20', voucher='0')
    record.update(overrides)
    return record


def build_cases():
    cases = []

    def add(name, rule, records, rationale, gold=None):
        cases.append(Case(name, rule, records, expected(records) if gold is None else gold, rationale))

    empty = dict(total_minor=0, billed=0, excluded=[], fares={}, per_class={}, mean_minor=0)
    add('empty', 'R', [], 'Explicit empty result.', empty)
    # At C=200: rebate=18, Q=182. Class subtotals are 17.74, 28.84,
    # 44.58, 62.32. Multiply by 1.07, then add 6 only for priority.
    add('hand_all_classes', 'W', [row(c, passcode=p) for c, p in
        [('youth', '00000'), ('adult', '19000'), ('resident', '50000'), ('priority', '74000')]],
        'Manual arithmetic: 18.9818, 30.8588, 47.7006, 72.6824.',
        dict(total_minor=17022, billed=4, excluded=[],
             fares={'youth': 1898, 'adult': 3086, 'resident': 4770, 'priority': 7268},
             per_class={'youth': 1898, 'adult': 3086, 'resident': 4770, 'priority': 7268}, mean_minor=4256))
    # C=1, raw=.91 -> Q=1. Youth amount=5.4249; adult=7.6184;
    # resident=10.9033; priority=22.3282.
    add('hand_quarter_rounding', 'T', [row('p', fare='.5', baggage='0.5')],
        'Missing integer digit is invalid even if float parsers accept it.',
        dict(empty, excluded=['p']))
    add('hand_small_youth', 'T', [row('p', fare='0.5', baggage='0.5', passcode='18000')],
        'C=1 -> Q=1 -> 5.4249 -> 542.',
        dict(total_minor=542, billed=1, excluded=[], fares={'p': 542}, per_class={'youth': 542}, mean_minor=542))

    for prefix in range(100):
        for suffix in ('', '-007'):
            add(f'pass_{prefix:02d}_{"long" if suffix else "short"}', 'K',
                [row(passcode=f'{prefix:02d}321{suffix}')], 'Every prefix, both accepted shapes; inclusive class bounds.')
    invalid_passes = ['', ' ', '1234', '123456', '12345678', '12345-12', '12345-1234',
        '1234-123', '123456-123', '12345 123', '12345--123', '+12345', '-12345',
        '12a45', '12345x', ' 12345', '12345 ', '12345\n', '\t12345', '12345\r\n',
        '１２３４５', '١٢٣٤٥', '12٣45', '12345-１２３', '12345–123', '12345-123\n', '12345\x00']
    for i, value in enumerate(invalid_passes):
        add(f'pass_invalid_{i:02d}', 'K', [row(passcode=value)], 'Exact ASCII shape; no trimming or Unicode digits.')

    invalid_numbers = ['', ' ', ' 1', '1 ', '\t1', '1\n', '1\r\n', '+1', '1,000', '1_000',
        '1e2', '1E+2', '.5', '5.', '1..0', 'NaN', 'sNaN', 'Infinity', '-Infinity',
        'abc', '１', '١', '1.٢', '1\x00', '1/2', '--1', '-']
    for field in ('fare', 'baggage', 'voucher'):
        values = invalid_numbers + (['0', '00', '0.000', '-0', '-1', '-0.5'] if field != 'voucher' else [])
        for i, value in enumerate(values):
            add(f'{field}_invalid_{i:02d}', 'V', [row(**{field: value})], 'Reject each invalid number independently.')
        for i, value in enumerate(['0001', '001.2500', '0.00001'] +
                                  (['0', '-0', '-0.000', '-001.2500', '-100'] if field == 'voucher' else [])):
            add(f'{field}_valid_{i:02d}', 'V', [row(**{field: value})], 'Leading zeros, fractions and signed voucher semantics.')

    valid_dates = ['0000-01-01', '0000-02-31', '0001-01-01', '1900-02-29', '2023-02-29',
                   '2024-02-31', '2025-04-31', '2024-12-31', '2025-05-31', '2025-06-01',
                   '2025-06-19', '2025-06-20']
    invalid_dates = ['', ' ', ' 2025-06-20', '2025-06-20 ', '2025-06-20\n',
        '2025/06/20', '2025-06/20', '2025/06-20', '2025–06–20', '20250620',
        '025-06-20', '02025-06-20', '2025-6-20', '2025-006-20', '2025-06-2',
        '2025-06-020', '2025-00-20', '2025-13-20', '2025-06-00', '2025-06-32',
        '2025-aa-20', '+025-06-20', '２０２５-06-20', '2025-٠٦-20', '2025-06-٢٠',
        '2025-06-20\x00', '2025-06-21', '2025-07-01', '2025-12-01', '2026-01-01', '9999-12-31']
    for label, dates in [('valid', valid_dates), ('excluded', invalid_dates)]:
        for i, value in enumerate(dates):
            add(f'date_{label}_{i:02d}', 'D', [row(sailed=value)], 'Range-only date validation and lexicographic cutoff.')

    for i, (fare, baggage) in enumerate([
        ('0.01', '0.01'), ('0.5', '0.5'), ('0.25', '24.75'),
        ('0.25', '24.7499999999999999999999999999999999999999'),
        ('0.25', '24.7500000000000000000000000000000000000001'),
        ('99.9999', '100'), ('100', '100'), ('100.0001', '100'),
        ('100', '100.25'), ('100', '100.2499999999999999999999999999999999999999'),
        ('100', '100.2500000000000000000000000000000000000001'),
        ('9999999999999999999999999999999999999999.99', '0.01'),
        ('0.' + '0' * 39 + '1', '0.' + '0' * 39 + '1')]):
        for code in ('00000', '19000', '50000', '74000'):
            add(f'charge_{i:02d}_{code}', 'T', [row(fare=fare, baggage=baggage, passcode=code)],
                'Cap at C=200; exact/below/above quarter; tiny and long decimals without context loss.')

    # These vouchers target amounts +/-1.005 and their immediate decimal neighbors.
    # They are derived from the manual C=1 amounts above, not helper output.
    tie_vouchers = {'00000': ('4.4199', '6.4299'), '19000': ('6.6134', '8.6234'),
                    '50000': ('9.8983', '11.9083'), '74000': ('21.3232', '23.3332')}
    for code, vouchers in tie_vouchers.items():
        cls = {'00000': 'youth', '19000': 'adult', '50000': 'resident', '74000': 'priority'}[code]
        for sign, voucher, minor in [('positive', vouchers[0], 101), ('negative', vouchers[1], -101)]:
            add(f'tie_{code}_{sign}', 'W', [row(fare='0.5', baggage='0.5', passcode=code, voucher=voucher)],
                'Exact +/-1.005 rounds away from zero.',
                dict(total_minor=minor, billed=1, excluded=[], fares={'p': minor}, per_class={cls: minor}, mean_minor=minor))
            for side in ('below', 'above'):
                # String integer arithmetic preserves 40 decimal places.
                scaled = int(voucher.replace('.', '')) * 10**36
                adjusted = scaled + (1 if side == 'above' else -1)
                text = str(adjusted).zfill(41)
                near = text[:-40] + '.' + text[-40:]
                add(f'near_tie_{code}_{sign}_{side}', 'W',
                    [row(fare='0.5', baggage='0.5', passcode=code, voucher=near)],
                    'One 10^-40 step on either side of a half-cent tie.')

    for name, vouchers, totals, mean in [
        ('positive_mean_tie', ['4.4249', '4.4149'], [100, 101], 101),
        ('negative_mean_tie', ['6.4249', '6.4349'], [-100, -101], -101),
        ('zero_crossing_mean', ['5.4149', '5.4449'], [1, -2], -1),
        ('positive_half_mean', ['5.4249', '5.4149'], [0, 1], 1),
        ('round_records_before_sum', ['5.4199', '5.4199'], [1, 1], 1),
        ('zero_billed_amount', ['5.4249', '5.4249'], [0, 0], 0)]:
        records = [row(str(i), fare='0.5', baggage='0.5', passcode='00000', voucher=v) for i, v in enumerate(vouchers)]
        add(name, 'R', records, 'Manual C=1 youth amount is 5.4249; round per record, then integer mean.',
            dict(total_minor=sum(totals), billed=2, excluded=[], fares=dict(zip(['0', '1'], totals)),
                 per_class={'youth': sum(totals)}, mean_minor=mean))
    add('all_invalid', 'R', [row('first', passcode='bad', fare='0', sailed='bad', voucher='+2'),
        row('second', baggage='0'), row('third', sailed='2026-01-01')], 'One exclusion each in input order.',
        dict(empty, excluded=['first', 'second', 'third']))
    mixed = [row('z', fare='0'), row('', passcode='00000'), row('é/渡船', voucher='100'),
        row('a', sailed='2025-06-21'), row('None', passcode='74000'),
        row('total_minor', passcode='50000'), row('bad-many', fare='x', baggage='x', passcode='x')]
    add('mixed_order_identifiers', 'R', mixed, 'Interleaved valid/excluded, negative settlement, arbitrary distinct identifiers.')
    add('mixed_reverse_order', 'R', list(reversed(mixed)), 'Exclusions retain input order; aggregation independent of order.')

    rng = Random(846207)
    for batch in range(40):
        records = []
        for j in range(rng.randrange(2, 20)):
            record = row(f'b{batch}-{j}',
                fare=f'{rng.randrange(0, 500)}.{rng.randrange(1, 10000):04d}',
                baggage=f'{rng.randrange(0, 120)}.{rng.randrange(1, 10000):04d}',
                voucher=f'{rng.randrange(-100, 100)}.{rng.randrange(10000):04d}',
                passcode=f'{rng.randrange(100):02d}{rng.randrange(1000):03d}' + ('-123' if j % 2 else ''),
                sailed=rng.choice(valid_dates))
            if j % 7 == 3:
                record[rng.choice(['fare', 'baggage', 'voucher', 'passcode', 'sailed'])] = 'invalid'
            records.append(record)
        add(f'seeded_batch_{batch:02d}', 'R', records, 'Deterministic mixed batches; exact rational oracle, fixed seed 846207.')
    return cases
