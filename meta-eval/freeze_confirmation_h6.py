import datetime,hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
paths=['run_confirmation_h6.py','protocol/CONFIRMATION-H6-ADMISSION.json','grades/root-review/H6-ASTRA-REPLAY.json','grades/owner-review/astra-H6-FULL-GRADE.json','packets/primary/H6/prompt.md','packets/primary/H6/MANIFEST.json','FREEZE.json']
value={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cohort':'3freshAstraH6authorattempts','same_primary_packet':True,'models':['gpt-6-astra'],'condition':'minimal_reconstruction_with_metadata','files':{p:hashlib.sha256((root/p).read_bytes()).hexdigest()for p in paths}}
target=root/'CONFIRMATION-H6-FREEZE.json'
if target.exists():raise SystemExit('Refusing overwrite')
target.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'frozen_files':len(paths)}))
