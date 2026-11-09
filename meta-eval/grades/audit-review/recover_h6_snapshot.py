"""Capture stopped H6draw1 snapshot while retaining unknown native terminal state."""
import hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'runs/confirmation/gpt-6-astra/H6/draw1'
def inv(root):
    values={}
    for p in root.rglob('*'):
        key=p.relative_to(root).as_posix()
        if p.is_symlink():values[key]={'symlink':str(p.readlink())}
        elif p.is_file():values[key]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    return values
launch=json.loads((OUT/'launch.json').read_text());pid=launch['pid']
process=subprocess.run(['/mnt/c/Windows/System32/tasklist.exe','/FI',f'PID eq {pid}','/FO','CSV','/NH'],capture_output=True,text=True)
assert f'"{pid}"'not in process.stdout,'Native actor still exists'
windows=launch['workspace'];source=Path('/mnt/'+windows[0].lower()+windows[2:].replace('\\','/'))
before=inv(source);time.sleep(2);stable=inv(source);assert before==stable,'Snapshot still changing; no recovery claim'
partial=OUT/'delivery';retained=OUT/'delivery-capture-fault'
assert OUT.is_relative_to(ROOT/'runs')
if partial.exists():
    assert not retained.exists(),'Prior capture already retained; inspect without overwriting'
    partial.rename(retained)
shutil.copytree(source,partial,symlinks=True)
actual=inv(partial);assert actual==stable and inv(source)==stable
events=[json.loads(line)for line in(OUT/'transcript.jsonl').read_text().splitlines()]
completed=any(e.get('type')=='turn.completed'for e in events)
failed=any(e.get('type')=='turn.failed'for e in events)
receipt={'schema_version':'eval-author-stopped-snapshot-recovery/v1','model_calls':0,
         'native_pid_absent':True,'native_pid_probe':{'stdout':process.stdout,'exit_code':process.returncode},
         'native_turn_completed_event':completed,'native_turn_failed_event':failed,
         'native_final_present':(OUT/'final.txt').exists(),'native_exit_code':'not_persisted',
         'native_terminal_status':'unknown_no_terminal_event'if not completed and not failed else('completed'if completed else'failed'),
         'delivery_custody_verified':True,'source_two_observations_stable':True,'source_unchanged_after_copy':True,
         'partial_capture_retained':str(retained),'original_launch_and_runtime_error_preserved':True,
         'recovered_status':'captured_snapshot_native_terminal_unknown'if not completed else'transport_completed_delivery_recovered',
         'inventory':actual,'scoring_eligibility':'incomplete_or_unknown_native_turn; artifact diagnostics only until independently adjudicated'}
(OUT/'RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'files':len(actual),'native_terminal_status':receipt['native_terminal_status'],'custody':True,'model_calls':0}))
