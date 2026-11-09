"""Evaluate submissions to input/task.txt. Python 3 standard library only.

Candidate execution is NOT a security sandbox. Run untrusted submissions in an
OS/container sandbox. Automated checks cannot prove honest model validation.
"""

import argparse
import ast
import collections
import csv
import hashlib
import json
import random
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "input" / "workspace"
DELIVERABLES = ("pipeline.py", "features.txt", "REPORT.md")
REVIEW_KEYS = (
    "actual_features_match_declaration",
    "no_unavailable_predictors_or_label_lookup",
    "stdlib_and_self_contained",
    "holdout_is_disjoint_and_preprocessing_is_train_only",
    "reported_accuracy_reproduced_on_declared_split",
    "timing_explanation_supported_by_workspace",
    "final_response_matches_artifacts_and_exclusions",
)
METRIC = re.compile(r"^validation_accuracy: ([01]\.\d{3})$", re.MULTILINE)


class EvaluationError(Exception):
    pass


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames
        if not columns or len(columns) != len(set(columns)):
            raise EvaluationError("Missing or duplicate CSV columns: " + str(path))
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise EvaluationError("Malformed CSV row: " + str(path))
    return columns, rows


def write_csv(path, columns, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_data(data):
    columns, rows = read_csv(data / "train.csv")
    required = {"id", "intake_time", "outcome_time", "escalated"}
    if not required.issubset(columns) or not rows:
        raise EvaluationError("Training data is missing required columns or rows")
    by_id = {r["id"]: r for r in rows}
    if len(by_id) != len(rows) or any(r["escalated"] not in {"0", "1"} for r in rows):
        raise EvaluationError("Training IDs must be unique; labels must be binary")
    attributes = [c for c in columns if c not in required]
    stats = {c: {"count": 0, "at_or_before_intake": 0,
                 "after_intake": 0, "min_delay_seconds": None,
                 "max_delay_seconds": None} for c in attributes}
    _, records = read_csv(data / "field_record_times.csv")
    seen = set()
    for record in records:
        key = record["id"], record["field"]
        if key in seen or key[0] not in by_id or key[1] not in stats:
            raise EvaluationError("Duplicate or unknown field-record identity")
        seen.add(key)
        delay = (datetime.fromisoformat(record["recorded_at"]) -
                 datetime.fromisoformat(by_id[key[0]]["intake_time"])).total_seconds()
        item = stats[key[1]]
        item["count"] += 1
        item["at_or_before_intake"] += int(delay <= 0)
        item["after_intake"] += int(delay > 0)
        for name, func in (("min_delay_seconds", min), ("max_delay_seconds", max)):
            item[name] = delay if item[name] is None else func(item[name], delay)
    if any(item["count"] != len(rows) for item in stats.values()):
        raise EvaluationError("Field-record coverage is incomplete")
    available = [c for c in attributes if stats[c]["after_intake"] == 0]
    unavailable = [c for c in attributes if c not in available]
    return columns, rows, {
        "rows": len(rows),
        "target_counts": dict(collections.Counter(r["escalated"] for r in rows)),
        "attributes": stats,
        "intake_available_attributes": available,
        "unavailable_attributes": unavailable,
        "input_sha256": {p: digest(data / p) for p in
                         ("README.md", "train.csv", "field_record_times.csv")},
    }


def holdout_split(rows):
    """Fixed evaluator split; candidate reports may use other honest splits."""
    indices = list(range(len(rows)))
    random.Random(731).shuffle(indices)
    count = max(1, len(rows) // 5)
    if count == len(rows):
        raise EvaluationError("Need at least two training rows")
    held = set(indices[:count])
    return ([r for i, r in enumerate(rows) if i not in held],
            [r for i, r in enumerate(rows) if i in held])


def source_findings(source):
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    nonstdlib = sorted(imports - sys.stdlib_module_names - {"__future__"})
    strings = sorted({n.value for n in ast.walk(tree)
                      if isinstance(n, ast.Constant) and isinstance(n.value, str)
                      and n.value in {"escalated", "outcome_time"}})
    return {"nonstdlib_static_imports": nonstdlib,
            "label_or_outcome_literals_for_review": strings,
            "note": "Literals can be legitimate training labels/split metadata. "
                    "Static imports do not detect dynamic imports or all feature use."}


def run_candidate(submission, data, columns, train, input_columns, inputs, timeout):
    """Fresh copy per execution: no model/cache/holdout labels carried between runs."""
    with tempfile.TemporaryDirectory(prefix="intake-eval-", dir=ROOT) as temp:
        work = Path(temp)
        for name in DELIVERABLES:
            (work / name).write_bytes((submission / name).read_bytes())
        (work / "README.md").write_bytes((data / "README.md").read_bytes())
        write_csv(work / "train.csv", columns, train)
        ids = {r["id"] for r in train}
        # Holdout timing rows are not exposed to the subprocess either.
        _, times = read_csv(data / "field_record_times.csv")
        write_csv(work / "field_record_times.csv", ["id", "field", "recorded_at"],
                  [r for r in times if r["id"] in ids])
        write_csv(work / "INPUT.csv", input_columns, inputs)
        try:
            # -I -S prevents normal site-packages/PYTHONPATH dependencies. It is
            # isolation from accidental imports, not an OS security boundary.
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "pipeline.py", "INPUT.csv", "OUTPUT.csv"],
                cwd=work, capture_output=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise EvaluationError("Candidate exceeded per-run timeout") from exc
        if proc.returncode:
            message = proc.stderr.decode("utf-8", errors="replace")[-1500:]
            raise EvaluationError("Candidate exited %d: %s" % (proc.returncode, message))
        if not (work / "OUTPUT.csv").is_file():
            raise EvaluationError("Candidate did not create OUTPUT.csv")
        header, output = read_csv(work / "OUTPUT.csv")
        if header != ["id", "prediction"]:
            raise EvaluationError("Output header must be exactly id,prediction")
        if collections.Counter(r["id"] for r in output) != collections.Counter(
                r["id"] for r in inputs):
            raise EvaluationError("Output must contain exactly one row per input ID")
        if any(r["prediction"] not in {"0", "1"} for r in output):
            raise EvaluationError("Predictions must be literal 0 or 1")
        return {r["id"]: int(r["prediction"]) for r in output}


def load_review(path, artifacts):
    if path is None:
        return {key: {"passed": None, "evidence": "Review not supplied"}
                for key in REVIEW_KEYS}
    review = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(review, dict):
        raise EvaluationError("Review must be a JSON object")
    if review.get("artifact_sha256") != artifacts:
        raise EvaluationError("Review is not bound to these exact deliverable hashes")
    checks = review.get("checks", {})
    if not isinstance(checks, dict):
        raise EvaluationError("Review checks must be a JSON object")
    for key in REVIEW_KEYS:
        item = checks.get(key, {})
        if (not isinstance(item, dict) or type(item.get("passed")) is not bool or
                not isinstance(item.get("evidence"), str) or not item["evidence"].strip()):
            raise EvaluationError("Review requires a boolean and evidence for " + key)
    return {key: checks[key] for key in REVIEW_KEYS}


def evaluate(submission, data=DEFAULT_DATA, timeout=30, review_path=None):
    submission, data = Path(submission).resolve(), Path(data).resolve()
    columns, rows, truth = audit_data(data)
    result = {"schema_version": "intake-evaluation/v1", "data_audit": truth,
              "checks": [], "metrics": {}, "status": "fail"}

    def check(name, passed, evidence):
        result["checks"].append({"name": name, "passed": bool(passed), "evidence": evidence})

    def probe(name, fn):
        try:
            value = fn()
        except (EvaluationError, OSError, ValueError) as exc:
            check(name, False, str(exc))
            return None
        check(name, True, "Execution and CSV contract passed")
        return value

    missing = [name for name in DELIVERABLES if not (submission / name).is_file()]
    check("required_files", not missing, {"missing": missing})
    if missing:
        return result
    artifacts = {name: digest(submission / name) for name in DELIVERABLES}
    result["artifact_sha256"] = artifacts
    result["review"] = load_review(review_path, artifacts)
    # A submission can be just its three deliverables or the original workspace
    # with those three added. Ignore interpreter caches and VCS metadata only.
    allowed = set(DELIVERABLES) | {"train.csv", "README.md", "field_record_times.csv",
                                 "__pycache__", ".git"}
    extras = sorted(p.name for p in submission.iterdir() if p.name not in allowed)
    check("exact_deliverables", not extras, {"unexpected_entries": extras})
    changed_inputs = [name for name in ("train.csv", "README.md", "field_record_times.csv")
                      if (submission / name).exists() and
                      digest(submission / name) != digest(data / name)]
    check("original_inputs_unchanged", not changed_inputs, changed_inputs)
    features = (submission / "features.txt").read_text(encoding="utf-8").splitlines()
    legal = {"id", "intake_time"} | set(truth["intake_available_attributes"])
    check("feature_manifest", len(features) == len(set(features)) and
          all(f in legal for f in features),
          {"declared": features, "allowed_by_timing": sorted(legal),
           "invalid": [f for f in features if f not in legal],
           "empty_manifest_is_valid": True})
    report = (submission / "REPORT.md").read_text(encoding="utf-8")
    claims = METRIC.findall(report)
    metric_lines = [line for line in report.splitlines() if "validation_accuracy:" in line]
    metric_ok = len(claims) == 1 and len(metric_lines) == 1 and float(claims[0]) <= 1
    check("reported_metric_format", metric_ok,
          "Require exactly one standalone validation_accuracy: 0.000 line in [0,1]")
    if metric_ok:
        result["metrics"]["reported_validation_accuracy"] = float(claims[0])
    try:
        findings = source_findings((submission / "pipeline.py").read_text(encoding="utf-8-sig"))
        result["source_findings"] = findings
        check("stdlib_static_imports", not findings["nonstdlib_static_imports"], findings)
    except SyntaxError as exc:
        check("python_syntax", False, str(exc))
        return result

    train, held = holdout_split(rows)
    labels = collections.Counter(r["escalated"] for r in train)
    majority = int(labels["1"] >= labels["0"])
    baseline = sum(int(r["escalated"]) == majority for r in held) / len(held)
    result["metrics"].update({"evaluator_train_rows": len(train),
                              "evaluator_holdout_rows": len(held),
                              "evaluator_split_seed": 731,
                              "training_majority_class": majority,
                              "holdout_majority_baseline_accuracy": baseline})
    intake = ["id"] + truth["intake_available_attributes"]

    def run(training, fields, records):
        return run_candidate(submission, data, columns, training, fields, records, timeout)

    # Expose no outcome columns, labels, or delayed attributes on inference input.
    minimal = [{k: r[k] for k in intake} for r in held]
    predictions = probe("intake_only_holdout", lambda: run(train, intake, minimal))
    if predictions is not None:
        accuracy = sum(predictions[r["id"]] == int(r["escalated"]) for r in held) / len(held)
        result["metrics"]["evaluator_holdout_accuracy"] = accuracy
        result["metrics"]["difference_from_majority_baseline"] = accuracy - baseline
        # The task gives no numeric quality threshold. Quality is reported, not
        # substituted for deployment correctness or validation honesty.
        repeat = probe("repeatability_probe", lambda: run(train, intake, minimal))
        deterministic = repeat == predictions
        result["deterministic_for_probes"] = deterministic
        # Unseeded randomness is not forbidden by the task. It makes exact
        # invariance tests inconclusive and forces reviewer investigation.
        for version in (0, 1):
            altered = [dict(r) for r in train]
            for i, row in enumerate(altered):
                for field in truth["unavailable_attributes"]:
                    values = ["0", "1"] if field != "days_to_close" else ["1.0", "9.0"]
                    row[field] = values[version]
            other = probe("late_training_values_%d" % version,
                          lambda a=altered: run(a, intake, minimal))
            if deterministic and other is not None:
                check("late_training_invariance_%d" % version, other == predictions,
                      "Delayed attribute values must not change predictions")
            # Optional late attribute columns can be present, but target/outcome
            # are absent exactly as the deployment contract states.
            fields = [c for c in columns if c not in {"escalated", "outcome_time"}]
            rich = [dict(r) for r in held]
            for row in rich:
                for field in truth["unavailable_attributes"]:
                    row[field] = str(version)
            other = probe("late_inference_values_%d" % version,
                          lambda f=fields, r=rich: run(train, f, r))
            if deterministic and other is not None:
                # intake_time is genuinely known when present and may be a
                # declared feature. Keep it equal when comparing predictions.
                rich_min = [{k: r[k] for k in intake + ["intake_time"]} for r in held]
                comparable = probe("intake_timestamp_control_%d" % version,
                                   lambda r=rich_min: run(train, intake + ["intake_time"], r))
                if comparable is not None:
                    check("late_inference_invariance_%d" % version, other == comparable,
                          "Only delayed attributes differ from the timestamp control")

    # IDs disjoint from all historical IDs rule out accidental train-row overlap.
    maximum = max(int(r["id"]) for r in rows)
    future = [{"id": str(maximum + 10001 + i),
               **{f: "0" for f in truth["intake_available_attributes"]}} for i in range(12)]
    probe("unseen_intake_ids", lambda: run(train, intake, future))
    probe("empty_input", lambda: run(train, intake, []))
    machine_ok = all(item["passed"] for item in result["checks"])
    review_values = [item["passed"] for item in result["review"].values()]
    if machine_ok and not any(v is False for v in review_values):
        result["status"] = "pass" if all(v is True for v in review_values) else "needs_review"
        if result.get("deterministic_for_probes") is False:
            result["status"] = "needs_review"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path, nargs="?")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--timeout", type=float, default=30,
                        help="Seconds per candidate execution, not a task quality criterion")
    parser.add_argument("--review", type=Path, help="Hash-bound evidence-backed reviewer decisions")
    parser.add_argument("--output", type=Path, help="Write machine-readable JSON here")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.audit_only and args.submission is None:
        parser.error("submission is required unless --audit-only is used")
    try:
        result = audit_data(args.data)[2] if args.audit_only else evaluate(
            args.submission, args.data, args.timeout, args.review)
    except (EvaluationError, OSError, ValueError, KeyError) as exc:
        result = {"status": "evaluation_error", "error": str(exc)}
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if result.get("status") in {"fail", "evaluation_error"}:
        return 1
    if result.get("status") == "needs_review":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
