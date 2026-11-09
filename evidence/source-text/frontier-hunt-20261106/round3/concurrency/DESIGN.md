> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/concurrency/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round3/concurrency (FROZEN before any model episode)

Frozen: 2026-11-07, before gate completion and before episode 1.
No change to SPEC/prompt/grader after first episode; any change invalidates.

## Hypothesis
A frontier model with tools implements a concurrency primitive that passes
its own casual tests but fails systematic interleavings: close failing to
wake all waiters, lost wakeup, overfill past capacity when several putters
wake for one slot, no draining after close, enqueuing after close/timeout,
per-wakeup (not total) timeout budgets, deadlock or lost/duplicated items
under producer/consumer stress. Its own tests are expected to be mostly
sequential; the hidden grader choreographs adversarial interleavings.

## Task (fresh for Round 3)
`BoundedQueue`: closeable bounded blocking FIFO queue (`put`/`get`/`close`/
`qsize`/`closed`, `QueueClosed`), fully specified in SPEC.md rules R1–R11.
Delivered per episode in a fresh workspace: `SPEC.md`, `bounded_queue.py`
skeleton. Prompt requires implementing + writing own tests
`test_bounded_queue.py` (including concurrent/blocking/close/timeout tests)
+ running them with tools. Hidden from model (never in episode workspaces):
`grader.py`, `reference_bounded_queue.py`, `naive1/naive2_bounded_queue.py`,
this file. Grader imports ONLY the specified API. Stdlib only.

## E1 alignment table (grader rule -> prompt/workspace sentence), frozen pre-episode
The prompt (sentence P2) requires the implementation to satisfy "every rule
in SPEC.md exactly (rules R1–R11)"; SPEC.md is delivered in the workspace.
Each grader scenario below cites the SPEC rule(s) it checks. Nothing outside
R1–R11 is graded: no waiter fairness (SPEC explicitly makes it a
non-requirement), no formatting, no extra attributes, no import scanning.
Model's own tests are recorded as evidence, never graded by grader.py.

| Grader scenario | What it checks | SPEC rule(s) | Prompt/workspace license |
|---|---|---|---|
| S01 | capacity ValueError, FIFO, None/identity, qsize, negative-timeout ValueError | R1,R2,R10,R9 | SPEC R1/R2/R10/R9 verbatim; prompt P2 |
| S02 | close: drain FIFO, put-after-close QueueClosed, closed-empty get, idempotent, closed flag | R7,R8 | SPEC R7/R8 verbatim; prompt P2 |
| S03 | get blocks empty+open, wakes on put with the item | R6,R11 | SPEC R6; prompt P2 |
| S04 | put blocks full+open, capacity held, wakes on get, order | R4,R3,R2 | SPEC R4/R3; prompt P2 |
| S05 | close wakes ALL 4 blocked getters -> QueueClosed | R7 | SPEC R7 "All blocked getters are woken"; prompt P2 |
| S06 | close wakes ALL 3 blocked putters -> QueueClosed, items not enqueued, orig drains | R7 | SPEC R7 "All blocked putters are woken ... does NOT enqueue"; prompt P2 |
| S07 | close with 2 items + 4 getters: exactly 2 served, 2 QueueClosed | R7,R2 | SPEC R7 drain sentence; prompt P2 |
| S08 | one freed slot, 3 putters: exactly 1 proceeds, qsize==capacity, rest stay blocked | R3,R4,R11 | SPEC R3 bound + R4; prompt P2 |
| S09 | TimeoutError on time both ways, timeout=0, no enqueue/consume on timeout, success before deadline, closed beats timeout | R9,R7 | SPEC R9 verbatim incl. precedence; prompt P2 |
| S10 | timeout is TOTAL budget under wakeup churn (success with churn item also accepted; fail only if blocked past deadline+slack or wrong exception) | R9 | SPEC R9 "total budget ... not a per-wakeup budget"; prompt P2 |
| S11 | MPMC stress 4x200 cap7, close+drain: exact multiset, no loss/dup; single-producer FIFO exact | R11,R2,R3 | SPEC R11/R2; prompt P2 |
| S12 | stress with timeout-retry loops: exact multiset (timeout paths must not corrupt) | R9,R11 | SPEC R9/R11; prompt P2 |
| S13 | close then get frees slot: blocked putters still QueueClosed, nothing enqueued | R7 | SPEC R7 "even if space is or becomes available after close"; prompt P2 |

