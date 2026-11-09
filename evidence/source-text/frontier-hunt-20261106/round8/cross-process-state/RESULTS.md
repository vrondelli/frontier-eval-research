> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/cross-process-state/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — round8/cross-process-state

Verdict: **ceiling** (honest negative). Both `gpt-6-luna` screen draws
PASS the hidden grader 8/8 (and auditor regrade 8/8); per the frozen
protocol the lane STOPs — variant `ep3` and `gpt-5.6-terra` `ep4` are
not run. 2 model episodes total, zero silent retries.

Lane: `<original-workspace>/research/hackathon/frontier-hunt-20261106/round8/cross-process-state/`
DESIGN.md frozen before gate/episodes with the E1 table (G1-G8 -> SPEC
R1-R10). Inputs pinned in `gate/inputs.sha256` (DESIGN `88b2f7cb…`,
SPEC `2b305a64…`, prompt `c9a089db…`, prompt-variant `b52709ad…`,
grader `d4c807bf…`, skeleton `1c1845ab…`).

## Why this is a new mechanism (predecessor contrast)
Predecessors read in full: SUBMISSION-FINAL.md sections 1-3 (no promotable
hit in 32 protocols/108 episodes, Rounds 1-7), `round3/concurrency`
(closeable bounded queue, ceiling 13/13 x2), `round4/rwlock` (writer-
preference + downgrade, ceiling 16/16 x2), `round5/fair-upgrade-lock`
(FIFO/upgrade, ceiling 18/18 x2). All three lanes are **in-process thread**
primitives where one `threading.Condition/Lock` is the correct textbook
answer — the exact pattern both models produced there. This lane inverts
that: the state lives in a **file shared by separate OS processes**, so
the previously-correct in-process-lock habit is the pre-registered trap
(SPEC R10 states correctness "must not rely on in-process locks alone").
It also takes up round3's own untried "atomic multi-account transfer with
a total invariant" (G4) and adds mechanisms with no predecessor analogue:
duplicate allocation (G3), torn raw-byte reads (G5, R2), concurrent
first-use/init races (G6), and cross-interpreter persistence (G7).

## Task / grader
`store.py`: JSON file `{counter, next_id, accounts}` with `init_store`,
`allocate_id`, `increment`, `get_counter`, `deposit`, `withdraw`,
`transfer`, `balance` (SPEC R1-R10), plus the model's own `test_store.py`
required to include genuine multi-process tests. Hidden grader: G1
sequential semantics/validation; G2 8 procs x150 barrier increments =
1200; G3 8x100 ids exactly 1..800; G4 6 procs x100 transfer+deposit ->
9400/600/1200; G5 4 writers vs 2 raw-byte JSON readers (never torn,
counter never backwards); G6 concurrent init/first-use on a nonexistent
path -> ids 1..120, re-init preserves; G7 fresh-subprocess persistence;
G8 8-proc mixed stress exact totals. Each scenario runs in its own
subprocess (90 s cap), workers barrier-synchronized (`fork`).

## Gate (before any episode; `gate/gate.txt`)
| Candidate | Result |
|---|---|
| reference (fcntl.flock on `path.lock`, RMW under lock, tempfile + fsync + `os.replace`) | **PASS 8/8, 3 consecutive runs** (G5 reader iterations 1017/1097/1064 — grader reliability/flake check) |
| naive1 (plain RMW, direct overwrite, no lock) | FAIL 2/8 — G2 counter 27/1200 (1173 lost), G3 ids uniq 26/800, G4 worker hit false "insufficient funds" from lost deposits, G5 torn JSON (`Extra data`), G6 uniq 9/120, G8 uniq 3/320; passes only G1 sequential + G7 |
| naive2 (`threading.Lock` + atomic replace, no file lock — the predecessor-correct pattern) | FAIL 2/8 — G2 207/1200 (993 lost), G3 uniq 138/800, G4 balances 9880/120/238, G5 counter went backwards 2->1, G6 uniq 23/120, G8 uniq 50/320; passes only G1 + G7 |
| skeleton | FAIL 0/8 (`NotImplementedError`) |

The discrimination is wide, not borderline: both naives are *sequentially
correct* (G1 PASS) and fail catastrophically only under process
contention — exactly the hypothesised single-process-correct /
multi-process-unsafe signature. Had a model shipped either pattern, the
grader would have caught it with hundred-fold margins.

