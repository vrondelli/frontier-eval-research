#!/usr/bin/env python3
"""Eval-author runtime. Added grade.py adapter is not historical prompt replay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent

def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def inventory(path):
    path = Path(path)
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and not p.is_symlink()}

def execute(command, cwd, timeout, stdin=None):
    started = time.time()
    proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                            errors='replace', start_new_session=os.name != 'nt')
    status = 'completed'
    try:
        stdout, stderr = proc.communicate(stdin, timeout=timeout)
    except subprocess.TimeoutExpired:
        status = 'timeout'
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    return {'command': command, 'cwd': str(cwd), 'status': status, 'exit_code': proc.returncode,
            'seconds': time.time() - started, 'stdout': stdout, 'stderr': stderr}

def manifests():
    values = []
    for path in [ROOT/'owner/cases/manifest.json', ROOT/'owner/audit_cases/manifest.json']:
        if path.exists():
            document = json.loads(path.read_text(encoding='utf-8'))
            for case in document['cases']:
                values.append((path, case))
    return values

def control_path(manifest, value):
    p = Path(value)
    if p.is_absolute():
        return p
    options = [ROOT/p, manifest.parent/p]
    return next((v.resolve() for v in options if v.exists()), options[0].resolve())

def materialize(value, destination):
    """Owner-side representation conversion only; never repairs candidate code."""
    destination.mkdir()
    def put(name, content):
        target=(destination/name).resolve()
        if not target.is_relative_to(destination.resolve()):
            raise ValueError('control asset escapes candidate directory')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content,encoding='utf-8')
    case=value['case_id']
    if case=='H1':
        put('service.py',value['code'])
        put('answer.json',json.dumps({'task_id':'E1','code':value['code']}))
    elif case=='H6': put('summarize.py',value['code'])
    elif case=='H4':
        put('test_fares.py',value['test_code'])
        for name,content in value['assets'].items(): put(name,content)
    elif case=='H5':
        for name,content in value['files'].items(): put(name,content)
    elif case=='H7':
        put('request.json',json.dumps(value['request']))
        put('report.txt',value['report'])
        put('extraction.json',json.dumps(value['extraction']))
    else:
        put('input.json',json.dumps(value.get('input',{})))
        put('report.json',json.dumps(value.get('candidate_response',{})))
    for entry in destination.rglob('*'):
        entry.chmod(0o755 if entry.is_dir() else 0o644)
    destination.chmod(0o755)
    return destination

def prepare(args):
    source, destination = Path(args.packet).resolve(), Path(args.workspace).resolve()
    if destination.exists():
        raise ValueError('workspace must be new; existing workspace is not overwritten')
    if source == ROOT or (source.is_relative_to(ROOT) and 'owner' in source.relative_to(ROOT).parts):
        raise ValueError('refusing owner/package root as actor input')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('input packet must not contain symlinks')
    shutil.copytree(source, destination)
    dump(args.receipt, {'kind':'source_only_workspace', 'source':str(source), 'workspace':str(destination),
                        'files':inventory(destination), 'condition':'adapter_added_unless_proven_otherwise',
                        'generation_filesystem_isolation':'not_proven_by_copy'})

def launch(args):
    workspace = Path(args.workspace).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    prompt = Path(args.prompt).read_text(encoding='utf-8')
    executable = args.codex or shutil.which('codex.exe') or shutil.which('codex') or 'codex'
    command = [executable, 'exec', '--skip-git-repo-check', '--sandbox', 'workspace-write',
               '-m', args.model, '-c', 'model_reasoning_effort="high"', '--json',
               '-o', str(output/'final.txt'), '-']
    if os.name == 'nt':
        command[2:2] = ['-c', 'windows.sandbox=mxc']
    receipt = {'kind':'native_author_attempt', 'model_requested':args.model,
               'condition':args.condition, 'command':command, 'workspace':str(workspace),
               'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
               'before':inventory(workspace), 'executed':args.execute,
               'generation_filesystem_isolation':'not_independently_qualified'}
    if args.execute:
        result = execute(command, workspace, args.timeout, prompt)
        (output/'transcript.jsonl').write_text(result.pop('stdout'), encoding='utf-8')
        (output/'stderr.txt').write_text(result.pop('stderr'), encoding='utf-8')
        receipt.update(result)
        receipt['after'] = inventory(workspace)
    dump(output/'launch.json', receipt)
    print(json.dumps({'executed':args.execute, 'receipt':str(output/'launch.json')}))

def score(args):
    package = Path(args.package).resolve()
    if any(p.is_symlink() for p in package.rglob('*')):
        raise ValueError('delivered package symlinks require explicit owner review; refusing implicit dereference')
    adapter = json.loads(Path(args.adapter).read_text(encoding='utf-8')) if args.adapter else None
    if not adapter and not (package/'grade.py').is_file():
        dump(args.output, {'status':'unknown_adapter_required','formal_eligible':False,
                           'reason':'Owner must map the immutable delivered grader CLI; no subject change required.'})
        return 2
    if not args.docker_image and not args.allow_unisolated_diagnostic:
        dump(args.output, {'status':'unqualified', 'reason':'No isolated execution backend supplied',
                           'formal_eligible':False, 'executed':False})
        print('Unqualified: use --docker-image for isolated grading; diagnostic bypass is ineligible.')
        return 2
    rows = []
    before = inventory(package)
    for manifest, case in manifests():
        if args.case and case['case_id'] != args.case:
            continue
        for control in case['controls']:
            source = control_path(manifest, control['path'])
            artifact = control_path(manifest, control['artifact_dir']) if control.get('artifact_dir') else None
            with tempfile.TemporaryDirectory(prefix='eval-author-score-') as folder:
                temp = Path(folder)
                actor = temp/'subject'
                shutil.copytree(package, actor, symlinks=False)
                # Only the disposable mount copy changes mode; source artifacts stay immutable.
                actor.chmod(0o755)
                for entry in actor.rglob('*'):
                    entry.chmod(0o755 if entry.is_dir() else 0o644)
                casefile = temp/'case.json'
                shutil.copy2(source, casefile)
                casefile.chmod(0o644)
                if artifact is None and adapter is not None:
                    artifact=materialize(json.loads(source.read_text(encoding='utf-8')),temp/'candidate')
                if args.docker_image:
                    container_name='eval-author-'+uuid.uuid4().hex
                    command = ['docker', 'run', '--rm', '--name',container_name,'--network', 'none', '--read-only',
                               '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                               '--pids-limit', '64', '--memory', '256m', '--cpus', '1',
                               '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
                               '--mount', f'type=bind,source={actor},target=/subject,readonly',
                               '--mount', f'type=bind,source={casefile},target=/input/case.json,readonly']
                    if artifact:
                        command += ['--mount',f'type=bind,source={artifact},target=/candidate,readonly']
                    template=adapter['command'] if adapter else ['python','grade.py','{case_file}']
                    values={'case_file':'/input/case.json','candidate_dir':'/candidate' if artifact else '/input',
                            'package_dir':'/subject'}
                    command += ['-w','/subject',args.docker_image] + [s.format(**values) for s in template]
                else:
                    template=adapter['command'] if adapter else [sys.executable,'grade.py','{case_file}']
                    values={'case_file':str(casefile),'candidate_dir':str(artifact or casefile.parent),
                            'package_dir':str(actor)}
                    command=[s.format(**values) for s in template]
                result = execute(command, actor, args.timeout)
                if args.docker_image and result['status']=='timeout':
                    cleanup=subprocess.run(['docker','rm','-f',container_name],capture_output=True,text=True)
                    result['container_timeout_cleanup_exit']=cleanup.returncode
            verdict, error = None, None
            try:
                if adapter and adapter.get('verdict_source')=='exit_code':
                    if result['exit_code'] not in [0,1]: raise ValueError('grader exit is neither pass0 nor fail1')
                    verdict=result['exit_code']==0
                else:
                    decoded = json.loads(result['stdout'])
                    key=adapter.get('pass_key','pass') if adapter else 'pass'
                    if type(decoded.get(key)) is not bool:
                        raise ValueError('verdict field must be a JSON boolean')
                    verdict = decoded[key]
            except (ValueError, TypeError) as exc:
                error = str(exc)
            expected = control['expected_pass']
            valid = result['status'] == 'completed' and error is None and (result['exit_code'] in [0,1]
                     if adapter and adapter.get('verdict_source')=='exit_code' else result['exit_code']==0)
            rows.append({'case_id':case['case_id'], 'control':str(source.relative_to(ROOT)),
                         'control_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                         'expected_pass':expected, 'actual_pass':verdict, 'valid':valid,
                         'correct':valid and verdict == expected, 'parse_error':error, **result})
    if not rows:
        raise ValueError('no controls selected')
    result = {'status':'scored', 'adapter_condition':not bool(adapter),
              'owner_cli_mapping':adapter,
              'formal_eligible':False,
              'formal_eligibility_reason':'Instruction provenance and human semantic review require separate qualification',
              'owner_bank_isolation':'docker_mount_boundary' if args.docker_image else 'unisolated_diagnostic',
              'nested_scored_candidate_isolation':'not_exercised_by_JSON_adapter',
              'package_before':before, 'package_unchanged':before == inventory(package),
              'checks':rows, 'total':len(rows), 'correct':sum(x['correct'] for x in rows),
              'false_accepts':sum(x['valid'] and x['actual_pass'] and not x['expected_pass'] for x in rows),
              'false_rejects':sum(x['valid'] and not x['actual_pass'] and x['expected_pass'] for x in rows),
              'invalid':sum(not x['valid'] for x in rows)}
    dump(args.output, result)
    print(json.dumps({k:result[k] for k in ['total','correct','false_accepts','false_rejects','invalid','formal_eligible']}))
    return 0 if result['correct'] == result['total'] else 1

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--packet', required=True); p.add_argument('--workspace', required=True)
    p.add_argument('--receipt', required=True); p.set_defaults(function=prepare)
    p = commands.add_parser('launch')
    p.add_argument('--workspace', required=True); p.add_argument('--prompt', required=True)
    p.add_argument('--model', required=True); p.add_argument('--condition', required=True)
    p.add_argument('--output', required=True); p.add_argument('--codex')
    p.add_argument('--timeout', type=int, default=600); p.add_argument('--execute', action='store_true')
    p.set_defaults(function=launch)
    p = commands.add_parser('score')
    p.add_argument('--package', required=True); p.add_argument('--case'); p.add_argument('--output', required=True)
    p.add_argument('--timeout', type=int, default=20); p.add_argument('--docker-image')
    p.add_argument('--adapter',help='Owner CLI mapping created after immutable delivery, never shown to author')
    p.add_argument('--allow-unisolated-diagnostic', action='store_true'); p.set_defaults(function=score)
    args = parser.parse_args()
    return args.function(args) or 0

if __name__ == '__main__':
    raise SystemExit(main())
