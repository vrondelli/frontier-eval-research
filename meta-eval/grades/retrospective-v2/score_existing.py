"""Post-hoc evidence scoring of existing deliveries. No model/code-under-test calls."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def evidence(paths):
    result = []
    for path in dict.fromkeys(paths):
        assert (ROOT / path).is_file(), path
        result.append({"path": path, "sha256": digest(path)})
    return result


# Post-outcome subweights, explicitly not a preregistered v2 run.
CHECKS = [
    ("A1", 5, "Actual delivered grader invoked through a native adapter"),
    ("A2", 5, "Delivered clean runner independently reproduced as documented"),
    ("B1", 7.5, "Reviewed source requirements preserved in the delivered task"),
    ("B2", 7.5, "Reviewed graded requirements disclosed to the actual solver"),
    ("C1", 7.5, "Delivered reference independently checked on core domain obligations"),
    ("C2", 7.5, "Delivered reference independently checked on licensed boundary cases"),
    ("D1", 10, "Baseline independently qualified correct answer accepted"),
    ("D2", 10, "Qualified correct alternative/representation accepted"),
    ("E1", 10, "All exercised qualified baseline faulty controls rejected"),
    ("E2", 10, "Separately authored sibling faulty controls rejected"),
    ("F1", 5, "Required author/eval/candidate boundaries independently qualified"),
    ("F2", 5, "Required work/evidence measurement independently checked"),
    ("G1", 2.5, "Author's delivered positive and negative controls execute"),
    ("G2", 2.5, "Author's own control claims independently validated"),
    ("H1", 2.5, "Published numeric/calibration claims recomputed from evidence"),
    ("H2", 2.5, "Material report conclusions independently supported"),
]


def main():
    results = read("RESULTS.json")
    weights = {c["id"]: c["points"] for c in read("protocol/meta-eval-v2/SCORING.json")["dimension_weights"]}
    assert len({x[0] for x in CHECKS}) == 16
    assert sum(x[1] for x in CHECKS) == 100
    for dimension, weight in weights.items():
        assert sum(w for k, w, _ in CHECKS if k.startswith(dimension)) == weight
    registry = {
        "status": "post_hoc_partial_scoring_registry",
        "weights_chosen_after_outcomes": True,
        "new_model_calls": 0,
        "scope": "Selected evidenced properties, not comprehensive v2 qualification. No new requirement imposed on historical authors.",
        "checks": [{"id": k, "points": w, "description": desc} for k, w, desc in CHECKS],
        "unknown_policy": "Unreviewed, unqualified or originally unrequested properties receive no invented pass or failure; their weight remains unresolved.",
        "scope_policy": "Passing D/E checks describes the exercised control bank only. It does not prove an entire language/domain correct.",
    }
    (HERE / "CHECK-REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n")
    rows = []
    for attempt in results["attempts"]:
        complete = attempt["effective_status"] in ("completed", "recovered_completed_turn_delivery")
        main_track = attempt["case_id"] not in ("H8", "H9")
        checks = {k: {"id": k, "points": w, "description": desc, "status": "unknown", "reason": "Not established by the imported evidence; not a subject failure.", "evidence": []} for k, w, desc in CHECKS}

        def mark(key, passed, reason, paths):
            checks[key].update(status="pass" if passed else "fail", reason=reason, evidence=evidence(paths))

        case = attempt["case_id"]
        model = attempt["model_requested"]
        cohort = attempt["cohort"]
        if complete and main_track:
            bank_path = None
            if case == "H1":
                if cohort == "initial_screen":
                    bank_path = "grades/root-review/H1-SOL-REPLAY.json"
                elif cohort == "H1_budget_diagnostic":
                    bank_path = f"grades/owner-review/H1-BUDGET-{attempt['draw']}-FULL.json"
                elif cohort == "selected_hit_clean_staging":
                    bank_path = "grades/owner-review/H1-CLEAN-FULL.json"
                elif cohort == "selected_hit_coached_staging":
                    bank_path = "grades/owner-review/H1-COACHED-FULL.json"
            elif case == "H4":
                bank_path = f"grades/owner-review/{model}-H4-SUCCESSOR.json"
            elif case == "H7":
                prefix = "sol" if model == "gpt-6.1-sol" else "astra"
                bank_path = f"grades/owner-review/{prefix}-H7-FULL-GRADE.json"

            if bank_path:
                bank = read(bank_path)
                controls = bank.get("rows", bank.get("checks", []))
                assert controls and all(c.get("valid") for c in controls), bank_path
                valid_positive = []
                valid_negative = []
                for control in controls:
                    name = control.get("control", "")
                    expected = control.get("expected_pass", "correct_" in name)
                    actual = control.get("actual_pass")
                    if actual is None:
                        assert "correct" in control
                        actual = expected if control["correct"] else not expected
                    (valid_positive if expected else valid_negative).append((name, actual))
                assert len(valid_positive) == 2 and len(valid_negative) == 3, bank_path
                mark("A1", True, "Native submitted grader was actually invoked; this is not a complete clean-runner check.", [bank_path])
                if case == "H1":
                    baseline = next(v for n, v in valid_positive if "correct_accepted" in n)
                    alternate = next(v for n, v in valid_positive if "correct_applied" in n)
                else:
                    baseline, alternate = valid_positive[0][1], valid_positive[1][1]
                extra = " Controls are post-outcome H4 corrections." if case == "H4" else ""
                if cohort == "selected_hit_coached_staging":
                    extra += " Controls are explicitly mapped to the new published accepted-only interface; original scope preservation remains unknown."
                mark("D1", baseline, "Baseline qualified correct control result." + extra, [bank_path])
                mark("D2", alternate, "Second qualified correct strategy/representation result." + extra, [bank_path])
                mark("E1", all(v is False for _, v in valid_negative), "Three independently labeled baseline faults checked." + extra, [bank_path])
                if case == "H1" and not alternate:
                    mark("B2", False, "Grader requires accepted while documented solver-only views omit it; source-license analysis is AI-reviewed with human adjudication pending.", [bank_path, "grades/semantic-review/H1-INDEPENDENT.json"] if cohort == "initial_screen" else [bank_path] + attempt["review_evidence"])
                if case == "H7":
                    sibling = f"grades/owner-review/{model}-H7-CONTIGUITY.json"
                    sibling_data = read(sibling)
                    # The source-reviewed native receipt, not the author's claimed test count.
                    assert sibling_data["package_unchanged"]
                    sibling_negatives = [c for c in sibling_data["checks"] if not c["expected_pass"]]
                    assert len(sibling_negatives) == 1 and all(c["valid"] for c in sibling_negatives)
                    mark("E2", all(c["actual_pass"] is False for c in sibling_negatives), "One separately authored post-outcome noncontiguous-quote mutant rejected per package; the second probe is a correct literal control. Literal-source scope only.", [sibling, "grades/owner-review/H7-REVIEW.md"])
                raw = {"valid_positives": len(valid_positive), "accepted_positives": sum(v for _, v in valid_positive), "valid_negatives": len(valid_negative), "rejected_negatives": sum(not v for _, v in valid_negative), "false_rejects": sum(not v for _, v in valid_positive), "false_accepts": sum(v for _, v in valid_negative)}
            else:
                raw = None

            if case == "H2":
                review_path = f"grades/semantic-review/H2-{model}.json"
                review = read(review_path)
                assert not review["actual_failure_witnesses"]
                mark("B1", True, "Original rubric-writing obligations checked in AI semantic review; no new full-package delivery requirement imposed.", [review_path])
                mark("B2", True, "Rubric criteria and mapping are explicit in the delivered criteria document; no private prior-art ranking imposed.", [review_path])
                mark("H1", True, "Worked CAL totals and score mapping recomputed and internally consistent; this is not empirical construct validity.", [review_path])
            elif case == "H3":
                mark("A1", True, "Delivered evaluation function actually invoked on the saved diagnostic probe; semantic verdict remains scoped.", [f"grades/semantic-review/H3-{model}.json"])
            elif case == "H6":
                if cohort == "initial_screen" and model == "gpt-6-astra":
                    native = "grades/root-review/H6-ASTRA-REPLAY.json"
                    bad_accepted = read(native)["observed"]["new_eval_report"]["all_passed"]
                    output_pair = "grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json"
                elif cohort == "initial_screen":
                    native = "grades/owner-review/sol-H6-ZERO-COVERAGE.json"
                    bad_accepted = read(native)["observed"]["selected_negative_zero_cli"]["success"]
                    output_pair = None
                elif cohort == "H6_same_condition_confirmation":
                    native = f"grades/owner-review/H6-CONFIRM-{attempt['draw']}.json"
                    bad_accepted = read(native)["observed"]["pass"]
                    output_pair = None
                else:
                    native = "grades/owner-review/H6-CLEAN-FULL.json"
                    bad_accepted = read(native)["observed"]["actual_saved_bad_cli_accepted"]
                    output_pair = "grades/owner-review/H6-CLEAN-OUTPUT-ZERO-PAIR.json"
                mark("A1", True, "Actual native numeric evaluator invoked; no inference from self-reported verification alone.", [native])
                mark("E1", not bad_accepted, "Actual known-bad CLI rejection checked. Rejection may detect another real defect and does not establish zero-family coverage.", [native, "grades/owner-review/H6-REVIEW.md"])
                if output_pair:
                    pair = read(output_pair)["observed"]
                    assert any(c.get("judge_passed", c.get("pass")) is True for c in pair.get("receipts", pair.get("rows", [])))
                    assert any(c.get("judge_passed", c.get("pass")) is False for c in pair.get("receipts", pair.get("rows", [])))
                    mark("D2", False, "Correct canonical-zero output passes but equivalent licensed exponent-zero output fails. This is an output-only control, not a universally correct full CLI.", [output_pair, "grades/semantic-review/H6-SOURCE-CLAUSES.md"])
                elif cohort == "initial_screen":
                    assert read(native)["observed"]["legal_zero_output_accepted"] is True
                    mark("D2", True, "Direct licensed equivalent-zero output accepted; output-only positive, not full-CLI positive qualification.", [native, "grades/semantic-review/H6-SOURCE-CLAUSES.md"])
                # Never award D1 using the two excluded original positive programs.
        else:
            raw = None

        if not main_track:
            state = "supplementary_audit_probe_not_100_point_eval_author_score"
            interval = None
        elif not complete:
            state = "incomplete_timeout" if attempt["effective_status"] == "timeout" else "capture_unknown"
            interval = None
        else:
            state = "counterexample_reproduced_human_adjudication_pending" if attempt["verified_dimensions"] else "no_full_scoped_verdict_evidence_incomplete"
            lower = sum(c["points"] for c in checks.values() if c["status"] == "pass")
            unresolved = sum(c["points"] for c in checks.values() if c["status"] == "unknown")
            interval = [lower, lower + unresolved]
        rows.append({"attempt_id": attempt["id"], "case_id": case, "model": model, "cohort": cohort, "native_status": attempt["effective_status"], "track": "eval_authoring" if main_track else "audit_supplement", "historical_outcome": attempt["semantic_outcome"], "retrospective_verdict": state, "score_interval": interval, "raw_control_classification": raw, "historical_verified_dimensions": attempt["verified_dimensions"], "checks": list(checks.values()) if main_track and complete else [], "review_evidence": evidence(attempt["review_evidence"]), "human_review_complete": False})

    assert len(rows) == len({r["attempt_id"] for r in rows}) == 31
    defects = [r for r in rows if r["historical_verified_dimensions"]]
    assert len(defects) == 8
    report = {"schema_version": "retrospective-eval-author-score/v1", "generated_utc": datetime.now(timezone.utc).isoformat(), "post_hoc": True, "preregistered": False, "model_calls": 0, "new_subject_executions": 0, "scoring_method": "Import existing qualified native receipts and explicit AI semantic reviews. Score selected properties only; unknown weights remain unresolved. Not a final v2 benchmark grade.", "source_bindings": evidence(["RESULTS.json", "owner/ADJUDICATION.json", "protocol/meta-eval-v2/SCORING.json", str((HERE / "CHECK-REGISTRY.json").relative_to(ROOT)).replace('\\', '/')]), "attempt_count": 31, "eval_authoring_attempts": sum(r["track"] == "eval_authoring" for r in rows), "supplementary_audit_attempts": 4, "completed_eval_authoring_outputs": sum(r["track"] == "eval_authoring" and r["score_interval"] is not None for r in rows), "counterexample_outputs": len(defects), "fully_qualified_passes": None, "human_review_complete": False, "no_pooled_rate": True, "counts": dict(Counter(r["retrospective_verdict"] for r in rows)), "limitations": ["Post-outcome rubric/subweights; existing instruction conditions remain separate.", "Numeric bounds indicate unresolved evidence, not capability confidence intervals or rankings.", "Passing a finite control family is not full-domain reference or grader qualification.", "Unrequested v2 deliverables do not become historical model failures.", "H2 paper-rubric and H3 hybrid-review interfaces retain their original task scope.", "H4 controls corrected post-outcome; H6 excluded positives never regain gold status.", "No additional defect-output count from duplicate failed dimensions/checks.", "The prior verified ZIP is unchanged; this is a separate retrospective addendum."], "attempts": rows}
    (HERE / "SCORES.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Retrospective scores of existing outputs", "", "**Post hoc, provisional and evidence-limited.** No new author calls or subject executions. Unknown checks do not receive invented points or penalties. These score intervals are not final v2 grades or confidence intervals. Human adjudication remains pending.", "", f"All31 attempts retained: {report['eval_authoring_attempts']} eval-authoring attempts, including {report['completed_eval_authoring_outputs']} completed outputs; four H8/H9 audit probes remain supplementary. Eight completed outputs have reproduced counterexamples. The number of fully qualified passes is not established, rather than asserted to be zero.", "", "Weights follow the proposed eight-dimension design. Each dimension has two explicitly post-outcome subchecks in CHECK-REGISTRY.json. Lower bound is earned points; upper bound adds unresolved weights. A lower bound is not a comparative model score. Missing originally unrequested features are unresolved, not failures.", "", "| Attempt | Native status | Score interval /100 | Existing control classification | Judgment |", "|---|---|---:|---|---|"]
    for row in rows:
        interval = "not scored" if row["score_interval"] is None else f"{row['score_interval'][0]:g}-{row['score_interval'][1]:g}"
        raw = row["raw_control_classification"]
        observed = "See per-check evidence" if not raw else f"Correct accepted {raw['accepted_positives']}/{raw['valid_positives']}; faults rejected {raw['rejected_negatives']}/{raw['valid_negatives']}"
        lines.append(f"| {row['attempt_id']} | {row['native_status']} | {interval} | {observed} | {row['retrospective_verdict']} |")
    lines += ["", "## What can be concluded now", "", "- The five completed H1 hidden-literal outputs and three completed H6 false-green outputs already fail a necessary reliability condition. Replaying their saved artifacts does not require fresh author generation.", "- The coached H1 output correctly classifies its mapped5/5 bank under the new published contract; whole-scope preservation remains unreviewed and receives no fabricated verdict.", "- Other checked successes remain successes within their actual scope. Missing whole-package qualification stays unknown; absence of an established defect is not a full pass.", "- Additional owner checks and human review can be performed on these same immutable deliveries to narrow the intervals. New author trials are needed for prospective replication, not to make retrospective scoring legitimate.", "", "[SCORES.json](SCORES.json) includes per-check evidence hashes and preserved historical verdicts. [CHECK-REGISTRY.json](CHECK-REGISTRY.json) states all post-hoc point assignments. Run `python score_existing.py` from any directory to regenerate this addendum; it makes no model calls.", ""]
    (HERE / "SCORES.md").write_text("\n".join(lines))
    print(json.dumps({k: report[k] for k in ["attempt_count", "eval_authoring_attempts", "completed_eval_authoring_outputs", "counterexample_outputs", "counts", "model_calls"]}))


if __name__ == "__main__":
    main()
