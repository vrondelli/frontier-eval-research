"""Independent self-test control, not the solution under evaluation.

Its arithmetic is bounded to practical exponent spans; it supports every probe.
The optional first argument selects a deliberately faulty implementation.
"""
import json
from decimal import Decimal
from pathlib import Path
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


class Numeric:
    def __init__(self, text):
        self.text = text


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate object member")
        result[key] = value
    return result


def number(value, mode):
    if mode == "boolean" and isinstance(value, bool):
        value = Numeric("1" if value else "0")
    if not isinstance(value, Numeric):
        raise ValueError("not a number")
    text = value.text.lower()
    if mode == "float":
        text = str(float(text))
    mantissa, _, power = text.partition("e")
    whole, dot, fraction = mantissa.partition(".")
    coefficient = int(whole + fraction)
    exponent = int(power or "0") - len(fraction)
    if coefficient == 0:
        return (0, 0)
    while coefficient % 10 == 0:
        coefficient //= 10
        exponent += 1
    if exponent < 0:
        raise ValueError("fractional measurement")
    return coefficient, exponent


def add(values):
    terms = {}
    for coefficient, exponent in values:
        terms[exponent] = terms.get(exponent, 0) + coefficient
    terms = {power: coefficient for power, coefficient in terms.items() if coefficient}
    if not terms:
        return (0, 0)
    if len(terms) == 1:
        exponent, coefficient = next(iter(terms.items()))
        return coefficient, exponent
    minimum = min(terms)
    if max(terms) - minimum > 20000:
        raise ValueError("self-test control's expansion resource bound")
    return sum(coefficient * 10 ** (power - minimum) for power, coefficient in terms.items()), minimum


def order_key(value):
    coefficient, exponent = value
    if not coefficient:
        return (0, 0, "")
    digits = str(abs(coefficient))
    # Compare decimal magnitudes without allocating exponent-many zeroes.
    return (1 if coefficient > 0 else -1, len(digits) + exponent, digits)


def greater(left, right):
    a, b = order_key(left), order_key(right)
    if a[0] != b[0]:
        return a[0] > b[0]
    if a[0] == 0:
        return False
    width = max(len(a[2]), len(b[2]))
    comparison = (a[1], a[2].ljust(width, "0")) > (b[1], b[2].ljust(width, "0"))
    if a[0] > 0:
        return comparison
    return (a[1], a[2].ljust(width, "0")) < (b[1], b[2].ljust(width, "0"))


def encode(value, mode):
    coefficient, exponent = value
    if mode == "equivalent":
        return f"{coefficient}.0e{exponent:+d}"
    return f"{coefficient}e{exponent}"


def main():
    args = sys.argv[1:]
    mode = args.pop(0) if len(args) == 3 else "reference"
    source, destination = map(Path, args)
    results = {}
    try:
        raw = source.read_bytes()
        if mode == "always_reject":
            raise ValueError("always rejects")
        if len(raw) > 8192 and mode != "ignore_size":
            raise ValueError("oversized input")
        obj = json.loads(raw.decode("utf-8"), parse_int=Numeric, parse_float=Numeric,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("constant")),
                         object_pairs_hook=dict if mode == "duplicates" else pairs)
        if not isinstance(obj, dict) or set(obj) != {"adjustment_sheets"}:
            raise ValueError("root schema")
        rows = obj["adjustment_sheets"]
        if not isinstance(rows, dict) or not rows:
            raise ValueError("sheets schema")
        for key, row in rows.items():
            if not key or not isinstance(row, dict) or set(row) != {"stat", "turns"}:
                raise ValueError("sheet schema")
            stat, entries = row["stat"], row["turns"]
            if stat not in ("net_units", "event_count", "largest_adjustment") or not isinstance(entries, list):
                raise ValueError("stat or turns schema")
            values = [number(entry, mode) for entry in entries]
            if stat == "net_units":
                if mode == "float":
                    value = number(Numeric(str(sum(float(entry.text) for entry in entries))), "reference")
                elif mode == "decimal_context":
                    value = number(Numeric(str(sum((Decimal(entry.text) for entry in entries), Decimal(0)))), "reference")
                else:
                    value = add(values)
            elif stat == "event_count":
                value = (len(set(values)) if mode == "unique_events" else len(values), 0)
            else:
                if not values and mode != "empty_max":
                    raise ValueError("empty maximum")
                value = values[0] if values else (0, 0)
                for item in values[1:]:
                    if mode == "absolute_max":
                        use = greater((abs(item[0]), item[1]), (abs(value[0]), value[1]))
                    else:
                        use = greater(item, value)
                    if use:
                        value = item
            results[key] = value
        if mode == "drop_row":
            results.pop(next(iter(results)))
        encoded = ",".join(json.dumps(key) + ":" + encode(value, mode) for key, value in results.items())
        # Noninteger metadata is deliberately allowed by the output schema.
        destination.write_text('{"stock_reports":{' + encoded + '},"diagnostics":{"ratio":1.25,"ok":true}}', encoding="utf-8")
        return 0
    except (ValueError, TypeError, UnicodeError, OverflowError) as exc:
        if mode == "empty_failure":
            destination.write_text('{"stock_reports":{}}', encoding="utf-8")
        elif mode == "partial_failure":
            encoded = ",".join(json.dumps(key) + ":" + encode(value, mode) for key, value in results.items())
            destination.write_text('{"stock_reports":{' + encoded + '}}', encoding="utf-8")
        else:
            destination.write_text(json.dumps({"error": str(exc)}), encoding="utf-8")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
