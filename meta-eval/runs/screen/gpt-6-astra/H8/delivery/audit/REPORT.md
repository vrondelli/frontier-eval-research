# Stored architecture-study evidence audit

The supplied packet has complete **receipt-to-manifest accounting**: 182 sessions, 232 distinct native turns, and 232 matching snapshot manifests. No missing expected manifests, orphan manifests, duplicate session/turn identities, aggregate-to-episode disagreements, or digest mismatches were found by the checks described below. This is a limited accounting result, not certification of workspace contents or study outcomes.

The study records account for 180 sessions and 228 snapshots. Two compatibility sessions add four snapshots. One study turn failed operationally; its receipt and snapshot manifest remain included.

## Coverage

Counts are derived from the supplied records, not a historical expected total. Session means one `episode.json` and its thread; a staged session contributes one turn and one expected snapshot per stage.

| Record group | Sessions | Native turns | Matching manifests | Completed native turns |
|---|---:|---:|---:|---:|
| F01 | 18 | 18 | 18 | 18 |
| F01V2 | 18 | 18 | 18 | 18 |
| F02 | 18 | 18 | 18 | 18 |
| F03 | 18 | 18 | 18 | 18 |
| R1B | 24 | 24 | 24 | 24 |
| R2 repair | 12 | 12 | 12 | 12 |
| R2 maintenance | 24 | 72 | 72 | 72 |
| R3 calibration | 8 | 8 | 8 | 8 |
| R3 development | 24 | 24 | 24 | 24 |
| R3 test | 16 | 16 | 16 | 15 |
| **Study subtotal** | **180** | **228** | **228** | **227** |
| Compatibility write (`COMPATV2`) | 1 | 1 | 1 | 1 |
| Compatibility policy | 1 | 3 | 3 | 3 |
| **All supplied sessions** | **182** | **232** | **232** | **231** |

The compatibility groups are separated by their fixture IDs; the write fixture also explicitly carries `excluded_from_benchmark: true`. F01 and F01V2 are counted as distinct stored cohorts, without assuming that both belong in a final benchmark analysis.

The 24 results in [NATIVE-R2.json](../input/NATIVE-R2.json) are policy chains, not 24 single-turn sessions. They reference 24 maintenance sessions with three turns each, plus 12 repair sessions. These expand to 36 sessions and 84 snapshots. All chain assignment sequences agree with their maintenance stage tasks.

There are **157 final snapshots** under `runs/<id>/final` (including the corresponding `r3/runs/` paths) and **75 stage snapshots** directly under `runs/<id>/stages/<stage-id>`. The stage total comprises 72 R2 snapshots and three compatibility snapshots. A discovery rule restricted to `stages/*/snapshot` would miss all 75 supplied stage manifests. The auditor resolves each receipt stage against both supported layouts and requires exactly one match, then independently reconciles all discovered manifests and layout declarations.

## Verified records and consistency

| Check | Result |
|---|---|
| Input JSON files parse, including duplicate-key detection | 425 / 425 |
| Input file sizes and SHA-256 match root `MANIFEST.json` | 425 / 425 |
| Supplied source-binding sizes and SHA-256 match copied files | 424 / 424 |
| Aggregate episode objects match local episode objects exactly | 181 / 181 referenced sessions |
| Snapshot manifest hashes match `snapshot-layout.json` | 232 / 232 |
| Receipt turns have exactly one manifest and a layout declaration | 232 / 232 |
| Declared snapshots have a receipt turn | 232 / 232 |
| Session thread identities are present and unique | 182 / 182 |
| Native turn identities are present and unique | 232 / 232 |
| Snapshot file-entry metadata is structurally valid | 34,440 / 34,440 entries |

Ten `NATIVE-*.json` aggregate files were inspected. There are no missing aggregate-referenced episodes. The one episode without an aggregate reference is discussed below. The additional input file without a copied source binding is the packet's `snapshot-layout.json`.

Additional checks found no episode/directory/assignment ID mismatches, native-to-session thread disagreements, reversed session timestamps, duplicate stage IDs, reused snapshot roots, incomplete stage snapshot statuses, invalid prompt/answer digest formats, invalid event-range ordering, token-total arithmetic errors, decreasing within-session cumulative usage, or disagreement between final native usage and episode resource usage. All 182 episodes record `actor_stopped: true`. These are checks on stored assertions, not independent observations of the original runs.

