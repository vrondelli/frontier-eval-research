"""Independent executable positive control, not the subject's submission.

Self-tests derive intentionally defective controls by changing MODE.
"""
from decimal import Decimal
import json
from pathlib import Path
import sys

MODE = "correct"
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result and MODE != "duplicates":
            raise ValueError("duplicate member")
        result[key] = value
    return result


def constant(value):
    raise ValueError(value)


def main():
    source, target = map(Path, sys.argv[1:])
    try:
        data = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                          parse_float=float if MODE == "float" else Decimal,
                          parse_constant=constant)
        if not isinstance(data, dict) or set(data) != {"adjustment_sheets"}:
            raise ValueError("root")
        sheets = data["adjustment_sheets"]
        if not isinstance(sheets, dict) or not sheets:
            raise ValueError("sheets")
        results = {}
        for key, row in sheets.items():
            if not key or not isinstance(row, dict) or set(row) != {"stat", "turns"}:
                raise ValueError("row")
            stat, turns = row["stat"], row["turns"]
            if stat not in ("net_units", "event_count", "largest_adjustment") or not isinstance(turns, list):
                raise ValueError("stat/turns")
            if stat == "largest_adjustment" and not turns:
                raise ValueError("empty maximum")
            values = []
            for value in turns:
                if MODE == "count_skips_validation" and stat == "event_count":
                    values.append(0)
                    continue
                if MODE == "strict_int" and type(value) is not int:
                    raise ValueError("integer token required")
                if isinstance(value, bool) and MODE != "bool":
                    raise ValueError("boolean")
                if not isinstance(value, (int, Decimal, float)):
                    raise ValueError("number")
                integer = int(value)
                if integer != value:
                    raise ValueError("fraction")
                values.append(integer)
            if stat == "net_units":
                answer = sum(values)
                if MODE == "float":
                    answer = int(sum(float(v) for v in values))
                if MODE == "decimal_context":
                    answer = int(sum((Decimal(v) for v in values), Decimal(0)))
            elif stat == "event_count":
                answer = len(set(values)) if MODE == "deduplicate" else len(values)
            else:
                answer = max([0] + values) if MODE == "max_zero" else max(values)
            results[key] = answer
            if MODE == "partial":
                target.write_text(json.dumps({"stock_reports": results}), encoding="utf-8")
        if MODE == "example_only":
            results = {"warehouse-sample-1-0": 5, "warehouse-sample-1-1": 3, "warehouse-sample-1-2": -3}
        if MODE == "wrong_keys":
            results = {"renamed-" + key: value for key, value in results.items()}
        if MODE == "legal_alternative":
            text = '{"diagnostic":{"ok":true},"stock_reports":{' + ','.join(
                json.dumps(k) + ':' + (str(v) + 'e0' if v else '-0e999999999999999999999999')
                for k, v in results.items()) + '}}'
        elif MODE == "strings":
            text = json.dumps({"stock_reports": {k: str(v) for k, v in results.items()}})
        else:
            text = json.dumps({"stock_reports": results})
        target.write_text(text, encoding="utf-8")
        return 0
    except (ValueError, TypeError, ArithmeticError):
        if MODE in ("empty_results_error", "success_error"):
            target.write_text('{"stock_reports":{}}', encoding="utf-8")
        if MODE == "legal_alternative":
            target.write_text('{"error":"invalid input"}', encoding="utf-8")
        return 0 if MODE == "success_error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
