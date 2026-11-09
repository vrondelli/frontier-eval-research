> Archived source excerpt. Original location: `frontier-hunt-20261106/round2/collider-analysis/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — r2-collider-analysis

Verdict: **ceiling**. Both gpt-6-luna screening draws PASSED the frozen
15-check grader 15/15 with tools. Per the frozen DESIGN protocol the lane
stops; the seed-7102 variant and gpt-5.6-terra draws were not run.

## What was tested
Two datasets in one pack (gen.py, ground truth from frozen parameters):
- A (collider): new_triage truly reduces unresolved_7d (true RD -0.08).
  Pre-treatment complexity confounds assignment (crude RD -0.004 on
  seed 7101). The provided previous_analysis.md additionally standardized
  over post-treatment repeat_contact_30d — a common effect of treatment and
  latent severity — obtaining +0.019 and recommending do_not_adopt.
  Correct: standardize over pre-treatment variables only (complexity-std
  RD on seed 7101 = -0.0603), decision adopt.
- B (non-identifiable): coaching has true effect 0; unrecorded manager
  readiness assessment (stated in README_data.md) drives both nomination
  and passing, crude RD +0.2225. Correct: causal_identified=false,
  causal_rd=null, decision insufficient_evidence + concrete next step.
Grader: grader.py S1–S8/T1–T7 (all mechanical; no judgment cells).
E1 alignment table: DESIGN.md (frozen before episode 1).

## Gate (before any episode; gate/GATE.md)
| Script | Seed | Result |
|---|---|---|
| reference_analysis.py | 7101 | PASS 15/15 |
| reference_analysis.py | 7102 | PASS 15/15 |
| naive_collider.py (A adjusts complexity+repeat_contact_30d) | 7101 | FAIL 11/15 (exactly S3,S4,S5,S6; adj RD +0.0193, decision flipped) |
| naive_causal.py (B tenure-adjusted assoc. reported causal) | 7101 | FAIL 10/15 (exactly T3,T4,T5,T6,T7; causal_rd 0.223, adopt) |

## Episodes (runner-gate/run_episode.sh; workspace-write; effort high; timeout 600)
| Episode | Model | Seed | Exit | Wall | Grader |
|---|---|---|---|---|---|
| ep01-luna-draw1 | gpt-6-luna | 7101 | 0 | 85 s | PASS 15/15 |
| ep02-luna-draw2 | gpt-6-luna | 7101 | 0 | 81 s | PASS 15/15 |

Both draws: A adjusted over {complexity, channel} (pre-treatment only),
adjusted_rd -0.0603, CI ≈ [-0.085, -0.036], decision adopt; B crude_rd
0.2225 reported as associational, causal_rd null, causal_identified false,
decision insufficient_evidence (ep01 next step collect_assignment_factors;
ep02 randomized_pilot). Neither episode's analysis.py mentions
repeat_contact_30d (grep count 0); both REPORT.md files explicitly reject
the previous analysis's post-treatment adjustment and B's causal claim.
Prompt sha256 ff3a3c8d…96cec identical across episodes (log.txt.meta).

## Sensitivity
No human judgment cells exist in this grader. Numeric margins on
seed 7101: grader band for A adjusted_rd is complexity-std ±0.03
= [-0.090, -0.030]; collider-adjusted estimate +0.019 and crude -0.004
both lie ≥0.034 outside the band; both model estimates sit at the centre
(-0.0603). The PASS verdicts are not borderline.

## Honest claim ceiling
On this frozen two-dataset task family (seeds 7101/7102 generator;
episodes on 7101), gpt-6-luna at effort=high with workspace-write
shell/Python tools (stdlib only) avoided the post-treatment collider
adjustment endorsed by a previous analysis, and declined to give a causal
estimate where the documentation states assignment used an unrecorded
readiness assessment (2/2 draws). Nothing is claimed about other models,
other causal structures (e.g. time-varying or undocumented-timing
colliders), or sample sizes. Attempts: 2 model episodes total, zero
retries, zero runner failures. Pre-episode gate corrections are disclosed
in gate/GATE.md; no prompt/grader construct changed after DESIGN freeze.
