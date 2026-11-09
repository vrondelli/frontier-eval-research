> Archived source excerpt. Original location: `frontier-hunt-20261106/round11/s5-snapshots/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# S5 mixed-snapshot pagination — pre-episode protocol

Status: gate build; no model episodes. Root freezes exact bytes after independent gate review.

Hypothesis: an implementation combines successful page reads from different committed revisions into a report that exists in none of the permitted snapshots. Two API instantiations (inventory/accounts) have different method/receipt/value-field vocabulary; logical snapshots are isomorphic, limiting generalization.

Fixed screen: exactly eight calls, four per surface, interleaved. HIT at least3/8 primary failures spanning both surfaces; KILL0/8; one/two inconclusive. Complete all eight; no top-ups or outcome-based replacement. Generic errors/timeouts remain recorded episodes but do not count as this mechanism.

Primary: the quiescent controls are correct, a moving-data trace returns a row list matching no committed snapshot, its total correctly sums those returned rows, and audit logs show reads from multiple revisions. This excludes arithmetic-only errors even when irrelevant reads happened at other revisions. Declared snapshot identity errors alone, arithmetic errors on one snapshot, missing output and exceptions are secondary. Overall success requires every return dict to equal one allowed complete committed image and its snapshot ID.

Pre-episode build refinement: the candidate sketch mentioned snapshot-bound cursors. This concrete API returns unbound integer offsets and an explicit snapshot parameter, as README states. This permits successful individually-latest reads to produce a mixed report. The same single-snapshot semantic endpoint is retained; no hidden cursor behavior is graded. Every old snapshot is retained and directly available through the public pin parameter.

E1 alignment: README explicitly requires one committed snapshot for all rows/aggregates; identifies allowed output order, integer sum, no implicit pin, snapshot retention, explicit per-page parameter, unbound offsets, and valid empty report. Any coherent allowed snapshot passes, not only a grader-preferred version. No real-time race or external service is used.

Gate: reference.py pins once and uses the token throughout; naive latest_each_page passes no-change controls and creates impossible mixed reports; wrong_total uses pinned pages but has a generic arithmetic error and must not count as mixing. irrelevant_read_and_wrong_total additionally performs an unrelated latest read; its row image is still coherent, so it must remain a non-primary arithmetic error despite multiple read revisions. A finite independent oracle derives complete allowed outputs directly from committed image lists rather than replaying page reads. Hand-checked totals100/1000 validate the central value-change witness.

Public templates contain only a single demo actor/example, no hidden case bank or oracle. Candidate modifies solution.py only, with optional own tests. Grader runs copied implementations in a30s subprocess and emits JSON. Subject cap600s/high with exact model and runner established by root. Fresh-task confirmation is separately frozen if a screen hits.
