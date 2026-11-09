"""Validate the grader with acceptance checks and actual CLI controls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from cases import Case, build_cases
from evaluate import check_output, run_suite
from numbers_exact import Number, loads


def main():
    here = Path(__file__).resolve().parent
    cases = build_cases()
    by_name = {case.name: case for case in cases}
    summary = {'oracle_checks': 0, 'mutations': {}}

    def require(condition, message):
        if not condition:
            raise AssertionError(message)
        summary['oracle_checks'] += 1

    require(Number.parse('1') == Number.parse('1000e-3'), 'integral negative exponent')
    require(Number.parse('-0e-99999') == Number.parse('0'), 'signed zero')
    require(Number.parse('1e100000000000000000000') ==
            Number.parse('10e99999999999999999999'), 'arbitrary exponent comparison')
    require(not Number.parse('1e-400').integral, 'tiny fraction')
    require(not Number.parse('1.00000000000000000000000000001').integral, 'near integer')
    require(Number.parse('9007199254740993') != Number.parse('9007199254740992'), 'float boundary')
    require(Number.parse('1' + '0' * 6000) == Number.parse('1e6000'), 'digit limit')
    for text in ('{"x":1,"x":2}', '{"a":1,"\\u0061":2}', '[NaN]', '[Infinity]'):
        try:
            loads(text)
        except ValueError:
            require(True, 'strict JSON')
        else:
            require(False, 'strict JSON accepted ' + text)

    with tempfile.TemporaryDirectory(prefix='numeric evaluator self test ', dir=Path.cwd()) as directory:
        work = Path(directory)
        output = work / 'output.json'
        probe = Case('oracle', 'selftest', b'', {'x': '9007199254740993'})
        for token in ('9007199254740993', '9007199254740993.0', '90071992547409930e-1'):
            output.write_text('{"meta":{"fraction":0.25},"stock_reports":{"x":' + token + '}}', encoding='utf-8')
            require(check_output(probe, 0, output) is None, 'equivalent number encoding')
        for content in ('{"stock_reports":{"x":9007199254740992}}',
                        '{"stock_reports":{"x":"9007199254740993"}}',
                        '{"stock_reports":{"x":true}}',
                        '{"stock_reports":{"x":9007199254740993.1}}',
                        '{"stock_reports":{}}',
                        '{"stock_reports":{"x":9007199254740993,"extra":1}}',
                        '{"stock_reports":{"x":NaN}}',
                        '{"stock_reports":{"x":9007199254740993,"x":9007199254740993}}',
                        '[]', '{'):
            output.write_text(content, encoding='utf-8')
            require(check_output(probe, 0, output) is not None, 'bad result accepted')
        invalid = Case('invalid', 'selftest', b'', None)
        for content in ('{"stock_reports":{}}', '{"stock_reports":{"x":1}}'):
            output.write_text(content, encoding='utf-8')
            require(check_output(invalid, 1, output) is not None, 'failure emitted results')
        output.write_text('{"error":"bad input"}', encoding='utf-8')
        require(check_output(invalid, 1, output) is None, 'error envelope')
        require(check_output(invalid, 0, output) is not None, 'zero exit on invalid')
        output.unlink()
        require(check_output(invalid, 1, output) is None, 'absent failure result')
        require(check_output(probe, 0, output) is not None, 'missing valid result')

        # Exercise the evaluator's real command interface, not just internal helpers.
        wrapper = work / 'summarize.py'
        wrapper.write_text('import runpy, sys\nsys.argv.insert(1, "correct")\nrunpy.run_path(' +
                           repr(str(here / 'control_cli.py')) + ', run_name="__main__")\n', encoding='utf-8')
        report_path = work / 'positive-report.json'
        invocation = [sys.executable, str(here / 'evaluate.py'), '--candidate', str(wrapper),
                      '--report', str(report_path)]
        process = subprocess.run(invocation, capture_output=True, text=True, timeout=120)
        if process.returncode != 0:
            raise AssertionError('positive CLI control failed:\n' + process.stdout + process.stderr)
        positive = json.loads(report_path.read_text(encoding='utf-8'))
        require(positive['all_passed'], 'positive control')
        summary['positive_control'] = {key: positive[key] for key in ('passed', 'total', 'categories')}
        (here / 'positive-control-report.json').write_text(json.dumps(positive, indent=2) + '\n', encoding='utf-8')

        witnesses = {
            'float': ['binary64_boundary', 'cancellation_and_order', 'beyond_float_range'],
            'booleans': ['net_units_true', 'event_count_false', 'largest_adjustment_true'],
            'duplicates': ['duplicate_root', 'duplicate_identifier', 'escaped_duplicate_identifier', 'duplicate_turns'],
            'reject_decimals': ['integral_number_encodings', 'binary64_boundary'],
            'dedup': ['identities_and_repetitions', 'long_array'],
            'max_zero': ['identities_and_repetitions', 'cancellation_and_order'],
            'count_without_validation': ['event_count_fraction', 'event_count_true', 'event_count_string'],
            'partial_failure': ['empty_max', 'net_units_fraction', 'duplicate_identifier'],
        }
        for mode, names in witnesses.items():
            report = run_suite([sys.executable, str(here / 'control_cli.py'), mode], here,
                               cases=[by_name[name] for name in names])
            failed = [case['name'] for case in report['cases'] if not case['passed']]
            require(set(failed) == set(names), f'mutation {mode} escaped a witness: {report}')
            summary['mutations'][mode] = {'detected': True, 'failed_cases': failed}

        sleeper = work / 'sleep.py'
        sleeper.write_text('import time\ntime.sleep(2)\n', encoding='utf-8')
        report = run_suite([sys.executable, str(sleeper)], work, [cases[0]], timeout=0.1)
        require(not report['all_passed'] and 'timeout' in report['cases'][0]['reason'], 'timeout handling')
        report = run_suite([str(work / 'missing-executable')], work, [cases[0]])
        require(not report['all_passed'] and 'could not run' in report['cases'][0]['reason'], 'launch failure')

    summary['all_passed'] = True
    (here / 'selftest-report.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
