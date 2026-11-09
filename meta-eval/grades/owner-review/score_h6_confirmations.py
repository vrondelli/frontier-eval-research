"""Native confirmation grading of the actual saved numeric failure, no subject repairs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,uuid
B=Path(__file__).resolve().parents[2];a=argparse.ArgumentParser();a.add_argument('--draws',nargs='+',default=['draw2','draw3']);args=a.parse_args()
for draw in args.draws:
 package=B/'runs/confirmation/gpt-6-astra/H6'/draw/'delivery';launch=json.loads((package.parent/'launch.json').read_text());before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
 # Each interface was inspected independently on immutable output.
 if draw=='draw2':module='evaluate';call="e.run_suite([sys.executable,str(script)],script.parent)"
 elif draw=='draw3':module='run_eval';call="e.evaluate(script)"
 else:raise ValueError('Inspect new native interface before adding draw')
 code="""import importlib,json,os,shutil,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();script=Path('/tmp/candidate/summarize.py');script.write_text(c['code']);sys.path.insert(0,'/tmp/eval/evaluation');os.chdir('/tmp');e=importlib.import_module(sys.argv[1]);r=eval(sys.argv[2]);print(json.dumps({'pass':r['all_passed'],'report':r}))
"""
 name='h6-confirm-owner-'+uuid.uuid4().hex;fixture=B/'owner/cases/H6/saved_luna_decimal.json'
 cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={fixture},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code,module,call]
 try:p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);result={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};result['observed']=json.loads(p.stdout)
 except Exception as e:subprocess.run(['docker','rm','-f',name],capture_output=True);result={'error':repr(e)}
 after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
 result.update(kind='actual_saved_failure_native_confirmation',model='gpt-6-astra',case_id='H6',draw=draw,attempt_status=launch['status'],command=cmd,package_unchanged=before==after,expected_candidate_pass=False,scope='Full native authored suite against actual saved Luna CLI known to fail legal191bytezero witness. A rejection does not establish that every zero representation was tested.')
 (B/'grades/owner-review'/('H6-CONFIRM-'+draw+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'draw':draw,'attempt_status':launch['status'],'actual_saved_failure_accepted':result.get('observed',{}).get('pass'),'error':result.get('error')}),flush=True)
