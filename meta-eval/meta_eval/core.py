"""Score check evidence without promoting missing evidence to success."""
import hashlib
import json
from pathlib import Path

CHECKS = [
    ("A1", 5, "Delivered grader actually executes"),
    ("A2", 5, "Delivered verification/runner executes in clean disposable state"),
    ("B1", 7.5, "Source requirements preserved"),
    ("B2", 7.5, "Graded requirements exposed to solver"),
    ("C1", 7.5, "Reference independently passes core semantics"),
    ("C2", 7.5, "Reference independently passes boundary semantics"),
    ("D1", 10, "Baseline correct control accepted"),
    ("D2", 10, "Correct alternative/representation accepted"),
    ("E1", 10, "Baseline faulty controls rejected"),
    ("E2", 10, "Fresh sibling faults rejected"),
    ("F1", 5, "Required isolation boundaries qualified"),
    ("F2", 5, "Required measurement/accounting checked independently"),
    ("G1", 2.5, "Delivered verification controls execute"),
    ("G2", 2.5, "Verification claims independently match observations"),
    ("H1", 2.5, "Numerical claims agree with evidence"),
    ("H2", 2.5, "Material conclusions supported"),
]
CRITICAL = {key for key, _, _ in CHECKS}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf8")


def inventory(path):
    path = Path(path)
    if path.is_symlink() or any(p.is_symlink() for p in path.rglob("*")):
        raise ValueError("Package symlinks are not permitted")
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def blank():
    return {k: {"id": k, "points": w, "description": d, "status": "unknown",
                "reason": "Required evidence or semantic qualification not yet established",
                "evidence": [], "method": "bound_review_required",
                "review_requirement": "Owner review must bind this exact package, public obligation and specific evidence; no unbound manual pass."} for k, w, d in CHECKS}


def set_check(checks, key, status, reason, evidence, method="executed"):
    if status not in {"pass", "fail", "unknown", "blocked_by_subject"}:
        raise ValueError("Invalid check outcome")
    if status in {"pass", "fail"} and not evidence:
        raise ValueError("Resolved check requires evidence")
    checks[key].update(status=status, reason=reason, evidence=evidence, method=method)


def set_family(checks, key, rows, reason):
    if not rows:
        return
    weight = checks[key]["points"] / len(rows)
    children = [{**row, "points": weight} for row in rows]
    statuses = {row["status"] for row in rows}
    status = "fail" if "fail" in statuses else "unknown" if statuses & {"unknown", "blocked_by_subject"} else "pass"
    set_check(checks, key, status, reason, [e for r in rows for e in r.get("evidence", [])])
    checks[key]["subchecks"] = children


def score(checks, native_status="completed", qualified=False, human_review=False):
    if set(checks) != {k for k, _, _ in CHECKS}:
        raise ValueError("Missing or duplicate scoring checks")
    for key, weight, _ in CHECKS:
        if checks[key]["points"] != weight:
            raise ValueError("Point allocation changed")
        if checks[key]["status"] in {"pass", "fail"} and not checks[key]["evidence"]:
            raise ValueError("Resolved check has no evidence")
        if checks[key]["status"] not in {"pass", "fail", "unknown", "blocked_by_subject"}:
            raise ValueError("Unknown result status")
    if native_status not in {"completed", "recovered_completed_turn_delivery"}:
        return {"score_interval": None, "verdict": "incomplete_delivery" if native_status == "timeout" else "capture_unknown",
                "critical_failures": [], "qualified": False}
    units = []
    for c in checks.values():
        children = c.get("subchecks")
        if children:
            if abs(sum(x["points"] for x in children) - c["points"]) > 1e-8:
                raise ValueError("Family subweights changed")
            if any(x["status"] not in {"pass", "fail", "unknown", "blocked_by_subject"} or x["points"] <= 0 for x in children):
                raise ValueError("Invalid family result")
            statuses = {x["status"] for x in children}
            aggregate = "fail" if "fail" in statuses else "unknown" if statuses & {"unknown", "blocked_by_subject"} else "pass"
            if c["status"] != aggregate:
                raise ValueError("Parent check hides a family outcome")
            units.extend(children)
        else:
            units.append(c)
    lower = round(sum(c["points"] for c in units if c["status"] == "pass"), 8)
    unknown = round(sum(c["points"] for c in units if c["status"] in {"unknown", "blocked_by_subject"}), 8)
    failed = [k for k, c in checks.items() if k in CRITICAL and c["status"] == "fail"]
    if failed:
        verdict = "defect_demonstrated" if human_review else "counterexample_reproduced_review_pending"
    elif all(c["status"] == "pass" for c in checks.values()) and qualified and human_review:
        verdict = "scoped_pass"
    else:
        verdict = "not_qualified"
    return {"score_interval": [lower, round(lower + unknown, 8)], "verdict": verdict,
            "critical_failures": failed, "qualified": qualified and human_review,
            "points_observed_pass": lower, "points_observed_fail": 100 - lower - unknown,
            "points_unresolved": unknown}
