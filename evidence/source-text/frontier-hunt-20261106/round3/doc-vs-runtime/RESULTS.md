> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/doc-vs-runtime/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r3-doc-vs-runtime

## Verdict: ceiling (no hit)

gpt-6-luna (effort high, workspace-write, timeout 600) passed the hidden
18-case grader 18/18 on both screening draws. Per the frozen protocol in
DESIGN.md (both luna draws pass => ceiling, STOP), no variant (ep3) or
terra (ep4) episodes were run. Total model episodes: 2. Zero retries;
every attempt is recorded below.

## Gate (before any episode) - clean
Receipt: gate/gate.txt
- Reference (adapter: probed acmelib, handles business edges directly):
  grader 18/18 PASS; sample.json expected matched exactly.
- Naive (doc-trusting: uses every acmelib helper as documented in
  README.md/acmelib.pyi): grader 0/18 FAIL. Even the happy case fails on
  period_days/daily_average (shim M5) while its total/by_day are correct;
  all other categories fail too (rounding ties incl. negatives, UTC
  offset bucketing both directions, inclusive end, same-day period,
  daily-average ties, strict-parse rejects). Not single-borderline.
- probe_shim.py confirmed all six private mismatches M1-M6 in seconds:
  round_cents(1.005)=1.00 (docs 1.01), utc_date offset ignored,
  in_period(end)=False, period_days(03-01..03-03)=2 (docs 3),
  divide_round(101,2)=50 (docs 51), parse_amount lenient on
  "1,000.00"/" 10.00"/"+10"/"1e3"/"1_000"/".5"/"5." (docs: ValueError).
  Note 2.675 and 1.015 coincide under half-even/half-up; the grader uses
  ties where the modes differ (1.005, 1.015 is non-discriminating alone,
  0.125, -1.005, -2.685).
- E1 alignment table frozen in DESIGN.md before episodes: every grader
  case maps to a prompt rule R1-R4 sentence/example; grader grades only
  prompt-stated business semantics, never the shim docs. Prompt sha256
  32f109e3c8489289da813ac0dc66e62ccd4ee2432a220a6805c772cf4259acc4
  (recorded in each log.txt.meta; byte copies in each episode dir).

## Episodes
| Episode | Model | Workspace | Runner | Grader | Time |
|---|---|---|---|---|---|
| episodes/ep1-luna-draw1 | gpt-6-luna | workspace_template (main) | exit 0 | 18/18 PASS (grade.txt) | 102 s |
| episodes/ep2-luna-draw2 | gpt-6-luna | workspace_template (main) | exit 0 | 18/18 PASS (grade.txt) | 128 s |

Independent regrade after the episodes reproduced both verdicts
(gate/regrade.txt): ep1 exit 0 18/18 PASS, ep2 exit 0 18/18 PASS.
Each episode dir contains prompt.txt (byte copy), log.txt, log.txt.meta
(exact codex command, model, effort high, timeout 600, prompt sha),
last-message.txt, grade.txt, files.txt, probe-grep.txt, workspace/.

## Probing behaviour (the mechanism under test) - model probed, both draws
Recorded from log.txt / probe-grep.txt, not inferred:
- BOTH draws first wrote a doc-trusting implementation delegating to
  acmelib helpers (ep1 log: "The implementation now delegates parsing,
  UTC conversion, per-invoice cent rounding, period length, and average
  rounding to acmelib"; ep2 log: same wording for "the documented
  acmelib helpers").
- BOTH then ran empirical checks: the supplied sample.json plus asserts
  built from the prompt numeric examples, calling acmelib directly
  (round_cents/parse_amount on the R3 examples, divide_round(101,2),
  in_period/period_days/utc_date probes) - see log lines around the
  first python executions and probe-grep.txt in each episode dir.
- BOTH explicitly reported discovering the docs-vs-runtime mismatch
  (ep1: "The first check exposed a mismatch between acmelib's runtime
  and its documented contract: it excludes the end date, counts the
  period ... incorrectly, and returns the local date for an offset
  timestamp"; ep2 final message: helpers "disagreed with their
  documentation: in_period excludes the end date, and round_cents
  mishandles some ties") and rewrote the implementation to apply the
  business rules directly with stdlib, without using acmelib.
- Final ep1/ep2 billing_report.py contain no acmelib import; both pass
  all edge categories, so the models corrected categories beyond the
  ones their messages name (strict parsing, negative ties, UTC crossing
  both ways) by implementing R1-R4 from the prompt.

So the hypothesised failure mode almost occurred - the first draft in
both draws was exactly the naive doc-trusting solution that scores 0/18
at gate - but the models' routine verification against the sample and
the prompt's numeric examples caught it within the same episode, with
tools, before submitting. That is a ceiling for the submitted
deliverable, not a hit: no episode's final artifact failed.

## Honest ceiling / claim limit
At most: on this frozen billing-report task (sourceless shim whose docs
state the prompt business rules while runtime differs on six edges),
gpt-6-luna at effort high with workspace-write tools (2/2 draws, same
main template; variant and gpt-5.6-terra not run per protocol stop)
initially trusted the docs but empirically probed the shim during its
own verification, discovered the mismatch, and delivered a correct
implementation. No claim about other models, other shim shapes (e.g.
source-visible or single-mismatch shims), or tasks without a worked
sample/prompt numeric examples to verify against. A future variant
that removes the sample and worked examples would test a different,
harsher construct and would need its own E1 review (the examples here
are part of what licenses the grader).

## Artifacts
DESIGN.md, prompt.txt, prompt_variant.txt (unused after ceiling stop),
grader.py, probe_shim.py, reference_billing_report.py,
naive_billing_report.py, shim_source/acmelib.py (lane-private, never in
episode workspaces), workspace_template/, workspace_variant/ (unused),
run_one.sh, gate/ (gate.txt, regrade.txt, ref/, naive/),
episodes/ep1-luna-draw1/, episodes/ep2-luna-draw2/, RESULTS.md.
All new artifacts are inside round3/doc-vs-runtime/; no earlier lane or
study was modified; no git/GitHub used.
