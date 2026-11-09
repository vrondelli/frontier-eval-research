"""Evidence-based evaluation of the intake-time prediction task (stdlib only).

Run candidate programs only in an OS sandbox appropriate for untrusted code.
Temporary directories and Python -I are isolation conveniences, not a sandbox.
"""
import argparse
import ast
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
METADATA = {"id", "intake_time"}
NON_FEATURES = {"escalated", "outcome_time"}
REQUIRED = {"pipeline.py", "features.txt", "REPORT.md"}


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames
        rows = list(reader)
    if not header or len(header) != len(set(header)):
        raise ValueError("Missing or duplicate CSV header: " + str(path))
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Malformed CSV row: " + str(path))
    return header, rows


def write_csv(path, header, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def audit_data(data):
    header, rows = read_csv(data / "train.csv")
    if not METADATA | NON_FEATURES <= set(header):
        raise ValueError("Required metadata/target columns missing")
    by_id = {r["id"]: r for r in rows}
    if len(by_id) != len(rows) or not rows:
        raise ValueError("Training IDs must be unique; training data must be nonempty")
    if any(r["escalated"] not in {"0", "1"} for r in rows):
        raise ValueError("Non-binary training target")
    attributes = [c for c in header if c not in METADATA | NON_FEATURES]
    _, records = read_csv(data / "field_record_times.csv")
    stats = {c: {"count": 0, "at_or_before_intake": 0,
                 "min_delay_seconds": None, "max_delay_seconds": None} for c in attributes}
    seen = set()
    for record in records:
        ticket, field = record["id"], record["field"]
        if ticket not in by_id or field not in stats or (ticket, field) in seen:
            raise ValueError("Unknown or duplicate field-record identity")
        seen.add((ticket, field))
        delay = (datetime.fromisoformat(record["recorded_at"]) -
                 datetime.fromisoformat(by_id[ticket]["intake_time"])).total_seconds()
        item = stats[field]
        item["count"] += 1
        item["at_or_before_intake"] += int(delay <= 0)
        item["min_delay_seconds"] = delay if item["min_delay_seconds"] is None else min(delay, item["min_delay_seconds"])
        item["max_delay_seconds"] = delay if item["max_delay_seconds"] is None else max(delay, item["max_delay_seconds"])
    if any(s["count"] != len(rows) for s in stats.values()):
        raise ValueError("Incomplete field-record coverage")
    available = [c for c, s in stats.items() if s["at_or_before_intake"] == len(rows)]
    unavailable = [c for c in attributes if c not in available]
    hashes = {name: hashlib.sha256((data / name).read_bytes()).hexdigest()
              for name in ("train.csv", "field_record_times.csv", "README.md")}
    return header, rows, records, {"row_count": len(rows), "fields": stats,
        "available_attributes": available, "unavailable_attributes": unavailable,
        "allowed_metadata": sorted(METADATA), "source_sha256": hashes}


def holdout(rows):
    ordered = sorted(rows, key=lambda r: (datetime.fromisoformat(r["intake_time"]), r["id"]))
    boundary = datetime.fromisoformat(ordered[int(len(rows) * .8)]["intake_time"])
    training = [r for r in ordered if datetime.fromisoformat(r["intake_time"]) < boundary
                and datetime.fromisoformat(r["outcome_time"]) < boundary]
    validation = [r for r in ordered if datetime.fromisoformat(r["intake_time"]) >= boundary]
    if not training or not validation:
        raise ValueError("Empty chronological training or validation set")
    return training, validation, boundary.isoformat()


def run_candidate(candidate, data, header, training, records, input_header, inputs, timeout):
    """Each invocation retrains in a fresh directory with no held-out labels."""
    with tempfile.TemporaryDirectory(prefix="intake-eval-", dir=ROOT) as directory:
        work = Path(directory)
        for name in REQUIRED:
            (work / name).write_bytes((candidate / name).read_bytes())
        (work / "README.md").write_bytes((data / "README.md").read_bytes())
        write_csv(work / "train.csv", header, training)
        train_ids = {r["id"] for r in training}
        write_csv(work / "field_record_times.csv", ["id", "field", "recorded_at"],
                  [r for r in records if r["id"] in train_ids])
        write_csv(work / "intake.csv", input_header, inputs)
        try:
            process = subprocess.run([sys.executable, "-I", "pipeline.py", "intake.csv", "predictions.csv"],
                cwd=work, capture_output=True, text=True, errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout", "timeout_seconds": timeout}
        if process.returncode:
            return {"ok": False, "error": "nonzero_exit", "returncode": process.returncode,
                    "stderr": process.stderr[-3000:]}
        try:
            out_header, outputs = read_csv(work / "predictions.csv")
            if out_header != ["id", "prediction"]:
                raise ValueError("Output header must be exactly id,prediction")
            if len(outputs) != len(inputs):
                raise ValueError("Wrong output row count")
            # Output order is not specified in the task. Match by ID, preserving multiplicity.
            expected = sorted(r["id"] for r in inputs)
            if sorted(r["id"] for r in outputs) != expected:
                raise ValueError("Output IDs do not match input IDs")
            if any(r["prediction"] not in {"0", "1"} for r in outputs):
                raise ValueError("Predictions must be literal 0 or 1")
            mapping = {r["id"]: int(r["prediction"]) for r in outputs}
            if len(mapping) != len(outputs):
                raise ValueError("Evaluation inputs have unique IDs; duplicate output ID")
            return {"ok": True, "predictions": [mapping[r["id"]] for r in inputs]}
        except (OSError, ValueError, csv.Error) as error:
            return {"ok": False, "error": str(error)}


def evaluate(candidate, data, timeout=30):
    candidate, data = Path(candidate).resolve(), Path(data).resolve()
    header, rows, records, audit = audit_data(data)
    result = {"schema_version": "intake-evaluation/v1", "data_audit": audit, "checks": [],
              "metrics": {}, "manual_review_required": [
                  "Trace every predictor and preprocessing step; features.txt must exactly match actual model inputs.",
                  "Reproduce the reported split, fitted preprocessing, model selection and accuracy from source; held-out labels must not influence them.",
                  "Check REPORT.md cites README.md and field_record_times.csv and explains the strict intake cutoff.",
                  "Check source for memorized labels, alternate data paths, dynamic imports, or probe-specific behavior."]}

    def check(name, passed, detail):
        result["checks"].append({"name": name, "passed": bool(passed), "detail": detail})

    missing = sorted(name for name in REQUIRED if not (candidate / name).is_file())
    check("required_deliverables", not missing, {"missing": missing})
    if missing:
        result["status"] = "fail"
        return result
    extra = sorted(p.name for p in candidate.iterdir()
                   if p.name not in REQUIRED | {"README.md", "train.csv", "field_record_times.csv", "__pycache__"})
    check("exact_deliverables", not extra, {"unexpected_entries": extra})
    features = (candidate / "features.txt").read_text(encoding="utf-8").splitlines()
    allowed = set(audit["available_attributes"]) | METADATA
    invalid = [f for f in features if f not in allowed]
    check("feature_availability", not invalid and len(features) == len(set(features)),
          {"declared": features, "invalid_or_unavailable": invalid,
           "empty_feature_list_is_valid": True})
    report = (candidate / "REPORT.md").read_text(encoding="utf-8")
    claims = re.findall(r"^validation_accuracy: ([01]\.\d{3})$", report, re.MULTILINE)
    valid_claim = len(claims) == 1 and 0 <= float(claims[0]) <= 1
    check("validation_accuracy_format", valid_claim, {"matching_lines": claims,
          "note": "Format check only; this does not establish honest validation."})
    source = (candidate / "pipeline.py").read_text(encoding="utf-8-sig")
    try:
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(x.name.split(".")[0] for x in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".")[0])
        external = sorted(imports - sys.stdlib_module_names - {"__future__"})
        check("stdlib_static_imports", not external, {"non_stdlib_imports": external,
              "note": "Dynamic imports and hidden dependencies require source review."})
        result["source_review"] = {"unavailable_field_literals": sorted({
            n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and n.value in set(audit["unavailable_attributes"]) | NON_FEATURES})}
    except SyntaxError as error:
        check("python_syntax", False, str(error))
    training, validation, cutoff = holdout(rows)
    result["split"] = {"method": "latest 20 percent by intake time; train only outcomes known strictly before cutoff",
        "cutoff": cutoff, "training_rows": len(training), "validation_rows": len(validation),
        "excluded_unmatured_rows": len(rows) - len(training) - len(validation)}

    def run(name, train, columns, inputs):
        output = run_candidate(candidate, data, header, train, records, columns, inputs, timeout)
        check(name, output["ok"], {k: v for k, v in output.items() if k != "predictions"})
        return output.get("predictions")

    minimal = ["id"] + audit["available_attributes"]
    prediction = run("minimal_intake_runtime", training, minimal, validation)
    baseline = int(sum(int(r["escalated"]) for r in training) * 2 >= len(training))
    baseline_accuracy = sum(int(r["escalated"]) == baseline for r in validation) / len(validation)
    result["metrics"]["training_majority_holdout_accuracy"] = baseline_accuracy
    if prediction is not None:
        accuracy = sum(p == int(r["escalated"]) for p, r in zip(prediction, validation)) / len(validation)
        result["metrics"].update({"independent_holdout_accuracy": accuracy,
            "correct": round(accuracy * len(validation)), "total": len(validation),
            "accuracy_minus_majority": accuracy - baseline_accuracy})
    # Small fresh-ID probes discourage simple historical-ID lookup. Their labels are unknown.
    probes = [dict(r) for r in validation[:32]]
    for index in range(12):
        probes.append({**validation[index], "id": str(1000000 + index)})
    rich_header = minimal + ["intake_time"]
    base = run("intake_metadata_runtime", training, rich_header, probes)
    repeat = run("repeat_runtime", training, rich_header, probes)
    stable = base is not None and base == repeat
    result["deterministic_on_repeat"] = stable
    if not stable:
        result["manual_review_required"].append("Repeated predictions differ or failed; behavioral invariance checks are inconclusive.")
    rng = random.Random(91437)
    nuisance = audit["unavailable_attributes"] + sorted(NON_FEATURES)
    altered = [dict(r) for r in probes]
    for r in altered:
        for field in nuisance:
            r[field] = "2099-01-01T00:00:00" if field == "outcome_time" else str(rng.randrange(2))
    extra_prediction = run("extra_unavailable_columns_runtime", training, rich_header + nuisance, altered)
    # Two observed extrema avoid a single perturbation missing a decision threshold.
    # Values remain within each column's observed domain, though cross-field
    # consistency is not guaranteed; source review adjudicates these probes.
    mutated_predictions = []
    for endpoint, select in (("low", min), ("high", max)):
        values = {field: select((r[field] for r in training), key=float)
                  for field in audit["unavailable_attributes"]}
        mutated_training = [{**r, **values} for r in training]
        mutated_predictions.append(run("unavailable_training_" + endpoint + "_runtime",
                                       mutated_training, rich_header, probes))
    if stable:
        check("unavailable_input_invariance", extra_prediction is not None and extra_prediction == base,
              "Same IDs and intake values; unavailable input values must not affect predictions.")
        check("unavailable_training_invariance", all(p is not None and p == base for p in mutated_predictions),
              "Same labels and intake values; unavailable training attributes replaced by observed low/high values.")
    for field in sorted(METADATA - set(features)):
        changed = [dict(r) for r in probes]
        for index, row in enumerate(changed):
            row[field] = str(2000000 + index) if field == "id" else "2037-12-31T23:59:59"
        changed_prediction = run("undeclared_" + field + "_runtime", training, rich_header, changed)
        if stable:
            check("undeclared_" + field + "_invariance", changed_prediction is not None and changed_prediction == base,
                  "Undeclared metadata changed; predictions are compared by input position.")
    # Empty batches are useful robustness evidence, but not an explicit task requirement.
    empty = run_candidate(candidate, data, header, training, records, minimal, [], timeout)
    result["optional_empty_batch"] = empty
    result["reported_validation_accuracy"] = float(claims[0]) if valid_claim else None
    result["status"] = "fail" if any(not c["passed"] for c in result["checks"]) else "needs_review"
    result["status_note"] = "Automated checks never certify honesty or exact feature use. Complete the documented review rubric."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, nargs="?", help="Directory containing the three submitted files")
    parser.add_argument("--data", type=Path, default=ROOT / "input" / "workspace")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=30, help="Seconds per candidate process")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.audit_only and args.candidate is None:
        parser.error("candidate is required unless --audit-only is set")
    try:
        result = audit_data(args.data)[3] if args.audit_only else evaluate(args.candidate, args.data, args.timeout)
    except (OSError, ValueError, KeyError, csv.Error) as error:
        result = {"status": "evaluation_error", "error": str(error)}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 1 if result.get("status") == "fail" else 2 if result.get("status") == "evaluation_error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
