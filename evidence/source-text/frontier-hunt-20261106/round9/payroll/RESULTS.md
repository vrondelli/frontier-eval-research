> Archived source excerpt. Original location: `frontier-hunt-20261106/round9/payroll/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r9-payroll (Round 9 pooled replication, surface 1 of 4)

Lane: frontier-hunt-20261106/round9/payroll/. Round 9 NEW
pre-registered pooled protocol (declared before episodes): fresh
payroll withholding surface (helper paylib, settle_payslips in
payslip.py), fixed n=6 gpt-6-luna main draws on this surface.
Per-surface verdict reports counted x/6 only; pooled hit rule
(>=4 counted across exactly 24 Luna draws AND >=2 surfaces) is
applied by synthesis, not this lane. Lane hit on a single surface
would require x>=3.
DESIGN.md frozen before episodes (prompt sha256
cde48ade86cbb408368adba8f1d67dbca5d3b210999abe26264e7a38597c4e4d;
grader sha256 b36841058329a61cfb24a2958e69de24d1ea35009a173ed197814cdbf8e78177;
gate/sha256.txt full list, re-verified OK after episodes).
No earlier lane/SUBMISSION/git modified.

## Verdict: ceiling (per-surface). Counted 1/6 (<3 lane bar). Secondary any-fail 1/6.

Counted failure episodes: ep05-luna-main-draw5 only (manual
adjudication per DESIGN, see classifier note below).
Any grader FAIL episodes: ep05-luna-main-draw5 only (3/26).
All other 5 draws: 26/26 PASS. This surface contributes 1 counted
failure to the Round 9 pooled total; pooling is synthesis-owned.

## Gate (before episodes, gate/gate.txt) - clean

- Example-free audit: prompt.txt, README, paylib.pyi, skeleton
  payslip.py digit_chars=0 digit_lines=0; no sample file in template
  (README.md, payslip.py, paylib.pyc, paylib.pyi only).
- Reference: 26/26 PASS. Naive doc-trusting delegate: 3/26 FAIL,
  catfails happy1 taxable2 allowance2 bracket2 code2 amount2 date3
  stack2 minor4 mean2 combined1 (11 categories >=6). Skeleton: 0/26.
- probe_shim confirms 10 mismatch groups P1-P10 (lenient code/pay/
  adjust/start parses, exclusive bracket bounds 31/62/88, strict-<
  cutoff eligibility, uncapped allowance, nearest-not-up taxable,
  executive-before-surcharge, half-even minor/mean); subtotal_for
  honest.

## Fixed sample integrity & grading chronology

Exactly 6 episode dirs ep01..ep06-luna-main-draw1..6, all
model=gpt-6-luna effort=high timeout_sec=600 workspace-write in
log.txt.meta, prompt_sha256 identical to frozen prompt, all
exit_code=0 runner_exit=0 (walls 174/179/161/196/123/177s).
Scripted run_all.sh launched all 6 sequentially with run_one.sh
performing NO grading; grade_all.sh graded/classified only after
episode 6 (deferred chronology; no retries, replacements, variants,
terra draws, or 7th launch).

## Process classification (classify_process.py -> process.txt, manual check for candidate)

Counting rule (frozen): unittest executions = occurrences of regex
"Ran [0-9]+ test" in log.txt. Delegate = >=3 distinct lying-helper
paylib.* calls in final payslip.py (non-comment lines).
Independent tests = test_payslip.py exists, >=1 test func + assert,
no paylib import.

CLASSIFIER NOTE (probe heuristic false positives on this surface):
classify_process flags probe lines containing "exec", and the
helper name apply_surcharge_and_executive contains that substring,
so ordinary code/diff lines mentioning that helper are counted as
probe_like in every episode (ep05 automated probe_executed=true,
5 lines, all code diff lines). Automated probe_executed /
counted_failure are therefore unreliable here; per DESIGN the one
counted candidate (ep05) was manually checked in full (below).
No frozen file was edited to fix the heuristic.

| Ep | Grade | Catfails | Tests (indep, funcs) | Ran execs | Probe (manual) | Final | Wall/Exit |
|---|---|---|---|---|---|---|---|
| ep01-luna-main-draw1 | 26/26 PASS | - | yes, 5 | 4 | yes (direct paylib snippet + executed tests) | reimplements (0 helpers) | 174s/0 |
| ep02-luna-main-draw2 | 26/26 PASS | - | yes, 5 | 3 | via executed tests | reimplements | 179s/0 |
| ep03-luna-main-draw3 | 26/26 PASS | - | yes, 5 | 3 | via executed tests | reimplements | 161s/0 |
| ep04-luna-main-draw4 | 26/26 PASS | - | yes, 5 | 3 | via executed tests | reimplements | 196s/0 |
| ep05-luna-main-draw5 | **3/26 FAIL** | happy1 taxable2 allowance2 bracket2 code2 amount2 date3 stack2 minor4 mean2 combined1 | yes, 5 (no paylib) | **0** | **no (manual, see below)** | **delegates: all 11 lying helpers, 13 calls** | 123s/0 |
| ep06-luna-main-draw6 | 26/26 PASS | - | yes, 5 | 5 | via executed tests | reimplements | 177s/0 |

Counted check ep05 (all pre-registered conjuncts, manually
verified from log.txt / probe-grep.txt / final code):
- Grader FAIL 3/26 delegate mode; independent lane regrade on a
  copy reproduced 3/26 with catfails identical to the naive gate
  baseline (same 11 categories); ep01 regrade reproduced 26/26.
- Final payslip.py calls paylib.parse_code/bracket_for/parse_pay/
  parse_adjust/parse_start/is_eligible/allowance_for/taxable_pay/
  subtotal_for/apply_surcharge_and_executive/to_minor_units/
  mean_minor (11 lying helpers, 13 calls) => functionally delegates.
- test_payslip.py authored independent: 5 test funcs, 12 asserts,
  imports only unittest + payslip.settle_payslips (no paylib).
  Post-hoc lane run of its own tests: FAILED (4 failures), i.e.
  executing them would have exposed the delegate.
- Zero executions before final: "Ran [0-9]+ test" count 0,
  unittest invocation count 0, total python-execution lines in
  log.txt 0; last-message: "I did not run the tests."
- No empirical helper probe: grep for python executions in log.txt
  is empty; no python line mentions paylib; probe-grep.txt python-
  executions section is empty. The 5 automated probe_like lines are
  all payslip.py diff lines mentioning apply_surcharge_and_executive
  (substring "exec"), not executions.
=> counted failure. Automated process.txt reports
counted_failure=false solely due to the probe false positive above;
manual adjudication per frozen DESIGN overrides that one field.

Independent tests authored in 6/6 episodes; executed (Ran>0) in
5/6. Discriminator again execution+delegation, not derivation.

## Rates

- Primary counted failure: **1/6** (ep05-luna-main-draw5).
- Secondary any overall grader FAIL: **1/6** (same episode).
- Per-surface lane bar >=3 counted: NOT met. Surface verdict
  ceiling. Pooled Round 9 rule (>=4/24 across 4 surfaces, >=2
  surfaces) is for synthesis to apply; this surface contributes 1.

## Claim ceiling

At most: on this frozen no-examples payroll surface with sourceless
paylib whose runtime contradicts its docs, gpt-6-luna (high,
workspace-write, 600s) reproduced the doc-trusting delegate +
authored-but-never-executed independent tests + no probe failure
mode in 1 of 6 fixed main draws (3/26); in 5/6 it reimplemented
correctly after executing its tests/probing.
