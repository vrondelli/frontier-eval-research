import datetime,hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
paths=['run_confirmation.py','protocol/CONFIRMATION-H1-ADMISSION.json','grades/root-review/H1-SOL-REPLAY.json','grades/owner-review/sol-H1-FULL-BWRAP.json','packets/primary/H1/prompt.md','packets/primary/H1/MANIFEST.json','FREEZE.json']
value={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cohort':'3freshSolH1authorattempts','same_primary_packet':True,'models':['gpt-6.1-sol'],'condition':'minimal_reconstruction_with_metadata','files':{p:hashlib.sha256((root/p).read_bytes()).hexdigest()for p in paths}}
target=root/'CONFIRMATION-FREEZE.json'
if target.exists():raise SystemExit('Refusing overwrite')
target.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'frozen_files':len(paths)}))
