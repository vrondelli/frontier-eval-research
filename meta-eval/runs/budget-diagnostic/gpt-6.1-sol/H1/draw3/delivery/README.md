# E1 ledger-admission evaluation

This is a new evaluation built only from [the supplied task](input/E1.md) and
[its public runtime contract](input/README.md). It is not a recovery of the original
grader or reference. It measures finite admission correctness and separately
supports explanation review. No model performance, hiring validity, creativity
score, exhaustive concurrency proof or throughput claim is produced.

## Run

Python 3.11+ standard library is sufficient. Executing a submitted service requires
Linux, `bwrap`, working unprivileged namespaces, and `/usr/bin/python3` with SQLite.
On unsupported systems the evaluator returns `formal_status: unavailable` and
does not execute submitted code. There is no isolation bypass.

```sh
python evaluate.py answer.json --output report.json
python -m unittest test_evaluation -v
```

`answer.json` contains `task_id: "E1"`, the complete `code` string defining
`Service(path)` with `apply(request)`, and a nonempty `explanation`. Candidate code
must be standard-library Python, self-contained in that source string. An answer
may instead submit `alternative_format: true`, `alternative: "..."`, and
`explanation: "..."`; this produces `review_required` without executing code.

Exit 0 means the finite executable checks passed; exit 2 means failure, invalid
input, unavailability or review required. Successful execution still has
`overall_status: formal_pass_review_pending`. Explanation presence is validated,
but quality is reviewed using [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md).

## Declared experiment

Each of three repetitions starts with a separate empty database. Two fresh service
processes initialize against that database, receive distinct 60-unit A requests,
and acknowledge that they are armed before either is released. This overlaps their
application windows; it cannot force every internal database interleaving. Either
request may win. One must be accepted at remaining 40 and the other rejected at
remaining 40.

Every subsequent call uses another fresh service process, testing idempotent
initialization and process-independent durable decisions. The sequence is:

1. Replay both overlap requests.
2. Change the first key's amount; change the second key's account to B. Both must
   return `payload_mismatch` and null remaining without any database change.
3. Request all 100 units from B, independently of A.
4. Spend A's remaining 40 with a new key; replay both original requests again.
   Each original reply must still report its historical remaining 40, including
   the rejected decision, although A is now at 0.
5. Reject a fresh 1-unit A request twice and replay B's full debit.

The final balance is A=0, B=0, with three accepted ledger rows and five decisions.
The extra tail debit/replays are disclosed probes of F2's historical remaining
rule. The evaluator enumerates both permitted serial outcomes and compares every
reply and complete public table contents against one consistent outcome.

Workers stop before each independent inspection. The parent opens SQLite in a
separate trusted process, read-only, with a three-second inspection deadline and
bounded query work. It verifies integrity, ordinary tables, declared column types
and primary keys, fewer than 100 rows per table, and exact accounts, decisions and
ledger contents. Extra implementation tables are allowed. State symlinks are
rejected. Unchanged snapshots establish that replay/mismatch did not alter public
state at the observed checkpoints; extra private implementation tables are not
compared.

## Isolation and evidence

Each worker has private network, PID, IPC, user and other namespaces; an empty
environment; read-only Linux runtime, candidate and worker files; writable
disposable `/state` and private `/tmp`; and no benchmark, oracle, test, reference or
credential mount. Limits are 512 MiB address space, 256 FDs, 8 MiB file size,
10 CPU seconds per process, 6 wall seconds for startup and each reply, and 64 KiB
per protocol line. Workers and their descendants are torn down before inspection.
An exception, timeout, malformed reply or failed exit is an executable failure,
never an accepted/rejected business response. Isolation startup failures detected
by the trusted preflight are `unavailable`.

Reports bind the parsed answer with a canonical JSON SHA-256 and retain requests,
observed replies, worker terminal codes, independent snapshots, and diagnostic
failures. Temporary source and state are removed. Worker stderr is discarded;
protocol violations and terminal codes remain recorded. The task source is
included only in the parent evaluation workspace, not in worker mounts.

The authored positive fixture is in `tests/fixtures/reference.py`. Do not show it
or the tests to a solver. Tests include both serial winners, historical replay,
overdraft/double acceptance, missing ledger/rejection, duplicate ledger, payload
conflict mutation, reset-on-initialization, database exceptions, schema/view
substitution and unsupported isolation. Real sandbox integration controls run only
when the declared isolation is available; skipped checks do not establish a pass.

## First answer and reveal

For the fixed reveal experiment, seal the first parsed answer before exposing F6:

```sh
python protocol.py start stage0.json
# Give only stage0.json's view to the solver; save its first JSON answer.
python protocol.py reveal stage0.json first-answer.json stage1.json
# Give only stage1.json's view to the solver; save the final JSON answer.
python protocol.py finish stage1.json final-answer.json report.json
```

Output files are created exclusively. Source and state hashes check local lineage
and preserve the initial answer for review. They are not external timestamping or
tamper-proof custody: someone with file access can recompute hashes. Direct
`evaluate.py` grading evaluates a final artifact and makes no staged-experiment
claim. Do not supply the full source question to the solver before a staged run.

## Boundaries

This suite does not inject crashes during commit, exhaustively explore schedules,
stress sustained hot-account traffic, or prove transaction atomicity under all
failures. It checks visible durable consistency at finite checkpoints. There is no
latency gold label. Hot-account diagnosis, unknown-outcome recovery, deployment
tradeoffs and useful alternative architectures require independent review.

See [VALIDATION.md](VALIDATION.md) for checks actually performed on this host.
