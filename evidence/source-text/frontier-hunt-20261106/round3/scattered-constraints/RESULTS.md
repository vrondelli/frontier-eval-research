> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/scattered-constraints/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — r3-scattered-constraints

**Verdict: ceiling.** Both frozen gpt-6-luna screen draws PASSED the hidden
grader 21/21 on fresh 181-file workspaces, finding and applying all five
scattered constraints. Per the frozen screen protocol (both pass => ceiling
STOP), no variant or gpt-5.6-terra episode was run. Total episodes: 2.
Zero retries; every attempt recorded below.

## Gate (before any episode; `gate/gate-output.txt`)
- Workspace generator `gen_workspace.py` seed 42: 11 core + 170 generated
  filler = 181 files (filler programmatic, seeded, not hand-written).
- Reference (`reference_export.py`): **RESULT PASS 21/21**; existing basic
  tests 3 passed (pytest absent in WSL; run by direct import).
- Naive headline-only (`naive_export.py`): **RESULT FAIL 11/21** — fails 10
  checks spanning all five constraints (C1b, C2a, C2c, C3a-c, C4a-b, C5a-b).
- Findability on the pristine stub workspace: each constraint string occurs
  in exactly 1 file (compliance md / billing.ini / data-dictionary /
  CHANGELOG / legacy comment); `grep -ril export` lists 8 files including
  all five constraint files.
- Disclosure: one pre-episode gate repair — a 21st check (C1d, 2.365
  half-up vs banker's) was added and the findability grep was retargeted
  from the reference workspace to a pristine one. Gate was fully re-run
  clean before any episode; DESIGN.md counts updated at the same time and
  then frozen (DESIGN sha 41fc70d4…, prompt sha 6b6b1cba… in gate log).

## Episodes (900s cap per DESIGN, effort high, workspace-write)

| Episode | Model | Wall | Exit | Grader | Constraint files evidenced in log |
|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 53s | 0 | PASS 21/21 | billing-compliance.md x12, billing.ini x8, data-dictionary.md x16, CHANGELOG.md x4, pricing_notes.py x4 |
| ep2-luna-draw2 | gpt-6-luna | 61s | 0 | PASS 21/21 | billing-compliance.md x18, billing.ini x12, data-dictionary.md x22, CHANGELOG.md x5, pricing_notes.py x5 |

Per-episode receipts in `episodes/<id>/`: prompt.txt + prompt.sha256
(6b6b1cba… both), log.txt + log.txt.meta (codex-cli 0.167.0, exact
command, 900s), last-message.txt, grader-output.txt, changed-files.txt
(only `billing/export.py` differs from pristine, plus `__pycache__`),
constraint-access.txt, gen.txt, runner-exit.txt.

Both implementations independently parsed `config/billing.ini` for the
export timezone, used `Decimal` + `ROUND_HALF_UP`, mapped SENT/SETTLED
aliases, filtered the exportable status set, and clamped to
[0.00, 10000.00] — i.e. the with-tools search the hypothesis bet against
happened in ~1 minute per draw, with the prompt explicitly licensing
docs/configs as authoritative and telling the model to search thoroughly.

## Honest claim ceiling
Under this frozen, E1-aligned protocol (explicit prompt license to search,
181 files, constraints each greppably keyed to ticket keywords), gpt-6-luna
with tools finds scattered constraints reliably in 2/2 draws. This lane
replicates the Rounds 1-2 lesson: once the prompt tells the model that repo
docs are authoritative, a single repo-wide grep defeats scattering — the
placed files were 8 of 181 for the keyword `export`. A harder successor
would need constraints that are NOT keyword-greppable from the ticket
(e.g. reachable only by following cross-references, or contradicted by a
stale doc the solver must adjudicate), which this protocol deliberately
excluded for fairness. No submission-worthy failure here; claim is
protocol-indexed, n=2, one model id (terra unrun per stop rule).
