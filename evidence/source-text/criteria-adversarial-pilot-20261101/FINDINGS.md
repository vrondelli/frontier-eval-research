> Archived source excerpt. Original location: `criteria-adversarial-pilot-20261101/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# What the attacks, repairs and fresh cases show

**The repairs made several ambiguous ratings determinate and transferred those rules to new examples. They did not demonstrate a gain in finite-claim accuracy: both versions already made zero contradicted claims in the primary fresh bank. Some repaired ordinal ratings also remained variable.**

[Interactive report: actual questions and answers](http://127.0.0.1:5187/criteria-adversarial-pilot-20261101/report.html) · Results (historical reference: `RESULTS.json`) · Every normalized claim (historical reference: `CLAIM-ACCOUNTING.json`) · Native audit (historical reference: `CUSTODY-AUDIT.json`)

## What ran

Three parallel agents constructed and cross-reviewed case banks, independently checked actual attacks and repairs, and replayed outcomes. All model inference used gpt-6.1-sol/high through the signed-in Codex app server with ordinary local tools.

The39calls comprise three attackers, three original development scorers, three original applications to generated attacks, three single repairs, three repaired attack regressions,18paired original/repaired evaluations and six focused transfer calls. No failed request or model answer was replaced; no additional repair was selected after fresh feedback. No actual applicants or recordings were used.

The original20development records and25withheld records were created and frozen before inference. Every instrument was repaired once using development evidence only. All three repaired instruments were then committed before the25case bank reached a model. Each version was evaluated three times on the same per-repeat case order in separate conversations.

A later focused extension adds12new records across four base situations, one observation per version. It was added after repair commitment and some primary results, because review exposed a coverage gap: P1's main fresh valid cases all had next checks, so they could not directly test the changed no-next-check boundary. This extension is exploratory, separately frozen and reported, not retroactively presented as the primary preregistered bank.

## Actual adversarial results

Sol proposed four attacks, not12: two for P1, one for P2 and one for P3. All attempts and qualifications were preserved. Applying the original instruments produced no false substantive judgment on these attacks.

| Attack | Original observed application | Repaired observed application | Supported interpretation |
| --- | --- | --- | --- |
| P1: valid safety argument without a candidate next check; assessor supplies one separately | E3=U; identifies anchor/example conflict; technical content correct | E3=2; no assessor check credited as candidate planning | Explicitly revised usefulness boundary resolves one observed applicability gap. |
| P1: familiarity but no frozen repertoire | E4=U; novelty unverified | E4=U; novelty unverified | Attack unsuccessful; missing comparison evidence correctly stays unresolved. |
| P2: familiar bridge puzzle with a complete17minute analysis | A1=unknown despite correctly verified solution | A1=3; solution still correct; novelty unverified | Changed target explicitly credits displayed analysis rather than treating familiarity as proof of no analysis. |
| P3: omitted transaction acceptance predicate | K4=1; technical status insufficient | K4=1; technical status insufficient | Attack unsuccessful; a safe predicate cannot be invented by the assessor. |

The first two ambiguity-related changes are not repairs of observed false technical claims. The scorer appropriately declined to choose a unique ordinal value under conflicting rules. Some attack contexts included attacker-supplied interpretations, so these are qualified boundary probes, not unbiased estimates of unprompted error. The original bridge counterfactual and P1's mentioned record pair were not separate blinded observations; the focused extension provides a concrete paired example for familiarity.

Independent attack reviews: P1 (historical reference: `analysis/p1-attack-review.md`), P2 (historical reference: `analysis/p2-attack-review.md`), P3 (historical reference: `analysis/p3-attack-review.md`).

## What changed in the instruments

- **P1,16text edits:** E3level2now requires a feasible route and material limitation; a future check is reserved for level3alongside comparison/adoption evidence. Candidate and assessor evidence are distinguished. Familiarity cannot substitute for frozen-repertoire membership. This is a declared semantic revision.
- **P2,16text edits:** A1targets displayed analysis; recall alone remains insufficient, while familiarity does not erase visible reasoning. A5is explicitly transmission/audience adequacy, with technical falsity scored under A2. Existing novelty labels are conditional on an actual reference comparison. The communication construct narrowed, so its higher number is not an unchanged-gold accuracy gain.
- **P3,18text edits:** K9separates generic declarations from concrete partial actions. K4requires provenance for necessary predicates, and K7keeps novelty relative to a frozen comparison. It preserves the already correct insufficient response to the actual attack.

All criterion/example IDs were retained. Independent reviews found no construct deletion, case-ID lookup policy or universal-unknown strategy. Thresholds and scales remain provisional. Commitment hashes (historical reference: `REPAIRED-COMMIT.json`), P1review (historical reference: `analysis/p1-repair-review.md`), P2review (historical reference: `analysis/p2-repair-review.md`), P3review (historical reference: `analysis/p3-repair-review.md`).

## Primary fresh-bank comparison

| Instrument | Fresh records / base families | Checked content judgments per version | Original contradicted claims | Repaired contradicted claims |
| --- | --- | --- | --- | --- |
| P1 |8/4|33|0|0|
| P2 |9/4|57|0|0|
| P3 |8/4|45|0|0|

Those135judgments per version are repeated observations of fixed finite claim slots, not135independent tasks or people. Across both versions there are270such observations:264supported determinate claims and six correct identifications of insufficient novelty evidence. Positive-claim coverage is100% in every observed cell; zero error was not achieved by withholding every answer. Out-of-scope fields and non-discriminating allowlists are excluded.

These checks concern stated technical claims, explicit repertoire evidence and narrow content classifications. They are not a complete semantic audit of every sentence or a validation of the ordinal scales. Original-specific numeric anchor diagnostics are kept separate from the comparable normalized endpoint. Ambiguous mechanism-family boundaries remain reviewable rather than forced gold; no such boundary produced an actual primary error here.

**Ordinal repeatability is a separate issue.** In the primary fresh bank, P1's K129usefulness score is3,3,3under the original and2,3,2under the repair. P2's journal-case A7score likewise changes from3,3,3to2,3,2. Explanations vary about what counts as sufficient comparison/planning evidence. These are residual interpretation/calibration signals, not proof that a particular score is scientifically wrong.

P3moves in the other direction: one fresh generic-intention case receives0,0,Uoriginally and0,0,0after repair. A scorer can correctly identify the content as a generic intention while being unable to choose between overlapping numeric anchors. Content coverage and ordinal applicability must therefore remain distinct.

Ordinal repeatability (historical reference: `ORDINAL-REPEATABILITY.json`) is a post hoc descriptive analysis, not a preregistered primary endpoint or causal estimate. Case batches permit joint comparison; three repeats and changing batch order cannot establish population reliability.

Independent primary reviews: P1 (historical reference: `analysis/p1-final-review.md`), P2 (historical reference: `analysis/p2-final-review.md`), P3 (historical reference: `analysis/p3-final-review.md`).

## Focused fresh transfer

The separate exploratory extension checks the actual changed boundaries in new scheduling, jug/interlock and compute-allocation situations.

| Fresh example | Original | Repaired | Controls preserved |
| --- | --- | --- | --- |
| Feasible schedule plus material limitation, no candidate future check | E3=U | E3=2 | Adding an assessor check gives no candidate planning credit; dependency-violating schedule remains0. |
| Complete jug reasoning, no familiarity disclosure / familiarity disclosed | A1=3 / unknown | A1=3 /3 | Bare recalled target staysunknown; false interlock remains technical0and receives no innovation credit. |
| Generic cooperation statement / partial action / complete process | K9=U /1/3 | K9=0/1/3 | Resource/permission violation remains0, with technical0. No sincerity claim is made. |

The false but clearly transmitted interlock receives A5=unknownoriginally and2under the repaired transmission definition. Its technical score stays0. That change illustrates construct separation, not improved technical ability or proof that the new communication definition is scientifically preferable.

These are24scored records from12case variants across four base situations, one original/repaired call each. They support local rule transfer and control preservation. They do not establish generalization across all engineering work, robust causal familiarity effects or validated hiring measurement. P1focused review (historical reference: `analysis/p1-focused-review.md`), P2focused review (historical reference: `analysis/p2-focused-review.md`), P3focused review (historical reference: `analysis/p3-focused-review.md`).

## Implication and next decision

This workflow can expose contradictory anchors, inappropriate evidence attribution and the difference between a useful familiar solution and evidence of invention. The current repairs clarify several boundaries while preserving uncertainty where information is genuinely missing. They should remain candidate instruments until human expert calibration.

The evidence does **not** support claiming that the original or repaired systems identify the best engineers, that the repairs improved predictive hiring accuracy, or that they constitute a strong frontier-failure submission. We found applicability and repeatability issues rather than persistent false finite claims. The next useful work is adjudicating the highest-level comparison/planning anchors and testing them with independently reviewed answer pairs, rather than converting every changed score into a success metric.

## Custody and execution limits

All39native jobs pass the independent source/request/response/tool/snapshot audit, with distinct threads and no active actors remaining. The audit checks5,063bindings; scientific validity remains separate. The run has125terminal calls, no nonzero terminal exits, timeouts or truncations, and no operational/admission errors. Usage is recorded in RESULTS.json (historical reference: `RESULTS.json`); no monetary price was returned by the signed-in connection.

A reviewer briefly refreshed an initially pinned review-metadata file; the exact original bytes were restored and both the event and preserved refresh are retained in `analysis/p3-review-restoration.json` and `analysis/p3-postfreeze-review-refresh-preserved.json`. Case, criterion, prompt, grader and actor-input bytes were not changed by that event. Final phase-pin verification passes. This is recorded rather than omitted from the evidence history.

No publication, employment use or participant collection occurred. All semantic reviews here are agent analyses and finite mathematical checks; Vladimir's human expert review remains pending.
