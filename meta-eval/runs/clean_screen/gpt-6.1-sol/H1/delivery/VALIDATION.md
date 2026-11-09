# Validation performed

Host: Windows, Python 3.14.2. The requested task source is unchanged.

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 20 portable tests passed; the Linux integration test class was explicitly skipped. See [unit-tests.txt](validation/unit-tests.txt). |
| `python -m compileall -q evaluator.py staged.py e1eval tests tools` | Passed, including syntax of the isolated adapter and authored fixtures. |
| Authored-control generation and real `grade` CLI | Produced [reference-control.json](validation/reference-control.json) and [reference-report.json](validation/reference-report.json). Result: `unavailable`, `executable_ran: false`, actual Python process exit code 2. |
| Actual `review-template` CLI | Created [review-template.json](validation/review-template.json). This is an uncompleted form, not an independent review. |
| Actual staged start/reveal/finish CLI | Preserved the first authored answer and source/lineage bindings in [staged-report.json](validation/staged-report.json). Final execution result remained `unavailable`. This smoke check reused an authored control; it is not an adaptation experiment. |
| Negative CLI checks | An uncompleted review was rejected and an existing staged file was preserved. See [cli-smoke.json](validation/cli-smoke.json). |
| WSL runtime discovery | `wsl --list --quiet` returned `Wsl/E_ACCESSDENIED`. No Linux execution or isolation fallback was attempted. |

The portable tests include actual read-only inspection in a separate Python process
against an authored SQLite fixture. Tests of model observations and mocked runner
admission are distinct from executing a submitted service. Both legal serial winners
pass the oracle; fifteen independently corrupted observations fail it. Review and
lineage tests reject wrong hashes, nonexistent quotes, missing criteria and changed
preserved answers.

**Not verified on this host:** successful bubblewrap startup, actual concurrent
candidate execution, authored positive/negative service outcomes, resource enforcement,
network/filesystem isolation and Linux process cleanup. The three integration test
methods covering those surfaces are present in [tests/test_evaluation.py](tests/test_evaluation.py)
and require a supported Linux runner. No executable reference pass is claimed here.

No fresh model run, independent expert review, latency measurement, creativity score
or hiring validation was performed. Coverage limits of the finite executable task
are documented separately in [README.md](README.md).
