# E1 ledger-admission evaluation

This is a standalone evaluation authored from [input/E1.md](input/E1.md) and
[input/README.md](input/README.md). It does not reconstruct or claim parity with
the unavailable original grader. The input files are unchanged. The instrument
is a research candidate; explanation quality and operational usefulness require
independent review.

## Run

Use Python 3.11+ and its standard library. Candidate execution additionally
requires Linux, `bwrap`, usable unprivileged user/PID/network/mount namespaces
and `/usr/bin/python3`. Unsupported isolation returns `unavailable`. Candidate
source is never imported or executed by the host grader and there is no unsafe
fallback. No network installation, credentials or external repository is needed.

```sh
python3 evaluate.py answer.json --output evidence.json
python3 -m unittest discover -s tests -v
```

`answer.json` is a JSON object containing `task_id:"E1"`, a complete Python
`code` string defining `Service(path)` with `apply(request)`, and a nonempty
`explanation`. The public interface is exactly the three tables in the task.
No prints to stdout are allowed from the submitted module/service because it
is reserved for the worker protocol. Diagnostic stderr is discarded. JSON must
have unique keys and finite numbers. Submission limits added by this instrument
are 1 MiB per answer and 256 KiB of UTF-8 source; disclose them to the solver.

An alternative architecture can submit `task_id`, `alternative_format:true`,
nonempty `alternative`, and `explanation`. That route returns `review_required`
without executing any supplied source. It gets no fabricated executable pass.

Exit 0 means only the formal checks passed. Exit 2 means formal failure, invalid
submission, unavailable isolation or alternative review required. A formal pass
has `overall_status:"formal_pass_review_pending"` and does not grade explanation
quality. Output files are created exclusively; use a new path for each run.
Reports bind the original answer bytes with SHA-256, retain requests, replies,
oracle states, SQL observations and process terminal codes. Disposable state and
candidate copies are removed after the run.

## Executable contract and evidence

Exactly three repetitions start with separate disposable databases and A=B=100.
Every batch starts fresh service processes, which initialize, acknowledge their
request, and then wait. Both overlap workers must acknowledge before the parent
releases either `apply`. This arms overlapping calls; OS scheduling and internal
SQLite interleavings are not forced. Either serial winner is valid. Different
random key prefixes avoid a fixture that works only for literal public keys.

| Probe | Required observation |
| --- | --- |
| Two released A/60 requests with distinct keys | One accepted and one rejected, both with remaining 40; A=40, B=100; both decisions durable; exactly one ledger row. |
| Both original retries in fresh processes | Exactly their stored decisions, no extra debit or ledger row. |
| Changed amount and changed account for **each** original key | Exact `payload_mismatch` with null remaining, no state changes. Covers accepted and rejected identities and global key scope. |
| Fresh B/100 | Accepted with remaining 0; original A decisions preserved. |

This instrument explicitly adds the following bounded probes beyond the short
F5 sequence. Disclose them with the solver prompt (the staged reveal does so):

| Additional probe | Purpose |
| --- | --- |
| Before B/100, install a `BEFORE INSERT ON ledger` trigger that raises SQLite `ABORT` | A DB write error must yield an exception from `apply` or a JSON error object, never accepted/rejected/payload_mismatch. All public tables must remain at the previous checkpoint. The trigger is then removed and the exact same B key is admitted normally. Catches partial commits and incorrectly persisted business rejections. No specific exception class/error JSON schema is required. |
| Fresh A/40 | Exact exhaustion is accepted with remaining 0. |
| Retry both original A keys after exhaustion | Both must still report their historical remaining 40. Catches implementations that recompute remaining on retry, including rejected retries. |
| Retry B/100 | Same original decision, no new mutation. |
| Fresh A/1 at zero, then retry it | Durable rejection with remaining 0. |

There are 13 named checks per successful repetition, including the database
error check. Failure stops that repetition at the first failed check; remaining
repetitions still run. Unsupported isolation stops execution with `unavailable`.
Initialization is exercised repeatedly under concurrent and sequential fresh
processes; it must preserve all prior state.

