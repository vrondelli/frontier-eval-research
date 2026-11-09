> Archived source excerpt. Original location: `readiness-study-20261031/REPORT.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Engineering evaluation: audited research observations

All150 registered valid episodes are complete and audited.
The original120-episode core,18-episode adaptive G2 extension and12 corrected E4/E5 trials remain separately reported. Six additional completed protocol-invalid observations are retained and excluded from intervention efficacy inference. Human author review and actual submission remain pending.

## What the completed controls establish

On the difficult development case, Sol and Astra each passed1/3 in fresh and1/3 in persistent no-tool conditions. Generic planning guidance produced1/3 for Sol and0/3 for Astra. Offered computation with an explicit first-use request produced3/3 for each model, with19 actual tool calls and no tool errors. This concerns the entire intervention setup, including resources and instructions; it is not a universal remedy or a standalone causal estimate for computation.
Persistent threads did not remove the difficult-case failures in these observations. Other-case changes ran in both directions. Development-exposed controls are not holdouts; three trials per cell give wide uncertainty and no broad model ranking.

## Every audited task and condition

### h1-context

Observed 24/24 records; audited 24; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | fresh | probe-candidate-0 | 3/3 | {"pass": 3} |
| gpt-6-astra | fresh | probe-candidate-19 | 1/3 | {"fail": 2, "pass": 1} |
| gpt-6-astra | persistent | probe-candidate-0 | 2/3 | {"fail": 1, "pass": 2} |
| gpt-6-astra | persistent | probe-candidate-19 | 1/3 | {"fail": 2, "pass": 1} |
| gpt-6.1-sol | fresh | probe-candidate-0 | 2/3 | {"fail": 1, "pass": 2} |
| gpt-6.1-sol | fresh | probe-candidate-19 | 1/3 | {"fail": 2, "pass": 1} |
| gpt-6.1-sol | persistent | probe-candidate-0 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | probe-candidate-19 | 1/3 | {"fail": 2, "pass": 1} |

Source results (historical reference: `h1-context/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### h2b-interventions

Observed 12/12 records; audited 12; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | compute | probe-candidate-19 | 3/3 | {"pass": 3} |
| gpt-6-astra | scaffold | probe-candidate-19 | 0/3 | {"fail": 3} |
| gpt-6.1-sol | compute | probe-candidate-19 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | scaffold | probe-candidate-19 | 1/3 | {"fail": 2, "pass": 1} |

