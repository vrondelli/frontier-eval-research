# Actual validation

Validated locally on Windows (`win32`), Python 3.14.2. This is evaluator-development
evidence, not a model run, independent expert review, or complete Linux sandbox
qualification.

- Unit suite: 24 discovered, **20 passed, 4 skipped**, no failures/errors.
- Portable checks exercised both possible overlap winners, illegal outcomes,
  global key identity, immutable historical replies, exact table comparison,
  database-error rollback orchestration, SQL schema/type/row limits, the trigger
  installer, alternative review admission, and staged first-answer integrity.
- CLI smoke checks: alternative -> `review_required`/exit 2; duplicate JSON keys
  -> `invalid`/exit 2; executable submission on this host -> `unavailable`/exit 2.
- All three staged CLI commands ran, retained the first response, and produced
  `review_required` for an authored alternative-format control. Exclusive output
  creation was checked by retrying an existing output path; it returned exit 2.
- The source task and public README hashes match `MANIFEST.json`.

The skipped checks are the Linux symlink-sidecar test and three live sandbox
integration tests. The integration tests contain the authored correct SQLite
service, seven defective variants, process failure/limit probes, and basic
isolation probes. **Those implementations have not been executed through this
sandbox in this environment.** The portable orchestration tests use a trusted
model double, and inspector tests use independently created SQLite fixtures.
Neither establishes Linux worker correctness or the effectiveness of bubblewrap.

Windows cannot run the required Linux isolation. `wsl --list --quiet` also failed
with `Wsl/E_ACCESSDENIED`; no unsafe candidate execution fallback was attempted.
On a supported Linux host, rerun:

```sh
python3 -m unittest discover -s tests -v
python3 evaluate.py answer.json --output new-evidence.json
```

Local test execution used a writable workspace scratch directory because this
managed Windows environment's default temporary location was inaccessible. The
initial test attempt also exposed SQLite test-fixture handles that needed
explicit closing on Windows; these were fixed and the full suite rerun. To
reproduce in this environment, use PowerShell:

```powershell
New-Item -ItemType Directory -Force .tmp | Out-Null
$env:TEMP = Join-Path (Get-Location) '.tmp'
$env:TMP = $env:TEMP
python -m unittest discover -s tests -v
```

Evidence: [machine-readable summary](validation/summary.json),
[unit log](validation/unittest.log), [unsupported-host result](validation/candidate-result.json),
[alternative result](validation/alternative-result.json),
[invalid JSON result](validation/invalid-result.json), and
[staged control result](validation/staged-result.json).
