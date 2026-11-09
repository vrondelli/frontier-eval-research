> Archived source excerpt. Original location: `wording-ambiguity-isolation-pilot-20261101/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Wording versus case ambiguity: findings

**Human validation remains pending. The 30 reserved cases stayed outside this native experiment.**

The registered phase produced 54/54 completed native responses, with 53/54 primary-eligible trials, 53/54 primary and 212/216 background judgments. One completed response is operationally excluded after a snapshot failure during administrative cleanup. All results are retained; no scorer, case, proxy or observation was repaired after inference.

The earlier stop checkpoint incorrectly called this a pre-native failure. The same controller attempt continued after its hung helper was stopped, then failed its snapshot after container removal. The correction and preserved timeline (historical reference: `RESUME-ERRATUM.md`) keep the excluded answer separate. No new model call or replacement trial was made on resume.

| Readout | Observed / planned |
| --- | ---: |
| Cells retaining the same decision across all three repeats | 13/18 |
| Cells retaining the same full feature vector across all three repeats | 12/18 |
| Within-condition style pairs with the same decision | 21/27 |
| Within-condition style pairs with the same full feature vector | 19/27 |
| Primary categories within authored allowed sets | 50/54 |

The last row is reference-set membership, not accuracy. Some sets deliberately allow ambiguity. A decision is applicability plus category; U and N/A are not numeric distances. The 27 style comparisons include the disputed bridge conditions and must be read by condition.

## All conditions and repeats

| Lane / condition | Style | Repeat 1 / 2 / 3 | Authored allowed category set |
| --- | --- | --- | --- |
| lane-a / bridge | command | 3 / 2 / 3 | 2 or 3 |
| lane-a / bridge | nominal | 2 / 2 / 1 | 2 or 3 |
| lane-a / explicit_branch | command | 3 / 3 / 3 | 3 |
| lane-a / explicit_branch | nominal | 3 / 3 / 3 | 3 |
| lane-a / sequence_only | command | 2 / 2 / 2 | 2 |
| lane-a / sequence_only | nominal | 2 / 2 / 2 | 2 |
| lane-b / unspecified_permission | direct | 0 / 2 / 2 | 2 or U |
| lane-b / unspecified_permission | nominal | U / 0 / U | 2 or U |
| lane-b / permitted_revision | direct | 2 / 2 / 2 | 2 |
| lane-b / permitted_revision | nominal | 2 / 2 / 2 | 2 |
| lane-b / fixed_implementation | direct | 0 / 0 / excluded from primary | 0 |
| lane-b / fixed_implementation | nominal | 0 / 0 / 0 | 0 |
| lane-c / both_explicit | imperative | 2 / 2 / 2 | 2 |
| lane-c / both_explicit | nominal | 2 / 2 / 2 | 2 |
| lane-c / unspecified | imperative | 2 / 2 / 2 | 2 |
| lane-c / unspecified | nominal | 2 / 2 / 2 | 2 |
| lane-c / precommit_only | imperative | 2 / 2 / 2 | 2 |
| lane-c / precommit_only | nominal | 2 / 2 / 2 | 2 |

## Main interpretation

Across explicitly stated conditions, 17/17 available style pairs retain the category/applicability decision (18 planned; one is excluded). This descriptive grouping of the frozen conditions shows no general command-versus-nominal category penalty in the observed explicit controls. All four category-unstable repeat groups are original underspecified compatibility/compression bridges. This supports a local interpretation/under-specification explanation, with human adjudication still pending. It does not identify a unique internal cause or validate the reference sets.

The all-54-native-output diagnostic sensitivity is preserved separately in independent counts (historical reference: `analysis/metric-independent-counts.json`). It includes the excluded response and its four backgrounds only as a diagnostic, without changing the 53-trial primary inclusion policy. The excluded response gives category 0 for the fixed-contract control; treating it diagnostically does not create an unambiguous control failure.

## Identical-input variation versus wording

The following cases change applicability/category across identical supplied prompts:
- A410V1 / bridge / command: 3 / 2 / 3.
- A410V2 / bridge / nominal: 2 / 2 / 1.
- B520V1 / unspecified_permission / direct: 0 / 2 / 2.
- B520V2 / unspecified_permission / nominal: U / 0 / U.
This is observed within the new fixed batches, independently of old-to-new batch differences. A deterministic surface-style explanation is insufficient. Paired style differences can combine wording, task interpretation and repeated-call variation; three repeats cannot identify the internal cause or a population rate.

Feature-only repeat variation also occurs with an unchanged category:
- C630V5: {"specific_limitation": ["yes", "no", "yes"]}.
These are observed feedback differences across identical inputs. A flag can reflect competing interpretations without changing the category because another gate determines that category. They are not evidence of a wording cause or a human-confirmed wrong label.

## Compatibility: explicit controls versus the old bridge

- bridge: categories 1 × 1, 2 × 3, 3 × 2; style decisions agree 1/3 and feature vectors 0/3. Decision-link flags: no × 4, yes × 2.
- explicit_branch: categories 3 × 6; style decisions agree 3/3 and feature vectors 3/3. Decision-link flags: yes × 6.
- sequence_only: categories 2 × 6; style decisions agree 3/3 and feature vectors 3/3. Decision-link flags: no × 6.

No category-level style difference appears in the two clarified compatibility conditions in this run. This narrows the residual issue to the bridge/interpretation boundary under the tested controls; it does not prove that ambiguity is the sole cause or that every phrasing is robust.

The original nominal bridge can be read strictly as a correct policy/cost account without an expressly uncertain reader inventory or a sufficiently specified check. A compositional reading recovers the old-reader risk and inventory target from context. The frozen bridge set remains 2/3 even if an actual output falls outside it. The new explicit/sequence controls both add that reader presence is currently unknown; bridge-to-control contrasts therefore change uncertainty explicitness as well as the action-link content. Within those two controls the prefix is matched, allowing the explicit-branch contrast to remain distinct.

## Compression: task contract and candidate evidence

- unspecified_permission: categories 0 × 2, 2 × 2, U × 2; style decisions agree 0/3; comparison flags: no × 6.
- permitted_revision: categories 2 × 6; style decisions agree 3/3; comparison flags: no × 6.
- fixed_implementation: categories 0 × 5; style decisions agree 2/3; comparison flags: no × 5.

Permitted-revision versus fixed-implementation comparisons change the decision in 5/6 registered pairs. Candidate text stays identical across scope within a style, and the original mathematical facts stay fixed. This tests the named assessment objective, not a paraphrase of that objective.

Permission is not candidate comparison evidence. A working two-bit identity route can be assessed as separately scoped advice when expressly permitted; it cannot meet an unchanged one-bit implementation contract. The latter can receive 0 through the no-applicable-action boundary even when a particular mandatory-violation feature interpretation is contested. Do not substitute an incomplete six-boolean table for the full E3 criterion. The new unspecified 2/U set is prospective uncertainty disclosure; the earlier study’s category-2 proxy and U/U observations remain unchanged.

The Lane B source review preserves three noncanonical `B520 task` citations. Their quoted task text exists, but the identifiers are not silently normalized into canonical evidence IDs. This is a citation-format issue separate from the permission/feasibility interpretation.

## Crash checks: coverage versus grammar

- both_explicit: categories 2 × 6; style decisions agree 3/3, full feature vectors 3/3; check flags: yes × 6.
- unspecified: categories 2 × 6; style decisions agree 3/3, full feature vectors 3/3; check flags: no × 6.
- precommit_only: categories 2 × 6; style decisions agree 3/3, full feature vectors 2/3; check flags: yes × 6.

The common mechanism prefix removes the previous prefix-change confound. Both named cut points make coverage explicit. Unnamed boundary verification retains contextual-versus-explicit readings. An explicit pre-commit-only test can detect a partial-application fault and therefore can discriminate without providing complete test coverage. The author’s broad sets for partial/unspecified checks must not be called evidence of correct check recognition. Category 2 can mask changes in this feature because none of these candidates supplies the result-dependent rollout decision needed for 3.

## What is and is not isolated

The study keeps the scorer fixed while crossing surface bundles with named substantive conditions. It can locate disagreement within a clearer versus disputed condition. It cannot prove an internal linguistic mechanism, certify every transformation or determine a human-preferred category. The original bridge objects recur, but target aliases, batch order and positions differ from the preceding study; old-to-new changes are not exact full-prompt repeatability results. Three repeats remain a small dependent diagnostic, with matching repeat indices unrelated to shared random seeds.

Source reviews preserve the actual rationales and possible case/reference shortcomings. Compatibility review (historical reference: `analysis/lane-a-output-review.md`), compression review (historical reference: `analysis/lane-b-output-review.md`) and crash-check review (historical reference: `analysis/lane-c-output-review.md`) are AI analysis, not human labels. The native replay (historical reference: `analysis/native-custody.json`) and independent raw-count check (historical reference: `analysis/metric-crosscheck.json`) establish custody/arithmetic, not validity.

## Human validation and delivery boundary

The two existing reviewer packs remain unchanged, with zero completed human exports and native release false. No reserved case enters assessed Sol. The current authorized delivery is this frozen diagnostic plus independent checks and report; prospective human semantic review and hiring validation remain pending. Neither reference-set adherence nor subagent agreement establishes hiring quality, global originality or a first-place contribution.

Inspect every actual task, synthetic answer and Sol judgment in the interactive report (historical reference: `report.html`).
