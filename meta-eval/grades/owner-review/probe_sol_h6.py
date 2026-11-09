from pathlib import Path
import json,subprocess
B=Path(__file__).resolve().parents[2];package=B/'runs/screen/gpt-6.1-sol/H6/delivery';fixture=B/'owner/cases/H6/saved_luna_decimal.json'
code="""import json,sys
from pathlib import Path
sys.path.insert(0,'/subject/evaluation');import evaluate
c=json.load(open('/control.json'));Path('/tmp/summarize.py').write_text(c['code']);case=next(c for c in evaluate.make_cases()if c.name=='negative_zero');r=evaluate.evaluate([sys.executable,'/tmp/summarize.py'],cases=[case])
output_case=evaluate.Case('owner-zero-output','equivalent_output',b'',{'e':'0'});reason=evaluate.judge_output(output_case,0,b'{\"stock_reports\":{\"e\":0e10000000000000000000}}')
print(json.dumps({'selected_negative_zero_cli':r,'legal_zero_output_rejection_reason':reason,'legal_zero_output_accepted':reason is None}))
"""
cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={fixture},target=/control.json,readonly','-w','/tmp','python:3.14-slim','python','-B','-c',code]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);r={'kind':'scoped_native_cli_and_output_probe','model':'gpt-6.1-sol','case_id':'H6','command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'scope':'Selected existing negative_zero test plus owner legal equivalent-zero output check; not entire public language.'}
if p.returncode==0:r['observed']=json.loads(p.stdout)
(B/'grades/owner-review/sol-H6-ZERO-COVERAGE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'exit':p.returncode,'observed':r.get('observed')}))
