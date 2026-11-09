# E1 ledger-admission evaluation

This is a standalone evaluator for [input/E1.md](input/E1.md). The supplied
[input/README.md](input/README.md) describes a larger package which is absent here;
this implementation covers E1 only. Python 3.11+ and the standard library suffice
for the oracle, admission checks, staged flow and review tools. Executing submitted
code requires Linux, `bwrap`, `/usr/bin/python3` and working unprivileged namespaces.
Windows and broken isolation return `unavailable`; there is no execution fallback.

```sh
python evaluator.py grade answer.json --output report.json
python -m unittest discover -s tests -v
```

The input is one JSON object with `task_id: "E1"`, `code` (complete Python source
defining `Service(path)`), and a nonempty `explanation`. Status literals are
`accepted`, `rejected`, and `payload_mismatch`. A valid alternative uses
`alternative_format: true`, a nonempty `alternative`, and `explanation`, and gets
`review_required` without executing source. Input limits are 1 MiB per answer and
128 KiB of UTF-8 source. Duplicate JSON keys and nonfinite numbers are invalid.

Output files are created exclusively, so reruns need a new filename. Exit 0 means
the declared executable checks passed. Exit 2 covers formal failure, invalid input,
unavailable isolation, review required, or CLI errors. Reports separate
`formal_status` from `overall_status`; a pass is `formal_pass_review_pending`.
Explanation presence never establishes explanation quality. No scalar creativity,
originality, performance or hiring score is calculated.

## Executable protocol

Each of **three** repetitions has a fresh disposable database and fresh random keys:

1. Start two independent service processes using the same SQLite path. Both finish
   initialization and acknowledge their pending 60-unit request to A before either
   receives the release command. Both are released before awaiting a reply.
2. Repeat each request from a separate fresh process. Replies must exactly match
   the original `{status, remaining}`, including the rejected request's value.
3. For each original key, change its amount to 61, then separately change its
   account to B. Each of these four fresh-process calls must return exactly
   `{status: "payload_mismatch", remaining: null}` and leave state unchanged.
4. In another fresh process request 100 from B. It must be accepted with remaining 0.
5. Stop all workers, then independently inspect the three public tables read-only.

There are nine service processes per repetition, 27 in the declared suite. Either
overlap winner is valid. The oracle enumerates A's two serial outcomes and requires
**one same outcome** to explain every reply and every row. Both accepted, both
rejected, a negative balance, missing rejected decisions, duplicate effects, extra
rows and replies inconsistent with persisted state fail. Table columns/types and
primary keys follow F4; extra implementation tables are ignored. Inspection rejects
views, virtual tables, database/sidecar symlinks, noninteger amounts/remaining and
100 or more rows per public table. It has a three-second subprocess deadline and a
SQLite VM instruction budget. A shutdown that cannot be confirmed prevents inspection.

Barriers establish overlapping invocations, not simultaneous instructions inside
SQLite. The suite does not force both winners to occur or enumerate all internal
interleavings. Every repetition runs even if another fails. Reports retain request
plans, worker acknowledgments, replies, bounded diagnostics, terminal codes, expected
histories, independent observations, and exact hashes of answer, protocol and harness.
Disposable source and databases are removed after evaluation.

## Isolation and limits

Bubblewrap provides private user, network and PID namespaces, read-only runtime
directories and candidate/adapter files, private `/tmp`, and one writable disposable
`/state`. The worker receives no benchmark, oracle, answer files, original working
directory or inherited environment secrets. Candidate stdout is redirected to bounded
diagnostics so ordinary prints cannot corrupt the adapter's separate protocol stream.

The worker sets per-process limits before importing the candidate: 512 MiB address
space, 256 descriptors, 10 CPU seconds, 8 MiB file size, and no core dumps. Replies
have a shared six-second deadline after releasing the concurrent pair and a 64 KiB
adapter-message limit. Initialization and barrier acknowledgments are also bounded.
Malformed output, exceptions, timeouts and abnormal worker exits fail a repetition;
they are never recorded as business rejections. Inspection runs only after workers stop.

These are the declared small research-test constraints. Resource limits are per
process, not a container-wide cgroup budget; this is not a kernel exploit resistance
claim. Use a disposable Linux runner for untrusted submissions. An unavailable
preflight does not execute candidate source and cannot produce a pass.

## Explanation and fixed reveal

Use only each state's `view` as solver input. Keep evaluator source, controls,
reviewer guidance and administrative state away from the solver. Give the initial
view with the runtime/input limits above, without the reveal or this full README.

```sh
python staged.py start-case case-0.json
# Give only case-0.json's view to the solver; save the first JSON answer.
python staged.py reveal-case case-0.json first-answer.json case-1.json
# Give only case-1.json's view to the solver; save the final JSON answer.
python staged.py finish-case case-1.json final-answer.json result.json
```

The initial view contains F1–F5. Reveal preserves the first answer's original UTF-8
bytes, parsed object and hash before publishing F6 and the complete final contract.
Finish checks source and lineage and attaches the first answer to the final report.
Exclusive files and local hashes detect accidental drift; they do not authenticate
external timestamps, prevent deliberate rewriting by the operator, or prove that a
solver lacked earlier exposure. Plain `grade` has no staged-experiment claim. No
model calls are made by these tools.

```sh
python evaluator.py review-template answer.json --output review-1.json
# Independent reviewer completes review-1.json using REVIEW-RUBRIC.md.
python evaluator.py validate-review answer.json review-1.json
```

Review-form validation checks exact answer binding, reviewer/independence declarations,
criterion coverage, reasons and quote existence. It cannot authenticate the reviewer
or the truth of judgments. Keep two separate first reviews, retain disagreements,
then document adjudication. Alternative architectures receive the same review route
and no fabricated executable pass/fail.

## Authored controls and validation boundaries

```sh
python tools/make_control.py reference-control.json
python evaluator.py grade reference-control.json --output reference-report.json
```

The generated answer and [reference implementation](tests/fixtures/reference_service.py)
are authored harness controls, not model performance or independently validated
ground truth. Never send them to a solver. Linux integration tests run this control
and faulty implementations (nondurable rejections, ignored amount conflicts, balance
resets, a forced lost-update race and fabricated acceptance) inside real sandboxes, and test network/filesystem
isolation. They skip explicitly when the required Linux runtime is unavailable.
Portable tests exercise both overlap winners, fifteen corrupted observations, real
SQLite inspection, input admission, review validation and sealed-reveal lineage.

The declared schedule does **not** inject database failures, kill a process around
commit, spend A's last 40 before replay, or race two requests under the same key.
Consequently a finite pass cannot prove general atomicity, unknown-outcome safety,
historical replay after later spending, or every identity race. The model represents
historical decisions, and review must examine those claims in code/explanation;
do not describe model tests as observations of a submitted service. These additional
stress cases would require a separately declared protocol revision. B's successful
100-unit request establishes logical independence for that history, not simultaneous
cross-account writes. Hot-account contention, deadlock diagnosis, throughput and
latency are reviewed qualitatively; there is no executable latency gold label.

See [VALIDATION.md](VALIDATION.md) for checks actually run in this workspace.