Timing tolerances are generous (e.g. 0.3s timeout accepted in [0.2s, 3s);
5s wake joins; 30s per-scenario subprocess cap) so scheduling jitter cannot
fail a correct implementation. Race ties at an exact expiry instant are
deliberately not graded (S10 accepts either legitimate outcome).

## Failure-mode clusters (for same-mode replication judgement)
- close-wake/drain: S02,S05,S06,S07,S13
- capacity/overfill/blocking: S03,S04,S08
- timeout correctness: S09,S10,S12
- stress integrity: S11,S12
- sequential/API: S01
Same mode = failing scenarios share a cluster (S12 counts for both of its
clusters). A bare runner timeout (exit 124) with no graded implementation
is NOT a model failure mode and cannot count toward a hit.

## Grader gate (must pass BEFORE any episode, else verdict=invalid, 0 episodes)
- reference (single Condition, while-loops, monotonic deadlines,
  notify_all): 13/13 PASS required, and repeated runs must stay PASS
  (flake check: 3 consecutive grader runs).
- naive1 (check-once/wait-once `if`, timeout result ignored): must FAIL,
  expected S08 (overfill) and S09 (timeout), plus close scenarios.
- naive2 (correct loops/deadlines; close uses single notify; get checks
  closed before items so no drain): must FAIL, expected S02/S05/S06/S07.
- skeleton: must FAIL (NotImplementedError) — sanity grader is not vacuous.
Gate output saved verbatim in gate/gate.txt.

## Episode protocol (screen 2, max 4, zero retries, every attempt recorded)
Runner: runner-gate/run_episode.sh (codex exec, -s workspace-write,
effort high, timeout 600s). Primary gpt-6-luna, second gpt-5.6-terra.
Exact ids only. Fresh workspace per episode (copy of task/).
- ep1: gpt-6-luna draw1, base SPEC.
- ep2: gpt-6-luna draw2, base SPEC.
- If ep1+ep2 both PASS grader: verdict=ceiling, STOP.
- If any FAILS: ep3 = gpt-6-luna fresh variant (gen_variant.py seed 7:
  same semantics/API, rule blocks reordered; same grader),
  ep4 = gpt-5.6-terra base SPEC. Max 4 episodes total.
Per episode saved: prompt.txt byte copy + its sha256 is in log.txt.meta,
log.txt, log.txt.meta, last-message.txt, workspace/, files.txt (file list),
grade.txt (grader.py output + exit), own-tests.txt (running the model's
test_bounded_queue.py; plus a concurrency-content classification: whether
the model's tests use threads/close/timeout stress or are sequential-only).
A runner/model error is recorded as that outcome, never re-drawn.

## Verdict rule (hit bar)
hit = clean gate AND E1 table above AND replicated with-tools failure:
>=2 draws failing the same mode cluster, or 1 draw + fresh variant (ep3)
same mode; failure attributable to the model (not exit-124 alone); no
single-borderline dependence (failing scenarios are binary thread-outcome
checks with generous timing; a hit resting on one timing-boundary scenario
alone (S09/S10 elapsed edges) does not count).
ceiling = both luna screen draws pass, or failures unreplicated.
invalid = gate fails or prompt/grader/reference defect found.
blocked = runner prevents episodes.

## Claim ceiling (pre-registered)
At most: "model X (exact id) at high effort, with tools, failed this frozen
BoundedQueue spec on scenarios [...] (mode [...]) in N/M draws, while its own
tests [passed/failed/absent; concurrency content ...]". No general claim
about concurrency ability, other models, or other primitives.
