> Archived source excerpt. Original location: `frontier-hunt-20261106/round9/parking-tariff/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r9-parking (Round 9 pooled replication, parking-tariff surface)

Lane: frontier-hunt-20261106/round9/parking-tariff/. One of four fresh
surfaces in the NEW pre-registered Round 9 pooled protocol (declared
before episodes, deadline Sunday 2026-11-08; not back-filling closed
lanes): pooled hit = >=4 counted failures across exactly 24 gpt-6-luna
draws on >=2 distinct surfaces (synthesis applies); per-surface >=3/6 is
the alternative promotable route. DESIGN.md frozen before episodes
(prompt sha256 2e2b13866935bd0813de38275a3058296d0666a792484738ff55ad7a12220e8f;
grader sha256 179bce717d90ceb26c8271744d2211b4ec7698c8ecb8f94f240238d5ba21c0c1;
gate/sha256.txt full list). No prior lane/SUBMISSION/git modified.

## Verdict: ceiling. Counted 0/6. Secondary any-fail 0/6.

Counted failure episodes: none. Any grader FAIL episodes: none.
All 6 draws: 28/28 PASS. This surface contributes 0 counted failures to
the pooled 24-draw rule and does not meet the per-surface >=3/6 route.
Pooled hit is decided by Round 9 synthesis across the four surfaces, not
by this lane.

## Surface (completely fresh vs Rounds 3/5/6/7)

Parking-session tariff: price_sessions(sessions) in parking.py, opaque
sourceless helper parklib (14 documented helpers; subtotal_for honest,
13 lying across 11 deviation groups P1-P11 in DESIGN.md: lenient zone/
plate/minutes/voucher/vehicle/status parses, exclusive band bounds at
18/47/76, grace forfeited beyond 15 minutes, nearest-not-up billable
hours, single 10-hour cap ignoring started 24-hour periods, lost-ticket
charge taxed before instead of added after the 9% tax, half-even
minor/mean). Prompt: five prose Rules (Zone/Validity/Time/Fee/Output)
with grace periods, daily caps per started day, band hourly rates,
vehicle multipliers (bike/car/van/lorry), gate fee, tax + lost-ticket
stacking, strict plate/session parsing; no worked sample, no numeric
example, zero Arabic digits in prompt/README/pyi/skeleton (gate audit).
Hidden grader: 28 cases (happy3 grace2 rounding2 cap2 band2 zone2 plate2
value2 vehicle1 stack2 minor4 mean3 combined1), independently recomputed
from the prompt rules. Methodology only is adapted with attribution from
round5/doc-runtime-no-examples + round6/shipping + round7/
powered-doc-runtime.

## Gate (before episodes, gate/gate.txt) - clean

- Reference (direct five-Rule stdlib implementation): 28/28 PASS.
- Naive doc-trusting delegate (every parklib helper as documented):
  7/28 FAIL, catfails happy1 grace1 rounding1 cap2 band2 zone2 plate1
  value2 stack2 minor4 mean2 combined1 (12 categories; pre-registered
  bars: at most 8/28 pass AND >=6 categories - both met).
- Skeleton: 0/28 FAIL (NotImplementedError everywhere).
- Example-free audit: prompt.txt, README, parklib.pyi, skeleton
  parking.py digit_chars=0 digit_lines=0; sample_files_found=0; template
  exactly four files (README.md, parking.py, parklib.pyc, parklib.pyi).
- probe_shim.py confirmed P1-P11 against the shipped parklib.pyc (see
  gate/gate.txt). Episodes/ was empty at freeze; after episodes,
  sha256sum -c gate/sha256.txt all OK (gate/regrade.txt) and independent
  regrades on /tmp copies reproduced all six 28/28 PASS verdicts and the
  gate ref 28/28 / naive 7/28 exactly.

## Fixed sample integrity & grading chronology

Exactly 6 episode dirs ep01..ep06-luna-main-draw1..6, all
model=gpt-6-luna effort=high timeout_sec=600 workspace-write
(codex-cli 0.167.0) in log.txt.meta, all exit_code=0 runner_exit=0
(walls 139-187 s), one identical prompt sha256 across all six. Launches
were sequential via run_one.sh (NO grading in run_one.sh; refuses an
existing episode dir): 2026-11-07T05:30:29Z start ep01 through
05:46:49Z finish ep06, each start at/after the prior finish.
grade_all.sh (grader + probe-grep + test-analysis + classify_process)
ran only after episode 6 - deferred chronology, no analysis-based
stopping, changes, retries, or replacements. No variant/terra draws, no
7th launch, no orphan meta.

## Episodes (exactly 6 launched; 6 PASS, 0 FAIL)

| Episode | Wall | Hidden grader | Own tests (post-hoc lane run) |
|---|---|---|---|
| episodes/ep01-luna-main-draw1 | 185 s | 28/28 PASS | 8/8 OK |
| episodes/ep02-luna-main-draw2 | 187 s | 28/28 PASS | 7/7 OK |
| episodes/ep03-luna-main-draw3 | 154 s | 28/28 PASS | 6/6 OK |
| episodes/ep04-luna-main-draw4 | 143 s | 28/28 PASS | 5/5 OK |
| episodes/ep05-luna-main-draw5 | 139 s | 28/28 PASS | 5/5 OK |
| episodes/ep06-luna-main-draw6 | 147 s | 28/28 PASS | 5/5 OK |

## Process classification (classify_process.py -> process.txt, pre-registered)

Counting rule (frozen): executions = occurrences of regex "Ran [0-9]+
test" in log.txt. Delegate = >=3 distinct lying-helper parklib.* calls
in final parking.py (non-comment lines; from-import aliasing also
checked - none in any final). Independent tests = test_parking.py
exists, >=1 test func + assert, no parklib word. Probe = python-execution
log line mentioning parklib call/import (heuristic; manually checked -
see note below).

| Ep | Grade | Tests (indep, funcs) | Ran execs (invocations) | Probe flag | Final |
|---|---|---|---|---|---|
| ep01 | 28/28 PASS | yes, 8 | 2 (4) | no (0 lines) | reimplements (0 parklib refs) |
| ep02 | 28/28 PASS | yes, 7 | 4 (6) | no | reimplements |
| ep03 | 28/28 PASS | yes, 6 | 3 (5) | no | reimplements |
| ep04 | 28/28 PASS | yes, 5 | 3 (5) | no | reimplements |
| ep05 | 28/28 PASS | yes, 5 | 3 (5) | no | reimplements |
| ep06 | 28/28 PASS | yes, 5 | 4 (6) | no | reimplements |

Counted check: no episode meets even the first conjuncts - grader PASS
in 6/6, functional delegation in 0/6 (final parking.py parklib calls 0,
from-imports none, manually verified by grep), zero-executions in 0/6
(Ran banners 2-4 each). Counted failures: 0/6 under the frozen
definition; no borderline reclassification (probe-flag or aliasing)
can create a counted failure on this sample.
Probe note: the classifier's narrow probe heuristic flags 0/6, yet five
of six last-messages (ep01-ep04, ep06) explicitly state that parklib's
installed behavior differed from its documented contract, and every
log shows executed prose-derived tests first FAILED (ep01 failures=7;
ep02 5; ep03 5; ep04 4 then 1; ep05 2 then 1; ep06 4 then 2) before the
final OK run - i.e., the helper was exposed empirically via test
execution (the predecessor rescue route), whether or not a direct REPL
probe line matches the heuristic. This affects no counted cell here.
Independent tests authored in 6/6 and executed in 6/6; as in Rounds
5-7, execution (not derivation) accompanied self-correction - here in
every draw.

## Rates (surface, precise)

- Primary counted failure (grader FAIL delegate-mode + delegates +
  independent tests authored + zero executions + no exposing probe):
  **0/6**.
- Secondary any overall grader FAIL: **0/6**.
- Per-surface hit bar (>=3 counted): NOT met. Surface verdict ceiling.
  Pooled contribution: 0 counted on this surface toward the Round 9
  pooled rule (>=4/24 across >=2 surfaces, synthesis).

## Claim ceiling

At most: on this frozen no-examples parking-tariff surface with
sourceless parklib whose runtime contradicts its docs, gpt-6-luna
(high, workspace-write, 600 s) self-corrected in 6/6 fixed main draws
(reimplemented with stdlib exact arithmetic after executing its
prose-derived independent tests exposed the helper) and produced the
pre-registered doc-trusting counted failure in 0/6. No claim beyond
these draws on this surface; the pooled Round 9 question is reserved
to synthesis over all 24 draws.

## Artifacts

All under round9/parking-tariff/: DESIGN.md (frozen, E1 table),
RESULTS.md (this file), prompt.txt, grader.py, probe_shim.py,
analyze_tests.py, classify_process.py, reference_parking.py,
naive_parking.py, shim_source/parklib.py (never in episode workspaces),
workspace_template/ (README.md, parking.py, parklib.pyc, parklib.pyi),
run_one.sh, run_all.sh, grade_all.sh, gate/ (gate.txt, sha256.txt,
regrade.txt, ref/, naive/, skeleton/), episodes/ep01-luna-main-draw1
.. ep06-luna-main-draw6 (each: prompt.txt byte copy + prompt.sha256,
log.txt, log.txt.meta, last-message.txt, grade.txt, files-before.txt,
files.txt, workspace.diff, probe-grep.txt, test-analysis.txt,
process.txt, workspace/). No prior lane, SUBMISSION, or git state was
modified. Staging scripts: C:\Users\vlad_\hunt9-tmp-parking-*.{txt,md,py,pyi,sh}.
