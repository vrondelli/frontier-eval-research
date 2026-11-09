> Archived source excerpt. Original location: `frontier-hunt-20261106/lane1-common-mode/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — lane1-common-mode (FROZEN before any model episode)

Frozen: 2026-11-06, before episode 1. No change after first episode;
any change would invalidate the lane.

## Hypothesis
A frontier model implementing a subtle stateful spec, required to write
and run its OWN tests, encodes the same misreading in code and tests;
its tests pass, an independent grader fails it. A "hit" is therefore
strengthened (not required) by: model tests pass AND grader fails.

## Task (fresh; not corpus E1–E5)
`PermitLedger` (versioned allowance ledger, Python stdlib only).
Delivered to model per episode in a fresh workspace: `SPEC.md`,
`permit_ledger.py` skeleton, and `prompt.txt` (implement + write own
tests `test_permit_ledger.py` + run them with tools).
Hidden from model (never in episode workspaces): `grade.py`,
`reference_permit_ledger.py`, `naive_permit_ledger.py`, this file.

Trap families, all fully specified in SPEC rules S1–S16:
boundary inclusivity (expiry exclusive S6; exact-balance spend S8.5;
equal-version stale S4), replace-vs-add + spent-carryover (S2,S5,S14),
invalid-does-not-consume (grant version S3; txn_id S9), duplicate
precedence over expiry and invalid precedence over duplicate (S8 order),
any-difference conflict (S8.2), global txn namespace (S8.2), rollback
across version/expiry and txn reuse after reversal (S12,S13),
no-revival of replaced grant (S5), history (now, txn_id) tie order (S15).

## Prompt<->grader alignment audit (E1 lesson)
Grader checks ONLY: the 5 skeleton methods, return strings copied
verbatim from SPEC (`ok,stale,invalid,no_grant,expired,insufficient,
duplicate_ok,conflict,reversed,unknown,already_reversed`), integer
balances, and history tuples in SPEC S15 format. Nothing else is graded:
no file names beyond the prompt-specified `permit_ledger.py`, no
formatting, no extra attributes, no exception types. Model's own tests
are recorded as evidence, never graded for pass/fail by the grader.

## Check -> spec-sentence mapping (26 checks)
c01 S5,S7 | c02 S2,S5,S10 | c03 S4 | c04 S3 | c05 S5(0 valid),S4 |
c06 S6,S7 | c07 S5(no revival),S6,S8.4 | c08 S8.5 | c09 S8.1,S9 |
c10 S8.5,S9 | c11 S8.3,S8.4,S8.5,S6 | c12 S8.2,S10,S11,S15 |
c13 S8.2(any-difference, global) | c14 S8(order: 2 before 4) |
c15 S8(order: 1 before 2),S9 | c16 S8.4,S9,S5 | c17 S12,S15 |
c18 S12 | c19 S13,S8.2,S12 | c20 S12(cross-expiry),S7,S5 |
c21 S14,S7,S12 | c22 S15 | c23 S15,S16,S12 | c24 S7,S15 |
c25 S9(no_grant not recorded),S8.3 | c26 S11,S15

## Grader gate (must pass before ANY episode)
- reference_permit_ledger.py: 26/26 PASS required.
- naive_permit_ledger.py (coherent plausible misreadings, see its
  docstring): must FAIL >=3 checks.
- skeleton: must fail to load/pass (sanity that grader is not vacuous
  is covered by naive failures).
If gate fails: verdict=invalid, zero model episodes.

## Episode protocol (cap 4, zero retries, every attempt recorded)
Runner: runner-gate/run_episode.sh (codex exec, -s workspace-write,
effort high, timeout 600s). Strongest verified model: gpt-6-luna.
Second model: gpt-5.6-terra.
- ep1: gpt-6-luna draw1, base SPEC.
- ep2: gpt-6-luna draw2, base SPEC, fresh workspace.
- If ep1+ep2 both PASS grader: verdict=ceiling, STOP.
- If any FAILS: ep3 = gpt-6-luna on fresh generated variant
  (gen_variant.py seed=7: same semantics/API/strings, shuffled rule
  listing; same grader), ep4 = gpt-5.6-terra on base SPEC.
- A runner/model error (nonzero exit, no implementation) is recorded
  as that episode's outcome, never re-drawn or substituted.
Per episode saved: prompt.txt byte copy, log.txt, log.txt.meta (exact
command, model, effort, prompt sha256, wall, exit), last-message.txt,
workspace/ (fresh copy; file list via files.txt), grade.txt,
own-tests.txt (result of running the model's own test file with
python3 -m pytest -q if present, else recorded absent).

## Verdict rule
hit = grader gate clean AND >=1 with-tools FAIL that is replicated
(second failing draw among ep2/ep3/ep4) or variant-confirmed (ep3 fails).
A single isolated fail with all later draws passing is NOT a hit;
recorded as ceiling-with-one-failure in RESULTS and verdict=ceiling
per parent definition (hit requires replicated/variant-confirmed).
ceiling = all run draws pass (or single unreplicated fail, labelled).
invalid = any prompt/grader/reference defect found at any point.
blocked = runner prevents episodes.

## Claim ceiling (pre-registered)
At most: "model X at high effort, with terminal/Python tools, failed
this frozen PermitLedger spec on checks [...] while its own tests
[passed/failed/absent]" for the exact draws run. No general claim
about coding ability, other models, or other specs.
