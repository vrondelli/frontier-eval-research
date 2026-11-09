"""Admission contract grading against independent serial histories and SQL state."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from .oracle import Model, serial_outcomes
from .runner import Unavailable, WorkerFailure, inspect, require_sandbox, run_batch, storage_fault

TOPICS = ['atomic_boundary', 'global_identity', 'unknown_outcome_replay',
          'contention_vs_cycles', 'cross_account_parallelism', 'first_mitigation',
          'rollback_trigger', 'deployment_tradeoffs']


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def same(a, b):
    return canonical(a) == canonical(b)


def valid_reply(envelope):
    if type(envelope) is not dict or set(envelope) != {'kind', 'value'} or envelope['kind'] != 'reply':
        return False
    reply = envelope['value']
    return (type(reply) is dict and set(reply) == {'status', 'remaining'} and
            reply['status'] in ('accepted', 'rejected', 'payload_mismatch') and
            (reply['remaining'] is None if reply['status'] == 'payload_mismatch'
             else type(reply['remaining']) is int and reply['remaining'] >= 0))


def request(key, account='A', amount=1):
    return {'key': key, 'account': account, 'amount': amount}


def storage_error(envelope):
    raised = (type(envelope) is dict and set(envelope) == {'kind', 'type'} and
              envelope['kind'] == 'error' and type(envelope['type']) is str)
    returned = same(envelope, {'kind': 'reply', 'value': {'status': 'error', 'remaining': None}})
    return raised or returned


def batches():
    return [
        ('overlap', [request('x', amount=60), request('y', amount=60)]),
        ('replay_x', [request('x', amount=60)]),
        ('replay_y', [request('y', amount=60)]),
        ('mismatch_account', [request('x', 'B', 60)]),
        ('mismatch_amount', [request('y', amount=61)]),
        ('account_B', [request('b', 'B', 100)]),
        ('rejection_B', [request('reject', 'B', 1)]),
        ('replay_rejection_B', [request('reject', 'B', 1)]),
        ('advance_A', [request('advance', amount=10)]),
        ('historical_x', [request('x', amount=60)]),
        ('historical_y', [request('y', amount=60)]),
        ('duplicate_overlap', [request('duplicate', amount=10)] * 2),
        ('conflicting_overlap', [request('conflict', 'A', 1), request('conflict', 'B', 1)]),
        ('conflict_replay_A', [request('conflict', 'A', 1)]),
        ('conflict_replay_B', [request('conflict', 'B', 1)]),
    ]


def base_report(answer, mode):
    return {'schema_version': 'e1-report/v1', 'task_id': 'E1',
            'submission_sha256': hashlib.sha256(canonical(answer).encode()).hexdigest(),
            'status': 'invalid', 'formal_status': 'not_run', 'overall_status': 'invalid',
            'isolation': mode, 'checks': [], 'trials': [], 'diagnostics': [],
            'explanation_review': {'status': 'pending', 'criteria': TOPICS,
                                   'unresolved_claims': [], 'quality_scored': False}}


def grade(answer, *, _trusted_control=False):
    """Private switch is used only by verification of authored controls."""
    mode = 'trusted_control' if _trusted_control else 'linux_bwrap'
    report = base_report(answer, mode)
    if type(answer) is not dict or answer.get('task_id') != 'E1':
        report['diagnostics'].append('Expected a JSON object with task_id E1')
        return report
    if type(answer.get('explanation')) is not str or not answer['explanation'].strip():
        report['diagnostics'].append('A nonempty explanation is required; quality is reviewed separately')
        return report
    if 'alternative_format' in answer and type(answer['alternative_format']) is not bool:
        report['diagnostics'].append('alternative_format must be boolean')
        return report
    if answer.get('alternative_format'):
        if type(answer.get('alternative')) is not str or not answer['alternative'].strip():
            report['diagnostics'].append('Alternative review requires a nonempty alternative')
            return report
        report.update(status='review_required', overall_status='review_required')
        return report
    if type(answer.get('code')) is not str or not answer['code'].strip() or len(answer['code'].encode()) > 262144:
        report['diagnostics'].append('code must be a complete nonempty Python source string <=256 KiB')
        return report
    with tempfile.TemporaryDirectory(prefix='.e1-clean-', dir=Path.cwd()) as root:
        root = Path(root)
        source = root / 'candidate.py'
        source.write_text(answer['code'], encoding='utf-8')
        probe_state = root / 'probe'
        probe_state.mkdir()
        if not _trusted_control:
            try:
                require_sandbox(source, probe_state)
            except Unavailable as error:
                report.update(status='unavailable', overall_status='unavailable')
                report['diagnostics'].append(str(error))
                return report
        for trial_index in range(3):
            state = root / ('trial-' + str(trial_index))
            state.mkdir()
            model = Model()
            trial = {'index': trial_index + 1, 'events': [], 'passed': True}
            report['trials'].append(trial)
            try:
                for name, requests in batches():
                    records = run_batch(source, state, requests, _trusted_control)
                    actual = inspect(state)
                    expected = serial_outcomes(model, requests)
                    matches = [(next_model, replies) for next_model, replies in expected
                               if all(valid_reply(r['response']) for r in records)
                               and same([r['response']['value'] for r in records], replies)
                               and same(actual, next_model.snapshot())]
                    passed = bool(matches)
                    report['checks'].append({'id': f't{trial_index+1}.{name}', 'passed': passed})
                    trial['events'].append({'name': name, 'records': records, 'snapshot': actual,
                                            'legal_outcomes': [{'replies': replies, 'snapshot': m.snapshot()}
                                                               for m, replies in expected]})
                    if not passed:
                        raise WorkerFailure('Replies and SQL state do not match any legal serial outcome: ' + name)
                    model = matches[0][0]
                # Inject real SQLite errors; decisions and allowance must roll back.
                for table, req in [('ledger', request('fault_accept')),
                                   ('decisions', request('fault_reject', 'B', 1))]:
                    storage_fault(state, table, True)
                    before = deepcopy(model.snapshot())
                    records = run_batch(source, state, [req], _trusted_control)
                    actual = inspect(state)
                    envelope = records[0]['response']
                    passed = storage_error(envelope) and same(actual, before)
                    report['checks'].append({'id': f't{trial_index+1}.fault_{table}', 'passed': passed})
                    trial['events'].append({'name': 'fault_' + table, 'records': records,
                                            'snapshot': actual, 'expected_snapshot': before})
                    if not passed:
                        raise WorkerFailure('Storage error must be distinct from a business decision and preserve state: ' + table)
                    storage_fault(state, table, False)
                    records = run_batch(source, state, [req], _trusted_control)
                    expected_reply = model.apply(req)
                    actual = inspect(state)
                    passed = (valid_reply(records[0]['response']) and
                              same(records[0]['response']['value'], expected_reply) and same(actual, model.snapshot()))
                    report['checks'].append({'id': f't{trial_index+1}.retry_{table}', 'passed': passed})
                    trial['events'].append({'name': 'retry_' + table, 'records': records, 'snapshot': actual,
                                            'expected_reply': expected_reply, 'expected_snapshot': model.snapshot()})
                    if not passed:
                        raise WorkerFailure('Storage-error retry did not produce a fresh valid decision')
            except (WorkerFailure, sqlite3.Error, OSError, ValueError) as error:
                trial['passed'] = False
                report['checks'].append({'id': f't{trial_index+1}.completion', 'passed': False})
                report['diagnostics'].append(f'Trial {trial_index+1}: {type(error).__name__}: {error}')
    passed = all(t['passed'] for t in report['trials'])
    report.update(status='pass' if passed else 'fail', formal_status='pass' if passed else 'fail',
                  overall_status='formal_pass_review_pending' if passed else 'formal_fail')
    return report
