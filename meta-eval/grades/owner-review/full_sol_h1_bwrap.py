"""Full immutable Sol H1 native grader inside an outer user/PID/network/filesystem boundary."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,tempfile
B=Path(__file__).resolve().parents[2];package=B/'runs/screen/gpt-6.1-sol/H1/delivery'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
manifest=json.loads((B/'owner/cases/manifest.json').read_text());case=next(c for c in manifest['cases']if c['case_id']=='H1')
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
probe=subprocess.run(base+['/usr/bin/python3','-c','print(123)'],capture_output=True,text=True,timeout=10)
receipts=[]
code="import json;from evaluation.grader import grade;c=json.load(open('/control.json'));print(json.dumps(grade({'task_id':'E1','code':c['code'],'explanation':'Owner-authored executable control; prose quality is separately reviewed.'})))"
if probe.returncode==0:
 for c in case['controls']:
  cmd=base+['--ro-bind',str(package),'/subject','--ro-bind',str(B/c['path']),'/control.json','--chdir','/subject','/usr/bin/python3','-B','-c',code]
  p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:out,err=p.communicate(timeout=120);state='completed'
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();state='timeout'
  r={'control':c['id'],'expected_pass':c['expected_pass'],'command':cmd,'status':state,'exit_code':p.returncode,'stdout':out,'stderr':err}
  try:
   report=json.loads(out);r['report']=report;r['actual_pass']=report['formal_status']=='pass'if report['formal_status']in ['pass','fail']else None
  except Exception as e:r['parse_error']=repr(e);r['actual_pass']=None
  r['valid']=state=='completed'and p.returncode==0 and r['actual_pass']is not None
  r['correct']=r['valid']and r['actual_pass']==r['expected_pass'];receipts.append(r)
after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
result={'kind':'full_native_grader_outer_bwrap','model':'gpt-6.1-sol','case_id':'H1','attempt_status':'completed','outer_probe':{'exit_code':probe.returncode,'stdout':probe.stdout,'stderr':probe.stderr},'package_unchanged':before==after,'receipts':receipts,'total':len(receipts),'valid':sum(r['valid']for r in receipts),'false_rejects':sum(r['valid']and not r['actual_pass']and r['expected_pass']for r in receipts),'false_accepts':sum(r['valid']and r['actual_pass']and not r['expected_pass']for r in receipts)}
(B/'grades/owner-review/sol-H1-FULL-BWRAP.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['receipts']}))
