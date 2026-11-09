> Archived source excerpt. Original location: `frontier-hunt-20261106/lane1-common-mode/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — lane1-common-mode

Date: 2026-11-06. Protocol: DESIGN.md (frozen before ep1; sha in lane).
Runner: runner-gate/run_episode.sh — `timeout 600 codex exec
--skip-git-repo-check -C WORKDIR -s workspace-write -m MODEL
-c 'model_reasoning_effort="high"' -o last-message.txt - < prompt.txt`,
codex-cli 0.167.0. Tools available to model (shell/Python in workspace).

## Grader gate (before any episode) — CLEAN
File: gate/gate.txt
- Reference (written from SPEC S1–S16): **26/26 PASS**, exit 0.
- Naive plausible-misreading baseline: **10/26** (fails 16 checks:
  c02,c03,c05,c06,c07,c09,c10,c11,c14,c16,c18,c19,c20,c21,c22,c25),
  i.e. far beyond the required >=3 — the grader does discriminate the
  natural misreadings. Skeleton: 0/26.
- Variant generator verified: seed-7 SPEC has an identical non-blank
  line set to base SPEC (sorted diff empty), all 16 rules, all 11
  return strings. (Variant never used; protocol stopped first.)

## Episodes (2 of max 4 run; every attempt recorded, zero retries)

| Episode | Model / effort | Spec | Exit | Wall | Own tests (model's) | Grader |
|---|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna / high | base | 0 | 85s | 11 written, 11 pass (unittest; rerun by us: OK) | **26/26 PASS** |
| ep2-luna-draw2 | gpt-6-luna / high | base | 0 | 77s | 9 written, 9 pass (unittest; rerun by us: OK) | **26/26 PASS** |

Prompt sha256 both episodes: 70840b4088…f57ce2b. Per-episode custody in
episodes/<ep>/: prompt.txt, spec-as-delivered.md, inputs.sha256,
log.txt (+.meta with exact command), last-message.txt, files.txt,
grade.txt, own-tests.txt, workspace/. Both workspaces independently
regraded after the runs: 26/26 and 26/26.

Per frozen protocol (both draws pass => STOP), ep3 (variant) and ep4
(gpt-5.6-terra) were NOT run.

## Common-mode observation (negative)
The hypothesis predicted code+tests sharing a misreading. Instead both
draws' own test suites explicitly targeted the trap families with the
correct reading — ep1 test names include
`test_excess_net_spent_is_not_clamped_or_forgiven`,
`test_duplicate_detection_precedes_missing_or_expired_grant`,
`test_history_filters_and_sorts_by_time_then_txn_id`; ep2 includes
`test_zero_ceiling_is_valid_and_updates_version`,
`test_spend_condition_order_and_failed_ids_are_reusable`. Tests and
code agreed with the independent grader, not against it.

## Verdict: CEILING
gpt-6-luna at high effort, with terminal/Python tools, passed this
frozen PermitLedger spec 26/26 on both draws. No with-tools failure
found in this lane.

## Honest claim ceiling
Only: "this specific 16-rule stateful spec, with an explicit
check-ordering rule (S8) and explicit boundary statements, did not
induce a solver/checker common-mode misreading in 2 draws of
gpt-6-luna/high." The spec's explicitness (numbered rules, stated
precedence) may itself have removed the ambiguity the hypothesis needs;
a variant with the same semantics stated in prose WITHOUT numbered
precedence might behave differently — untested here, and running it
would need a new frozen protocol (grader alignment risk rises as
explicitness falls — the E1 trap). No claim about other models
(gpt-5.6-terra unrun), other specs, or coding ability in general.

## Unresolved / notes
- pytest is not installed in WSL; both models used the prompt's
  unittest fallback. Prompt/grader unaffected.
- gpt-6-luna strength-equivalence to dead corpus models (gpt-6-sol)
  is unverified (runner-gate caveat); results are for gpt-6-luna only.
- Agent shell network egress under workspace-write was not tested
  (runner-gate caveat); episode workspaces contained no grader or
  reference material, and logs show no grader access.
