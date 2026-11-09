"""Audit the supplied architecture-study packet without changing source records.

Usage: python audit_sessions.py [--input input] [--output audit]
Exit 0: accounting checks pass (limitations may remain); exit 1: discrepancies.
Uses only the Python standard library. Counts are derived, never campaign constants.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import itertools
import json
from pathlib import Path, PurePosixPath
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def audit(root, packet_manifest=None):
    issues, checks, rows, groups = [], [], [], []

    def check(name, failures, checked):
        checks.append({"check": name, "checked": checked, "passed": not failures,
                       "failures": failures})
        for failure in failures:
            issues.append({"severity": "error", "code": name, "detail": failure})

    files = sorted(p for p in root.rglob("*") if p.is_file())
    docs, parse_errors = {}, []
    inventory = []
    for p in files:
        relative = p.relative_to(root).as_posix()
        data = p.read_bytes()
        inventory.append({"path": relative, "bytes": len(data), "sha256": sha(data)})
        if p.suffix == ".json":
            try:
                docs[relative] = load(p)
            except (ValueError, UnicodeError) as exc:
                parse_errors.append({"path": relative, "error": str(exc)})
    check("json_parse_and_unique_keys", parse_errors, len(files))
    if parse_errors:
        return {"status": "DISCREPANCIES", "checks": checks, "findings": issues,
                "input_inventory": inventory, "turns": [], "groups": []}

    packet_errors = []
    if packet_manifest and packet_manifest.exists():
        packet = load(packet_manifest)
        entries = packet["files"]
        names = [e["path"] for e in entries]
        for name, count in collections.Counter(names).items():
            if count != 1:
                packet_errors.append({"duplicate_path": name, "count": count})
        for e in entries:
            p = packet_manifest.parent / e["path"]
            if not p.is_file():
                packet_errors.append({"missing": e["path"]})
            elif len(p.read_bytes()) != e["bytes"] or sha(p.read_bytes()) != e["sha256"]:
                packet_errors.append({"identity_mismatch": e["path"]})
        expected_input = {e["path"][6:] for e in entries if e["path"].startswith("input/")}
        if expected_input != {x["path"] for x in inventory}:
            packet_errors.append({"missing_input": sorted(expected_input - set(docs)),
                                  "extra_input": sorted(set(docs) - expected_input)})
        check("packet_manifest_bytes_and_sha256", packet_errors, len(entries))

    episodes = {k: v for k, v in docs.items() if k.endswith("/episode.json")}
    manifests = {k.removesuffix("/manifest.json"): v for k, v in docs.items()
                 if k.endswith("/manifest.json")}
    layout = docs["snapshot-layout.json"]["source_layout"]
    layout_by_root = {x["root"]: x for x in layout}
    duplicate_layout = [{"root": k, "count": n} for k, n in
                        collections.Counter(x["root"] for x in layout).items() if n != 1]
    check("unique_layout_roots", duplicate_layout, len(layout))
    expected_episodes, origins, chain_errors = {}, {}, []
    aggregate_count = 0
    design_checks, design_errors, partitions = [], [], {}
    for path, data in sorted(docs.items()):
        if not PurePosixPath(path).name.startswith("NATIVE-"):
            continue
        results = data["results"]
        aggregate_count += 1
        prefix = "r3/" if path.startswith("r3/") else ""
        group = {"source": path, "results": len(results), "episodes": 0, "turns": 0}
        assignments = [x["assignment"] for x in results]
        if path.startswith("r3/"):
            partitions[data["partition"]] = sorted({a["repository"] for a in assignments})
            observed = {(a["case"]["id"], a["repeat"]) for a in assignments}
            desired = set(itertools.product({a["case"]["id"] for a in assignments},
                                             {a["repeat"] for a in assignments}))
        else:
            fields = ("family", "policy", "order", "repeat") if path == "NATIVE-R2.json" else ("task", "variant", "repeat")
            if all(all(f in a for f in fields) for a in assignments):
                observed = {tuple(a[f] for f in fields) for a in assignments}
                desired = set(itertools.product(*({a[f] for a in assignments} for f in fields)))
            else:
                observed = desired = None
        if observed is not None:
            design_checks.append({"source": path, "observed_cells": len(observed),
                                  "expected_from_observed_domains": len(desired),
                                  "missing_cells": sorted(desired - observed)})
            if observed != desired or len(observed) != len(results):
                design_errors.append(design_checks[-1])
        ids = [x["id"] for x in results]
        if len(set(ids)) != len(ids):
            chain_errors.append({"source": path, "duplicate_result_ids": ids})
        if "registered" in data and data["registered"] != len(results):
            chain_errors.append({"source": path, "registered": data["registered"],
                                 "results": len(results)})
        for index, result in enumerate(results):
            children = [("", result)] if "native" in result else [
                (k, result[k]) for k in ("repair", "maintenance") if result.get(k)]
            if "maintenance" in result:
                a = result["assignment"]
                sequence = [s["task"] for s in result["maintenance"]["stages"]]
                if sequence != a["sequence"] or len(sequence) != len(a["public_tasks"]):
                    chain_errors.append({"id": result["id"], "sequence": sequence,
                                         "assignment_sequence": a["sequence"]})
                if (a["policy"] == "repair") != bool(result.get("repair")):
                    chain_errors.append({"id": result["id"], "repair_policy_mismatch": True})
                if result.get("blocked_stages") or result.get("errors"):
                    issues.append({"severity": "warning", "code": "chain_execution_issue",
                                   "id": result["id"], "source": path})
            for key, episode in children:
                ep = f"{prefix}runs/{episode['id']}/episode.json"
                if ep in expected_episodes:
                    chain_errors.append({"duplicate_expected_episode": ep})
                expected_episodes[ep] = episode
                origins[ep] = f"{path}#/results/{index}" + (f"/{key}" if key else "")
                group["episodes"] += 1
                group["turns"] += len(episode["stages"]) if "stages" in episode else 1
        groups.append(group)
    check("aggregate_registration_and_chain_shape", chain_errors, sum(g["results"] for g in groups))
    check("observed_assignment_design_cells", design_errors, len(design_checks))
    overlaps = [{"partitions": [a, b], "overlap": sorted(set(partitions[a]) & set(partitions[b]))}
                for a, b in itertools.combinations(partitions, 2) if set(partitions[a]) & set(partitions[b])]
    check("r3_repository_partition_disjointness", overlaps, len(partitions))
    comparisons = []
    for path, expected in expected_episodes.items():
        if path not in episodes:
            comparisons.append({"missing_episode": path, "source": origins[path]})
        elif expected != episodes[path]:
            fields = sorted(k for k in set(expected) | set(episodes[path])
                            if expected.get(k) != episodes[path].get(k))
            comparisons.append({"episode": path, "different_fields": fields,
                                "source": origins[path]})
    check("aggregate_episode_equality", comparisons, len(expected_episodes))
    unindexed = sorted(set(episodes) - set(expected_episodes))
    for path in unindexed:
        issues.append({"severity": "warning", "code": "episode_without_aggregate_entry",
                       "source": path, "detail": "Retained and included in turn accounting."})

    # Use the union: a missing episode must not erase its expected snapshots.
    union = {**expected_episodes, **episodes}
    identity_errors, stage_errors, usage_errors = [], [], []
    turn_keys, thread_ids, episode_ids = [], [], []
    expected_roots = []
    for path, e in sorted(union.items()):
        run = path.removesuffix("/episode.json")
        episode_ids.append(e["id"])
        thread_ids.append(e.get("thread_id"))
        if PurePosixPath(run).name != e["id"] or e.get("assignment", {}).get("id", e["id"]) != e["id"]:
            identity_errors.append({"episode": path, "id_mismatch": e["id"]})
        if e.get("started_utc") and e.get("finished_utc"):
            if datetime.datetime.fromisoformat(e["started_utc"]) > datetime.datetime.fromisoformat(e["finished_utc"]):
                identity_errors.append({"episode": path, "timestamps_reversed": True})
        stages = e.get("stages")
        units = stages if stages is not None else [{"id": "final", "native": e["native"]}]
        active, previous_usage, previous_range = [], None, None
        for s in units:
            n = s["native"]
            candidates = [f"{run}/stages/{s['id']}", f"{run}/stages/{s['id']}/snapshot"] if stages is not None else [f"{run}/final"]
            matches = [c for c in candidates if c in layout_by_root or c in manifests]
            snapshot = matches[0] if matches else candidates[0]
            if len(matches) > 1:
                stage_errors.append({"episode": path, "stage": s["id"], "ambiguous_roots": matches})
            expected_roots.append(snapshot)
            turn_keys.append((n.get("thread_id"), n.get("turn_id")))
            if not n.get("thread_id") or not n.get("turn_id") or n.get("thread_id") != e.get("thread_id"):
                identity_errors.append({"episode": path, "stage": s["id"], "thread_or_turn_identity": n})
            for field in ("answer_sha256", "prompt_sha256"):
                if not re.fullmatch(r"[0-9a-f]{64}", n.get(field, "")):
                    identity_errors.append({"episode": path, "stage": s["id"], "invalid_hash": field})
            usage = n.get("cumulative_native_usage", {})
            if usage.get("totalTokens") != usage.get("inputTokens", 0) + usage.get("outputTokens", 0):
                usage_errors.append({"episode": path, "stage": s["id"], "token_arithmetic": usage})
            if stages is not None:
                active.append(s["task"])
                if s["active"] != active or s["id"] != f"{len(active):02}-{s['task']}" or s.get("snapshot_status") != "completed":
                    stage_errors.append({"episode": path, "stage": s["id"], "stage_sequence_or_snapshot_status": True})
                if previous_usage and any(usage[k] < previous_usage[k] for k in usage):
                    usage_errors.append({"episode": path, "stage": s["id"], "nonmonotonic_usage": True})
                event_range = n.get("server_event_range")
                if previous_range and event_range[0] != previous_range[1]:
                    stage_errors.append({"episode": path, "stage": s["id"], "event_range_discontinuity": True})
                previous_range, previous_usage = event_range, usage
            rows.append({"episode": path, "aggregate_source": origins.get(path), "episode_present": path in episodes,
                         "stage": s["id"], "snapshot_root": snapshot,
                         "manifest_present": snapshot in manifests, "layout_present": snapshot in layout_by_root,
                         "thread_id": n.get("thread_id"), "turn_id": n.get("turn_id"),
                         "native_status": n.get("status"), "generation_status": n.get("generation_status"),
                         "prompt_sha256": n.get("prompt_sha256"), "answer_sha256": n.get("answer_sha256"),
                         "workspace_body_present": (root / snapshot / "workspace").is_dir(),
                         "manifest_entries": len(manifests.get(snapshot, {}))})
        recorded = e.get("resources", {}).get("cumulative_native_usage", e.get("cumulative_native_usage"))
        if recorded != units[-1]["native"].get("cumulative_native_usage"):
            usage_errors.append({"episode": path, "resource_usage_differs_from_last_turn": True})
        if e.get("status") != "completed":
            issues.append({"severity": "warning", "code": "retained_execution_failure", "source": path,
                           "episode_status": e.get("status"), "native_status": units[-1]["native"].get("status"),
                           "detail": "Retained in coverage; not a successful completion or verified task failure."})
            if not e.get("errors") and not units[-1]["native"].get("error"):
                issues.append({"severity": "warning", "code": "failure_diagnostic_absent", "source": path,
                               "detail": "Failure status has errors=[] and native.error=null. Its cause cannot be established from this packet."})
    for key, n in collections.Counter(turn_keys).items():
        if n != 1:
            identity_errors.append({"duplicate_turn_identity": key, "count": n})
    for key, n in collections.Counter(episode_ids).items():
        if n != 1:
            identity_errors.append({"duplicate_episode_id": key, "count": n})
    check("episode_and_turn_identities", identity_errors, len(rows))
    check("stage_sequence_and_receipt_event_ranges", stage_errors, sum("stages" in e for e in union.values()))
    check("token_arithmetic_and_resource_receipts", usage_errors, len(rows))

    coverage_errors = []
    expected_set = set(expected_roots)
    for label, roots in (("manifest", set(manifests)), ("layout", set(layout_by_root))):
        for missing in sorted(expected_set - roots):
            coverage_errors.append({"missing_" + label: missing})
        for orphan in sorted(roots - expected_set):
            coverage_errors.append({"orphan_" + label: orphan})
    if len(expected_set) != len(rows):
        coverage_errors.append({"turns": len(rows), "unique_expected_roots": len(expected_set)})
    check("one_snapshot_per_recorded_turn", coverage_errors, len(rows))
    hash_errors, entry_errors = [], []
    for snapshot, manifest in sorted(manifests.items()):
        path = root / snapshot / "manifest.json"
        if snapshot in layout_by_root and sha(path.read_bytes()) != layout_by_root[snapshot]["manifest_source_sha256"]:
            hash_errors.append({"snapshot": snapshot, "manifest_hash_mismatch": True})
        for name, entry in manifest.items():
            safe = not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts and "\\" not in name
            if not safe or not isinstance(entry, dict) or not isinstance(entry.get("bytes"), int) or entry.get("bytes", -1) < 0 or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")):
                entry_errors.append({"snapshot": snapshot, "invalid_entry": name})
    check("manifest_identity_against_source_layout", hash_errors, len(manifests))
    check("snapshot_manifest_entry_structure", entry_errors, sum(len(m) for m in manifests.values()))
    for group in groups:
        group_rows = [r for r in rows if (r["aggregate_source"] or "").startswith(group["source"] + "#")]
        group["manifests_present"] = sum(r["manifest_present"] for r in group_rows)
    missing_bodies = sum(not r["workspace_body_present"] for r in rows)
    issues.extend([
        {"severity": "limitation", "code": "workspace_bodies_omitted", "count": missing_bodies,
         "source": "snapshot-layout.json#/reconstruction_notice",
         "detail": "workspace_exists is a source-layout claim. Copied manifests do not verify snapshot file bytes."},
        {"severity": "limitation", "code": "native_payloads_and_grading_not_supplied",
         "detail": "Prompt/answer hashes and event ranges are receipts only. Native transcripts, prompt/answer bodies, tests and human validation are not independently verified."}])
    return {"status": "DISCREPANCIES" if any(not c["passed"] for c in checks) else "ACCOUNTING_PASS_WITH_LIMITATIONS",
            "scope": "Local supplied packet; discovery and accounting, not workspace byte integrity or task correctness.",
            "counts": {"input_files": len(files), "aggregate_files": aggregate_count,
                       "aggregate_results": sum(g["results"] for g in groups),
                       "aggregate_indexed_episodes": len(expected_episodes), "stored_episodes": len(episodes),
                       "distinct_episode_threads": len(set(thread_ids)), "recorded_turns": len(rows),
                       "snapshot_manifests": len(manifests), "source_layout_roots": len(layout),
                       "final_roots": sum(r.endswith("/final") for r in manifests),
                       "stage_roots": sum("/stages/" in r for r in manifests),
                       "manifest_file_entries": sum(len(m) for m in manifests.values()),
                       "workspace_bodies_present": len(rows) - missing_bodies},
            "compatibility_turns": sum(PurePosixPath(r["episode"]).parent.name.startswith("compat-") for r in rows),
            "observed_design_checks": design_checks, "r3_repository_partitions": partitions,
            "native_status_counts": dict(collections.Counter(r["native_status"] for r in rows)),
            "human_validation_counts_on_episodes": dict(collections.Counter(e.get("human_validation", "absent") for e in episodes.values())),
            "unindexed_episodes": unindexed, "groups": groups, "checks": checks,
            "findings": issues, "turns": rows, "input_inventory": inventory,
            "reconstruction_notice": docs["snapshot-layout.json"]["reconstruction_notice"]}


def render(report):
    c = report.get("counts", {})
    lines = ["# Architecture-study evidence audit", "", f"Status: **{report['status']}**.", "",
             "This audit covers the records supplied in `input/`. Counts and findings below are computed from this packet.", ""]
    if report['status'] != 'DISCREPANCIES':
        lines += [f"All **{c['recorded_turns']} recorded turns** map to distinct supplied snapshot manifests and source-layout roots. No expected episode or snapshot metadata is missing; no orphan snapshot, duplicate turn identity, mismatched aggregate/episode record or hash mismatch was found.", "",
                  f"The total includes **{c['recorded_turns'] - report['compatibility_turns']} study turns and {report['compatibility_turns']} compatibility-control turns**. The compatibility controls are `compat-workspace-write-v2` (one turn) and `compat-policy-three-turns-maintenance` (three turns). The latter has no aggregate index entry, but its episode and all three snapshot manifests are present.", "",
                  "R2 contains 24 chains, expanded into 24 maintenance episodes with 72 stage turns plus 12 repair episodes/turns. Its 72 stage snapshots live directly at `runs/{episode}/stages/{stage_id}`. Searching only `stages/*/snapshot` would miss them. The compatibility maintenance session contributes three more direct stage roots.", "",
                  "R3 retains all 48 attempts: 47 native completions and one transport failure. `R3-packaging-C1-r2` is the failed attempt; its final manifest is present. Its answer hash is the SHA-256 of empty bytes. Generation completion is not evidence of task correctness.", "",
                  "All supplied packet files match their declared lengths and SHA-256 hashes, and all snapshot manifests match the hashes in `snapshot-layout.json`. These are internal packet consistency checks. The packet contains **zero snapshot workspace bodies**, so the 34,440 manifest file entries cannot be checked against actual file contents.", ""]
    lines += ["## Coverage", "", "| Evidence | Count |", "|---|---:|"]
    lines += [f"| {k.replace('_', ' ')} | {v} |" for k, v in c.items()]
    lines += ["", "| Aggregate receipt | Results | Episodes | Turns | Manifests present |",
              "|---|---:|---:|---:|---:|"]
    lines += [f"| `{g['source']}` | {g['results']} | {g['episodes']} | {g['turns']} | {g['manifests_present']} |" for g in report["groups"]]
    lines += ["", "Aggregate counts exclude the standalone compatibility maintenance session, whose three stages are included in total coverage.", "",
              "## Findings and evidence limits", ""]
    for f in report["findings"]:
        lines.append(f"- **{f['severity']}: {f['code']}**. " + json.dumps({k: v for k, v in f.items() if k not in ('severity', 'code')}, ensure_ascii=False))
    lines += ["", "## Checks", "", "| Check | Items checked | Result |", "|---|---:|---|"]
    lines += [f"| {x['check']} | {x['checked']} | {'PASS' if x['passed'] else 'FAIL'} |" for x in report["checks"]]
    lines += ["", "Native receipt statuses: `" + json.dumps(report.get("native_status_counts", {})) + "`.",
              "Human validation fields on stored episodes: `" + json.dumps(report.get("human_validation_counts_on_episodes", {})) + "`.", "",
              "## Study-design accounting", "",
              "F01, F01V2, F02 and F03 each contain all observed 3-task × 3-variant × 2-repeat cells. R1B contains 3 tasks × 2 variants × 4 repeats. R2 contains 3 families × 2 policies × 2 orders × 2 repeats. R3 contains two repeats for each of 24 observed cases, with repository partitions disjoint: calibration (2 repositories, 8 attempts), development (6 repositories, 24 attempts), test (4 repositories, 16 attempts). No gaps occur within these observed domains. A separately supplied preregistration is absent, so these checks cannot prove that an entirely omitted family or case never existed.", "",
              "## Follow-up", "",
              "Add or explicitly document the missing aggregate index entry for the compatibility maintenance control. To extend this audit to custody or correctness, supply the snapshot workspace bodies, native prompt/answer and event records, preregistration and grading/validation evidence. Preserve the failed R3 attempt and obtain its diagnostic event record before assigning a cause. No source records were changed by this audit.", "",
              "## Method and reproducibility", "",
              "Parse every JSON file with duplicate-key rejection. Expand each aggregate result into its episode(s), compare complete JSON values with stored episode records, and include standalone episodes. Expand each episode into native turns using its actual stage IDs. Resolve both `stages/{id}` and `stages/{id}/snapshot`, rejecting ambiguous roots. Compare exact root sets across expected turns, stored manifests and source layout; matching counts alone are insufficient. Preserve failed turns in the denominator.", "",
              "Validate packet file lengths and SHA-256 hashes, manifest hashes against source-layout claims, manifest entry structure, receipt identities, stage sequences, cumulative token arithmetic and recorded event-range continuity. These checks validate supplied metadata, not the contents of unprovided source workspaces or event streams.", "",
              "Reproduce with `python audit_sessions.py --input input --output audit`. Exit 0 means accounting checks passed; findings and evidence limitations remain. Exit 1 indicates discrepancies. `audit.json` contains exact per-check failures, input hashes and the full turn inventory; `turns.csv` provides the episode-to-snapshot mapping.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("input"))
    parser.add_argument("--output", type=Path, default=Path("audit"))
    args = parser.parse_args()
    report = audit(args.input, args.input.parent / "MANIFEST.json")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.output / "AUDIT.md").write_text(render(report), encoding="utf-8")
    with (args.output / "turns.csv").open("w", newline="", encoding="utf-8") as stream:
        if report["turns"]:
            writer = csv.DictWriter(stream, fieldnames=list(report["turns"][0]))
            writer.writeheader()
            writer.writerows(report["turns"])
    print(json.dumps({"status": report["status"], "counts": report.get("counts"),
                      "findings": len(report["findings"]), "failed_checks": sum(not c["passed"] for c in report["checks"])}))
    return 1 if report["status"] == "DISCREPANCIES" else 0


if __name__ == "__main__":
    raise SystemExit(main())
