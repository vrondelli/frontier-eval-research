# E1 ledger-admission evaluation

This is a newly authored, standalone evaluation of [input/E1.md](input/E1.md), using the execution and review boundaries in [input/README.md](input/README.md). The original evaluator, example answers, private probes and reviewer rubric were not supplied. This package does not claim to reproduce them. The supplied input and provenance files are unchanged.

## Run

Use Python 3.11 or newer. The evaluator uses only the standard library. Executing candidate code additionally requires **Linux, bubblewrap (`bwrap`), working unprivileged namespaces, and `/usr/bin/python3`**. It returns `unavailable` when isolation is missing; it has no unsandboxed candidate execution mode.

```sh
python evaluate.py question
python evaluate.py grade answer.json --output result.json
python -m unittest discover -s tests -v
```

`answer.json` contains `task_id: "E1"`, `code` (the complete Python `Service` source string), and a nonempty `explanation`. It must be UTF-8 JSON; duplicate keys and nonfinite numbers are rejected. A local CLI envelope limit of 2 MiB applies. Candidate source is loaded as module `candidate` only inside the worker, with standard-library imports available. The evaluator never imports candidate source into its own process.

The CLI prints one JSON report. `--output` also saves it, refusing to overwrite an existing file. Exit 0 means **formal pass only**. Exit 2 covers `fail`, `invalid`, `unavailable` and `review_required`. A pass has `overall_status: "formal_pass_review_pending"`; no explanation score follows from an executable pass.

Alternative architectures use `{"task_id":"E1","alternative_format":true,"alternative":"...","explanation":"..."}`. They receive `review_required`, without running code or inventing an executable grade.

## Executable protocol

There are exactly **three isolated repetitions**, each using a new disposable SQLite database, fresh worker interpreters and opaque request keys. Every sequential request uses a fresh process. In concurrent phases both processes initialize `Service`, acknowledge that their requests are armed, and then receive release messages before either reply is awaited. This creates overlapping invocations; it does not force a particular internal database interleaving.

The declared schedule runs in each repetition:

1. Overlap distinct 60-unit requests to A. Exactly one accepts with remaining 40 and one rejects with remaining 40. Either key may win; the oracle branches over both serial orders.
2. Replay each request from a fresh process, requiring the exact original reply.
3. Change each original key's amount, then its account to B. Every reply must be `payload_mismatch` with null remaining; tables must stay unchanged. Both accepted and rejected identities are checked.
4. Request 100 units from B. It must accept with remaining 0, regardless of the A winner.

By default, the same three repetitions then include these **additional contract probes**, authored here rather than recovered from an original grader:

| Probe | Why it matters |
| --- | --- |
| Two concurrent identical 10-unit requests to A | One decision, one ledger row and one debit; both replies say accepted/30 |
| Request exactly A's remaining 30 | Inclusive allowance boundary and exact exhaustion |
| Replay the original accepted/rejected requests and later accepted requests | Historical remaining survives subsequent spending; a rejection must still report 40 when A now has 0 |
| Two concurrent identical 1-unit requests to exhausted A, followed by a fresh retry | One durable rejected decision at 0, no ledger row |

`--core-only` runs only the declared schedule and labels the report `declared_schedule`. The default is labeled `contract_plus_probes`. Select the suite before collecting responses and compare results only within the same suite. The default performs 20 requests in 12 phases per repetition. The core performs 9 requests in 7 phases.

After every phase, **all candidate processes terminate before inspection**. A separate process opens the database read-only and queries the public accounts, decisions and ledger tables. The oracle compares complete row sets with the state implied by observed legal replies. It checks balances, immutable payloads and historical decisions, accepted-row correspondence, absence of rejected ledger rows, and absence of extra/missing rows. It does not trust a candidate-supplied state summary. Public table names, columns and single-column primary keys are checked; views and virtual tables are refused. Additional implementation tables are ignored.

Reports retain exact requests, raw response envelopes, replies, barrier acknowledgments, terminal codes, independent table snapshots and failure reasons, plus the answer and input SHA-256 bindings. A failing phase ends that repetition; the other repetitions still run. State inspection is attempted after protocol errors as well. Temporary source/databases are removed at the end; preserve the JSON report for evidence.

