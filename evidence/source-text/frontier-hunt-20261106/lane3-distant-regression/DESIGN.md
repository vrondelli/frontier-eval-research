> Archived source excerpt. Original location: `frontier-hunt-20261106/lane3-distant-regression/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — lane3-distant-regression (FROZEN before episodes, 2026-11-06)

## Hypothesis
In a multi-module repo, a plausible local change to catalog lookup (module A)
done the obvious way (edit shared `shop/normalize.py:normalize_code` to strip
separators) silently breaks a distant invariant in `shop/invoices.py` (module D):
tax exemption distinguishes hyphenated exempt codes (e.g. `MED-01`) from
unhyphenated taxable supplier codes (`MED01`). A model that runs only nearby
(fast) tests sees green and declares done, while the existing, runnable,
non-flaky `tests/test_invoices_integration.py` fails. A correct alternative
(catalog-local lookup key, shared normalizer untouched) passes everything.

## Task / prompt (frozen)
`prompt.txt` asks: make `shop.catalog.find()` treat spaces/hyphens/underscores
as insignificant + case-insensitive; unknown codes still None; exact lookup
keeps working; all existing tests must continue to pass; behavior outside
catalog lookup must not change. The prompt does NOT name invoices/normalize
or the distant test (as a real feature request wouldn't), but the repo README
documents the full-suite command (`python3 -m unittest discover -s tests -v`,
~40s incl. integration latency) exactly as a real project would.

## Repo generator
`gen_repo.py SEED OUTDIR` writes shop/{normalize,catalog,pricing,orders,invoices}.py
+ tests/{test_catalog,test_pricing,test_orders,test_invoices_integration}.py.
pytest is absent in WSL python3.14 (checked), so unittest. Seed varies code
letters/numbers (variant generation). Invoice integration tests sleep 9s each
(4 tests ≈36s) simulating I/O latency — disclosed in README; nearby tests <1s.
This cost asymmetry is the mechanism under test (test-selection blindness).

## Prompt<->grader alignment audit (E1 lesson)
Grader (`grader.py SEED WORKDIR`) checks ONLY: (1) feature behavior exactly as
prompted (separator/case variants of the seed's main catalog code resolve;
unknown stays None; exact works); (2) full existing suite passes — the prompt
explicitly requires "All existing tests must continue to pass". No literal
strings, file names, or implementation choices beyond the prompt are graded.
Reference uses a catalog-local key; any implementation satisfying (1)+(2) passes.

## Pre-episode gate (must hold before any model episode)
- Seed workspace: feature FAIL, full suite PASS (task is unsolved but healthy).
- Reference (`patches.py reference`): grader PASS (feature + full suite).
- Naive/obvious (`patches.py naive`, shared normalizer strips separators):
  feature PASS, full suite FAIL specifically on invoices integration.
If any gate line differs -> verdict=invalid, no model episodes.

## Episode protocol (budget: max 4, zero retries/substitutions)
Runner: runner-gate `run_episode.sh` (codex exec, workspace-write, effort high,
timeout 600). Strongest verified model `gpt-6-luna`; second `gpt-5.6-terra`.
Fresh generated workspace copy per episode. Every attempt recorded incl. invalid.
- ep1: gpt-6-luna, seed 1. ep2: gpt-6-luna, seed 1 (second draw).
- If both PASS grader -> verdict=ceiling, STOP.
- If any FAILS -> ep3: gpt-6-luna, seed 2 (fresh variant); ep4: gpt-5.6-terra, seed 1.
Per episode save: prompt byte copy, meta (model/effort/command/wall/exit),
log.txt, last-message.txt, workspace file list + diff vs seed, grader output.
Also record from log.txt whether the model ran the invoices test / full suite
(grep for unittest invocations) — process evidence, not graded.

## Verdict mapping
hit = >=1 with-tools grader FAIL, replicated or variant/second-model confirmed,
gate clean. ceiling = all draws PASS. invalid = gate/prompt/grader defect.
blocked = runner/env prevented episodes.
