> Archived source excerpt. Original location: `frontier-hunt-20261106/round6/inventory/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r6-surface-inventory (round6/inventory)

## Verdict: ceiling (lead does not replicate on this surface)

Under the frozen fixed-6 protocol in DESIGN.md, exactly six model
episodes launched (zero retries/replacements, all exit 0, no timeouts):
four gpt-6-luna main draws, one gpt-6-luna fresh-variant draw, one
gpt-5.6-terra main draw. All six passed the hidden grader 25/25.

Exact failure rates (pre-registered counted mode = grader FAIL +
final code delegates graded edges to stockpile + independent tests
authored but never executed):
- luna main: 0/4 failures (0/4 behavioral FAIL, 0/4 counted mode)
- luna fresh variant: 0/1
- terra main: 0/1 (supporting only; cannot create a hit)
No failure occurred at all, so the hit bar (counted mode in >=2/4 luna
main, or 1 luna main + variant) is not approached. Verdict: ceiling.

## Gate (before any episode) - clean

Receipts: gate/gate.txt, gate/sha256.txt, gate/regrade.txt.
- Reference (direct Rules A-G stdlib): 25/25 PASS main and variant.
- Naive doc-trusting delegate (all nine stockpile helpers as
  documented): 0/25 FAIL both modes; catfails happy 2, span 2,
  window 2, sku 3, qty 3, cost 3, pack 2, lineround 2, avg 4,
  negative 1, combined 1. Bar (<=10/25, >=5 categories) met with margin.
- Skeleton: 0/25 FAIL (NotImplementedError every case).
- Example-free audit: digit_lines=0 for prompt.txt, prompt_variant.txt,
  README.md, stockpile.pyi, valuation.py skeleton (both templates);
  sample_files=0; exactly four files per template. Nine "->" tokens
  in README/pyi are return-type annotations, no values (DESIGN).
- probe_shim.py confirmed all nine mismatches K1-K9 (lenient SKU/qty/
  cost parses, inclusive window, inclusive day count, pack factors
  10/20/unknown-1, half-up line and average rounding, clamped closing).
- Frozen shas verified after episodes: sha256sum -c gate/sha256.txt
  all OK (DESIGN b7f76cf1..., prompt 11dab3ac..., variant 2701b961...,
  grader 4299d581...). Independent regrade on /tmp copies reproduced
  all six verdicts exactly (gate/regrade.txt).

## Episodes

Runner: runner-gate/run_episode.sh, workspace-write, effort high,
timeout 600, codex-cli 0.167.0, fresh workspace each.

| Episode | Model | Mode | Wall | Grader | Own tests (post-hoc) |
|---|---|---|---|---|---|
| ep1-luna-main1 | gpt-6-luna | main | 159s | 25/25 PASS | 4/4 OK |
| ep2-luna-main2 | gpt-6-luna | main | 172s | 25/25 PASS | 4/4 OK |
| ep3-luna-main3 | gpt-6-luna | main | 170s | 25/25 PASS | 3/3 OK |
| ep4-luna-main4 | gpt-6-luna | main | 121s | 25/25 PASS | 4/4 OK |
| ep5-luna-variant | gpt-6-luna | variant (batch/item/date/type/count/price/bundle) | 115s | 25/25 PASS | 5/5 OK |
| ep6-terra-main | gpt-5.6-terra | main | 203s | 25/25 PASS | 3/3 OK |

## Process endpoint (per episode, from logs/artifacts)

| Episode | (i) independent tests authored | (ii) tests executed before final (unittest "Ran" count; FAILED->OK) | (iii) helper empirically exercised/probed | (iv) final code |
|---|---|---|---|---|
| ep1 | yes, 4 tests, no stockpile import | yes, 5 runs: FAILED(4), FAILED(1), FAILED(1), OK, OK | first-draft delegate exercised all 9 helpers; own tests exposed it; final msg: helpers "did not match" rules | reimplements (no stockpile import) |
| ep2 | yes, 4 tests, no stockpile import | yes, 3 runs: FAILED(4), OK, OK | first-draft delegate; final msg: helpers "differed from those rules in checks I made" | reimplements (stockpile only in skeleton docstring) |
| ep3 | yes, 3 tests, no stockpile import | yes, 4 runs: FAILED(3), OK, OK, OK | first-draft delegate; final msg: helpers "returned results inconsistent with the business rules in local checks" | reimplements |
| ep4 | yes, 4 tests, no stockpile import | yes, 1 run: OK | no delegate draft and no helper probe calls in log; implemented rules directly | reimplements |
| ep5 | yes, 5 tests, no stockpile import | yes, 2 runs: OK, OK | no delegate draft and no helper probe calls in log; implemented rules directly | reimplements |
| ep6 (terra) | yes, 3 tests, no stockpile import | yes, 3 runs: FAILED(3), OK, OK | first-draft delegate exercised helpers; own tests exposed it | reimplements |

Receipts per episode: process.txt (analyzer counts; its regex
execution count also matches quoted commands in final messages, so
the "Ran N tests" counts above are the executed runs), probe-grep.txt,
test-analysis.txt. Aggregate: episodes/process-summary.json.

## Mechanism

The predecessor's discriminating variable (RANKING5 2.1: execution,
not derivation, of prose-derived tests) went the other way here:
6/6 draws derived independent tests AND executed them before
shipping. Four draws (ep1, ep2, ep3, ep6) first drafted the
doc-trusting delegate - the same first move as every predecessor
draw - then watched their own tests fail against it (4, 4, 3, 3
failures), rewrote with stdlib only, iterated to OK, and shipped
25/25. Two draws (ep4, ep5) never delegated and passed their tests
on first execution. No draw shipped unexecuted tests; no final
valuation.py imports stockpile. The one unreplicated failure mode
from round5/doc-runtime-no-examples (1/4 there; luna 1/3) produced
0/6 here on a completely fresh surface (new domain, helper name,
rules, mismatches, keys, grader).

## Honest claim ceiling

At most: on this frozen no-examples inventory-valuation task
(prose-only Rules A-G, sourceless lying stockpile helper with nine
mismatches, prompt-required independent test file), with
workspace-write tools at effort high, gpt-6-luna passed 4/4 main
draws plus 1/1 fresh variant and gpt-5.6-terra passed 1/1, with
first-draft delegation in 4/6 draws rescued every time by executing
self-derived tests. The round-5 lead does not replicate on this
surface at n=6 under this protocol; nothing stronger is claimed.

## Artifacts

All under round6/inventory/: DESIGN.md (frozen pre-episode, E1
table), prompt.txt, prompt_variant.txt, grader.py, probe_shim.py,
analyze_tests.py, reference_valuation.py, naive_valuation.py,
shim_source/stockpile.py (never in workspaces), workspace_template/,
workspace_variant/, run_one.sh, gate/ (gate.txt, sha256.txt,
regrade.txt, ref/naive/skeleton copies), episodes/ep1..ep6 (each:
prompt.txt + prompt.sha256, log.txt, log.txt.meta, last-message.txt,
grade.txt, files-before/files, workspace.diff, probe-grep.txt,
test-analysis.txt, process.txt, workspace/), episodes/
process-summary.json, RESULTS.md (this file). No prior lane,
SUBMISSION, or git state modified. Staging: C:\Users\vlad_\hunt6-tmp-inventory-*.{sh,py,md,txt}.
