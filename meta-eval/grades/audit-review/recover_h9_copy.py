"""Recover stopped H9 actor files after Windows MAXPATH copy fault; no generation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def inv(root):
    result={}
    for p in root.rglob('*'):
        relative=p.relative_to(root).as_posix()
        if p.is_symlink():result[relative]={'symlink':str(p.readlink())}
        elif p.is_file():result[relative]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    return result
rows=[]
for model in ['gpt-6.1-sol','gpt-6-astra']:
    out=ROOT/'runs/screen'/model/'H9'
    launch=json.loads((out/'launch.json').read_text())
    error=json.loads((out/'runtime-error.json').read_text())
    pid=launch['pid']
    check=subprocess.run(['/mnt/c/Windows/System32/tasklist.exe','/FI',f'PID eq {pid}','/FO','CSV','/NH'],capture_output=True,text=True)
    if f'"{pid}"'in check.stdout:raise RuntimeError('Original actor process still exists; refusing recovery')
    windows=launch['workspace'];source=Path('/mnt/'+windows[0].lower()+windows[2:].replace('\\','/'))
    transcript=out/'transcript.jsonl'
    events=[json.loads(line)for line in transcript.read_text().splitlines()]
    turn_completed=any(e.get('type')=='turn.completed'for e in events)
    before=inv(source)
    shutil.copytree(source,out/'delivery',dirs_exist_ok=True,symlinks=True)
    after=inv(out/'delivery')
    if before!=after:raise RuntimeError('Recovered delivery inventory mismatch')
    if before!=inv(source):raise RuntimeError('Actor workspace changed during recovery')
    record={'schema_version':'eval-author-copy-recovery/v1','model_calls':0,'model':model,'case_id':'H9',
            'raw_runtime_error_retained':str(out/'runtime-error.json'),'raw_error':error.get('runtime_error',error.get('error')),
            'actor_pid':pid,'actor_pid_absence_probe':{'exit_code':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
            'native_turn_completed_event':turn_completed,'native_exit_code':'not_persisted_before_copy_fault',
            'native_final_present':(out/'final.txt').is_file(),'native_final_sha256':hashlib.sha256((out/'final.txt').read_bytes()).hexdigest(),
            'source_workspace':str(source),'recovered_delivery_files':len(after),'inventory':after,
            'source_unchanged':True,'delivery_custody_verified':True,
            'recovered_status':'transport_completed_delivery_recovered'if turn_completed else'unknown_native_terminal_delivery_recovered'}
    (out/'RECOVERY.json').write_text(json.dumps(record,indent=2)+'\n')
    rows.append({'model':model,'files':len(after),'turn_completed':turn_completed,'custody':True})
print(json.dumps(rows))
