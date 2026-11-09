> Archived source excerpt. Original location: `semantic-invariance-pilot-20261101/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Frozen-scorer semantic diagnostics: findings

**Both independent human review packs are ready. Human validation remains pending as requested.** The separate 30 new cases have not been assessed by native Sol.

The registered known-case study produced 60/60 usable Sol/high calls, 60/60 primary judgments and 240/240 background judgments. There were 0 episode/admission errors and 0 automatic retries.

| Diagnostic | Observed desired relation / planned | Available comparisons |
| --- | ---: | ---: |
| Identical-prompt repeat decisions agree | 30/30 | 30 |
| Intended-equivalent variants retain the decision | 22/24 | 24 |
| Consequential variants change the decision | 24/24 | 24 |
| Judgments within the frozen operational reference sets | 58/60 | 60 |

A decision is the joint applicability/category pair. U and N/A are distinct statuses, not numeric zero. A category change alone does not establish correctness; the proxy-set check and source evidence remain separate.

## All variants, without selection

| Family | Base | Equivalent 1 | Equivalent 2 | Consequential 1 | Consequential 2 |
| --- | --- | --- | --- | --- | --- |
| Disconnected spending rights | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 3 | 0 / 0 |
| Useful novelty per fixed budget | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 3 | 0 / 0 |
| Compression and explicit relaxation | 3 / 3 | 3 / 3 | 3 / 3 | U / U | 0 / 0 |
| Reader inventory and compatibility | 3 / 3 | 3 / 3 | 2 / 2 | 0 / 0 | U / U |
| Retry directive versus factual claim | 2 / 2 | 2 / 2 | 2 / 2 | 0 / 0 | 0 / 0 |
| Atomic journal and rollout gate | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 3 | 0 / 0 |

Each cell contains both repeat outputs. The full question, candidate snippets, feature judgments, decision basis and exact raw answers are accessible in the interactive report (historical reference: `report.html`). The reader-inventory base/equivalents retain a frozen allowed set of 2 or 3; the experiment does not retroactively choose one as human truth.

## What this means

The table and raw outputs show which registered relations hold and which need review. A disagreement may reflect stochastic scoring, a disputed semantic transformation or a rubric/reference issue. Do not attribute a causal wording mechanism from these counts alone.

Feature vectors also agreed for 30/30 identical repeats and 20/24 intended-equivalence comparisons. Evidence quotations and explanations can differ even when the decision and feature values agree.

The practical distinctions are visible in the cases: a spending-rights allocation protects a global cap while uncoordinated rights growth can break it; a reproduction check is different from a stated result-conditioned publication decision; a declared two-bit fallback is different from claiming to satisfy a one-bit limit. For uncertain transcripts, a disputed imperative does not erase securely attributable risk evidence, while a securely attributable false factual guarantee can still be decisive.

## Concrete boundaries to review

**Reader-inventory wording:** the base received 3 / 3; the second intended paraphrase received 2 / 2. Both retain the rule to write identity encoding while old readers remain, plus an inventory check before switching. The lower-scored version is treated as lacking a result-to-action link. Its first sentence nevertheless retains a conditional writing policy. This is a candidate conditional-evidence integration failure, or a disputed semantic relation. Both categories belong to the frozen allowed set; absolute proxy agreement therefore does not resolve the invariance issue. Inspect the actual judgment (historical reference: `runs/p2-t356v3-r1/answer.json`).

**Shortened compression answer:** the proof-removal variant received U / U, against the frozen proposal of 2. Sol does not dispute that two-bit identity encoding works. The conflict concerns whether the answer offers an authorized conditional relaxation or leaves the original mandatory requirement unresolved. The source review identifies a legitimate case/anchor scope ambiguity; this is not a confirmed model error. The original proxy remains frozen, and the additional route-scope concern is recorded as a posthoc finding, not retrofitted into the preflight. A change from 3 to U still passes the coarse category-change endpoint while failing exact operational reference agreement. Inspect the actual judgment (historical reference: `runs/p1-t913v4-r1/answer.json`).

**Feature-only drift:** the atomic-journal base and its second intended paraphrase both retain category 2, but the discriminating-check feature changes from yes to no in both repeats. This is an evidence-extraction difference hidden by category-level agreement. The shorter variant drops the literal word "both" from the check, although the preceding context still names before/after-commit states. Its coverage and proposal specificity are therefore contestable: authored paraphrase weakening is an alternative to a scorer failure. The transformation and source interpretation need human confirmation; identical ordinal outputs alone do not establish stable diagnostic feedback. Inspect the actual judgment (historical reference: `runs/p2-t185v3-r1/answer.json`).

## Independent checks and their limits

The native custody replay checks actual app-server events, exact frozen prompts, model alias and effort, strict admission, IDs/order, source binding, reserved-case exposure and actor closure. It is separate from semantic grading. The independent E3 and A7 source reviews preserve ambiguities and inspect decisive predicates and evidence references. Neither kind of AI review establishes a human baseline.

The main metrics are independently recomputed from exact native raw answers before comparison with the root summary. See metric cross-check (historical reference: `analysis/metric-crosscheck.json`), native replay (historical reference: `analysis/native-custody.json`), E3 review (historical reference: `analysis/e3-diagnostic-review.md`) and A7 review (historical reference: `analysis/a7-diagnostic-review.md`).

## What remains deliberately pending

Two independently ordered packs contain 30 new cases and 24 neutral pair comparisons. Individual ratings come before pair judgments. They contain no author/AI suggested scores, and no native Sol assessment of those cases is released. Zero completed human exports have been received. Expertise and independence will be self-attested and need provenance; the browser does not authenticate them.

Human review must test both the proposed categories and the semantic relations themselves, retaining alternative readings and disagreement. Importing future labels does not automatically launch assessment or override the user instruction to keep validation pending. The current UI lets reviewers edit individual labels after pair review unlocks and does not export an immutable initial snapshot or revision history. The accompanying procedure therefore requires preserving a separate 30-case draft before opening pairs. That draft is evidence of the initial labels, not a completed review or validation release.

## Interpretation boundaries

- These are known, previously exposed families, not untouched generalization cases.
- Six families, dependent variants and two repeats do not estimate population reliability. Matching repeat indices across variants does not couple the model randomness.
- Equivalence and category-change relations are authored predicates with independent AI QA; the translation from wording to predicate still needs human review.
- Agreement with an AI/authored allowed set is operational reference agreement, not human accuracy.
- Tools were available in ordinary offline Linux actors; tool availability and actual tool use are reported separately.
- This does not validate three-answer hiring, stable traits, authorship, cooperation in practice, long-horizon coding or job-performance prediction.
- It applies established behavioral-testing methods and makes no global novelty or first-place claim.

The current delivery completes the registered automated diagnostic and prepares both review packs. It leaves the wider human and hiring-validation program unvalidated, with human work explicitly deferred.
