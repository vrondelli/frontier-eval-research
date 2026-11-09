"""Read-only diagnostic of the terminal timeout snapshot, never a completed-attempt label."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/screen/gpt-6-astra/H1/delivery'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
probe='''import json
from evaluation.oracle import Oracle,request,ContractFailure
from evaluation.staging import start,source_text
results={}
for literal in ['applied','accepted']:
 try:Oracle().observe([request('x','A',60)],[{'status':literal,'remaining':40}]);results[literal]={'accepted':True}
 except ContractFailure as e:results[literal]={'accepted':False,'error':str(e)}
print(json.dumps({'observed':results,'staged_initial_view':start()['view'],'staged_final_view':source_text()}))
'''
command=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--mount',f'type=bind,source={package},target=/subject,readonly','-w','/subject','python:3.14-slim','python','-B','-c',probe]
p=subprocess.run(command,capture_output=True,text=True,timeout=30)
after={str(x.relative_to(package)):hashlib.sha256(x.read_bytes()).hexdigest()for x in package.rglob('*')if x.is_file()}
out={'kind':'timeout_snapshot_oracle_diagnostic','model':'gpt-6-astra','case_id':'H1','attempt_status':'timeout','command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'package_unchanged':before==after,'scope':'Pure immutable saved oracle, not full grading or a completed-turn failure.'}
if p.returncode==0:out['observed']=json.loads(p.stdout)
(B/'grades/owner-review/astra-H1-ORACLE-WITNESS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'exit':p.returncode,'observed':out.get('observed',{}).get('observed')}))
