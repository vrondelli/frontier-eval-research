"""Deterministic, source-position-aware evaluator for the supplied H7 report."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "input" / "workspace"
EXPECTED = {
    "path": "Amber",
    "load_profile": "Q1",
    "metric": "seal_inspection_p90",
    "value_ms": "18.2",
    "sample_count": "4900",
    "time_scope": "14:05-UTC",
    "rejection_rate": "unspecified",
    "deployment_region": "unspecified",
}
HASHES = {
    "report.txt": "a75d7ddeb6a73fdcead53b2283294788f5beace8f71a41083465c54aa0faf3c5",
    "request.json": "3fe6a149bad68d94f4bb014bc40d71b2111a6b2195bca55c75270840692863d3",
    "README.md": "57c25c3af4ecb9e3a838051a99ee74a7432cd12580ad2f2dd27598fbbaeb56e6",
}


def load_source():
    for name, expected in HASHES.items():
        if hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Evaluation source changed: {name}; review annotations before grading")
    # Text-mode newline normalization makes Windows and Unix submissions equivalent.
    return (SOURCE / "report.txt").read_text(encoding="utf-8")


def occurrences(text, needle):
    start = 0
    while needle:
        found = text.find(needle, start)
        if found < 0:
            break
        yield found, found + len(needle)
        start = found + 1


def support_spans(report):
    """Annotate affirmative facts at their actual offsets, never global keywords.

    Equal-looking numbers in the average/negation and Silver sentences are not
    annotations for Amber latency. Longer quotes must contain a valid annotation.
    """
    lines = report.splitlines()
    spans = {field: [] for field in EXPECTED}

    def add(field, line_number, phrase):
        sentence = lines[line_number]
        assert sentence.count(phrase) == 1, (field, phrase)
        base = report.index(sentence)
        start = base + sentence.index(phrase)
        spans[field].append((start, start + len(phrase)))

    # Direct labels are expressly permitted by the task.
    spans["path"] = list(occurrences(report, "Amber"))
    spans["load_profile"] = list(occurrences(report, "Q1"))
    add("time_scope", 0, "14:05 UTC")
    add("sample_count", 0, "4,900 requests")
    add("metric", 1, "90th-percentile seal-inspection completion time")
    add("metric", 2, "slowest tenth of Amber seal inspections began at")
    add("value_ms", 1, "18.2 milliseconds")
    add("value_ms", 2, "18.2 milliseconds")
    return spans


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)


def normalize(candidate):
    # Accept both common interpretations of 'with fields as an object ... or a list'.
    if isinstance(candidate, dict) and "fields" in candidate:
        if set(candidate) != {"fields"}:
            raise ValueError("The fields wrapper must contain only fields")
        candidate = candidate["fields"]
    if isinstance(candidate, list):
        rows = {}
        for row in candidate:
            if not isinstance(row, dict) or set(row) != {"id", "value", "quote"}:
                raise ValueError("Each list row must contain exactly id, value, quote")
            field = row["id"]
            if not isinstance(field, str) or field in rows:
                raise ValueError("List IDs must be unique strings")
            rows[field] = {"value": row["value"], "quote": row["quote"]}
        candidate = rows
    if not isinstance(candidate, dict):
        raise ValueError("Expected a field object or row list")
    return candidate


def grade(candidate, report=None):
    if report is None:
        report = load_source()
    spans = support_spans(report)
    try:
        rows = normalize(candidate)
    except ValueError as exc:
        return {"passed": False, "score": 0.0, "errors": [str(exc)], "fields": {}}
    errors = []
    missing = sorted(set(EXPECTED) - set(rows))
    extra = sorted(set(rows) - set(EXPECTED))
    if missing:
        errors.append(f"Missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"Unexpected fields: {', '.join(extra)}")
    checks = {}
    for field, expected in EXPECTED.items():
        row = rows.get(field)
        reasons = []
        valid = (isinstance(row, dict) and set(row) == {"value", "quote"}
                 and isinstance(row.get("value"), str) and isinstance(row.get("quote"), str))
        if not valid:
            checks[field] = {"value_correct": False, "quote_supported": False,
                             "reasons": ["Requires exactly string value and string quote"]}
            continue
        value_ok = row["value"] == expected
        if not value_ok:
            reasons.append(f"Expected normalized value {expected!r}")
        quote = row["quote"].replace("\r\n", "\n")
        if expected == "unspecified":
            quote_ok = quote == ""
            if not quote_ok:
                reasons.append("Absent fields require the empty quote")
        else:
            matches = list(occurrences(report, quote))
            quote_ok = any(start <= a and b <= end
                           for start, end in matches for a, b in spans[field])
            if not matches:
                reasons.append("Quote must be a nonempty exact contiguous report span")
            elif not quote_ok:
                reasons.append("Quote lacks affirmative support for this target field (including required units/activity/percentile)")
        # Credit evidence only when it supports the value actually assigned.
        checks[field] = {"value_correct": value_ok,
                         "quote_supported": value_ok and quote_ok, "reasons": reasons}
    points = sum(int(c["value_correct"]) + int(c["quote_supported"]) for c in checks.values())
    return {"passed": not errors and points == 16, "score": points / 16,
            "points": points, "possible_points": 16, "errors": errors, "fields": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Path to the submitted extraction.json")
    args = parser.parse_args()
    try:
        report = load_source()
    except (OSError, ValueError) as exc:
        print(json.dumps({"evaluation_error": str(exc)}))
        return 2
    try:
        candidate = read_json(args.candidate)
        result = grade(candidate, report)
    except (OSError, ValueError) as exc:
        result = {"passed": False, "score": 0.0, "errors": [str(exc)], "fields": {}}
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
