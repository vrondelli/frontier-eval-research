"""Independent specification oracle: ASCII grammar + integer rational arithmetic.

Never imports fares, farelib, or a candidate test. No Decimal context or float.
"""
from fractions import Fraction as Q


def digits(s):
    return bool(s) and all('0' <= c <= '9' for c in s)


def number(s, signed=False):
    negative = signed and s.startswith('-')
    body = s[1:] if negative else s
    parts = body.split('.')
    if len(parts) not in (1, 2) or not all(digits(p) for p in parts):
        raise ValueError('decimal grammar')
    fractional = parts[1] if len(parts) == 2 else ''
    value = Q(int(parts[0] + fractional), 10 ** len(fractional))
    if negative:
        value = -value
    if not signed and value <= 0:
        raise ValueError('nonpositive charge')
    return value


def half_away(value):
    magnitude = abs(value)
    whole, remainder = divmod(magnitude.numerator, magnitude.denominator)
    rounded = whole + (2 * remainder >= magnitude.denominator)
    return -rounded if value < 0 else rounded


def classify(code):
    parts = code.split('-')
    if (len(parts) not in (1, 2) or len(parts[0]) != 5
            or not digits(parts[0])
            or (len(parts) == 2 and (len(parts[1]) != 3 or not digits(parts[1])))):
        raise ValueError('pass grammar')
    prefix = int(parts[0][:2])
    return ('youth' if prefix <= 18 else 'adult' if prefix <= 49
            else 'resident' if prefix <= 73 else 'priority')


def eligible(s):
    parts = s.split('-')
    if len(parts) != 3 or tuple(map(len, parts)) != (4, 2, 2):
        return False
    if not all(digits(p) for p in parts):
        return False
    year, month, day = map(int, parts)
    return 1 <= month <= 12 and 1 <= day <= 31 and (year, month, day) <= (2025, 6, 20)


def expected(records):
    result = dict(total_minor=0, billed=0, excluded=[], fares={}, per_class={}, mean_minor=0)
    tariffs = {'youth': (3, 7), 'adult': (5, 12), 'resident': (8, 19), 'priority': (13, 26)}
    for row in records:
        passenger = row['passenger']
        try:
            cls = classify(row['passcode'])
            fare = number(row['fare'])
            baggage = number(row['baggage'])
            voucher = number(row['voucher'], signed=True)
            if not eligible(row['sailed']):
                raise ValueError('sailing date')
        except ValueError:
            result['excluded'].append(passenger)
            continue
        combined = fare + baggage
        raw = combined - min(Q(9, 100) * combined, Q(18))
        quarters = -((-raw.numerator * 4) // raw.denominator)
        charge = Q(quarters, 4)
        levy, percent = tariffs[cls]
        amount = (levy + 2 + Q(percent, 100) * charge) * Q(107, 100)
        if cls == 'priority':
            amount += 6
        settled = half_away((amount - voucher) * 100)
        result['fares'][passenger] = settled
        result['per_class'][cls] = result['per_class'].get(cls, 0) + settled
        result['total_minor'] += settled
        result['billed'] += 1
    if result['billed']:
        result['mean_minor'] = half_away(Q(result['total_minor'], result['billed']))
    return result
