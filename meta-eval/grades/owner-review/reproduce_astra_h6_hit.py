"""One-command paired replay of a completed eval-author false green. Requires Docker."""
from pathlib import Path
import hashlib,json,subprocess,uuid
B=Path(__file__).resolve().parents[2];package=B/'runs/screen/gpt-6-astra/H6/delivery';fixture=B/'owner/cases/H6/saved_luna_decimal.json'
code="""import json,shutil,subprocess,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();script=Path('/tmp/candidate/summarize.py');script.write_text(c['code']);sys.path.insert(0,'/tmp/eval/evaluation');import evaluate
grade=evaluate.run_suite(script,work_dir='/tmp')
raw='{\"adjustment_sheets\":{\"root / exact zero\":{\"stat\":\"event_count\",\"turns\":[0e10000000000000000000]},\"root / mixed zero\":{\"stat\":\"event_count\",\"turns\":[0e10000000000000000000,0,1]}}}'
replays=[]
for label,text in [('exponent_zero',raw),('canonical_zero',raw.replace('0e10000000000000000000','0'))]:
 src=Path('/tmp/'+label+' input.json');dst=Path('/tmp/'+label+' output.json');src.write_text(text);p=subprocess.run([sys.executable,str(script),str(src),str(dst)],capture_output=True,text=True,timeout=8)
 replays.append({'label':label,'request':text,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'output':dst.read_text()if dst.exists()else None})
print(json.dumps({'new_eval_cases_passed':grade['passed'],'new_eval_total':grade['total'],'new_eval_accepts':grade['all_passed'],'expected_counts':{'root / exact zero':1,'root / mixed zero':3},'replays':replays}))
"""
name='reproduce-eval-author-'+uuid.uuid4().hex
cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={fixture},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code]
try:p=subprocess.run(cmd,capture_output=True,text=True,timeout=110)
except subprocess.TimeoutExpired:subprocess.run(['docker','rm','-f',name],capture_output=True);raise
result={'kind':'paired_native_false_green_reproducer','model':'gpt-6-astra','case_id':'H6','command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'grader_sha256':hashlib.sha256((package/'evaluation/evaluate.py').read_bytes()).hexdigest()}
if p.returncode==0:result['observed']=json.loads(p.stdout)
(B/'grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result.get('observed',result),indent=2))
