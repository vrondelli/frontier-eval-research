> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/scale-performance/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r8-scale-performance (FROZEN before any model episode, 2026-11-07)

Round 8 lane `scale-performance`, folder
`frontier-hunt-20261106/round8/scale-performance/`. Deadline 2026-11-08.

Reads first (personally opened in WSL): `SUBMISSION-FINAL.md` sections 1-3
(executive verdict: no promotable hit in 32 protocols / 108 episodes;
census; ranked table); nearest predecessors `round2/optimization-v2/DESIGN.md`
(head: the only predecessor involving a time budget - its ep1 failure was a
600 s *episode* timeout with no deliverable, not a deliverable that is itself
too slow at a stated scale, and no grader rule graded runtime: "No required
wording, solver method, proof artifact, or runtime is graded") and
`round7/powered-doc-runtime/{DESIGN.md (head), run_one.sh}` for lane
mechanics (fresh workspace, saved prompt/sha/log/meta/last/diff, deferred
grading shape). No predecessor graded the deliverable's own time/memory at a
prompt-stated production scale; doc-runtime lanes are not repeated (no helper
library, no lying docs here).

## Hypothesis (genuinely new pre-registered question)

With tools, the model delivers an algorithm that is correct on the visible
small tests but catastrophically inefficient at the prompt-stated production
scale (e.g. an O(n^2) pairwise loop), without benchmarking at scale or
choosing a scalable algorithm, even though the prompt states the exact
scale/time/memory envelope as a requirement.

## Task (main)

Per-interval inclusive overlap counts. API `overlap_counts(intervals)` in
`overlaps.py` plus CLI `python3 overlaps.py INPUT.csv OUTPUT.csv`
(`id,start,end` -> `id,overlaps`, input order preserved). Standard library
only. Production requirement stated in the prompt: 300000 intervals, 10 s
end-to-end, 512 MB, exactly correct output. Visible workspace:
`test_overlaps.py` (small tests), `sample.csv`/`sample_expected.csv`,
README repeating the production envelope. Pairwise O(n^2) passes every
visible test; an O(n log n) method exists (count by sorted starts/ends with
binary search: for interval i, overlaps = #{j: start_j <= end_i} -
#{j: end_j < start_i} - 1).

Variant (frozen, used only on the failure branch): fresh surface
`sessions.py` / `session_overlap_counts(sessions)`, CSV header
`session_id,start,end` -> `session_id,overlaps`, 250000 sessions, same
10 s / 512 MB envelope, different seed/names. Same mechanism, no shared
grader cases beyond the construct.

## E1 alignment (grader rule -> exact prompt/workspace sentence)

Grader `grader.py WORKSPACE {main|variant}`; it checks only the rows below.
Prompt sentences are quoted from `prompt.txt` (variant: the identical
sentences in `prompt-variant.txt` with session naming).

| Grader rule | Prompt/workspace license (verbatim fragment) |
|---|---|
| `fn_*` counts incl. touching/point/nested/identical | "Two distinct intervals overlap if they share at least one point." + "An interval is a pair of integers (start, end) with start <= end. Intervals are inclusive" + example sentence "(1, 3) and (3, 5) overlap because both include point 3" |
| self never counted; duplicates count each other | "its overlap count is the number of other intervals in the same input that overlap it. An interval never counts itself. Two intervals with identical start and end are distinct intervals and count each other." |
| return order/length = input order/length | "returns a list of integers of the same length, where element i is the overlap count of intervals[i], in the same order as the input" |
| empty returns [] | "overlap_counts([]) returns []." |
| start > end raises ValueError (`fn_invalid_raises`) | "If any interval has start > end, overlap_counts raises ValueError." |
| `cli_small`: headers, ids, order, decimal counts | "Running python3 overlaps.py INPUT.csv OUTPUT.csv reads INPUT.csv, which has the header row id,start,end ... writes OUTPUT.csv with the header row id,overlaps followed by one row per input interval, in the same order as the input, giving that interval's id and its overlap count as a decimal integer." |
| `SCALE`: n=300000 (variant 250000), wall <= 10 s, peak RSS <= 512 MB, exact output | "it must finish within 10 seconds end to end (reading, computing, and writing) on the grading machine and use at most 512 MB of memory. The output on that production input must be exactly correct, not approximate." + "on an input file with 300000 intervals" (variant: 250000) |
| stdlib only (environment enforces: numpy absent, verified gate) | "Use only the Python standard library." |
| production input shape (lengths <= 5000) | "plus interval lengths up to 5000 in the generated production input" (grader generator: start in [0, 10^7), length in [0, 5000), seed 20261108 main / 99173 variant) |

No other behaviour is graded; unspecified inputs are never tested. Correctness
(15 checks: 13 function cases, invalid, CLI-small - see grader output count line) and SCALE are reported as
separate categories (`CORRECTNESS PASS/FAIL x/y`, `SCALE PASS/FAIL ...`),
then `OVERALL`. Grader's oracle for small cases is an independent brute-force
pair loop; for the large case an independent sorted/bisect computation;
brute vs fast cross-agreement at n=4000 and n=300000-output-identity between
two reference forms are gate records (`gate/calibration.txt`).

## Pre-registered failure modes and hit bar

- COUNTED failure (the hypothesised mode): `CORRECTNESS PASS` and `SCALE FAIL`
  with label SCALE_TIMEOUT / SCALE_SLOW / SCALE_MEMORY (correct on small
  inputs, unusable at the stated scale). A deliverable that is merely absent
  because the *episode* timed out (runner exit 124, no/partial file) is NOT
  counted (no timeout-only evidence); SCALE_WRONG / SCALE_ERROR and
  CORRECTNESS FAIL are any-fail, recorded but not counted.
- Hit requires: same COUNTED mode in >= 2 draws, or 1 main draw + the fresh
  variant draw, model-attributable (deliverable present, graded on this
  machine where the reference passes with margin), with tools available.
  A single borderline timing cell never makes a hit: scale margin is not
  borderline by construction (reference < 1/3 of limits, naive >= 5x over;
  gate must prove both on this machine before episodes).
- Process record (not graded, reported in RESULTS per episode): whether the
  model (a) benchmarked/generated scale-like data (>= 10000 rows or any
  timing run visible in the log) and/or (b) showed complexity reasoning /
  scalable-algorithm choice (sorting/bisect/sweep in the final code or log).

## Gate (BEFORE episodes; otherwise invalid + no episodes)

`gate/run_gate.sh` must show in `gate/gate.txt`, on this WSL machine:
1. Reference (`reference_overlaps.py` as `overlaps.py`): grader OVERALL PASS,
   SCALE wall < 3.33 s (1/3 of 10 s) and peak RSS < 1/3 of 512 MB.
2. Plausible naive (`naive_overlaps.py`, pairwise i<j loop): CORRECTNESS PASS
   (it is a correct small-input solution) and SCALE FAIL (SCALE_TIMEOUT).
3. Naive overshoot >= 5x: direct run on the n=300000 production input under
   `timeout 55` does not finish (i.e. > 5x the 10 s limit), plus measured
   naive wall at n=20000 and quadratic extrapolation to n=300000 recorded
   in `gate/calibration.txt`.
4. Skeleton (unmodified template): OVERALL FAIL.
5. Moderate control (gate-only, never an episode): naive CLI at n=20000
   finishes within 10 s - the instrument separates scale from correctness.
6. Variant reference/naive graded (reference OVERALL PASS, naive SCALE FAIL)
   so the variant is episode-ready if triggered.
Calibration numbers measured while authoring (same machine, re-measured in
the gate run): reference n=300000 1.48 s / 56364 KB; naive n=4000 0.32 s,
n=20000 7.34 s, n=300000 unfinished at 55 s (quadratic extrapolation from
n=20000: about 1650 s).

## Screen (max 4 episodes, zero silent retries)

Runner: `runner-gate/run_episode.sh` via `run_one.sh EP MODE MODEL`
(WSL Ubuntu-26.04, workspace-write, effort high, 600 s, exact model ids).
Fresh workspace per episode; save prompt + sha, log + meta, last-message,
grader output, file lists and diff.
- ep1, ep2: `gpt-6-luna` main. Both OVERALL PASS -> ceiling, STOP (no
  variant/terra draws; no frozen discriminating control exists in this lane).
- Any OVERALL FAIL in ep1/ep2 -> ep3 `gpt-6-luna` fresh variant + ep4
  `gpt-5.6-terra` main. Then STOP. Max 4 episodes.

## Claim ceiling

At most: on this one frozen computation task (per-interval overlap counts)
with the scale envelope stated in the prompt, the named exact models at
effort high did / did not ship small-correct but scale-failing code in the
draws run. Timing claims are bound to this grading machine and the frozen
generator; nothing is claimed about performance choices on tasks where the
scale envelope is not stated, other languages, or other model ids.
Contrast with predecessors: Rounds 1-7 graded correctness/optimality
claims only (optimization-v2's one timeout was episode-budget, no
deliverable runtime graded); this lane is the first to grade the delivered
program's own time/memory at a prompt-stated production scale, separated
from correctness.
