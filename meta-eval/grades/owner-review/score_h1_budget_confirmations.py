"""Native full graders for independently completed budget-diagnostic H1 authors."""
from pathlib import Path
import hashlib,json,os,signal,subprocess
B=Path(__file__).resolve().parents[2];manifest=json.loads((B/'owner/cases/manifest.json').read_text());controls=next(c['controls']for c in manifest['cases']if c['case_id']=='H1')
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
probe=subprocess.run(base+['/usr/bin/python3','-c','print(123)'],capture_output=True,text=True,timeout=10);assert probe.returncode==0,probe.stderr
summary=[]
for draw,function in [('draw1','evaluate'),('draw2','evaluate'),('draw3','grade')]:
 package=B/'runs/budget-diagnostic/gpt-6.1-sol/H1'/draw/'delivery';launch=json.loads((package.parent/'launch.json').read_text());assert launch['status']=='completed'
 before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()};rows=[]
 code="import json,sys;sys.path.insert(0,'/subject');import evaluate;c=json.load(open('/control.json'));a=dict(task_id='E1',code=c['code'],explanation='Owner executable control; prose quality reviewed separately.');r=getattr(evaluate,sys.argv[1])(a);print(json.dumps(r))"
 for control in controls:
  cmd=base+['--ro-bind',str(package),'/subject','--ro-bind',str(B/control['path']),'/control.json','--chdir','/tmp','/usr/bin/python3','-B','-c',code,function]
  p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:out,err=p.communicate(timeout=120);status='completed'
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();status='timeout'
  row={'control':control['id'],'expected_pass':control['expected_pass'],'command':cmd,'status':status,'exit_code':p.returncode,'stdout':out,'stderr':err,'actual_pass':None}
  try:
   r=json.loads(out);row['report']=r;s=r.get('formal_status');row['actual_pass']=True if s in ['pass','passed']else False if s in ['fail','failed']else None
  except Exception as exc:row['parse_error']=repr(exc)
  row['valid']=p.returncode==0 and status=='completed'and row['actual_pass']is not None;row['correct']=row['valid']and row['actual_pass']==control['expected_pass'];rows.append(row)
 after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
 result={'kind':'completed_budget_diagnostic_native_grader','model':'gpt-6.1-sol','case_id':'H1','draw':draw,'attempt_status':launch['status'],'author_seconds':launch['seconds'],'author_cap_seconds':1200,'outer_bwrap_probe':{'exit_code':probe.returncode,'stdout':probe.stdout},'package_unchanged':before==after,'rows':rows,'valid':sum(r['valid']for r in rows),'false_rejects':sum(r['valid']and r['expected_pass']and not r['actual_pass']for r in rows),'false_accepts':sum(r['valid']and not r['expected_pass']and r['actual_pass']for r in rows),'scope':'New1200capcondition, samevisibleminimalprompt; allauthorsfinishedunder600. Separatefrominitial600capconfirmations.'}
 (B/'grades/owner-review'/('H1-BUDGET-'+draw+'-FULL.json')).write_text(json.dumps(result,indent=2)+'\n');summary.append({k:v for k,v in result.items()if k not in ['rows','outer_bwrap_probe']});print(json.dumps(summary[-1]),flush=True)
(B/'grades/owner-review/H1-BUDGET-NATIVE-SUMMARY.json').write_text(json.dumps({'draws':summary},indent=2)+'\n')
