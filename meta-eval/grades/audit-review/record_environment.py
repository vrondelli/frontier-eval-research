"""Record only selected reproducibility properties; never dump environment/auth."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess

ROOT=Path(__file__).resolve().parents[2]
launch=json.loads((ROOT/'runs/screen/gpt-6.1-sol/H1/launch.json').read_text())
def call(command):
    r=subprocess.run(command,capture_output=True,text=True,timeout=30)
    return {'command':command,'exit_code':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()}
cli=launch['command'][0]
report={'schema_version':'eval-author-environment/v1','model_calls':0,
        'author_python_executable':launch['python_executable'],
        'author_python_reported':launch['python_runtime'],
        'author_python_actual':call([launch['python_executable'],'--version']),
        'codex_cli':call([cli,'--version']),
        'codex_binary_sha256':hashlib.sha256(Path(cli).read_bytes()).hexdigest(),
        'host_platform':platform.platform(),
        'machine':platform.machine(),
        'linux_python':call(['wsl.exe','--distribution','Ubuntu-26.04','--user','vlad_','--exec','python3','--version']),
        'docker_image':call(['wsl.exe','--distribution','Ubuntu-26.04','--user','vlad_','--exec','docker','image','inspect','python:3.12-slim','--format','{{json .RepoDigests}} {{.Id}}']),
        'docker_python314_image':call(['wsl.exe','--distribution','Ubuntu-26.04','--user','vlad_','--exec','docker','image','inspect','python:3.14-slim','--format','{{json .RepoDigests}} {{.Id}}']),
        'model_weight_identity':'not independently pinned; requested aliases saved per launch',
        'generation_sandbox':'Windows native MXC workspace-write; scoped UNC read-denial probe recorded separately',
        'owner_execution':'Docker no network, read-only root, no capabilities, no privilege escalation,256MiB,1CPU,64PIDlimit'}
(ROOT/'grades/audit-review/ENVIRONMENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'python':report['author_python_actual']['stdout'],'codex':report['codex_cli']['stdout'],'docker':report['docker_image']['stdout']}))
