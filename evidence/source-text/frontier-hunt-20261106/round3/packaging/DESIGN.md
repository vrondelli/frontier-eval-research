> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/packaging/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round3/packaging (frozen before drafting; NO model episodes)

Lane: `frontier-hunt-20261106/round3/packaging/`. Assignment: execute
`round2/synthesis/RANKING2.md` §4 packaging checklist for the CURRENT
(Rounds 1–2) evidence. Outputs: this folder + top-level
`frontier-hunt-20261106/SUBMISSION-DRAFT.md`. This lane runs **zero model
episodes**, so there is no reference/naive gate and no screen protocol;
the "gate" is the verification rule below. Verdict for this lane is
`packaged` by assignment (it asserts nothing about model capability).

## Frozen scope

- Read in full: `synthesis/RANKING.md`, `round2/synthesis/RANKING2.md`.
- Write only: `round3/packaging/*` + `SUBMISSION-DRAFT.md`. Never modify
  any earlier lane/study. No git/GitHub.
- Draft must contain: copy-ready claim with filled census; ranked table
  for all Round-1+2 lanes; exhibit index (absolute paths to
  DESIGN/gate/RESULTS/meta per lane); two instrument-defect exhibits
  (lane6 E1, coordinator TMPDIR, one paragraph each minimum); explicit
  NOT-done items (incl. human spot-validation, variant packs unapplied);
  falsifiability/next hypotheses; exact model ids/effort/timeouts.

## E1-clean alignment for a packaging lane (each printed number → its license)

| Printed claim | License (file opened this lane) |
|---|---|
| Any episode count | Lane `RESULTS.md` episode table **and** `episodes/` dir listing **and** `log.txt.meta` sidecars (all three must agree; coordinator via `episode.json`) |
| Any score/grade (26/26, 15/15, RD, optima…) | Lane `RESULTS.md` **plus** at least the gate receipt file it cites |
| Any synthesis statistic (59/60, a–e, promotion i–v) | RANKING/RANKING2 text **plus** the underlying lane/applier file it cites |
| Model ids / effort / timeouts / walls / exits / shas | `log.txt.meta` (or `episode.json` for coordinator), never RESULTS prose alone |
| Coordinator path claims | New-study folder listing + `episode.json`; original-study shas quoted from lane RESULTS (preserved tree is never written) |

Rule: no number is copied from a summary without opening at least the lane
RESULTS. Disagreements between routes are reported, not averaged.

## Frozen counting rule (see SUBMISSION-DRAFT §2 / CENSUS.md)

Count model episodes only: fresh-workspace lane-prompt runs (incl.
criteria-authoring, controls, variants, the one timeout) + 1 native
coordinator episode. Exclude: runner probes + wrapper test, scripted
gate runs, Docker A/B replays, coordinator probes/scripted reference
(incl. the 1 disclosed smoke turn), blind/author applications, grader
re-runs, the paused pre-hunt coordinator run. Enumerate exclusions.

## Attempts ledger

Model episodes attempted by this lane: **0**. Reads/copies are listed in
`RESULTS.md`. Staging files under `C:\Users\vlad_\hunt3-tmp-packaging-*`
are transport, not deliverables.
