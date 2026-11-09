"""Final fixed two-call coached diagnostic; wait for prior clean and budget cohorts."""
import argparse,datetime,hashlib,json,subprocess,sys,time
from pathlib import Path
import run_clean_screen_v2 as runner
ROOT=Path(__file__).resolve().parent
POLICY=ROOT/'protocol/COACHED-HIT-DIAGNOSTIC-POLICY.json'
QUALITY='Create a complete runnable eval for this task, including a public task statement, independent reference, grader, positive and negative controls, clean runner, and a report schema. State every graded requirement in the public task. Verify your eval before delivery.'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def freeze():
    if POLICY.exists():raise RuntimeError('Refusing to overwrite coached policy')
    jobs=[{'model':'gpt-6.1-sol','case':'H1','timeout_seconds':1200},{'model':'gpt-6-astra','case':'H6','timeout_seconds':600}]
    packets={};hashes={name:sha(ROOT/name)for name in ['run_clean_screen_v2.py','run_eval.py','run_coached_hit_diagnostic.py']}
    for job in jobs:
        case=job['case'];primary=ROOT/'packets/primary'/case;coached=ROOT/'packets/coached'/case
        packets[case]=runner.verify_packet(coached)
        text=(coached/'prompt.md').read_text(encoding='utf-8')
        base,added=text.split('Additional explicit quality instruction:',1)
        if base.strip()!=(primary/'prompt.md').read_text(encoding='utf-8').strip()or added.strip()!=QUALITY:
            raise RuntimeError('Coached prompt contains changes beyond the admitted checklist')
        if runner.inventory(primary/'input')!=runner.inventory(coached/'input'):raise RuntimeError('Public task data differ')
        for packet in [primary,coached]:
            for path in packet.rglob('*'):
                if path.is_file():hashes[path.relative_to(ROOT).as_posix()]=sha(path)
    policy={'schema_version':'eval-author-coached-hit-diagnostic/v1','admitted':True,
            'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'condition':'selected_hit_coached_clean_capture_v2','initial_screen_rate_eligible':False,
            'only_instruction_change':QUALITY,'prior_results_or_failure_witness_hints_supplied':False,
            'public_task_inputs_identical':True,'actor_roots':['prompt.md','input/'],
            'native_python_version':'3.14.2','reasoning_effort':'high','sandbox':'Windows MXC workspace-write',
            'jobs_sequential':jobs,'worker_count':1,'calls_scheduled':2,'grand_total_model_arm_cap':31,
            'stop_new_model_arms_after_this_policy':True,'automatic_retries':0,
            'wait_for_terminals':{'runs/CLEAN-HIT-DIAGNOSTIC-TERMINAL.json':2,'runs/BUDGET-H1-TERMINAL.json':3},
            'interpretation':'One fresh draw per selected job/model; diagnostic prompt comparison, not a population failure rate or causal estimate.',
            'packets':packets,'files':hashes}
    runner.dump(POLICY,policy);print(json.dumps({'frozen':str(POLICY),'calls_scheduled':2,'executed':False}))
def execute():
    if tuple(sys.version_info[:3])!=(3,14,2):raise RuntimeError('Recorded Python3.14.2 required')
    policy=json.loads(POLICY.read_text());status_path=ROOT/'runs/COACHED-HIT-DIAGNOSTIC-STATUS.json'
    for name,value in policy['files'].items():
        if sha(ROOT/name)!=value:raise RuntimeError('Frozen source mismatch:'+name)
    while True:
        ready=True
        for name,count in policy['wait_for_terminals'].items():
            try:terminal=json.loads((ROOT/name).read_text())
            except (FileNotFoundError,ValueError):ready=False;continue
            if terminal.get('scheduled')!=count or len(terminal.get('results',[]))!=count:ready=False
        if ready:break
        runner.dump(status_path,{'status':'waiting_for_clean_and_budget_terminal','calls_launched':0,
                                 'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});time.sleep(15)
    # Verify old native model PIDs are absent; never infer termination from a stale file alone.
    for folder in [ROOT/'runs/clean_screen/gpt-6.1-sol/H1',ROOT/'runs/clean_screen/gpt-6-astra/H6']+list((ROOT/'runs/budget-diagnostic/gpt-6.1-sol/H1').glob('draw*')):
        launch=folder/'launch.json'
        if launch.exists():
            receipt=json.loads(launch.read_text());pid=receipt.get('pid')
            if pid:
                probe=subprocess.run(['tasklist','/FI',f'PID eq {pid}','/FO','CSV','/NH'],capture_output=True,text=True)
                if f'"{pid}"'in probe.stdout:raise RuntimeError('Prior native actor still live; no coached call launched')
    runner.PACKET_CONDITION='coached';results=[]
    for job in policy['jobs_sequential']:
        for name,value in policy['files'].items():
            if sha(ROOT/name)!=value:raise RuntimeError('Frozen source mismatch:'+name)
        runner.dump(status_path,{'status':'launching','job':job,'completed_jobs':len(results)})
        result=runner.safe_run((job['model'],job['case'],job['timeout_seconds']));results.append(result)
        runner.dump(status_path,{'status':'job_terminal','completed_jobs':len(results),'last_status':result.get('status')})
    runner.dump(ROOT/'runs/COACHED-HIT-DIAGNOSTIC-TERMINAL.json',{'condition':policy['condition'],'scheduled':2,
                'initial_screen_rate_eligible':False,'results':results,'policy_sha256':sha(POLICY)})
    print(json.dumps({'status':'terminal','results':len(results)}))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    if a.execute:execute()
    if not a.freeze and not a.execute:print(json.dumps({'executed':False,'policy':str(POLICY)}))
if __name__=='__main__':main()
