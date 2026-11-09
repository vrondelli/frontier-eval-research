"""Native coached H1 checks respecting its explicitly published status vocabulary."""
from pathlib import Path
import hashlib,json,os,signal,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/clean_screen_v2/coached/gpt-6.1-sol/H1/delivery';launch=json.loads((package.parent/'launch.json').read_text());assert launch['status']=='completed'
controls=next(c['controls']for c in json.loads((B/'owner/cases/manifest.json').read_text())['cases']if c['case_id']=='H1');before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
probe=subprocess.run(base+['/usr/bin/python3','-c','print(123)'],capture_output=True,text=True,timeout=10);assert probe.returncode==0,probe.stderr
code="""import hashlib,json,sys
sys.path.insert(0,'/subject');from e1eval.grader import grade
c=json.load(open('/control.json'));old=c['code'];source=old.replace(\"'applied' if changed\",\"'accepted' if changed\")
r=grade(dict(task_id='E1',code=source,explanation='Owner executable control; prose quality is separately reviewed.'));print(json.dumps({'report':r,'owner_mapping':{'reason':'Coached publicTASK explicitly mandates accepted literal; only conform ownercontrol wirevalue, preserving all business faults. This is not a subject repair.','source_sha256':hashlib.sha256(old.encode()).hexdigest(),'mapped_sha256':hashlib.sha256(source.encode()).hexdigest(),'literal_only_changes':old.count(\"'applied' if changed\")}}))
"""
rows=[]
for control in controls:
 cmd=base+['--ro-bind',str(package),'/subject','--ro-bind',str(B/control['path']),'/control.json','--chdir','/tmp','/usr/bin/python3','-B','-c',code]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 try:out,err=p.communicate(timeout=120);status='completed'
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();status='timeout'
 row={'control':control['id'],'expected_after_public_vocabulary_mapping':control['expected_pass'],'command':cmd,'status':status,'exit_code':p.returncode,'stdout':out,'stderr':err,'actual_pass':None}
 try:v=json.loads(out);row['observed']=v;s=v['report']['formal_status'];row['actual_pass']=s=='pass'if s in ['pass','fail']else None
 except Exception as e:row['parse_error']=repr(e)
 row['valid']=p.returncode==0 and status=='completed'and row['actual_pass']is not None;row['correct']=row['valid']and row['actual_pass']==control['expected_pass'];rows.append(row)
after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
result={'kind':'coached_public_contract_native_check','model':'gpt-6.1-sol','case_id':'H1','condition':launch['condition'],'attempt_status':launch['status'],'author_seconds':launch['seconds'],'package_unchanged':before==after,'valid':sum(r['valid']for r in rows),'correct':sum(r['correct']for r in rows),'rows':rows,'scope':'NewcoachedTASK explicitly states accepted literal and is the actualsole solver input. Oldappliedpositive is outofnewwirecontract; mappedcontrols test validpubliccontract, not originalscopepreservation. No hidden-literal recurrence if mappingpasses.'}
(B/'grades/owner-review/H1-COACHED-FULL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