## Episodes (runner-gate/run_episode.sh, workspace-write, high, 600 s, codex-cli 0.167.0)
| Episode | Model | Wall/exit | Hidden grader | Auditor regrade | Own tests (auditor rerun) |
|---|---|---|---|---|---|
| ep1-luna-draw1 | gpt-6-luna | 150 s / 0 | **PASS 8/8** (G5 588 iters) | PASS 8/8 (534) | 6 tests OK |
| ep2-luna-draw2 | gpt-6-luna | 100 s / 0 | **PASS 8/8** (G5 501 iters) | PASS 8/8 (431) | 6 tests OK |

Per-episode receipts in `episodes/<ep>/`: `prompt.txt` (sha `c9a089db…`
in both metas, matching the gate pin), `log.txt`, `log.txt.meta`,
`last-message.txt`, `workspace/`, `files-before.txt`, `files.txt`,
`spec-as-delivered.md`, `inputs.sha256`, `workspace.diff`, `grade.txt`,
`regrade.txt`, `own-tests.txt`.

## What the models actually wrote
Both draws independently produced the reference-class construction
(verified by reading both `store.py` files): a **persistent sibling lock
file** with `fcntl.flock(LOCK_EX)` held across the whole
read-modify-write, and **same-directory temp-file + `os.replace`** writes
so raw readers only ever see complete JSON. Both explicitly handled the
subtlest pre-registered trap — locking the data file itself would break
under `os.replace` inode swap — ep1's comment notes the lock file is
distinct so its inode survives "across the atomic replacement of the
state file" and that "a separate descriptor per operation makes flock
serialize both [threads and processes]"; ep2 comments "Same-directory
replace is atomic: raw readers see the old complete [file]". Neither used
any `threading.Lock` (grep: none). There was no single-process-only draft
to correct: both shipped the cross-process mechanism directly, so there
is not even an in-episode near-miss of the hypothesised mode.

**Process-level own tests (recorded per DESIGN):** both draws wrote
genuine multi-process tests, not thread-only or sequential-only —
`multiprocessing.get_context("fork")` with `ctx.Process` workers
(0 `threading` mentions in either test file). ep1 (6 tests, 199 lines):
concurrent first initialization (8 procs), multiprocess increment +
gapless unique ids, multiprocess deposits/transfers preserving balances,
and a raw-byte reader process during 250-increment writers checking for
torn JSON. ep2 (6 tests, 143 lines): many-process increment without lost
updates and unique contiguous ids (barrier-started), competing transfers
preserving totals, raw readers during 200-increment writers. In other
words each model's own suite already choreographs the hidden grader's
main mechanisms (G2/G3/G4/G5/G6 analogues) — the secondary hypothesis
that own tests would be single-process-only and give false confidence
also failed. Both final messages' claims (6 tests passed, mechanism
description) match our auditor reruns.

## Claim ceiling (actual)
Under this frozen E1-aligned protocol, `gpt-6-luna` at high effort with
tools implemented a multi-process-safe file-backed store (lock-file
`flock` + atomic replace) and wrote passing genuine multi-process tests
in 2/2 draws (hidden grader 8/8 twice + regrade 8/8 twice). Bounds:
2 draws of one model (screen STOP; no variant/terra); choreographed
barrier contention on one machine/filesystem (WSL ext4-style semantics),
not NFS/network filesystems where `flock` behaviour differs; crash
durability, fsync policy and fairness were explicit non-requirements and
are untested here; the frozen variant is a reordered prompt over
identical SPEC/grader bytes (disclosed in DESIGN) and remains unused.
Nothing supports claims about append-log/WAL designs, database-backed
state, lock-free algorithms, or other models.

## Disposition
Not promotable, not a near-miss: a clean ceiling with a strongly
discriminating gate (sequentially-correct naives fail by ~1000 lost
updates). The "previously-correct habit becomes the trap" inversion did
not bite: when the SPEC names the multi-process requirement explicitly,
the model reaches for OS-level locking directly and avoids even the
lock-the-data-file inode trap. A harder successor would need to remove
that explicitness without breaking E1 (hard: the requirement is the
construct), or move to semantics where flock+replace is insufficient
(e.g. multi-file invariants, append-only log compaction, or
crash-durability under kill -9 mid-write graded by replay) — each its
own frozen protocol.
