"""Paired literal-only control intervention on fresh completed H1 budget draw1.

Run from Linux with working bubblewrap. No model calls or subject-code edits.
"""
from pathlib import Path
import hashlib,json,os,signal,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/budget-diagnostic/gpt-6.1-sol/H1/draw1/delivery';source=B/'owner/cases/H1/correct_applied.json'
before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
probe=subprocess.run(base+['/usr/bin/python3','-c','print(123)'],capture_output=True,text=True,timeout=10);assert probe.returncode==0,probe.stderr
code="""import hashlib,json,sys
sys.path.insert(0,'/subject');import evaluate
c=json.load(open('/control.json'));source=c['code'];needle=\"'applied' if changed\";assert source.count(needle)==1
if sys.argv[1]=='accepted':source=source.replace(needle,\"'accepted' if changed\")
answer=dict(task_id='E1',code=source,explanation='Owner executable control; prose quality independently reviewed.')
report=evaluate.evaluate(answer);print(json.dumps({'code_sha256':hashlib.sha256(source.encode()).hexdigest(),'literal':sys.argv[1],'report':report}))
"""
rows=[]
for literal in ['applied','accepted']:
 cmd=base+['--ro-bind',str(package),'/subject','--ro-bind',str(source),'/control.json','--chdir','/tmp','/usr/bin/python3','-B','-c',code,literal]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 try:out,err=p.communicate(timeout=120);state='completed'
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();state='timeout'
 row={'literal':literal,'command':cmd,'status':state,'exit_code':p.returncode,'stdout':out,'stderr':err}
 try:row['observed']=json.loads(out)
 except ValueError:pass
 rows.append(row)
after={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
result={'kind':'paired_literal_only_native_grader_intervention','model':'gpt-6.1-sol','case_id':'H1','draw':'budget-diagnostic/draw1','author_attempt_completed':True,'model_calls':0,'subject_package_unchanged':before==after,'source_control_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'intervention':"Only 'applied' if changed becomes 'accepted' if changed; same Service code, requests, owner explanation, execution boundary and grader.",'rows':rows}
(B/'grades/owner-review/H1-BUDGET-draw1-LITERAL-PAIR.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'package_unchanged':before==after,'verdicts':[(r['literal'],r.get('observed',{}).get('report',{}).get('formal_status'))for r in rows]}))
