"""Explicit post-outcome controls with the unchanged frozen scoring runtime."""
from pathlib import Path
from argparse import Namespace
import importlib.util,json
B=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frozen_runtime',B/'run_eval.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
manifest=B/'owner/expansion-h6/MANIFEST.json';m=json.loads(manifest.read_text())
r.manifests=lambda:[(manifest,{'case_id':'H6','controls':m['cases']})]
args=Namespace(package=str(B/'runs/screen/gpt-6-astra/H6/delivery'),adapter=str(B/'grades/adapters/astra-H6.json'),docker_image='python:3.14-slim',allow_unisolated_diagnostic=False,case='H6',output=str(B/'grades/owner-review/astra-H6-ZERO-DIAGNOSTIC.json'),timeout=90)
raise SystemExit(r.score(args))