Source results (historical reference: `h2b-interventions/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### g1-fresh

Observed 36/36 records; audited 36; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | persistent | G01 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | G02 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | G03 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | G04 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | G05 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | G06 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | G01 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | G02 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | G03 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | G04 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | G05 | 2/3 | {"fail": 1, "pass": 2} |
| gpt-6.1-sol | persistent | G06 | 3/3 | {"pass": 3} |

Source results (historical reference: `g1-fresh/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### p1-operational

Observed 18/18 records; audited 18; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | software | O1 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | O2 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | O3 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | O1 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | O2 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | O3 | 3/3 | {"pass": 3} |

Source results (historical reference: `p1-operational/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### c1-software-controls

Observed 30/30 records; audited 30; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | software | E1 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | E2 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | E3 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | E4 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | E5 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E1 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E2 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E3 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E4 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E5 | 3/3 | {"pass": 3} |

Source results (historical reference: `c1-software-controls/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### g2-fragility

Observed 18/18 records; audited 18; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | persistent | F01 | 3/3 | {"pass": 3} |
| gpt-6-astra | persistent | F02 | 1/3 | {"fail": 2, "pass": 1} |
| gpt-6-astra | persistent | F03 | 1/3 | {"fail": 2, "pass": 1} |
| gpt-6.1-sol | persistent | F01 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | persistent | F02 | 2/3 | {"fail": 1, "pass": 2} |
| gpt-6.1-sol | persistent | F03 | 2/3 | {"fail": 1, "pass": 2} |

Source results (historical reference: `g2-fragility/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

### c2-cleanup-controls

Observed 12/12 records; audited 12; complete and audited: True.

| Model | Condition | Case/task | Passes / observed | All statuses |
| --- | --- | --- | ---: | --- |
| gpt-6-astra | software | E4 | 3/3 | {"pass": 3} |
| gpt-6-astra | software | E5 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E4 | 3/3 | {"pass": 3} |
| gpt-6.1-sol | software | E5 | 3/3 | {"pass": 3} |

Source results (historical reference: `c2-cleanup-controls/RESULTS.json`). Transport, wire, action-limit and execution errors are separate from completed semantic outcomes.

## Read the actual answers

Interactive full prompts, unmodified answers and effects (historical reference: `report.html`) · Fresh Sol failure with a21-leaf valid alternative (historical reference: `G1-SOL-CASE-STUDY.md`) · All constructive recovery and final counterhistory witnesses (historical reference: `RECOVERY-COUNTEREXAMPLES.json`).

The G05 Sol example tracked every possible-world set correctly, then chose a reliable test that consumed too much budget. Both oracles agree its achievable final guarantee worsened from one world to two. It ended honestly with two possibilities. This is a planning failure under the declared objective, not a fabricated false-certainty label. Passing repeats remain visible.

## Resources and reproduction

Native cumulative usage for audited valid trials: `{"cacheWriteInputTokens": 0, "cachedInputTokens": 7570944, "inputTokens": 18206826, "outputTokens": 692987, "reasoningOutputTokens": 513946, "totalTokens": 18899813}`. Cached input and reasoning output are subsets, not quantities to add to total. Include retained invalid-arm usage separately when accounting for development cost. The compatibility preflight is additionally outside benchmark performance. Subscription receipts do not supply a defensible dollar price, and model aliases do not pin served backend revisions.
Per-model block start/end times are in the evidence summary (historical reference: `EVIDENCE-SUMMARY.json`). They record observed wall time including control overhead; parallel response latencies are not summed as wall time. Clean-path/container draft checks are in the reproduction record (historical reference: `PORTABLE-DRAFT-CHECKS.json`). A final snapshot requires completed trials and a new clean extraction check.

## What remains uncertain

The finite diagnostic game is not production debugging. Operational file/SQLite fixtures establish their stated synthetic effects, not production transfer. E1/E2 test finite schedules and a process kill, not every interleaving, power loss or storage-device failure. All-pass tasks remain controls and are not redesigned after seeing their answers. Task selection, practitioner relevance and explanation quality require Vladimir's actual review.
G2 is an adaptive cohort selected by an objective structural difficulty filter after G1 had started; it is not the same sampling distribution or an independent preregistration of the original hypothesis. No G2 model answer determines which G2 case is retained.

Interpretation rules (historical reference: `INTERPRETATION-RULES.md`) · Guide rubric (historical reference: `RUBRIC-COVERAGE.md`) · Prior work (historical reference: `ORIGINALITY-AND-METHODS.md`) · Eight practical task reviews (historical reference: `author-review.html`) · D1 review supplement (historical reference: `DIAGNOSTIC-AUTHOR-REVIEW.md`).

## Separate saved-code reproduction

{"all_check_maps_match": true, "all_statuses_match": true, "authority_effect": "none", "new_model_calls": 0, "reexecuted_answers": 12}

All saved E1/E2 reexecutions (historical reference: `service-reproduction/RESULTS.json`) are new Docker executions, not replacements for original trials. Their per-answer status and check-map comparisons remain visible even if they differ. No new model calls were made.

## Source issues still needing a new version

Original E4 retains legacy batch wording; original E5 can mutate a retained historical-view object through a shared reference. Their native prompts and primary results remain frozen. Corrected source and a separate12-episode retest are recorded in C2; the current review packet uses that corrected version. Passing outputs alone do not fix a source issue, and actual human review is still pending.

E4 wording review (historical reference: `E4-WORDING-REVIEW.json`) · E5 historical-view review (historical reference: `E5-STAGING-REVIEW.json`) · Offline audit ordering correction (historical reference: `C1-AUDIT-ORDERING-NOTE.md`).

