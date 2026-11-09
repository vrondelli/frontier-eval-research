"""Reproduce receipt accounting, not the historical experiment or its graders.

Run from any directory with: python path/to/audit_round10.py
Only audit_evidence.json is written. Historical input files are never executed.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
REGRADES = INPUT / "synthesis" / "outcome-regrades"


def read(path):
    return path.read_text(encoding="utf-8")


def relative(path):
    return path.relative_to(ROOT).as_posix()


def verdict(text):
    matches = re.findall(r'^OVERALL (\w+)|"verdict": "(\w+)"', text, re.M)
    values = [a or b for a, b in matches]
    assert len(values) == 1, values
    return values[0]


def process_fields(path):
    if not path.exists():
        return None
    text = read(path)
    if text.startswith("{"):
        # Some files have a JSON prefix followed by human-readable receipts.
        return json.JSONDecoder().raw_decode(text)[0]
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def evidence_lines(path):
    pattern = re.compile(
        r"^(OVERALL|SUMMARY|HELDOUT_SUMMARY|PRISTINE_SUMMARY|COUNTED|ENDPOINT|"
        r"CLASSIFICATION|CORRECTNESS|ADVERSARIAL|CRASH_SUMMARY|FUNCTIONAL_SUMMARY|"
        r"OWN_|TRAP_EXACTLY|DIM |GROUP |FAIL |MISMATCH|WRONG|QUOTE_FAIL|PREMIUM)"
    )
    return [{"line": i, "text": line} for i, line in enumerate(read(path).splitlines(), 1)
            if pattern.search(line)]


def main():
    manifest = json.loads(read(ROOT / "MANIFEST.json"))
    mismatches = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        data = path.read_bytes() if path.is_file() else b""
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            mismatches.append(item["path"])
    actual = {relative(p) for p in INPUT.rglob("*") if p.is_file()}
    listed = {e["path"] for e in manifest["files"] if e["path"].startswith("input/")}
    rows = []
    families = defaultdict(Counter)
    for regrade in sorted(REGRADES.rglob("grade.txt")):
        rel = regrade.relative_to(REGRADES)
        original = INPUT / rel
        unit_dir = original.parent
        unit = rel.parent.as_posix()
        family = unit.split("/episodes/")[0]
        original_verdict = verdict(read(original)) if original.exists() else None
        result = verdict(read(regrade))
        logs = sorted(unit_dir.rglob("log.txt"))
        proc = unit_dir / "process.txt"
        row = {
            "unit": unit, "family": family,
            "original_grade": relative(original) if original.exists() else None,
            "regrade": relative(regrade),
            "original_verdict": original_verdict, "regrade_verdict": result,
            "verdict_agrees": original_verdict == result if original_verdict else None,
            "outcome_lines": evidence_lines(original if original.exists() else regrade),
            "process_receipt": relative(proc) if proc.exists() else None,
            "process_fields_as_recorded": process_fields(proc),
            "sessions": [],
        }
        for log in logs:
            meta = dict(line.split("=", 1) for line in read(log.with_name("log.txt.meta")).splitlines()
                        if "=" in line)
            last = log.with_name("last-message.txt")
            row["sessions"].append({
                "log": relative(log), "metadata": meta,
                "last_message": relative(last), "last_message_text": read(last),
                # This is a literal output-banner index, not a count of tool calls.
                "test_banners": [{"line": i, "text": line} for i, line in
                                 enumerate(read(log).splitlines(), 1)
                                 if re.match(r"Ran \d+ tests? in ", line)],
            })
        rows.append(row)
        families[family][result] += 1
        families[family]["units"] += 1
        families[family]["sessions"] += len(logs)
    sessions = [session for row in rows for session in row["sessions"]]
    mutations = []
    for row in rows:
        if row["family"] != "v6-common-mode":
            continue
        proc = row["process_fields_as_recorded"]
        m = proc["mutation"]
        variants = m["variants"]
        # Rejecting a known-bad implementation alone is not discriminatory evidence.
        ref_ok = variants["reference"]["passed"] and variants["reference"]["ran"] > 0
        bad_rejected = not variants["naive"]["passed"] and variants["naive"]["ran"] > 0
        mutations.append({
            "unit": row["unit"], "reported_convicting": m["convicting"],
            "reference_pass": ref_ok, "naive_rejected": bad_rejected,
            "reference_valid_naive_discrimination": ref_ok and bad_rejected,
            "model_pass": variants["model"]["passed"],
            "ran_during_agent_session_as_recorded": proc["executed_own_tests_ran_ge1"],
            "mutants_rejected_raw": m["mutants_convicted"],
            "mutants_rejected_with_reference_control": m["mutants_convicted"] if ref_ok else [],
        })
    inventory = Counter(p.name for p in INPUT.rglob("*") if p.is_file())
    report = {
        "scope": "Local audit of archived receipts; no model reruns or historical grader execution",
        "manifest_files_checked": len(manifest["files"]), "manifest_mismatches": mismatches,
        "input_files": len(actual), "unlisted_input_files": sorted(actual - listed),
        "missing_input_files": sorted(listed - actual), "file_counts": dict(inventory),
        "unique_units": len(rows), "sessions": len(sessions),
        "original_grades": sum(r["original_grade"] is not None for r in rows),
        "regrades": len(rows),
        "paired_verdict_disagreements": [r["unit"] for r in rows if r["verdict_agrees"] is False],
        "unit_outcomes": dict(Counter(r["regrade_verdict"] for r in rows)),
        "metadata_counts": {k: dict(Counter(s["metadata"].get(k, "MISSING") for s in sessions))
                            for k in ["model", "effort", "codex_version", "timeout_sec", "exit_code", "runner_exit"]},
        "started_utc_min": min(s["metadata"]["started_utc"] for s in sessions),
        "finished_utc_max": max(s["metadata"]["finished_utc"] for s in sessions),
        "families": {k: dict(v) for k, v in sorted(families.items())},
        "v6_control_audit": mutations,
        "units": rows,
    }
    assert not mismatches and actual == listed
    assert len(rows) == 147 and len(sessions) == 150
    assert sum(r["original_grade"] is not None for r in rows) == 137
    assert not report["paired_verdict_disagreements"]
    assert len({s["log"] for s in sessions}) == len(sessions)
    assert {s["log"] for s in sessions} == {relative(p) for p in INPUT.rglob("log.txt")}
    (ROOT / "audit_evidence.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ["units", "v6_control_audit"]}, indent=2))


if __name__ == "__main__":
    main()
