"""Read the two admitted three-draw cohorts without launching or restarting them."""
import json,pathlib,hashlib
from run_clean_screen_v2 import long_path
ROOT=pathlib.Path(__file__).resolve().parent;rows=[]
for model,case in [('gpt-6.1-sol','H1'),('gpt-6-astra','H6')]:
 for draw in range(1,4):
  folder=ROOT/'runs/confirmation'/model/case/('draw'+str(draw));path=folder/'launch.json';error=folder/'runtime-error.json'
  row={'model':model,'case':case,'draw':draw,'status':'pending'}
  if path.exists():
   r=json.loads(path.read_text());row.update(status=r.get('status','running'),pid=r.get('pid'),condition=r.get('condition'),seconds=r.get('seconds'),exit_code=r.get('exit_code'))
  if error.exists():row.update(status='runtime_error',error=json.loads(error.read_text()).get('runtime_error'),raw_runtime_fault_retained=True)
  recovery_path=folder/'RECOVERY.json'
  if recovery_path.exists():
   recovery=json.loads(recovery_path.read_text());delivery=long_path(folder/'delivery');actual={}
   for f in delivery.rglob('*'):
    relative=f.relative_to(delivery).as_posix()
    if f.is_symlink():actual[relative]={'symlink':str(f.readlink())}
    elif f.is_file():actual[relative]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
   row['delivery_hashes_match']=actual==recovery['inventory'];row['capture_recovery_status']=recovery['recovered_status']
   row['native_terminal_status']=recovery.get('native_terminal_status','not_persisted')
   row['native_exit_code']='not_persisted'
   row['status']='recovered_completed'if recovery.get('native_turn_completed_event')and row['delivery_hashes_match']else'capture_recovered_native_unknown'
  rows.append(row)
report={'scheduled':6,'completed':sum(r['status']in['completed','recovered_completed']for r in rows),'timeouts':sum(r['status']=='timeout'for r in rows),'runtime_errors':sum(r['status']=='runtime_error'for r in rows),'native_terminal_unknown':sum(r['status']=='capture_recovered_native_unknown'for r in rows),'raw_runtime_faults_retained':sum(r.get('raw_runtime_fault_retained',False)for r in rows),'rows':rows}
(ROOT/'runs/CONFIRMATION-CENSUS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
