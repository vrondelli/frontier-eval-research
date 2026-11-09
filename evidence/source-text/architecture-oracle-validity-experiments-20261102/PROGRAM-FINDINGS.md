> Archived source excerpt. Original location: `architecture-oracle-validity-experiments-20261102/PROGRAM-FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# What our architecture and maintenance experiments actually showed

We tested whether a structural warning earns its penalty by predicting a harder future change, and whether fixing that warning pays back. Those are separate questions. A detector can correctly count duplicated code or direct database access without establishing the cost of keeping it.

## The experiment, in ordinary terms

We began with three different mechanisms in one commerce application: shared pricing rules, delivery storage access and stored receipt formats. Each starting version passed the same applicable behavior checks. Sol used normal editing and testing tools. Independent owner checks judged the requested change and preservation of earlier behavior; the warning itself was excluded from the success gate.

The primary screen made 54 fresh attempts across those mechanisms. All 54 passed. A further 24 attempts used three new delivery-selector requests, and all passed. The direct-storage design was faster on average for two fresh requests; the port adapter was faster for the third. This gives no stable general architecture ranking. Repeated calls measure variability in this artifact; they are not independent repositories or human participants.

!Fresh-case attempt times (historical reference: `fresh-cases.png`)

The initial read-only-host F01 batch remains separate: 17/18 passed. One model reported a read-only policy, supplied a correct patch and made no disk edit; its commands did not show an actual write-denial error. We retained the result and tested the corrected workspace configuration separately. Calling that an architecture failure would confuse the harness with the software.

## Paying for a repair changed the answer

We assigned 24 three-change trajectories to repair-first or direct maintenance. Repair-first includes the actual repair, its finite admission gate and a fresh maintainer handoff. All 12 repairs were admitted; all 24 full chains and all 72 release checkpoints passed.

Repair-first spent 48.7% more native task time and 35.5% more processed tokens in aggregate. Its mean time was higher for every mechanism. It did not demonstrate average payback over these next three changes. This measures a policy bundle, including generated tests and documentation, in one lineage; it is not a claim that every refactor loses value or that a longer horizon would do the same. Processed tokens include cached input and are not billed dollars.

!Actual direct and repair-first costs (historical reference: `repair-costs.png`)

We separately crossed two saved implementations with their generated test suites. All eight replays passed. A roughly 3-second versus 79–82-second difference followed the suite on either implementation. Coverage and execution style changed together. That warns against attributing all elapsed time to architecture, while recognizing that more thorough testing can be worthwhile.

## Could initial structure predict work in other repositories?

The simple baseline uses source size, public-request length and an existing-operation versus other-request flag. The augmented version adds three custom measurements: a high percentile of per-function branch counts, exact AST function-body clone share and the fraction of modules in lexical import cycles. These are measurements, not standardized quality grades. Whole-repository counts can miss the particular neighborhood a future change needs to touch; unresolved dynamic imports and type-only lexical edges also limit interpretation.

All 48 registered attempts reached a terminal state across twelve public Python repositories. Four repositories were held out for the final test. Models used only initial source and public-request features and were frozen before held-out calls. The two targets are processed tokens and native task-window seconds; neither is the unknown cost to eventual correctness.

One test attempt ended with an explicit provider-capacity error. Its 357.7 native seconds and 502,524 processed tokens remain in the registered-spending account (historical reference: `OPERATIONAL-ACCOUNTING.json`), with no replacement run. It is operationally unavailable, excluded from predictive losses and not counted as a witnessed software failure. Packaging therefore contributes three eligible observations; the other test repositories contribute four each. See the raw-event classification (historical reference: `R3-OPERATIONAL-EXCLUSION.json`).

For total_tokens, baseline mean absolute log error was 0.631, versus 0.590 after adding structural features. The difference was +0.041 (positive favors augmentation).

For task_window_seconds, baseline mean absolute log error was 0.509, versus 0.598 after adding structural features. The difference was -0.089 (positive favors augmentation).

Both calibration repositories favored the simple baseline on both expenditure targets. The registered forecasters were kept unchanged; those diagnostic outcomes were not used to tune coefficients or choose a different feature set.

The raw-oracle test Brier loss was 0.0066 for the baseline and 0.0055 for the structural model. These are reproducible raw-label calculations, not evidence of a valid success predictor: its only development failures came from the disputed Jinja exception check. No forecast was silently refitted.

The eligible held-out outcomes contain only one class. Brier loss still records probability error on those outcomes; success-versus-failure ranking and average precision are not estimable in this test set.

| Partition | Assigned | Eligible | Raw-oracle passes |
| --- | --- | --- | --- |
| calibration | 8 | 8 | 8 |
| development | 24 | 24 | 22 |
| test | 16 | 15 | 15 |

!Held-out forecast differences (historical reference: `transfer-forecast.png`)

Lower forecast error is better. The registered worthwhile improvement for processed-token forecasts is 0.10 in mean absolute log1p error. A point estimate above that margin would still need adequate independent-lineage precision for a confirmatory claim.

Four held-out lineages are a descriptive pilot, not adequate evidence for a repository-population predictor. Public-source familiarity, one model/runtime, a Python convenience sample and shared-host timing remain limitations. The registered precision plan distinguishes this pilot from a future confirmatory study.

## The judge also needed to be tested

Two Jinja submissions passed the requested sorting cases and original regression suite but failed a private demand for ValueError. They raised the library's normal FilterArgumentError instead; the public request did not specify that class. A separate read-only replay changed only that exception allowance, and both submissions passed. Original outcomes, coefficients and prediction timestamps are preserved. The first diagnostic launcher ran no probe because stdin was not attached; that invalid evidence is also retained and excluded.

This is a concrete oracle-validity problem. Repeatable failure alone does not establish a meaningful model weakness. The success model fitted to those two negative labels is qualified accordingly. This finding does not change the expenditure model, which retained all eligible spending.

## What this means for architectural drift and long tasks

This study does not demonstrate that long autonomous coding causes structural erosion, that every form of erosion is covered, or that we can estimate future human maintenance cost. The persistent maintenance horizon here is three releases. The multi-repository study uses independent resets, not twelve long evolving histories. Passing finite checks also does not prove architectural equivalence.

The useful result is a way to test a proposed warning against future obligations, include the real cost of a repair, compare a simple predictive baseline and audit the judge. Structural advice should carry its measured scope and challenge conditions. These results do not justify a universal architecture penalty, a human ability score or a hiring claim.

## Evidence and remaining validation

Human validation remains pending. Both independent expert packs are prepared, with raw disagreements to be retained before reconciliation. No owner decision or canonical Lab type admission is fabricated.

Reference alternatives come from the same authoring process, and some differ only in small control-flow choices. Accepting both is useful finite QA, not evidence that every reasonable implementation will pass the oracle.

Links: live program evidence (historical reference: `report.html`), all repair questions and actual answers (historical reference: `report-R2.html`), fresh questions and actual answers (historical reference: `report-R1B.html`), transfer questions and actual answers (historical reference: `r3/report.html`), oracle diagnostic (historical reference: `oracle-audit/FINDING.md`), research design and literature (historical reference: `../architecture-oracle-validity-study-20261102/report.html`), reviewer one (historical reference: `review/reviewer-1.html`), reviewer two (historical reference: `review/reviewer-2.html`), candidate record catalog (historical reference: `records/CATALOG.json`).
