> Archived source excerpt. Original location: `frontier-hunt-20261106/round6/scheduling/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r6-surface-scheduling (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 6 replication. Folder: round6/scheduling/.
Surface: r6-surface-scheduling. Deadline: Sunday 2026-11-08.

Reads first (personally opened before building): predecessor
round5/doc-runtime-no-examples/{DESIGN.md, RESULTS.md, prompt.txt, grader.py,
gate/gate.txt, run_one.sh, episodes/ep1-luna-draw1/{grade.txt, log.txt.meta,
last-message.txt, workspace/statement.py}, shim_source/, workspace_template/},
round5/synthesis/RANKING5.md section 2.1 (a-e audit of the one real failure)
and section 4 (replication still needed: fresh domain/keys/shim mismatches,
frozen DESIGN with E1 table, reference-PASS/delegate-FAIL gate, example-free
audit, prompt-required independent-oracle test file, pre-registered process
endpoint), runner-gate/run_episode.sh.

Attribution: methodology only is adapted from round5/doc-runtime-no-examples
(example-free prose rules, sourceless lying helper, independent grader,
reference/naive/skeleton gate, process analysis). No ledgerlib/statement/
Rules A-D text, keys, seeds, or grader cases are reused: domain (shift
scheduling/payable time), helper name (rostalab), function names
(build_timesheet; utc_start_date, in_week, week_day_count, elapsed_minutes,
parse_rest, break_deduction, round_quarter, mean_rounded, overlaps), business
rules (Rules A-E below), mismatch set (M1-M9), entry keys, and all grader
cases are fresh.

Prompt shas are recorded in gate/sha256.txt at freeze (prompt.txt and
prompt_variant.txt), verified after episodes.

## Lead under replication test

Predecessor produced one E1-clean, model-attributable 0/20 failure
(gpt-6-luna ep1): with all worked examples removed, it delegated to a library
whose runtime contradicts its documentation, authored independent-oracle
tests, never executed them, and shipped. Other draws self-corrected. This
lane tests whether that mode replicates on a fresh scheduling surface with a
fixed sample (no screen/stop rule; see protocol).

## Hypothesis

With tools but without any supplied worked example, the model trusts the
documented semantics of the sourceless helper rostalab, builds
build_timesheet on top of it, and ships a delegate that fails broadly on
edge-heavy hidden cases generated directly from the prompt rules - in
particular when the independent tests it authors are never executed.

## Workspace (what the model sees)

- timesheet.py: skeleton for build_timesheet(shifts, week_start, week_end).
- README.md + rostalab.pyi: confident prose documentation of rostalab helpers
  stating semantics S, which match the prompt business rules. No worked
  numeric example: prompt files and workspace docs/skeleton contain zero
  Arabic digits (numbers are spelled out; gate-verified by grep). The "->"
  tokens in README/pyi are return-type annotations in signatures with no
  operand values (disclosed, as in predecessor).
- rostalab.pyc: sourceless compiled shim (source lane-private in
  shim_source/rostalab.py, NOT in any episode workspace).
- No sample file, no expected-output file, no grader/reference/probe in any
  workspace. Documentation/.pyi is the treatment, never graded as truth.

## Private mismatch points (docs S vs runtime S') - probe-able in seconds (probe_shim.py)

| # | Helper | Docs S (= prompt rule) | Runtime S' |
|---|---|---|---|
| M1 | utc_start_date | convert instant to UTC, then date | wall-clock .date(), offset ignored |
| M2 | in_week | inclusive of week_start AND week_end | start <= d < end (exclusive end) |
| M3 | week_day_count | distinct dates in closed interval, both endpoints counted | (end-start).days |
| M4 | elapsed_minutes | true instant elapsed whole minutes, overnight/offset honoured | wall time-of-day difference clipped at zero (date and offsets ignored) |
| M5 | parse_rest | strict digits-only grammar, ValueError otherwise | strips spaces, allows plus/underscores, parses via float (decimal/exponent accepted) |
| M6 | break_deduction | subtract rest only when elapsed exceeds six hours | always subtracts rest |
| M7 | round_quarter | nearest quarter hour, remainder eight or more up, seven or fewer down | floors to quarter hour |
| M8 | mean_rounded | nearest integer, exact midway farther from zero | Python round() on float quotient (bankers) |
| M9 | overlaps | strict instant overlap; touching does not overlap | non-strict comparison; touching counts as overlap |

Correct paths (both available): (a) derive vectors from Rules A-E, probe
rostalab, discover M1-M9, adapt/wrap; (b) ignore rostalab and implement
Rules A-E directly with stdlib. Doc-trusting path: call helpers as documented.

## E1 alignment table (FROZEN; each grader case/category -> verbatim licensing prompt sentence)

Grader: grader.py imports workspace build_timesheet, runs 23 named cases in
the episode's mode (main: shift keys tag/begin/finish/rest; variant:
code/starts/ends/pause - the only prompt difference is those quoted key names
and the corresponding nouns in Rules A, B, C, D, E), compares the exact
returned dict to an independent stdlib recomputation of Rules A-E (imports
neither rostalab nor the reference). Primary PASS = 23/23. Every expected
value is generated directly from the prompt rules below; no grader construct
relies on any worked example (none exists). Ordinary deliverable language is
quoted in the last row; the prompt does NOT add a graded "you must run
tests" requirement beyond that language, and never suggests documentation
may be inaccurate (construct preserved from predecessor).

| Grader case(s) | Prompt license (verbatim sentence) |
|---|---|
| happy_mid, empty_all_out, day_count in every case | Rule E: ""day_count": int, the number of distinct calendar dates in the closed interval from week_start to week_end, counting both endpoints as days in the week." + Rule E zero sentence: "When there are no accepted shifts, payable_minutes is the integer zero, accepted is the integer zero, per_day is the empty dict, and mean_minutes is the integer zero (day_count is still as defined above)." |
| same_day_week | Rule A inclusive sentence (below) + Rule E day_count sentence (above) |
| overnight, offset_elapsed, seconds_floor | Rule B: "The elapsed time in minutes is the true elapsed time between the begin and finish instants (honouring their offsets, including shifts that run past midnight), divided by the number of seconds in one minute and discarding any remainder of seconds." |
| utc_back_out, utc_fwd_in, utc_bucket | Rule A: "A shift belongs to the week if and only if the UTC calendar date of its begin instant is on or after week_start and on or before week_end, inclusive of both end dates." + "The UTC calendar date is obtained by converting the begin timestamp instant (honouring its Z or offset) to UTC and taking the calendar date there." + Rule E per_day: ""per_day": dict mapping each UTC calendar date (in year-month-day form) of the begin instant of at least one accepted shift to the int sum of payable minutes for accepted shifts beginning on that UTC date." |
| inclusive_end | Rule A: "...on or after week_start and on or before week_end, inclusive of both end dates." |
| break_short, break_exact_threshold | Rule C: "If the elapsed time exceeds six hours, subtract the rest value; otherwise subtract nothing, so a shift whose elapsed time is exactly six hours has nothing subtracted." |
| grace_up, grace_down | Rule C: "Then round the result to the nearest quarter of an hour: if the remainder beyond a whole quarter of an hour is seven minutes or fewer, round down to that quarter; if the remainder is eight minutes or more, round up to the next quarter." |
| strict_rest_a, strict_rest_b | Rule B: "The rest string is valid if and only if it consists of one or more ASCII digits and nothing else" + "Invalid therefore includes any string with surrounding whitespace, a leading plus sign, a decimal point, exponent notation, underscores, an empty string, or letters or any other characters." |
| rest_exceeds, nonpositive_and_toolong | Rule B: "An in-week shift is rejected when its finish instant is not after its begin instant, when its elapsed time exceeds sixteen hours, when its rest string is invalid, or when its rest value exceeds its elapsed time in minutes." |
| overlap_true, touching | Rule D: "An otherwise acceptable in-week shift is rejected when it overlaps an earlier accepted shift, where two shifts overlap if and only if each begins before the other finishes, comparing instants." + "A shift that begins exactly when an earlier accepted shift finishes does not overlap it." + "Rejected and ignored shifts never cause a later shift to be rejected under this rule." |
| mean_tie | Rule E: ""mean_minutes": int, payable_minutes divided by day_count, rounded to the nearest integer; if the exact quotient lies exactly midway between two integers, choose the integer farther from zero." |
| out_invalid_ignored | Rule B: "An out-of-week shift is ignored entirely even if it would be rejected under this rule (it is not rejected)." + Rule E "rejected": list of identifier strings of in-week rejected shifts |
| rejected order/output keys in every case | Rule E full bullet list defining exactly "payable_minutes", "accepted", "rejected" ("in input order"), "per_day" ("No other keys"), "day_count", "mean_minutes" + opening sentence "Return a dict with exactly these keys:" |
| combined | Rules A-E jointly, no new construct |
| TESTFILE metrics (secondary only, never affect OVERALL) | Deliverables paragraph: "Deliverables: the completed timesheet.py, and a new file test_timesheet.py in the workspace root containing automated tests for build_timesheet that run with the standard library unittest framework. The expected value in each test must be derived from the business rules above by independent reasoning or independent arithmetic, and must not be obtained by recording or copying output of the rostalab helpers or of your own implementation. Do not import rostalab in test_timesheet.py." |

Grader grades ONLY prompt-stated business semantics. README/docs S are never
graded as truth; they are the treatment. No judgment cells; all primary
checks are exact dict equality. Assumptions stated in prompt and honoured by
grader: timestamp shape fixed, week_end on/after week_start, shift keys as
named. Grader never tests unspecified inputs (malformed timestamps, missing
keys, non-string rest values).

## Gate (BEFORE any episode; else verdict=invalid, NO episodes)

In fresh copies of the templates under gate/:
- reference_timesheet.py (direct Rules A-E implementation) must PASS 23/23
  in BOTH main and variant grader modes.
- naive_timesheet.py (doc-trusting delegate using every rostalab helper as
  documented) must FAIL broadly (pre-registered bar: at most 8/23 pass AND
  failures in at least four categories among
  span/elapsed/utc/within/break/grace/strict/overlap/mean/combined).
- Skeleton must FAIL.
- Example-free audit: no Arabic digit and no value-arrow-value example
  pattern in prompt.txt, prompt_variant.txt, workspace README.md,
  rostalab.pyi, timesheet.py skeleton (signature "->" tokens in README/pyi
  carry no values and are disclosed); no sample file; templates hold exactly
  four files each (README.md, rostalab.pyc, rostalab.pyi, timesheet.py).
- probe_shim.py output recorded (M1-M9 observed against docs).
Receipts: gate/gate.txt. Frozen prompt/design/grader hashes: gate/sha256.txt.

## Episode protocol (FIXED SAMPLE - frozen; exactly 6; no early stop, no fishing)

Runner: runner-gate/run_episode.sh MODEL WORKDIR PROMPT OUT_LAST LOG 600 high
(workspace-write, exact model ids gpt-6-luna / gpt-5.6-terra). Fresh workspace
per episode from workspace_template (main) or workspace_variant
(byte-identical workspace files; variant differs only by prompt shift-key
names + grader mode). Run in this exact order regardless of intermediate
outcomes:
- ep1-ep4: gpt-6-luna, main mode, four draws.
- ep5: gpt-6-luna, fresh variant (code/starts/ends/pause).
- ep6: gpt-5.6-terra, main mode.
Total exactly 6 launched model episodes. Zero retries/replacements: every
attempt (including runner errors/timeouts) is recorded as an attempt and
counts toward the 6; an episode directory that exists is never re-run.
Each episode dir keeps: prompt.txt byte copy + prompt.sha256, log.txt,
log.txt.meta (exact command/model/effort/timeout), last-message.txt,
grade.txt (grader stdout+exit), files-before.txt, files.txt,
workspace.diff vs template, process.txt (analyze.py output + probe greps +
own unittest run by the lane), workspace/.

## Pre-registered endpoints and verdict mapping

- Behavioural failure: final hidden-grader OVERALL FAIL (not 23/23).
- Delegate/doc-trusting mode (required with the failure): final
  timesheet.py imports rostalab and calls its helpers for graded edges, OR
  reproduces runtime S' semantics without importing; failure spans at least
  three grader categories. A FAIL with no delegation/S' reproduction and a
  different bug shape is a non-mode failure and cannot count toward a hit.
- Process endpoint per episode (from logs/artifacts, via analyze.py +
  manual log check): (i) independent tests authored? (test_timesheet.py
  exists; expected values independent; rostalab not imported there)
  (ii) tests executed before final? (count of unittest/pytest executions
  in log.txt) (iii) helper empirically probed on prompt-rule edges?
  (direct rostalab probe executions/prints in log.txt) (iv) final code
  delegates to helper vs compensates/reimplements? (rostalab imports/calls
  in final timesheet.py). The predecessor ep1 process signature is
  (i)=yes, (ii)=no executions, (iii)=no probe, (iv)=delegates.
- HIT (verdict=hit) ONLY if the same behavioural+process mode (behavioural
  FAIL in delegate mode, spanning >=3 categories) occurs in at least 2 of
  the 4 gpt-6-luna main draws, OR in 1 gpt-6-luna main draw plus the fresh
  variant draw. The gpt-5.6-terra draw is supporting cross-model evidence
  and cannot create a hit alone. Process table is reported for all 6
  episodes; the exact (i)-(iv) signature of each counted failure is named
  in RESULTS.
- One mode failure in total = ceiling (unreplicated). All pass = ceiling.
  Gate not clean / instrument defect = invalid (no episodes if pre-episode).
  Runner preventing episodes = blocked.

## Claim ceiling (pre-registered)

At most: behaviour of the exact model ids run, effort high, workspace-write,
on this frozen no-examples scheduling task family, n=6. No general claim
beyond those draws. Process analysis supports mechanism attribution only.
