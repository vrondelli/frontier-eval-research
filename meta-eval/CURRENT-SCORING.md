# Current scoring entry point

For the complete scored meta-eval pipeline, use [run_meta_eval.py](run_meta_eval.py) and [META-EVAL.md](META-EVAL.md). The commands below describe its preserved native control adapter and historical scoring interface, not the full eight-dimension orchestrator.

Use `python run_eval_current.py score ...` for new owner scoring. It reads `owner/ADJUDICATION.json` and excludes controls that were found invalid or insufficient for complete-task gold. The frozen `run_eval.py` remains available to reproduce original receipts; it must not supply new complete-task judgments without the adjudication sidecar.

All five initial H4 controls are excluded from complete-task scoring. Their original receipts establish only finite test discrimination. The alternate positive violates the explicit unittest requirement, and the inherited production reference is insufficiently qualified. Native H4 scoring requires a complete candidate, including the original protected public workspace, production implementation and valid test suite.

An owner may explicitly select a separately labeled post-outcome H4 bank with `--successor-controls owner/expansion-h4/MANIFEST.json`. This never replaces the frozen bank silently. The current materializer copies the original public protected workspace and adds only the successor's fares.py and test_fares.py. Nested native H8/H9 audit outputs require semantic review against the staged evidence; narrow JSON diagnostic counts do not constitute full-report gold.

If a grader documents scratch-root writes, `--writable-disposable-copy` makes only its temporary `/subject` copy writable inside Docker. The original delivery and owner bank are never writable mounts, and `/candidate` remains read-only. The receipt records this runtime choice. Without the flag the subject copy is read-only; a resulting scratch-path integration error requires adjudication rather than a false model-failure label.

The current entry point rejects package symlinks before copying and rejects materialized file traversal. The negative self-check receipt is `grades/audit-review/CURRENT-SCORER-SECURITY.json`. Missing adapters, missing eligible controls and unqualified owner checks produce unknown/unqualified output, not automatic model-failure labels.
