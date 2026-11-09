"""Pure native-judge paired output spelling probe on the completed clean H6 artifact."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/clean_screen/gpt-6-astra/H6/delivery';before={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()for p in package.rglob('*')if p.is_file()}
code="""import json,sys
from pathlib import Path
sys.path.insert(0,'/subject/evaluation');import evaluate as e
raw=b'{\"adjustment_sheets\":{\"zero\":{\"stat\":\"event_count\",\"turns\":[]}}}'
case=e.Case('owner-empty-count','semantics',raw,{'zero':e.Decimal(0)})
rows=[]
for label,token in [('canonical','0'),('equivalent_exponent','0e10000000000000000000')]:
 out='{\"stock_reports\":{\"zero\":'+token+'}}';path=Path('/tmp/'+label+'.json');path.write_text(out)
 try:passed,reason=e.judge(case,0,path);rows.append({'label':label,'output':out,'bytes':len(out.encode()),'pass':passed,'reason':reason})
 except Exception as exc:rows.append({'label':label,'output':out,'bytes':len(out.encode()),'error':type(exc).__name__+': '+str(exc)})
print(json.dumps({'request':raw.decode(),'expected_integer':0,'rows':rows}))
"""
cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--mount',f'type=bind,source={package},target=/subject,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);after={str(x.relative_to(package)):hashlib.sha256(x.read_bytes()).hexdigest()for x in package.rglob('*')if x.is_file()}
result={'kind':'paired_native_judge_exact_integer_output_spelling','model':'gpt-6-astra','case_id':'H6','condition':'selected_hit_clean_staging','model_calls':0,'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'package_unchanged':before==after,'public_clause':'Any JSON number encoding denoting that exact integer is acceptable, including integral exponent notation.','scope':'Direct native judge used by actual completed evaluator, same valid empty-count request and expected zero. Both tiny outputs have exact mathematical value zero.'}
if p.returncode==0:result['observed']=json.loads(p.stdout)
(B/'grades/owner-review/H6-CLEAN-OUTPUT-ZERO-PAIR.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'package_unchanged':before==after,'observed':result.get('observed')}))
