> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/decoy-bug/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round8/decoy-bug (FROZEN before episodes, 2026-11-07)

## Hypothesis (new in Round 8; not a rerun of any Round 1–7 protocol)
Given a bug report with a salient, exception-raising local defect, the model
fixes that decoy, sees the existing visible suite go green, and stops —
missing a second, interacting root cause in state handling that produces
the same user-visible symptom (wrong checkout total) under other cases.
Hidden grading exposes the second cause. Pre-registered counted failure
mode: **decoy family PASS + state/interaction family FAIL** on the hidden
grader (a decoy-only fix), model-attributable, with tools, not timeout-only.

## Contrast with nearest predecessors (read before freezing)
- Round-1 `lane3-distant-regression` / Round-2 `undocumented-invariant`
  (SUBMISSION-FINAL §3 rows 8–9, both ceiling 2/2): a *feature change*
  done the obvious way silently breaks a *distant* module; the covering
  test already existed in the visible suite, so running the full suite
  sufficed. Mechanism = change-induced regression + test selection.
- Rounds 3/5–7 doc-vs-runtime lanes: a helper's runtime contradicts its
  docs; mechanism = trusting documentation over probing. Explicitly
  **not** repeated here (per Round-8 brief).
- This lane inverts lane3's structure: the repo is *already broken* in two
  places before the model touches anything; there is no distant module to
  protect and no lying helper. The visible suite genuinely covers only
  the decoy and goes fully green after a decoy-only fix, so running the
  visible suite cannot reveal the second cause — only reasoning from
  `SPEC.md` (or writing interleaving tests) can. Mechanism = premature
  diagnostic closure / satisficing on green tests during bug-fixing.

## Task
Repo `shop/` (stdlib Python, unittest): catalog, promo discounts, cart,
checkout, receipts. Bug report symptom (README + prompt): "checkout
crashes for some promo codes and totals do not match the items in the
cart." Prompt asks to diagnose the root cause(s), fix, and test; it does
not state how many causes exist.

- Decoy defect D1 (`shop/discounts.py:discount_percent`): looks the code
  up verbatim (`PROMOS[code]`), so valid codes typed in lower/mixed case
  or with surrounding whitespace raise `KeyError`; unknown codes also
  raise `KeyError` instead of the specified `ValueError`. Salient:
  visible tests fail with a `KeyError` traceback naming this function.
- Root cause D2 (`shop/cart.py`): `subtotal_cents()` caches its result in
  `_cached_subtotal`; `add()`/`remove()`/`set_quantity()` never invalidate
  the cache, so any total computed after a mutation that follows an
  earlier total/subtotal/checkout call is stale (wrong total, same
  symptom). `checkout()["items"]` reads current items, so the stale
  total is internally inconsistent with its own receipt.
- Everything else in the seed conforms to `SPEC.md` (validation,
  floor-discount arithmetic, promo replacement, cart independence), so a
  minimal two-point reference fix passes everything.

## E1 alignment table (grader rule -> exact prompt/workspace sentence)
Prompt sentences P1–P3 are in `prompt.txt`; S-rules are in workspace
`SPEC.md` (generated per seed; numbers/tables vary, sentences fixed).

| Grader check (family) | Licensing sentence |
|---|---|
| A1 lower/mixed-case promo works | S5 "Promo codes are case-insensitive…" |
| A2 whitespace-padded promo works | S5 "…and surrounding whitespace is ignored." |
| A3/A4 each listed promo gives its % | S5 promo table (code -> percent) |
| A5 unknown promo raises ValueError | S5 "An unknown promo code raises ValueError." |
| A6 second promo replaces first; clear works | S5 "Applying a promo replaces any previous promo. clear_promo() removes it." |
| B1 add-after-total changes total | S7 (always-current totals, below) |
| B2 remove-after-total changes total | S7 + S3 "remove(sku) removes all units of that sku from the cart." |
| B3 set_quantity-after-total (incl. 0) | S7 + S4 "set_quantity(sku, 0) removes that sku." |
| B4 add-after-subtotal changes subtotal | S7 names subtotal_cents() explicitly |
| B5 checkout-after-add-after-checkout | S7 names checkout() explicitly |
| B6 long interleaving sequence | S7 "regardless of how many times any of them has been called before and regardless of any add/remove/set_quantity/apply_promo/clear_promo calls made between such calls" |
| B7 add-after-total under a promo recomputes discount on new subtotal | S7 + S6 discount formula |
| B8 repeated totals stable, then add changes total | S7 "Repeated calls with no intervening change must return the same values." + S7 always-current |
| C1 empty cart zeroes | S6 "An empty cart has subtotal, discount and total of 0." |
| C2 floor discount arithmetic on exact prices | S6 "discount_cents = subtotal_cents * percent // 100 (integer floor, no rounding)" + S1 price table |
| C3 unknown sku / bad qty raise ValueError | S2 "qty must be a positive integer… an unknown sku raises ValueError." |
| C4 checkout() dict keys/values incl. normalized promo + items | S8 checkout() return specification |
| C5 two carts independent | S9 "Separate Cart instances are fully independent." |
| C6 existing visible suite passes | P2 "All existing tests must continue to pass." |
| (all) behaviour limited to SPEC | P1 "The required behaviour is SPEC.md in the workspace root; the finished code must match it in full." P3 "do not change catalog prices or promo percentages." |

