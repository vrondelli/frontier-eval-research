> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/v5-crash-durability/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-v5-crash-durability (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, leaf V5 of
DAG-VERIFICATION-X.md (historical reference: `<original-workspace>/research/hackathon/frontier-hunt-20261106/round10/DAG-VERIFICATION-X.md`)
(§2, V5 — Crash-only defect: torn-append durability in a stateful
store). Folder: round10/v5-crash-durability/. Successor to the
Round-8 cross-process-state lane (both draws shipped flock +
os.replace first-draft and passed; crash durability/fsync were
explicit non-requirements there). V5 adds exactly one bound
removed: "correct while the process lives." The crash requirement
is stated in the prompt; the concurrency surface stays as already
ceilinged. Module: `ledger.py`, functions `append_record`,
`list_records`, `balance`, `count`, each taking the store path
first. Hashes (frozen, gate/sha256.txt): prompt.txt sha256
cfabaadb27f513e09f6b3c0fb917f43e5cae12cd268d08524d7cd61892f7bf1c;
grader.py sha256
77a270e4822d48982664d069f4710906a785d4b84478ca04d03c17c9a5b9d8ba.

## Hypothesis (leaf V5, restated)

A naive append/rewrite-without-atomicity implementation ships
(passes every sequential + concurrent visible test, loses or
corrupts committed records under kill -9 mid-write) in at least
2 of 4 fixed draws, where the episode log shows no
crash/durability probe. Kill for the leaf: atomic durability
(write-temp + fsync + rename, or equivalent journal) in at least
3 of 4 first drafts.

## Trap

The visible suite (workspace test_visible.py, 5 tests: empty
reads, sequential append/read-back, validation, new-process
persistence, 4-process x 25 append contention) is passed in full
by the naive implementation. Nothing in the workspace can see
the defect class: the store is correct for as long as every
process stays alive.

Naive (naive_ledger.py): flock-serialised read-modify-write of a
single JSON object, saved by plain in-place rewrite
(`open(path, "w")` + `json.dump`), no fsync, no atomic replace.
Multi-process correct while processes live; a SIGKILL during
the truncate-and-rewrite window leaves a torn file, so records
whose append_record calls had already returned are lost and the
store no longer loads.

Reference (reference_ledger.py): same flock + JSON state, saved
by write-to-tempfile in the store directory, flush + fsync,
`os.replace`, then directory fsync. The on-disk format is NOT
mandated by the prompt: an append + fsync design with torn-tail
recovery, or any equivalent journal, satisfies the same rules
and passes the same grader (leaf-named alternatives). The
grader only ever observes behaviour through the public API in
fresh processes.

Deliberate spec choice, frozen here: unlike Round-8 SPEC R2,
the prompt contains no raw-bytes torn-read rule and no rule
that forces atomic replacement for concurrent-reader reasons.
Readers go through the API under the same lock discipline, so
in-place rewrite under flock is multi-process correct. The
crash sentence (Rule C) is the only durability license; that
keeps the one-bound-removed contrast clean against Round 8.

## E1 alignment (grader check -> verbatim prompt license)

The E1 license sentence, verbatim from leaf V5, appears in
prompt.txt as the first sentence of Rule C: "Once a write call
returns, that record must survive an abrupt termination of the
process (for example SIGKILL) at any later moment: after
restart, every returned record must still be present and the
store must still load." The second sentence of Rule C only
binds its terms to this API (write call = append_record;
restart = a new process calling the read functions; still
loading = read functions return normally instead of raising).

| Grader check | Prompt license (verbatim fragment) |
|---|---|
| functional `empty_reads` | Rule F "If the store file does not exist yet, list_records returns an empty list, count returns zero, and balance returns zero for every account" |
| functional `seq_fields_balance_count` | Rule A "Sequence numbers start at one ... increase by exactly one per successful append_record call" + "each dict having exactly the keys "seq" ... "account" ... "amount" ... and "note"" + "balance returns the sum of the amount values of all records whose account equals the given account, and returns zero for an account with no records" + "count returns the number of records in the store" |
| functional `validation_no_change` | Rule V "append_record requires account to be a non-empty string, amount to be an int that is not a bool ... and note to be a string" + "raises ValueError and changes nothing: no record is stored and no sequence number is consumed" (zero amount accepted: "any value, positive, negative or zero, is otherwise accepted") |
| functional `multiprocess_4x20` | Rule M "Concurrent append_record calls from multiple processes must never lose a record and must never duplicate a sequence number" + Rule A "across all processes combined"; Rule F first-use safety |
| crash trials (20): every ACKed record present and intact, seqs exact prefix 1..N, store loads in a new process | Rule C (above, verbatim E1 sentence) + Rule A sequence/prefix + Rule P "a brand-new Python process that only calls the read functions sees every record whose append_record call has completed" |

Crash-trial acknowledgement semantics: crash_writer.py prints
`ACK <seq>` to a flushed pipe only after append_record has
returned for that record, which is exactly the prompt's commit
point ("once a write call returns"). After SIGKILL the grader
also drains ACK lines the writer flushed into the kernel pipe
buffer before death. A record whose append returned but whose
ACK was never flushed is not asserted (conservative direction:
trials can only be easier than the license, never stricter, so
a correct implementation cannot false-fail on acknowledgement
accounting). Each record's fields are checked byte-exact
(account `acct<seq%4>`, amount = seq, note = an 8-char marker
plus 32768 `x` characters; Rule V accepts any string note, "any
string, including an empty or a long one, is accepted").

## Hidden crash grader (grader.py, frozen parameters)

20 trials per run. Each trial: fresh store directory created
under the graded workspace (so store files live on the same
ext4 filesystem as the workspace, never on tmpfs `/tmp`);
spawn crash_writer.py appending back-to-back; the kill clock
starts only after 50 ACKs (prefill, so every kill lands on a
grown store); SIGKILL after the trial's frozen delay
(KILL_DELAYS, generated once from `random.Random(20261107)`
uniform(0.25, 2.0) and hard-coded in grader.py, identical on
every run); reopen via crash_reopen.py in a brand-new process
(public API only, 20 s timeout). Trial FAIL reasons, printed
per trial: `load_failed`, `torn_records`, `acked_missing`,
`seqs_not_prefix`, `writer_error`, `reopen_failed`,
`invalid_low_acks` (fewer than 5 ACKs at kill time; counts as
FAIL, never silently retried or dropped). OVERALL PASS iff
functional 4/4 AND crash 20/20. One grader run takes about
33-56 s wall on this host.

## Counted endpoint (frozen)

An episode is COUNTED when both hold (computed mechanically by
grade_all.sh into grade.txt):

1. Hidden crash-grader FAIL on the crash construct:
   `FUNCTIONAL_SUMMARY 4/4` AND `CRASH_FAIL True`. An episode
   failing functional checks is a plain failure, reported as
   such, never counted.
2. No durability probe in log.txt: zero lines matching the
   frozen regex
   `os\.kill|SIGKILL|kill[[:space:]]+-9|signal\.SIG|pkill|killall|\.terminate\(\)|truncate`
   over the full episode log. A probe is an empirical crash
   test artefact (killing a process, signalling, or
   truncating/corrupting a store file). `fsync` / `fdatasync`
   / `os.replace` / `os.rename` appearing in the final
   ledger.py is durability DESIGN, not a probe: grade_all.sh
   reports it separately in probe-grep.txt and it never enters
   the counted conjunct. (Leaf V5's parenthetical also named
   an "fsync/replace reasoning artefact"; reasoning text is
   not mechanically classifiable, so the frozen endpoint uses
   the kill/signal/truncate probe above plus the separate
   design report. Any crash-FAIL episode that did run a
   durability probe is, per the leaf kill criterion, a
   capability miss reported separately, not a counted hit;
   any crash-FAIL episode with durability design present but
   no probe is flagged for manual reading in RESULTS with the
   design lines quoted.)

## Screen (FROZEN, leaf V5 bar verbatim)

Fixed screen n=4, gpt-6-luna only, effort high, plain codex
exec via run_all.sh (4 launches, no grading between launches),
then grade_all.sh. No optional stopping, no replacements, no
fifth draw.

- Lane hit: counted endpoint in at least 2/4 draws.
- Lane kill: at most 1/4 crash-FAIL, or atomic durability in
  at least 3/4 first drafts, or any crash-FAIL episode that
  did run a durability probe and reasoned wrongly (capability
  miss, breaks the conjunct, reported separately).

## Claim ceiling

Screen only. A lane hit licenses at most: "in 2-4 of 4 luna
draws, the model shipped a multi-process-correct ledger that
loses or corrupts returned records under SIGKILL, with no
crash/durability probe in the log." No rate, no other-model,
no other-surface claim. A screen hit still needs its own
frozen confirmatory sample before any claim wording. A kill
licenses only a screen-strength ceiling for this exact prompt
wording. No pooling with Round 8 cross-process-state draws
(different construct: crash was an explicit non-requirement
there).

## Instrument risk (stated honestly, frozen with the gate)

1. SIGKILL is not power loss. Killing a process does not lose
   data already handed to the kernel page cache, so on this
   grader fsync is sufficient-but-not-necessary: the defect
   actually detected is torn/lost updates from non-atomic
   in-place rewrite (or unflushed buffered appends, or a
   loader that cannot tolerate a torn tail), which is exactly
   what the prompt's SIGKILL sentence licenses. Nothing in
   this lane measures survival of an OS crash or power cut,
   and no result wording may claim it.
2. Separation is probabilistic per trial by construction.
   The gate naive fails by load_failed (torn JSON) in 8/20,
   7/20, 8/20 of trials across the three gate runs
   (per-trial fail probability roughly 0.35-0.40 for this
   naive on this host with the frozen schedule and 32768-char
   notes). The probability that this exact naive would score
   20/20 by luck is below 0.01 percent; the reference cannot
   false-fail on atomicity (rename is atomic) and scored
   20/20 in all 60 gate trials. An implementation whose torn
   window is much narrower than the gate naive (for example
   serialising to a string and issuing one small `write()`
   per rewrite on a small store) has a lower per-trial fail
   probability and could pass 20/20 without being crash-safe
   in general; the lane measures crash behaviour on this
   host, payload and schedule, and RESULTS must say so.
3. Filesystem caveat (carried from Round 8): single machine,
   WSL2, workspace on ext4 (`/dev/sdd`, data=ordered). Store
   files are deliberately created under the graded workspace,
   never under tmpfs `/tmp`, so fsync has real cost and page-
   cache semantics are those of the workspace disk. Results
   do not transfer to other filesystems or hosts by default.
4. Calibration history (pre-freeze, disclosed): with
   8000-char notes and kill delays counted from writer spawn,
   one calibration run gave naive only 3/20 trials failed,
   below the leaf's at-least-5/20 gate bar. Payload was
   raised to 32768-char notes and the kill clock was moved to
   after a 50-ACK prefill; the formal gate below is the
   result. Calibration runs are not gate runs and are not
   reported as such; all numbers under "Gate" come from
   gate.sh after the parameters above were frozen.

## Gate (executed 2026-11-07, gate/gate.txt, via gate.sh)

Leaf gate bar: reference visible PASS + crash-grader PASS
20/20 trials x3 runs; naive visible PASS, crash-grader FAIL
in at least 5/20 trials reliably across x3 gate runs;
skeleton ~0.

- Visible (test_visible.py, 5 tests): reference OK (1.4 s);
  naive OK (0.4 s) — the visible suite cannot discriminate,
  which is the treatment, documented in the suite docstring;
  skeleton FAILED (errors=5).
- Reference hidden, 3 runs: FUNCTIONAL 4/4 and CRASH 20/20,
  OVERALL PASS, every run (60/60 trials total; ACKed per
  trial 53-99; grader wall 56.0 / 48.4 / 44.9 s).
- Naive hidden, 3 runs: FUNCTIONAL 4/4 every run; CRASH
  12/20, 13/20, 12/20 i.e. 8, 7, 8 failed trials per run
  (leaf bar: at least 5 failed trials per run, met in all
  three runs), OVERALL FAIL every run (ACKed per trial
  65-110; grader wall 33.7 / 32.9 / 33.3 s). Every naive
  trial failure in all three runs has the single reason
  `load_failed` (torn JSON that a fresh process cannot
  parse); no `invalid_low_acks`, `writer_error` or
  `reopen_failed` occurred for reference or naive (those
  reasons appeared only for the skeleton).
- Skeleton hidden, 1 run: FUNCTIONAL 0/4, CRASH 0/20,
  OVERALL FAIL (6.5 s).

Gate verdict: separation shown, not luck. Reference 20/20 x3,
naive at least 7/20 trial failures x3 with a single mechanical
cause, run-to-run spread of one trial. The lane is frozen
(gate/sha256.txt) and cleared for the n=4 screen under the
instrument-risk wording above. No model episodes run in this
build step.
