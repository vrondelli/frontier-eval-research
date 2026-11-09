# Validation record

This package was authored on Windows from only `input/E1.md`, `input/README.md` and the supplied provenance/manifest. The original evaluator, original reference, private probes and saved candidate answers were not available. All reference and fault controls in `tests/` were authored here. No model-performance measurement or independent expert review was conducted.

The final retained run uses Python 3.14.2 on Windows 11. Run details, timestamps and Python source hashes are in [validation/summary.json](validation/summary.json); the test log is [validation/unittest.txt](validation/unittest.txt).

| Check | Observed result |
| --- | --- |
| Portable unit/component tests | 23 tests passed, zero errors/failures |
| Both serial winners | Accepted by the oracle; trusted SQLite control checked in both sequential orders |
| Authored fault controls | Eight deliberate implementation faults rejected at their expected phase in sequential SQLite component checks |
| Independent inspection | Real SQLite reads; view/missing-column/missing-primary-key/row-bound controls rejected |
| CLI smoke checks | Eight passed: unavailable execution, alternative review routing, staged sequence, review-template validation and exclusive-write protection |
| Linux process integration class | Skipped explicitly: Linux/bubblewrap isolation unavailable on this host |
| Actual isolated reference evaluation | `unavailable`, not pass; see [reference-result.json](validation/reference-result.json) |
| Alternative-format control | `review_required`; see [alternative-result.json](validation/alternative-result.json) |

The first local test attempt hit a Windows sandbox temporary-directory restriction when opening SQLite files. Test fixtures were moved to disposable directories under the writable workspace, and SQLite test connections were explicitly closed. The final retained test run passed. WSL enumeration returned `Wsl/E_ACCESSDENIED`; no permission workaround or unsafe execution fallback was used.

Portable sequential control checks validate the oracle/inspector and authored mutations. They do **not** establish process overlap, simultaneous initialization, real sandbox confinement, resource-limit enforcement or live Linux compatibility. Those checks are implemented in `tests/test_integration.py` and remain unverified here. On a suitable Linux host run:

```sh
python -m unittest discover -s tests -v
python -m tests.record_validation
```

`tests.record_validation` refreshes the local validation artifacts. An execution claim requires the integration class to run without a skip and the isolated reference report to say `pass`. Preserve earlier reports separately if collecting repeated experiments. A finite pass still does not prove all interleavings or production durability; explanation review remains separate.
