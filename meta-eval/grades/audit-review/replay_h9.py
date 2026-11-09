"""Replay immutable H9 accounting programs after no-model transport recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

ROOT=Path(__file__).resolve().parents[2]
def inv(root):return{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in root.rglob('*')if p.is_file()and not p.is_symlink()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--models',nargs='+',default=['gpt-6.1-sol','gpt-6-astra']);a=p.parse_args();rows=[]
    for model in a.models:
        out=ROOT/'runs/screen'/model/'H9';recovery=json.loads((out/'RECOVERY.json').read_text())
        assert recovery['delivery_custody_verified']and recovery['native_turn_completed_event']
        delivery=out/'delivery';before=inv(delivery)
        if any(p.is_symlink()for p in delivery.rglob('*')):raise ValueError('symlink requires review')
        name='h9check-'+uuid.uuid4().hex
        artifact='audit-summary.json'if model=='gpt-6.1-sol'else'audit_evidence.json'
        expected=json.loads((delivery/artifact).read_text())
        with tempfile.TemporaryDirectory(prefix='h9-independent-')as temp:
            work=Path(temp)/'subject';shutil.copytree(delivery,work,ignore=shutil.ignore_patterns('__pycache__'))
            work.chmod(0o777)
            for path in work.rglob('*'):path.chmod(0o777 if path.is_dir()else 0o666)
            (work/artifact).unlink() # Require newly generated evidence, not the copied historical output.
            command=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
                     '--memory','256m','--cpus','1','--pids-limit','64','--tmpfs','/tmp:rw,nosuid,size=32m',
                     '--mount',f'type=bind,source={work},target=/subject','-w','/subject','python:3.14-slim','python','-B','audit_round10.py']
            try:
                result=subprocess.run(command,capture_output=True,text=True,timeout=90)
                reproduced=json.loads((work/artifact).read_text())if(work/artifact).exists()else None
                rows.append({'model':model,'exit_code':result.returncode,'command':command,'stdout':result.stdout,'stderr':result.stderr,
                             'generated_json_semantically_matches':reproduced==expected,'recorded_counts':reproduced.get('counts'),
                             'original_delivery_unchanged':before==inv(delivery),'model_calls':0})
            except subprocess.TimeoutExpired:
                subprocess.run(['docker','rm','-f',name],capture_output=True);rows.append({'model':model,'status':'owner_timeout','model_calls':0})
    receipt={'schema_version':'h9-independent-replay/v1','model_calls':0,'checks':rows,
             'scope':'Reproduce stored packet accounting; historical code/graders not re-executed, research prose separately reviewed.'}
    (ROOT/'grades/audit-review/H9-INDEPENDENT-REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps([{k:r.get(k)for k in ['model','exit_code','generated_json_semantically_matches','original_delivery_unchanged']}for r in rows]))
if __name__=='__main__':main()
