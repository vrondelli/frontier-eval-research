> Archived source excerpt. Original location: `frontier-hunt-20261106/round8/cross-process-state/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — round8/cross-process-state (FROZEN before gate/episodes)

Frozen 2026-11-07 before any model episode. No change to SPEC/prompt/grader
after first episode; any change invalidates the lane.

## Hypothesis (new mechanism, Round 8)
A frontier model implements file-backed state correctly for a single
process (and possibly for threads) but unsafely under concurrent OS
processes — lost updates, duplicate id allocation, torn/partial reads —
despite the prompt/SPEC explicitly requiring multi-process safety.
Predicted model failure modes: (a) plain read-modify-write with direct
overwrite; (b) `threading.Lock`-only protection (correct within a process,
useless across processes); (c) file lock held but non-atomic overwrite, so
raw readers observe torn JSON; (d) lock on the data file itself broken by
atomic-replace inode swap. The hidden grader spawns barrier-synchronized
processes and checks exact invariants.

## Contrast with predecessors (read in full before freezing)
- `round3/concurrency` (ceiling 13/13 x2): in-process `threading`
  BoundedQueue; a single `Condition` suffices. It never tested separate
  processes or files.
- `round4/rwlock` (ceiling 16/16 x2) and `round5/fair-upgrade-lock`
  (ceiling 18/18 x2): in-process thread locks with ordering/upgrade rules.
  In all three, the textbook single-process `Condition` pattern that the
  models produced is exactly the pattern that FAILS here if transplanted
  (`threading.Lock` = naive2 below). That inversion is the new mechanism:
  the previously-correct habit is now the trap, and the SPEC says so
  explicitly (R10). Round 3's own RESULTS also named "atomic multi-account
  transfer with a total invariant" as untried; G4 covers it across
  processes. Executive verdicts in SUBMISSION-FINAL.md sections 1-3: no
  promotable hit in 32 protocols/108 episodes; this lane is a genuinely
  new pre-registered question, not a backfill.

## Task
Implement `store.py` (functions in SPEC): file-backed counter + unique-id
allocation + account ledger (deposit/withdraw/transfer/balance) in one
JSON file, safe under concurrent OS processes, no torn reads, persistent
across processes. Workspace delivered per episode: `SPEC.md`, `store.py`
skeleton. Prompt requires implementation + own `test_store.py` including
genuine multi-process tests + running them. Hidden (never in episode
workspaces): `grader.py`, reference/naives, this file. Stdlib only, Linux.

## E1 alignment table (grader -> prompt/workspace sentence)
Prompt P2 requires satisfying "every rule in SPEC.md exactly (R1-R10)"
and states the store "will be called simultaneously from multiple OS
processes". Nothing outside R1-R10 is graded (SPEC lists
non-requirements: crash recovery beyond R2/R3, fsync policy, fairness,
speed beyond completion). Model's own tests are recorded, never graded.

| Grader | Checks | SPEC license (verbatim substance) |
|---|---|---|
| G1 sequential | init defaults/format, ids 1,2, counter +/- , deposit/withdraw/transfer arithmetic, ValueError cases (non-positive, overdraw, unknown), src==dst no-op without funds check, failed ops change nothing, re-init preserves, exact top-level keys | R1 "exactly these top-level semantics... Extra top-level keys are not permitted"; R4 init/preserve; R5 fresh reads as empty; R6 "Ids start at 1... exactly one more"; R7 delta "any int, including negative"; R8/R9 validation + "changes nothing" + src==dst "(no funds check)" |
| G2 concurrent increment | 8 procs x150 barrier increments = exactly 1200 | R7 "must never lose an update: final counter must equal sum of all deltas"; R10 atomic "with respect to concurrent calls from other OS processes... must not rely on in-process locks alone" |
| G3 concurrent allocate | 8x100 ids exactly {1..800}, next 801 | R6 "no duplicates, no gaps... across all processes combined... never reissues" |
| G4 transfers+deposits | 6 procs x100 (transfer A->B 1, deposit C 2) from A=10000 -> 9400/600/1200 | R8 deposit; R9 transfer "atomically... no interleaving may lose or duplicate... sum preserved"; R10 |
| G5 torn reads | 4 writers x150 (increment+deposit) while 2 readers loop raw-byte json.loads (exact keys, counter never backwards) + API get_counter never raises; finals exact | R2 "any process reading the raw bytes... must observe either previous or next complete valid JSON, never partial"; R10 reads "never torn... must not raise because a writer... is active"; counter monotonicity follows from R7 (only +1 writes in G5) + R1 "after any completed operation file must reflect full effect" |
| G6 concurrent init/first use | 6 procs on nonexistent path: init+20 ids each -> {1..120}; 4-proc re-init preserves, next id 121 | R4 "safe to call concurrently... leave existing data unchanged"; R5 first-use "must also be safe under concurrent processes" |
| G7 persistence | fresh subprocess writes (7/42/id1), parent sees it, second fresh subprocess reads + allocates id 2 | R3 "a brand-new Python process that only calls the read functions must see all previously completed operations"; R6 never reissue |
| G8 mixed stress | 8 procs: 50x increment(3)+deposit own acct, 40 ids, 20x deposit shared 5 -> counter 1200, ids {1..320}, acct_i=50(i+1), shared=800 | R6+R7+R8+R10 combined |

Timing: generous (90 s per scenario subprocess, 60 s worker joins,
30 s barrier). Deadlock/hang = FAIL for that scenario (R10 "must not
deadlock... must complete under contention"). Exact-equality checks are
on completed-operation counts only; no elapsed-time or borderline cells.

## Failure-mode clusters (same-mode replication)
- lost-update/duplicate (cross-process RMW atomicity): G2,G3,G4,G8 (+G6 ids)
- torn-read/format: G5 (and exact-keys part of G1)
- init/first-use race: G6
- sequential/API semantics: G1,G7
Same mode = shared cluster. A bare runner timeout (exit 124) with no
graded implementation is not a failure mode and cannot count toward a hit.
A hit resting only on G1 sequential semantics does NOT support the
cross-process hypothesis and is reported as such, not as this lane's hit.

## Grader gate (before episodes, else invalid + 0 episodes)
- reference (fcntl.flock on `path.lock`, RMW under lock, tempfile+
  fsync+os.replace): must PASS 8/8 in 3 consecutive grader runs.
- naive1 (plain RMW, direct overwrite, no lock): must FAIL, expected
  lost-update cluster and G5.
- naive2 (`threading.Lock` + atomic replace, no file lock): must FAIL,
  expected lost-update cluster (the predecessor-correct pattern).
- skeleton: must FAIL (NotImplementedError).
Gate also proves grader reliability: reference 3x PASS required; naive
failure margins (actual lost counts) recorded in gate/gate.txt.
If either naive passes, the instrument does not discriminate: invalid,
no episodes, no silent grader strengthening after episodes begin.

## Episodes (screen 2, max 4, zero retries)
Runner runner-gate/run_episode.sh, gpt-6-luna primary / gpt-5.6-terra
secondary, effort high, workspace-write, 600 s. Fresh workspace/episode.
ep1 luna draw1, ep2 luna draw2 (main prompt). Both pass => ceiling STOP.
Any pre-registered failure (any grader FAIL) => ep3 luna fresh variant
(prompt-variant.txt: P-sentences reordered/reworded, same SPEC.md bytes
and same grader — disclosed weaker freshness than a new surface) +
ep4 terra main. Max 4. Save prompt/sha (meta), log, meta, last-message,
workspace, diffs, grade.txt, own-tests.txt (auditor rerun of model's
test_store.py + process-level classification: does it spawn OS processes
via multiprocessing/subprocess, threads only, or sequential only?).

## Verdict / claim ceiling
hit = clean gate + same cross-process mode cluster in >=2 draws or
1 draw + variant, model-attributable, with tools, no timeout-only.
ceiling = 2/2 screen pass or failures unreplicated. invalid = gate/E1
defect. blocked = runner prevents episodes.
At most: "exact model, high effort, with tools, [passed/failed] this
frozen multi-process file-store protocol in N/M draws (scenarios ...),
own tests [process-level or not]". No claim about other storage tasks,
databases, crash durability (ungraded), or other models.
