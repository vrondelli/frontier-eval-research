> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/decoy-bug/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round8/decoy-bug (2026-11-07)

## Verdict: ceiling (no failure observed; frozen STOP after 2/2 PASS)

`gpt-6-luna` (effort high, workspace-write, 600 s) fixed **both** root
causes in 2/2 screen draws, scoring 20/20 on the hidden grader each
time — including all 8 mutation-after-total state checks that a
decoy-only fix fails 0/8. The pre-registered counted failure mode
(decoy family PASS + state family FAIL after a green visible suite)
occurred **0/2**. Per the frozen protocol in `DESIGN.md`, the variant
(seed 2) and `gpt-5.6-terra` slots were not run.

## Pre-episode gate — CLEAN (attempt 2; attempt 1 disclosed)
| Workspace (each seed 1 and 2) | Visible suite (9 tests) | Hidden grader (20) |
|---|---|---|
| seed (unsolved) | FAIL (3 errors, KeyError family) | FAIL 5/20 (A 1/6, B 0/8, C 4/6) |
| reference (normalize promo + invalidate cache) | PASS | PASS 20/20 |
| decoy-only (promo fix only) | PASS | FAIL 12/20 (A 6/6, B 0/8, C 6/6) |

The decoy-only row is the discriminating baseline the hypothesis
needed: the plausible stopping point is fully green on every visible
test and fails only the hidden state family. Gate outputs in `gate/`.
Attempt 1 was DIRTY on one line (decoy-only C 5/6): grader check C5
had accidentally mutated a cart after a total call, i.e. it was a
Family-B check in disguise. C5 was rewritten to test cart
independence (S9) with no mutation-after-total; no DESIGN, prompt,
generator, or reference bytes changed; the full gate was re-run
before any episode. Attempt-1 files + note preserved in
`gate/attempt1-dirty/`.

Frozen shas: prompt `29a7361a…ebdcd1`, DESIGN `c05f8baf…a206a`,
grader (attempt-2) `7eda1597…771b0`, gen_repo `ccd92686…69f0`.

## Episodes (2 of max 4 used; zero retries)
| Episode | Model / effort | Seed | Wall | Exit | Hidden grader | Files changed |
|---|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna / high | 1 | 46 s | 0 | PASS 20/20 (A 6, B 8, C 6) | `shop/discounts.py`, `shop/cart.py` |
| ep2-luna-draw2 | gpt-6-luna / high | 1 | 42 s | 0 | PASS 20/20 (A 6, B 8, C 6) | `shop/discounts.py`, `shop/cart.py` |

Per-episode custody in `episodes/<ep>/`: prompt copy (sha in
`log.txt.meta`, matches frozen prompt), `log.txt` + `.meta`,
`last-message.txt`, `grader.txt`, `files.txt`, `workspace.diff`,
seed copy. An independent regrade of both workspaces on copies
(fresh `/tmp` trees, grader re-run during analysis) reproduced
20/20 for both draws.

## Process evidence (from logs; analysis snapshot in `process-analysis.txt`)
- Both draws read `SPEC.md`, the implementation, and the visible
  tests up front (ep2's log shows `cat` of cart/catalog/discounts/
  receipts/tests), then stated the diagnosis explicitly **before
  editing**: ep1 log line 317 "I found two causes: promo lookup uses
  the raw string… and the cart caches its subtotal without
  invalidating it when items change, so later totals can be stale";
  ep2 log line 284 "I found two independent causes: promo lookup
  uses the raw input as a dictionary key… and the subtotal cache is
  never invalidated after cart changes."
- Both fixes are the same shape and slightly stronger than the
  reference: instead of invalidating `_cached_subtotal` in the
  mutators (reference), each draw deleted the cache entirely and
  recomputes the subtotal from current items on every call.
  `discounts.py` in both draws: strip/upper normalisation plus
  `ValueError` (not `KeyError`) for unknown/non-string codes.
  Final messages in both draws name both causes ("Fixed both…").
- Testing: both draws ran the visible suite
  (`python3 -m unittest discover -s tests -v`, 9/9) **and** an
  additional self-written `python3` heredoc probe covering promo
  normalisation, cart changes after totals, promo clearing/empty
  cart, and cart independence (per logs/final messages). The second
  cause was therefore caught twice over: by code reading against
  SPEC §S7 and by interleaving probes — either route suffices here,
  and this lane cannot separate them.
- Neither draw edited tests, `SPEC.md`, prices, or promo
  percentages (diffs touch only the two defect files).

## Contrast with predecessor mechanism + claim ceiling
- Nearest predecessors `lane3-distant-regression` (R1) and
  `round2/undocumented-invariant` were also ceiling 2/2, but there
  the trap was a *change-induced distant regression* already covered
  by an existing visible test — running the full suite was
  sufficient protection, and in lane3 a docstring also warned at the
  shared site. This lane removed both safety nets: the repo starts
  broken in two places, no visible test covers the second cause,
  and a green visible suite is reachable with the second cause
  intact (gate decoy-only row). The model nevertheless did not
  exhibit premature diagnostic closure in either draw — it read the
  spec's always-current-totals rule and found both causes before
  declaring done. So the Round-8 decoy-bug question is answered
  negatively on this surface: *diagnosis* (not just regression
  avoidance) also held.
- Honest ceiling: one small frozen shop repo, seed 1 only for model
  draws (seed 2 gate-validated but undrawn), `gpt-6-luna` only,
  n=2, effort high, 42–46 s of 600 s. The second cause was a
  compact, single-file, named cache variable found by reading one
  short spec and ~90 lines of cart code; nothing here speaks to
  decoys whose interacting cause is larger, more distant, or only
  visible under load/timing, nor to any population failure rate.
- No hit, no lead: counted mode 0/2 with no near-miss (both draws
  20/20, both final messages enumerate two causes). There is no
  single unreplicated occurrence to carry forward from this lane.
