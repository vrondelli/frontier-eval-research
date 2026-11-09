"""Independently validate executed-report accounting and evidence identities."""
import argparse
import hashlib
import json
from pathlib import Path


def validate(report_path, root, all_existing=False):
    d = json.loads(report_path.read_text(encoding="utf8"))
    rows = d["subjects"]
    ids = [r["subject"]["id"] for r in rows]
    assert len(ids) == len(set(ids)) == d["attempts_requested"] == d["attempts_reported"]
    if all_existing:
        original = json.loads((root / "RESULTS.json").read_text())
        assert set(ids) == {a["id"] for a in original["attempts"]}
        assert len(ids) == 31
    receipts = [e for r in rows for e in r["execution_receipts"]]
    assert len(receipts) == d["fresh_native_execution_count"]
    for row in rows:
        if row["checks"]:
            assert len(row["checks"]) == len({c["id"] for c in row["checks"]}) == 16
            assert sum(c["points"] for c in row["checks"]) == 100
            interval = row["scoring"]["score_interval"]
            assert 0 <= interval[0] <= interval[1] <= 100
            units = [u for c in row["checks"] for u in c.get("subchecks", [c])]
            earned = sum(u["points"] for u in units if u["status"] == "pass")
            unresolved = sum(u["points"] for u in units if u["status"] in {"unknown", "blocked_by_subject"})
            assert abs(interval[0] - earned) < 1e-6 and abs(interval[1] - earned - unresolved) < 1e-6
            assert set(row["scoring"]["critical_failures"]) == {c["id"] for c in row["checks"] if c["status"] == "fail"}
        if row["scoring"]["verdict"] == "scoped_pass":
            assert row["human_review_complete"] and row["scoring"]["qualified"]
            assert all(c["status"] == "pass" for c in row["checks"])
        for check in row["checks"]:
            if check["status"] in {"pass", "fail"}:
                assert check["evidence"]
            for evidence in check["evidence"]:
                if "path" not in evidence:
                    raise AssertionError("Unbound check evidence")
    for ev in receipts + [e for r in rows for c in r["checks"] for e in c["evidence"]]:
        p = Path(ev["path"])
        p = p if p.is_absolute() else root / p
        assert p.is_file(), str(p)
        assert hashlib.sha256(p.read_bytes()).hexdigest() == ev["sha256"], str(p)
    assert d["runner_unchanged_during_run"]
    return {"attempts_verified": len(rows), "execution_receipts_verified": len(receipts), "all_existing": all_existing, "model_calls": d["model_calls"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    p.add_argument("--all-existing", action="store_true")
    a = p.parse_args()
    print(json.dumps(validate(a.report, Path(__file__).resolve().parent, a.all_existing)))
