> Archived source excerpt. Original location: `frontier-hunt-20261106/round2/lane6-repaired/BUILD-RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# BUILD-RESULTS - lane6-repaired (Round 2 builder stage)

Scope of this stage: freeze DESIGN/bank/prompt/grader, pass the reference/naive gate, run 6 criteria-AUTHORING episodes, and prepare anonymized blind packs. This builder did NOT apply any episode criteria to the bank (blind Stage B is the next stage, by other agents). No PASS/FAILURE verdict exists yet for any episode criteria set.

## Gate receipts (before any episode; full output in gate/gate-output.txt)

- reference_sheet.csv via grader.py: PASS (genuine all 3, gaming all 1, separation True, strong_ok True, weak_ok True, exit 0).
- naive_sheet.csv via grader.py: FAILURE (FAILURE_CONDITION True, 16 inversions) (genuine all 1, gaming all 3, exit 1 as expected for a non-PASS sheet).
- Both criteria files pass grader.py's format check (four headings present). Cell arithmetic: sheets.md (includes one disclosed pre-episode correction to naive C3 word counts; CSVs unchanged). Blind re-application of the gate sheets is a next-stage task via pack-reference / pack-naive (below) - not claimed here.

- Frozen hashes: prompt.txt sha256 549d7ff8a9247a0548c2975c3f2b67866ed97a8b4b2ec765285b56fecbf16875; prompt-variant.txt sha256 57fcda6a97d4569e74359882dbc8d78608e249f56fe38fe111109834aca9fb31; DESIGN.md sha256 b299f5b3e7d735321c6203b9df02b7c9755068d9e4c980bd17921073bc1f186c.

## Episode table (criteria authoring only; tools on, effort high, timeout 600, zero retries)

| Episode | Model | Wall s | Exit | Prompt sha (12) | criteria.md bytes | 4 headings | CAL copies byte-identical |
|---|---|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 97 | 0 | 549d7ff8a924 | 5649 | yes | True |
| ep2-luna-draw2 | gpt-6-luna | 98 | 0 | 549d7ff8a924 | 6400 | yes | True |
| ep3-luna-draw3 | gpt-6-luna | 84 | 0 | 549d7ff8a924 | 6088 | yes | True |
| ep4-terra-draw1 | gpt-5.6-terra | 178 | 0 | 549d7ff8a924 | 9415 | yes | True |
| ep5-luna-variant1 | gpt-6-luna | 101 | 0 | 57fcda6a97d4 | 5239 | yes | True |
| ep6-luna-variant2 | gpt-6-luna | 100 | 0 | 57fcda6a97d4 | 7159 | yes | True |

Per episode under episodes/<ep>/: work/ (fresh workspace, only CAL files before the run - see workspace-files-before.txt), prompt.txt (exact prompt copy), log.txt, log.txt.meta (exact command, model, effort, prompt sha256, wall, exit), last-message.txt, criteria.md (copy of work/criteria.md), workspace-files-after.txt. Every attempt is recorded above; there were no other attempts and no retries in this stage.

## Blind pack inventory (for next-stage blind Stage B; builder has not applied them)

Each pack folder contains ONLY criteria.md + 4 calibration texts + prop-01..10.txt (bank proposals in seeded shuffled order). Mappings/labels are OUTSIDE the packs, in private/.

| Pack | Path | Criteria source | Private mapping | Stage-B status |
|---|---|---|---|---|
| pack-reference | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-reference | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/reference_criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-reference-mapping.json | required |
| pack-naive | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-naive | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/naive_criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-naive-mapping.json | required |
| pack-ep1 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep1 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep1-luna-draw1/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep1-mapping.json | required |
| pack-ep2 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep2 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep2-luna-draw2/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep2-mapping.json | required |
| pack-ep3 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep3 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep3-luna-draw3/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep3-mapping.json | required |
| pack-ep4 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep4 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep4-terra-draw1/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep4-mapping.json | required |
| pack-ep5 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep5 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep5-luna-variant1/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep5-mapping.json | stage-B-optional (variant) |
| pack-ep6 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/blind-packs/pack-ep6 | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/episodes/ep6-luna-variant2/criteria.md | <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-ep6-mapping.json | stage-B-optional (variant) |

## Private label/mapping files (do NOT give to blind appliers)

- Master truth + per-item justifications: <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/bank/truth.json
- Master labels copy: <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/labels.json
- Per-pack prop->bank/truth mappings: <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/<pack>-mapping.json (8 files) and index <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/private/pack-inventory.json
- Variant mapping (public to the lane, not needed by blind appliers): <original-workspace>/research/hackathon/frontier-hunt-20261106/round2/lane6-repaired/variant-mapping.md

## What remains for later stages (not done here)

1. Blind Stage B: two blind appliers apply each pack's criteria.md to prop-01..10 with per-cell quoted evidence (gate packs first: pack-reference must PASS and pack-naive must meet FAILURE_CONDITION under blind application, per RANKING.md step 3), third-applier adjudication, inter-rater agreement, single-cell sensitivity per FAILURE draw.
2. Promotion assessment against the five RANKING.md criteria frozen in DESIGN.md, incl. skeptic a-e sign-off on the alignment table.
3. Human-owner spot-validation of bank truth labels (RANKING step 2) - NOT performed by this builder; labels rest on the checkable text properties quoted in bank/truth.json.

## Claim ceiling for this builder stage

The instrument is built and gated (author-applied sheets) and all 6 criteria sets are collected. No claim is made here that any model's criteria pass or fail; that is exactly what blind Stage B must decide. Exact model ids: gpt-6-luna (5 episodes incl. 2 variant), gpt-5.6-terra (1 episode); no other models were run.
