# E1 ledger-admission evaluation

A standalone reconstruction from the two supplied public inputs. This package does not
recover or claim parity with the withheld original grader, private probes, reference
answer or historical candidate results. Inputs in `input/` remain unchanged.

Python 3.11+ and the standard library are sufficient for portable harness tests.
Submitted code executes only on Linux with `bwrap`, working unprivileged namespaces
and `/usr/bin/python3`. The evaluator returns `unavailable` on unsupported hosts.

```sh
python -m unittest -v test_evaluation
python evaluate.py answer.json --output result.json
```

The answer is one JSON object with `task_id: "E1"`, `code` containing complete Python
`Service` source, and a nonempty `explanation`. Only standard library imports are
available. Use at most 1 MiB of answer JSON. Do not wrap it in Markdown fences.
Alternative-format answers use `alternative_format: true`, `alternative` and
`explanation` instead of executable code. They receive `review_required`.

Exit 0 means formal pass with explanation review pending. Exit 2 means formal fail,
invalid input, review required or unavailable; inspect `formal_status` for the reason.
Output files are created exclusively, so evidence is never silently overwritten.
`answer_sha256` binds canonical parsed answer JSON; `source_sha256` binds the actual E1
input bytes. Cases retain generated requests, barrier/worker messages, SQL snapshots,
process terminal codes, failure reasons and compatible serial orders. Reports can
contain submitted source indirectly through staged first responses; store them accordingly.

## Executable checks

The core suite uses exactly three isolated databases. In each repetition:

1. Two fresh `Service` processes initialize the same database. Both acknowledge
   armed 60-unit requests against A before either receives a release message.
2. The parent accepts either legal serial order: one acceptance and one durable
   rejection, each with remaining 40; A has 40, B has 100 and exactly one ledger row.
3. Workers stop and the parent independently inspects actual SQLite state. Fresh
   processes replay both requests and change each key's amount and account. All
   original decisions survive, and mismatches change nothing.
4. B spends 100. A spends its remaining 40; both original A requests are replayed
   again, exposing implementations that substitute current balance for history.
   New one-unit requests against exhausted A and B reject durably. Repeated B100
   and A40 return their original decisions.
5. Workers stop and state is inspected again. Fresh processes initialize and replay
   accepted/rejected decisions, then stop for a third independent inspection.

Each checkpoint compares **all** public rows against the independent model in
`oracle.py`, including exact account/amount/status/history, ledger membership,
uniqueness and allowance conservation. Process restarts expose resets and in-memory
identity caches. Replies alone cannot establish a pass. JSON booleans/floats do not
count as integer balances. Database exceptions and malformed replies fail execution;
they are never converted to an insufficient-allowance decision by the harness.

Three explicitly supplemental identity cases each use a fresh database: simultaneous
identical same-key requests, same-key/different-amount requests (60/80), and
same-key/different-account requests (A/B). Both serial orders are permitted, followed
by replay and restart checks. These extend the disclosed base workload using F2's
global identity rule. They are separately labeled in reports. Keys are generated
per run and preserved in evidence. The suite is finite and its cases are public.

## Staged delivery and review

For an experiment evaluating revision after the hot-account reveal, use:

```sh
python stages.py start initial-state.json
# Give only initial-state.json's view to the solver. Save its first JSON answer.
python stages.py reveal initial-state.json first-answer.json revealed-state.json
# Give only revealed-state.json's view to the solver. Save its final JSON answer.
python stages.py finish revealed-state.json final-answer.json staged-result.json
```

The first view includes F1-F5 and runtime limits; F6 appears only after the first
parsed response and canonical digest are recorded. Invalid first responses are retained,
not discarded. Finish verifies phase, source and transcript bindings and attaches the
first response to the final formal report for review. Local hashes detect accidental
drift; an administrator can rewrite and rehash files. They provide no external timestamp,
identity authentication or proof that the solver did not see the reveal elsewhere.
`evaluate.py` alone grades a final answer and establishes no staged experiment.

Use [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md) for atomic boundaries, global identity,
unknown-outcome replay, hot-account diagnosis, parallelism, first mitigation and rollback.
Explanation presence is validated automatically; its quality is judged separately.
A formal pass is always `formal_pass_review_pending`. No aggregate hiring or
creativity score is produced and no latency gold label is fabricated.

## Runtime isolation and inspection

Each process receives only read-only `/usr` and existing `/lib`/`/lib64` runtime
directories, the submitted source and adapter; writable shared disposable `/state`;
private `/tmp`, `/dev`, `/proc`; private network/PID namespaces; dropped capabilities;
and a cleared environment. It cannot import this evaluator or access the repository,
credentials or host home directories. The source is never imported by the parent.
The mounted runtime directories are not a claim that every file in `/usr` has been
individually audited for host data. Use an appropriate dedicated evaluation host.

The adapter sets 512 MiB address space, 256 file descriptors, 8 MiB maximum file size
and 10 CPU seconds per process. Initialization, barrier acknowledgment and replies
have six-second deadlines; reply output is capped at 64 KiB. Worker exceptions are
reported as execution errors. Standard output belongs to the JSON protocol, so
debugging prints there are invalid. Standard error is discarded, rather than captured
without bounds. An early/abnormal exit fails the relevant protocol operation. After
EOF, workers have 0.5 seconds to exit before their process group is killed. Group
cleanup and bubblewrap PID namespaces prevent candidate writers surviving inspection.

Inspection uses a separate bounded parent-side Python process, read-only SQLite,
disabled extensions/trusted schema, a query deadline and conservative SQLite limits.
The database and sidecars must be regular files, the three public relations ordinary
tables with their declared primary keys, and each must contain fewer than 100 rows.
Extra implementation tables/columns are allowed. Sidecar symlinks, views, corrupt
databases, missing rows and invented extra public rows cannot produce a pass.
Temporary state is removed; report JSON preserves observations. Use `TMPDIR` to
select an appropriate disposable filesystem on Linux if needed.

This is a benchmark sandbox, not a guarantee against kernel or SQLite exploits,
fork bombs or aggregate disk exhaustion. Use a disposable resource-bounded host for
untrusted submissions. Never substitute unsandboxed execution when namespaces fail.

## Authored controls and evidence limits

```sh
python controls.py --write generated-controls
python controls.py --check > controls-report.json
```

Do not send `controls/reference.py`, generated controls or evaluator source to a solver
as answer examples. The positive control and nine defective variants test missing
ledger writes, lost rejections, current-balance replay, ignored payloads, overspending,
initialization resets, unconditional rejection, database-error-as-rejection and
process-local storage. `controls.py --check` requires the real supported sandbox;
unavailability is a nonzero result, never control success.

Portable tests use a **test-only synchronous adapter with authored source** for
coordinator/oracle integration and real SQLite snapshots. They also exercise a real
two-thread SQLite race and independent inspection subprocess. These are distinct from
the real two-process bubblewrap test, which skips explicitly on unsupported hosts.
No user submission uses the test adapter. See [VALIDATION.md](VALIDATION.md) for the
checks actually run in this authoring environment.

The barrier coordinates entry at the adapter, not internal SQL instructions. It does
not force every interleaving or guarantee a flawed race will manifest. Graceful process
restart checks durable visible state; E1 does not inject SIGKILL at commit, power loss,
storage errors, day rollover, invalid accounts/amounts, settlement or refunds. Unknown
commit outcomes and failure atomicity require explanation review and further fault
experiments. A finite pass is not a proof of universal concurrency safety, throughput,
crash durability, human transfer or assessment validity. No fresh model evaluation or
independent expert review was run while authoring this package.
