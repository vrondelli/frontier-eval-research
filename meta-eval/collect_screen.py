"""Read existing receipts only; never launches/retries actors."""
import hashlib,json,pathlib,os
ROOT=pathlib.Path(__file__).resolve().parent
def long_path(p):
 value=str(pathlib.Path(p).absolute())
 if os.name!='nt'or value.startswith('\\\\?\\'):return pathlib.Path(value)
 return pathlib.Path('\\\\?\\UNC\\'+value[2:])if value.startswith('\\\\')else pathlib.Path('\\\\?\\'+value)
policy=json.loads((ROOT/'protocol/RUN-POLICY.json').read_text())
rows=[]
for case in policy['screen']['case_ids']:
 for model in policy['models']:
  folder=ROOT/'runs/screen'/model/case;p=folder/'launch.json'
  row={'model':model,'case':case,'status':'pending'}
  if p.exists():
   data=json.loads(p.read_text());row.update(status=data.get('status','launched'),pid=data.get('pid'),condition=data.get('condition'),exit_code=data.get('exit_code'),seconds=data.get('seconds'))
   if 'output_inventory'in data:
    delivery=long_path(folder/'delivery')
    actual={f.relative_to(delivery).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in delivery.rglob('*')if f.is_file()and not f.is_symlink()}
    row['delivery_hashes_match']=actual==data['output_inventory']
   transcript=folder/'transcript.jsonl'
   if transcript.exists():
    events=[];invalid=0
    for line in transcript.read_text(encoding='utf-8').splitlines():
     try:events.append(json.loads(line))
     except ValueError:invalid+=1
    row['event_count']=len(events);row['invalid_json_lines']=invalid
    row['thread_ids']=[e.get('thread_id')for e in events if e.get('type')=='thread.started']
   if(folder/'runtime-error.json').exists():
    row['raw_runtime_fault_retained']=True;row['raw_runtime_error_path']=str(folder/'runtime-error.json')
    if row['status']=='launched':row['status']='runtime_error'
   recovery_path=folder/'RECOVERY.json'
   if recovery_path.exists():
    recovery=json.loads(recovery_path.read_text())
    row['raw_launch_status']=data.get('status','not_persisted')
    row['recovery_status']=recovery['recovered_status'];row['native_exit_code_recovery']='not_persisted'
    row['recovery_receipt']=str(recovery_path)
    delivery=long_path(folder/'delivery');actual={}
    for f in delivery.rglob('*'):
     relative=f.relative_to(delivery).as_posix()
     if f.is_symlink():actual[relative]={'symlink':str(f.readlink())}
     elif f.is_file():actual[relative]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
    row['delivery_hashes_match']=actual==recovery['inventory']
    row['status']='recovered_completed'if recovery.get('native_turn_completed_event')and recovery.get('delivery_custody_verified')and row['delivery_hashes_match']else'recovered_unknown'
  rows.append(row)
result={'expected':len(rows),'completed':sum(r['status']in['completed','recovered_completed']for r in rows),'recovered_completed':sum(r['status']=='recovered_completed'for r in rows),'timeouts':sum(r['status']=='timeout'for r in rows),'runtime_errors':sum(r['status']=='runtime_error'for r in rows),'raw_runtime_faults_retained':sum(r.get('raw_runtime_fault_retained',False)for r in rows),'rows':rows}
(ROOT/'runs/SCREEN-CENSUS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
