"""Clean author runner v2: preserve native terminal facts before delivery capture."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
import time
from run_eval import execute, inventory, dump

ROOT=Path(__file__).resolve().parent
PACKET_CONDITION='primary'

def snapshot_inventory(root):
    root=long_path(root);result={}
    for p in root.rglob('*'):
        key=p.relative_to(root).as_posix()
        if p.is_symlink():result[key]={'kind':'symlink','target':str(p.readlink())}
        elif p.is_file():result[key]={'kind':'file','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    return result

def archive_stable(source,destination):
    observation_errors=[];expected=None
    for attempt in range(3):
        try:
            first=snapshot_inventory(source);time.sleep(.25);second=snapshot_inventory(source)
            if first==second:expected=second;break
            observation_errors.append('Source inventory changed between observations')
        except OSError as error:observation_errors.append(str(error))
    if expected is None:
        return {'archive_status':'source_unstable','delivery_custody_verified':False,'observation_errors':observation_errors}
    try:
        shutil.copytree(long_path(source),long_path(destination),symlinks=True)
        actual=snapshot_inventory(destination);after=snapshot_inventory(source)
    except Exception as error:
        return {'archive_status':'copy_error','archive_error':str(error),'delivery_custody_verified':False,
                'source_stability_observations':2,'observation_errors':observation_errors}
    qualified=actual==expected and after==expected
    return {'archive_status':'verified'if qualified else'inventory_mismatch','delivery_custody_verified':qualified,
            'source_stability_observations':2,'observation_errors':observation_errors,'capture_inventory':actual,
            'output_inventory':{k:v['sha256']for k,v in actual.items()if v['kind']=='file'},
            'output_symlinks':{k:v['target']for k,v in actual.items()if v['kind']=='symlink'}}

def capture_self_check():
    with tempfile.TemporaryDirectory(prefix='eval-capture-gate-')as tmp:
        root=Path(tmp);source=root/'source';source.mkdir();(source/'probe.txt').write_text('harmless stable source')
        success=archive_stable(source,root/'delivery')
        blocked=root/'blocked';blocked.write_text('existing path')
        native={'status':'completed','native_status':'completed','exit_code':0,'seconds':1.0}
        native.update(archive_stable(source,blocked))
        report={'model_calls':0,'stable_copy_qualified':success['delivery_custody_verified'],
                'copy_fault_retains_native_completed':native['status']=='completed'and native['native_status']=='completed'and native['exit_code']==0,
                'copy_fault_custody_unqualified':not native['delivery_custody_verified'],'fault_receipt':native}
    dump(ROOT/'grades/audit-review/CAPTURE-V2-SELF-CHECK.json',report)
    print(json.dumps(report));return 0 if all(report[k]for k in ['stable_copy_qualified','copy_fault_retains_native_completed','copy_fault_custody_unqualified'])else 1

def long_path(path):
    value=str(Path(path).absolute())
    if os.name!='nt'or value.startswith('\\\\?\\'):return Path(value)
    return Path('\\\\?\\UNC\\'+value[2:])if value.startswith('\\\\')else Path('\\\\?\\'+value)

def verify_packet(packet):
    packet=long_path(packet)
    if any(p.is_symlink()for p in packet.rglob('*')):raise ValueError('Packet symlink refused')
    manifest=json.loads((packet/'MANIFEST.json').read_text(encoding='utf-8'))
    provenance=json.loads((packet/'PROVENANCE.json').read_text(encoding='utf-8'))
    expected={item['path']:item for item in manifest['files']}
    actual={p.relative_to(packet).as_posix()for p in packet.rglob('*')if p.is_file()}
    if actual!=set(expected)|{'MANIFEST.json'}:raise ValueError('Packet contains missing or unlisted files')
    for relative,item in expected.items():
        if Path(relative).is_absolute()or '..'in Path(relative).parts:raise ValueError('Manifest path escapes packet')
        p=packet/relative
        data=p.read_bytes()
        if hashlib.sha256(data).hexdigest()!=item['sha256']or ('bytes'in item and len(data)!=item['bytes']):
            raise ValueError('Packet byte mismatch: '+relative)
    prompt_hash=hashlib.sha256((packet/'prompt.md').read_bytes()).hexdigest()
    if provenance.get('author_instruction_sha256')!=prompt_hash:raise ValueError('Prompt differs from provenance')
    case_id=manifest.get('case_id',provenance.get('case_id'))
    if not case_id or case_id!=provenance.get('case_id'):raise ValueError('Packet case identity mismatch')
    return {'case_id':case_id,'manifest_sha256':hashlib.sha256((packet/'MANIFEST.json').read_bytes()).hexdigest(),
            'provenance_sha256':hashlib.sha256((packet/'PROVENANCE.json').read_bytes()).hexdigest(),
            'verified_file_count':len(expected),'prompt_sha256':prompt_hash}

def preflight_self_check():
    source=ROOT/'packets/primary/H1';positive=verify_packet(source)
    with tempfile.TemporaryDirectory(prefix='eval-clean-gate-')as tmp:
        packet=Path(tmp)/'packet';shutil.copytree(source,packet)
        path=next((packet/'input').rglob('*'));path.write_bytes(path.read_bytes()+b'\nchanged')
        try:verify_packet(packet);refused=False
        except ValueError:refused=True
    result={'model_calls':0,'unchanged_packet_accepted':True,'modified_input_refused_before_launch':refused,
            'positive_receipt':positive}
    dump(ROOT/'grades/audit-review/CLEAN-RUNNER-PREFLIGHT-CHECK.json',result)
    print(json.dumps(result));return 0 if refused else 1

def long_path_self_check():
    base=ROOT/'grades/audit-review'/('long-path-gate-'+uuid.uuid4().hex)
    destination=base/('p'*80)/('q'*80)/('r'*80)
    with tempfile.TemporaryDirectory(prefix='eval-longpath-source-')as tmp:
        source=Path(tmp)/'source';source.mkdir();(source/'probe.txt').write_text('harmless copy/hash test')
        shutil.copytree(long_path(source),long_path(destination))
        correct=inventory(long_path(source))==inventory(long_path(destination))
    result={'model_calls':0,'destination_characters':len(str(destination/'probe.txt')),
            'windows_extended_path_used':os.name=='nt','copy_and_hash_match':correct}
    # Remove only the explicitly created scratch leaf and its known empty parents.
    long_path(destination/'probe.txt').unlink()
    for path in [destination,destination.parent,destination.parent.parent,base]:long_path(path).rmdir()
    dump(ROOT/'grades/audit-review/LONG-PATH-COPY-CHECK.json',result)
    print(json.dumps(result));return 0 if correct and result['destination_characters']>260 else 1

def run(job):
    model,case,cap=job
    packet=ROOT/'packets'/PACKET_CONDITION/case
    preflight=verify_packet(packet)
    if preflight['case_id']!=case:raise ValueError('Requested case differs from packet identity')
    out=ROOT/'runs/clean_screen_v2'/PACKET_CONDITION/model/case
    if out.exists():raise RuntimeError('Refusing to overwrite '+str(out))
    out.mkdir(parents=True)
    work=Path(tempfile.mkdtemp(prefix='eval-clean-'+case+'-'))/'workspace';work.mkdir()
    source=packet/'input'
    if any(p.is_symlink()for p in source.rglob('*')):raise ValueError('public input symlink requires review')
    shutil.copytree(long_path(source),long_path(work/'input'))
    shutil.copy2(long_path(packet/'prompt.md'),long_path(work/'prompt.md'))
    expected_actor={name:record for name,record in inventory(long_path(packet)).items()if name=='prompt.md'or name.startswith('input/')}
    if inventory(work)!=expected_actor:raise ValueError('Staged actor payload differs from verified public files')
    prompt=(work/'prompt.md').read_text(encoding='utf-8')
    provenance=json.loads((packet/'PROVENANCE.json').read_text(encoding='utf-8'))
    cli=shutil.which('codex.exe')or shutil.which('codex')
    if cli is None:raise RuntimeError('Codex executable unavailable')
    command=[cli,'-c','windows.sandbox=mxc','exec','--json','--skip-git-repo-check',
             '-C',str(work),'-s','workspace-write','-m',model,'-c','model_reasoning_effort="high"',
             '-o',str(out/'final.txt'),'-']
    runtimebin=work.parent/'runtimebin';runtimebin.mkdir()
    (runtimebin/'python3.cmd').write_text('@"'+sys.executable+'" %*\r\n',encoding='utf-8')
    # The local alias is execution infrastructure outside the author workspace.
    prior_path=os.environ.get('PATH','')
    env=os.environ.copy();env['PATH']=str(runtimebin)+os.pathsep+str(Path(sys.executable).parent)+os.pathsep+prior_path
    receipt={'case_id':case,'model_requested':model,'condition':'coached_clean_capture_v2'if PACKET_CONDITION=='coached'else'clean_staging_capture_v2',
             'source_instruction_condition':provenance['condition_id'],'exact_full_context_replication':False,
             'metadata_payload_supplied':False,'staged_roots':['prompt.md','input/'],
             'source_preflight':preflight,
             'input_inventory':inventory(work),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
             'workspace':str(work),'command':command,'python_executable':sys.executable,'python_runtime':sys.version,
             'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formal_claim_eligible':False}
    dump(out/'launch.json',receipt)
    # execute helper has no environment override; use Popen locally to retain the exact scoped PATH.
    import subprocess,time
    started=time.monotonic()
    process=subprocess.Popen(command,cwd=work,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    receipt['pid']=process.pid;dump(out/'launch.json',receipt)
    try:stdout,stderr=process.communicate(prompt,timeout=cap);status='completed'
    except subprocess.TimeoutExpired:
        if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
        else:process.kill()
        stdout,stderr=process.communicate();status='timeout'
    receipt.update(status=status,native_status=status,exit_code=process.returncode,seconds=time.monotonic()-started,
                   end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive_status='pending',
                   transcript_sha256=hashlib.sha256(stdout.encode()).hexdigest(),
                   stderr_sha256=hashlib.sha256(stderr.encode()).hexdigest(),native_final_present=(out/'final.txt').exists())
    events=[]
    for line in stdout.splitlines():
        try:events.append(json.loads(line))
        except ValueError:pass
    receipt['native_turn_completed_event']=any(e.get('type')=='turn.completed'for e in events)
    receipt['native_turn_failed_event']=any(e.get('type')=='turn.failed'for e in events)
    receipt['raw_capture_status']='pending'
    # Persist native outcome and raw outputs BEFORE any filesystem archive operation.
    dump(out/'launch.json',receipt)
    try:
        (out/'transcript.jsonl').write_text(stdout,encoding='utf-8');(out/'stderr.txt').write_text(stderr,encoding='utf-8')
        receipt['raw_capture_status']='written'
    except Exception as error:
        receipt.update(raw_capture_status='write_error',raw_capture_error=str(error))
    dump(out/'launch.json',receipt)
    receipt.update(archive_stable(work,out/'delivery'))
    dump(out/'launch.json',receipt)
    return receipt

def safe_run(job):
    try:return run(job)
    except Exception as error:
        model,case,_=job;out=ROOT/'runs/clean_screen_v2'/PACKET_CONDITION/model/case;launch=out/'launch.json'
        receipt=json.loads(launch.read_text())if launch.exists()else{'case_id':case,'model_requested':model}
        receipt['runtime_error']=str(error)
        if receipt.get('native_status')not in ['completed','timeout']:receipt['status']='runtime_error'
        receipt['delivery_custody_verified']=False
        dump(out/'runtime-error.json',receipt);return receipt

def main():
    global PACKET_CONDITION
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true')
    p.add_argument('--preflight-self-check',action='store_true');p.add_argument('--preflight',action='store_true')
    p.add_argument('--long-path-self-check',action='store_true')
    p.add_argument('--capture-self-check',action='store_true')
    p.add_argument('--packet-condition',choices=['primary','coached'],default='primary')
    p.add_argument('--models',nargs='+',default=['gpt-6.1-sol','gpt-6-astra']);p.add_argument('--cases',nargs='+',default=['H'+str(i)for i in range(1,10)])
    p.add_argument('--workers',type=int,default=4);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    jobs=[(m,c,a.timeout)for c in a.cases for m in a.models]
    PACKET_CONDITION=a.packet_condition
    if a.preflight_self_check:return preflight_self_check()
    if a.long_path_self_check:return long_path_self_check()
    if a.capture_self_check:return capture_self_check()
    if a.preflight:
        report={'model_calls':0,'packet_condition':PACKET_CONDITION,'packets':[verify_packet(ROOT/'packets'/PACKET_CONDITION/case)for case in a.cases]}
        dump(ROOT/'grades/audit-review/CLEAN-RUNNER-PREFLIGHT.json',report)
        print(json.dumps(report));return
    if not a.execute:
        print(json.dumps({'executed':False,'scheduled':len(jobs),'condition':'coached_clean_capture_v2'if PACKET_CONDITION=='coached'else'clean_staging_capture_v2',
                          'only_actor_roots':['prompt.md','input/'],'jobs':jobs}));return
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers)as pool:results=list(pool.map(safe_run,jobs))
    dump(ROOT/('runs/CLEAN-SCREEN-V2-'+PACKET_CONDITION.upper()+'-TERMINAL.json'),{'condition':PACKET_CONDITION,'scheduled':len(jobs),'results':results})

if __name__=='__main__':raise SystemExit(main()or 0)
