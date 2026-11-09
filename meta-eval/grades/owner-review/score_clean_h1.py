"""Clean-staging completed H1 eval, original native byte-answer interface."""
from pathlib import Path
import hashlib,json,os,signal,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/clean_screen/gpt-6.1-sol/H1/delivery';launch=json.loads((package.parent/'launch.json').read_text());assert launch['status']=='completed'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
controls=next(c['controls']for c in json.loads((B/'owner/cases/manifest.json').read_text())['cases']if c['case_id']=='H1')
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
p=subprocess.run(base+['/usr/bin/python3','-c','print(123)'],capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr
code="import json,sys;sys.path.insert(0,'/subject');import evaluator;c=json.load(open('/control.json'));a=dict(task_id='E1',code=c['code'],explanation='Owner executable control; prose quality is separately reviewed.');print(json.dumps(evaluator.grade(json.dumps(a).encode())))"
rows=[]
for control in controls:
 cmd=base+['--ro-bind',str(package),'/subject','--ro-bind',str(B/control['path']),'/control.json','--chdir','/tmp','/usr/bin/python3','-B','-c',code]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 try:out,err=p.communicate(timeout=120);state='completed'
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();state='timeout'
 row={'control':control['id'],'expected_pass':control['expected_pass'],'command':cmd,'status':state,'exit_code':p.returncode,'stdout':out,'stderr':err,'actual_pass':None}
 try:r=json.loads(out);row['report']=r;s=r.get('formal_status');row['actual_pass']=s=='pass'if s in ['pass','fail']else None
 except Exception as e:row['parse_error']=repr(e)
 row['valid']=p.returncode==0 and state=='completed'and row['actual_pass']is not None;rows.append(row)
after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
result={'kind':'clean_staging_native_grader','model':'gpt-6.1-sol','case_id':'H1','condition':launch['condition'],'author_seconds':launch['seconds'],'attempt_status':launch['status'],'package_unchanged':before==after,'valid':sum(r['valid']for r in rows),'false_rejects':sum(r['valid']and r['expected_pass']and not r['actual_pass']for r in rows),'false_accepts':sum(r['valid']and not r['expected_pass']and r['actual_pass']for r in rows),'rows':rows}
(B/'grades/owner-review/H1-CLEAN-FULL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
