# Verification record

Verified on Windows with Python 3.14.2. `clean-verification.json` records a complete
replay from a new directory containing only the package and its public documents.
`verification.json` is the verification report retained from that clean replay.

Observed results:

- 18 harness unit tests passed.
- All three positive controls passed all three isolated trials (57 checks per control).
- All 15 negative controls failed as expected, with no unexpected passes.
- The reference export CLI exited 0.
- The submission-grading CLI returned `unavailable` and exited 2.
- The resulting formal report validated and its validation CLI exited 0.
- The clean replay exited 0; all evaluator source hashes match the delivered sources.
- The final clean verification took about 70 seconds on this host. This is harness
  runtime, not candidate latency evidence.

The first verification attempts exposed a restricted system temporary-directory path
and SQLite connection cleanup errors. The delivered runner uses disposable directories
under its writable current directory, and explicit connection closure. The final clean
replay did not reproduce either error. Four directories from those failed development
attempts remain in the workspace because automatic approval review rejected recursive
cleanup with reason `blocked by policy`. They are not part of the package or its runtime.

Production Linux isolation has **not** been executed on this host. WSL queries returned
`Wsl/E_ACCESSDENIED`; native Windows is unsupported by the production sandbox. The
production grader correctly refused execution. The local authored-control processes
verify service behavior, concurrency protocol, SQL observation, error handling, report
validation and cleanup, but provide no OS isolation/resource-limit evidence.

Before using this package for untrusted submissions on a Linux host, run:

```sh
python3 -m e1eval verify --sandbox --output sandbox-verification.json
```

That command requires actual bubblewrap execution of the reference and every control;
unavailability is a verification failure in that mode. This outstanding platform
qualification is explicit rather than replaced with an unsafe fallback.

No fresh model outputs or independent human explanation reviews were collected.
