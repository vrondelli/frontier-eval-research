"""Verify extracted archive bytes, public packets and authored owner controls offline."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import os

ROOT=Path(__file__).resolve().parent
if os.name=='nt'and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\UNC\\'+str(ROOT)[2:])if str(ROOT).startswith('\\\\')else Path('\\\\?\\'+str(ROOT))

def main():
    manifest=json.loads((ROOT/'RELEASE-MANIFEST.json').read_text())
    for item in manifest['files']:
        path=ROOT/item['path']
        assert path.is_relative_to(ROOT) and path.is_file(),item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['path']
    packets=0
    for path in (ROOT/'packets/primary').glob('*/MANIFEST.json'):
        for item in json.loads(path.read_text())['files']:
            assert hashlib.sha256((path.parent/item['path']).read_bytes()).hexdigest()==item['sha256']
        packets+=1
    owner=subprocess.run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL',
                          '--security-opt','no-new-privileges','--pids-limit','128','--memory','512m','--cpus','1',
                          '--tmpfs','/tmp:rw,nosuid,size=128m','--mount',f'type=bind,source={ROOT/"owner"},target=/owner,readonly',
                          '-w','/tmp','python:3.14-slim','python','-B','/owner/check_cases.py'],capture_output=True,text=True,timeout=120)
    assert owner.returncode==0,owner.stderr
    result=json.loads(owner.stdout)
    spec=importlib.util.spec_from_file_location('auditcheck',ROOT/'owner/audit_cases/check.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    audit=0
    for case in json.loads((ROOT/'owner/audit_cases/manifest.json').read_text())['cases']:
        for control in case['controls']:
            assert module.check(json.loads((ROOT/control['path']).read_text())) is control['expected_pass']
            audit+=1
    adjudication=json.loads((ROOT/'owner/ADJUDICATION.json').read_text())if(ROOT/'owner/ADJUDICATION.json').exists()else{}
    print(json.dumps({'archive_hashes_verified':len(manifest['files']),'public_packets_verified':packets,
                      'historical_finite_owner_checks_reproduce':result['all_implemented_controls_qualified'],
                      'excluded_full_task_owner_controls':len(adjudication.get('excluded_controls',[])),
                      'complete_task_gold_claim':False,
                      'audit_controls_verified':audit,'model_calls':0,
                      'scope':'offline authored controls; not a claim all generated model evals are correct'}))

if __name__=='__main__':main()
