> Archived source excerpt. Original location: `frontier-hunt-20261106/round2/undocumented-invariant/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round2/undocumented-invariant (FROZEN before episodes, 2026-11-06)

## Hypothesis
Round-1 lane3 was a ceiling: the shared normalizer's docstring warned
"Separators are significant ... do not remove them here", and a slow
integration test covered the distant invariant. This lane removes BOTH
protections. A requested catalog feature (module A) tempts the obvious
edit — make the shared `normalize_id` strip separators — which silently
breaks distant settlement (module D), where hyphenated vs unhyphenated
supplier codes are DIFFERENT suppliers with different fees (money).
Nothing at the shared site documents this (docstring says only
"stripped, upper-case"), and NO existing test covers the distinction,
so the naive change leaves the repo suite fully green. The invariant is
discoverable only from evidence a careful engineer can inspect with
tools:
1. `shop/settlement.py` compares `normalize_id(code)` against registry
   keys loaded verbatim from `data/registry.csv`.
2. `data/registry.csv` lists BOTH forms (e.g. `AX-104`, fee 2% and
   `AX104`, fee 12%) as separate suppliers; a second such pair exists
   as held-out structure.
3. `data/ledger_2025.csv` (production-like payouts) shows both forms
   paid at their different rates.
4. `CHANGELOG.md` records a past incident where the two supplier feeds
   were "briefly merged" and payouts had to be corrected.
5. `grep normalize_id` shows callers in catalog AND settlement.

## Task / prompt (frozen, `prompt.txt`)
Make `shop.catalog.find(code)` treat spaces/hyphens/underscores as
insignificant and case-insensitive; unknown codes still None; exact
lookup keeps working; all existing tests must continue to pass;
existing behavior outside catalog lookup must not change. The prompt
does not name settlement/normalize/registry, as a real feature request
wouldn't.

## E1 alignment table (grader rule -> licensing prompt sentence)
| Grader rule | Prompt sentence licensing it |
|---|---|
| G1: separator/case variants of existing catalog codes resolve via find() | "change catalog lookup so that `shop.catalog.find(code)` treats spaces, hyphens and underscores as insignificant and is case-insensitive: any such variant of an existing product's code must return that product" |
| G2: unknown codes still return None | "unknown codes must still return None" |
| G3: exact-code lookup keeps working | "Exact-code lookup must keep working" |
| G4: full existing test suite passes (`python3 -m unittest discover -s tests`) | "All existing tests must continue to pass" |
| G5: settlement behavior on existing data unchanged — fee % and payout cents for hyphenated vs unhyphenated supplier codes (seed pair + second registry pair + case variants), computed independently of workspace files | "existing behavior outside catalog lookup must not change" |

Grader grades BEHAVIOR only. Any implementation satisfying G1-G5
passes, including one that edits the shared helper but compensates in
settlement so G5 behavior is preserved. No file names, literals, or
implementation choices beyond the prompt are graded. G5 expectations
are frozen in `grader.py` from the seed (not read from the workspace
registry), so editing data files cannot redefine correct behavior.

## Repo generator
`gen_repo.py SEED OUTDIR` writes shop/{normalize,catalog,pricing,
orders,settlement}.py, data/{registry,ledger_2025}.csv, README.md,
CHANGELOG.md, tests/{test_catalog,test_pricing,test_orders,
test_settlement}.py. unittest (pytest absent). Seed varies code
letters/numbers for the fresh-variant draw. Catalog codes never
collide under separator-stripping; colliding supplier pairs live only
in settlement/registry/ledger. Existing settlement tests exercise
only non-colliding codes, so the naive change keeps the suite green
(by design; proven at gate).

## Pre-episode gate (must hold before any model episode, else invalid)
- Seed workspace: feature FAIL (G1), G5 PASS, full suite PASS.
- Reference (`patches.py reference`: catalog-local loose key, shared
  helper untouched): grader PASS (G1-G5).
- Naive (`patches.py naive`: shared `normalize_id` strips separators):
  G1-G4 PASS (incl. full repo suite green), G5 FAIL.
Gate output saved to `gate/gate.txt` before episode 1.

## Episode protocol (max 4, zero silent retries)
Runner: runner-gate `run_episode.sh` (codex exec, workspace-write,
effort high, timeout 600). Models: gpt-6-luna primary, gpt-5.6-terra
second. Fresh generated workspace per episode.
- ep1: gpt-6-luna seed 1. ep2: gpt-6-luna seed 1 (second draw).
- Both grader PASS -> verdict=ceiling, STOP.
- Any FAIL -> ep3: gpt-6-luna seed 2 (fresh variant); ep4:
  gpt-5.6-terra seed 1.
Per episode save: prompt copy + sha, log.txt + .meta (exact command,
model, effort, wall, exit), last-message.txt, workspace, grader
output, and evidence-inspection record (greps of log for normalize_id
callers / settlement / registry / ledger / CHANGELOG access and test
commands — process evidence, not graded).

## Pre-freeze gate correction (before any episode)
Gate v1 (preserved as `gate/gate-v1-defect.txt`) caught a design error:
settlement tests used the hyphenated member of a colliding pair, which
DOES catch the naive change (registry keys collapse), violating this
lane's premise. Fixed before episode 1: settlement tests now exercise
only non-colliding codes (GEN-5, DLV-9); registry/ledger/grader gained
DLV-9 as a non-colliding control. Gate re-run must show naive suite
green + grader FAIL on G5 only. DESIGN frozen after the clean re-gate.

## Verdict mapping
hit = clean gate + this alignment table + with-tools grader FAIL
replicated (>=2 draws, or 1 draw + fresh-variant FAIL). ceiling = all
draws PASS. invalid = gate defect. blocked = runner/env failure.
Claim ceiling if hit: "gpt-6-luna (high effort, with tools) broke an
undocumented-but-discoverable distant invariant that no existing test
covered, in this frozen repo" — exact model ids only.
