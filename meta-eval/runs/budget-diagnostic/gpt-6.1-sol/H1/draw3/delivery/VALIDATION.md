# Validation performed

Host: Windows 11, CPython 3.14.2. The supplied input hashes still match
`MANIFEST.json`; input task, README and provenance were not modified.

`python -m unittest test_evaluation -v` completed successfully:

- 14 test methods passed.
- The Windows symlink test was skipped.
- The complete Linux sandbox integration class was skipped before execution.
  This includes the authored service, seven broken-service controls and the
  isolation-surface probe. None has a live executable result on this host.

Unittest reports `Ran 15 tests`, `OK (skipped=2)` because the skipped class is an
additional skip entry rather than an executed method. The portable passing tests
cover both serial oracles, twelve deliberately corrupted traces, independent
SQLite inspection and schema rejection, review routing, unsupported isolation,
first-answer sealing and drift detection, concurrent worker reads and cleanup.
Worker coordination tests use controlled doubles; they do not validate bubblewrap.

CLI smoke checks returned exit 2 with the expected statuses:

- Authored executable answer: `unavailable`, without executing its code.
- Architectural alternative: `review_required`.
- Wrong task identifier: `invalid`.

Evidence is retained in [validation/summary.json](validation/summary.json),
[validation/unittest.txt](validation/unittest.txt), and the `cli-*.json` reports
in that directory. The positive control is authored, not a model observation.

Attempting to list WSL distributions returned `Wsl/E_ACCESSDENIED`. No unsafe host
execution or sandbox bypass was used. Full execution qualification remains to be
performed on Linux with working bubblewrap and unprivileged namespaces:

```sh
python3 -m unittest test_evaluation -v
```

Check that the integration class actually runs, that the reference passes all
three repetitions, and that each negative control fails for its behavioral
defect. Skipped integration is not a successful executable qualification. No
independent explanation review or model study was performed.
