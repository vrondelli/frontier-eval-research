# Validation performed

Authoring environment: Windows PowerShell, Python 3.14.2, 2026-11-08.

`python -m unittest -v test_evaluation` passed 27 test methods. The separate
`IsolatedIntegrationTests` class was skipped because this host does not provide the
declared Linux/bubblewrap runtime. It was not counted as an isolated execution pass.

The passing portable checks cover:

- Both legal serial outcomes; global same-key identity; accepted/rejected historical
  replay; mismatches with no state change; integer reply semantics; whole-state
  comparison; fabricated replies and tampered ledger/decision/account rows.
- All six authored-reference scenarios via a test-only synchronous worker adapter
  and real SQLite, including all three inspection checkpoints per scenario.
- Nine defective authored controls failing the core scenario via that same adapter:
  missing ledger, lost rejection, current-balance replay, ignored payload, overspend,
  reset on initialization, unconditional rejection, database-error-as-rejection,
  and process-local storage. These are control checks, not model performance.
- A real two-thread SQLite race using independent Service instances/connections.
  This does not substitute for the two-process sandbox run.
- Independent read-only inspection in a separate Python process; missing/corrupt
  database, views, missing primary key, row limit and symlink rejection.
- Invalid envelopes, ambiguous/non-finite JSON, alternative-format routing,
  execution errors distinct from business rejection, and unavailable-runtime behavior
  without executing submitted source.
- First-view withholding of F6; preserved initial answers including invalid ones;
  final answer binding; wrong-phase and transcript-tampering detection.

CLI smoke checks generated authored control JSON, created a first-stage state, sealed
an alternative first answer, produced a staged alternative review-required result,
and evaluated the authored reference on the native host. The reference correctly
returned `formal_status: unavailable` with no cases executed. `runtime-check.json`
and `staged-check.json` retain these outcomes. All author-written Python files were
compiled for syntax checking.

The first portable test attempt encountered inaccessible default temporary directories
under this managed Windows sandbox. Tests now create their disposable directories
inside this writable workspace; they passed after that correction. Linux evaluation
continues to use the system temporary directory or the operator's `TMPDIR`.

Remaining validation: on a supported disposable Linux host, run
`python controls.py --check` and retain its JSON. The expected results are one formal
reference pass, nine defective-control failures and one review-required alternative.
Also run the unittest suite there so the real sandbox integration class executes.
No Linux process/namespace isolation, forced crash/commit fault experiment, fresh model
study, latency benchmark or independent expert review is claimed by this authoring run.
