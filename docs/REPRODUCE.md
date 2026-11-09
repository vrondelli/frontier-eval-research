# Reproduce the work

## Inspect without Docker

From the repository root, with Python 3.10 or newer:

```sh
python3 tools/show_results.py
python3 tools/validate_portfolio.py
```

These inspect saved data/hashes, execute no submitted model code, call no model and need no API key.

## Replay the executable meta-eval

Use Linux, Python 3.14, Docker with `python:3.14-slim`, bubblewrap and working unprivileged user namespaces. The H4 sourceless helper requires the declared runtime. Subject code has no host fallback.

```sh
cd meta-eval
python3 run_meta_eval.py doctor
python3 -m unittest discover -s meta_eval/tests -v
python3 run_meta_eval.py qualify --output qualification-replay
python3 run_meta_eval.py run --output scored-replay --jobs 3
python3 validate_meta_eval_report.py scored-replay/REPORT.json --all-existing
```

Allow roughly ten minutes on the tested workstation; host speed varies. Jobs are bounded and network-disabled. Installing prerequisites or obtaining a missing Docker image is separate environment setup.

Expected: 31 retained records, 19 completed packages exercised, 114 native jobs, explicit incomplete statuses and stable H1/H6 counterexamples. H1 budget draw3 has intermittent protocol rejection, so operational scores can vary. A completed investigation returns zero even if it reproduces subject defects: the defects are report data.

[Full guide](../meta-eval/META-EVAL.md) · [Check registry](../meta-eval/meta_eval/CHECK-REGISTRY.json).

## Verify the release

The immutable scored-v2 ZIP is 25,923,702 bytes, SHA256:

```text
fb4fca7b22311573f65337f83fb17ad63fa0cce4225505f2727ffc6506cf1c45
```

[Delivery receipt](../releases/SCORED-DELIVERY.json) · [Clean verification](../releases/SCORED-CLEAN-VERIFICATION.json).

Extracted `meta-eval/` files retain their ZIP bytes. Curated documentation lives outside them. Original receipt paths describe the historical layout, not paths guaranteed to exist on your machine.

## Earlier studies

A clone contains their pages, excerpts, protocol records and selected ledgers. The full archive is local at `research/hackathon/`, ignored by Git. It is not a public export of every historical session.

On the original machine:

```sh
python3 tools/build_catalogue.py
python3 tools/validate_portfolio.py
```

Catalogue generation reads preserved reports/metadata, makes no model calls and does not rewrite originals.
