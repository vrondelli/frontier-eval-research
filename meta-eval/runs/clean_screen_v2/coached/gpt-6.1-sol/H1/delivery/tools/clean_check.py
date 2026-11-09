"""Copy a minimal package into a new directory, then replay verification and CLI.

Run from repository root: python tools/clean_check.py
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='.e1-portable-', dir=ROOT) as directory:
        clean = Path(directory)
        shutil.copytree(ROOT / 'e1eval', clean / 'e1eval', ignore=shutil.ignore_patterns('__pycache__'))
        for name in ['README.md', 'TASK.md', 'REVIEW-RUBRIC.md', 'CONTROLS.md']:
            shutil.copy2(ROOT / name, clean / name)
        verification = subprocess.run([sys.executable, '-m', 'e1eval', 'verify', '--output', 'verification.json'],
                                      cwd=clean, capture_output=True, text=True, timeout=300)
        export = subprocess.run([sys.executable, '-m', 'e1eval', 'reference', '--output', 'answer.json'],
                                cwd=clean, capture_output=True, text=True, timeout=10)
        grading = subprocess.run([sys.executable, '-m', 'e1eval', 'grade', 'answer.json', '--output', 'report.json'],
                                 cwd=clean, capture_output=True, text=True, timeout=120)
        validation = subprocess.run([sys.executable, '-m', 'e1eval', 'validate-report', 'report.json'],
                                    cwd=clean, capture_output=True, text=True, timeout=10)
        verified = json.loads((clean / 'verification.json').read_text(encoding='utf-8'))
        report = json.loads((clean / 'report.json').read_text(encoding='utf-8'))
        result = {'schema_version': 'e1-clean-replay/v1',
                  'passed': verification.returncode == export.returncode == validation.returncode == 0
                            and grading.returncode == (0 if report['status'] == 'pass' else 2)
                            and report['status'] in ('pass', 'unavailable'),
                  'verification': verified, 'grade_report': report,
                  'commands': [{'name': name, 'exit_code': process.returncode, 'stdout': process.stdout,
                                'stderr': process.stderr} for name, process in
                               [('verify', verification), ('reference', export), ('grade', grading), ('validate', validation)]],
                  'input_sha256': {name: hashlib.sha256((ROOT / 'input' / name).read_bytes()).hexdigest()
                                   for name in ['E1.md', 'README.md']}}
        (ROOT / 'clean-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'passed': result['passed'], 'sandbox_status': report['status'],
                          'unit_tests': verified['unit_tests']['run'], 'controls': len(verified['controls'])}))
        return 0 if result['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
