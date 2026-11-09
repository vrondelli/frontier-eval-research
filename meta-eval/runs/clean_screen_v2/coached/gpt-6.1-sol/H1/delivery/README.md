# E1 ledger-admission evaluation

This standalone package evaluates the task supplied in `input/E1.md`. All graded
requirements, including inspection and resource constraints, are in [TASK.md](TASK.md).
Give **only TASK.md** to a solver. Keep `e1eval/`, controls, references, reports and the
source input README evaluator-side. The original `input/README.md` describes an upstream
ten-task package whose other assets are not present; none are required here.

Python 3.11+ and its standard library suffice for authored-control verification.
Untrusted submission grading additionally requires Linux, `bwrap`, working unprivileged
user/network/PID namespaces, and `/usr/bin/python3`. There are no pip dependencies,
credentials, model calls, or sibling repositories. Run from a writable directory with
this package on the Python module path. Temporary directories are created in the current
directory and cleaned after each invocation.

```sh
# Cross-platform verification: ONLY repository-authored controls execute locally.
python -m e1eval verify --output verification.json

# Required Linux production-backend qualification; fails if isolation is unavailable.
python3 -m e1eval verify --sandbox --output sandbox-verification.json

# Export an evaluator-only answer; do not send it to the solver.
python -m e1eval reference --output reference-answer.json

# Actual submission grading, always isolated, never a local execution fallback.
python3 -m e1eval grade answer.json --output report.json
python -m e1eval validate-report report.json

# Run smaller harness tests separately if needed.
python -m unittest e1eval.test_eval -v

# Repeat in a new directory, or build the evaluator ZIP with a hash manifest.
python tools/clean_check.py
python tools/package.py
```

`verify` exits 0 only when unit tests and both positive and all negative control
expectations match. Its optional `--sandbox` additionally requires the reference and
every control to match through real bubblewrap workers. A normal verification on a
non-Linux host records `sandbox_probe.status=unavailable`; that is not sandbox
qualification. `grade` exits 0 only for a formal pass and exits 2 for all other report
statuses, including unavailable and review-required. See [VERIFICATION.md](VERIFICATION.md)
and the retained JSON artifact for the actual verification scope on this host.

The executable reference in `e1eval/reference.py` uses one immediate SQLite transaction.
The independent pure state machine in `e1eval/oracle.py` does not import the reference,
SQLite, or candidate code. It enumerates legal serial orders and predicts replies and
all public rows. The parent inspector never asks the candidate to report its own state.
Both reply and database observations must agree with one legal outcome. Three isolated
trials use fresh service processes, including replays. Errors during acceptance and
rejection are injected using real aborting SQLite triggers.

Authored controls cover a valid conditional-debit strategy, explicit JSON storage errors, overspend, missing ledger,
missing debit, lost rejection, changing historical replay, ignored payload conflicts,
account-scoped identity, resetting initialization, split commits, storage errors turned
into business decisions, an unlocked race, replay side effects, wrong value types,
worker crashes, and malformed replies. Unit tests also check both serial winners,
duplicate/conflicting keys, schema inspection, strict input/report validation, bounded
output, timeouts and cleanup. These are authored test cases, not model performance.

`e1eval/report.schema.json` is a Draft 2020-12 report schema. The dependency-free validator
also checks consistency between status fields and that a formal pass has three successful
trials. Reports retain every completed step's requests, observed replies, terminal codes,
independently inspected rows, legal outcomes, failing checks and diagnostics. The
submission digest hashes canonical parsed JSON: sorted keys, compact separators,
ASCII escapes, UTF-8 encoding, SHA-256. Invalid unparsed input is identified diagnostically
instead of being treated as an executable response.

The clean runner mounts only the candidate source, worker adapter, system runtime and
disposable state. It clears inherited environment secrets and isolates networking.
No evaluator files or reference are mounted. The Linux sandbox depends on the host
kernel and bubblewrap; this package makes no claim against kernel exploits. The
cross-platform internal trusted-control mode has no such isolation or OS resource
guarantees and is never exposed as a submission-grading CLI option.

Formal success leaves explanation review pending under [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md).
There is no numeric combined score. This is a final-answer evaluation with a disclosed
fixed reveal, not a staged adaptation experiment. Three finite schedules do not prove
all interleavings, production crash durability, performance, human transfer, or hiring
validity. The original input files are retained unchanged for provenance.
