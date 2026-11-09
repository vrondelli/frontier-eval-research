# H4 fresh eval-author review

Both model attempts completed: Sol362seconds; Astra323seconds. Each delivers a native grader with an independent exact-arithmetic oracle, large behavioral suite and independent/manual test-source review. Both explicitly describe their process runner as intended for trusted submissions, and do not claim hostile-code isolation.

The initial owner bank had a defect: `correct_independent_alternate` was a standalone assertion script, while the original task explicitly required tests that run with unittest. Its original expected full-task positive label is invalid. The inherited original `reference_fares.py` also uses regex `.match` and can accept a final newline forbidden by Rule K, so it cannot be universal full-task positive gold. The original frozen bank is retained, with exclusions in `owner/ADJUDICATION.json`.

A transparent post-outcome successor provides exact-rational production code, full-match validation and two independent unittest styles. The three targeted test-suite negatives are retained. The owner qualification verifies both proper suites pass the rule implementation and reject naive behavior; then both *immutable newly authored graders* run natively in Docker Python3.14 with original protected files preserved. The graders' documented writable scratch-root requirements are satisfied on disposable exact copies.

Result: **Sol5/5 and Astra5/5** successor control verdicts correct, zero false accepts/rejects. These are post-outcome diagnostics, not blind original-bank results or proof of full domain correctness. No model failure is established on these owner checks. Source hashes for the immutable packages remain unchanged.

Evidence: `owner/expansion-h4/QUALIFICATION.json`, `gpt-6.1-sol-H4-SUCCESSOR.json`, `gpt-6-astra-H4-SUCCESSOR.json`. The corrected owner controls demonstrate why raw rejection of the initial faulty positive must not be described as a model error.
