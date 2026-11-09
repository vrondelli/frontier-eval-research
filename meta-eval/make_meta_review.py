"""Create an unapproved, package-bound human review form from an executed report."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError("Refusing to overwrite an existing review")
    report = json.loads(a.report.read_text())
    subjects = {}
    for row in report["subjects"]:
        if not row["checks"]:
            continue
        subjects[row["subject"]["id"]] = {
            "kind": "human", "reviewer": "", "completed": False,
            "owner_qualification_complete": False, "package_hashes": row["subject_before_sha256"],
            "decisions": {c["id"]: {"status": "unknown", "rationale": "", "evidence": []}
                          for c in row["checks"] if c["status"] == "unknown"},
            "existing_executed_findings": {c["id"]: c["status"] for c in row["checks"] if c["status"] != "unknown"},
        }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({"schema_version": "meta-eval-human-review/v1", "subjects": subjects,
                                   "instruction": "Fill only judgments actually reviewed. Bind every decision to existing evidence hashes. Do not silently override executed findings. No form authenticates identity or expertise."}, indent=2) + "\n")
    print(json.dumps({"subjects": len(subjects), "all_approvals_pending": True}))


if __name__ == "__main__":
    main()
