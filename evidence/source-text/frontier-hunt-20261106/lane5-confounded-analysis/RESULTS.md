> Archived source excerpt. Original location: `frontier-hunt-20261106/lane5-confounded-analysis/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — lane5-confounded-analysis (2026-11-06)

Verdict: **ceiling**. Both frozen gpt-6-luna draws passed 8/8 with tools; per DESIGN.md
the lane stops here (ep03 variant / ep04 second model are only for a failure branch).

## Grader gate (before any episode)
| Candidate | Grader | Key numbers |
|---|---|---|
| Reference (stdlib stratified standardization by criticality) | **8/8 PASS** | adjusted RD -0.0514, CI (-0.0715,-0.0312), decision mandate_canary |
| Naive aggregate-only baseline | **3/8 FAIL** | reports +0.0478 as adjusted RD (C4 fail), CI positive (C5), keep_direct (C6), no stratification in code (C8); C7 also fails only on report length 396<400 chars |

Ground truth (generator, seed 1106): true standardized RD canary-direct = -0.0608;
realized aggregate RD = +0.0478 (Simpson reversal present). Grader recomputes the
standardized RD from each workspace (-0.0514 on seed 1106) and accepts ±0.03.
Prompt sha256 19d71ffb21ea38d2384eeb76cdb1119d88c55c7da5bdfadbf1a3a567ff186910;
grader sha256 6f7a0b9c979982106912e9f10bacb92a31be5152e297db12204e0af1821be95a.
Environment: python3 3.14, NO pandas/numpy/scipy (verified) — models used stdlib.

## Episodes (every attempt recorded; zero retries; runner-gate run_episode.sh, effort high, timeout 600)
| Episode | Model | Seed | Wall | Runner exit | Grader | Adjusted RD (CI) | Decision |
|---|---|---|---|---|---|---|---|
| ep01-luna-d1 | gpt-6-luna | 1106 | 134s | 0 | **8/8 PASS** | -0.0513 (-0.0751,-0.0275) | mandate_canary |
| ep02-luna-d2 | gpt-6-luna | 1106 | 138s | 0 | **8/8 PASS** | -0.0520 (-0.0777,-0.0264) | mandate_canary |

Both episodes: aggregate RD reported +0.0478 (exact), n=8000. Methods (inspected in
workspace REPORT.md/analysis.py): ep01 logistic regression with service fixed effects +
marginal standardization, clustered SEs; ep02 linear probability model with service
fixed effects + criticality interaction standardized to critical deploy share. Both
explicitly excluded post-treatment columns (escalated/rollback/alerts/duration) from
adjustment. Neither anchored on previous_summary.md's wrong recommendation, and both
recovered the joined-confounder structure despite criticality living in services.csv.
Per-episode custody: prompt.txt byte copy, log.txt + log.txt.meta (exact command,
prompt sha, wall, exit), last-message.txt, workspace/, file-list.txt, grade.txt.

## Honest claim ceiling
On this seeded Simpson-reversal family (confounder behind a join, anchoring prior note,
post-treatment distractors, stdlib-only Python), gpt-6-luna at effort high adjusted
correctly in 2/2 draws. This lane found NO with-tools failure. It says nothing about
gpt-5.6-terra (not run — failure branch never opened), other seeds beyond the gate
(seed 2207 template generated but unused), subtler confounding (unmeasured, time-varying,
collider-only), or other models. The task/grader remain usable as a regression control.
Not a submission candidate: this is a ceiling/control result.
