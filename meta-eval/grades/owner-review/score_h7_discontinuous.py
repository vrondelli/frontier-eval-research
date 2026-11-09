from pathlib import Path
from argparse import Namespace
import importlib.util,json
B=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('frozen_runtime',B/'run_eval.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
manifest=B/'owner/expansion-h7/MANIFEST.json';m=json.loads(manifest.read_text());r.manifests=lambda:[(manifest,{'case_id':'H7','controls':m['controls']})]
for model,adapter in [('gpt-6.1-sol','sol-H7.json'),('gpt-6-astra','astra-H7.json')]:
 args=Namespace(package=str(B/'runs/screen'/model/'H7/delivery'),adapter=str(B/'grades/adapters'/adapter),docker_image='python:3.14-slim',allow_unisolated_diagnostic=False,case='H7',output=str(B/'grades/owner-review'/(model+'-H7-CONTIGUITY.json')),timeout=30)
 status=r.score(args);print(json.dumps({'model':model,'runtime_exit':status,'condition':'posthoc_component_probe'}),flush=True)
