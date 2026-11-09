"""Decimal-based positive control and explicit fault switches for self-tests.

Not used to produce any grader expectations. Syntax is checked by splitting
strings rather than using the oracle's regular expressions.
"""

from datetime import date as calendar_date
from decimal import Decimal, localcontext, ROUND_CEILING, ROUND_DOWN, ROUND_HALF_UP, ROUND_HALF_EVEN


DEFECTS = (
    "unicode", "strip", "compact_pass", "youth_boundary", "adult_boundary",
    "resident_boundary", "fare_zero", "baggage_zero", "permissive_money",
    "voucher_positive", "voucher_absolute", "calendar", "date_ranges",
    "cutoff_exclusive", "ignore_year", "rebate_rate", "rebate_cap", "uncapped",
    "quarter_down", "no_quarter", "component_charge", "no_handling",
    "priority_before_surcharge", "no_surcharge", "half_even", "float_round",
    "clamp_negative", "mean_truncate", "mean_floor", "mean_half_even",
    "mean_unrounded", "sorted_excluded", "double_excluded", "all_classes",
    "extra_key", "float_values", "ignore_baggage_validity",
)


def make_control(defect=None):
    def digits(text):
        return bool(text) and text.isdecimal() and (defect == "unicode" or text.isascii())

    def number(text, signed=False):
        if signed and text.startswith("-"):
            text = text[1:]
        parts = text.split(".")
        return len(parts) <= 2 and all(digits(part) for part in parts)

    def settle_fares(records):
        with localcontext() as ctx:
            ctx.prec = 60 + sum(len(value) for row in records for value in row.values())
            fares, groups, excluded, unrounded = {}, {}, [], Decimal(0)
            for row in records:
                passenger = row["passenger"]
                values = {key: (value.strip() if defect == "strip" else value)
                          for key, value in row.items()}
                code, sailed = values["passcode"], values["sailed"]
                try:
                    code_parts = code.split("-")
                    valid_code = ((len(code_parts) == 1 and len(code_parts[0]) == 5)
                                  or (len(code_parts) == 2 and len(code_parts[0]) == 5
                                      and len(code_parts[1]) == 3))
                    if defect == "compact_pass" and len(code) == 8 and digits(code):
                        valid_code = True
                    valid_code &= all(digits(p) for p in code_parts)
                    if not valid_code:
                        raise ValueError
                    parts = sailed.split("-")
                    if len(parts) != 3 or list(map(len, parts)) != [4, 2, 2] or not all(map(digits, parts)):
                        raise ValueError
                    y, m, d = map(int, parts)
                    if defect != "date_ranges" and not (1 <= m <= 12 and 1 <= d <= 31):
                        raise ValueError
                    if defect == "calendar":
                        calendar_date(y, m, d)
                    if ((defect == "cutoff_exclusive" and (y, m, d) >= (2025, 6, 20))
                            or (defect == "ignore_year" and (m, d) > (6, 20))
                            or (defect not in ("cutoff_exclusive", "ignore_year")
                                and (y, m, d) > (2025, 6, 20))):
                        raise ValueError
                    amounts = []
                    for field in ("fare", "baggage"):
                        text = values[field]
                        if defect == "ignore_baggage_validity" and field == "baggage":
                            amounts.append(Decimal(1))
                            continue
                        if defect != "permissive_money" and not number(text):
                            raise ValueError
                        value = Decimal(text)
                        allow_zero = defect == field + "_zero"
                        if value < 0 or (value == 0 and not allow_zero):
                            raise ValueError
                        amounts.append(value)
                    if not number(values["voucher"], signed=True):
                        raise ValueError
                    voucher = Decimal(values["voucher"])
                    if defect == "voucher_positive" and voucher <= 0:
                        raise ValueError
                except (ValueError, ArithmeticError):
                    excluded.append(passenger)
                    if defect == "double_excluded":
                        excluded.append(passenger)
                    continue
                prefix = int(code[:2])
                youth = 17 if defect == "youth_boundary" else 18
                adult = 48 if defect == "adult_boundary" else 49
                resident = 72 if defect == "resident_boundary" else 73
                if prefix <= youth:
                    cls, levy, rate = "youth", 3, Decimal("0.07")
                elif prefix <= adult:
                    cls, levy, rate = "adult", 5, Decimal("0.12")
                elif prefix <= resident:
                    cls, levy, rate = "resident", 8, Decimal("0.19")
                else:
                    cls, levy, rate = "priority", 13, Decimal("0.26")

                def charge(combined):
                    rebate = combined * Decimal("0.9" if defect == "rebate_rate" else "0.09")
                    if defect != "uncapped":
                        rebate = min(rebate, Decimal(180 if defect == "rebate_cap" else 18))
                    raw = combined - rebate
                    if defect == "no_quarter":
                        return raw
                    rounding = ROUND_DOWN if defect == "quarter_down" else ROUND_CEILING
                    return (raw * 4).to_integral_value(rounding=rounding) / 4

                chargeable = (sum(map(charge, amounts)) if defect == "component_charge"
                              else charge(sum(amounts)))
                subtotal = levy + rate * chargeable + (0 if defect == "no_handling" else 2)
                priority = 6 if cls == "priority" else 0
                if defect == "priority_before_surcharge":
                    subtotal += priority
                    priority = 0
                surcharged = subtotal * (1 if defect == "no_surcharge" else Decimal("1.07"))
                amount = surcharged + priority - (abs(voucher) if defect == "voucher_absolute" else voucher)
                unrounded += amount * 100
                rounding = ROUND_HALF_EVEN if defect == "half_even" else ROUND_HALF_UP
                minor = (round(float(amount) * 100) if defect == "float_round" else
                         int((amount * 100).to_integral_value(rounding=rounding)))
                if defect == "clamp_negative":
                    minor = max(0, minor)
                fares[passenger] = minor
                groups[cls] = groups.get(cls, 0) + minor
            total, billed = sum(fares.values()), len(fares)
            mean = 0
            if billed:
                quotient = Decimal(total) / billed
                if defect == "mean_truncate":
                    mean = int(quotient)
                elif defect == "mean_floor":
                    mean = total // billed
                else:
                    if defect == "mean_unrounded":
                        quotient = unrounded / billed
                    rounding = ROUND_HALF_EVEN if defect == "mean_half_even" else ROUND_HALF_UP
                    mean = int(quotient.to_integral_value(rounding=rounding))
            if defect == "all_classes":
                for cls in ("youth", "adult", "resident", "priority"):
                    groups.setdefault(cls, 0)
            result = dict(total_minor=total, billed=billed,
                          excluded=sorted(excluded) if defect == "sorted_excluded" else excluded,
                          fares=fares, per_class=groups, mean_minor=mean)
            if defect == "extra_key":
                result["debug"] = True
            if defect == "float_values":
                result["total_minor"] = float(total)
            return result

    return settle_fares
