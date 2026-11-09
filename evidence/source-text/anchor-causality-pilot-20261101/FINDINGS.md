> Archived source excerpt. Original location: `anchor-causality-pilot-20261101/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Why the repaired scores vary

Completed: 44 fresh native gpt-6.1-sol/high calls through Codex app-server, 32 diagnosis and 12 fresh validation. All outcomes retained. Inputs, both candidate anchors and fresh certificates were fixed before the first call. This is a local follow-up to the earlier 2,3,2 observations, not an exact replay of that elicitation protocol.

## Main finding

The usefulness boundary varies under identical visible inputs: P1 current exact singleton gives ['3', '3', '2']. Every diagnostic 3 accepts the impossibility-proof/declared-fallback comparison; every 2 rejects it. The difference is the expressed comparison judgment, while feasibility, limitation, check and adoption flags remain the same. This is observable interpretation variation, not access to hidden reasoning.

P2 current singleton gives ['2', '2', '2'], while its full-batch last-position cell gives ['3', '2']. Its 3 reads “verify both crash boundaries before rollout” as a decision prerequisite; its 2 does not infer an outcome-to-decision link. Thus residual variation also reproduces in that fixed-context cell. Tiny first/last samples do not establish that placement caused the difference.

## Exact diagnostic results

Ratings in repeat-number order; 2 or 3 observations per cell.

| Target | Intervention | Ratings |
| --- | --- | --- |
| P1 | current-base-singleton | 3, 3, 2 |
| P1 | current-base-first | 3, 2 |
| P1 | current-base-last | 3, 3 |
| P1 | current-explicit-singleton | 3, 3, 3 |
| P1 | v2-base-singleton | 3, 3, 3 |
| P1 | current-clean-singleton | 2, 2, 2 |
| P2 | current-base-singleton | 2, 2, 2 |
| P2 | current-base-first | 2, 2 |
| P2 | current-base-last | 3, 2 |
| P2 | current-explicit-singleton | 3, 3, 3 |
| P2 | v2-base-singleton | 2, 2, 2 |
| P2 | example-only-base-singleton | 2, 2, 2 |

## Changes fixed before inference

P1 v2 explicitly counts a proved-infeasible original versus an openly declared feasible relaxation as a justified comparison. It requires the candidate to supply the comparison, limitation, next check and adoption conditions; the assessor may not invent them. The base answer stays unchanged. A separate deletion-only arm removes the unsupported table sentence and yields ['2', '2', '2']; this is source-edit sensitivity, not proof that a missing table caused the old sequence.

P2 v2 distinguishes activity order from a result-conditioned decision: “check before rollout” alone has no explicit decision link; “roll out only if both checks pass” does. An only-if-pass gate does not need a redundant negative branch. The linked example is corrected with the text. The example-only control gives ['2', '2', '2']; no observed score effect in this cell does not prove examples have no effect generally.

## Fresh validation

The two versions each rated 12 fresh case variants, six per target across four new base domains, three repeats: 72 fresh judgments. The v2 matches to precommitted operational references are 36/36. Table consistency from the model's own reported features, diagnosis and fresh combined, is 42/42. Current-anchor clear controls match 24/24; its ambiguous boundaries have no uniquely preferred gold. Do not compare those unequal denominators as an accuracy lift.

Both versions gave identical ratings on 36/36 matched fresh judgments. This bank demonstrates preserved operational discrimination, not a fresh-case accuracy improvement from v2.

Controls include high, missing-comparison/missing-decision, explicit contradiction and unresolved-source/feasibility cases. A correct U is a reference match; a U on a decidable case is coverage loss, not a fabricated technical claim. Ratings and feature-reference differences for every answer appear in RESULTS.json and report.html; feature differences require source review and are not automatically factual failures.

## Limits and use

The evidence supports these explicit operational anchors as local candidates. It does not establish a scientifically preferred 2 or 3, human usefulness, confidence calibration, hiring validity, general order invariance or elimination of scoring instability. Both arms share new inline exposure, target-only output, structured feature extraction and source-independence instructions; those changes are confounded with comparison to the historical study. Answer clarification changes content and length together. The example intervention is nested rather than a full factorial design. Aliases are recorded, underlying weights are not independently attested. Tools were available; actual terminal calls = 0.

Human expert review remains pending. Preserve evidence-grounded features and apply deterministic gates for operational categories; do not silently force ambiguous old answers into a new preferred gold. No participant data or employment decision was used.

Independent source review found no cross-case or unknown cited evidence IDs across 624 feature records. Of 898 quoted spans, 897 matched literally; one capitalizes a source sentence's initial letter. That minor quote-fidelity defect is preserved, rather than repaired in the saved answer. All 216 fresh v2 feature codes match the operational reference coding.

Evidence: FREEZE.json, VALIDATION-FREEZE.json, AUDIT-FREEZE.json, native runs/, independent reviews under analysis/, CUSTODY-AUDIT.json and FINAL-MANIFEST.json. The historical study remains a separate frozen record.
