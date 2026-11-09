# Validation record

Executed on 2026-11-08 with Python 3.14.2 on Windows:

```text
python -m unittest discover -s evaluation -p 'test_*.py' -v
Ran 7 tests in 27.949s
OK
```

The full subprocess evaluation accepted the temporary conforming fixture on all
96 cases (28 valid inputs and 68 invalid inputs). It generated and checked a JSON
report and the evaluator's successful exit status. A separate full run against
an always-failing fixture verified failure status and report generation.

All 10 deliberately defective variants were rejected on their targeted CLI
cases. Additional checks accepted exact exponent output and unrelated metadata,
rejected wrong output types and inexact numbers, checked failure output rules,
and verified deterministic, size-bounded case generation.

The initial run encountered a Windows temporary-directory permission error.
Temporary directories now live under the writable invocation directory; the
complete command above passed after that change.

No submitted `summarize.py` was supplied. These results validate the evaluation
infrastructure and test fixtures; they do not grade an actual task submission.
