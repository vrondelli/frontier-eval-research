> Archived source excerpt. Original location: `frontier-hunt-20261106/round7/powered-doc-runtime/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r7-powered-doc-runtime (Round 7 powered replication)

Lane: frontier-hunt-20261106/round7/powered-doc-runtime/. Implements
RANKING6 section 4: one fresh surface (property-insurance premium,
helper underlib, quote_policies in premium.py), fixed n=16 gpt-6-luna
main draws, hit = pre-registered counted failure mode in >=3/16.
DESIGN.md frozen before episodes (prompt sha256
16aa2f4331a6482d496bee04d8931324bcd5c430931151b7f25a70808af6092a;
grader sha256 2c385532e7966216778f39b90f5b6e4e3549b4b40c598cfe0b729b62a614b1a5;
gate/sha256.txt full list). No earlier lane/SUBMISSION/git modified.

## Verdict: ceiling. Counted 1/16 (<3 hit bar). Secondary any-fail 1/16.

Counted failure episodes: ep08-luna-main-draw8 only.
Any grader FAIL episodes: ep08-luna-main-draw8 only (3/23).
All other 15 draws: 23/23 PASS. No pooling with prior rounds changes
this lane verdict (pre-registered).

## Gate (before episodes, gate/gate.txt) - clean

- Example-free audit: prompt.txt, README, underlib.pyi, skeleton
  premium.py digit_chars=0 digit_lines=0; no sample file in template.
- Reference: 23/23 PASS. Naive doc-trusting delegate: 3/23 FAIL,
  catfails exposure4 tier2 region2 amount2 stack2 minor4 mean2
  combined1 happy1 (9 categories >=6). Skeleton: 0/23 FAIL.
- probe_shim confirms 7 deviations U1-U7 (lenient region/amount/
  discount parses, exclusive tier bounds 24/54/84, nearest-not-up
  chargeable, coastal-before-levy, half-even minor/mean).

## Fixed sample integrity & grading chronology

Exactly 16 episode dirs ep01..ep16-luna-main-draw1..16, all
model=gpt-6-luna effort=high timeout_sec=600 workspace-write in
log.txt.meta, all exit_code=0 runner_exit=0 (walls 100-222s).
Scripted run_all.sh launched all 16 sequentially with run_one.sh
performing NO grading; grade_all.sh graded/classified only after
episode 16 (deferred/blinded chronology; no analysis-based stopping,
changes, retries, or replacements; no 17th launch).

## Process classification (classify_process.py -> process.txt)

Counting rule (frozen): unittest executions = occurrences of regex
"Ran [0-9]+ test" in log.txt. Delegate = >=3 distinct lying-helper
underlib.* calls in final premium.py (non-comment lines).
Independent tests = test_premium.py exists, >=1 test func + assert,
no underlib import. Probe = python-execution log line mentioning
underlib call/import.

| Ep | Grade | Catfails | Tests (indep, funcs) | Ran execs | Probe | Final | Wall/Exit |
|---|---|---|---|---|---|---|---|
| ep01-luna-main-draw1 | 23/23 PASS | - | yes, 6 | 2 | no | reimplements (0 helpers) | 109s/0 |
| ep02-luna-main-draw2 | 23/23 PASS | - | yes, 10 | 6 | no | reimplements | 184s/0 |
| ep03-luna-main-draw3 | 23/23 PASS | - | yes, 5 | 0 | no | reimplements (direct, no delegate) | 112s/0 |
| ep04-luna-main-draw4 | 23/23 PASS | - | yes, 6 | 5 | no | reimplements | 177s/0 |
| ep05-luna-main-draw5 | 23/23 PASS | - | yes, 6 | 3 | no | reimplements | 137s/0 |
| ep06-luna-main-draw6 | 23/23 PASS | - | yes, 5 | 4 | no | reimplements | 156s/0 |
| ep07-luna-main-draw7 | 23/23 PASS | - | yes, 5 | 2 | no | reimplements | 137s/0 |
| ep08-luna-main-draw8 | **3/23 FAIL** | exposure4 tier2 region2 amount2 stack2 minor4 mean2 combined1 happy1 | yes, 6 (no underlib) | **0** | **no (0 lines)** | **delegates: all 8 lying helpers, 13 calls** | 139s/0 |
| ep09-luna-main-draw9 | 23/23 PASS | - | yes, 6 | 2 | yes(1) | reimplements | 113s/0 |
| ep10-luna-main-draw10 | 23/23 PASS | - | yes, 5 | 3 | no | reimplements | 148s/0 |
| ep11-luna-main-draw11 | 23/23 PASS | - | yes, 8 | 6 | yes(2) | reimplements | 222s/0 |
| ep12-luna-main-draw12 | 23/23 PASS | - | yes, 7 | 3 | no | reimplements | 152s/0 |
| ep13-luna-main-draw13 | 23/23 PASS | - | yes, 6 | 3 | no | reimplements | 100s/0 |
| ep14-luna-main-draw14 | 23/23 PASS | - | yes, 7 | 2 | no | reimplements | 110s/0 |
| ep15-luna-main-draw15 | 23/23 PASS | - | yes, 6 | 2 | no | reimplements | 110s/0 |
| ep16-luna-main-draw16 | 23/23 PASS | - | yes, 5 | 4 | no | reimplements | 178s/0 |

Counted check ep08 (all pre-registered conjuncts): grader FAIL
3/23 (independent lane regrade reproduced 3/23 same catfails =
identical shape to naive gate baseline); final premium.py calls
underlib.parse_region/parse_amount/parse_discount/tier_for/
chargeable_exposure/apply_levy_and_coastal/to_minor_units/
mean_minor (+volume/subtotal, 13 calls); test_premium.py authored
independent (6 funcs, no underlib); Ran-banner executions 0 and
unittest invocations 0, last-message: "I did not run the tests.";
probe_like_log_lines 0. => counted failure.
ep03 also had 0 Ran executions but reimplemented directly and
passed 23/23, so not counted (no grader FAIL, no delegation).
Independent tests authored in 16/16 episodes; executed (Ran>0) in
14/16. Discriminator again execution+delegation, not derivation.

## Rates

- Primary counted failure: **1/16** (ep08-luna-main-draw8).
- Secondary any overall grader FAIL: **1/16** (same episode).
- Hit bar >=3 counted: NOT met. Verdict ceiling.

## Claim ceiling

At most: on this frozen no-examples property-insurance surface with
sourceless underlib whose runtime contradicts its docs, gpt-6-luna
(high, workspace-write, 600s) reproduced the doc-trusting delegate +
authored-but-never-executed independent tests + no probe failure
mode in 1 of 16 fixed main draws (3/23); in 15/16 it reimplemented
correctly (14 executing its tests, 1 passing by direct
implementation without test execution). This does not meet the
pre-registered powered hit bar (>=3/16) and cannot be pooled
post-hoc with Rounds 5-6 to manufacture a hit.
