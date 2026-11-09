"""Independent specification arithmetic: integers and fractions, never farelib.

Decimal strings are interpreted as integer ratios, so neither a Decimal context
nor binary floating point can influence expected results.
"""

import re
from fractions import Fraction


PASS = re.compile(r"[0-9]{5}(?:-[0-9]{3})?\Z")
MONEY = re.compile(r"[0-9]+(?:\.[0-9]+)?\Z")
VOUCHER = re.compile(r"-?[0-9]+(?:\.[0-9]+)?\Z")
DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})\Z")
CLASS_TERMS = ((18, "youth", 3, 7), (49, "adult", 5, 12),
               (73, "resident", 8, 19), (99, "priority", 13, 26))


def ratio(text):
    negative = text.startswith("-")
    unsigned = text[1:] if negative else text
    whole, dot, decimal = unsigned.partition(".")
    value = Fraction(int(whole + decimal), 10 ** len(decimal))
    return -value if negative else value


def nearest_away(value):
    """Nearest integer, exact halves away from zero, by quotient/remainder."""
    quotient, remainder = divmod(abs(value.numerator), value.denominator)
    rounded = quotient + (2 * remainder >= value.denominator)
    return -rounded if value < 0 else rounded


def expected(records):
    fares, per_class, excluded = {}, {}, []
    for record in records:
        passenger = record["passenger"]
        match = DATE.fullmatch(record["sailed"])
        date = tuple(map(int, match.groups())) if match else None
        valid = (PASS.fullmatch(record["passcode"]) is not None
                 and MONEY.fullmatch(record["fare"]) is not None
                 and MONEY.fullmatch(record["baggage"]) is not None
                 and VOUCHER.fullmatch(record["voucher"]) is not None
                 and date is not None
                 and 1 <= date[1] <= 12 and 1 <= date[2] <= 31
                 and date <= (2025, 6, 20))
        if valid:
            fare, baggage = ratio(record["fare"]), ratio(record["baggage"])
            valid = fare > 0 and baggage > 0
        if not valid:
            excluded.append(passenger)
            continue
        prefix = int(record["passcode"][:2])
        _, cls, levy, rate = next(t for t in CLASS_TERMS if prefix <= t[0])
        combined = fare + baggage
        raw = combined - min(combined * Fraction(9, 100), Fraction(18))
        quarters = raw * 4
        chargeable = Fraction(-(-quarters.numerator // quarters.denominator), 4)
        subtotal = levy + 2 + Fraction(rate, 100) * chargeable
        amount = subtotal * Fraction(107, 100)
        if cls == "priority":
            amount += 6
        settled = nearest_away((amount - ratio(record["voucher"])) * 100)
        fares[passenger] = settled
        per_class[cls] = per_class.get(cls, 0) + settled
    total = sum(fares.values())
    return {"total_minor": total, "billed": len(fares), "excluded": excluded,
            "fares": fares, "per_class": per_class,
            "mean_minor": nearest_away(Fraction(total, len(fares))) if fares else 0}


def assert_result(actual, wanted):
    """Equality alone accepts bools and floats in place of required integers."""
    assert type(actual) is dict, "return value must be a dict"
    assert set(actual) == set(wanted), "return keys differ from Rule R"
    for key in ("total_minor", "billed", "mean_minor"):
        assert type(actual[key]) is int, f"{key} must be int"
    assert type(actual["excluded"]) is list, "excluded must be list"
    assert all(type(p) is str for p in actual["excluded"]), "excluded IDs must be strings"
    for key in ("fares", "per_class"):
        assert type(actual[key]) is dict, f"{key} must be dict"
        assert all(type(p) is str and type(v) is int
                   for p, v in actual[key].items()), f"invalid {key} key/value types"
    assert actual == wanted, f"expected {wanted!r}; received {actual!r}"