After **every** batch all candidate workers are stopped and reaped. A separate
trusted SQL inspector, without candidate source, reads the DB read-only in its
own sandbox. It checks table kind, public column types/order and primary keys,
regular database/sidecar files, SQLite integrity, row caps and stored value types.
All three tables are compared exactly to an independently implemented finite
oracle. Extra implementation tables are permitted. The inspector never invokes
submitted methods. The fault installer is a separate trusted process with a
writable state mount and only the fixed trigger commands.

## Isolation and limits

Workers receive only read-only system runtime directories (`/usr`, `/bin`,
`/lib`, `/lib64` when present), read-only candidate/adapter, writable disposable
`/state`, private `/tmp`, private `/proc` and minimal `/dev`. They have private
network/PID/user/mount namespaces, no capabilities and a cleared environment.
The worker does not receive the oracle, benchmark, input, control sources,
inspector or host workspace. The trusted read-only inspector gets only its own
script, runtime and state. The system runtime mounts must not contain secrets;
use a clean evaluation host. This is not a kernel-exploit resistance claim or
an attestation against a submission tailored to spoof its own worker protocol.

Per process: 512 MiB address space, 256 file descriptors, 8 MiB file-size limit,
10 CPU seconds, no core dumps. Parent deadlines bound startup, arming, each
reply and inspection to six wall seconds; each worker's entire protocol output
is capped at 64 KiB. Both replies in a pair are collected concurrently under
the release deadline. Protocol errors, crashes, excessive output and timeouts
fail the executable route. CPU time is per fresh worker, not a throughput score.
SQL inspection additionally has a two-second progress budget and fewer than
100 rows per public table. Public DB/sidecars must be regular files, not links;
inspection targets must be real tables, not views or virtual tables.

## Stage the operational reveal

```sh
python3 stages.py start initial-state.json
# Give only initial-state.json's `view` to the solver; save first-answer.json.
python3 stages.py reveal initial-state.json first-answer.json revealed-state.json
# Give only revealed-state.json's `view`; save final-answer.json.
python3 stages.py finish revealed-state.json final-answer.json final-evidence.json
```

The initial view contains F1–F5 but withholds F6. Reveal seals the first parsed
JSON response and canonical digest before exposing the full fixed task. Finish
checks state/source hashes and first-answer lineage and attaches first-answer
evidence to the final result. Files are created exclusively. Local hashes detect
accidental changes, not malicious rewriting with recomputed hashes; there is no
external timestamp/identity authentication. Plain `evaluate.py` accepts a final
answer without establishing staging. Neither command queries a model.

Review the explanation under [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md). Do not score
the hot-account answer by keyword presence or fabricate a latency label.

## Validation and limits of inference

`tests/controls.py` contains an authored SQLite reference and seven defective
variants, for evaluator development only. They are not solver performance and
must not be supplied to a solver. Portable tests cover both serial outcomes,
state comparison, historical replies, identity, malformed JSON, alternate-route
admission and qualitative/formal separation. Trusted model controls exercise
the whole orchestration without running candidate code. Trusted SQLite fixtures
test the inspector and trigger; they do not establish sandbox integration.

On a supported Linux host the integration tests also execute the reference and
defective implementations through real isolated workers, plus hangs, output
floods, import errors, exits and basic environment/filesystem/network isolation
checks. A skipped integration test is not a pass. See [VALIDATION.md](VALIDATION.md)
for the actual local validation scope.

The finite suite observes specific terminal/checkpoint states. It cannot prove
atomicity for every internal interleaving, crash point or storage failure. It
does not exercise all SQLite modes, force both winners to occur empirically,
inject a real deadlock, or measure hot-account latency/cross-account throughput.
Unknown-outcome replay is reviewed and approximated by fresh-process replays;
there is no forced lost-response experiment. New models, production deployment,
independent expert review, originality and hiring validity remain unmeasured.
