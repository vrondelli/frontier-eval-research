"""Offline runtime qualification using trusted checker, never a model result."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='eval-runtime-isolated-') as temp:
    package=Path(temp)
    shutil.copy2(root/'owner/audit_cases/check.py',package/'grade.py')
    command=[sys.executable,str(root/'run_eval.py'),'score','--package',str(package),
             '--case','H8','--docker-image','python:3.12-slim',
             '--output',str(root/'owner/runtime/ISOLATED-SELF-CHECK.json')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=180)
    print(result.stdout,result.stderr)
    assert result.returncode==0
    receipt=json.loads((root/'owner/runtime/ISOLATED-SELF-CHECK.json').read_text())
    assert receipt['correct']==5 and receipt['package_unchanged']
