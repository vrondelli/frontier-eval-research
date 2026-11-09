"""Standalone positive control. Modes generate deliberate negative controls.

Number parsing is lexical integer arithmetic, independent of the Decimal-based
oracle. This file imports no evaluator code and works with site packages off.
"""
import json
from pathlib import Path
import re
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


class Number(str):
    pass


def integer(token, mode):
    if mode == "boolean_values" and type(token) is bool:
        return int(token)
    if not isinstance(token, Number):
        raise ValueError("expected a JSON number")
    if mode == "truncate_fractions":
        return int(float(token))
    if mode == "float_math":
        return int(float(token))
    if mode == "int_tokens_only" and any(c in token for c in ".eE"):
        raise ValueError("integer token required")
    match = re.fullmatch(r"(-?)([0-9]+)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?", token)
    if match is None:
        raise ValueError("invalid number")
    sign, whole, fractional, exponent = match.groups()
    fractional = fractional or ""
    digits = (whole + fractional).lstrip("0") or "0"
    scale = int(exponent or "0") - len(fractional)
    if digits == "0":
        return 0
    if scale < 0:
        places = -scale
        if places >= len(digits) or any(c != "0" for c in digits[-places:]):
            raise ValueError("nonintegral number")
        digits = digits[:-places]
        scale = 0
    result = int(digits) * 10**scale
    if sign:
        result = -result
    if mode == "bound64" and not -(2**63) <= result < 2**63:
        raise ValueError("out of range")
    if mode == "reject_big_digits" and len(digits) > 4300:
        raise ValueError("too many digits")
    return result


def encode(result, mode):
    if mode == "extra_identifier":
        result = dict(result, unexpected=0)
    if mode == "strings_output":
        result = {key: str(value) for key, value in result.items()}
    if mode == "boolean_output":
        result = {key: bool(value) for key, value in result.items()}
    if mode == "exponent_metadata":
        pairs = []
        for index, (key, value) in enumerate(reversed(list(result.items()))):
            encoding = str(value) + ("e0" if index % 2 else ".000")
            pairs.append(json.dumps(key) + ":" + encoding)
        return '{"diagnostic":{"ok":true,"ratio":0.25},"stock_reports":{' + ",".join(pairs) + "}}"
    return json.dumps({"stock_reports": result}, ensure_ascii=True)


def main(mode="correct"):
    if len(sys.argv) != 3:
        raise SystemExit(2)
    destination = Path(sys.argv[2])
    try:
        raw = Path(sys.argv[1]).read_bytes()
        size = len(raw.decode("utf-8")) if mode == "character_limit" else len(raw)
        if mode != "no_size_limit" and size > 8192:
            raise ValueError("input too large")

        def pairs(items):
            obj = {}
            for name, value in items:
                if mode != "allow_duplicates" and name in obj:
                    raise ValueError("duplicate key")
                obj[name] = value
            return obj

        def bad_constant(value):
            raise ValueError("nonstandard JSON number")

        doc = json.loads(raw.decode("utf-8"), parse_int=Number, parse_float=Number,
                         parse_constant=bad_constant, object_pairs_hook=pairs)
        if not isinstance(doc, dict) or "adjustment_sheets" not in doc:
            raise ValueError("invalid root")
        if mode != "extra_properties" and len(doc) != 1:
            raise ValueError("unknown root member")
        rows = doc["adjustment_sheets"]
        if not isinstance(rows, dict) or len(rows) == 0:
            raise ValueError("nonempty object required")
        result = {}
        for identifier, row in rows.items():
            if identifier == "" or not isinstance(row, dict):
                raise ValueError("invalid sheet")
            if "stat" not in row or "turns" not in row:
                raise ValueError("missing member")
            if mode != "extra_properties" and len(row) != 2:
                raise ValueError("extra member")
            operation, values = row["stat"], row["turns"]
            if type(operation) is not str or operation not in ("net_units", "event_count", "largest_adjustment"):
                raise ValueError("unknown operation")
            if not isinstance(values, list):
                raise ValueError("array required")
            numbers = ([0] * len(values) if mode == "unchecked_count" and operation == "event_count"
                       else [integer(v, mode) for v in values])
            if operation == "net_units":
                answer = max(numbers, default=0) if mode == "sum_as_max" else sum(numbers)
            elif operation == "event_count":
                answer = len(set(numbers)) if mode == "count_unique" else len(numbers)
            else:
                if not numbers:
                    raise ValueError("maximum requires entries")
                if mode == "abs_max":
                    answer = max(abs(v) for v in numbers)
                elif mode == "zero_max":
                    answer = max([0] + numbers)
                else:
                    answer = max(numbers)
            result[identifier] = answer
            if mode == "partial_on_error":
                destination.write_text(encode(result, mode), encoding="utf-8")
            if mode == "first_only":
                break
        if mode == "example_only":
            result = {"warehouse-sample-1-0": 5, "warehouse-sample-1-1": 3, "warehouse-sample-1-2": -3}
        if mode != "missing_output":
            destination.write_text(encode(result, mode), encoding="utf-8")
        raise SystemExit(1 if mode == "nonzero_success" else 0)
    except (ValueError, TypeError, OSError, OverflowError, RecursionError) as exc:
        if mode == "empty_on_error":
            destination.write_text('{"stock_reports":{}}', encoding="utf-8")
        elif mode == "error_envelope":
            destination.write_text(json.dumps({"error": str(exc)}), encoding="utf-8")
        elif mode == "malformed_error":
            destination.write_text("not json", encoding="utf-8")
        raise SystemExit(0 if mode == "success_on_error" else 2)


if __name__ == "__main__":
    main('abs_max')
