"""Execute the immutable Sol H1 oracle witness in the outer Docker boundary."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parents[2]
package=B/'runs/screen/gpt-6.1-sol/H1/delivery'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
probe='''import json
from evaluation.oracle import exact,overlap_options,request
from evaluation.grader import grade
a={'task_id':'E1','code':'class Service: pass','explanation':'Owner control explanation. Functional checks and prose review are distinct.'}
options=overlap_options(request('race-left'),request('race-right'))
applied=[{'status':'applied','remaining':40},{'status':'rejected','remaining':40}]
accepted=[{'status':'accepted','remaining':40},{'status':'rejected','remaining':40}]
print(json.dumps({'oracle_accepts_applied':any(exact(applied,v)for _,v in options),'oracle_accepts_accepted':any(exact(accepted,v)for _,v in options),'expected_reply_options':[v for _,v in options],'full_grader_runtime_probe':grade(a)}))
'''
command=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--mount',f'type=bind,source={package},target=/subject,readonly','-w','/subject','python:3.14-slim','python','-B','-c',probe]
p=subprocess.run(command,capture_output=True,text=True,timeout=30)
after={str(x.relative_to(package)):hashlib.sha256(x.read_bytes()).hexdigest()for x in package.rglob('*')if x.is_file()}
out={'kind':'immutable_oracle_diagnostic','model':'gpt-6.1-sol','case_id':'H1','command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'package_unchanged':before==after,'scope':'Executes delivered pure oracle and runtime availability probe, not a full candidate grade. Applied/accepted comparison is original-contract fidelity evidence.'}
if p.returncode==0:out['observed']=json.loads(p.stdout)
(B/'grades/owner-review/sol-H1-ORACLE-WITNESS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'exit':p.returncode,'package_unchanged':out['package_unchanged'],'observed':out.get('observed')}))
