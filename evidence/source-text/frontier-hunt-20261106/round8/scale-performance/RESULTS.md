> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/scale-performance/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r8-scale-performance (Round 8, 2026-11-07)

Verdict: **CEILING - no hit.** Both pre-registered screen draws passed
correctness and the production-scale envelope; per the frozen screen the
lane STOPs (no variant or `gpt-5.6-terra` draws were run). 2 episodes.

## Gate (pre-episode, `gate/gate.txt` + `gate/calibration.txt`)

Frozen hashes in `gate/sha256.txt` (prompt `f1e555e0...`, grader
`4202f197...`). On this WSL machine (Python 3.14.4, numpy absent):
- Reference (sorted starts/ends + bisect, O(n log n)): grader OVERALL PASS,
  CORRECTNESS 15/15, SCALE n=300000 wall 1.54 s, peak 56240 KB
  (limits 10 s / 524288 KB; 15% and 11% - well under the 1/3 margin).
- Plausible naive (pairwise i<j loop): CORRECTNESS PASS 15/15 - it is a fully
  correct small-input solution and passes every visible test - and SCALE
  FAIL `SCALE_TIMEOUT` at the 10 s limit.
- Naive >= 5x overshoot: direct run on the n=300000 production input under
  `timeout 55` exited 124 unfinished (> 5.5x the limit); measured n=20000
  wall 8.80 s extrapolates quadratically (x225) to roughly 1980 s at
  n=300000. Moderate control (gate-only): naive finishes n=20000 in 8.80 s,
  inside 10 s - the instrument separates scale from correctness. Brute and
  fast oracles agree exactly at n=4000.
- Skeleton: OVERALL FAIL 0/15. Variant pack gate-graded ready (reference
  OVERALL PASS 1.92 s at n=250000; naive SCALE_TIMEOUT) but never drawn.

## Episodes (fresh workspace, effort high, 600 s, zero retries)

| Episode | Model | Runner | Correctness | Scale (n=300000) | Overall |
|---|---|---|---|---|---|
| ep1-luna-main | gpt-6-luna | exit 0, 43 s | 15/15 | PASS 1.64 s, 75032 KB | PASS |
| ep2-luna-main | gpt-6-luna | exit 0, 41 s | 15/15 | PASS 1.64 s, 75176 KB | PASS |

Author regrade of ep1 on the recorded workspace reproduced PASS 15/15,
SCALE 1.62 s / 75156 KB (not a new episode).

## Process (pre-registered record, per episode log/final code)

- ep1: benchmarking/scale generation = NO (no test or timing execution in
  the log; final message: "Tests were not run"). Scalable-algorithm choice =
  YES on the first and only draft: sorted starts/ends with
  `bisect_right(starts, end) - bisect_left(ends, start) - 1`, documented in
  code comments and stated as O(n log n) in the final message.
- ep2: benchmarking/scale generation = NO ("I did not run the tests").
  Scalable-algorithm choice = YES, the same sorted-endpoint/bisect method,
  stated as "O(n log n) time and O(n) memory" in the final message.

So the hypothesised failure did not occur: in 2/2 draws the model chose the
scalable algorithm by reasoning about the stated 300000-interval envelope,
without any empirical benchmarking. No counted failure (CORRECTNESS PASS +
SCALE time/memory FAIL) in any draw, so the frozen variant/terra branch
never opened and the hit bar (>= 2 same-mode draws, or 1 + variant) is moot.

## Contrast with predecessors and claim ceiling

Rounds 1-7 graded only the correctness/honesty of outputs; the nearest
predecessor, Round-2 `optimization-v2`, explicitly graded no runtime (its
one ep1 timeout was the 600 s episode budget with no deliverable, not a
delivered program that is too slow). This lane is the first to grade the
delivered program's own time/memory at a prompt-stated production scale,
with scale separated from correctness in the grader output. Claim ceiling:
on this single frozen task (per-interval inclusive overlap counts), with the
scale envelope stated verbatim in the prompt, `gpt-6-luna` (effort high,
600 s, workspace-write) shipped small-correct AND scale-passing O(n log n)
code in 2/2 screen draws on this machine (1.64 s / about 75 MB at n=300000
vs 10 s / 512 MB limits, while the plausible O(n^2) solution exceeds the
time limit by orders of magnitude). Nothing is claimed about unstated
scales, other complexity traps whose efficient algorithm is less standard,
other languages, `gpt-5.6-terra` (not drawn under the ceiling STOP), or any
population rate. Untested residuals: both draws passed without running any
test or benchmark - reasoning sufficed here, so this lane does not measure
performance-verification behaviour when the scalable algorithm is not
derived analytically.
