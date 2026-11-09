"""Deterministic corpus. Fixed cases have hand-derived oracle cross-checks."""
from dataclasses import dataclass
import json
import random


@dataclass(frozen=True)
class Case:
    name: str
    requirements: tuple
    raw: bytes
    valid: bool
    anchor: dict | None = None


def document(sheets):
    return json.dumps({"adjustment_sheets": sheets}, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def sheet(op, values):
    return {"stat": op, "turns": values}


def numeric(tokens, op="net_units", key="quantity"):
    return ('{"adjustment_sheets":{' + json.dumps(key) + ':{"stat":' +
            json.dumps(op) + ',"turns":[' + ','.join(tokens) + ']}}}').encode()


def build_cases(seed=73129, generated=24):
    cases = []

    def add(name, raw, valid=True, tags=("STRUCTURE",), anchor=None):
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        cases.append(Case(name, tuple(tags), raw, valid, anchor))

    add("example", document({
        "warehouse-sample-1-0": sheet("net_units", [4, -3, 4]),
        "warehouse-sample-1-1": sheet("event_count", [0, -2, -2]),
        "warehouse-sample-1-2": sheet("largest_adjustment", [-9, -3, -4])}),
        tags=("CLI", "OPERATIONS", "OUTPUT"),
        anchor={"warehouse-sample-1-0": 5, "warehouse-sample-1-1": 3,
                "warehouse-sample-1-2": -3})
    add("mixed_identifiers", document({
        "café / 空 \" \\ \n": sheet("net_units", [7, -11, 7]),
        "stock_reports": sheet("event_count", [8, 8, 8, 8]),
        "__proto__": sheet("largest_adjustment", [-18, -7, -99]),
        " ": sheet("net_units", [])}), tags=("CLI", "OUTPUT", "OPERATIONS"),
        anchor={"café / 空 \" \\ \n": 3, "stock_reports": 4, "__proto__": -7, " ": 0})
    add("empty_identities", document({"sum": sheet("net_units", []),
                                      "count": sheet("event_count", [])}),
        tags=("OPERATIONS",), anchor={"sum": 0, "count": 0})
    for name, op, values, answer in [
        ("repeated_events", "event_count", [0, -2, -2, 7, 7], 5),
        ("signed_maximum", "largest_adjustment", [-99, -3, -11], -3),
        ("sum_not_maximum", "net_units", [5, 5, -2], 8),
        ("singleton", "largest_adjustment", [0], 0),
        ("many_events", "event_count", [7] * 1500, 1500),
        ("unbounded_integer", "net_units", [2**100, 19], 2**100 + 19),
    ]:
        add(name, document({"quantity": sheet(op, values)}),
            tags=("OPERATIONS", "EXACT"), anchor={"quantity": answer})
    for name, tokens, op, answer in [
        ("integral_encodings", ["1.0", "1e3", "10e-1", "-0.0", "12.000", "2E+2"], "net_units", 1214),
        ("binary_precision", ["9007199254740993", "1", "-9007199254740992"], "net_units", 2),
        ("decimal_precision", ["9007199254740993.0", "-9007199254740992.0"], "net_units", 1),
        ("exponent_overflow", ["1e400", "-1e400", "7"], "net_units", 7),
        ("huge_result", ["1e400", "1"], "net_units", 10**400 + 1),
        ("large_coefficient", ["9" * 5000], "largest_adjustment", 10**5000 - 1),
        ("huge_count_values", ["1e400", "1e400", "-1e400"], "event_count", 3),
        ("signed_huge_max", ["-1e401", "-1e400"], "largest_adjustment", -(10**400)),
    ]:
        add(name, numeric(tokens, op), tags=("EXACT", "OPERATIONS"), anchor={"quantity": answer})
    add("many_sheets", document({f"id-{i}": sheet("net_units", [i, -2]) for i in range(80)}),
        tags=("OUTPUT", "OPERATIONS"), anchor={f"id-{i}": i - 2 for i in range(80)})
    boundary = document({"é" * 16: sheet("net_units", [2])})
    add("exact_byte_limit", boundary + b" " * (8192 - len(boundary)),
        tags=("JSON",), anchor={"é" * 16: 2})
    add("oversize_ascii", numeric(["1"]) + b" " * (8193 - len(numeric(["1"]))), False, ("JSON", "FAILURE"))
    oversized = document({"é" * 4050: sheet("net_units", [2])})
    # Ensure <=8192 characters but >8192 bytes, independently of key overhead.
    oversized += b" " * max(0, 8193 - len(oversized))
    add("oversize_utf8", oversized, False, ("JSON", "FAILURE"))
    invalid_docs = {
        "root_array": [], "root_null": None, "root_number": 3,
        "root_boolean": True, "missing_sheets": {},
        "extra_root": {"adjustment_sheets": {"q": sheet("net_units", [1])}, "extra": 0},
        "sheets_array": {"adjustment_sheets": []},
        "sheets_null": {"adjustment_sheets": None},
        "empty_sheets": {"adjustment_sheets": {}},
        "empty_identifier": {"adjustment_sheets": {"": sheet("net_units", [1])}},
    }
    for name, doc in invalid_docs.items():
        add(name, json.dumps(doc), False, ("STRUCTURE", "FAILURE"))
    bad_sheets = {
        "sheet_null": None, "sheet_array": [], "sheet_string": "net_units",
        "missing_stat": {"turns": [1]}, "missing_turns": {"stat": "net_units"},
        "extra_sheet": {"stat": "net_units", "turns": [1], "extra": 0},
        "unknown_stat": sheet("sum", [1]), "stat_array": sheet([], [1]),
        "stat_null": sheet(None, [1]), "stat_number": sheet(1, [1]),
        "turns_null": sheet("net_units", None), "turns_object": sheet("net_units", {}),
        "turns_string": sheet("event_count", "123"),
        "empty_max": sheet("largest_adjustment", []),
    }
    for name, bad in bad_sheets.items():
        add(name, document({"q": bad}), False, ("STRUCTURE", "FAILURE"))
    bad_tokens = ["true", "false", "null", '"3"', "[]", "{}", "1.5",
                  "-0.5", "1e-400", "1.00000000000000000000000000000000001",
                  "9007199254740992.1", "NaN", "Infinity", "-Infinity"]
    for i, token in enumerate(bad_tokens):
        for op in ("net_units", "event_count", "largest_adjustment"):
            add(f"bad_number_{i}_{op}", numeric([token], op), False, ("EXACT", "FAILURE"))
    for name, raw in {
        "duplicate_root": '{"adjustment_sheets":{"q":{"stat":"net_units","turns":[1]}},"adjustment_sheets":{"q":{"stat":"net_units","turns":[2]}}}',
        "duplicate_identifier": '{"adjustment_sheets":{"q":{"stat":"net_units","turns":[1]},"q":{"stat":"net_units","turns":[2]}}}',
        "duplicate_escaped_identifier": '{"adjustment_sheets":{"q":{"stat":"net_units","turns":[1]},"\\u0071":{"stat":"net_units","turns":[2]}}}',
        "duplicate_stat": '{"adjustment_sheets":{"q":{"stat":"net_units","stat":"event_count","turns":[2]}}}',
        "duplicate_turns": '{"adjustment_sheets":{"q":{"stat":"net_units","turns":[1],"turns":[2]}}}',
        "duplicate_escaped_field": '{"adjustment_sheets":{"q":{"stat":"net_units","turns":[1],"tu\\u0072ns":[2]}}}',
        "truncated": '{"adjustment_sheets":', "trailing_document": '{} {}',
        "empty_file": '', "trailing_comma": '{"adjustment_sheets":{},}',
        "invalid_utf8": b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[1]}}}',
        "leading_zero": numeric(["01"]),
    }.items():
        add(name, raw, False, ("JSON", "FAILURE"))
    add("late_invalid_sheet", document({"valid-first": sheet("net_units", [9]),
                                         "bad-last": sheet("largest_adjustment", [])}),
        False, ("STRUCTURE", "FAILURE"))
    rng = random.Random(seed)
    for i in range(generated):
        sheets, answers = {}, {}
        for j in range(rng.randint(1, 8)):
            op = rng.choice(("net_units", "event_count", "largest_adjustment"))
            values = [rng.randint(-(10**35), 10**35) for _ in range(rng.randint(1, 12))]
            if op != "largest_adjustment" and rng.random() < 0.2:
                values = []
            elif values and rng.random() < 0.5:
                values += values[:2]
            key = f"{i}-随机-{j}-{rng.getrandbits(32):x}"
            sheets[key] = sheet(op, values)
            answers[key] = sum(values) if op == "net_units" else len(values) if op == "event_count" else max(values)
        add(f"generated_{i:03}", document(sheets), tags=("EXACT", "OPERATIONS", "OUTPUT"), anchor=answers)
    assert len({case.name for case in cases}) == len(cases)
    return cases
