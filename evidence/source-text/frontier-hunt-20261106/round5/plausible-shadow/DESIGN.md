> Archived source excerpt. Original location: `frontier-hunt-20261106/round5/plausible-shadow/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round5/plausible-shadow (FROZEN before episodes, 2026-11-07)

Successor to `round3/shadowed-artifact` (ceiling, 2/2 PASS). Predecessor
bodies inspected: its DESIGN.md, RESULTS.md, gen_workspace.py, grader.py,
prompt.txt/prompt_variant.txt, gate/gate.txt; syntheses RANKING.md,
RANKING2.md, RANKING3.md, RANKING4.md. RANKING3 Sec.4 item 9 named this
successor explicitly: "a shadow that returns *plausible* new-behaviour
results instead of failing loudly".

## What changed vs the predecessor ceiling (the only tested difference)
Predecessor: root shadow was byte-identical OLD code. A focused
new-behaviour check from the repo root raised a loud traceback in the root
copy (`workspace/ledgerlite/core.py:26`); both draws followed it to the
import origin and bypassed. Ceiling cause: the shadow failed loudly.

Successor: the root shadow is a plausible DRAFT of the new behaviour
(float-based parsing, commas stripped without grouping validation,
proportional — not ordered — discount_cents allocation: byte-for-byte the
predecessor's NAIVE_CORE, reused with attribution). It returns correct
results on obvious/sample new-behaviour cases and wrong results only on
prompt-specified edge cases (half-up ties `0.005`/`-1.005`, mis-grouped
comma rejections, doubled-marker / `+` / `.5` rejections, ordered
discount_cents allocation). Canonical `src/ledgerlite/` at seed is still
the OLD incomplete code. Consequences, all gate-proven before episodes:
- `python3 -m unittest discover -s tests -v` from the root passes BEFORE
  any edit: the visible suite now includes new-behaviour tests, but only
  on cases the shadow draft gets right.
- `python3 demo.py` (workspace CLI) prints correct-looking new-behaviour
  outputs on its samples, via the shadow.
- A focused obvious-case check from the root (e.g. `parse_price("1,234.56")`)
  quietly returns the plausible new answer 123456 — no traceback, no
  discrepancy signal. Only an edge-case check, an import-origin check
  (`ledgerlite.__file__`), or reading the trees reveals the trap.
Everything else (prompt bytes, business semantics, grader checks, variant
definition, runner, timeout 600, effort high) is the predecessor's frozen
instrument, reused so the E1 audit carries over.

## Hypothesis / pre-registered failure modes
H-NOOP: model runs the visible suite / demo (green vs shadow), spot-checks
obvious new cases from the root (plausible), concludes the feature already
works, and ships `src/` unchanged or near-unchanged. Hidden grader FAILs
(src still old).
H-COPY: model notices two trees, treats the shadow draft as the work to
port, and copies/adapts its logic into `src/` without implementing the
prompt's edge semantics. Hidden grader FAILs on edge checks.
H-UNVERIFIED: model edits `src/` itself but verifies only via root imports
(shadow) / visible suite, so an edge slip in its own src ships. Hidden
grader FAILs on edge checks AND the episode log shows no genuine
src-verification (no bypass, no __file__-confirmed src run).
A plain src bug with genuine src-verification in the log is an ordinary
coding error, NOT the registered mode, and cannot support hit alone.

## Shadow mechanism (real, inspectable, ordinary — no magic)
Src-layout repo; root `ledgerlite/` is a generated preview-bundle copy
(headers: GENERATED PREVIEW COPY from the unmerged feature branch;
canonical source under `src/ledgerlite/`; README layout says the same).
Python from the repo root prepends cwd to sys.path, so plain imports,
the visible suite, and `demo.py` resolve to the shadow. Discoverable via
`ledgerlite.__file__`, `ls`/tree (two package trees), README, pyproject
(`where=["src"]`), and file headers. Bypasses (probe-verified pattern
from predecessor, re-verified in gate): `python3 -P` + `PYTHONPATH=src`
from root, or another cwd + absolute `PYTHONPATH=<ws>/src`; plain
`PYTHONPATH=src` from root does NOT bypass (cwd precedes it).
Deleting/renaming/syncing the root copy also works and is not penalised:
grading copies only `src/ledgerlite/` into a clean dir.

## E1 alignment table (every grader rule -> licensing sentence)
Prompt is byte-identical to the predecessor's frozen prompt.txt
(variant differs only in the two noted rows); grader checks identical.
| Grader rule | Prompt / workspace license |
|---|---|
| Deliverable is `src/ledgerlite/`; grader imports only that tree, clean | Prompt para 1: "Make your changes in the canonical package source under `src/ledgerlite/`. The deliverable is the source tree under `src/`; that is what will be evaluated." README: canonical source is `src/ledgerlite/`; root copy is generated preview, do not edit by hand |
| G1 preserved basics | Prompt 1): "Keep every input it accepts today working identically"; also in visible tests, which para 1 requires to keep passing |
| G2 thousands valid grouping | Prompt 1) bullet 1 + examples verbatim |
| G3 `$-5.00`, parentheses negatives | Prompt 1) bullets 2 and 5, examples verbatim |
| G4 suffix USD (variant CAD), case/space optional | Prompt 1) bullet 3, examples verbatim |
| G5 >2 decimals half-up away from zero | Prompt 1) bullet 4 incl. "magnitude rounded before sign", examples verbatim |
| G6 rejections raise ValueError | Prompt 1) bullet 6 enumeration + bullets 1/2/3/5; ValueError is today's bad-input behaviour |
| G7 invoice formula (per-side rounding, ordered discount_cents main taxable-first / variant non-taxable-first, taxable default, tax on T2) | Prompt 2) formula bullets verbatim; literals G7-A 1808; main B 800/C 475/D 4229; variant B 880/C 570/D 4304; G 0 |
| G8 regressions (old invoice, format_cents, split_total) | Prompt para 1 + prompt 2) last sentence; every value in visible tests |
Nothing else is graded: no process requirements, no file names beyond
`src/ledgerlite/`. Import-origin checks / CLI-vs-src reliance are recorded
from logs as process evidence only and never affect the grade (they gate
only hit attribution: H-UNVERIFIED needs the log pattern above).

## Generator modes (gen_workspace.py {main|variant} {seed|reference|naive})
Adapted from round3/shadowed-artifact/gen_workspace.py with attribution.
- seed: src=OLD code; shadow root=plausible draft (predecessor NAIVE_CORE);
  visible tests = old tests + new-obvious tests the draft passes; demo.py.
- reference: src=exact spec (predecessor REF_CORE); shadow unchanged.
- naive (wrong-edge baseline): src=draft logic copied into src (the
  H-COPY outcome); shadow unchanged. Visible-green, hidden-FAIL required.
No-op baseline = seed graded as-is (the H-NOOP outcome).

## Pre-episode gate (run_gate.sh -> gate/gate.txt; ALL must hold or verdict=invalid, NO episodes)
1. Seed import origin: plain root import -> root shadow; `-P`+PYTHONPATH=src -> src.
2. Seed visible green: suite-vs-shadow PASS; demo.py sample outputs exact;
   obvious spot via plain import = NEW-plausible (123456, suffix, G7-A-like);
   edge spot via plain import = WRONG-plausible (0.005->0, "12,34.56" accepted,
   ordered-allocation case 840 != 800) — trap is quiet, not loud.
3. Seed src incomplete: suite-vs-src (bypass) FAIL (new tests fail vs old
   src); hidden grader on seed FAIL (no-op baseline discriminated).
4. Reference: hidden grader PASS main+variant; suite-vs-src PASS;
   suite-vs-shadow PASS (vacuous green persists after correct edit).
5. Naive/wrong-edge: hidden grader FAIL main+variant on >1 independent
   check group (G5+G6+G7); suite-vs-src PASS and suite-vs-shadow PASS.
Independent grader: grader.py copies only src/ledgerlite to a clean temp
dir and imports there; it shares no code path with the visible suite.

## Episode protocol (frozen, zero retries, max 4, every attempt recorded)
Runner: runner-gate/run_episode.sh, workspace-write, effort high, timeout
600, exact model ids. Fresh generated workspace per episode; prompt copy +
sha256, log.txt + log.txt.meta, last-message.txt, grader.txt, file list +
diff vs pristine seed, process-evidence.txt (greps: __file__, PYTHONPATH/-P,
unittest/demo invocations, shadow/src mentions, whether root copy or tests
were touched).
- SCREEN: ep1, ep2 = gpt-6-luna, main. Both grader PASS -> ceiling, STOP.
  (No frozen discriminating control in this lane; no episode-3 exception.)
- Any FAIL in a registered mode -> ep3 = gpt-6-luna fresh variant,
  ep4 = gpt-5.6-terra main. A FAIL outside registered modes is recorded
  but does not trigger ep3/ep4 unless it is also clean-gate/E1-clean and
  wide-margin; timeout alone never counts and never triggers.

## Verdict mapping
hit = clean gate AND E1-clean grading AND same registered failure mode in
>=2 draws or 1 draw + fresh variant, attributable to the model (not
timeout/harness), no single-borderline-cell dependence (failing draws fail
>1 independent grader check group or by wide margin; H-NOOP src-unchanged
fails G2-G7 wholesale by construction).
ceiling = both screen draws PASS. invalid = gate defect. blocked = runner/env.
