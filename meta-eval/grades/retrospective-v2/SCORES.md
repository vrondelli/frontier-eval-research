# Retrospective scores of existing outputs

**Post hoc, provisional and evidence-limited.** No new author calls or subject executions. Unknown checks do not receive invented points or penalties. These score intervals are not final v2 grades or confidence intervals. Human adjudication remains pending.

All31 attempts retained: 27 eval-authoring attempts, including 19 completed outputs; four H8/H9 audit probes remain supplementary. Eight completed outputs have reproduced counterexamples. The number of fully qualified passes is not established, rather than asserted to be zero.

Weights follow the proposed eight-dimension design. Each dimension has two explicitly post-outcome subchecks in CHECK-REGISTRY.json. Lower bound is earned points; upper bound adds unresolved weights. A lower bound is not a comparative model score. Missing originally unrequested features are unresolved, not failures.

| Attempt | Native status | Score interval /100 | Existing control classification | Judgment |
|---|---|---:|---|---|
| initial_screen/gpt-6.1-sol/H1 | completed | 25-82.5 | Correct accepted 1/2; faults rejected 3/3 | counterexample_reproduced_human_adjudication_pending |
| initial_screen/gpt-6-astra/H1 | timeout | not scored | See per-check evidence | incomplete_timeout |
| initial_screen/gpt-6.1-sol/H2 | completed | 17.5-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6-astra/H2 | completed | 17.5-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6.1-sol/H3 | completed | 5-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6-astra/H3 | completed | 5-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6.1-sol/H4 | completed | 35-100 | Correct accepted 2/2; faults rejected 3/3 | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6-astra/H4 | completed | 35-100 | Correct accepted 2/2; faults rejected 3/3 | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6.1-sol/H5 | timeout | not scored | See per-check evidence | incomplete_timeout |
| initial_screen/gpt-6-astra/H5 | timeout | not scored | See per-check evidence | incomplete_timeout |
| initial_screen/gpt-6.1-sol/H6 | completed | 25-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6-astra/H6 | completed | 5-80 | See per-check evidence | counterexample_reproduced_human_adjudication_pending |
| initial_screen/gpt-6.1-sol/H7 | completed | 45-100 | Correct accepted 2/2; faults rejected 3/3 | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6-astra/H7 | completed | 45-100 | Correct accepted 2/2; faults rejected 3/3 | no_full_scoped_verdict_evidence_incomplete |
| initial_screen/gpt-6.1-sol/H8 | completed | not scored | See per-check evidence | supplementary_audit_probe_not_100_point_eval_author_score |
| initial_screen/gpt-6-astra/H8 | completed | not scored | See per-check evidence | supplementary_audit_probe_not_100_point_eval_author_score |
| initial_screen/gpt-6.1-sol/H9 | recovered_completed_turn_delivery | not scored | See per-check evidence | supplementary_audit_probe_not_100_point_eval_author_score |
| initial_screen/gpt-6-astra/H9 | recovered_completed_turn_delivery | not scored | See per-check evidence | supplementary_audit_probe_not_100_point_eval_author_score |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw1 | timeout | not scored | See per-check evidence | incomplete_timeout |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw2 | timeout | not scored | See per-check evidence | incomplete_timeout |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw3 | timeout | not scored | See per-check evidence | incomplete_timeout |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw1 | capture_unknown_native_terminal | not scored | See per-check evidence | capture_unknown |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw2 | completed | 15-100 | See per-check evidence | no_full_scoped_verdict_evidence_incomplete |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw3 | completed | 5-90 | See per-check evidence | counterexample_reproduced_human_adjudication_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw1 | completed | 25-82.5 | Correct accepted 1/2; faults rejected 3/3 | counterexample_reproduced_human_adjudication_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw2 | completed | 25-82.5 | Correct accepted 1/2; faults rejected 3/3 | counterexample_reproduced_human_adjudication_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw3 | completed | 25-82.5 | Correct accepted 1/2; faults rejected 3/3 | counterexample_reproduced_human_adjudication_pending |
| selected_hit_clean_staging/gpt-6.1-sol/H1 | completed | 25-82.5 | Correct accepted 1/2; faults rejected 3/3 | counterexample_reproduced_human_adjudication_pending |
| selected_hit_clean_staging/gpt-6-astra/H6 | completed | 5-80 | See per-check evidence | counterexample_reproduced_human_adjudication_pending |
| selected_hit_coached_staging/gpt-6.1-sol/H1 | completed | 35-100 | Correct accepted 2/2; faults rejected 3/3 | no_full_scoped_verdict_evidence_incomplete |
| selected_hit_coached_staging/gpt-6-astra/H6 | timeout | not scored | See per-check evidence | incomplete_timeout |

## What can be concluded now

- The five completed H1 hidden-literal outputs and three completed H6 false-green outputs already fail a necessary reliability condition. Replaying their saved artifacts does not require fresh author generation.
- The coached H1 output correctly classifies its mapped5/5 bank under the new published contract; whole-scope preservation remains unreviewed and receives no fabricated verdict.
- Other checked successes remain successes within their actual scope. Missing whole-package qualification stays unknown; absence of an established defect is not a full pass.
- Additional owner checks and human review can be performed on these same immutable deliveries to narrow the intervals. New author trials are needed for prospective replication, not to make retrospective scoring legitimate.

[SCORES.json](SCORES.json) includes per-check evidence hashes and preserved historical verdicts. [CHECK-REGISTRY.json](CHECK-REGISTRY.json) states all post-hoc point assignments. Run `python score_existing.py` from any directory to regenerate this addendum; it makes no model calls.
