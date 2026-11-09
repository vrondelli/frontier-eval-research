"""Harmless deterministic Codex sandbox read-boundary probe; no model call."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT=Path(__file__).resolve().parents[2]
marker=uuid.uuid4().hex
sentinel=ROOT/'owner/runtime'/('sentinel-'+marker+'.txt')
sentinel.write_text(marker,encoding='utf-8')
workspace=Path(tempfile.mkdtemp(prefix='eval-generation-boundary-'))
probe=workspace/'probe.py'
probe.write_text('import json,pathlib\np=pathlib.Path('+repr(str(sentinel))+')\nr={}\ntry:\n r["owner_read"]=p.read_text()\nexcept Exception as e:\n r["owner_read_error"]=str(e)\ntry:\n pathlib.Path("workspace-write.txt").write_text("allowed")\n r["workspace_write"]=True\nexcept Exception as e:\n r["workspace_write_error"]=str(e)\nprint(json.dumps(r))\n',encoding='utf-8')
command=[shutil.which('codex.exe') or shutil.which('codex') or 'codex','sandbox','-P',':workspace','-C',str(workspace),
         '-c','windows.sandbox="mxc"','-c','sandbox_mode="workspace-write"',sys.executable,str(probe)]
try:
    result=subprocess.run(command,capture_output=True,text=True,timeout=45)
    receipt={'command':command,'workspace':str(workspace),'sentinel_sha256':hashlib.sha256(marker.encode()).hexdigest(),
             'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    try:
        answer=json.loads(result.stdout)
        receipt['owner_readable']=answer.get('owner_read')==marker
        receipt['workspace_writable']=answer.get('workspace_write') is True
        receipt['qualified_read_boundary']=receipt['workspace_writable'] and not receipt['owner_readable'] and 'owner_read_error' in answer
    except ValueError:
        receipt['qualified_read_boundary']=False
except subprocess.TimeoutExpired:
    receipt={'status':'probe_timeout','qualified_read_boundary':False,'workspace':str(workspace)}
finally:
    sentinel.unlink(missing_ok=True)
(ROOT/'owner/runtime/GENERATION-BOUNDARY-PROBE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
