"""Exercise audit detection against isolated copies of the supplied packet."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import tempfile

from audit_sessions import audit


def main():
    workspace = Path(__file__).resolve().parent
    original = audit(workspace / "input", workspace / "MANIFEST.json")
    assert original["status"] == "ACCOUNTING_PASS_WITH_LIMITATIONS"
    assert original["counts"]["recorded_turns"] == original["counts"]["snapshot_manifests"]
    assert any(r["native_status"] == "transport_failed" and r["manifest_present"] for r in original["turns"])
    results = [{"scenario": "baseline_all_turns_including_failure", "passed": True}]
    with tempfile.TemporaryDirectory(prefix=".audit-probes-", dir=workspace) as temp:
        temp_root = Path(temp).resolve()
        assert temp_root.is_relative_to(workspace)  # Verify recursive cleanup boundary.
        root = temp_root / "input"
        shutil.copytree(workspace / "input", root)
        shutil.copy2(workspace / "MANIFEST.json", temp_root / "MANIFEST.json")
        shutil.copy2(workspace / "prompt.md", temp_root / "prompt.md")
        shutil.copy2(workspace / "PROVENANCE.json", temp_root / "PROVENANCE.json")

        @contextmanager
        def changed(relative):
            path = root / relative
            body = path.read_bytes()
            try:
                yield path
            finally:
                path.write_bytes(body)

        def verify(name, required):
            report = audit(root, temp_root / "MANIFEST.json")
            failed = {c["check"] for c in report["checks"] if not c["passed"]}
            assert report["status"] == "DISCREPANCIES", name
            assert required <= failed, (name, required, failed)
            results.append({"scenario": name, "passed": True, "detected_checks": sorted(failed)})

        stage = "runs/R2-F01-direct-A-r1-maintenance/stages/01-C1/manifest.json"
        with changed(stage) as path:
            path.unlink()
            verify("missing_direct_stage_manifest", {"one_snapshot_per_recorded_turn"})

        failed_final = "r3/runs/R3-packaging-C1-r2/final/manifest.json"
        with changed(failed_final) as path:
            path.unlink()
            verify("missing_failed_attempt_manifest", {"one_snapshot_per_recorded_turn"})

        with changed(stage) as path:
            orphan = root / "runs/orphan/final/manifest.json"
            orphan.parent.mkdir(parents=True)
            orphan.write_bytes(path.read_bytes())
            path.unlink()
            try:
                verify("same_manifest_count_but_missing_and_orphan_roots", {"one_snapshot_per_recorded_turn"})
            finally:
                orphan.unlink()

        with changed(stage) as path:
            path.write_bytes(path.read_bytes() + b"\n")
            verify("manifest_bytes_changed_valid_json", {"manifest_identity_against_source_layout"})

        episode = "runs/F01-C1-V01-r1/episode.json"
        with changed(episode) as path:
            e = json.loads(path.read_text())
            e["native"]["tool_calls"] += 1
            path.write_text(json.dumps(e), encoding="utf-8")
            verify("aggregate_episode_disagreement", {"aggregate_episode_equality"})

        with changed(episode) as path:
            path.write_text('{"id":"one","id":"two"}', encoding="utf-8")
            verify("duplicate_json_keys", {"json_parse_and_unique_keys"})

        with changed(episode) as path:
            path.unlink()
            verify("missing_episode_keeps_aggregate_turn_expectation", {"aggregate_episode_equality"})

    after = audit(workspace / "input", workspace / "MANIFEST.json")
    assert after["input_inventory"] == original["input_inventory"]
    assert after["status"] == original["status"]
    results.append({"scenario": "original_input_inventory_unchanged", "passed": True})
    destination = workspace / "audit" / "VALIDATION.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps({"passed": True, "scenarios": results}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "scenarios": len(results), "report": str(destination)}))


if __name__ == "__main__":
    main()