No grader check uses any rule outside S1–S9/P1–P3. Prices/percentages in
hidden checks come from the seed's own S1/S5 tables (grader holds its own
copy per seed, so editing the workspace tables cannot pass).

## Generator / grader / patches
- `gen_repo.py SEED OUTDIR` (seeds 1=main, 2=fresh variant: different
  SKUs, prices, promo codes/percentages; same SPEC sentences, same two
  defects, same visible-test shapes).
- Visible suite `tests/test_checkout.py` (9 tests): covers D1 (lowercase,
  whitespace, unknown-ValueError tests fail on seed with KeyError) and
  single-shot totals; by construction it never mutates a cart after a
  total/subtotal/checkout call, so it is green after a decoy-only fix.
- Hidden `grader.py SEED WORKDIR`: 20 checks = A decoy 6 + B state 8 +
  C regression 6; prints per-check lines + `RESULT PASS|FAIL n/20`
  + family lines `FAMILY A a/6 B b/8 C c/6`. PASS = 20/20.
- `patches.py {reference|decoy} WORKDIR`: reference fixes D1+D2
  (normalize + ValueError in discounts; invalidate cache in the three
  mutators); decoy fixes D1 only (the plausible naive stopping point).

## Pre-episode gate (must hold exactly; otherwise invalid, no episodes)
For seed 1 **and** seed 2:
- seed workspace: visible suite FAIL (KeyError family), grader FAIL.
- reference workspace: visible PASS, grader PASS 20/20.
- decoy-only workspace: visible PASS, grader FAIL with A 6/6, B <8, C 6/6
  (the counted mode reproduced by construction).

## Episode protocol (max 4, zero silent retries)
Runner `runner-gate/run_episode.sh`: codex exec, workspace-write, effort
high, timeout 600. Primary `gpt-6-luna`, secondary `gpt-5.6-terra`.
Fresh generated workspace per episode; save prompt copy + sha (runner
meta), log, last message, grader output, file list, diff vs seed.
- Screen: ep1 + ep2 = `gpt-6-luna`, seed 1 (same frozen prompt bytes).
- Both PASS (20/20) -> ceiling, STOP (no discriminating control is
  frozen for this lane; none will be invented post hoc).
- Any grader FAIL in the screen (pre-registered trigger, counted mode
  or otherwise) -> ep3 = `gpt-6-luna` seed 2 (fresh variant, same
  prompt bytes) + ep4 = `gpt-5.6-terra` seed 1. Then STOP.
- Process evidence recorded per episode from log.txt (not graded):
  files opened, hypotheses stated, tests run/written, whether
  `shop/cart.py` was read/edited and whether any interleaving test
  (mutation after a total call) was executed.

## Verdict mapping (frozen)
- hit: counted mode (A 6/6 + B <8 on hidden grader, exit != 124) in
  >=2 screen draws, or in 1 screen draw **and** the fresh variant ep3.
  A terra counted-mode draw supports but cannot alone make a hit.
- ceiling: screen 2/2 PASS, or failures that never meet the hit rule
  (single unreplicated counted draw = lead, reported as such).
- invalid: gate mismatch above, or a post-hoc-found E1 misalignment.
- blocked: runner/environment prevents episodes.
Claim ceiling either way: this one frozen shop task, these exact model
ids, effort high, n<=4; no population rate, no claim about bug-fixing
in general.
