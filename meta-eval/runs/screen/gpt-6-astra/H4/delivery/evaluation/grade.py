"""Evaluate a submission directory without changing the supplied task fixture."""
import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from cases import build_cases

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROTECTED = ('farelib.pyc', 'farelib.pyi', 'README.md', 'TESTING.md')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def audit(candidate):
    original = ROOT / 'input' / 'workspace'
    checks = {name: digest(candidate / name) == digest(original / name) for name in PROTECTED}
    issues = []
    imports = {}
    for name in ('fares.py', 'test_fares.py'):
        path = candidate / name
        if not path.is_file():
            issues.append(f'Missing deliverable: {name}')
            continue
        try:
            tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=name)
        except (SyntaxError, UnicodeError) as exc:
            issues.append(f'{name}: {exc}')
            continue
        imports[name] = []
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or '']
            elif isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant):
                if ((isinstance(node.func, ast.Name) and node.func.id == '__import__') or
                    (isinstance(node.func, ast.Attribute) and node.func.attr == 'import_module')):
                    if isinstance(node.args[0].value, str):
                        names = [node.args[0].value]
            imports[name].extend(names)
        if name == 'test_fares.py' and any(x.split('.')[0] == 'farelib' for x in imports[name]):
            issues.append('test_fares.py imports farelib, contrary to TESTING.md')
    return dict(protected_files=checks, issues=issues, imports=imports,
                passed=all(checks.values()) and not issues)


def child(command, cwd, timeout, report_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    try:
        completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                   text=True, encoding='utf-8', errors='replace', timeout=timeout)
        report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
        return dict(report, exit_code=completed.returncode,
                    passed=report.get('passed', False) and completed.returncode == 0,
                    stdout=completed.stdout[-12000:], stderr=completed.stderr[-12000:])
    except subprocess.TimeoutExpired:
        return dict(passed=False, timeout_seconds=timeout)
    except (OSError, ValueError) as exc:
        return dict(passed=False, runner_error=f'{type(exc).__name__}: {exc}')


def evaluate(candidate, timeout=30):
    candidate = Path(candidate).resolve()
    if not candidate.is_dir():
        return dict(automated_pass=False, error='Candidate directory does not exist')
    checks = audit(candidate)
    cases = build_cases()
    with tempfile.TemporaryDirectory(prefix='.ferry-eval-', dir=HERE) as temporary:
        temp = Path(temporary)
        assert temp.resolve().is_relative_to(HERE)
        behavior = child([sys.executable, str(HERE / 'test_fares.py'), '--candidate', str(candidate),
                          '--report', str(temp / 'behavior.json')], candidate, timeout, temp / 'behavior.json')
        submitted = child([sys.executable, str(HERE / 'submission_tests.py'), str(candidate),
                           str(temp / 'submitted.json')], candidate, timeout, temp / 'submitted.json')
    after = audit(candidate)
    checks['after_execution'] = after
    checks['passed'] = checks['passed'] and after['passed']
    failures = {entry['test'].split(' ')[0].removeprefix('test_') for entry in behavior.get('failures', [])}
    ran_all = behavior.get('run') == len(cases) + 1
    coverage = {}
    for rule, count in sorted(Counter(case.rule for case in cases).items()):
        passed = sum(case.name not in failures for case in cases if case.rule == rule) if ran_all else 0
        coverage[rule] = dict(passed=passed, total=count)
    score = sum(v['passed'] / v['total'] for v in coverage.values()) / len(coverage)
    bytecode = candidate / 'farelib.pyc'
    library_magic = bytecode.read_bytes()[:4].hex() if bytecode.is_file() else None
    report = dict(
        schema_version='ferry-evaluation/v1', candidate=str(candidate),
        runtime=dict(python=sys.version, executable=sys.executable,
                     host_magic=importlib.util.MAGIC_NUMBER.hex(), library_magic=library_magic,
                     bytecode_compatible=library_magic == importlib.util.MAGIC_NUMBER.hex()),
        integrity=checks, behavior=behavior, submitted_tests=submitted,
        rule_coverage=coverage, behavioral_score=round(score, 6),
        automated_pass=checks['passed'] and behavior['passed'] and submitted['passed'],
        manual_review_required=[
            'Expected values in submitted tests come from independent business-rule reasoning/arithmetic, not recorded helper or solution output.',
            'Only standard library and the provided farelib are used, including dynamic imports and any local support modules.',
            'Tests contain meaningful assertions and do not bypass unittest or alter the implementation to make assertions pass.'
        ])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path, help='Directory containing fares.py, test_fares.py and original protected files')
    parser.add_argument('--report', type=Path, default=HERE / 'report.json')
    parser.add_argument('--timeout', type=float, default=30, help='Seconds per child process (default 30)')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    report = evaluate(args.candidate, args.timeout)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('automated_pass', 'behavioral_score', 'rule_coverage') if k in report}, indent=2))
    print(f'Report: {args.report.resolve()}')
    return 0 if report['automated_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
