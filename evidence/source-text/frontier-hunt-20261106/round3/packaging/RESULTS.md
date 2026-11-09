> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/packaging/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round3/packaging

Verdict: **packaged**. No model episodes were run by this lane (0 attempts,
0 retries). Deliverable: `<original-workspace>/research/hackathon/frontier-hunt-20261106/SUBMISSION-DRAFT.md`
plus this folder's `DESIGN.md` (frozen scope + verification rule) and
`CENSUS.md` (three-route count log). No earlier lane/study was modified.

## What was done (RANKING2 §4 checklist, item by item)

1. **Read in full:** `synthesis/RANKING.md` (206 lines) and
   `round2/synthesis/RANKING2.md` (348 lines); all 11 lane `RESULTS.md`
   (lanes 1–6, collider, forced-autonomy, undocumented-invariant,
   optimization-v2, coordinator-r2) + lane6-repaired `BUILD-RESULTS.md` +
   `blind-A/B APPLIER-RESULTS.md` + lane7 `DIAGNOSIS.md` +
   `runner-gate/{RESULTS,RUNNER}.md`; gate receipts for every lane;
   all 33 `log.txt.meta` files (32 episodes + script-test) and the
   coordinator `episode.json`.
2. **Census:** **33 model episodes** (30× `gpt-6-luna`, 3×
   `gpt-5.6-terra`; R1 15 + R2 18) under the frozen counting rule in
   `CENSUS.md`/draft §2, with exclusions enumerated (8 probes + 1 wrapper
   test, gate runs, lane7 A/B + re-pass, StaleOwner A/B, coordinator
   probes incl. 1 disclosed smoke turn, blind/author applications, paused
   pre-hunt run).
3. **Draft:** copy-ready claim + short version; ranked 12-lane table;
   methods box (exact ids, `codex-cli 0.167.0`, effort `high`, 600 s /
   2400 s budgets); Exhibit A (lane6 E1) + Exhibit B (TMPDIR); absolute-path
   exhibit index; 8 NOT-done items (human spot-validation + ep5/ep6 first);
   falsifiability + 5 next hypotheses; claim ceiling; Appendix A with all
   32 metas + coordinator receipt.

## Honest claim ceiling (this lane)

This lane adds no new model evidence. It certifies only that the draft's
numbers reconcile across RESULTSes, episode dirs, and metas on disk at
packaging time, and that its dispositions match the two skeptic audits.
Whether the methods negative is the right Sunday entry — and the pending
human spot-validation — remain owner decisions (draft §9). Round 3 is
explicitly out of scope: if a Round-3 lane promotes a hit before Sunday,
the draft's claim text must be superseded, not patched silently.

## Unresolved

- Owner decision + optional post-hoc spot-validation (§7.1) outstanding.
- `StaleOwner` single factor, E48 cause, cumulative-cost recognition:
  carried as open in the draft, not resolved here (correctly).
