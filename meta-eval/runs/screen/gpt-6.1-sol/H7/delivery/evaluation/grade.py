"""Deterministic, source-position-aware grader for the frozen H7 extraction case."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "input"
MAX_CANDIDATE_BYTES = 1_048_576


class EvaluationError(ValueError):
    """An evaluation configuration or source-integrity error."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-JSON numeric constant: {value}")


def parse_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)


def occurrences(text: str, span: str) -> list[tuple[int, int]]:
    """Return all exact occurrences, including overlaps. Empty spans are not evidence."""
    if not span:
        return []
    found = []
    start = 0
    while (start := text.find(span, start)) != -1:
        found.append((start, start + len(span)))
        start += 1
    return found


def load_case(input_dir: Path = DEFAULT_INPUT) -> tuple[dict[str, Any], str, dict[str, list[tuple[int, int]]]]:
    spec = parse_json((HERE / "spec.json").read_text(encoding="utf-8"))
    for relative, expected in spec["input_sha256"].items():
        path = input_dir / relative
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise EvaluationError(f"Cannot read frozen input {relative}: {exc}") from exc
        if actual != expected:
            raise EvaluationError(f"Input integrity mismatch: {relative}; this grader is for frozen H7 only")
    # read_bytes preserves the original CR/LF characters for exact-span checks.
    report = (input_dir / "workspace" / "report.txt").read_bytes().decode("utf-8")
    request = parse_json((input_dir / "workspace" / "request.json").read_text(encoding="utf-8"))
    if set(request["fields"]) != set(spec["fields"]):
        raise EvaluationError("Requested fields do not match evaluation specification")
    anchors: dict[str, list[tuple[int, int]]] = {}
    for field, rule in spec["fields"].items():
        anchors[field] = []
        for support in rule["supports"]:
            context = spec["contexts"][support["context"]]
            context_positions = occurrences(report, context)
            span_positions = occurrences(context, support["span"])
            if len(context_positions) != 1 or len(span_positions) != 1:
                raise EvaluationError(f"Ambiguous or absent annotation for {field}: {support}")
            base = context_positions[0][0]
            start, end = span_positions[0]
            anchors[field].append((base + start, base + end))
    return spec, report, anchors


def normalize(candidate: Any, expected: set[str]) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if isinstance(candidate, dict) and "fields" in candidate:
        candidate = candidate["fields"]
    rows: dict[str, Any] = {}
    if isinstance(candidate, dict):
        rows = candidate
    elif isinstance(candidate, list):
        for index, row in enumerate(candidate):
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                errors.append(f"Row {index} must be an object with a string id")
                continue
            field = row["id"]
            if field in rows:
                errors.append(f"Duplicate field id: {field}")
                continue
            rows[field] = row
    else:
        errors.append("Fields must be an object keyed by field name or a list of {id,value,quote} rows")
    for field in sorted(expected - set(rows)):
        errors.append(f"Missing requested field: {field}")
    for field in sorted(set(rows) - expected):
        warnings.append(f"Unrequested field ignored: {field}")
    for field in sorted(expected & set(rows)):
        row = rows[field]
        if not isinstance(row, dict):
            errors.append(f"{field}: expected an object containing value and quote")
        elif not isinstance(row.get("value"), str) or not isinstance(row.get("quote"), str):
            errors.append(f"{field}: value and quote must both be strings")
    return rows, errors, warnings


def failed_document(reason: str) -> dict[str, Any]:
    return {
        "case_id": "H7", "passed": False, "score": 0.0,
        "checks_passed": 0, "checks_total": 16, "schema_valid": False,
        "errors": [reason], "warnings": [], "fields": {},
        "manual_review_required": True,
        "scope": "Artifact correctness only; process and brief limitations explanation require review.",
    }


def grade(candidate: Any, *, input_dir: Path = DEFAULT_INPUT) -> dict[str, Any]:
    spec, report, anchors = load_case(input_dir)
    rows, errors, warnings = normalize(candidate, set(spec["fields"]))
    results = {}
    passed_checks = 0
    for field, rule in spec["fields"].items():
        row = rows.get(field)
        value = row.get("value") if isinstance(row, dict) else None
        quote = row.get("quote") if isinstance(row, dict) else None
        value_ok = isinstance(value, str) and value == rule["value"]
        locations = occurrences(report, quote) if isinstance(quote, str) else []
        exact = isinstance(quote, str) and (quote == "" or bool(locations))
        if rule["value"] == "unspecified":
            evidence_ok = value_ok and quote == ""
            reason = "Absent fields require value 'unspecified' and exactly an empty quote."
        else:
            supported = any(
                q_start <= a_start and a_end <= q_end
                for q_start, q_end in locations
                for a_start, a_end in anchors[field]
            )
            evidence_ok = value_ok and supported
            reason = (
                "Quote must be one exact contiguous report span covering affirmative evidence "
                "for this field and the requested target; numbers must include units, and "
                "the metric must include activity and percentile."
            )
        passed_checks += int(value_ok) + int(evidence_ok)
        issues = []
        if not value_ok:
            issues.append(f"Expected normalized string value {rule['value']!r}.")
        if not evidence_ok:
            issues.append(reason)
        results[field] = {
            "value_correct": value_ok,
            "quote_exact": exact,
            "quote_supports_assigned_value": evidence_ok,
            "passed": value_ok and evidence_ok,
            "issues": issues,
        }
    total = 2 * len(spec["fields"])
    # An ambiguous/invalid document cannot earn a perfect artifact score.
    score = passed_checks / total if not errors else 0.0
    return {
        "case_id": spec["case_id"],
        "passed": not errors and passed_checks == total,
        "score": score,
        "checks_passed": passed_checks,
        "checks_total": total,
        "schema_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "fields": results,
        "manual_review_required": True,
        "scope": "Artifact correctness only; process and brief limitations explanation require review.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Path to the solver's extraction.json")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT, help="Frozen input directory (default: ../input)")
    parser.add_argument("--output", type=Path, help="Also save the grading result as JSON")
    args = parser.parse_args(argv)
    try:
        # Always check the benchmark, even if the candidate is invalid.
        load_case(args.input_dir)
        try:
            if args.candidate.stat().st_size > MAX_CANDIDATE_BYTES:
                raise ValueError("Candidate exceeds the 1 MiB evaluation resource limit")
            candidate = parse_json(args.candidate.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError, RecursionError) as exc:
            result = failed_document(f"Cannot read candidate JSON: {exc}")
        else:
            result = grade(candidate, input_dir=args.input_dir)
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return 0 if result["passed"] else 1
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({"evaluation_error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
