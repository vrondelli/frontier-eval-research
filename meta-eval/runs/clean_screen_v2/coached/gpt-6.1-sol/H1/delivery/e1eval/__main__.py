import argparse
import hashlib
import json
from pathlib import Path
import sys

from .grader import base_report, grade
from .schema import validate_report


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_answer(path):
    raw = Path(path).read_bytes()
    if len(raw) > 1048576:
        raise ValueError('Answer file exceeds 1 MiB')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=strict_object,
                      parse_constant=lambda text: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + text)))


def write(value, path):
    text = json.dumps(value, indent=2, allow_nan=False) + '\n'
    if path:
        Path(path).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)


def main():
    parser = argparse.ArgumentParser(description='E1 standalone ledger admission evaluation')
    commands = parser.add_subparsers(dest='command', required=True)
    grading = commands.add_parser('grade', help='Grade an untrusted JSON submission; requires Linux isolation')
    grading.add_argument('answer')
    grading.add_argument('--output')
    controls = commands.add_parser('verify', help='Verify repository-authored controls ONLY')
    controls.add_argument('--sandbox', action='store_true', help='Also require real Linux sandbox execution')
    controls.add_argument('--output')
    reference = commands.add_parser('reference', help='Export evaluator-only authored reference answer')
    reference.add_argument('--output')
    schema = commands.add_parser('validate-report')
    schema.add_argument('report')
    args = parser.parse_args()
    if args.command == 'grade':
        try:
            answer = load_answer(args.answer)
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            report = base_report({'unparsed_input': str(args.answer)}, 'linux_bwrap')
            report['diagnostics'].append(type(error).__name__ + ': ' + str(error))
        else:
            try:
                report = grade(answer)
            except Exception as error:
                report = base_report(answer, 'linux_bwrap')
                report.update(status='internal_error', overall_status='internal_error')
                report['diagnostics'].append(type(error).__name__ + ': ' + str(error))
        validate_report(report)
        write(report, args.output)
        return 0 if report['status'] == 'pass' else 2
    if args.command == 'verify':
        from .verify import verify
        report = verify(args.sandbox)
        write(report, args.output)
        return 0 if report['verified'] else 2
    if args.command == 'reference':
        from .controls import reference_answer
        write(reference_answer(), args.output)
        return 0
    if args.command == 'validate-report':
        validate_report(load_answer(args.report))
        print('Report valid')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
