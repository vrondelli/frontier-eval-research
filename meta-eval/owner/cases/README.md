# Owner control bank

`build_controls.py` copies selected preserved code/data into portable JSON artifacts and records source hashes in `manifest.json`. `check_cases.py` executes authored controls to qualify expected labels. These are owner-only materials; do not expose them to the eval author.

Automated controls: H1 actual E1 Service/SQLite behavior; H4 original ferry tests against rule-reference and naive implementations; H5 actual query CLI, engine, optimizer, public pack, independent semantic oracle and whole-CLI pair-counter line trace; H6 actual numeric CLI including a saved original Luna implementation; H7 original field-evidence report/request and licensed extraction formats. The H5 positives use distinct saved Astra-derived and Sol implementations; H6 positives use separate integer-token and Fraction parsers; H4 positives use independent suite styles. Negative controls are authored audit mutants, not new model trials.

H2 and H3 have human review rubrics and are not automated pass/fail claims. Their manifest `qualified:false` means independent semantic adjudication is still required, not that the model failed. Full task-domain proof is not claimed: see per-case finite scope in the manifest. H1 control checks do not establish process-concurrency correctness. H5 trace is scoped to the reviewed pair-increment source structure and does not qualify nested oracle isolation; the runtime isolation gate is separate. H6 covers finite bounded-output cases, not every mathematically unbounded output. H7 is one original source document.

The optional runtime JSON adapter is an invocation convention introduced for this evaluation. It is not claimed as an original authoring instruction. An owner adapter can invoke a delivered grader's native interface without changing the subject prompt.

`QUALIFICATION-INITIAL-WINDOWS-CLEANUP-ERROR.json` preserves an owner instrumentation incident: correct E1 assertions passed, but a verifier SQLite connection remained open during Windows temp cleanup. The owner helper was corrected to close that connection; no original subject artifact was modified.
