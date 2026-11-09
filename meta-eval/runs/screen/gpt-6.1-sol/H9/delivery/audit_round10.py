"""Audit the supplied receipts without running historical experiment code.

Run from this directory: python audit_round10.py
Only audit-summary.json and episode-inventory.csv are generated.
Research interpretations are maintained separately in research-results.md.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
REGRADE = INPUT / "synthesis" / "outcome-regrades"


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def structured(text):
    match = re.search(r"^RESULT_JSON (.+)$", text, re.M)
    if match:
        return json.loads(match[1])
    try:
        return json.JSONDecoder().raw_decode(text.lstrip())[0]
    except ValueError:
        return {}


def verdict(text):
    match = re.search(r"^OVERALL (\w+)", text, re.M)
    return match[1] if match else structured(text).get("verdict", "MISSING")


def markers(text):
    return [line for line in text.splitlines() if re.match(
        r"(?:SUMMARY |GROUP |DIM |COUNTED|CLASSIFICATION |CRASH_SUMMARY |"
        r"CORRECTNESS |ADVERSARIAL |OWN_|TRAP_EXACTLY |ENDPOINT_|"
        r"SPEC_BREAKING|TEST_INTEGRITY|BANNED_HITS|weakened=)", line)]


def anchors(path, patterns):
    return [{"line": i, "text": line[:1000]}
            for i, line in enumerate(read(path).splitlines(), 1)
            if any(re.search(pattern, line) for pattern in patterns)]


def main():
    manifest = json.loads(read(ROOT / "MANIFEST.json"))
    entries = manifest["files"]
    failures = []
    listed = set()
    for entry in entries:
        rel = entry["path"]
        listed.add(rel)
        path = (ROOT / rel).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            failures.append({"path": rel, "problem": "missing or outside workspace"})
            continue
        data = path.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            failures.append({"path": rel, "problem": "size or SHA-256 mismatch"})
    actual = {p.relative_to(ROOT).as_posix() for p in INPUT.rglob("*") if p.is_file()}
    actual.update(name for name in ("prompt.md", "PROVENANCE.json") if (ROOT / name).is_file())
    logs = sorted(p for p in INPUT.rglob("log.txt") if "synthesis" not in p.parts)
    units = sorted({p.parent.parent if p.parent.name in ("stage1", "stage2") else p.parent for p in logs})
    rows = []
    details = []
    families = defaultdict(list)
    for unit in units:
        rel = unit.relative_to(INPUT)
        orig = unit / "grade.txt"
        regrade = REGRADE / rel / "grade.txt"
        old, new = read(orig), read(regrade)
        process_text = read(unit / "process.txt")
        process = structured(process_text)
        unit_logs = sorted(unit.rglob("log.txt"))
        meta = [dict(re.findall(r"^([a-z_]+)=(.*)$", read(p.with_name("log.txt.meta")), re.M)) for p in unit_logs]
        row = {
            "family": rel.parts[0],
            "scenario": rel.parts[1] if rel.parts[0] == "pooled-x5" else rel.parts[0],
            "unit": rel.as_posix(),
            "log_count": len(unit_logs),
            "original_verdict": verdict(old),
            "regrade_verdict": verdict(new),
            "model": ";".join(sorted({m.get("model", "MISSING") for m in meta})),
            "effort": ";".join(sorted({m.get("effort", "MISSING") for m in meta})),
            "exit_codes": ";".join(m.get("exit_code", "MISSING") for m in meta),
            "runner_exits": ";".join(m.get("runner_exit", "MISSING") for m in meta),
            "recorded_counted_failure": process.get("counted_failure", ""),
            "own_test_executions_proxy": process.get("own_test_executions", ""),
            "mutation_reference_pass": process.get("mutation", {}).get("own_tests_pass_on_reference", ""),
            "original_grade": orig.relative_to(ROOT).as_posix() if orig.exists() else "",
            "regrade": regrade.relative_to(ROOT).as_posix() if regrade.exists() else "",
        }
        rows.append(row)
        families[row["family"]].append(row)
        details.append({**row, "original_markers": markers(old), "regrade_markers": markers(new),
                        "original_structured": structured(old), "regrade_structured": structured(new),
                        "process": process or process_text})

    common = [r for r in rows if r["original_verdict"] != "MISSING"]
    differences = [r["unit"] for r in common if r["original_verdict"] != r["regrade_verdict"]]
    failed_units = [r["unit"] for r in rows if r["regrade_verdict"] == "FAIL"]
    source_anchors = {}
    for root, episodes in {
        "v1-green-suite": ["ep10-luna-main-draw10", "ep12-luna-main-draw12"],
        "v6-common-mode": ["ep02-luna-main-draw2", "ep04-luna-main-draw4"],
        "e-glob-blowup": ["ep01-luna-main-draw1"],
        "q1-table-consistency": ["ep03-luna-main-draw3"],
        "q2-abstention": ["ep01-luna-main-draw1", "ep02-luna-main-draw2", "ep03-luna-main-draw3"],
    }.items():
        for episode in episodes:
            for name in ("log.txt", "grade.txt", "process.txt", "last-message.txt"):
                path = INPUT / root / "episodes" / episode / name
                if path.exists():
                    source_anchors[path.relative_to(ROOT).as_posix()] = anchors(path, [
                        r"^/bin/bash", r"did not run", r"^SUMMARY", r"^CORRECTNESS",
                        r"^ADVERSARIAL", r"^CLASSIFICATION", r"^RESULT_JSON", r'"counted_failure"',
                        r'"own_test_executions"', r'"own_tests_pass_on_reference"',
                    ])
    summary = {
        "scope": "Supplied historical receipts only; no historical product or grader rerun",
        "manifest": {"entries": len(entries), "actual_files": len(actual), "input_files": len(actual) - 2, "failures": failures,
                     "unlisted": sorted(actual - listed), "absent": sorted(listed - actual)},
        "counts": {"families": len(families), "scenarios": len({r["scenario"] for r in rows}),
                   "logical_units": len(units), "model_sessions": len(logs),
                   "original_grades": len(common), "regrades": sum(r["regrade_verdict"] != "MISSING" for r in rows),
                   "original_verdicts": dict(Counter(r["original_verdict"] for r in rows)),
                   "regrade_verdicts": dict(Counter(r["regrade_verdict"] for r in rows)),
                   "models": dict(Counter(r["model"] for r in rows)),
                   "efforts": dict(Counter(r["effort"] for r in rows))},
        "status_disagreements": differences,
        "failed_units": failed_units,
        "family_results": {k: {"units": len(v), "original": dict(Counter(r["original_verdict"] for r in v)),
                               "regrade": dict(Counter(r["regrade_verdict"] for r in v))} for k, v in sorted(families.items())},
        "source_anchors": source_anchors,
        "units": details,
    }
    (ROOT / "audit-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (ROOT / "episode-inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"counts": summary["counts"], "manifest": summary["manifest"],
                      "status_disagreements": differences, "failed_units": failed_units}, indent=2))
    if failures or actual != listed or differences:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
