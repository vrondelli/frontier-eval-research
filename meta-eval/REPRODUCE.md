# Reproduce the saved findings

To rerun the integrated eight-dimension meta-evaluation on the existing packages, follow [META-EVAL.md](META-EVAL.md). This page retains the smaller saved-finding exhibits; they are also useful for checking individual counterexamples.

These commands execute saved model-created graders and authored candidate controls. They make **zero model calls**. A successful exhibit command means the documented **grader defect was reproduced**, not that the model-created eval was correct.

Use Linux with CPython3.14, bubblewrap and Docker. Tested environment identities and image digests are in [ENVIRONMENT.json](grades/audit-review/ENVIRONMENT.json). The isolated numeric examples use `python:3.14-slim`; pin its recorded digest for an exact image replay. Original H4 bytecode also needs CPython3.14. Harness source-only controls support Python3.12, but this is not sufficient for every original native artifact.

After extracting the final archive into a clean directory:

```sh
python3 verify_release.py
python3 reproduce_h1.py
python3 reproduce_h6.py
python3 reproduce_h6_confirmation.py
```

| Command | Expected observation |
| --- | --- |
| `verify_release.py` | Archive files match the release manifest and the scoped owner controls reproduce. Excluded full-task controls are reported, not reinstated as gold. |
| `reproduce_h1.py` | Five valid native control verdicts, one false rejection of the correct `applied` Service, zero false accepts, delivered package unchanged. |
| `reproduce_h6.py` | The actual faulty CLI rejects legal exponent-zero input but accepts canonicalzero counts1/3; the new Astra grader nevertheless passes it84/84. |
| `reproduce_h6_confirmation.py` | A different fresh Astra-created grader passes that same bad CLI126/126; the preserved zero counterexample still fails. |

Fresh reproduction receipts are written under `replays/`; original model deliveries and archived audit receipts are not overwritten. The scripts isolate scored code with bubblewrap or Docker and disable its network. Missing backend/runtime support is an instrument error, not a model failure. Check [CURRENT-SCORING.md](CURRENT-SCORING.md) before adapting a new arbitrary grader.

For one clean extracted-archive verification, including the saved seed and fresh-confirmation exhibits:

```sh
python3 verify_release_findings.py PATH/TO/eval-author-meta-eval.zip --output replay-verification.json
```

To launch **new paid author attempts**, use [AUTHOR-RUNNER.md](AUTHOR-RUNNER.md). New inference is variable and is not expected to regenerate byte-identical packages. Exact original instruction text, reconstruction, clean staging and coaching must retain their separate condition labels. Human task/criterion review remains distinct from successful executable replay.
