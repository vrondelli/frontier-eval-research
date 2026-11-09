# Executed meta-evaluation

Actual native executions of saved GPT-created evals, not imported historical verdicts. Post-hoc scoring; zero model calls. Unknown checks remain unresolved. Human task/grading review is pending.

| Subject | Native status | Score interval /100 | Verdict |
|---|---|---:|---|
| initial_screen/gpt-6.1-sol/H1 | completed | 57.5-82.5 | counterexample_reproduced_review_pending |
| initial_screen/gpt-6-astra/H1 | timeout | not scored | incomplete_delivery |
| initial_screen/gpt-6.1-sol/H2 | completed | 10-100 | not_qualified |
| initial_screen/gpt-6-astra/H2 | completed | 10-100 | not_qualified |
| initial_screen/gpt-6.1-sol/H3 | completed | 12.5-100 | not_qualified |
| initial_screen/gpt-6-astra/H3 | completed | 15-100 | not_qualified |
| initial_screen/gpt-6.1-sol/H4 | completed | 45-100 | not_qualified |
| initial_screen/gpt-6-astra/H4 | completed | 42.5-100 | not_qualified |
| initial_screen/gpt-6.1-sol/H5 | timeout | not scored | incomplete_delivery |
| initial_screen/gpt-6-astra/H5 | timeout | not scored | incomplete_delivery |
| initial_screen/gpt-6.1-sol/H6 | completed | 58.5-100 | not_qualified |
| initial_screen/gpt-6-astra/H6 | completed | 37.5-80 | counterexample_reproduced_review_pending |
| initial_screen/gpt-6.1-sol/H7 | completed | 67.5-100 | not_qualified |
| initial_screen/gpt-6-astra/H7 | completed | 67.5-100 | not_qualified |
| initial_screen/gpt-6.1-sol/H8 | completed | not scored | supplementary_audit_probe |
| initial_screen/gpt-6-astra/H8 | completed | not scored | supplementary_audit_probe |
| initial_screen/gpt-6.1-sol/H9 | recovered_completed_turn_delivery | not scored | supplementary_audit_probe |
| initial_screen/gpt-6-astra/H9 | recovered_completed_turn_delivery | not scored | supplementary_audit_probe |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw1 | timeout | not scored | incomplete_delivery |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw2 | timeout | not scored | incomplete_delivery |
| H1_same_condition_confirmation/gpt-6.1-sol/H1/draw3 | timeout | not scored | incomplete_delivery |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw1 | capture_unknown_native_terminal | not scored | capture_unknown |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw2 | completed | 57.1591-100 | not_qualified |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw3 | completed | 47.5-90 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw1 | completed | 42.5-82.5 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw2 | completed | 57.5-82.5 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw3 | completed | 42.5-72.5 | counterexample_reproduced_review_pending |
| selected_hit_clean_staging/gpt-6.1-sol/H1 | completed | 57.5-82.5 | counterexample_reproduced_review_pending |
| selected_hit_clean_staging/gpt-6-astra/H6 | completed | 37.5-80 | counterexample_reproduced_review_pending |
| selected_hit_coached_staging/gpt-6.1-sol/H1 | completed | 67.5-100 | not_qualified |
| selected_hit_coached_staging/gpt-6-astra/H6 | timeout | not scored | incomplete_delivery |

Fresh native jobs: 114. Every job's command/stdout/stderr and hash-bound evidence is retained beside its subject score. Replay executions are not new author attempts.

Missing or unqualified checks are visible per subject. The scorer and runner are implemented; this does not certify full-domain oracle correctness, historical exposure isolation or pending human semantics.
