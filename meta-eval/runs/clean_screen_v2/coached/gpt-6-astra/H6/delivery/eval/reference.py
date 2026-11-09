"""Independent oracle: strict JSON -> schema validation -> Python integer math.

This module never imports a candidate or control. Decimal parses numeric tokens
exactly; all arithmetic is performed on arbitrary-precision ints. The test
corpus deliberately uses bounded exponents, not resource-exhaustion inputs.
"""
import json
import sys
from decimal import Decimal
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


class InvalidInput(ValueError):
    pass


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise InvalidInput("duplicate member")
        result[key] = value
    return result


def _constant(value):
    raise InvalidInput("non-JSON constant: " + value)


def parse_json(raw, reject_duplicates=True):
    return json.loads(raw.decode("utf-8"), parse_int=Decimal,
                      parse_float=Decimal, parse_constant=_constant,
                      object_pairs_hook=_pairs if reject_duplicates else dict)


def is_integer(value):
    return (isinstance(value, Decimal) and value.is_finite()
            and value == value.to_integral_value())


def expected(raw):
    """Return {identifier: exact int}, or raise InvalidInput."""
    try:
        if len(raw) > 8192:
            raise InvalidInput("too many bytes")
        doc = parse_json(raw)
        if not isinstance(doc, dict) or set(doc) != {"adjustment_sheets"}:
            raise InvalidInput("root structure")
        sheets = doc["adjustment_sheets"]
        if not isinstance(sheets, dict) or not sheets:
            raise InvalidInput("sheet collection")
        result = {}
        for key, sheet in sheets.items():
            if not key or not isinstance(sheet, dict) or set(sheet) != {"stat", "turns"}:
                raise InvalidInput("sheet structure")
            op, turns = sheet["stat"], sheet["turns"]
            if not isinstance(op, str) or op not in ("net_units", "event_count", "largest_adjustment"):
                raise InvalidInput("operation")
            if not isinstance(turns, list) or any(not is_integer(n) for n in turns):
                raise InvalidInput("integer array")
            if op == "largest_adjustment" and not turns:
                raise InvalidInput("empty maximum")
            values = [int(n) for n in turns]
            if op == "net_units":
                result[key] = sum(values)
            elif op == "event_count":
                result[key] = len(values)
            else:
                result[key] = max(values)
        return result
    except (ValueError, UnicodeError, TypeError, RecursionError, OverflowError) as exc:
        if isinstance(exc, InvalidInput):
            raise
        raise InvalidInput(str(exc)) from exc


def main():
    if len(sys.argv) != 3:
        return 2
    try:
        answer = expected(Path(sys.argv[1]).read_bytes())
    except (InvalidInput, OSError):
        return 1
    Path(sys.argv[2]).write_text(json.dumps({"stock_reports": answer}) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