## Gaps and exceptional records

1. **Workspace bodies intentionally omitted.** [snapshot-layout.json](../input/snapshot-layout.json) explicitly states that manifests were copied and workspace bodies omitted. Its 232 `workspace_exists: true` declarations describe the source layout; there are zero local `workspace` directories. The manifests describe 34,440 file occurrences totaling 221,858,341 bytes across snapshots, including repeated files. None of those workspace bytes can be verified here. This is a disclosed packet limitation, not 232 proven missing source snapshots.

2. **One retained operational failure with insufficient diagnostic detail.** [R3-packaging-C1-r2/episode.json](../input/r3/runs/R3-packaging-C1-r2/episode.json) agrees exactly with its entry in [NATIVE-test.json](../input/r3/NATIVE-test.json). The episode records `operational_or_transport_failure`; native status is `transport_failed`, and generation/native completion statuses are `failed`. Its answer digest is the SHA-256 of empty bytes. However, `native.error` is null and `errors` is empty. The failure classification is recorded consistently, but its cause cannot be established from this packet. The final manifest exists and is included in coverage; its existence does not imply successful completion. There are 47 completed native R3 turns out of 48, and 15 out of 16 in the test partition; these are execution counts, not correctness or eligibility judgments.

3. **One standalone compatibility session.** [compat-policy-three-turns-maintenance/episode.json](../input/runs/compat-policy-three-turns-maintenance/episode.json) has three completed turns and three matching manifests, but no supplied `NATIVE-*.json` aggregate references it. It is explicitly retained in this audit. An aggregate-only inventory would omit this session and its three snapshots. The packet does not establish whether an aggregate was ever produced, so this is an aggregate-reference gap, not proof of a lost record.

4. **Original event, prompt, answer, and execution evidence is unavailable.** The 425 input files consist solely of ten aggregates, 182 episodes, 232 snapshot manifests, and one layout declaration. Native receipts supply prompt/answer hashes, event ranges, resource counters, and tool-call counts; their underlying content and event logs are not supplied. Their recorded formats and internal relationships can be checked, but event completeness, actual tool behavior, timings, and prompt/answer integrity cannot be independently reconstructed.

5. **Outcome validation remains outside this packet's evidence coverage.** Human validation is explicitly `pending` in 157 episode receipts; the other 25 staged episode receipts have no such field. Absence is not approval. R2 aggregates contain embedded repair-gate assessments, but the packet lacks executable workspace contents and does not provide a complete independent grading record for all turns. Native `completed` status must not be interpreted as a passed architecture task. Full campaign completeness beyond the registrations and sessions represented here also cannot be established without an external study registry.

No additional missing or inconsistent accounting records were detected. Hash comparisons establish agreement with the supplied manifests and source bindings; they do not independently authenticate the original source or verify omitted content.

## Reproduction and deliverables

Run from the workspace root:

```powershell
python audit_architecture.py
python -m unittest test_audit_architecture -v
```

- [audit.json](audit.json) contains counts, group summaries, observations, inconsistencies, and all turn-to-snapshot mappings.
- [coverage.csv](coverage.csv) contains one row per turn, with episode path, stage ID, thread/turn IDs, native status, snapshot root, and exact aggregate JSON pointer where present.
- [audit_architecture.py](../audit_architecture.py) regenerates those outputs using the supplied files. It returns exit code 1 on accounting inconsistencies and labels workspace integrity separately as not verifiable.
- [test_audit_architecture.py](../test_audit_architecture.py) checks the supplied packet and four deliberate defects in disposable copies: a missing R2 stage manifest, altered manifest bytes, aggregate/episode disagreement, and an unreferenced extra snapshot. These controls test detection; they are not defects in the original input.

Validation result: all five tests passed. Each deliberate defect produced an accounting failure with the expected finding, while the supplied packet passed the accounting checks and retained the workspace-integrity limitation.

The audit reads `input/` without modifying it. No original study execution or grading was rerun.
