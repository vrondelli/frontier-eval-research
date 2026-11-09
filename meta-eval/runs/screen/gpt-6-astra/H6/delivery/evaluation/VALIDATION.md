# Validation record

Validated locally on 2026-11-08 using Python 3.14.2 on Windows.

Command:

```text
python -m unittest discover -s evaluation/tests -v
```

Result: 7 tests passed. The integration test runs `evaluate.py` as an actual
subprocess against a temporary copy of `tests/control_cli.py`, reads its JSON
report, and requires all 84 probes to pass (19 valid and 65 invalid inputs).

The six negative controls were all rejected on their targeted probes:

| Control defect | Failed probes |
| --- | --- |
| Binary floating-point parsing | binary64-integer-boundary, beyond-finite-float |
| Duplicate members accepted | duplicate-root, escaped-duplicate-row |
| Event-count values not validated | event_count-true, event_count-near-integral |
| Repeated events collapsed | identities-repetitions-and-sign |
| Maximum initialized to zero | illustrative-example |
| Empty result written on failure | empty-maximum, net_units-true |

Direct grader checks cover integral decimal/exponent output, extra diagnostic
metadata, exact large-number comparison, incorrect types/keys/status, absent output,
failure envelopes, malformed output, and parsing failures. Subprocess checks also
exercise paths with spaces, timeouts, and missing output.

The initial self-test attempt encountered permission errors in the sandbox's
system temporary directory. The runner and self-tests now create temporary
directories in the writable current directory, with an optional runner override.
The complete suite was rerun successfully after this correction.

No submitted `summarize.py` was included in the packet, so these results validate
the evaluation and its controls only. Solver process requirements remain unreviewed.
