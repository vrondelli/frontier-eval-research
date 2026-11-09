> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/concurrency/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round3/concurrency

Verdict: **ceiling** (honest negative). No hit. Protocol stop after the
2-draw luna screen: both draws PASS the full hidden grader.

Lane: `frontier-hunt-20261106/round3/concurrency` (WSL
`<original-workspace>/research/hackathon/`).
DESIGN.md (with the frozen E1 alignment table) was frozen before the
gate and before any episode; gate inputs pinned in `gate/inputs.sha256`
(prompt `3bb2317c…`, SPEC `9759ba67…`, grader `186d48f1…`,
DESIGN `7b73922e…`, variant SPEC `91a4e771…`).

## Task in one paragraph
Implement `BoundedQueue`, a closeable bounded blocking FIFO queue
(`put`/`get` with total-budget timeouts, `close()` waking all waiters,
drain-after-close, `qsize`/`closed`, `QueueClosed`), from SPEC.md
R1–R11, plus the model's own `test_bounded_queue.py`. Hidden grader:
13 scenarios (S01–S13) — sequential contract, blocking wakeups,
close-wakes-all (getters and putters), close+drain split, one-slot/
three-putter overfill probe, timeout timing/side-effects/precedence,
total-budget-under-churn, 800-item MPMC stress + exact FIFO, timeout-
retry stress, close-vs-freed-slot race. Deadlock = FAIL via daemon
threads, timed joins, 30s per-scenario subprocess cap.

## Gate (before any episode; `gate/gate.txt`)
| Candidate | Result |
|---|---|
| reference (Condition + while-loops + monotonic deadlines + notify_all) | **PASS 13/13, three consecutive runs** (flake check) |
| naive1 (check-once/wait-once `if`, timeout result ignored) | FAIL 4/13 — S05/S06/S07 (close outcomes), S08 (qsize 3 > capacity 1), S09/S10 (IndexError not TimeoutError), S11/S12 (consumer IndexError), S13 (enqueued after close) |
| naive2 (correct loops; close `notify()` one waiter; no drain after close) | FAIL 6/13 — S02/S13 (QueueClosed instead of drained item), S05 (3/4 getters hung), S06 (2/3 putters hung), S07 (0 items drained), S08 (cleanup hang), S11 (deadlock, 30s subprocess timeout) |
| skeleton | FAIL 0/13 |

The two naive failures are the intended failure modes of the
hypothesis, so the instrument demonstrably discriminates. Cosmetic
note: naive2's S02/S13 are reported as "grader scenario crashed:
QueueClosed" because the submission's exception propagates where the
scenario requires a drained item; the FAIL verdict and cause are
correct. No episode depends on that label (both passed outright).

## Episodes (runner-gate/run_episode.sh, effort high, timeout 600, workspace-write, zero retries)
| Episode | Model | Exit / wall | Hidden grader | Model's own tests |
|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 0 / 90s | **PASS 13/13** | 8 tests, `python3 -m unittest -v` OK |
| ep2-luna-draw2 | gpt-6-luna | 0 / 110s | **PASS 13/13** | 12 tests, `python3 -m unittest -v` OK |

Per-episode receipts in `episodes/<ep>/`: prompt copy, log + meta
(prompt sha `3bb2317c…` both), last-message, workspace, files lists,
`workspace.diff`, `grade.txt`, `own-tests.txt`, `inputs.sha256`,
`spec-as-delivered.md`. Both final messages claim completion with
test counts matching our independent re-run of their tests.

Per the frozen protocol (2 luna screen draws both pass ⇒ ceiling,
STOP), ep3 (variant luna) and ep4 (terra) were **not** run. The seed-7
reordered-rules variant exists under `task-variant/` unused.

## What the model actually did (why there is no failure)
Both draws independently wrote the textbook-correct implementation:
one `threading.Condition`, `while True` re-check loops,
`time.monotonic` total-budget deadlines, `notify_all` on every state
change including `close()` (verified by grep of both workspaces).
Every adversarial choreography passed on first grading: close woke
all 4 getters and all 3 putters, exactly one of three putters took a
single freed slot with capacity held, the 2-item/4-getter drain split
was exact, timeouts fired as total budgets under churn (0.80s), and
both stress runs delivered exact multisets with no deadlock.

The secondary hypothesis — that the model's own tests would be
sequential-only and give false confidence — also did not hold. Both
test files contain genuine interleaving tests: blocked put/get
wakeups, close waking blocked threads, drain-after-close, MPMC
exactly-once delivery, timed-out calls leaving the queue unchanged.
ep2 additionally tested `test_timeout_is_total_across_wakeups` and
close-wakes-getters-and-drains-FIFO. (Neither model tested the
one-slot/three-putter overfill probe or the close-vs-get race
explicitly, but their implementations handle both.)

## Honest claim ceiling
"gpt-6-luna at high effort, with tools, correctly implemented this
frozen closeable-bounded-queue spec and wrote passing concurrency
tests in 2/2 draws (grader 13/13 each; own tests 8/8 and 12/12)."
That is all. Caveats that bound even the negative: only 2 draws
(protocol stop, no variant/terra draws after a clean screen); one
textbook primitive whose correct pattern is heavily represented in
training data; grader interleavings are choreographed sleeps + stress
(not exhaustive schedule exploration), with generous timing
tolerances; S10 by design also accepts a legitimate success outcome
under churn, so per-wakeup-budget bugs that still deliver could pass
that one scenario (both draws instead passed it via on-time
TimeoutError, and their deadline code is visibly total-budget).
Nothing here supports a claim about less canonical primitives
(lock-ordering ledgers, RW-lock writer preference), subtler memory-
ordering bugs, or other models.

## Disposition
Not promotable, not a near-miss: a clean ceiling with a discriminating
gate. If Round 4 revisits concurrency, the untried surface is a
primitive without a single canonical pattern (e.g. writer-preference
RW lock with upgrade/downgrade rules, or atomic multi-account transfer
with a total invariant), where a fully explicit spec still leaves
genuine design choices that systematic interleavings can punish.
