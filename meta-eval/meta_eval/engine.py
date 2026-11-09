"""Execute, inspect and score complete eval packages; preserve unresolved evidence."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import time

from .core import blank, dump, inventory, score, set_check, set_family, sha
from .existing import build, read
from .oracles import audit_numeric_cases, rubric_checks
from .runtime import decode, doctor, execute_isolated, verdict


def ensure_controls(root):
    path = root / "meta_eval/controls/H1/wrong_B_reply_v2.json"
    original = read(root, "owner/cases/H1/correct_accepted.json")["code"]
    if "class Service:" not in original:
        raise ValueError("Inspect owner baseline class before building sibling")
    code = original.replace("class Service:", "class OriginalService:", 1) + """

class Service(OriginalService):
    def apply(self, request):
        result = super().apply(request)
        if request['account'] == 'B' and result.get('status') == 'accepted':
            result = dict(result, remaining=1)
        return result
"""
    value = {"case_id": "H1", "kind": "sqlite_service", "code": code}
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError("Existing sibling control changed; version it rather than overwrite")
    else:
        dump(path, value)


def evidence(path, root):
    path = Path(path)
    try:
        display = path.relative_to(root).as_posix()
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha(path)}


def execute_subject(root, subject, outdir, capabilities, cache=False):
    package = root / subject["package"]
    if outdir.resolve().is_relative_to(package.resolve()):
        raise ValueError("Output must stay outside immutable submitted package")
    outdir.mkdir(parents=True, exist_ok=True)
    before = inventory(package)
    checks = blank()
    observations, receipts, problems = [], [], []
    for index, job in enumerate(subject["jobs"]):
        path = outdir / f"{index:02d}-{job['name']}.json"
        backend = job["command"][0]
        available = capabilities.get("docker" if backend == "docker" else "bubblewrap", False)
        if not available:
            receipt = {"status": "unavailable", "reason": f"{backend} backend not qualified", "command": job["command"], "decoded": None}
        else:
            receipt = execute_isolated(job["command"], root, job.get("timeout", 150))
        receipt.update(job_id=job["name"], kind=job["kind"], expected=job.get("expected"), family=job.get("family"))
        dump(path, receipt)
        ev = evidence(path, root)
        receipts.append(ev)
        decoded = receipt.get("decoded")
        if receipt.get("status") != "completed" or receipt.get("exit_code") != 0 or decoded is None:
            problems.append({"job": job["name"], "kind": "native_check_unavailable_or_invalid", "evidence": ev})
        if job["kind"] == "control":
            actual = verdict(decoded)
            valid = receipt.get("status") == "completed" and receipt.get("exit_code") == 0 and type(actual) is bool
            observations.append({"name": job["name"], "expected": job["expected"], "actual": actual,
                                 "valid": valid, "family": job["family"], "evidence": ev})
            if not valid:
                problems.append({"job": job["name"], "kind": "invalid_native_verdict", "evidence": ev})
        elif job["kind"] == "output_pair" and isinstance(decoded, dict):
            rows = decoded.get("rows", [])
            if len(rows) == 2 and all(type(row.get("accepted")) is bool for row in rows):
                set_check(checks, "D2", "pass" if all(row["accepted"] for row in rows) else "fail",
                          "Actual native judge on two source-licensed spellings of exact zero; output-only scope.", [ev])
        elif job["kind"] == "numeric_reference" and isinstance(decoded, dict) and "cases" in decoded:
            comparison = audit_numeric_cases(decoded["cases"])
            auditpath = outdir / "independent-numeric-reference.json"
            dump(auditpath, {"oracle": "independent lexical integer normalization plus Python integer arithmetic", "rows": comparison,
                             "scope": "Valid supplied cases; infeasible nonzero output magnitudes stay unknown. No invalid-input gold inferred."})
            for key, family in [("C1", "core"), ("C2", "boundary")]:
                selected = [r for r in comparison if r.get("family") == family]
                if selected:
                    set_family(checks, key, [{"name": r["name"], "status": r["status"], "evidence": [evidence(auditpath, root)]} for r in selected], f"Independent oracle compared {len(selected)} supplied {family} reference answers; finite scope only.")
        elif job["kind"] in {"reference_core", "reference_boundary"} and isinstance(decoded, dict) and type(decoded.get("ok")) is bool:
            key = "C1" if job["kind"] == "reference_core" else "C2"
            set_check(checks, key, "pass" if decoded["ok"] else "fail", "Delivered reference tested by independent owner Service/SQLite core or three-process-overlap checker.", [ev])
        elif job["kind"] == "hybrid" and isinstance(decoded, dict) and isinstance(decoded.get("report"), dict):
            if decoded["report"].get("status") in {"pass", "fail", "needs_review"}:
                set_check(checks, "A1", "pass", "Actual hybrid evaluator executed; needs_review is not a complete semantic pass.", [ev])
        elif job["kind"] == "selftests" and isinstance(decoded, dict):
            text = decoded.get("stdout", "") + decoded.get("stderr", "")
            ran = re.search(r"Ran (\d+) tests?", text)
            if "Failed to import test module" in text:
                ran = None
            events = decoded.get("observed_execution_events") or {}
            observed_tests = events.get("unittest_cases_entered", 0)
            observed_grades = events.get("native_grader_calls", 0)
            if observed_tests > 0 or observed_grades > 0:
                set_check(checks, "G1", "pass", f"Observed {observed_tests} actual unittest-case entries and {observed_grades} native grading calls under an owner-side profiler. Control-label correctness is a separate review.", [ev])
                if decoded.get("native_exit") == 0:
                    set_check(checks, "A2", "pass", "Delivered verification suite reproduced in clean temporary copy under the supplied runtime; this does not establish all CLI paths.", [ev])
                    claims = []
                    for f in package.rglob("*"):
                        if f.is_file() and f.suffix in {".md", ".txt", ".log"} and "input" not in f.parts and f.stat().st_size < 200000:
                            t = f.read_text(encoding="utf8", errors="replace")
                            for match in re.finditer(r"Ran (\d+) tests?", t):
                                if observed_tests > 0 and int(match.group(1)) == observed_tests:
                                    claims.append(evidence(f, root))
                    if claims:
                        set_check(checks, "H1", "pass", "Stored authored unittest-count claim matches actual observed TestCase entries and successful native suite. This checks a numerical verification claim, not control-label correctness.", [ev] + claims, "executed_plus_artifact_inspection")
                else:
                    problems.append({"job": job["name"], "kind": "delivered_selftests_failed", "evidence": ev})

    valid = [o for o in observations if o["valid"]]
    if valid:
        set_check(checks, "A1", "pass", "Actual delivered grading functions executed on independently supplied controls.", [o["evidence"] for o in valid])
    positives = [o for o in valid if o["expected"] and o["family"] == "baseline"]
    negatives = [o for o in observations if o["expected"] is False and o["family"] == "baseline"]
    siblings = [o for o in observations if o["expected"] is False and o["family"] == "sibling"]
    if positives:
        baseline = next((o for o in positives if "accepted" in o["name"]), positives[0])
        set_check(checks, "D1", "pass" if baseline["actual"] else "fail", "Independent baseline correct control under the recorded public interface.", [baseline["evidence"]])
        alternatives = [o for o in positives if o is not baseline]
        if alternatives:
            set_check(checks, "D2", "pass" if all(o["actual"] for o in alternatives) else "fail", "Independent correct alternatives/representations under the recorded public interface.", [o["evidence"] for o in alternatives])
    for key, group in [("E1", negatives), ("E2", siblings)]:
        if group and all(o["valid"] for o in group):
            set_family(checks, key, [{"name": o["name"], "status": "pass" if not o["actual"] else "fail", "evidence": [o["evidence"]]} for o in group], "Actual native verdicts on independently labeled finite faulty-control family; controls macro-averaged within family.")

    # Artifact checks are independent of the generated evaluator's claims.
    if subject["case_id"] == "H2":
        path = package / "criteria.md"
        data = rubric_checks(path.read_text(encoding="utf8"))
        artifact = outdir / "rubric-arithmetic.json"
        dump(artifact, data)
        ev = evidence(artifact, root)
        if data.get("format_supported"):
            set_check(checks, "B1", "pass" if data["ordered_required_headings"] and data["all_worked_checks"] and data["mapping_exhaustive_disjoint"] else "fail", "Original explicit rubric mechanics only; qualitative construct validity remains unresolved.", [ev], "artifact_inspection")
            set_check(checks, "H1", "pass" if data["worked_arithmetic"] and data["worked_score_mapping"] else "fail", "Recomputed all worked totals and score mapping from the delivered document.", [ev], "artifact_inspection")
    if subject["case_id"] == "H7" and subject.get("reference"):
        reference = read(root, f"{subject['package']}/{subject['reference']}")
        reference = reference.get("fields", reference) if isinstance(reference, dict) else reference
        control = read(root, "owner/cases/H7/correct_flat.json")
        spec = importlib.util.spec_from_file_location("trusted_owner_checks", root / "owner/check_cases.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        control["extraction"] = reference
        try:
            good, rows = module.check_h7(control)
            artifact = outdir / "independent-extraction-reference.json"
            dump(artifact, {"pass": good, "rows": rows})
            set_check(checks, "C1", "pass" if good else "fail", "Delivered reference JSON independently checked against source field/quote semantics.", [evidence(artifact, root)], "artifact_inspection")
            quotes = reference.values() if isinstance(reference, dict) else reference
            literal = all(not item.get("quote") or item["quote"] in control["report"] for item in quotes)
            set_check(checks, "C2", "pass" if literal else "fail", "Every nonempty reference quote is an actual contiguous source substring.", [evidence(artifact, root)], "artifact_inspection")
        except (KeyError, TypeError, ValueError) as e:
            problems.append({"kind": "reference_interface_requires_review", "reason": str(e)})
    if subject["case_id"] == "H1" and checks["D2"]["status"] == "fail":
        # Public licensing is retained as a source-bound semantic annotation, never inferred from a preferred word alone.
        source = root / "owner/contracts/H1.md"
        set_check(checks, "B2", "fail", "Reproduced correct-alternative rejection; source-bound review identifies accepted-only rule omitted from documented solver views. Human adjudication pending.", checks["D2"]["evidence"] + [evidence(source, root)], "executed_plus_source_review")

    after = inventory(package)
    if before != after:
        raise RuntimeError("Subject delivery changed during scoring")
    if subject["case_id"] == "H1" and checks["D1"]["status"] == "pass" and checks["D2"]["status"] == "pass" and subject["cohort"] == "selected_hit_coached_staging":
        checks["B1"]["reason"] = "Published status contract fixed target mismatch, but final-answer-only scope change still needs human adjudication."
    human, qualified = False, False
    if subject.get("bound_review"):
        review = subject["bound_review"]
        if review.get("package_hashes") != before or not review.get("reviewer") or review.get("kind") != "human":
            raise ValueError("Human review does not bind this exact package")
        for key, decision in review.get("decisions", {}).items():
            if key not in checks or not decision.get("rationale") or not decision.get("evidence"):
                raise ValueError("Review decision missing licensed rationale/evidence")
            if checks[key]["status"] != "unknown" and checks[key]["status"] != decision["status"]:
                raise ValueError("Review conflicts with executed result; explicit instrument adjudication required")
            for entry in decision["evidence"]:
                bound = Path(entry["path"])
                bound = bound if bound.is_absolute() else root / bound
                if not bound.is_file() or sha(bound) != entry["sha256"]:
                    raise ValueError("Human review evidence is missing or changed")
            set_check(checks, key, decision["status"], decision["rationale"], decision["evidence"], "human_declared_bound_review")
        human = review.get("completed") is True
        qualified = review.get("owner_qualification_complete") is True
    summary = score(checks, subject["native_status"], qualified=qualified, human_review=human)
    result = {"subject": subject, "scoring": summary, "checks": list(checks.values()), "native_control_results": observations,
              "execution_receipts": receipts, "instrument_observations": problems, "subject_unchanged": True,
              "subject_before_sha256": before, "human_review_complete": human,
              "scope": "Executable meta-evaluation on the finite registered checks; unqualified semantic/boundary claims remain unresolved."}
    dump(outdir / "score.json", result)
    return result


def run_existing(root, output, jobs=2, tasks=None, ids=None, image="python:3.14-slim", reviews=None):
    started = time.monotonic()
    ensure_controls(root)
    capabilities = doctor(root, image)
    output.mkdir(parents=True, exist_ok=True)
    dump(output / "environment.json", capabilities)
    attempts = read(root, "RESULTS.json")["attempts"]
    selected = [a for a in attempts if (not tasks or a["case_id"] in tasks) and (not ids or a["id"] in ids)]
    subjects = [build(root, a, image) for a in selected]
    if not selected:
        raise ValueError("No matching existing subject IDs/tasks")
    for subject in subjects:
        if output.resolve().is_relative_to((root / subject["package"]).resolve()):
            raise ValueError("Output cannot be inside any selected immutable package")
    if reviews:
        review_data = json.loads(Path(reviews).read_text(encoding="utf8"))
        for subject in subjects:
            if subject["id"] in review_data.get("subjects", {}):
                subject["bound_review"] = review_data["subjects"][subject["id"]]
    runner_before = inventory(root / "meta_eval")
    dump(output / "subjects.json", subjects)
    result_rows = []
    to_execute = []
    for subject in subjects:
        if subject.get("supplementary") or subject["native_status"] != "completed":
            result_rows.append({"subject": subject, "scoring": {"verdict": "supplementary_audit_probe" if subject.get("supplementary") else "incomplete_delivery" if subject["native_status"] == "timeout" else "capture_unknown", "score_interval": None}, "checks": [], "execution_receipts": []})
        else:
            to_execute.append(subject)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(execute_subject, root, subject, output / subject["id"], capabilities): subject for subject in to_execute}
        for future in as_completed(futures):
            subject = futures[future]
            try:
                row = future.result()
            except Exception as e:
                row = {"subject": subject, "scoring": {"verdict": "instrument_error", "score_interval": None}, "error": repr(e), "checks": [], "execution_receipts": []}
                dump(output / subject["id"] / "instrument-error.json", row)
            result_rows.append(row)
            print(json.dumps({"subject": subject["id"], "verdict": row["scoring"]["verdict"], "score_interval": row["scoring"].get("score_interval")}), flush=True)
    order = {a["id"]: i for i, a in enumerate(selected)}
    result_rows.sort(key=lambda r: order[r["subject"]["id"]])
    assert len(result_rows) == len(selected) == len({r["subject"]["id"] for r in result_rows})
    report = {"schema_version": "executed-eval-author-meta-eval/v2", "created_utc": datetime.now(timezone.utc).isoformat(),
              "elapsed_seconds": time.monotonic() - started, "model_calls": 0, "post_hoc": True,
              "attempts_requested": len(selected), "attempts_reported": len(result_rows),
              "fresh_native_execution_count": sum(len(r["execution_receipts"]) for r in result_rows),
              "score_policy": "Eight dimensions, fixed100points, evidence-linked unknown intervals. All semantic/full-boundary reviews must resolve before scoped_pass.",
              "human_review_complete": False, "subjects": result_rows,
              "runner_before_sha256": runner_before, "runner_unchanged_during_run": runner_before == inventory(root / "meta_eval")}
    dump(output / "REPORT.json", report)
    lines = ["# Executed meta-evaluation", "", "Actual native executions of saved GPT-created evals, not imported historical verdicts. Post-hoc scoring; zero model calls. Unknown checks remain unresolved. Human task/grading review is pending.", "", "| Subject | Native status | Score interval /100 | Verdict |", "|---|---|---:|---|"]
    for row in result_rows:
        s = row["scoring"]
        interval = s.get("score_interval")
        text = "not scored" if interval is None else f"{interval[0]:g}-{interval[1]:g}"
        lines.append(f"| {row['subject']['id']} | {row['subject']['native_status']} | {text} | {s['verdict']} |")
    lines += ["", f"Fresh native jobs: {report['fresh_native_execution_count']}. Every job's command/stdout/stderr and hash-bound evidence is retained beside its subject score. Replay executions are not new author attempts.", "", "Missing or unqualified checks are visible per subject. The scorer and runner are implemented; this does not certify full-domain oracle correctness, historical exposure isolation or pending human semantics.", ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf8")
    return report
