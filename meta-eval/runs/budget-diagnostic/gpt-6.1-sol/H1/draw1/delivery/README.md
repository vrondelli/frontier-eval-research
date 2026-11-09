# E1 ledger-admission evaluation

This standalone evaluator implements [input/E1.md](input/E1.md). It reports finite executable correctness separately from explanation review. It is newly authored from the two public input files; it does not reconstruct or claim access to the withheld original grader, reference, probes or candidate answers. Python 3.11+ and its standard library are sufficient for the evaluator. Candidate execution additionally requires Linux, `/usr/bin/python3`, bubblewrap (`bwrap`) and working unprivileged namespaces.

## Run

Save the solver's JSON object as `answer.json`:

```json
{"task_id":"E1","code":"<complete Python source defining Service>","explanation":"<design and response to the reveal>"}
```

```sh
python evaluate.py grade answer.json > result.json
python -m unittest -v test_evaluation
```

`Service(path).apply(request)` must return exactly `{"status":"accepted","remaining":integer}`, `{"status":"rejected","remaining":integer}`, or the task's `{"status":"payload_mismatch","remaining":null}`. This evaluator uses the prose terms `accepted` and `rejected` as the executable status spellings. Only valid positive-integer requests against A/B are issued. Extra reply fields and numeric strings/floats/booleans are not accepted as integers. SQL row order does not matter.

If the host's default temporary directory is not writable, set `TMPDIR` (Linux) or `TEMP` and `TMP` (Windows) to a writable directory before running. Candidate execution has no Windows/native/unsafe fallback. WSL is not invoked automatically. On an unsupported host `grade` returns `unavailable`, exit 2, before executing submitted Python.

| Result | Meaning |
| --- | --- |
| `pass` | All three declared executable repetitions passed; `overall_status=formal_pass_review_pending`. |
| `fail` | A request, reply, process, deadline or independent state observation failed after isolation preflight. |
| `invalid` | Invalid answer JSON, required fields or Python syntax. |
| `unavailable` | Required isolation/runtime could not be established; no candidate outcome assigned. |
| `review_required` | Alternative construction; no executable pass/fail assigned. |

Only a formal pass exits 0 from `grade`/`finish-case`; all other grading results exit 2. Administrative commands exit 0 on success. Reports include answer-byte SHA-256, requests, protocol acknowledgments, replies, terminal codes, observations and failures. Temporary candidate files/databases are removed after evaluation. `score` stays null: there is no combined creativity/hiring score or automatic explanation grade.

## Executable protocol and oracle

Each of **three isolated repetitions** uses a new database and fresh service processes for every request. The same sequence is used in each repetition; keys are unique across scenarios. Both concurrent workers must acknowledge their request before either receives its release command. Initialization also occurs in overlapping fresh processes. Barrier release creates the opportunity for overlap; it does not force every internal SQLite interleaving or guarantee observation of both outcomes.

| Phase | Check |
| --- | --- |
| Two A requests for 60 | Either request can win: exactly one accepted at 40, one rejected at 40; one debit/ledger row and both decisions. |
| Replay each from another process | Exact stored decisions and unchanged tables. |
| Change amount, then account under an old key | Global identity, mismatch response and no changes, including to B. |
| Request B's entire 100 | Independent allowance, acceptance at zero. |
| Debit A by 10, then replay both original keys | Original accepted/rejected remaining values stay 40 after A becomes 30. |
| Two concurrent identical requests for 5, then replay | One decision/ledger row/debit; both replies show 25. |
| Reject B's next unit, change its account, then replay | Durable rejection, rejected-key conflict and zero preserved. |

The latter phases directly exercise F2/F3 beyond the F5 overlap example. They are disclosed here rather than treated as secret performance probes. There are 14 phases, 16 apply calls and 16 fresh workers per successful repetition.

