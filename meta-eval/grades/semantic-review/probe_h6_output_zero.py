"""Independent single-case output-spelling pair; no model calls or candidate programs."""
import json,hashlib,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
package=B/'runs/screen/gpt-6-astra/H6/delivery';before={p.relative_to(package).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
linux='/home/vlad_/projects/engineer-assessment/'+package.resolve().relative_to(Path(r'\\wsl.localhost\Ubuntu-26.04\home\vlad_\projects\engineer-assessment')).as_posix()
code='''import json,sys
sys.path.insert(0,'/subject/evaluation')
from cases import Case
from evaluate import judge
raw='{"adjustment_sheets":{"zero":{"stat":"event_count","turns":[]}}}'
case=Case('independent-empty-count','independent-output-spelling',raw,{'zero':0})
canonical=b'{"stock_reports":{"zero":0}}'
exponent=b'{"stock_reports":{"zero":0e10000000000000000000}}'
rows=[]
for name,out in [('canonical_zero',canonical),('exponent_zero',exponent)]:
 passed,reason=judge(case,0,out)
 rows.append({'spelling':name,'input':raw,'input_bytes':len(raw.encode()),'candidate_exit':0,'output':out.decode(),'output_bytes':len(out),'expected_exact_value':0,'judge_passed':passed,'judge_reason':reason})
print(json.dumps({'case_expected':case.expected,'receipts':rows}))
'''
cmd=['wsl.exe','--distribution','Ubuntu-26.04','--user','vlad_','--exec','docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--memory','256m','--cpus','1','--pids-limit','64','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','-v',linux+':/subject:ro','-w','/tmp','python:3.14-slim','python','-B','-c',code]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
after={q.relative_to(package).as_posix():hashlib.sha256(q.read_bytes()).hexdigest()for q in package.rglob('*')if q.is_file()}
r={'kind':'independent_direct_judge_output_spelling_pair','condition':'post_outcome_semantic_diagnostic','reviewer_type':'AI_reviewer_not_human','model_calls':0,'command':cmd,'exit_code':p.returncode,'stderr':p.stderr,'package_unchanged':before==after,'judge_source_sha256':before['evaluation/evaluate.py'],'source_case_sha256':before['evaluation/cases.py'],'scope':'One legal empty-count output case, identical mathematicalvalue0 under two explicitly permitted representations. No assertion that an entire authored output-spelling CLI is universally correct.'}
try:r['observed']=json.loads(p.stdout)
except ValueError:r['stdout']=p.stdout
(HERE/'H6-OUTPUT-ZERO-PAIR.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps({'exit_code':p.returncode,'package_unchanged':before==after,'observed':r.get('observed')}))
