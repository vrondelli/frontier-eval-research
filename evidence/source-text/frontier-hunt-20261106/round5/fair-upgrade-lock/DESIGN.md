> Archived source excerpt. Original location: `frontier-hunt-20261106/round5/fair-upgrade-lock/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round5/fair-upgrade-lock (FROZEN before any model episode)

Frozen 2026-11-07 before gate and episodes. No SPEC/prompt/grader change after ep1.
Successor to round3/concurrency (bounded queue, ceiling 13/13 x2) and
round4/rwlock (writer-preference RW lock + downgrade, ceiling 16/16 x2).
Those audits explicitly named as untested: fair/FIFO ticket-ordered RW locks
where ordering itself is graded, and upgrade-permitted locks with
upgrade-serialization (round4/rwlock RESULTS "Next-hypothesis note";
round3/concurrency RESULTS disposition). This lane tests exactly that
successor; it does not rerun writer-preference semantics (here a waiting
writer does NOT overtake earlier waiting readers, the opposite priority for
that pair) and upgrade was forbidden (RuntimeError) in round4 but is a
specified converting operation here. Structure adapted from round4/rwlock
(grader/episode/gate pattern, attribution); all rules/scenarios/reference/
naives new.

## Hypothesis
With tools, model passes own tests but fails choreographed FIFO ordering
(reader/writer barging, writer order, reader batch), upgrade serialization
(two upgraders deadlocking instead of second raising, upgrade as
release+reacquire letting a waiting writer in, upgrade timeout losing the
read hold), downgrade+FIFO interaction, timed-out-waiter residue blocking
the queue behind it, or lost wakeups.

## Contract choices (all in SPEC R1-R12, deadlock-free by construction)
- FIFO among waiting acquire_read/acquire_write with consecutive-head reader batching (R3).
- Exactly one pending upgrader; second upgrade raises RuntimeError immediately, keeps read (R5). This avoids the classic two-upgrader deadlock by spec.
- Upgrader keeps read hold, waits to be sole reader, converts atomically, outranks all waiting acquire requests incl. earlier waiting writer (R5). This avoids upgrader-vs-waiting-writer deadlock by spec.
- Pending upgrade blocks all new read grants (R4) so sole-reader is reachable.
- Downgrade atomic, never blocks; head reader batch may join, readers behind a waiting writer may not (R6).
- Total-budget monotonic timeouts, no FIFO/pending residue on timeout (R7); no reentrancy (R8); owner-only releases (R9); wake-on-every-eligibility-event (R10); errors unchanged (R11).

## E1 alignment table (grader -> SPEC rule -> prompt license)
Prompt step 2 requires satisfying SPEC R1-R12 exactly; SPEC is in workspace.
Grader imports only fair_rwlock.FairRWLock with the 7 specified methods.
Own tests recorded, never graded. Nothing outside R1-R12 graded.

| Grader | Checks | SPEC | License |
|---|---|---|---|
| S01 | returns, negative ValueError, unheld/non-owner-mode errors, reentry, writer upgrade error, usable after | R1,R5,R7,R8,R9,R11 | SPEC verbatim; prompt step 2 |
| S02 | 3 readers simultaneous, writer try False during | R2,R7 | R2 "any number" + R7 try |
| S03 | writer excludes reader(0.4 False)+writer, reader after | R2,R7 | R2 exclusive |
| S04 | R1 holds, W waits, later R2 waits, order W then R2 | R3(a),R10 | R3(a) no reader ahead of earlier writer |
| S05 | W holds, R1 waits, later W2 waits, order R1 then W2 | R3(b),R10 | R3(b) no writer overtake earlier reader |
| S06 | W holds, R1+R2 wait batch before later W2, both together | R3(b)(c),R10 | R3(c) batch |
| S07 | writers W1 before W2 in arrival order | R3(d) | R3(d) |
| S08 | 5 try-readers False while writer waiting | R3(a),R7 | R3(a) incl timeout=0 |
| S09 | sole-reader upgrade try+timed True, becomes writer | R5 | R5 sole reader conversion |
| S10 | upgrade waits for other reader; new/try readers blocked while pending; completes on drain; queued reader after write release | R4,R5,R10 | R4 grant ban + R5 |
| S11 | second upgrade prompt RuntimeError, keeps read; first completes after second releases | R5,R11 | R5 one pending, second raises immediately |
| S12 | upgrader beats already-waiting writer, no writer in between, order up then W | R5 | R5 ahead of every waiting request incl earlier writer |
| S13 | upgrade timeout 0.5 False in window, still reader, pending cleared (new reader joins) | R5,R7,R4 | R5 timeout keeps read + R7 no residue |
| S14 | downgrade prompt None with W2 waiting; W2 and reader-behind-W2 blocked until downgraded releases; order W2 then R | R6,R3 | R6 atomic + behind-writer reader ban |
| S15 | downgrade wakes head reader batch alongside downgraded | R6,R10,R3(c) | R6 head batch may be granted |
| S16 | head writer times out 0.6, reader behind it acquires joining active reader without release | R7,R10,R3 | R7 timed-out leaves no FIFO residue, may then be granted |
| S17 | 0.8 timeout under timeout-churn wakeups expires total-budget window | R7 | R7 TOTAL not per-wakeup |
| S18 | stress readers/writers/upgraders, invariants, no deadlock | R12,R2,R5 | R12 never writer+reader / 2 writers |

Timing: generous windows (settle 0.3-0.6s, joins 5s, timeout windows e.g.
[0.6,2.0) for 0.8 budget, 35s scenario subprocess cap). No internal
introspection; arrival order choreographed by spawn + settle sleep +
not-acquired checks.

## Failure clusters (same-mode replication)
FIFO/barging: S04 S05 S06 S07 S08 (S14 also). Upgrade: S09 S10 S11 S12 S13.
Downgrade: S14 S15. Timeout/residue/wakeup: S13 S16 S17 S15. Ownership: S01.
Invariants: S02 S03 S18. Bare runner timeout (124) is not a model mode.

## Gate (before episodes, else invalid + 0 episodes)
reference PASS 18/18 x3 consecutive; naiveA (upgrade=release_read+acquire_write,
keeps no atomicity/priority, loses read on timeout) FAIL load-bearing
(expected S10/S12/S13 cluster); naiveB (barging: readers ignore waiting
writers/pending, writers ignore queue position) FAIL load-bearing
(expected S04/S05/S08/S10); skeleton FAIL 0/18. Receipts gate/gate.txt,
shas gate/inputs.sha256.

## Episodes (max 4, zero retries)
runner-gate/run_episode.sh, workspace-write, high, 600s, fresh workspace.
ep1/ep2 gpt-6-luna screen. Both PASS => ceiling STOP. Any FAIL in
pre-registered mode => ep3 gpt-6-luna variant (gen_variant.py reorders
R1-R12 blocks, same grader), ep4 gpt-5.6-terra base. Per episode: prompt
copy+sha in meta, log/meta, last-message, workspace, files-before/files,
spec-as-delivered, inputs.sha256, workspace.diff, grade.txt, own-tests.txt
(incl interleaving grep classification).

## Hit bar / claim ceiling
hit = clean gate + E1-clean + same cluster in >=2 draws or 1+variant,
attributable to model, not single timing edge. ceiling = screen 2/2 pass
or unreplicated. invalid = gate not clean. Claim at most protocol-indexed
exact-model statement; no general concurrency claim.
