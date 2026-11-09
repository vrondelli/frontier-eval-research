"""Independent isolated replay of both immutable H8 auditors and fresh defects."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

ROOT=Path(__file__).resolve().parents[2]
MODELS={'gpt-6.1-sol':'audit_sessions.py','gpt-6-astra':'audit_architecture.py'}
def inventory(path):return{p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in path.rglob('*')if p.is_file()and not p.is_symlink()}
rows=[]
for model,script in MODELS.items():
    delivery=ROOT/'runs/screen'/model/'H8/delivery'
    before=inventory(delivery)
    for kind in ['original_packet','drop_last_direct_R2_stage','alter_manifest_whitespace']:
        with tempfile.TemporaryDirectory(prefix='h8-independent-')as temp:
            work=Path(temp)/'subject';shutil.copytree(delivery,work,ignore=shutil.ignore_patterns('__pycache__'))
            layout=json.loads((work/'input/snapshot-layout.json').read_text())['source_layout']
            stage=sorted(x['root']for x in layout if x['root'].startswith('runs/R2-')and '/stages/'in x['root'])[-1]
            target=work/'input'/stage/'manifest.json'
            if kind=='drop_last_direct_R2_stage':target.unlink()
            if kind=='alter_manifest_whitespace':target.write_bytes(target.read_bytes()+b'\n ')
            work.chmod(0o755)
            for p in work.rglob('*'):p.chmod(0o755 if p.is_dir()else 0o644)
            name='h8check-'+uuid.uuid4().hex
            command=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL',
                     '--security-opt','no-new-privileges','--memory','256m','--cpus','1','--pids-limit','64',
                     '--tmpfs','/tmp:rw,nosuid,size=64m','--mount',f'type=bind,source={work},target=/subject,readonly',
                     '-w','/subject','python:3.14-slim','python','-B',script,'--input','input','--output','/tmp/check']
            try:
                result=subprocess.run(command,capture_output=True,text=True,timeout=60)
                row={'model':model,'control':kind,'modified_relative_path':str(target.relative_to(work))if kind!='original_packet'else None,
                     'expected_exit':0 if kind=='original_packet'else 1,'exit_code':result.returncode,
                     'stdout':result.stdout,'stderr':result.stderr,'command':command}
                row['concordant']=row['exit_code']==row['expected_exit']
            except subprocess.TimeoutExpired:
                subprocess.run(['docker','rm','-f',name],capture_output=True)
                row={'model':model,'control':kind,'status':'owner_timeout','concordant':False}
            rows.append(row)
    assert before==inventory(delivery),'original delivery changed'
report={'schema_version':'h8-independent-replay/v1','model_calls':0,'original_deliveries_unchanged':True,
        'checks':rows,'concordant':sum(r['concordant']for r in rows),'total':len(rows),
        'scope':'Supplied packet accounting and two independent omission/hash defects, not universal auditor correctness or workspace-body integrity.'}
(ROOT/'grades/audit-review/H8-INDEPENDENT-REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'total':len(rows),'concordant':report['concordant']}))
