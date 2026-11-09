# E1 ledger-admission evaluation

Standalone Python 3.11+ evaluation reconstructed from [input/E1.md](input/E1.md) and [input/README.md](input/README.md). The original grader, reference, private probes and saved answers were not supplied. This package is a new instrument, with authored controls, rather than a recovered original or a model-performance result. Input hashes are verified before grading.

```sh
python benchmark.py question
python benchmark.py grade answer.json > result.json
python benchmark.py demo
python -m unittest discover -s tests -v
python verify_evaluation.py
```

An answer is a JSON object with `task_id: "E1"`, `code` containing complete Python `Service(path)` source, and a nonempty `explanation`. `examples/E1.json` is the authored positive control; keep it and evaluator internals out of solver prompts. The service returns exactly `{"status":"accepted"|"rejected", "remaining": integer}` or `{"status":"payload_mismatch", "remaining":null}`. The public table contract is in the task. Standard-library-only Python is available inside the sandbox.

Exit 0 from grading means the finite formal checks passed; exit 2 means fail, invalid answer, unavailable runtime or review required. `formal_status` is separate from `review_status`; a pass yields `overall_status: formal_pass_review_pending`. There is no creativity, hiring or throughput score. CLI administration commands return 0 on successful creation/structural validation. Malformed JSON, duplicate keys and nonfinite numbers are invalid inputs.

## Executable coverage

Three fresh isolated repetitions each contain these disclosed scenarios:

| Scenario | Observations and failure targets |
| --- | --- |
| Allowance, F5 core | Concurrent idempotent initialization; initial A/B=100 with empty tables; two distinct 60-unit requests to A; both workers acknowledge before either release; accept either serial outcome; inspect the disk immediately after overlap |
| Replay/conflict, F2–F5 | Fresh workers replay each identity; change amount and account under a key; B accepts 100; exact full table comparison catches extra/missing rows and conflict mutation |
| Additional history probe | Spend another 1 from A, replay both earlier decisions at their historical 40; reject B=1 at remaining 0; conflict with accepted/rejected identities; restart and replay all identities; inspect unchanged final state |
| Additional concurrent identity probes | On separate fresh databases, concurrently submit identical same-key requests, then conflicting same-key requests to different accounts; inspect one durable accepted decision and exactly one ledger effect; fresh-instance retries |

There are nine cases: three allowance/history cases and six identity cases. These extensions test F2/F3 using valid request shapes; they are newly authored probes, beyond the specific F5 example sequence. No hidden expectation requires both race winners to appear across repetitions. Scheduling is nondeterministic. The barrier establishes overlapping invocations, not exhaustive internal database interleavings. Cross-account correctness is tested; parallel throughput and actual deadlock behavior are not measured.

The trusted parent records requests, acknowledgments, replies, per-check actual/expected values, independent table snapshots, cleanup terminal codes and diagnostic elapsed time. Elapsed time has no performance grade. Both workers stop before each independent read-only inspection. A separate bounded Python subprocess inspects the public database, with no candidate import. Views, virtual tables, non-primary-key public schemas, symlinks/nonregular DB or sidecars and 100+ rows per table are rejected under the disclosed tiny-suite interface. Extra implementation tables and columns are allowed. Every snapshot is compared to the legal serialized history, including exact JSON integer types, durable rejected decisions and absence of rejected ledger rows.

## Isolation and availability

Actual submitted code runs only on Linux with `bwrap`, `/usr/bin/python3` 3.11+, working unprivileged user/PID/network namespaces and a compatible mounted Python runtime. There are no pip dependencies or model credentials. The current Windows authoring session cannot run this boundary; see [VALIDATION.md](VALIDATION.md) for observed checks and limits.

Each worker receives a disposable shared writable `/state`, private `/tmp`, read-only `/usr` and available runtime library directories, plus read-only candidate/worker files. It receives private PID/network namespaces, dropped capabilities, a cleared environment and no host workspace mount. Limits are 512 MiB address space, 256 FDs, 8 MiB per file, 10 CPU seconds per worker, six wall seconds per startup/acknowledgment/reply and 64 KiB reply size. Stderr is separately capped at 64 KiB. Administrative JSON input is capped at 2 MiB. The independent inspector has a three-second parent deadline, SQLite progress limits and 512 MiB address-space limit on Linux. Workers and their process groups are killed before inspection; cleanup SIGKILL codes are labeled as evaluator cleanup, not candidate crashes or E2 crash-recovery evidence.

An isolation probe runs before the candidate. Unsupported hosts return `unavailable` with no candidate execution. There is no unsafe execution fallback or option to disable isolation. Missing third-party modules, service exceptions, SQL errors, invalid replies, sandbox access failures and deadline violations during candidate execution are formal failures, never synthesized business decisions. Runtime limits apply to the finite interface, not to production architecture recommendations. Bubblewrap and host Python/SQLite depend on kernel/runtime trust; this is not a kernel-exploit resistance claim.

## Stage the reveal

To preserve an initial response before publishing the fixed F6 reveal:

```sh
python benchmark.py start-case initial-state.json > initial-view.json
# Send ONLY initial-view.json to the solver; save its JSON answer as first.json.
python benchmark.py reveal-case initial-state.json first.json revealed-state.json > final-view.json
# Send ONLY final-view.json, with the solver's earlier context; save final.json.
python benchmark.py finish-case revealed-state.json final.json result.json
```

State/output files are created exclusively. The sealed first parsed JSON, its canonical SHA-256 and fixed source/view bindings are preserved and checked at finish. Initial views omit F6 and its hot-account facts. These files establish local ordering and drift detection, not external timestamp authentication or protection from an operator who rewrites every state/hash. `grade` works directly with a final answer and reports `staged:false`. The review rubric keeps first/final revision quality separate.

## Explanation review and evidence limits

Follow [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md), with two independent first reviews and preserved disagreements. `review-template` and `validate-review` provide answer-bound forms and structural checks. They do not grade explanation quality automatically. Alternatives use `alternative_format:true`, nonempty `alternative` and `explanation`; they return `review_required` and are never executed or given an invented pass.

Deterministic tests exercise both serial histories, two positive implementations, the scenario driver, inspection, protocol and eight authored defective implementations. They deliberately use only known authored fixture code in-process, never a submitted answer. This is not evidence of process isolation or race detection. The separate integration test class runs the actual sandbox on compatible Linux, including both positive controls, a read/write race defect and access probes; otherwise it explicitly skips. No real model evaluation, human review, external-side-effect test, E2 kill-during-commit experiment, physical durability or production load test is claimed. [EVALUATION-PROVENANCE.json](EVALUATION-PROVENANCE.json) records the new authoring exposure and scope.