The oracle admits both serial overlap orders and keeps only histories whose replies **and full public table projections** match. It never compares against authored-reference output. Exact state comparison detects missing/extra rows, wrong account balances, missing rejected decisions, duplicate debits and ledger/decision inconsistencies. After each phase all candidate workers are stopped before the independent inspector opens the SQLite database read-only. The tables must be real ordinary tables with the declared columns/types and primary keys; extra implementation tables/columns are allowed. Public database/sidecars must be regular files; each public table must contain fewer than 100 rows. Inspector execution and SQL work are bounded; views, virtual tables, symlinks, corrupt files and inspection errors cannot establish a pass.

The sandbox exposes writable `/state`, private `/tmp`, read-only runtime directories and candidate/worker files, private network/PID namespaces, standard `/dev` and private `/proc`, with a cleared environment. The candidate sees no evaluator/oracle/control files. Limits are 512 MiB address space, 256 FDs, 8 MiB file size, 10 CPU seconds **per process**, six wall seconds per protocol phase/reply and 64 KiB per reply. Startup and arm acknowledgments also have six-second deadlines. Normal candidate stdout is discarded; output that corrupts the worker protocol fails. Workers are deliberately killed after their reply, so negative terminal codes alone are not failures. Killing bubblewrap tears down the PID namespace and its descendants. These are bounded research constraints, not resistance to kernel exploits or an aggregate resource quota for arbitrary process trees.

These tests establish observable quiescent states and restart replay, not a proof of atomicity under every crash timing. No E2-style crash injection, forced database faults, production deadlock, throughput or latency experiment is claimed. Database/worker exceptions are protocol failures, never synthesized business rejections. Unknown-outcome handling and full atomicity reasoning are reviewed separately.

## First-answer seal and hot-account reveal

For a staged experiment, do not supply the full final task before the initial response:

```sh
python evaluate.py start-case case-0.json
# Give only case-0.json's view to the solver; save the first JSON response as first.json.
python evaluate.py reveal-case case-0.json first.json case-1.json
# Give only case-1.json's view; save the final response as final.json.
python evaluate.py finish-case case-1.json final.json result.json
```

The initial view contains F1–F5 and the disclosed constraints, withholding the fixed hot-account reveal. Reveal preserves the first parsed JSON response, even a semantically invalid one, before publishing the final view. Finish checks source/state/answer digests and attaches the first response to the result for review. Output files are created exclusively. This is local ordering and tamper detection against inconsistent files; an operator can recompute hashes, so it is not external authentication or proof of first-attempt custody. Plain `grade` does not establish a staged experiment.

## Explanation and alternative review

```sh
python evaluate.py review-template answer.json review.json
# An independent reviewer fills the form using REVIEW-RUBRIC.md.
python evaluate.py validate-review answer.json review.json
```

See [REVIEW-RUBRIC.md](REVIEW-RUBRIC.md). An alternative answer can submit `{"task_id":"E1","alternative_format":true,"alternative":"...","explanation":"..."}`. Review remains available when executable testing is unavailable or fails. Review validation checks exact answer binding, criterion coverage, declared reviewer/comparison information and quote existence. It does not authenticate identity or independence, validate judgments, or upgrade a formal result. Preserve two separate first reviews and disagreements before adjudication.

## Authored controls and validation

`controls.py` creates a reference service and seven deliberately defective implementations. These are evaluation development fixtures, not model-performance observations. **Do not send evaluator source, controls, tests or review results to a fresh solver.**

```sh
python controls.py reference reference.json
python evaluate.py grade reference.json
python controls.py current_remaining wrong.json
python evaluate.py grade wrong.json
```

The integration test grades all eight implementations inside the sandbox, expecting the reference to pass and every mutation to fail. Mutations cover initialization resetting allowance, lost rejection, current instead of historical replay, ignored payload mismatch, missing ledger, database failure represented as rejection, and overspending. On unsupported hosts the entire isolated integration class is explicitly skipped; pure oracle/driver tests and trusted inspector fixtures still run. A mocked model-driver pass is not submitted-code execution.

Current-host validation and its limits are recorded in [VALIDATION.md](VALIDATION.md).

`python verify_evaluation.py` reruns tests and six CLI smoke checks and refreshes the `validation/` evidence files. It uses workspace-local temporary files and retains the unavailable result when isolation is unsupported.
