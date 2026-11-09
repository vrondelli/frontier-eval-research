"""Fixed selected-hit clean-input diagnostic; waits for H6 confirmation, no retries."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time
import run_clean_screen as runner

ROOT=Path(__file__).resolve().parent
POLICY=ROOT/'protocol/CLEAN-HIT-DIAGNOSTIC-POLICY.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def freeze():
    if POLICY.exists():raise RuntimeError('Refusing to overwrite existing diagnostic policy')
    jobs=[{'model':'gpt-6.1-sol','case':'H1','timeout_seconds':1200},
          {'model':'gpt-6-astra','case':'H6','timeout_seconds':600}]
    packets={job['case']:runner.verify_packet(ROOT/'packets/primary'/job['case'])for job in jobs}
    dependencies=['run_clean_screen.py','run_eval.py','run_clean_hit_diagnostic.py']
    hashes={name:sha(ROOT/name)for name in dependencies}
    for job in jobs:
        packet=ROOT/'packets/primary'/job['case']
        for p in packet.rglob('*'):
            if p.is_file():hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    policy={'schema_version':'eval-author-clean-hit-diagnostic/v1','admitted':True,
            'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'condition':'selected_hit_clean_staging_diagnostic','initial_screen_rate_eligible':False,
            'trigger':'Post-screen selection of H1 and H6 evaluator weaknesses; measure clean staging without provenance/manifest author payload.',
            'source_instruction_conditions':'H1/H6 minimal reconstruction, no stronger quality checklist',
            'actor_roots':['prompt.md','input/'],'forbidden_actor_metadata':['PROVENANCE.json','MANIFEST.json'],
            'native_python_version':'3.14.2','reasoning_effort':'high','sandbox':'Windows MXC workspace-write',
            'jobs_sequential':jobs,'worker_count':1,'model_calls_scheduled':2,
            'wait_for_terminal':'runs/CONFIRMATION-H6-TERMINAL.json',
            'concurrency_context':'May overlap3H1budgetdiagnosticactors; this supervisor contributes max1actor.',
            'automatic_retries':0,'fresh_sessions':True,'packets':packets,'files':hashes}
    runner.dump(POLICY,policy)
    print(json.dumps({'frozen':str(POLICY),'calls_scheduled':2,'executed':False}))

def execute():
    policy=json.loads(POLICY.read_text())
    if tuple(sys.version_info[:3])!=(3,14,2):raise RuntimeError('Diagnostic requires recorded CPython3.14.2 runtime')
    for name,expected in policy['files'].items():
        if sha(ROOT/name)!=expected:raise RuntimeError('Frozen diagnostic byte mismatch:'+name)
    for job in policy['jobs_sequential']:
        if(ROOT/'runs/clean_screen'/job['model']/job['case']).exists():raise RuntimeError('Fresh diagnostic output already exists')
    status_path=ROOT/'runs/CLEAN-HIT-DIAGNOSTIC-STATUS.json'
    while not(ROOT/policy['wait_for_terminal']).exists():
        runner.dump(status_path,{'status':'waiting_for_H6_confirmation','model_calls_launched':0,
                                 'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        time.sleep(15)
    terminal=json.loads((ROOT/policy['wait_for_terminal']).read_text())
    if terminal.get('scheduled')!=3 or len(terminal.get('results',[]))!=3:raise RuntimeError('H6confirmation terminal census incomplete')
    results=[]
    for job in policy['jobs_sequential']:
        for name,expected in policy['files'].items():
            if sha(ROOT/name)!=expected:raise RuntimeError('Frozen diagnostic byte mismatch before launch:'+name)
        runner.dump(status_path,{'status':'launching','job':job,'completed_jobs':len(results)})
        result=runner.safe_run((job['model'],job['case'],job['timeout_seconds']))
        results.append(result)
        runner.dump(status_path,{'status':'job_terminal','completed_jobs':len(results),'last_status':result.get('status')})
    runner.dump(ROOT/'runs/CLEAN-HIT-DIAGNOSTIC-TERMINAL.json',{'condition':policy['condition'],
                'initial_screen_rate_eligible':False,'scheduled':2,'results':results,'policy_sha256':sha(POLICY)})
    print(json.dumps({'status':'terminal','results':len(results)}))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    if a.execute:execute()
    if not a.freeze and not a.execute:print(json.dumps({'policy':str(POLICY),'executed':False}))
if __name__=='__main__':main()
