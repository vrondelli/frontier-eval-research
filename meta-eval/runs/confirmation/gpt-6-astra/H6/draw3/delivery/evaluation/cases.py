"""Public-contract probes; expectations are built from mathematical integers.

Numeric wire spellings and mathematical values are supplied separately, so the
oracle never parses input with the candidate's numeric conversion strategy.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import random
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class Case:
    name: str
    category: str
    payload: bytes
    expected: dict[str, int] | None


def valid(name, rows, category="semantics"):
    encoded, expected = {}, {}
    for key, stat, values in rows:
        numbers = [v[1] if isinstance(v, tuple) else v for v in values]
        tokens = [v[0] if isinstance(v, tuple) else str(v) for v in values]
        encoded[key] = ('{"stat":' + json.dumps(stat) + ',"turns":['
                        + ','.join(tokens) + ']}')
        expected[key] = (sum(numbers) if stat == "net_units" else
                         len(numbers) if stat == "event_count" else max(numbers))
    payload = ('{"adjustment_sheets":{' + ','.join(
        json.dumps(k, ensure_ascii=False) + ':' + v for k, v in encoded.items()) + '}}')
    return Case(name, category, payload.encode("utf-8"), expected)


def build_cases():
    cases = []
    def add(name, rows, category="semantics"):
        cases.append(valid(name, rows, category))
    def bad(name, value, raw=False, category="validation"):
        payload = value if raw else json.dumps(value, ensure_ascii=False)
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        cases.append(Case(name, category, payload, None))

    example = Path(__file__).resolve().parents[1] / "input/workspace/example.json"
    cases.append(Case("provided_example", "semantics", example.read_bytes(), {
        "warehouse-sample-1-0": 5, "warehouse-sample-1-1": 3,
        "warehouse-sample-1-2": -3}))
    add("empty_identities", [("empty sum", "net_units", []), ("empty count", "event_count", [])])
    add("signed_and_repeated", [("sum", "net_units", [-7, 2, -7, 0]),
        ("count", "event_count", [-7, -7, 0, 0, 0]),
        ("max", "largest_adjustment", [-900, -2, -30, -2])])
    add("singleton_and_zero", [("s", "net_units", [-11]),
        ("c", "event_count", [0]), ("m", "largest_adjustment", [0])])
    add("positive_max", [("m", "largest_adjustment", [2, 100, 3, -500])])
    add("identifier_preservation", [(key, "net_units", [n, -1]) for n, key in enumerate(
        ["仓庫📦", "a/b", 'quote"slash\\', "\n", " ", "__proto__", "é", "e\u0301", "0", "A", "a"])])
    for stat in ("net_units", "event_count", "largest_adjustment"):
        add("integral_spellings_" + stat, [("row", stat,
            [("1.0", 1), ("-2.000", -2), ("3e2", 300), ("120e-1", 12),
             ("0.01e2", 1), ("-0.0", 0), ("0e9999", 0), ("2E+1", 20)])], "numeric")
    large = 10**90 + 123456789
    add("beyond_binary64", [("s", "net_units", [9007199254740993, 2]),
        ("m", "largest_adjustment", [9007199254740992, 9007199254740993]),
        ("negative", "largest_adjustment", [-9007199254740993, -9007199254740992])], "numeric")
    add("exact_decimal_cancellation", [("s", "net_units",
        [(str(large) + ".0", large), 1, (str(-large) + ".000", -large)])], "numeric")
    add("exact_integer_cancellation", [("s", "net_units", [large, 1, -large])], "numeric")
    add("overflow_exponents", [("sum", "net_units", [("1e400", 10**400), 1]),
        ("max", "largest_adjustment", [("-1e400", -10**400), ("-2e400", -2*10**400)]),
        ("count", "event_count", [("1e4000", 10**4000)])], "numeric")
    add("decimal_precision", [("s", "net_units", [("123456789012345678901234567890.0", 123456789012345678901234567890), 1])], "numeric")
    add("long_integer_literal", [("s", "net_units", [10**5000 + 7])], "numeric")
    add("long_decimal_literal", [("s", "net_units", [(str(10**5000 + 9) + ".0", 10**5000 + 9)])], "numeric")
    add("large_output_from_small_input", [("s", "net_units", [("1e6000", 10**6000), 1])], "numeric")
    add("many_events", [("s", "net_units", list(range(-250, 250))),
        ("c", "event_count", [3]*700)], "generalization")
    add("many_sheets", [(f"row-{n}", "net_units", [n, -2*n]) for n in range(90)], "generalization")
    limit = valid("exactly_8192_bytes", [("📦", "net_units", [4])], "generalization")
    cases.append(Case(limit.name, limit.category,
                      limit.payload + b' '*(8192-len(limit.payload)), limit.expected))
    rng = random.Random(602811)
    for trial in range(16):
        rows = []
        for n in range(rng.randint(1, 12)):
            stat = rng.choice(["net_units", "event_count", "largest_adjustment"])
            values = [rng.randint(-10**20, 10**20) for _ in range(rng.randint(1, 10))]
            if n % 3 == 0:
                values += values[:2]
            rows.append((f"generated {trial}/{n}", stat, values))
        add(f"generated_{trial:02d}", rows, "generalization")

    for i, value in enumerate([None, True, 4, "x", [], {}, {"other": {}},
                              {"adjustment_sheets": {}, "extra": 1}]):
        bad(f"invalid_root_{i}", value)
    for i, value in enumerate([None, False, 3, "x", [], {}]):
        bad(f"invalid_sheets_{i}", {"adjustment_sheets": value})
    bad("empty_identifier", {"adjustment_sheets": {"": {"stat": "net_units", "turns": []}}})
    bad("extra_root_property", {"adjustment_sheets": {"row": {"stat": "net_units", "turns": [1]}}, "extra": 1})
    for i, value in enumerate([None, True, 4, "x", [], {}, {"stat": "net_units"},
        {"turns": []}, {"stat": "net_units", "turns": [], "extra": 1},
        {"stat": "sum", "turns": []}, {"stat": False, "turns": []},
        {"stat": None, "turns": []}, {"stat": [], "turns": []},
        {"stat": "largest_adjustment", "turns": []}]):
        bad(f"invalid_sheet_{i}", {"adjustment_sheets": {"row": value}})
    for i, value in enumerate([None, True, 4, "x", {}]):
        bad(f"invalid_turns_{i}", {"adjustment_sheets": {"row": {"stat": "net_units", "turns": value}}})
    for stat in ("net_units", "event_count", "largest_adjustment"):
        for i, token in enumerate(['true', 'false', 'null', '"1"', '{}', '[]',
            '1.5', '-0.1', '1e-400', '1.0000000000000000000000000000000000000001',
            '9007199254740992.5', 'NaN', 'Infinity', '-Infinity']):
            # A valid row precedes the invalid one to catch incremental output.
            bad(f"invalid_item_{stat}_{i}", '{"adjustment_sheets":{'
                '"valid":{"stat":"net_units","turns":[3]},'
                '"invalid":{"stat":' + json.dumps(stat) + ',"turns":[0,' + token + ']}}}', raw=True)
    row = '{"stat":"net_units","turns":[1]}'
    for name, payload in {
        "root": '{"adjustment_sheets":{"a":'+row+'},"adjustment_sheets":{"b":'+row+'}}',
        "identifier": '{"adjustment_sheets":{"a":'+row+',"a":'+row+'}}',
        "escaped_identifier": '{"adjustment_sheets":{"a":'+row+',"\\u0061":'+row+'}}',
        "stat": '{"adjustment_sheets":{"a":{"stat":"net_units","stat":"event_count","turns":[2]}}}',
        "turns": '{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1],"turns":[2]}}}',
        "escaped_stat": '{"adjustment_sheets":{"a":{"stat":"net_units","st\\u0061t":"event_count","turns":[2]}}}',
    }.items():
        bad("duplicate_" + name, payload, raw=True, category="duplicates")
    for i, payload in enumerate([b'', b'{', b'{} {}', b'{"adjustment_sheets":}',
        b'{"adjustment_sheets":{"a":{"stat":"net_units","turns":[01]}}}',
        b'{"adjustment_sheets":{"a":{"stat":"net_units","turns":[1,]}}}',
        b'{"adjustment_sheets":{"\xff":{"stat":"net_units","turns":[]}}}']):
        bad(f"malformed_{i}", payload, raw=True)
    assert len({c.name for c in cases}) == len(cases)
    assert all(len(c.payload) <= 8192 for c in cases)
    return cases
