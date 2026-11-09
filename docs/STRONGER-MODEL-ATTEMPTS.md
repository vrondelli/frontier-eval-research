# Stronger-model comparisons: every final slot

These are separate experiments. The original-five ledger retains all 14 started slots, including two interrupted instrument-unknown attempts. The verification-repair matrix retains all 30 attempts. Neither table estimates general reliability.

## Original tasks and selected payroll recurrence

| Arm | Model | Task | Trial | Outcome | Recorded checks |
|---|---|---|---|---|---|
| coding | gpt-6-astra | T02-field-evidence | 1 | pass | 8/8 |
| coding | gpt-6.1-sol | T02-field-evidence | 1 | pass | 8/8 |
| coding | gpt-6-astra | T03-payroll-sdk | 1 | pass | 26/26 |
| coding | gpt-6.1-sol | T03-payroll-sdk | 1 | pass | 26/26 |
| coding | gpt-6.1-sol | T01-warehouse-numeric | 1 | pass | 15/15 |
| coding | gpt-6-astra | T01-warehouse-numeric | 1 | pass | 15/15 |
| coding | gpt-6-astra | T04-query-optimizer | 1 | pass | 41/41 |
| coding | gpt-6.1-sol | T04-query-optimizer | 1 | pass | 41/41 |
| diagnostic | gpt-6-astra | T05-diagnostic-choice | 1 | pass | Not applicable/Not applicable |
| diagnostic | gpt-6.1-sol | T05-diagnostic-choice | 1 | pass | Not applicable/Not applicable |
| prior-contract-replication | gpt-6.1-sol | T03-payroll-sdk | 1 | instrument_unknown | Not applicable/Not applicable |
| prior-contract-replication | gpt-6.1-sol | T03-payroll-sdk | 2 | instrument_unknown | Not applicable/Not applicable |
| prior-contract-transport-recovery | gpt-6.1-sol | T03-payroll-sdk | 1 | goal_failure | 26/26 |
| prior-contract-transport-recovery | gpt-6.1-sol | T03-payroll-sdk | 2 | pass | 26/26 |

The initial ten pass. The additional completed payroll pair contains one valid-input failure and one pass even though both pass all original cases. Interrupted transport slots remain unknown. [Full report](../evidence/source-text/original-five-rerun-20261108/REPORT.md).

## Explicit verification repair

| Model | Task | Trial | Outcome | Decisions correct / cases |
|---|---|---|---|---|
| gpt-6-astra | T01-numeric | 1 | pass | 58/58 |
| gpt-6-astra | T01-numeric | 2 | pass | 58/58 |
| gpt-6-astra | T01-numeric | 3 | pass | 58/58 |
| gpt-6-astra | T02-quotes | 1 | pass | 55/55 |
| gpt-6-astra | T02-quotes | 2 | pass | 55/55 |
| gpt-6-astra | T02-quotes | 3 | pass | 55/55 |
| gpt-6-astra | T03-work-receipts | 1 | pass | 53/53 |
| gpt-6-astra | T03-work-receipts | 2 | pass | 53/53 |
| gpt-6-astra | T03-work-receipts | 3 | pass | 53/53 |
| gpt-6-astra | T04-isolation | 1 | pass | 58/58 |
| gpt-6-astra | T04-isolation | 2 | pass | 58/58 |
| gpt-6-astra | T04-isolation | 3 | pass | 58/58 |
| gpt-6-astra | T05-dependency | 1 | pass | 77/77 |
| gpt-6-astra | T05-dependency | 2 | pass | 77/77 |
| gpt-6-astra | T05-dependency | 3 | pass | 77/77 |
| gpt-6.1-sol | T01-numeric | 1 | pass | 58/58 |
| gpt-6.1-sol | T01-numeric | 2 | pass | 58/58 |
| gpt-6.1-sol | T01-numeric | 3 | pass | 58/58 |
| gpt-6.1-sol | T02-quotes | 1 | pass | 55/55 |
| gpt-6.1-sol | T02-quotes | 2 | pass | 55/55 |
| gpt-6.1-sol | T02-quotes | 3 | pass | 55/55 |
| gpt-6.1-sol | T03-work-receipts | 1 | pass | 53/53 |
| gpt-6.1-sol | T03-work-receipts | 2 | pass | 53/53 |
| gpt-6.1-sol | T03-work-receipts | 3 | pass | 53/53 |
| gpt-6.1-sol | T04-isolation | 1 | pass | 58/58 |
| gpt-6.1-sol | T04-isolation | 2 | pass | 58/58 |
| gpt-6.1-sol | T04-isolation | 3 | pass | 58/58 |
| gpt-6.1-sol | T05-dependency | 1 | pass | 77/77 |
| gpt-6.1-sol | T05-dependency | 2 | pass | 77/77 |
| gpt-6.1-sol | T05-dependency | 3 | pass | 77/77 |

All 30 pass. These 1,806 decisions are repeated case decisions within attempts, not 1,806 independent tasks. Repair under an explicit contract differs from independently building a complete eval. [Source review](../evidence/source-text/verification-eval-20261108/RESULTS-REVIEW.md).
