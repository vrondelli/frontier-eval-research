# How the research developed

The project began with a question: could unusual reasoning, planning and software tasks expose consequential failures in capable AI agents? It became a second question: could we trust the tests used to answer the first?

## 1. Build tasks before claiming a weakness

The first ten-task benchmark covered reasoning, planning, creativity and engineering. Three model aliases produced 30 episodes and 48 turns without answering tools. Review separated the raw failures: three allowance-service failures depended on an undocumented success word, while a Terra queue-equivalence answer really was wrong.

The successor made the status contract explicit and changed some creative tasks. All 30 attempts passed. Terra's queue task retained the same visible prompt and schema and succeeded in a fresh draw. Some non-recurrence was a genuine new success.

[Original campaign](campaigns/frontier-run-2026-10-31.md) · [Successor](campaigns/frontier-run-v2-2026-10-31.md).

## 2. Distinguish live planning from producing a search program

Adaptive diagnostics made the agent commit to actions under a budget. Sol and Astra sometimes tracked the correct possible-world set but chose a probe that destroyed a feasible winning continuation. Direct scheduling also exposed legal but suboptimal Terra plans.

A later ordinary-tool retest passed 24/24, with actual Python use in all 24. Computation helped under the changed conditions; it does not make the original no-tool failures imaginary.

[Planning study](campaigns/readiness-study-20261031.md) · [Tool-enabled retest](campaigns/submission-failure-audit-20261101.md).

## 3. Search across engineering, judgment and governance

Other campaigns tested rating invariance, adversarial criteria, successive code changes, architectural maintenance, governance and coordinators. Many small explicit tasks passed. Rating variability did not establish a validated scoring construct. Historical governance traces showed real cost and repeated tool errors, while short recreations often changed the authority boundary or missed the full process.

Architecture work exposed a research-side defect: the first custody audit found 156 snapshots for 228 turns, missing 72 stored differently. The corrected audit enforced 228/228. A green audit was insufficient when input discovery was incomplete.

[All campaigns](CAMPAIGNS.md) · [Instrument lessons](INSTRUMENT-LESSONS.md).

## 4. Expand the search, then audit the summaries

The closed R1-R10 cut has 67 protocol rows and 295 counted model episodes, predominantly Luna. Several families passed their finite checks. Lying-helper errors nevertheless recur across five cuts: 1/4, 1/6, 1/16, 3/24 and 2/12. These are separate denominators.

“No promoted hit” often meant a recurrence threshold was missed, not that the product was correct. R11-R13 widened the search to lifecycle, authorization, reporting, stale state, scope and numeric semantics. Some frozen endpoints stayed zero while broader review found errors or inadequate exposure.

[All 67 rows](ROUNDS-01-10.md) · [Later cohorts](LATER-ROUNDS.md) · [151 design locations](PROTOCOLS.md).

## 5. Investigate whether the tests were being fooled

An audit candidate executed 180 query comparisons while reporting 30 and passed the original 41 checks. The grader observed a declared plan, not all work performed.

That did not prove actual models exploited it. The 16 inspected stronger-model implementations genuinely reduced work on the reviewed paths. A private-oracle path was also readable during scoring, without proof a subject used it. A vulnerable evaluator and observed cheating are different claims.

## 6. Revisit original tasks on stronger models

Astra/Sol query comparisons passed. Both warehouse pilots passed the historical zero witness, so conditional replication correctly launched zero calls. Explicit verifier repair passed 30/30. The initial original-five comparison passed all ten tasks.

A broader source-licensed payroll probe found a Sol failure: a five-kilobyte spelling of one reached Python's integer-conversion limit. The follow-up retained two interrupted instrument-unknown slots and two completed recovery repetitions. One repetition failed; the other passed. This is specific fresh recurrence, not a universal frontier limitation.

[Payroll case](CASE-STUDIES.md) · [All 14 started slots](../evidence/ledgers/original-five-rerun-20261108/RESULTS.json).

## 7. Evaluate the evaluator author

The final direction made the model-created eval the object under test. Outer checks challenged delivered graders, references, task exposure, controls and reports.

Of 31 attempts, 19 completed eval-authoring packages received scored checks; four audit outputs stayed supplementary, seven attempts timed out, and one completion remained unknown. The meta-eval ran 114 native check jobs. Five H1 packages had an undisclosed success-word requirement; three H6 packages accepted a faulty CLI, and two also rejected legal equivalent output.

The software was calibrated and clean-replayed. Human semantic qualification remains incomplete. The result is reproducible software and concrete evidence alongside explicit unanswered questions.

[Final scores](META-EVAL-SCORES.md) · [Conclusions](CONCLUSIONS.md).
