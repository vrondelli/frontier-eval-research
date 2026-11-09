"""Independent replay of fresh AstraH6draw3's126-case false green."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
def inv(p):return {f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in p.rglob('*')if f.is_file()and not f.is_symlink()}
package=ROOT/'runs/confirmation/gpt-6-astra/H6/draw3/delivery';control=ROOT/'owner/cases/H6/saved_luna_decimal.json';before=inv(package)
script='''import json,sys,shutil,subprocess
from pathlib import Path
shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();code=json.load(open('/control.json'))['code'];candidate=Path('/tmp/candidate/summarize.py');candidate.write_text(code)
r=subprocess.run([sys.executable,'/tmp/eval/evaluation/run_eval.py',str(candidate),'--report','/tmp/report.json'],cwd='/tmp',capture_output=True,text=True,timeout=180)
report=json.load(open('/tmp/report.json'))if Path('/tmp/report.json').exists()else None
raw='{"adjustment_sheets":{"root / exact zero":{"stat":"event_count","turns":[0e10000000000000000000]},"root / mixed zero":{"stat":"event_count","turns":[0e10000000000000000000,0,1]}}}'
pair=[]
for name,text in [('exponent_zero',raw),('plain_zero',raw.replace('0e10000000000000000000','0'))]:
 inp=Path('/tmp/candidate/'+name+'.json');out=Path('/tmp/candidate/'+name+'-out.json');inp.write_text(text)
 q=subprocess.run([sys.executable,str(candidate),str(inp),str(out)],capture_output=True,text=True,timeout=5)
 pair.append({'case':name,'input':text,'exit_code':q.returncode,'stderr':q.stderr,'output':out.read_text()if out.exists()else None})
print(json.dumps({'grader_exit':r.returncode,'grader_stdout':r.stdout,'grader_stderr':r.stderr,'report':report,'candidate_pair':pair}))
'''
cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={control},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=240);observed=json.loads(r.stdout)if r.returncode==0 else{}
value={'model':'gpt-6-astra','case_id':'H6','draw':3,'kind':'independent_root_fresh_confirmation_replay','command':cmd,'exit_code':r.returncode,'stderr':r.stderr,'observed':observed,'package_unchanged':before==inv(package)}
path=ROOT/'replays/H6-CONFIRM-DRAW3-REPLAY.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
ok=r.returncode==0 and observed['report']['all_passed']and observed['report']['total']==126 and observed['candidate_pair'][0]['exit_code']!=0 and observed['candidate_pair'][1]['exit_code']==0 and value['package_unchanged']
print(json.dumps({'reproduced':ok,'package_unchanged':value['package_unchanged']}));raise SystemExit(0 if ok else 1)
