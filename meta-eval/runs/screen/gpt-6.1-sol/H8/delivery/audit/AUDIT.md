# Architecture-study evidence audit

Status: **ACCOUNTING_PASS_WITH_LIMITATIONS**.

This audit covers the records supplied in `input/`. Counts and findings below are computed from this packet.

All **232 recorded turns** map to distinct supplied snapshot manifests and source-layout roots. No expected episode or snapshot metadata is missing; no orphan snapshot, duplicate turn identity, mismatched aggregate/episode record or hash mismatch was found.

The total includes **228 study turns and 4 compatibility-control turns**. The compatibility controls are `compat-workspace-write-v2` (one turn) and `compat-policy-three-turns-maintenance` (three turns). The latter has no aggregate index entry, but its episode and all three snapshot manifests are present.

R2 contains 24 chains, expanded into 24 maintenance episodes with 72 stage turns plus 12 repair episodes/turns. Its 72 stage snapshots live directly at `runs/{episode}/stages/{stage_id}`. Searching only `stages/*/snapshot` would miss them. The compatibility maintenance session contributes three more direct stage roots.

R3 retains all 48 attempts: 47 native completions and one transport failure. `R3-packaging-C1-r2` is the failed attempt; its final manifest is present. Its answer hash is the SHA-256 of empty bytes. Generation completion is not evidence of task correctness.

All supplied packet files match their declared lengths and SHA-256 hashes, and all snapshot manifests match the hashes in `snapshot-layout.json`. These are internal packet consistency checks. The packet contains **zero snapshot workspace bodies**, so the 34,440 manifest file entries cannot be checked against actual file contents.

## Coverage

| Evidence | Count |
|---|---:|
| input files | 425 |
| aggregate files | 10 |
| aggregate results | 169 |
| aggregate indexed episodes | 181 |
| stored episodes | 182 |
| distinct episode threads | 182 |
| recorded turns | 232 |
| snapshot manifests | 232 |
| source layout roots | 232 |
| final roots | 157 |
| stage roots | 75 |
| manifest file entries | 34440 |
| workspace bodies present | 0 |

| Aggregate receipt | Results | Episodes | Turns | Manifests present |
|---|---:|---:|---:|---:|
| `NATIVE-COMPATV2.json` | 1 | 1 | 1 | 1 |
| `NATIVE-F01.json` | 18 | 18 | 18 | 18 |
| `NATIVE-F01V2.json` | 18 | 18 | 18 | 18 |
| `NATIVE-F02.json` | 18 | 18 | 18 | 18 |
| `NATIVE-F03.json` | 18 | 18 | 18 | 18 |
| `NATIVE-R1B.json` | 24 | 24 | 24 | 24 |
| `NATIVE-R2.json` | 24 | 36 | 84 | 84 |
| `r3/NATIVE-calibration.json` | 8 | 8 | 8 | 8 |
| `r3/NATIVE-development.json` | 24 | 24 | 24 | 24 |
| `r3/NATIVE-test.json` | 16 | 16 | 16 | 16 |

Aggregate counts exclude the standalone compatibility maintenance session, whose three stages are included in total coverage.

## Findings and evidence limits

- **warning: episode_without_aggregate_entry**. {"source": "runs/compat-policy-three-turns-maintenance/episode.json", "detail": "Retained and included in turn accounting."}
- **warning: retained_execution_failure**. {"source": "r3/runs/R3-packaging-C1-r2/episode.json", "episode_status": "operational_or_transport_failure", "native_status": "transport_failed", "detail": "Retained in coverage; not a successful completion or verified task failure."}
- **warning: failure_diagnostic_absent**. {"source": "r3/runs/R3-packaging-C1-r2/episode.json", "detail": "Failure status has errors=[] and native.error=null. Its cause cannot be established from this packet."}
- **limitation: workspace_bodies_omitted**. {"count": 232, "source": "snapshot-layout.json#/reconstruction_notice", "detail": "workspace_exists is a source-layout claim. Copied manifests do not verify snapshot file bytes."}
- **limitation: native_payloads_and_grading_not_supplied**. {"detail": "Prompt/answer hashes and event ranges are receipts only. Native transcripts, prompt/answer bodies, tests and human validation are not independently verified."}

## Checks

| Check | Items checked | Result |
|---|---:|---|
| json_parse_and_unique_keys | 425 | PASS |
| packet_manifest_bytes_and_sha256 | 427 | PASS |
| unique_layout_roots | 232 | PASS |
| aggregate_registration_and_chain_shape | 169 | PASS |
| observed_assignment_design_cells | 9 | PASS |
| r3_repository_partition_disjointness | 3 | PASS |
| aggregate_episode_equality | 181 | PASS |
| episode_and_turn_identities | 232 | PASS |
| stage_sequence_and_receipt_event_ranges | 25 | PASS |
| token_arithmetic_and_resource_receipts | 232 | PASS |
| one_snapshot_per_recorded_turn | 232 | PASS |
| manifest_identity_against_source_layout | 232 | PASS |
| snapshot_manifest_entry_structure | 34440 | PASS |

Native receipt statuses: `{"completed": 231, "transport_failed": 1}`.
Human validation fields on stored episodes: `{"pending": 157, "absent": 25}`.

## Study-design accounting

F01, F01V2, F02 and F03 each contain all observed 3-task × 3-variant × 2-repeat cells. R1B contains 3 tasks × 2 variants × 4 repeats. R2 contains 3 families × 2 policies × 2 orders × 2 repeats. R3 contains two repeats for each of 24 observed cases, with repository partitions disjoint: calibration (2 repositories, 8 attempts), development (6 repositories, 24 attempts), test (4 repositories, 16 attempts). No gaps occur within these observed domains. A separately supplied preregistration is absent, so these checks cannot prove that an entirely omitted family or case never existed.

## Follow-up

Add or explicitly document the missing aggregate index entry for the compatibility maintenance control. To extend this audit to custody or correctness, supply the snapshot workspace bodies, native prompt/answer and event records, preregistration and grading/validation evidence. Preserve the failed R3 attempt and obtain its diagnostic event record before assigning a cause. No source records were changed by this audit.

## Method and reproducibility

Parse every JSON file with duplicate-key rejection. Expand each aggregate result into its episode(s), compare complete JSON values with stored episode records, and include standalone episodes. Expand each episode into native turns using its actual stage IDs. Resolve both `stages/{id}` and `stages/{id}/snapshot`, rejecting ambiguous roots. Compare exact root sets across expected turns, stored manifests and source layout; matching counts alone are insufficient. Preserve failed turns in the denominator.

Validate packet file lengths and SHA-256 hashes, manifest hashes against source-layout claims, manifest entry structure, receipt identities, stage sequences, cumulative token arithmetic and recorded event-range continuity. These checks validate supplied metadata, not the contents of unprovided source workspaces or event streams.

Reproduce with `python audit_sessions.py --input input --output audit`. Exit 0 means accounting checks passed; findings and evidence limitations remain. Exit 1 indicates discrepancies. `audit.json` contains exact per-check failures, input hashes and the full turn inventory; `turns.csv` provides the episode-to-snapshot mapping.
