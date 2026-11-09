# E1 ledger-admission evaluation

This is an independently authored evaluator for [input/E1.md](input/E1.md), using
only the supplied task and [public constraints](input/README.md). It does not
reconstruct the withheld original grader. Python 3.11+ standard library suffices.
Running submitted code additionally requires Linux, `/usr/bin/python3`, bubblewrap
(`bwrap`) and working unprivileged user/network/PID namespaces. Unsupported hosts
return `unavailable`; the CLI has no unsafe execution fallback.

```sh
python3 evaluator.py --check-runtime
python3 evaluator.py answer.json > result.json
python3 -m unittest test_evaluator -v
```

The answer is a JSON object with `task_id: "E1"`, a complete Python `code` string
defining `Service(path).apply(request)`, and a nonempty `explanation`. Public
business status spellings are `accepted`, `rejected`, and `payload_mismatch`.
Replies contain exactly `status` and `remaining`; JSON null is required for
payload mismatch. The alternate route requires `alternative_format: true`,
nonempty `alternative` and `explanation`; it returns `review_required` without
executing code. An empty explanation is a format error; explanation quality is
reviewed independently under [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md).

CLI exit 0 means the finite executable checks passed, with explanation review
pending. Exit 2 means `fail`, `invalid`, `unavailable` or `review_required`. Results
contain a canonical parsed-answer digest and three independent repetition records.
They retain requests, observed replies, worker protocol messages/terminal codes,
independent snapshots and discrepancies against each permitted serial history.
Temporary code and databases are removed after reporting; redirect stdout to
retain evidence. A failed/unavailable execution is never converted into a business
rejection or an automatic zero on architecture quality.
Each repetition stops at its first definitive failure; all three repetitions are
still attempted. A consistent partial trace can never receive a formal pass.

## Declared cases and independent oracle

Each of **three fresh databases** gets this sequence. Every call uses a fresh
process and constructs a new Service against the same database for that repetition.
Initialization of the initial pair can overlap as well.

1. Start two workers, wait for each to initialize, arm A requests for 60 under
   `overlap-1` and `overlap-2`, collect both acknowledgements, then release both.
   Either may win: exactly one accepts with 40 and the other rejects with 40.
2. Replay both requests from other processes. Verify exact historical replies.
3. For both identities, change only account to B, then only amount to 61. Each
   returns `payload_mismatch` with null remaining and changes nothing.
4. Request 100 from B under a new identity. It accepts with 0, independently of A.
5. Accept A's final 40, then replay both original requests. Each must still return
   40, including the rejection, even though A now has 0. Replay B's acceptance.
6. Reject a new 1-unit request from each empty account, then replay each rejection.

After **every stage**, all workers are stopped before a separate trusted process
opens the SQLite file read-only. The oracle compares every public account,
decision and ledger row exactly with a pure specification model, rejecting missing
or extra rows and mutations. It admits either whole serial trace for the overlap,
never a mixture of the two. A cannot go negative, rejected requests have durable
decisions and no ledger entry, and accepted requests have exactly one ledger row.
The extra exhaustion/replay probes make the published historical-reply contract
observable; they are still tiny finite correctness checks, not a load test.

## Execution boundary

Workers see a disposable writable `/state`, private `/tmp`, read-only Python/runtime
files and only their submitted source and adapter. No answer, benchmark, oracle,
review files or inherited secrets are mounted. Network and PID namespaces are
private. The evaluator and temporary root must be outside `/usr`, `/lib`, `/lib64`
and `/bin`, since those read-only runtime trees are mounted. The host environment
is reduced and bubblewrap clears the child environment. Run on a disposable
unprivileged Linux host; this boundary does not claim resistance to kernel exploits
or aggregate host-resource exhaustion.

Before importing a candidate, the adapter sets per-process limits: 512 MiB address
space, 256 descriptors, 10 CPU seconds, 8 MiB file size and no core dumps. Startup,
arming and the released reply each have a six-second wall deadline; both concurrent
replies share their release deadline. Replies are at most 64 KiB. The parent bounds
and validates stdout, rejects duplicate JSON keys, booleans masquerading as integer
balances and invalid statuses, and kills worker process groups on completion/error.
Output is untrusted even if a submission imitates adapter messages; disk inspection
and the independent oracle remain authoritative.

The answer transport limit is 2 MiB JSON / 1 MiB source. Public tables must be real
tables with the specified columns and primary key; extra implementation tables and
columns are tolerated. Database/sidecars must be regular, nonsymlink files, each
at most 8 MiB; inspected public tables contain fewer than 100 rows. Inspection has
a 3-second parent deadline and a SQLite progress deadline. Views, malformed files,
oversized outputs, crashes and protocol errors fail execution rather than fabricate
decisions. File inspection happens after worker teardown, preserving WAL recovery
semantics rather than deleting sidecars before a read.

## Verification and interpretation

[test_evaluator.py](test_evaluator.py) checks the oracle, interface, hostile output,
read-only inspector and actual multiprocess adapter against authored positive and
negative controls. Portable process tests explicitly replace the sandbox launcher
**only for trusted controls**; they do not establish isolation or model performance.
A separate test runs the authored reference through real bubblewrap when available
and otherwise skips. The CLI always retains its isolation gate. See
[VALIDATION.md](VALIDATION.md) for the checks actually run in this workspace.

[examples/E1.json](examples/E1.json) is an authored reference answer. Its code comes
from [reference_service.py](examples/reference_service.py); regenerate it using
`python3 examples/build_reference.py`. Do not expose controls or grader source to a
solver. [examples/alternative.json](examples/alternative.json) tests routing only.

This evaluation does not force all internal transaction interleavings or prove
crash atomicity, unknown-outcome recovery, full error behavior, or production
durability. Those design claims need code/explanation review and further fault
experiments. Timing is used only for disclosed resource limits; there is no
throughput/latency gold score, originality score, human validity or hiring score.
The full E1 question already includes the reveal: a direct submission does not
demonstrate pre-reveal design or subsequent adaptation. For an adaptation study,
withhold F6 and the final hot-account instruction initially, preserve the first
response with its exact source/prompt and digest, then disclose the original full
question and retain both responses for independent review. No staged experiment
is claimed by this package.
