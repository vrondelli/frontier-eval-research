"""Independent finite source checks; no subject imports on the host."""
import json
import re
import sys


class UnsupportedMagnitude(ValueError):
    pass


class Integer:
    def __init__(self, token):
        m = re.fullmatch(r"(-?)(0|[1-9]\d*)(?:\.(\d+))?(?:[eE]([+-]?\d+))?", token)
        if not m:
            raise ValueError("Not a JSON number")
        digits = (m[2] + (m[3] or "")).lstrip("0")
        self.sign = -1 if m[1] else 1
        if not digits:
            self.sign, self.digits, self.exponent = 1, "0", 0
            return
        # Input is bounded; conversion does not expand 10**exponent.
        if hasattr(sys, "set_int_max_str_digits"):
            sys.set_int_max_str_digits(0)
        exponent = int(m[4] or "0") - len(m[3] or "")
        trimmed = len(digits) - len(digits.rstrip("0"))
        digits = digits.rstrip("0")
        exponent += trimmed
        if exponent < 0:
            raise ValueError("Nonintegral number")
        self.digits, self.exponent = digits, exponent

    def integer(self):
        if len(self.digits) + self.exponent > 20000:
            raise UnsupportedMagnitude("Finite reference probe would require >20000 output digits")
        return self.sign * int(self.digits) * 10 ** self.exponent

    def canonical(self):
        return self.sign, self.digits, self.exponent


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate object member")
        result[key] = value
    return result


def numeric_expected(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf8")
    if len(raw) > 8192:
        raise ValueError("Source input size limit")
    value = json.loads(raw.decode("utf8"), parse_int=Integer, parse_float=Integer,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)), object_pairs_hook=unique)
    sheets = value["adjustment_sheets"]
    if not isinstance(sheets, dict):
        raise ValueError("Sheets must be an object")
    answer = {}
    for key, row in sheets.items():
        values = row["turns"]
        if not isinstance(values, list) or any(not isinstance(v, Integer) for v in values):
            raise ValueError("Only integer-valued measurements")
        stat = row["stat"]
        if stat == "event_count":
            result = len(values)
        elif stat == "net_units":
            result = sum(v.integer() for v in values)
        elif stat == "largest_adjustment" and values:
            result = max(v.integer() for v in values)
        else:
            raise ValueError("Invalid stat/empty maximum")
        answer[key] = Integer(str(result)).canonical()
    return answer


def audit_numeric_cases(cases):
    rows = []
    for case in cases:
        if case.get("expected") is None:
            continue  # Invalid-schema gold is a separately reviewed component.
        family = "boundary" if re.search(r"\d[.\d]*[eE][+-]?\d", case["raw"]) else "core"
        try:
            expected = numeric_expected(case["raw"])
            actual = {k: Integer(str(v)).canonical() for k, v in case["expected"].items()}
            rows.append({"name": case["name"], "family": family, "status": "pass" if actual == expected else "fail",
                         "expected": expected, "actual": actual})
        except UnsupportedMagnitude as e:
            rows.append({"name": case["name"], "family": family, "status": "unknown", "reason": str(e)})
        except (ValueError, KeyError, TypeError) as e:
            rows.append({"name": case["name"], "family": family, "status": "fail", "reason": str(e)})
    return rows


def rubric_checks(text):
    headings = re.findall(r"^## (.+)$", text, re.M)
    required = ["Checks", "Score mapping", "Worked examples", "Failure modes"]
    ordered = [h for h in headings if h in required]
    weights = {int(m[0]): int(m[1]) for m in re.findall(r"^\d+\.\s+\*\*C(\d+).*?(\d+) point", text, re.M)}
    ranges = [tuple(map(int, m)) for m in re.findall(r"^\|\s*(\d+)\s*[-–]\s*(\d+)\s*\|\s*([0-3])\s*\|", text, re.M)]
    mapping, overlap = {}, False
    for lo, hi, score in ranges:
        if hi - lo > 1000:
            return {"format_supported": False}
        for point in range(lo, hi + 1):
            overlap |= point in mapping
            mapping[point] = score
    assigned, totals, scores = {}, None, None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("**", "") for c in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        match = re.match(r"C(\d+)", cells[0])
        if match and all("YES" in c or "NO" in c for c in cells[1:]):
            assigned[int(match[1])] = ["YES" in c for c in cells[1:]]
        if cells[0] == "Total":
            totals = [int(c) for c in cells[1:]]
        if cells[0] in ["Overall score", "Score"]:
            scores = [int(c) for c in cells[1:]]
    actual = [sum(weights.get(k, 0) * v[i] for k, v in assigned.items()) for i in range(4)]
    return {"format_supported": bool(weights) and bool(ranges) and bool(assigned),
            "ordered_required_headings": ordered == required,
            "all_worked_checks": bool(weights) and set(weights) == set(assigned),
            "mapping_exhaustive_disjoint": bool(weights) and not overlap and all(x in mapping for x in range(sum(weights.values()) + 1)),
            "worked_arithmetic": totals == actual,
            "worked_score_mapping": scores is not None and all(mapping.get(t) == s for t, s in zip(actual, scores)),
            "computed_totals": actual}
