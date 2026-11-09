"""Fixed-case native diagnostics of terminal timeout snapshots; no completed-failure claim."""
from pathlib import Path
import hashlib,json,subprocess,uuid
B=Path(__file__).resolve().parents[2]
for model,module,call in [('gpt-6.1-sol','evaluate',"e.evaluate(Path('/tmp/candidate'),generated=0,budget=80)"),('gpt-6-astra','run',"e.run_suite(Path('/tmp/candidate'),generated=0)")]:
 package=B/'runs/screen'/model/'H5/delivery';before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()};rows=[]
 code="""import importlib,json,shutil,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');shutil.copytree('/subject/input/workspace','/tmp/candidate')
for name,text in c['files'].items():Path('/tmp/candidate',name).write_text(text)
sys.path.insert(0,'/tmp/eval/evaluation');e=importlib.import_module(sys.argv[1]);original_cases=e.build_cases;e.build_cases=lambda *a,**kw:[c for c in original_cases(*a,**kw) if c.benchmark];report=eval(sys.argv[2]);print(json.dumps({'pass':report['passed'],'report':report}))
"""
 for control in ['correct_selected_plan','coherent_extra_work']:
  name='owner-h5-'+uuid.uuid4().hex;fixture=B/'owner/cases/H5'/(control+'.json')
  cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={fixture},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code,module,call]
  try:p=subprocess.run(cmd,capture_output=True,text=True,timeout=110);r={'control':control,'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};r['observed']=json.loads(p.stdout);r['valid']=p.returncode==0
  except Exception as e:subprocess.run(['docker','rm','-f',name],capture_output=True);r={'control':control,'valid':False,'error':repr(e)}
  rows.append(r)
 after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
 result={'kind':'timeout_snapshot_fixed_case_diagnostic','model':model,'case_id':'H5','attempt_status':'timeout','generated_cases':0,'package_unchanged':before==after,'rows':rows,'scope':'Native benchmark cases only with original checker logic and generated component disabled, not full default suite or completed author attempt.'}
 (B/'grades/owner-review'/(model+'-H5-BENCHMARK-SNAPSHOT.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'model':model,'verdicts':[(r['control'],r.get('observed',{}).get('pass'),r.get('error'))for r in rows]}),flush=True)

