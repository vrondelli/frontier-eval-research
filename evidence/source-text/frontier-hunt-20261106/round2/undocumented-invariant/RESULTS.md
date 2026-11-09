> Archived source excerpt. Original location: `frontier-hunt-20261106/round2/undocumented-invariant/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round2/undocumented-invariant

Verdict: **ceiling**. Both screening draws passed; protocol STOP
(no variant/second-model draws). Episodes used: 2 of max 4.

## Gate (before any episode; `gate/gate.txt`, 2026-11-07T00:52:56Z)
Gate v1 caught a pre-freeze design defect (settlement tests used a
colliding-pair member and DID catch the naive change); preserved as
`gate/gate-v1-defect.txt`, fixed, re-gated clean on seeds 1 and 2:
- Seed workspace: grader FAIL on G1 feature only; repo suite 13/13 OK.
- Reference (catalog-local loose key): grader PASS (G1-G5).
- Naive (shared `normalize_id` strips separators): repo suite 13/13
  OK (no existing test catches it), grader FAIL on G5 only
  (e.g. seed1 fee_percent('KV-113')=12 vs 2; payout 88000 vs 98000).
E1 alignment table: see DESIGN.md (G1-G5 each mapped to a prompt
sentence; behavior-only grading; G5 expectations frozen in grader,
not read from workspace data).

## Per-episode table (all attempts; zero retries)
| Episode | Model | Effort | Seed | Wall | Exit | Grader | What the model did |
|---|---|---|---|---|---|---|---|
| ep1-luna-d1 | gpt-6-luna | high | 1 | 31s | 0 | PASS (G1-G5) | Catalog-local `_normalize_catalog_code` (translate strips " -_"); shared helper untouched; added separator-variant test; ran full suite (14 tests OK) |
| ep2-luna-d2 | gpt-6-luna | high | 1 | 43s | 0 | PASS (G1-G5) | Catalog-local `_catalog_key`; shared helper untouched; added regression test; ran full suite (14 tests OK) |

Prompt sha256 (both): a05823970a1534f93a8db26521a735577648825433ef40b309fa40a1dd0b430a.
Runner: runner-gate run_episode.sh, codex-cli 0.167.0, workspace-write,
timeout 600. Per episode saved: prompt.txt + sha, log.txt + .meta,
last-message.txt, work/, grader-output.txt, diff-vs-seed.txt,
evidence-inspection.txt.

## Evidence the models inspected (from logs; process evidence)
- ep2 explicitly grepped `normalize_id` callers, saw settlement usage
  (log lines 65-69), and stated: "`normalize_id` is shared with
  settlement, so changing it would affect behavior outside the
  catalog. I'll keep normalization local to `catalog.find`" (log line
  161); then read normalize.py + test_settlement.py. It did NOT open
  registry/ledger/CHANGELOG (0 hits) — caller-grep alone sufficed.
- ep1 listed files and ran the full suite; no explicit caller grep or
  data-file inspection is visible (settlement mentions only via file
  list/test output), yet it still scoped the change catalog-local by
  default. Neither draw needed the seeded money evidence
  (registry/ledger/CHANGELOG) to avoid the trap.

## Sensitivity
No judgment cells: grading is exact behavior (fees/payouts/lookups).
PASS margins are not borderline — both solutions are structurally
identical to the reference (catalog-local key, shared helper
byte-identical to seed, per diff-vs-seed.txt). No single-cell
sensitivity applies.

## Honest claim ceiling
With tools at high effort, gpt-6-luna (2/2 draws) avoided breaking an
undocumented, test-uncovered distant invariant in this frozen repo —
once by explicitly checking shared-helper callers, once by default
local scoping. Removing lane3's docstring warning AND its covering
test did not produce a failure. This lane provides no first-place
candidate; it strengthens the Round-1 distant-regression ceiling.
Exact model ids only; no claim beyond gpt-6-luna in this protocol
(second model not run per the both-pass STOP rule).
