"""Inspect native interface first; this wrapper invokes it without changing subject code."""
from pathlib import Path
import argparse,hashlib,json,subprocess,uuid
B=Path(__file__).resolve().parents[2];a=argparse.ArgumentParser();a.add_argument('--package',required=True);a.add_argument('--module',required=True);a.add_argument('--call',required=True);a.add_argument('--pass-key',required=True);a.add_argument('--label',required=True);a.add_argument('--output',required=True);n=a.parse_args();package=Path(n.package).resolve();fixture=B/'owner/cases/H6/saved_luna_decimal.json'
launch=json.loads((package.parent/'launch.json').read_text());assert launch['status']=='completed'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
code="""import importlib,json,os,shutil,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();script=Path('/tmp/candidate/summarize.py');script.write_text(c['code']);sys.path.insert(0,'/tmp/eval/evaluation');os.chdir('/tmp');e=importlib.import_module(sys.argv[1]);report=eval(sys.argv[2]);print(json.dumps({'actual_saved_bad_cli_accepted':report[sys.argv[3]],'report':report}))
"""
name='h6-successor-'+uuid.uuid4().hex;cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={fixture},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code,n.module,n.call,n.pass_key]
try:p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);result={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};result['observed']=json.loads(p.stdout)
except Exception as e:subprocess.run(['docker','rm','-f',name],capture_output=True);result={'error':repr(e)}
after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
result.update(kind='completed_successor_native_bad_candidate_test',case_id='H6',model=launch['model_requested'],condition=n.label,attempt_status=launch['status'],author_seconds=launch['seconds'],command=cmd,package_unchanged=before==after,fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),scope='Native full authored suite on actual preserved Luna CLI independently known to fail a tiny licensed zero/count request. Positive full-task qualification remains separate.')
Path(n.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['observed','stdout','stderr','command']}));print(json.dumps({'actual_saved_bad_cli_accepted':result.get('observed',{}).get('actual_saved_bad_cli_accepted')}))
