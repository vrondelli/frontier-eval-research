> Archived source excerpt. Original location: `frontier-hunt-20261106/round4/rwlock/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round4/rwlock (FROZEN before any model episode)

Frozen: 2026-11-07, before gate completion and before episode 1.
No change to SPEC/prompt/grader after first episode; any change invalidates.
Pre-episode repair disclosed: after the first (passing) gate run, one
grader error label was clarified ("uncaught exception during scenario";
no check, threshold or SPEC/prompt byte changed), and the full gate was
re-run before episode 1. `gate/gate.txt` and `gate/inputs.sha256` record
the re-run that licenses the episodes.
Attribution: episode/grader/gate structure copied from
`round3/concurrency/` (its `DESIGN.md`, `grader.py`, `episode.sh`,
`setup_and_gate.sh`, `gen_variant.py` pattern), as suggested by that lane's
RESULTS ("non-canonical primitives"). All SPEC rules, scenarios, reference
and naive variants below are new for this lane.

## Hypothesis
A frontier model with tools implements a non-textbook concurrency primitive
that passes its own casual tests but fails choreographed interleavings of
the non-canonical semantics: writer preference (new readers barging past a
waiting writer, starving it), downgrade implemented as release+reacquire
(a waiting writer sneaks in, or the downgrade itself blocks behind the
writer it let in), notify-one lost wakeups (not all readers woken, or the
wrong waiter woken), waiting-writer residue after a timeout, per-wakeup
instead of total-budget timeouts, reentrancy/upgrade deadlocking instead
of raising, and release-by-non-owner silently corrupting counts. The hidden
grader choreographs each semantic with `Barrier`/`Event`-style threads.

## Task
`RWLock`: writer-preference read-write lock with atomic downgrade
(write->read without releasing) and timed acquire, fully specified in
SPEC.md rules R1–R11. Delivered per episode in a fresh workspace:
`SPEC.md`, `rwlock.py` skeleton. Prompt requires implementing + writing
own tests `test_rwlock.py` (including concurrent / writer-preference /
downgrade-with-waiting-writer / ownership-reentrancy / timeout tests) +
running them with tools. Hidden from model (never in episode workspaces):
`grader.py`, `reference_rwlock.py`, `naive1/2/3_rwlock.py`, this file.
Grader imports ONLY the specified API (`rwlock.RWLock`, 5 methods).
Python standard library only.

### Spec decisions pinned in SPEC (nothing left to a hidden key)
- Concurrent readers (R2); exclusive writer (R3).
- Writer preference (R4): while any writer is *waiting* (blocked in
  `acquire_write`, not yet granted or timed out), NO `acquire_read` may be
  granted, including `timeout=0` and including readers already waiting.
  Active (already-granted) readers are unaffected. Sole exception:
  `downgrade` itself. Timed-out/acquired writers stop being waiting.
  No FIFO required among writers or among readers (R4 last sentences).
- Downgrade (R9): write holder only (`RuntimeError` else); atomic single
  step, no grant in between, never blocks, returns `None`; afterwards the
  caller is a reader (must `release_read`; `release_write` raises).
  A waiting writer may acquire only after the downgraded reader releases.
- Reentrancy FORBIDDEN, exactly (R8): any `acquire_*` by a thread already
  holding read or write raises `RuntimeError` immediately regardless of
  timeout (incl. `None`/`0`), never blocks, never succeeds. Upgrade is
  the read-holder case of this rule. Downgrade is the only mode change.
- Ownership (R7): releases/downgrade only by the acquiring thread;
  non-owner raises `RuntimeError`. Errors leave state unchanged (R10).
- Timeout (R6): `None` indefinite; `>=0` total monotonic budget, not
  per-wakeup; `0` is try-acquire under the same R2–R4 predicates;
  expiry returns `False` with no hold and no waiter residue (a timed-out
  writer no longer blocks new readers); grantable-before-deadline must
  return `True`; negative raises `ValueError`.

## E1 alignment table (grader rule -> prompt/workspace sentence), frozen pre-episode
The prompt (task step 2) requires the implementation to satisfy "every rule
in SPEC.md exactly (rules R1–R11)"; SPEC.md is delivered in the workspace.
Each grader scenario below cites the SPEC rule(s) it checks. Nothing
outside R1–R11 is graded: no FIFO beyond R4 (SPEC makes waiter order a
non-requirement), no busy-wait check, no formatting, no extra attributes,
no import scanning. The model's own tests are recorded, never graded.

| Grader | What it checks | SPEC rule(s) | Prompt/workspace license |
|---|---|---|---|
| S01 | API returns True/None; negative-timeout ValueError; unheld/non-mode release & downgrade RuntimeError; reenter/upgrade RuntimeError at timeout 0 and 1; double release; usable after errors | R1,R6,R7,R8,R10 | SPEC R1/R6 ("negative timeout raises ValueError")/R7/R8/R10 verbatim; prompt step 2 |
| S02 | 3 readers hold simultaneously; writer try fails during overlap | R2,R3,R6 | SPEC R2 "any number ... at the same time", R3, R6 try-acquire; prompt step 2 |
| S03 | writer excludes reader (0.4s timeout False) and second writer (try False); reader ok after release | R3,R5,R6 | SPEC R3/R5/R6 verbatim; prompt step 2 |
| S04 | reader excludes writer (try and 0.4s False); writer ok after release | R3,R5,R6 | SPEC R3/R5/R6 verbatim; prompt step 2 |
| S05 | R1 holds; writer waits; new reader R2 must NOT acquire; R1 releases; writer acquires; only then R2 (order [w, r2]) | R4,R5 | SPEC R4 "no acquire_read may be granted" while writer waiting + R5 wake rules; prompt step 2 |
| S06 | waiting writer; 5 new readers timeout=0 all False (no barge); writer acquires ≤5s after R1 releases (bounded starvation check) | R4,R6 | SPEC R4 incl. "applies to acquire_read(timeout=0)" + R6 try-acquire; prompt step 2 |
| S07 | downgrade in main thread: returns None; other reader joins; writer try False; release_write/upgrade/second downgrade raise; release_read then writer ok | R9,R8,R2,R3 | SPEC R9 "After a downgrade the caller holds the read lock..." + R8; prompt step 2 |
| S08 | downgrade race: W1 holds, W2 waiting; W1 downgrade returns ≤3s; W2 NOT acquired while downgraded reader holds; new reader try False (W2 still waiting); W2 acquires only after downgraded release | R9,R4 | SPEC R9 "ONE atomic step ... must NOT acquire during or immediately after" + R4; prompt step 2 |
| S09 | two readers each attempt upgrade (timeout=0.5): both prompt RuntimeError, no deadlock/success; writer ok after both release | R8 | SPEC R8 "there is NO upgrade ... raises RuntimeError (it must not deadlock)"; prompt step 2 |
| S10 | release_read/release_write/downgrade by non-owner threads raise RuntimeError and do not free the lock (try-acquires still False) | R7,R10 | SPEC R7 "including from a different thread than the holder" + R10; prompt step 2 |
| S11 | timeout 0.4 fires in [0.25,2.0) both ways; 1.0s writer budget under timeout-churn wakeups expires in [0.8,2.0) (total, not per-wakeup) | R6 | SPEC R6 "TOTAL budget ... NOT a per-wakeup budget"; prompt step 2 |
| S12 | timed-out writer: new reader timeout=0 then succeeds while old reader holds; timed-out reader leaves lock usable | R6,R4 | SPEC R6 "leaves no residue: a timed-out writer is no longer a waiting writer" + R4; prompt step 2 |
| S13 | try-acquire True on free lock both modes; blocked writer/reader with 5s budget succeed after holder releases (~0.3s) | R6,R5 | SPEC R6 try-acquire + "becomes grantable before the deadline, must return True"; prompt step 2 |
| S14 | stress 6 readers/4 writers ×80 (client retries): invariant counters — never reader+writer, never 2 writers; writer increments exact 320; join deadline 25s | R11,R2,R3 | SPEC R11 "never two simultaneous writers, never a writer simultaneously with any reader"; prompt step 2 |
| S15 | writer holds; 4 readers wait; writer releases; ALL 4 acquire while gated (notify-one FAILs) | R5,R2 | SPEC R5 "ALL waiting readers may acquire (not just one of them)"; prompt step 2 |
| S16 | R1 holds; writer and 2 readers wait; R1 releases; writer acquires first, readers only after writer releases | R4,R5 | SPEC R5 "when the last reader releases, a waiting writer may acquire even if readers are also waiting (and, per R4, those readers must not acquire before that writer)"; prompt step 2 |

Timing tolerances are generous (0.4s timeouts accepted in [0.25,2.0);
5s wake joins; 0.4–0.6s settle sleeps before "must still be blocked"
checks; 30s per-scenario subprocess cap) so scheduling jitter cannot fail
a correct implementation. "Must be waiting/blocked" is only asserted after
a settle sleep plus a not-acquired event check, never by introspecting
implementation internals (no waiter-count API is specified or graded).

## Failure-mode clusters (for same-mode replication judgement)
- writer-preference / starvation: S05, S06, S16 (S08, S12 also exercise R4)
- downgrade: S07, S08
- wake-all / lost wakeup: S15, S16
- ownership / reentrancy / upgrade: S01, S09, S10
- timeout correctness: S03, S04, S11, S12, S13
- exclusion / stress invariants: S02, S03, S04, S14
Same mode = failing scenarios share a cluster. A bare runner timeout
(exit 124) with no graded implementation is NOT a model failure mode.

## Grader gate (must pass BEFORE any episode, else verdict=invalid, 0 episodes)
- reference (single Condition, while-loops, monotonic deadlines,
  notify_all, writer-preference predicate, downgrade under the lock):
  16/16 PASS required, 3 consecutive grader runs (flake check).
- naive1 (reader-preference: reference except `acquire_read` ignores
  waiting writers): must FAIL, expected S05/S06 (+S08/S16 R4 checks).
- naive2 (reference except downgrade = `release_write()` +
  `acquire_read()`): must FAIL, expected S08.
- naive3 (reference except every `notify_all()` -> `notify(1)`):
  must FAIL, expected S15 (+ possibly S16).
- skeleton: must FAIL (NotImplementedError) — grader not vacuous.
Gate output saved verbatim in gate/gate.txt; input shas in gate/inputs.sha256.

## Episode protocol (screen 2, max 4, zero retries, every attempt recorded)
Runner: `runner-gate/run_episode.sh` (codex exec, `-s workspace-write`,
effort high, timeout 600s). Primary `gpt-6-luna`, second `gpt-5.6-terra`.
Exact ids only. Fresh workspace per episode (copy of `task/`).
- ep1: gpt-6-luna draw1, base SPEC.
- ep2: gpt-6-luna draw2, base SPEC.
- If ep1+ep2 both PASS grader: verdict=ceiling, STOP (no ep3/ep4).
- If any FAILS: ep3 = gpt-6-luna fresh variant (`gen_variant.py`: same
  semantics/API, rule blocks reordered; same grader),
  ep4 = gpt-5.6-terra base SPEC. Max 4 episodes total.
Per episode saved: prompt.txt byte copy (its sha256 is in log.txt.meta),
log.txt, log.txt.meta, last-message.txt, workspace/, files-before.txt,
files.txt, spec-as-delivered.md, inputs.sha256, workspace.diff,
grade.txt (grader.py output + exit), own-tests.txt (running the model's
test_rwlock.py + a concurrency-content classification grep). A
runner/model error is recorded as that outcome, never re-drawn.

## Verdict rule (hit bar)
hit = clean gate AND E1 table above AND replicated with-tools failure:
>=2 draws failing the same mode cluster, or 1 draw + fresh variant (ep3)
same mode; failure attributable to the model (not exit-124 alone); no
single-borderline dependence (a hit resting only on one elapsed-time edge
in S03/S04/S11 does not count — failing checks are otherwise binary
thread-outcome/event checks with generous timing).
ceiling = both luna screen draws pass, or failures unreplicated/single-mode-unconfirmed.
invalid = gate fails or a prompt/grader/reference defect is found.
blocked = runner prevents episodes.

## Claim ceiling (pre-registered)
At most: "model X (exact id) at high effort, with tools, failed this frozen
RWLock spec on scenarios [...] (mode [...]) in N/M draws, while its own
tests [passed/failed/absent; concurrency content ...]". No general claim
about concurrency ability, other models, or other primitives.
