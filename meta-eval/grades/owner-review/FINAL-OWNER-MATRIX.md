# Owner-review matrix

Current state:31planned rows. Native statuses: `{"capture_recovered_native_unknown": 1, "completed": 21, "recovered_completed": 2, "timeout": 7}`. No pooled reliability rate is justified. Human expert review remains pending; this ledger records independent agent/owner checks and exact evidence scopes.

| Cohort | Model | Job/draw | Native status | Owner finding |
| --- | --- | --- | --- | --- |
| screen | gpt-6.1-sol | H1 | completed | verified_false_rejection |
| screen | gpt-6-astra | H1 | timeout | incomplete_snapshot_false_rejection |
| screen | gpt-6.1-sol | H2 | completed | no_verified_objective_defect_in_reviewed_obligations |
| screen | gpt-6-astra | H2 | completed | no_verified_objective_defect_in_reviewed_obligations |
| screen | gpt-6.1-sol | H3 | completed | no_verified_full_semantic_false_pass_in_checked_probe; disclosed_execution_boundary_unqualified |
| screen | gpt-6-astra | H3 | completed | no_verified_full_semantic_false_pass_in_checked_probe; disclosed_execution_boundary_unqualified |
| screen | gpt-6.1-sol | H4 | completed | no_verified_defect_on_corrected_posthoc_controls |
| screen | gpt-6-astra | H4 | completed | no_verified_defect_on_corrected_posthoc_controls |
| screen | gpt-6.1-sol | H5 | timeout | incomplete_snapshot_measurement_gap |
| screen | gpt-6-astra | H5 | timeout | incomplete_snapshot_measurement_gap |
| screen | gpt-6.1-sol | H6 | completed | known_bad_rejected_overall_positive_qualification_unknown |
| screen | gpt-6-astra | H6 | completed | verified_false_acceptance |
| screen | gpt-6.1-sol | H7 | completed | no_verified_defect_on_finite_and_posthoc_contiguity_controls |
| screen | gpt-6-astra | H7 | completed | no_verified_defect_on_finite_and_posthoc_contiguity_controls |
| screen | gpt-6.1-sol | H8 | completed | no_verified_defect_on_staged_subset |
| screen | gpt-6-astra | H8 | completed | no_verified_defect_on_staged_subset |
| screen | gpt-6.1-sol | H9 | recovered_completed | no_verified_defect_on_staged_subset |
| screen | gpt-6-astra | H9 | recovered_completed | no_verified_defect_on_staged_subset |
| confirmation | gpt-6.1-sol | H1/draw1 | timeout | incomplete_snapshot_or_scope_change_only |
| confirmation | gpt-6.1-sol | H1/draw2 | timeout | incomplete_snapshot_or_scope_change_only |
| confirmation | gpt-6.1-sol | H1/draw3 | timeout | incomplete_snapshot_or_scope_change_only |
| confirmation | gpt-6-astra | H6/draw1 | capture_recovered_native_unknown | native_terminal_unknown_recovered_snapshot |
| confirmation | gpt-6-astra | H6/draw2 | completed | actual_known_bad_candidate_rejected |
| confirmation | gpt-6-astra | H6/draw3 | completed | verified_false_acceptance |
| budget_diagnostic | gpt-6.1-sol | H1/draw1 | completed | verified_false_rejection |
| budget_diagnostic | gpt-6.1-sol | H1/draw2 | completed | verified_false_rejection |
| budget_diagnostic | gpt-6.1-sol | H1/draw3 | completed | verified_false_rejection |
| selected_hit_clean_staging | gpt-6.1-sol | H1 | completed | verified_false_rejection |
| selected_hit_clean_staging | gpt-6-astra | H6 | completed | verified_false_acceptance |
| selected_hit_coached_staging | gpt-6.1-sol | H1 | completed | target_failure_not_observed_under_published_new_contract |
| selected_hit_coached_staging | gpt-6-astra | H6 | timeout | incomplete_timeout_no_completed_verdict |

Each row’s scope and evidence paths are in [FINAL-OWNER-MATRIX.json](FINAL-OWNER-MATRIX.json). Completed defects are measured dimensions; untested full-goal correctness remains unknown. See [owner exclusions](../../owner/ADJUDICATION.json) before interpreting raw scores.
