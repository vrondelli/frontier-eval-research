> Archived source excerpt. Original location: `frontier-hunt-20261106/round4/rwlock/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round4/rwlock

Verdict: **ceiling**. Both `gpt-6-luna` screen draws PASS the hidden grader
16/16; per the frozen protocol the lane stops (no variant/terra episodes,
which exist only after a screen failure). Zero silent
retries; 2 episodes total, every attempt recorded below.

## Gate (before any episode)
`gate/gate.txt`, inputs pinned in `gate/inputs.sha256`
(prompt `dc382d81…`, base SPEC `5886bb4c…`, variant SPEC `29479746…`,
grader `4dd1ccc1…`, DESIGN `32b48ee1…`, skeleton `a4a07c64…`):

- reference: **16/16 PASS, 3 consecutive runs** (no flakes).
- naive1 (reader-preference: readers ignore waiting writers): FAIL
  S05 (R2 barged), S06 (try-acquire barge), S08 (barge after downgrade),
  S16 (waiting readers acquired while R1 holds) — exactly the
  writer-preference cluster.
- naive2 (downgrade = release_write + acquire_read): FAIL **only S08**
  ("downgrade did not return promptly while W2 waiting … w2_acquired=True")
  — the downgrade-atomicity check isolates this defect.
- naive3 (notify(1) instead of notify_all): FAIL S15 (1/4 readers woke on
  writer release), S16 (1/2 readers after writer released).
- skeleton: FAIL all 16 (NotImplementedError) — grader not vacuous.

Pre-episode repair (also disclosed in DESIGN.md): after a first gate run
with identical outcomes, one grader error *label* was clarified
("uncaught exception during scenario") and the **full gate was re-run**
before episode 1; no check, threshold, SPEC or prompt byte changed.
`gate/gate.txt` records the re-run that licenses the episodes.

## Episodes (runner-gate/run_episode.sh, workspace-write, effort high, 600s)

| Episode | Model | Wall | Runner exit | Hidden grader | Own tests (`own-tests.txt`) |
|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 179s | 0 | **PASS 16/16** (`grade.txt`) | 10 tests, all ok (`python3 -m unittest -v`, unittest_exit=0) |
| ep2-luna-draw2 | gpt-6-luna | 184s | 0 | **PASS 16/16** (`grade.txt`) | 12 tests, all ok (`python3 -m unittest -v`, unittest_exit=0) |

Per-episode receipts saved: `prompt.txt` (sha `dc382d81…` in
`log.txt.meta`, matching `gate/inputs.sha256`), `log.txt`, `log.txt.meta`,
`last-message.txt`, `workspace/`, `files-before.txt`, `files.txt`,
`spec-as-delivered.md` (sha `5886bb4c…` = base SPEC, unchanged in both),
`inputs.sha256`, `workspace.diff`, `grade.txt`, `own-tests.txt`. An
auditor re-run of `grader.py` on each finished workspace after the
episodes reproduced both verdicts (`regrade.txt`: PASS 16/16,
`regrader_exit=0`, both draws) — not a model retry.
`codex_version=codex-cli 0.167.0` in both metas.

## What the models actually wrote
Both draws independently produced the textbook-correct construction for
this (non-textbook) spec: a single `threading.Condition`, an explicit
waiting-writers counter gating `acquire_read`, predicate re-check in a
while loop against a monotonic deadline, `notify_all` on every release /
downgrade / writer-timeout exit (including the easy-to-miss
timed-out-writer wake that S12 targets), per-thread ownership sets with
prompt `RuntimeError` on reentry/upgrade/non-owner release, and downgrade
as a two-field mutation under the condition mutex (both implementations
carry a comment noting no waiter can observe an unlocked interval —
the exact S08 race). Their own tests were not casual: test names include
`test_downgrade_is_atomic_and_waiting_writer_waits_for_downgraded_reader`,
`test_waiting_writer_blocks_new_and_already_waiting_readers`,
`test_timeout_budget_is_not_reset_by_wakeups`,
`test_timed_out_writer_stops_blocking_new_readers`,
`test_writer_release_wakes_all_readers` — i.e. the own tests already
choreographed the grader's main traps.

## Claim ceiling (actual)
Under this frozen E1-aligned protocol, `gpt-6-luna` at high effort with
tools passed a writer-preference RW-lock + atomic downgrade + timed
acquire spec 2/2 (16/16 hidden choreographed scenarios each, own tests
10/10 and 12/12). No claim beyond this protocol/model/spec. The fresh
variant (reordered rule blocks) and `gpt-5.6-terra` were **not** run:
the frozen screen stops at 2/2 PASS.

## Next-hypothesis note (not run)
Harder successors would need semantics with no single-Condition textbook
collapse: e.g. fair (FIFO, ticket-ordered) RW locks where ordering itself
is graded, upgrade-permitted locks with upgrade-serialization, or
reentrant-with-counts semantics interacting with downgrade — each needing
its own frozen E1 protocol before any draw.
