# E1 ledger-admission evaluation

This is a new standalone evaluation reconstructed from the public
[task](input/E1.md) and [package description](input/README.md). The original
grader, private probes, original reference and saved candidate responses were
not available. Input files, MANIFEST.json and PROVENANCE.json are preserved.
The new code and controls make no claim of exact replication.

## Run

Python 3.11+ standard library; executable candidate grading additionally requires
Linux, `bwrap`, working unprivileged namespaces and `/usr/bin/python3` with SQLite.
Run in a writable directory; disposable directories are created under the current
directory and removed afterward. No pip install, model API or credentials.

```sh
python evaluate.py answer.json --output result.json
python -m unittest discover -v
```

`answer.json` is a UTF-8 JSON object with `task_id: "E1"`, `code` (the complete
Python source defining `Service(path)` and `apply(request)`), and `explanation`
(nonempty text). A response envelope is limited to 1 MiB; duplicate JSON fields,
non-JSON numeric constants and invalid Python syntax are rejected. No candidate
code is imported by the parent. Result files are created exclusively.

`status`/`formal_status` describe the executable checks only. A pass has
`overall_status: "formal_pass_review_pending"`. Explanation presence does not
establish explanation quality. Other results are `fail`, `invalid`, `unavailable`
or `review_required`. Exit 0 means formal pass; exit 2 means any other result.
A missing isolation runtime returns unavailable before candidate execution and
does not become a candidate failure or an unsafe host run.

An answer with `alternative_format: true`, `alternative` and `explanation`
receives `review_required`, with executable correctness `not_executed`. Review it
under [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md); no automatic score is invented.

## Declared finite checks

Three fresh databases are evaluated. Each has this scenario:

1. Start two fresh service processes on the same empty database. Both initialize
   and acknowledge an armed, distinct-key A/60 request before either is released.
   Send both release messages before waiting for results; alternate release order
   across trials. Either serial winner is valid. Exactly one result is accepted/40
   and one is rejected/40.
2. Replay each request in the other process. Change amount and account separately
   under **each** existing key; require payload_mismatch/null with no effects.
3. Admit B/100 to check independent allowance, drain A's remaining 40, then reject
   A/1 and B/1 at zero. Replay the original accepted and rejected A/60 requests
   after the balance changes; both must retain their historical remaining=40.
4. Start a third fresh Service on the same database and replay accepted and
   rejected decisions from both accounts. Initialization must not reset state.
5. Stop all workers, then independently read the ordinary public accounts,
   decisions and ledger tables. Compare **every** row to the serial state model,
   including no extra rows, one ledger row per accepted request, no ledger for a
   rejection, and the exact public column types/primary keys. Extra implementation
   tables/columns are permitted. Symlink/reparse targets and sidecars are rejected.

Requests/replies, barrier acknowledgments, terminal codes, permitted serial order,
expected SQL and actual SQL are retained in JSON reports. Random request keys
prevent reliance on fixed labels. Inspection is read-only with a SQLite progress
deadline and an outer three-second process deadline; public tables must have fewer
than 100 rows and database/sidecars are each limited to 8 MiB, as disclosed.

This is a finite correctness test. It does not force internal lock acquisition,
enumerate all interleavings, test throughput, measure production latency, prove
all rollback paths or execute E2's crash/kill experiment. Unknown commit outcomes,
database-error handling and hot-account diagnosis are also reviewed in the code
and explanation. A lost response is not evidence of rejection.

## Isolation

Each worker gets only a disposable writable `/state`, private `/tmp`, read-only
candidate/adapter/runtime, and private PID/network namespaces. Environment secrets
are not inherited. Runtime mounts are `/usr`, `/bin`, `/lib`, `/lib64` where
present, and the dynamic-loader cache. The worker sets hard limits before import:
512 MiB address space, 256 FDs, 8 MiB files, 10 CPU seconds per process, no core
dumps. Every initialization/command reply has a six-second absolute deadline and
a 64 KiB JSONL bound. Candidate stdout/stderr are redirected away from the adapter
protocol. Workers are stopped/killed before parent inspection. Bubblewrap relies
on the host kernel; these controls are not a kernel-exploit resistance claim.

## Seal, then reveal

For the staged experiment, give only each `view` to the solver. Do not expose the
reference, controls, administrative state or final question before the reveal.

```sh
python staged.py start initial-state.json
# Give initial-state.json's view only; save first response to first-answer.json.
python staged.py reveal initial-state.json first-answer.json revealed-state.json
# Give revealed-state.json's view only; save final response to answer.json.
python staged.py finish revealed-state.json answer.json staged-result.json
```

The first answer needs `task_id: "E1"` and a nonempty `explanation`; code is
optional. The initial view contains F1-F5, not F6's fixed operational facts. The
reveal preserves the parsed first answer and its exact-byte/canonical digests
before publishing the full fixed question. Finish verifies the view/parent/content
bindings and attaches the first answer to the graded report for separate review.
Hashing is local content binding, not external authentication or proof of time.
Plain `evaluate.py` makes no staged-experiment claim.

## Validate the evaluator

The two authored positive controls use immediate and exclusive SQLite transactions.
Ten faulty controls omit the ledger, forget rejections, replay current balances,
ignore changed amounts/accounts, reset initialization, debit incorrectly, replace
the ledger with a view, roll back acknowledged writes, or read before locking.
These are evaluator-development checks, not model-performance observations.

On Linux, run all controls through the actual isolation boundary:

```sh
python verify_controls.py --output isolated-controls.json
python make_control.py reference reference-answer.json
python evaluate.py reference-answer.json --output reference-result.json
```

For a host that cannot run bubblewrap, the following runs **only predeclared
authored fixture names** in separate host processes. It cannot load a submitted
answer, and is not available as a fallback in candidate grading:

```sh
python verify_controls.py --trusted-controls --output trusted-controls.json
```

The unit suite checks both possible serial winners, malformed replies, stale
rejection replay, strict envelopes, alternative routing, staging, SQL inspection,
an injected rollback failure on the reference, deadline handling and fail-closed
availability. The isolated integration test is explicitly skipped if unsupported.
See [VALIDATION.md](VALIDATION.md) for what actually ran here and the remaining
Linux qualification step.