## Isolation and limits

Bubblewrap provides private network/PID/user and other namespaces, drops capabilities, clears the environment and exposes only disposable writable `/state` and `/tmp`, `/proc`, `/dev`, and read-only candidate/worker/runtime files. Runtime mounts are `/usr/bin/python3`, `/usr/lib`, `/usr/lib64`, `/lib` and `/lib64` where present. The workspace, benchmark, home and host temporary directory are not mounted. Standard-library runtime mounts should be ordinary trusted OS runtime directories, without benchmark data installed in them.

Each candidate worker has 512 MiB address space, 256 file descriptors, 10 CPU seconds, 8 MiB per-file size, disabled core dumps, a six-second reply deadline and a 64 KiB reply bound. Startup and shutdown are also bounded. The inspector has its own process limits, a six-second reply deadline, a SQL progress bound, and a maximum of 99 rows per public table. Database files and conventional SQLite sidecars must be regular files, not symlinks. Inspection mounts `/state` read-only. Candidate stdout is a strict JSON protocol; unsolicited output fails the run. Diagnostics should go to stderr.

These are process limits, not aggregate cgroup limits. The sandbox is not a proof against kernel exploits or all denial-of-service attacks; run genuinely hostile submissions on a disposable, resource-contained Linux host. There is no unsafe fallback if isolation fails.

## First answer and fixed reveal

For an adaptation experiment, supply only the `view` at each stage to the solver:

```sh
python evaluate.py start-case initial.json
python evaluate.py reveal-case initial.json first-answer.json revealed.json
python evaluate.py finish-case revealed.json final-answer.json staged-result.json
```

The initial view includes F1-F5 and execution constraints but hides F6. Reveal preserves the first parsed JSON answer and its digest before exposing the full fixed hot-account question. Finish checks source/lineage and attaches the first answer for separate review. Administrative state, evaluator code, controls and future views must not be solver input. Files are created exclusively. The chain detects accidental modification; anyone able to rewrite all files can recompute it, so it is **not external authentication or timestamping**. Plain `grade` does not establish a staged experiment. If a first answer is malformed JSON, retain the raw artifact externally and record that failure; do not silently replace it with a corrected answer.

## Explanation review

```sh
python evaluate.py review-template answer.json review.json
# Two independent reviewers each complete a separate copy using REVIEW-RUBRIC.md.
python evaluate.py validate-review answer.json review.json
```

See [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md). Form validation checks answer binding, coverage, reasons and quote existence. It cannot verify reviewer identity/independence or the correctness of judgments. Preserve separate first reviews and disagreements before adjudication. Alternative architectures may be useful and valid even when they cannot be executed through this interface.

## Validation and controls

`tests/control_service.py` is a newly authored positive control, not a model answer. `tests/make_controls.py` emits it or deliberate faults: missing ledger rows, lost rejections, ignored mismatches, account-scoped keys, current rather than historical remaining, destructive initialization, unconditional rejection and overdraw. **Do not send these controls to a solver.**

```sh
python -m tests.make_controls reference > reference.json
python evaluate.py grade reference.json
python -m tests.make_controls historical_remaining > faulty.json
python evaluate.py grade faulty.json
```

Portable tests exercise both oracle orders, adversarial replies/states, real SQLite inspection with the trusted authored control, barrier sequencing, alternative/unavailable routing, review binding and reveal custody. Linux integration tests execute actual isolated candidate processes and all authored fault controls; they explicitly skip when isolation is unavailable. A green portable test run with skipped integration is not live qualification. [VALIDATION.md](VALIDATION.md) records what actually ran here.

Finite observations cannot prove all interleavings, transaction atomicity under arbitrary crashes, power-loss durability, throughput, cross-account parallelism, or production deployment readiness. Unknown-outcome replay and the hot-account diagnosis are reviewed in the explanation; E1 does not inject a commit-time crash. The six-second deadline is an execution constraint, not a performance gold label. No creativity, originality, hiring or population-level model-performance score is produced.
