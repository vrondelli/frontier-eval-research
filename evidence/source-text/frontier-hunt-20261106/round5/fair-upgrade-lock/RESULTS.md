> Archived source excerpt. Original location: `frontier-hunt-20261106/round5/fair-upgrade-lock/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round5/fair-upgrade-lock

Verdict: **ceiling**. Both `gpt-6-luna` screen draws PASS the hidden
grader 18/18; per the frozen protocol the lane stops (variant `ep3` and
`gpt-5.6-terra` `ep4` run only after a screen failure). 2 model episodes
total, zero silent retries/replacements, every attempt recorded.

Lane (WSL): `<original-workspace>/research/hackathon/frontier-hunt-20261106/round5/fair-upgrade-lock/`
DESIGN.md frozen before gate/episodes, with the E1 alignment table
(18 grader scenarios S01–S18, each mapped to SPEC R1–R12).
Inputs pinned in `gate/inputs.sha256` (prompt `585bf170…`, base SPEC
`ec360c1d…`, variant SPEC `26f54eca…`, grader `85c05358…`, DESIGN
`4232d5bf…`, skeleton `5f4dfb01…`).

## Successor vs predecessors (what changed)
Predecessors read in full: `round3/concurrency/RESULTS.md` (closeable
bounded queue: ceiling 13/13 in 2/2 luna draws) and
`round4/rwlock/{DESIGN,RESULTS}.md` (writer-preference RW lock with
atomic downgrade, **upgrade forbidden** (R8 RuntimeError): ceiling
16/16 in 2/2). Round-4's own next-hypothesis note named as untested
"fair (FIFO, ticket-ordered) RW locks where ordering itself is graded"
and "upgrade-permitted locks with upgrade-serialization". This lane
tests exactly those successors, not a rerun:
- Writer preference is replaced by bilateral FIFO: a later writer must
  not overtake earlier waiting readers (S05/S06 — the reverse of the
  round-4 R4 priority for that pair), writers are ordered among
  themselves (S07), consecutive head readers batch (S06/S15).
- `upgrade()` is a real converting operation (round 4: RuntimeError):
  sole-reader atomic conversion (S09), drain-wait with pending-upgrade
  grant ban (S10/S04-R4-analogue), exactly one pending upgrader with the
  second raising promptly (S11), priority over an already-waiting
  writer (S12), timeout preserving the read hold and clearing the
  pending slot (S13).
- Downgrade is kept but its post-grant rule is FIFO-indexed (head batch
  may join S15; reader behind a waiting writer may not S14), plus
  timed-out-head-writer queue-removal unblocking (S16).

## Contract (SPEC R1–R12, deadlock-free by construction)
`FairRWLock` with `acquire_read/release_read/acquire_write/release_write/
upgrade/downgrade`. Second concurrent upgrade raises `RuntimeError`
immediately (no two-upgrader deadlock); pending upgrader outranks all
waiting acquire requests incl. an earlier writer (no
upgrader-vs-waiting-writer deadlock) and blocks new read grants so
sole-reader is reachable; downgrade atomic/never blocks; total-budget
monotonic timeouts with no FIFO/pending residue; no reentrancy;
owner-only releases; errors leave state unchanged.

## Gate (before any episode; `gate/gate.txt`)
| Candidate | Result |
|---|---|
| reference (Condition + FIFO deque + pending-upgrader flag + monotonic deadlines + notify_all) | **PASS 18/18, 3 consecutive runs** |
| naiveA (upgrade = release read + acquire_write as new writer) | FAIL 15/18 — S11 (second upgrade not rejected / loses read), S12 (waiting writer acquired before upgrader), S13 (timed-out upgrader lost read hold) |
| naiveB (barging: readers ignore waiting writers/pending, writers ignore queue position) | FAIL 14/18 — S04, S08 (5/5 try-readers barged), S10 (reader granted while upgrade pending), S14 (reader behind writer joined downgraded reader) |
| skeleton | FAIL 0/18 (NotImplementedError) |

Both naives fail load-bearing, cluster-specific scenarios, so the
instrument discriminates the hypothesised mechanisms.

## Episodes (runner-gate/run_episode.sh, workspace-write, effort high, 600 s, codex-cli 0.167.0)
| Episode | Model | Wall / exit | Hidden grader | Own tests (auditor re-run) |
|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 191 s / 0 | **PASS 18/18** (`grade.txt`); auditor regrade PASS 18/18 (`regrade.txt`) | 9 tests, all OK (`own-tests.txt`) |
| ep2-luna-draw2 | gpt-6-luna | 197 s / 0 | **PASS 18/18** (`grade.txt`); auditor regrade PASS 18/18 (`regrade.txt`) | 10 tests; auditor full-suite re-run 9/10 (see note), model claimed 10/10 |

Per-episode receipts in `episodes/<ep>/`: `prompt.txt` (sha `585bf170…`
in both `log.txt.meta`, matching the gate pin), `log.txt`,
`log.txt.meta` (exact command/model/effort/timeout), `last-message.txt`,
`workspace/`, `files-before.txt`, `files.txt`, `spec-as-delivered.md`,
`inputs.sha256`, `workspace.diff`, `grade.txt`, `regrade.txt`,
`own-tests.txt` (with the interleaving classification: test names +
thread/upgrade/downgrade/FIFO/timeout grep counts).

**ep2 own-test note (recorded, not graded — DESIGN grades only the
hidden grader):** our independent full-suite re-run of ep2's tests gave
9/10, failing `test_reader_batch_and_writer_fifo`, and 3 targeted
re-runs of that single test gave OK/FAILED/FAILED. Reading the test
(workspace `test_fair_rwlock.py:25-49`): its reader workers release
immediately after setting their `entered` event, then the test asserts
the writer has not entered — but once both readers have released, the
writer is spec-legitimately free to enter, so the assertion races the
writer. It is a flaky test-choreography defect, not evidence against
the implementation: the hidden grader's gated version of the same
interleaving (S06, readers held on an Event while the writer-must-wait
check runs) passes for ep2 in both the episode grade and the auditor
regrade. ep2's final message nonetheless claimed "10 passed, 0 failed",
which was true of its own run at best. This is a test-quality blemish
in one draw; under the frozen verdict rule (hidden-grader failure
clusters) it is not a model failure mode and is not stretched into one.

## What the models actually wrote
Both draws independently produced the queue-based construction this
spec needs (verified by reading both `fair_rwlock.py` files): a single
`threading.Condition`, an explicit FIFO waiter `deque`, a
pending-upgrader field, head-of-queue grant logic with reader batching,
monotonic total-budget deadlines, `notify_all` on every
release/grant/timeout-removal/conversion, per-thread ownership with
prompt `RuntimeError` on reentry/second-upgrade/non-owner release, and
atomic upgrade/downgrade under the condition mutex (ep1 comment:
"Conversion is atomic and takes precedence over every queued
request"). Their own tests choreographed the grader's main traps by
name: e.g. ep1 `test_upgrade_preempts_waiting_writer_and_preserves_read_until_success`,
`test_two_readers_racing_to_upgrade_only_one_is_pending`,
`test_downgrade_keeps_waiting_writer_ahead_of_later_reader`; ep2
`test_upgrade_waits_and_has_priority_over_queued_writer_and_reader`,
`test_second_upgrade_is_rejected_while_first_is_pending`,
`test_upgrade_timeout_preserves_read_and_clears_pending`.

## Honest claim ceiling
Under this frozen E1-aligned protocol, `gpt-6-luna` at high effort with
tools passed a FIFO-fair RW-lock + upgrade/downgrade spec 2/2 (18/18
hidden choreographed scenarios each, regrade-confirmed; own tests 9/9
and 9–10/10 with one flaky self-test noted). The variant and
`gpt-5.6-terra` were not run (screen-stop). No claim beyond this
protocol/model/spec: 2 draws, choreographed sleeps + stress (not
exhaustive schedule exploration), generous timing tolerances. The
FIFO+upgrade successor surface that rounds 3–4 left untested is now
tested and is also a ceiling.
