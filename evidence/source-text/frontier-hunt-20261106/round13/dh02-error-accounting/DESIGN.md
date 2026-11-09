> Archived source excerpt. Original location: `frontier-hunt-20261106/round13/dh02-error-accounting/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DH02: native failure accounting

Source: FINDINGS DH02 and engineering/CASES ENG03. Historical baseline was not falsely all green. This is fresh fault injection.

Two surfaces: balance invariant and required-field validation. Four main tasks and four normal-semantic specificity tasks. Subject writes a real subprocess accounting runner, with a supplied functioning checker and CLI contract. Hidden grader invokes the implementation against real successful processes, exit-3 semantic rejections, missing executables, timeouts, signals, syntax errors, malformed protocols, diagnostics only on stderr, wrong obligations/diagnostics and wrong status codes. Both good and broken baselines are checked. No generic output word earns semantic credit. Contract diagnostic comparison is a stable machine protocol, not prose/keyword grading.

Primary endpoint requires a successful positive baseline, correct normal semantic credit and actual kill credit for an injected nonsemantic failure. A nonworking runner is not a targeted hit. Baseline qualification and ordinary case accuracy are independently reported. Controls retain expected nonzero semantic exits and successful accepted cases; they prevent treating every nonzero status as infrastructure. References use subprocess.run and check_output, respectively. Naive conflates all failures; adversarial accepts generic failed text and catches genuine error-shaped failures. Spawn/timeout/syntax errors in tested children are deliberate inputs, while failures launching the grader/subject remain excluded. No subject calls or freeze.
