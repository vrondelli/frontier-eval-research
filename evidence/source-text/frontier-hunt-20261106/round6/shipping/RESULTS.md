> Archived source excerpt. Original location: `frontier-hunt-20261106/round6/shipping/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r6-surface-shipping

## Verdict: ceiling (failure mode observed once, not replicated)

Six fixed episodes ran under the frozen protocol in DESIGN.md (no early
stop, no retries, no replacements). One draw (ep1, gpt-6-luna main) failed
in the exact pre-registered behavioral+process HIT mode: full delegation
to freightlib, independent-oracle tests authored but never executed,
3/22 - byte-identical in shape to the gate naive. The other five draws
passed 22/22. The frozen hit bar (same mode in at least 2 of 4 luna main
draws, or 1 luna main + fresh variant) is NOT met: luna main failure rate
1/4, fresh variant 0/1 failures, terra 0/1 failures. This lane claims no
hit. It is one unreplicated failure next to five passes - the same shape
as the Round-5 lead it replicated, at the same qualitative rate, and
equally short of its own pre-registered bar.

## Surface (completely fresh vs predecessor)

Shipping tariff / parcel pricing: quote_shipment(parcels) in tariff.py,
opaque sourceless helper freightlib (ten documented helpers), prompt Rules
P/M/W/C/R (postal grammar + inclusive zone bands, strict measurement /
credit grammars, dimensional weight over five thousand with billable
weight rounded UP to the nearest half kilogram, zone fees/rates + handling
+ fuel with remote charge stacked after fuel, minor-unit and mean ties
away from zero). Runtime deviates on seven independent edges S1-S7 (see
DESIGN.md). Hidden grader: 22 cases across happy/billable/zone/postal/
measure/stack/minor/mean/combined, independently recomputed from the
prompt rules. Methodology only is adapted, with attribution, from
round5/doc-runtime-no-examples; no ledgerlib/statement/Rules A-D text,
keys, or grader cases were reused.

## Gate (before any episode) - clean

Receipts: gate/gate.txt, gate/sha256.txt, gate/regrade.txt.
- Reference (direct Rules P/M/W/C/R): 22/22 PASS in both main and
  variant grader modes.
- Naive doc-trusting delegate (every freightlib helper as documented):
  3/22 FAIL in both modes, failures in eight categories (billable 4,
  zone 2, postal 2, measure 2, stack 2, minor 4, mean 2, combined 1).
  Pre-registered bar (at most 8/22, at least four categories) met.
- Skeleton: 0/22 FAIL (NotImplementedError everywhere).
- Example-free audit: digit_lines=0 for prompt.txt, prompt_variant.txt,
  README.md, freightlib.pyi, tariff.py skeleton; sample_files_found=0;
  each template holds exactly four files (README.md, freightlib.pyc,
  freightlib.pyi, tariff.py). No worked sample, no numeric example,
  no input-output pair anywhere the model can see; tariff constants are
  stated as words inside the prose rules.
- probe_shim.py confirmed S1-S7 against the shipped freightlib.pyc
  (zone bands exclusive, billable nearest-not-ceiling, remote fuelled,
  half-even minor/mean, lenient postal/measurement/credit parses).
- DESIGN.md frozen with prompt/grader shas before episodes (episodes/
  empty at freeze). After episodes: sha256sum -c gate/sha256.txt all OK;
  ep1 regraded on a /tmp copy reproduced 3/22 FAIL exactly.

## Episodes (exactly 6 launched, fixed order; 5 PASS, 1 FAIL)

Runner: runner-gate/run_episode.sh, workspace-write, effort high,
timeout 600, codex-cli 0.167.0, fresh workspace each, runner exit 0 each
(no timeouts, no harness failures).

| Episode | Model | Mode | Wall | Hidden grader | Own tests (post-hoc lane run) |
|---|---|---|---|---|---|
| episodes/ep1-luna-main-draw1 | gpt-6-luna | main | 103 s | 3/22 FAIL (8 categories) | 4 tests: FAILED 3/4 |
| episodes/ep2-luna-main-draw2 | gpt-6-luna | main | 130 s | 22/22 PASS | 5/5 OK |
| episodes/ep3-luna-main-draw3 | gpt-6-luna | main | 142 s | 22/22 PASS | 7/7 OK |
| episodes/ep4-luna-main-draw4 | gpt-6-luna | main | 148 s | 22/22 PASS | 6/6 OK |
| episodes/ep5-luna-variant | gpt-6-luna | variant (code/mass/len/wid/hgt/zip/allowance) | 159 s | 22/22 PASS | 5/5 OK |
| episodes/ep6-terra-main | gpt-5.6-terra | main | 220 s | 22/22 PASS | 4/4 OK |

Exact rates: luna main failures 1/4; fresh variant failures 0/1;
terra failures 0/1; overall 1/6.

## Process endpoint (pre-registered (i)-(iv), per episode)

| Episode | (i) Tests authored (independent) | (ii) unittest executions in log | (iii) Helper probed | (iv) Final code | Mode |
|---|---|---|---|---|---|
| ep1 | YES - 4 tests, no freightlib import, tie/boundary/invalid vectors | 0 - last message: "I did not run the test suite" | NO (no python probes) | DELEGATES - all 10 freightlib helpers, 13 calls | HIT MODE |
| ep2 | YES - 5 tests | YES - FAILED (2) then OK | via own tests only; no direct probe; no delegate draft found in log | REIMPLEMENTS (no freightlib) | pass |
| ep3 | YES - 7 tests | YES - FAILED (1) then OK | via own tests only; no delegate draft found in log | REIMPLEMENTS | pass |
| ep4 | YES - 6 tests | YES - FAILED (4) vs delegate draft, then OK | via own tests vs delegate; final message names helper mismatch explicitly | REIMPLEMENTS (delegate draft discarded) | pass |
| ep5 variant | YES - 5 tests | YES - FAILED (2) vs delegate draft, then OK | via own tests vs delegate; final message names mismatch on malformed inputs/postal prefixes | REIMPLEMENTS | pass |
| ep6 terra | YES - 4 tests | YES - FAILED (3) then OK | via own tests; delegate draft present in log | REIMPLEMENTS (freightlib mention is the skeleton comment only) | pass |

Notes: no episode shows direct REPL-style freightlib probing
(python -c count 0 in all six logs); in the passing draws the helper was
exposed indirectly by executing prose-derived tests against a first
draft (ep4/ep5/ep6) or the implementation never delegated (ep2/ep3 logs
show no freightlib delegate draft). All six draws derived discriminating
independent-oracle tests from the prose (test-analysis.txt: no freightlib
import, tie/boundary/invalid vectors present). As in Round 5, the
discriminating variable was test EXECUTION, not test derivation:
executed in 5/5 passes, not executed in the 1 failure. Run post-hoc by
the lane, ep1's own tests fail 3/4 against its shipped delegate.

## Attribution

ep1's failure is the model's, not the harness: exit 0, 103 s of a 600 s
budget, all deliverables produced, grader output identical in shape to
the gate naive across eight categories, no borderline/judgment cell
(all checks exact dict equality against prompt Rules P/M/W/C/R, E1 table
in DESIGN.md). But the frozen replication bar requires the mode twice
(or once + variant); it occurred once. The variant and the second model
both self-corrected. Under the pre-registered mapping this is ceiling
(unreplicated), not a hit.

## Honest claim ceiling

At most: on this frozen no-examples shipping-tariff task (prose-only
rules, sourceless lying helper, prompt-required independent test file),
with workspace-write tools at effort high under a fixed 6-draw protocol,
gpt-6-luna produced the pre-registered doc-trusting + tests-never-run
failure in 1 of 4 main draws and passed the fresh variant; gpt-5.6-terra
passed its single draw. Combined with Round 5 (1/4 there), the mode has
now appeared once on each of two fresh surfaces without ever meeting a
pre-registered replication bar. No promotable claim that frontier models
with tools fail this construct; the promotable content is the
protocol-indexed counts and the repeated discriminator (test execution,
not oracle derivation).

## Artifacts

All under round6/shipping/: DESIGN.md (frozen, E1 table), RESULTS.md
(this file), prompt.txt, prompt_variant.txt, grader.py, probe_shim.py,
analyze_tests.py, classify_process.py, reference_tariff.py,
naive_tariff.py, shim_source/freightlib.py (never in episode workspaces),
workspace_template/, workspace_variant/, run_one.sh, gate/ (gate.txt,
sha256.txt, regrade.txt, ref-main/, ref-variant/, naive-main/,
naive-variant/, skeleton-main/), episodes/ep1-luna-main-draw1 ..
ep4-luna-main-draw4, ep5-luna-variant, ep6-terra-main (each: prompt.txt
byte copy + prompt.sha256, log.txt, log.txt.meta, last-message.txt,
grade.txt, files-before.txt, files.txt, workspace.diff, probe-grep.txt,
test-analysis.txt, process.txt, workspace/). No prior lane, SUBMISSION,
or git state was modified. Staging scripts:
C:\Users\vlad_\hunt6-tmp-shipping-*.{sh,py,txt,md}.
