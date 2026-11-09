"""Post-outcome corrected owner controls; native immutable H4 graders in Docker."""
from pathlib import Path
import hashlib,json,subprocess,uuid
B=Path(__file__).resolve().parents[2];bank=B/'owner/expansion-h4';manifest=json.loads((bank/'MANIFEST.json').read_text())
for model,flag in [('gpt-6.1-sol','--output'),('gpt-6-astra','--report')]:
 package=B/'runs/screen'/model/'H4/delivery';before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()};rows=[]
 code="""import json,shutil,subprocess,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');shutil.copytree('/subject/input/workspace','/tmp/candidate');Path('/tmp/candidate/fares.py').write_text(c['assets']['reference_fares.py']);Path('/tmp/candidate/test_fares.py').write_text(c['test_code'])
p=subprocess.run([sys.executable,'/tmp/eval/evaluation/grade.py','/tmp/candidate',sys.argv[1],'/tmp/result.json'],capture_output=True,text=True,timeout=45)
report=json.load(open('/tmp/result.json'));print(json.dumps({'pass':report['automated_pass'],'report':report,'native_exit':p.returncode,'native_stdout':p.stdout,'native_stderr':p.stderr}))
"""
 for control in manifest['cases']:
  name='h4-owner-'+uuid.uuid4().hex
  cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={bank/control["path"]},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code,flag]
  try:p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);row={'control':control['path'],'expected_pass':control['expected_pass'],'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};v=json.loads(p.stdout);row['observed']=v;row['valid']=p.returncode==0 and type(v.get('pass'))is bool;row['correct']=row['valid']and v['pass']==control['expected_pass']
  except Exception as e:
   subprocess.run(['docker','rm','-f',name],capture_output=True);row={'control':control['path'],'expected_pass':control['expected_pass'],'valid':False,'correct':False,'error':repr(e)}
  rows.append(row)
 after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
 result={'kind':'post_outcome_corrected_owner_controls','model':model,'case_id':'H4','attempt_status':'completed','source_packages_unchanged':before==after,'rows':rows,'valid':sum(r['valid']for r in rows),'correct':sum(r['correct']for r in rows),'false_rejects':sum(r['valid']and r['expected_pass']and not r['observed']['pass']for r in rows),'false_accepts':sum(r['valid']and not r['expected_pass']and r['observed']['pass']for r in rows),'scope':'Native authored grader under Docker; owner controls corrected after outcome inspection; do not pool as blind initial bank.'}
 (B/'grades/owner-review'/(model+'-H4-SUCCESSOR.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['rows']}),flush=True)
