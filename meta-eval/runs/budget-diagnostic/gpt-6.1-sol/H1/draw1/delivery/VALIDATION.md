# Validation evidence

Validated on the current Windows workspace with Python 3.14.2 and SQLite 3.50.4:

```sh
python verify_evaluation.py
```

The final run passed **20 unit/component tests**, with zero failures/errors. The isolated implementation integration class was explicitly skipped because this host lacks the required Linux/bubblewrap runtime. Six CLI smoke checks passed: reference grading reported `unavailable` (exit 2), alternative grading and staged finish reported `review_required` (exit 2), and start/reveal/review-template commands succeeded (exit 0). The reference has **not** received an observed executable pass on this host. None of the seven defective service implementations has received an observed isolated failure here; those checks are implemented for the supported Linux environment.

Evidence files:

- [validation/summary.json](validation/summary.json): runtime, counts, skipped integration and CLI outcomes.
- [validation/unittest.txt](validation/unittest.txt): complete final test output.
- [validation/reference-result.json](validation/reference-result.json): actual reference grading result, including task/answer digests and the unavailability reason.

The pure oracle tests accept either overlap winner and reject double acceptance and inconsistent tables. Driver fixtures exercise three repetitions, historical replay, global mismatch, duplicate keys, failure propagation and error/result distinctions. These fixtures do not execute submitted Python. Other tests inspect real trusted SQLite fixtures independently, reject views/missing primary keys/excess rows/invalid sidecars, check strict JSON/type matching, verify sandbox command configuration and fail-closed preflight, validate review binding/quotes, and check staged response preservation, source/view tampering and final-answer binding.

The first local test attempt failed because the managed Windows process's default temporary directory did not allow file writes. The final validation explicitly selects a temporary directory inside this workspace; no isolation fallback was introduced. Earlier failed test output is not presented as a passing result.

To complete isolated qualification, run the same verification command on Linux with bubblewrap, unprivileged namespaces and `/usr/bin/python3`. That runs the reference and all seven negative implementation controls through the actual candidate sandbox and refreshes the machine-readable evidence. An unsupported runtime remains unavailable, never a fabricated pass.

The task/input files and supplied MANIFEST/PROVENANCE have not been modified. The original private grader/reference/probes and saved candidate labels were not accessed. This is a new bounded research evaluator, not a validated human hiring/creativity instrument. Independent expert explanation review, latency/load measurement and full crash/interleaving coverage remain unclaimed.
