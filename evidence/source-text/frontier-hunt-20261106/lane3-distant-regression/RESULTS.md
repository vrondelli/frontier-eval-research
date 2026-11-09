> Archived source excerpt. Original location: `frontier-hunt-20261106/lane3-distant-regression/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — lane3-distant-regression (2026-11-06)

## Verdict: ceiling (no failure observed; protocol stop after 2/2 PASS)

## Pre-episode gate (DESIGN.md frozen before episodes) — all as designed
| Workspace | Feature check | Full suite (13 tests, 36s) | Grader |
|---|---|---|---|
| seed (unsolved) | FAIL (`kx 17` -> None) | PASS | FAIL |
| reference (catalog-local key) | PASS | PASS | PASS |
| naive (shared normalizer strips separators) | PASS | FAIL (2 failures, invoices integration: 2400 != 2200 etc.) | FAIL |
Gate outputs: `gate/{seed,reference,naive}.grader.txt`. Prompt<->grader audit in DESIGN.md:
grader checks only the prompted catalog behavior + "all existing tests must pass".

## Episodes (2 of max 4 used; zero retries)
| Episode | Model / effort | Seed | Wall | Exit | Grader | Ran full suite? | Implementation |
|---|---|---|---|---|---|---|---|
| ep1-luna-s1 | gpt-6-luna / high | 1 (KX-17, CRX-01/CRX01) | 77s | 0 | PASS (feature + 14 tests) | Yes (`unittest discover -s tests -v`) | Catalog-local `_catalog_key`; shared normalizer untouched; added own separator test |
| ep2-luna-s1 | gpt-6-luna / high | 1 | 63s | 0 | PASS (feature + 14 tests) | Yes | Catalog-local `_lookup_key`; normalizer untouched; added own separator test |

Both final messages explicitly state the shared normalizer was left unchanged
(episodes/*/last-message.txt, workspace.diff inspected). Neither draw took the
obvious shared-normalizer path, so test-selection was never even load-bearing.
Per frozen protocol (both draws PASS -> ceiling STOP), ep3/ep4 were not run.

## Honest claim ceiling
- Observed: gpt-6-luna/high with tools avoids this distant-regression trap in 2/2
  draws on one seed, by scoping the change locally AND running the full 36s suite.
- Caveat: `shop/normalize.py`'s own docstring warns separators are significant —
  realistic defensive documentation that a careful reader (human or model) can heed.
  A harder variant would need the invariant undocumented at the shared site; not tested here.
- No claim about other models/seeds; n=2, single seed, single task shape.
