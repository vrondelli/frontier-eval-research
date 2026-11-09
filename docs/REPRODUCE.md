# Try the results yourself

You can approach the repository in two ways. The first reads the saved scores and checks that the portfolio files are complete. The second actually runs the model-created evaluators against the saved controls.

Neither route asks a model to generate new work or needs an API key.

## First, inspect what is already here

From the repository root, using Python 3.10 or newer:

```sh
python3 tools/show_results.py
python3 tools/validate_portfolio.py
```

The first command prints the final evaluator scores. The second checks the catalogues, documentation links, source hashes and portable release. It can work in a clone without the full historical archive.

If the score ranges are unfamiliar, read [how the meta-eval works](HOW-THE-META-EVAL-WORKS.md). A range keeps unresolved points visible; it is not a confidence interval.

## Then rerun the evaluator checks

This route executes saved model-created code in the declared sandbox. Use Linux, Python 3.14, Docker with `python:3.14-slim`, bubblewrap and working unprivileged user namespaces. One original task includes a sourceless Python helper tied to this runtime, so substituting an arbitrary Python version can change whether the package runs.

Start inside the extracted release:

```sh
cd meta-eval
python3 run_meta_eval.py doctor
```

The doctor checks the runtime prerequisites. Resolve missing Docker, image or sandbox support before interpreting an execution failure as a model error. The runner does not fall back to executing submissions directly on your host.

Next check the scoring logic and calibration examples:

```sh
python3 -m unittest discover -s meta_eval/tests -v
python3 run_meta_eval.py qualify --output qualification-replay
```

The qualification command tests small known-good and deliberately broken evaluators. It asks whether the checker detects the defects it was designed to notice.

Finally, run the saved-package investigation and validate its receipts:

```sh
python3 run_meta_eval.py run --output scored-replay --jobs 3
python3 validate_meta_eval_report.py scored-replay/REPORT.json --all-existing
```

The full replay took roughly ten minutes on the tested workstation; your host may differ. It retains 31 original records and runs 114 check jobs against the 19 completed evaluator packages. Open `scored-replay/REPORT.md` to read the result.

A successful harness exit means the investigation completed, even when it found a defective evaluator. The counterexamples are in the report. One saved H1 grader has a documented intermittent protocol rejection, so exact operational scores may vary; the stable semantic failures are reported separately.

## Check the release identity

The immutable ZIP is 25,923,702 bytes, with this SHA256:

```text
fb4fca7b22311573f65337f83fb17ad63fa0cce4225505f2727ffc6506cf1c45
```

The [delivery record](../releases/SCORED-DELIVERY.json) identifies it. The [clean-extraction verification](../releases/SCORED-CLEAN-VERIFICATION.json) records the earlier full replay. `meta-eval/` retains the ZIP's file bytes; the newer explanations live outside that frozen bundle.

For adapter details and advanced options, use [the original runner guide](../meta-eval/META-EVAL.md).

## What about the earlier experiments?

Their campaign pages, source excerpts and selected ledgers are public. The complete older workspaces and ambient sessions remain in the local archive at `research/hackathon/`, which is ignored by Git. A clone should not pretend those files are present.

On the original machine, the catalogue can be rebuilt with:

```sh
python3 tools/build_catalogue.py
python3 tools/validate_portfolio.py
```

This reads the archive and updates its derived guides. The human campaign introductions are maintained in `tools/campaign_context.py`, so rebuilding does not replace them with raw audit labels.
