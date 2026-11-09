#!/usr/bin/env python3
"""Black-box evaluation of the warehouse numeric export CLI (stdlib only)."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import time

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


class Number(str):
    """Retain the exact JSON spelling; never pass through binary floating point."""


class Object(dict):
    def __init__(self, pairs):
        super().__init__(pairs)
        self.members = pairs


def reject_constant(token):
    raise ValueError(f"non-JSON constant {token}")


def read_json(raw):
    # Decode explicitly: json.loads(bytes) also accepts UTF-16/32.
    return json.loads(raw.decode("utf-8"), parse_int=Number, parse_float=Number,
                      parse_constant=reject_constant, object_pairs_hook=Object)


def integer_identity(value):
    """Canonical (signed significant digits, base-ten exponent), without expansion.

    Even 1e999999999999999999999 is inexpensive to compare. Removing trailing
    zeros also recognizes integral decimals such as 1000e-3 and negative zero.
    """
    if not isinstance(value, Number):
        raise ValueError("report value is not a JSON number")
    match = re.fullmatch(r"(-?)(0|[1-9][0-9]*)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?", value)
    if not match:
        raise ValueError("invalid JSON number")
    sign, whole, fraction, power = match.groups()
    fraction = fraction or ""
    digits = (whole + fraction).lstrip("0")
    if not digits:
        return ("0", 0)
    exponent = int(power or "0") - len(fraction)
    significant = digits.rstrip("0")
    exponent += len(digits) - len(significant)
    if exponent < 0:
        raise ValueError("report value is not a mathematical integer")
    return (sign + significant, exponent)


@dataclass(frozen=True)
class Case:
    name: str
    group: str
    raw: bytes
    expected: dict[str, str] | None  # None means invalid input.


def document(rows):
    return json.dumps({"adjustment_sheets": rows}, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def make_cases():
    cases = []

    def valid(name, rows, group="semantics"):
        expected = {}
        for key, row in rows.items():
            values = row["turns"]
            stat = row["stat"]
            result = (sum(values) if stat == "net_units" else
                      len(values) if stat == "event_count" else max(values))
            expected[key] = str(result)
        cases.append(Case(name, group, document(rows), expected))

    def raw_valid(name, turns, stat, result, group="exact_numbers"):
        raw = ('{"adjustment_sheets":{"probe":{"stat":' + json.dumps(stat) +
               ',"turns":[' + turns + ']}}}').encode("utf-8")
        cases.append(Case(name, group, raw, {"probe": result}))

    def invalid(name, raw, group="validation"):
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        cases.append(Case(name, group, raw, None))

    valid("public_example", {
        "warehouse-sample-1-0": {"stat": "net_units", "turns": [4, -3, 4]},
        "warehouse-sample-1-1": {"stat": "event_count", "turns": [0, -2, -2]},
        "warehouse-sample-1-2": {"stat": "largest_adjustment", "turns": [-9, -3, -4]},
    })
    valid("empty_sum_and_count", {
        "zero net": {"stat": "net_units", "turns": []},
        "zero events": {"stat": "event_count", "turns": []},
    })
    valid("repetitions_are_events", {
        "repeat sum": {"stat": "net_units", "turns": [7, 7, -2, -2, 7]},
        "repeat count": {"stat": "event_count", "turns": [8] * 23},
        "negative maximum": {"stat": "largest_adjustment", "turns": [-10, -7, -20]},
    })
    valid("singletons_and_zero", {
        "net": {"stat": "net_units", "turns": [-17]},
        "count": {"stat": "event_count", "turns": [0]},
        "max": {"stat": "largest_adjustment", "turns": [0]},
    })
    valid("identifier_preservation", {
        key: {"stat": "net_units", "turns": [index, -9]}
        for index, key in enumerate([" ", "0", "01", "__proto__", "a.b", "a/b",
                                     "quote\"slash\\", "line\nbreak", "estoque-\u00e7", "\u8c03\u6574", "\U0001f4e6"])
    })
    valid("all_sheets_and_order", {
        f"shelf-{i:03}": {"stat": ("net_units", "event_count", "largest_adjustment")[i % 3],
                            "turns": [i - 30, i, -i]}
        for i in range(55)
    })
    valid("long_array", {"many": {"stat": "event_count", "turns": [1, -1, 0] * 850}})

    for name, turns, stat, result in [
        ("integral_decimals", "1.0,-2.000,3.00", "net_units", "2"),
        ("integral_exponents", "1e3,20e-1,0.01e2,-3E+2", "net_units", "703"),
        ("negative_zero", "-0,-0.0,-0e999999999999999999999", "net_units", "0"),
        ("encoded_repetitions", "1,1.0,10e-1,0.1e1", "event_count", "4"),
        ("encoded_negative_maximum", "-9e2,-3.0e2,-400.00", "largest_adjustment", "-300"),
        ("binary64_integer_boundary", "9007199254740993,-9007199254740992", "net_units", "1"),
        ("binary64_decimal_boundary", "9007199254740993.0,-9007199254740992.0", "net_units", "1"),
        ("binary64_maximum_boundary", "9007199254740992,9007199254740993", "largest_adjustment", "9007199254740993"),
        ("signed64_overflow", "9223372036854775807,1", "net_units", "9223372036854775808"),
        ("decimal_context_cancellation", "1e120,1,-1e120", "net_units", "1"),
        ("decimal_context_order", "1e120,-1e120,1", "net_units", "1"),
        ("exponent_overflow_cancellation", "1e400,-1e400,7", "net_units", "7"),
        ("exponent_overflow_max", "-1e400,-2e400", "largest_adjustment", "-1e400"),
        ("negative_exponent_order", "-1e400,-2e399,-8e450", "largest_adjustment", "-2e399"),
        ("beyond_default_digit_limit", "1" + "0" * 4600, "net_units", "1e4600"),
        ("large_exponent_sum", "1e10000,2e10000", "net_units", "3e10000"),
        ("large_exponent_cancellation", "1e10000,1,-1e10000", "net_units", "1"),
        ("extreme_exponent_singleton", "1e999999999999999999999", "net_units", "1e999999999999999999999"),
        ("extreme_exponent_count", "1e999999999999999999999,-1e999999999999999999999", "event_count", "2"),
        ("extreme_exponent_cancel", "1e999999999999999999999,-1e999999999999999999999,3", "net_units", "3"),
        ("extreme_exponent_max", "-2e999999999999999999999,-1e999999999999999999999", "largest_adjustment", "-1e999999999999999999999"),
    ]:
        raw_valid(name, turns, stat, result)

    rng = random.Random(20261108)
    for i in range(12):
        rows = {}
        for j, stat in enumerate(("net_units", "event_count", "largest_adjustment")):
            size = rng.randrange(1 if stat == "largest_adjustment" else 0, 30)
            values = [rng.randrange(-10**45, 10**45) for _ in range(size)]
            if size > 2:
                values[-1] = values[0]
            rows[f"generated-{i}-{j}"] = {"stat": stat, "turns": values}
        valid(f"generated_{i:02}", rows, "generated")

    # The byte limit is inclusive and counts UTF-8 bytes, not characters.
    base = document({"edge": {"stat": "net_units", "turns": [2, -1]}})
    cases.append(Case("exactly_8192_bytes", "byte_limit", base + b" " * (8192 - len(base)), {"edge": "1"}))
    invalid("8193_bytes", base + b" " * (8193 - len(base)), "byte_limit")
    unicode_base = document({"\u00e9" * 1800: {"stat": "event_count", "turns": [0]}})
    padding = 8193 - len(unicode_base)
    invalid("utf8_bytes_not_characters", unicode_base + b" " * padding, "byte_limit")

    invalid_rows = [
        ("empty_identifier", {"": {"stat": "net_units", "turns": []}}),
        ("empty_sheets", {}),
        ("sheet_not_object", {"x": []}),
        ("missing_stat", {"x": {"turns": [1]}}),
        ("missing_turns", {"x": {"stat": "net_units"}}),
        ("unknown_stat", {"x": {"stat": "sum", "turns": [1]}}),
        ("stat_not_string", {"x": {"stat": 1, "turns": [1]}}),
        ("extra_sheet_member", {"x": {"stat": "net_units", "turns": [], "note": 1}}),
        ("empty_maximum", {"x": {"stat": "largest_adjustment", "turns": []}}),
    ]
    for name, rows in invalid_rows:
        invalid(name, document(rows))
    for stat in ("net_units", "event_count", "largest_adjustment"):
        for label, bad in [("boolean_true", True), ("boolean_false", False), ("null", None),
                           ("string", "1"), ("object", {}), ("array", []), ("fraction", 1.25)]:
            invalid(f"{stat}_{label}", document({"x": {"stat": stat, "turns": [bad]}}))
        for label, bad in [("null", None), ("object", {}), ("string", "12"), ("number", 12)]:
            invalid(f"{stat}_turns_{label}", document({"x": {"stat": stat, "turns": bad}}))
    for name, raw in [
        ("root_array", "[]"), ("root_null", "null"), ("root_string", '"x"'),
        ("missing_sheets", "{}"), ("sheets_null", '{"adjustment_sheets":null}'),
        ("sheets_array", '{"adjustment_sheets":[]}'),
        ("extra_root_member", base.decode()[:-1] + ',"extra":true}'),
        ("truncated_json", '{"adjustment_sheets":'), ("empty_file", ""),
        ("trailing_document", base.decode() + " {}"),
        ("comment", base.decode() + " // comment"),
        ("trailing_comma", '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[1,]}}}'),
    ]:
        invalid(name, raw)
    for name, token in [
        ("rounded_fraction", "9007199254740992.5"),
        ("tiny_fraction", "1e-4000"),
        ("extreme_tiny_fraction", "1e-999999999999999999999"),
        ("decimal_hidden_fraction", "1.0000000000000000000000000000000000000001"),
        ("NaN", "NaN"), ("positive_infinity", "Infinity"), ("negative_infinity", "-Infinity"),
        ("leading_zero", "01"), ("plus_sign", "+1"), ("leading_dot", ".5"), ("trailing_dot", "1."),
    ]:
        invalid(name, '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[' + token + ']}}}')
    for stat in ("event_count", "largest_adjustment"):
        for name, token in [("rounded_fraction", "9007199254740992.5"), ("tiny_fraction", "1e-4000")]:
            invalid(f"{stat}_{name}", '{"adjustment_sheets":{"x":{"stat":' + json.dumps(stat) + ',"turns":[' + token + ']}}}')

    row = '{"stat":"net_units","turns":[1]}'
    for name, raw in [
        ("duplicate_root", '{"adjustment_sheets":{"x":' + row + '},"adjustment_sheets":{"y":' + row + '}}'),
        ("duplicate_identifier", '{"adjustment_sheets":{"x":' + row + ',"x":' + row + '}}'),
        ("escaped_duplicate_identifier", '{"adjustment_sheets":{"x":' + row + ',"\\u0078":' + row + '}}'),
        ("duplicate_stat", '{"adjustment_sheets":{"x":{"stat":"net_units","stat":"event_count","turns":[1]}}}'),
        ("duplicate_turns", '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[1],"turns":[2]}}}'),
    ]:
        invalid(name, raw, "duplicates")
    invalid("invalid_utf8", b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[]}}}')
    invalid("utf16_document", base.decode().encode("utf-16"))
    # A valid sheet preceding a bad sheet catches incremental output before validation.
    invalid("late_invalid_sheet", document({
        "good": {"stat": "net_units", "turns": [5]},
        "bad": {"stat": "largest_adjustment", "turns": []},
    }), "failure_atomicity")
    invalid("late_invalid_value", document({
        "good": {"stat": "event_count", "turns": [1, 2]},
        "bad": {"stat": "net_units", "turns": [1] * 100 + [False]},
    }), "failure_atomicity")
    assert len({c.name for c in cases}) == len(cases)
    assert all(len(c.raw) <= 8192 for c in cases if c.expected is not None)
    return cases


def judge_output(case, returncode, raw):
    if case.expected is None:
        if returncode == 0:
            return "invalid input exited zero"
        if raw is None or not raw.strip():
            return None
        try:
            obj = read_json(raw)
        except (ValueError, UnicodeError, RecursionError):
            return "failure output is neither absent nor a JSON error envelope"
        if not isinstance(obj, dict):
            return "failure output is not an error envelope object"
        if any(key == "stock_reports" and isinstance(value, dict) for key, value in obj.members):
            return "failure wrote a results object (including empty/partial results)"
        return None
    if returncode != 0:
        return f"valid input exited {returncode}"
    if raw is None:
        return "output file was not created"
    try:
        obj = read_json(raw)
        if not isinstance(obj, dict) or not isinstance(obj.get("stock_reports"), dict):
            return "missing stock_reports object"
        reports = obj["stock_reports"]
        if reports.keys() != case.expected.keys():
            return "report identifiers differ from the input identifiers"
        for key, expected in case.expected.items():
            if integer_identity(reports[key]) != integer_identity(Number(expected)):
                return f"incorrect mathematical integer for {key!r}"
    except (ValueError, UnicodeError, RecursionError) as exc:
        return f"invalid output: {str(exc)[:240]}"
    return None


def run_case(case, command, cwd, timeout):
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="numeric export evaluation ", dir=Path.cwd()) as temp:
        folder = Path(temp)
        input_path = folder / "input stock adjustments.json"
        output_path = folder / "output stock reports.json"
        input_path.write_bytes(case.raw)
        # Logs are files so a noisy candidate cannot exhaust grader pipe memory.
        with (folder / "stdout.log").open("wb") as out, (folder / "stderr.log").open("wb") as err:
            try:
                proc = subprocess.run([*command, str(input_path), str(output_path)],
                                      cwd=cwd, stdout=out, stderr=err, timeout=timeout,
                                      shell=False)
            except subprocess.TimeoutExpired:
                return {"name": case.name, "group": case.group, "passed": False,
                        "reason": f"command exceeded {timeout:g}s", "seconds": round(time.monotonic() - started, 3)}
            except OSError as exc:
                return {"name": case.name, "group": case.group, "passed": False,
                        "reason": f"could not execute command: {exc}", "seconds": round(time.monotonic() - started, 3)}
        if output_path.is_file() and output_path.stat().st_size > 2_000_000:
            reason = "output exceeds evaluation resource limit (2 MB)"
        else:
            try:
                raw = output_path.read_bytes() if output_path.exists() else None
                reason = judge_output(case, proc.returncode, raw)
            except OSError as exc:
                reason = f"could not read output file: {exc}"
        diagnostic = ""
        if reason:
            with (folder / "stderr.log").open("rb") as log:
                diagnostic = log.read(1000).decode("utf-8", errors="replace")
        result = {"name": case.name, "group": case.group, "passed": reason is None,
                  "returncode": proc.returncode, "seconds": round(time.monotonic() - started, 3)}
        if reason:
            result.update(reason=reason, stderr=diagnostic)
        return result


def evaluate(command, cwd=None, timeout=10, cases=None):
    cases = make_cases() if cases is None else cases
    results = [run_case(case, command, cwd, timeout) for case in cases]
    passed = sum(result["passed"] for result in results)
    groups = {}
    for result in results:
        group = groups.setdefault(result["group"], {"passed": 0, "total": 0})
        group["total"] += 1
        group["passed"] += result["passed"]
    success = bool(results) and passed == len(results)
    return {"evaluation": "warehouse-numeric-export-v1", "passed": passed,
            "total": len(results), "score": int(success),
            "pass_rate": passed / len(results) if results else 0,
            "success": success, "groups": groups, "cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, help="candidate working directory")
    parser.add_argument("--timeout", type=float, default=10, help="seconds per case (default: 10)")
    parser.add_argument("--report", type=Path, help="also save the JSON report")
    parser.add_argument("--list", action="store_true", help="list test cases without running a candidate")
    parser.add_argument("--case", action="append", help="run only this exact case name; repeatable, for diagnosis")
    parser.add_argument("--command", nargs=argparse.REMAINDER, help="candidate command; place this option last")
    args = parser.parse_args()
    if args.list:
        print(json.dumps([{"name": c.name, "group": c.group, "valid": c.expected is not None,
                           "input_bytes": len(c.raw)} for c in make_cases()], indent=2))
        return 0
    if not args.command:
        parser.error("--command is required unless --list is used")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    cases = make_cases()
    if args.case:
        unknown = set(args.case) - {case.name for case in cases}
        if unknown:
            parser.error("unknown case(s): " + ", ".join(sorted(unknown)))
        cases = [case for case in cases if case.name in args.case]
    report = evaluate(args.command, args.cwd, args.timeout, cases)
    report["scope"] = "selected_cases" if args.case else "full_suite"
    rendered = json.dumps(report, indent=2, ensure_ascii=True)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
