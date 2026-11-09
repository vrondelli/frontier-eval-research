"""Show a saved faulty numeric CLI passing the fresh Astra-created84-case eval."""
import argparse,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
def inv(p):return {f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in p.rglob('*')if f.is_file()and not f.is_symlink()}
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=pathlib.Path,default=ROOT/'replays/H6-ASTRA-REPLAY.json');args=a.parse_args()
 package=ROOT/'runs/screen/gpt-6-astra/H6/delivery';control=ROOT/'owner/cases/H6/saved_luna_decimal.json';before=inv(package)
 script='''import json,sys,shutil,subprocess
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();candidate=Path('/tmp/candidate/summarize.py');candidate.write_text(c['code'])
raw='{"adjustment_sheets":{"root / exact zero":{"stat":"event_count","turns":[0e10000000000000000000]},"root / mixed zero":{"stat":"event_count","turns":[0e10000000000000000000,0,1]}}}'
paired=[]
for name,text in [('exponent_zero',raw),('plain_zero',raw.replace('0e10000000000000000000','0'))]:
 inp=Path('/tmp/candidate/'+name+'.json');out=Path('/tmp/candidate/'+name+'-output.json');inp.write_text(text)
 r=subprocess.run([sys.executable,str(candidate),str(inp),str(out)],capture_output=True,text=True,timeout=5)
 paired.append({'input':text,'case':name,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'output':out.read_text()if out.exists()else None})
sys.path.insert(0,'/tmp/eval/evaluation');import evaluate
report=evaluate.run_suite(str(candidate),work_dir='/tmp')
print(json.dumps({'candidate_pair':paired,'new_eval_report':report,'expected_counts':[1,3]}))
'''
 cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,nosuid,size=32m','--mount',f'type=bind,source={package},target=/subject,readonly','--mount',f'type=bind,source={control},target=/control.json,readonly','-w','/subject','python:3.14-slim','python','-B','-c',script]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=180);observed=json.loads(r.stdout)if r.returncode==0 else{}
 expected={'stock_reports':{'root / exact zero':1,'root / mixed zero':3}}
 plain_correct=bool(observed)and json.loads(observed['candidate_pair'][1]['output'])==expected
 value={'kind':'independent_root_numeric_false_green','model':'gpt-6-astra','case_id':'H6','command':cmd,'exit_code':r.returncode,'stderr':r.stderr,'observed':observed,'plain_zero_expected_counts_verified':plain_correct,'package_unchanged':before==inv(package)}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2)+'\n')
 ok=r.returncode==0 and observed['candidate_pair'][0]['exit_code']!=0 and observed['candidate_pair'][1]['exit_code']==0 and plain_correct and observed['new_eval_report']['all_passed']and value['package_unchanged']
 print(json.dumps({'saved_candidate_rejects_legal_zero':bool(observed)and observed['candidate_pair'][0]['exit_code']!=0,'new_eval_all_passed':observed.get('new_eval_report',{}).get('all_passed'),'package_unchanged':value['package_unchanged']}))
 return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
