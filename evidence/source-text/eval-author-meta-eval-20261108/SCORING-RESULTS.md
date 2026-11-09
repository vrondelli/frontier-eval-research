> Archived source excerpt. Original location: `eval-author-meta-eval-20261108/SCORING-RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Executed scored meta-eval results

This is a live post-hoc replay of existing GPT-created eval packages, not a receipt-only score importer. All scores refer to finite registered checks. Human semantic and domain-wide qualification remain pending.

- 31 original records retained: 19 completed eval-authoring outputs, seven timeouts, one unknown native completion and four supplementary audit outputs.
- 114 native check jobs executed against the completed outputs.
- 19 scoring/oracle/runtime unit tests passed.
- Calibration: two good eval packages and ten broken variants detected as expected, plus three independent domain-control checks.
- Original subject artifacts remain unchanged; no new model calls.

## Main observations

Five completed H1 outputs reproduce the hidden-status-word rejection. Three completed Astra H6 outputs falsely accept the known faulty CLI. The seed and clean H6 outputs also reject a licensed equivalent-zero output. These overlap within eight author outputs, not ten independent failed trials.

The integrated replay additionally observed an intermittent native worker-protocol rejection of the accepted-status correct control in H1 budget draw3. One original failure plus one failure and two passes in three further identical Linux replays are preserved. This is an execution-reliability observation in an already-defective output, with human attribution review pending; not four new author attempts. The first three follow-up invocations used an unavailable Windows backend and are explicitly excluded from executed-repeat counts.

No number of fully qualified passes is established. Passing finite families and missing whole-package evidence remain separate. No pooled population failure rate is claimed.

| Saved output | Score interval /100 | Verdict |
|---|---:|---|
| initial_screen/gpt-6.1-sol/H1 | 57.50-82.50 | counterexample_reproduced_review_pending |
| initial_screen/gpt-6.1-sol/H2 | 10.00-100.00 | not_qualified |
| initial_screen/gpt-6-astra/H2 | 10.00-100.00 | not_qualified |
| initial_screen/gpt-6.1-sol/H3 | 12.50-100.00 | not_qualified |
| initial_screen/gpt-6-astra/H3 | 15.00-100.00 | not_qualified |
| initial_screen/gpt-6.1-sol/H4 | 45.00-100.00 | not_qualified |
| initial_screen/gpt-6-astra/H4 | 42.50-100.00 | not_qualified |
| initial_screen/gpt-6.1-sol/H6 | 58.50-100.00 | not_qualified |
| initial_screen/gpt-6-astra/H6 | 37.50-80.00 | counterexample_reproduced_review_pending |
| initial_screen/gpt-6.1-sol/H7 | 67.50-100.00 | not_qualified |
| initial_screen/gpt-6-astra/H7 | 67.50-100.00 | not_qualified |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw2 | 57.16-100.00 | not_qualified |
| H6_same_condition_confirmation/gpt-6-astra/H6/draw3 | 47.50-90.00 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw1 | 42.50-82.50 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw2 | 57.50-82.50 | counterexample_reproduced_review_pending |
| H1_budget_diagnostic/gpt-6.1-sol/H1/draw3 | 42.50-72.50 | counterexample_reproduced_review_pending |
| selected_hit_clean_staging/gpt-6.1-sol/H1 | 57.50-82.50 | counterexample_reproduced_review_pending |
| selected_hit_clean_staging/gpt-6-astra/H6 | 37.50-80.00 | counterexample_reproduced_review_pending |
| selected_hit_coached_staging/gpt-6.1-sol/H1 | 67.50-100.00 | not_qualified |

Intervals add unresolved weights to supported points; they are not confidence intervals or comparative ranks. The same saved artifact can vary on operational checks. Strong literal/numeric counterexamples and qualified domain expectations are reported separately from that variation.

Full execution report (historical reference: `grades/scored-v2-final/REPORT.md`), machine-readable scores (historical reference: `grades/scored-v2-final/REPORT.json`), calibration (historical reference: `grades/meta-eval-final-calibration/QUALIFICATION.json`), protocol replay audit (historical reference: `grades/scored-v2-flakiness-audit/SUMMARY.json`), run instructions (historical reference: `META-EVAL.md`).
