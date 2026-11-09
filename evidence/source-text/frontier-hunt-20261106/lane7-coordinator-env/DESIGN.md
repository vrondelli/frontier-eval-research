> Archived source excerpt. Original location: `frontier-hunt-20261106/lane7-coordinator-env/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Lane7 DESIGN — coordinator-continuation ERR_DLOPEN diagnosis (frozen)

Lane: `frontier-hunt-20261106/lane7-coordinator-env`. Diagnosis only.
NO frontier model episode will be run in this lane.

## Question

In paused run `coordinator-continuation-20261105/runs/gpt6-sol-r1`, the C09
child's H02/H07/H08 product check failed 0/3 with `ERR_DLOPEN_FAILED`
(terminal call-0092; `work-c09/h02-h07-h08.tap`), while the scripted
reference (`REFERENCE-RESULT.json`: build 10.464s, H02/H07/H08 3/3 in
275.279s) passed. Identify the exact native module, the exact missing
library/ABI or other loader cause, and the environment difference between
the reference path and the native child.

## Frozen method (set before any replay test)

1. Read-only inspection of preserved artifacts: TAP files, terminal
   call-0092/0098/0106/0114 (+ 0095/0099/0100/0101/0115 found adjacent),
   `REFERENCE-RESULT.json`, `reference.py`, `validate_arm.trial`,
   `run_pair.Actor`, `CoordinatorActor` (`actor.py`), `actor.json`,
   `run_native.py`, and `c08-evidence-replay-20261103/NEXT-CODING-EXPERIMENT.md`
   gate 1.
2. Identify the failing module from the loader stack; extract it without
   mutating the preserved run; `file`/`ldd`/`readelf` it in WSL.
3. Causal A/B probe in Docker with the actor's own image/flags: load the
   module via its real loader (`loadAtomicPublicationNative`) once with
   `TMPDIR=/tmp` (native-child condition) and once with TMPDIR on the
   `/workspace` bind mount (reference condition). No other variable changes.
4. Bounded fix test: copy the preserved workspace INTO this lane
   (`replay-workspace/`, preserved run never mutated), re-run ONLY the
   H02/H07/H08 check from the copy in Docker with the fix applied, fresh
   `C09_WORK`, `--test-concurrency=1` (reference shape), 600s timeout.
   Record exit/TAP verbatim. A re-pass is NOT required for `diagnosed`;
   any second, distinct failure is reported as a separate finding.
5. Write `DIAGNOSIS.md`: root cause with evidence lines, exact env fix,
   re-pass result, ready-to-launch fresh-episode checklist from
   `run_native.py`.

## Verdict rule

`diagnosed` iff root cause is identified with direct evidence (artifact
lines + causal A/B). `blocked` only if artifacts are unreadable.
No retries are hidden: every replay attempt is saved under `evidence/`.
