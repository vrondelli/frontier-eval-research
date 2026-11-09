import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import evaluate as ev
from inspector import inspect
import protocol

REFERENCE = Path(__file__).parent / 'tests' / 'fixtures' / 'reference.py'


def valid_trace(order=(0, 1)):
    oracle = ev.Oracle()
    pair = ev.requests()
    overlap = [None, None]
    for i in order:
        overlap[i] = oracle.apply(pair[i])
    trace = {'overlap': overlap, 'after_overlap': oracle.snapshot(), 'steps': []}
    for request in ev.followups():
        reply = oracle.apply(request)
        trace['steps'].append({'request': request, 'reply': reply, 'snapshot': oracle.snapshot()})
    return trace


def answer(code=None):
    return {'task_id': 'E1', 'code': code if code is not None else REFERENCE.read_text(),
            'explanation': 'Authored control only; quality requires independent review.'}


class OracleTests(unittest.TestCase):
    def test_both_serial_orders(self):
        for order in ((0, 1), (1, 0)):
            with self.subTest(order=order):
                self.assertTrue(ev.verify_trace(valid_trace(order))['passed'])

    def test_negative_trace_controls(self):
        def both_accept(t):
            t['overlap'][1] = {'status': 'accepted', 'remaining': 40}

        def current_balance_retry(t):
            t['steps'][7]['reply']['remaining'] = 0

        def current_balance_accepted_retry(t):
            t['steps'][6]['reply']['remaining'] = 0

        def absent_rejected_decision(t):
            t['after_overlap']['decisions'] = [t['after_overlap']['decisions'][0]]

        def double_debit(t):
            t['steps'][0]['snapshot']['accounts'][0][1] = -20

        def duplicate_ledger(t):
            t['steps'][0]['snapshot']['ledger'].append(['duplicate', 'A', 60])

        def mismatch_writes(t):
            t['steps'][2]['snapshot']['accounts'][0][1] = 39

        def changed_identity(t):
            t['steps'][3]['reply'] = {'status': 'accepted', 'remaining': 40}

        def b_starved(t):
            t['steps'][4]['reply'] = {'status': 'rejected', 'remaining': 0}

        def fake_boolean(t):
            t['steps'][8]['reply']['remaining'] = False

        def missing_ledger(t):
            t['after_overlap']['ledger'] = []

        def incomplete(t):
            t['steps'].pop()

        for mutation in (both_accept, current_balance_retry, current_balance_accepted_retry,
                         absent_rejected_decision, double_debit, duplicate_ledger,
                         mismatch_writes, changed_identity, b_starved, fake_boolean,
                         missing_ledger, incomplete):
            with self.subTest(mutation=mutation.__name__):
                trace = copy.deepcopy(valid_trace())
                mutation(trace)
                self.assertFalse(ev.verify_trace(trace)['passed'])

    def test_alternative_route_never_runs_code(self):
        with patch.object(ev, 'availability', side_effect=AssertionError('must not execute')):
            result = ev.grade({'task_id': 'E1', 'alternative_format': True,
                               'alternative': 'A partitioned transactional service.',
                               'explanation': 'Requires separate architectural review.'})
        self.assertEqual(result['formal_status'], 'review_required')

    def test_invalid_and_unavailable_are_not_passes(self):
        self.assertEqual(ev.grade({'task_id': 'E2'})['formal_status'], 'invalid')
        self.assertEqual(ev.grade([])['formal_status'], 'invalid')
        self.assertEqual(ev.grade({**answer(), 'explanation': ''})['formal_status'], 'invalid')
        with patch.object(ev, 'availability', return_value='no isolation'):
            result = ev.grade(answer())
        self.assertEqual(result['formal_status'], 'unavailable')

    def test_non_linux_fails_closed(self):
        with patch.object(ev.sys, 'platform', 'win32'):
            self.assertIn('not executed', ev.availability())

    def test_answer_binding(self):
        original = answer()
        changed = {**original, 'explanation': 'Different explanation'}
        self.assertNotEqual(ev.digest(original), ev.digest(changed))


class InspectorTests(unittest.TestCase):
    def setup_database(self, root):
        db = sqlite3.connect(Path(root) / 'service.sqlite')
        db.executescript('''
            CREATE TABLE accounts(account TEXT PRIMARY KEY,remaining INTEGER);
            CREATE TABLE decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER);
            CREATE TABLE ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER);
            INSERT INTO accounts VALUES ('A',100),('B',100);
        ''')
        return db

    def test_independent_read_only_inspection(self):
        with tempfile.TemporaryDirectory(dir=ev.ROOT) as root:
            db = self.setup_database(root)
            db.close()
            self.assertEqual(ev.normalize_snapshot(inspect(root)), ev.Oracle().snapshot())

    def test_view_and_missing_primary_key_rejected(self):
        for replacement in ('CREATE VIEW ledger AS SELECT "x" AS key,"A" AS account,1 AS amount',
                            'CREATE TABLE ledger(key TEXT,account TEXT,amount INTEGER)'):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory(dir=ev.ROOT) as root:
                db = self.setup_database(root)
                db.execute('DROP TABLE ledger')
                db.execute(replacement)
                db.commit()
                db.close()
                with self.assertRaises(ValueError):
                    inspect(root)

    def test_row_bound(self):
        with tempfile.TemporaryDirectory(dir=ev.ROOT) as root:
            db = self.setup_database(root)
            db.executemany('INSERT INTO ledger VALUES (?,?,?)', [(str(i), 'A', 1) for i in range(100)])
            db.commit()
            db.close()
            with self.assertRaises(ValueError):
                inspect(root)

    @unittest.skipIf(sys.platform == 'win32', 'Windows symlink privilege not assumed')
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory(dir=ev.ROOT) as root:
            db = self.setup_database(root)
            db.close()
            (Path(root) / 'service.sqlite-wal').symlink_to('/dev/null')
            with self.assertRaises(ValueError):
                inspect(root)


class ProtocolTests(unittest.TestCase):
    def test_first_view_withholds_reveal(self):
        view = protocol.start()['view']
        self.assertIn('F5.', view)
        self.assertNotIn('F6.', view)
        self.assertNotIn('deadlock', view)
        self.assertNotIn('dominate traffic', view)

    def test_stages_preserve_first_answer(self):
        with tempfile.TemporaryDirectory(dir=ev.ROOT) as directory:
            root = Path(directory)
            first = {'task_id': 'E1', 'explanation': 'Initial preserved response',
                     'code': 'initial source'}
            final = {'task_id': 'E1', 'alternative_format': True,
                     'alternative': 'Partitioned transactional store',
                     'explanation': 'Revised after hot-account reveal'}
            protocol.write_new(root / 'stage0.json', protocol.start())
            protocol.write_new(root / 'first.json', first)
            stage1 = protocol.reveal(root / 'stage0.json', root / 'first.json')
            self.assertIn('F6.', stage1['view'])
            protocol.write_new(root / 'stage1.json', stage1)
            protocol.write_new(root / 'final.json', final)
            report = protocol.finish(root / 'stage1.json', root / 'final.json')
            self.assertEqual(report['formal_status'], 'review_required')
            self.assertEqual(report['staged_evidence']['initial_answer'], first)
            self.assertEqual(report['staged_evidence']['initial_answer_sha256'], ev.digest(first))
            self.assertEqual(report['answer_sha256'], ev.digest(final))
            with self.assertRaises(FileExistsError):
                protocol.write_new(root / 'stage1.json', stage1)

    def test_tampered_and_out_of_order_state_rejected(self):
        with tempfile.TemporaryDirectory(dir=ev.ROOT) as directory:
            target = Path(directory) / 'state.json'
            state = protocol.start()
            protocol.write_new(target, state)
            with self.assertRaises(ValueError):
                protocol.load_state(target, 'revealed')
            state['view'] += 'tampered'
            target.write_text(json.dumps(state), encoding='utf-8')
            with self.assertRaises(ValueError):
                protocol.load_state(target, 'initial')


class WorkerCoordinationTests(unittest.TestCase):
    def test_both_armed_and_read_concurrently(self):
        workers = []
        readers = threading.Barrier(2)

        class ControlledWorker:
            def __init__(self, state, code, req):
                self.armed = False
                self.closed = False
                self.process = SimpleNamespace(returncode=None)
                workers.append(self)

            def arm(self):
                self.armed = True

            def release(self):
                if len(workers) != 2 or not all(w.armed for w in workers):
                    raise AssertionError('release before both workers armed')

            def result(self):
                readers.wait(timeout=1)
                return {'status': 'accepted', 'remaining': 40}

            def close(self):
                self.closed = True
                self.process.returncode = 0

        events = []
        with patch.object(ev, 'Worker', ControlledWorker):
            replies = ev.run_batch(None, None, ev.requests(), events)
        self.assertEqual(len(replies), 2)
        self.assertTrue(all(w.closed for w in workers))
        self.assertTrue(events[0]['both_armed_before_release'])
        self.assertEqual([w['returncode'] for w in events[0]['workers']], [0, 0])

    def test_failure_still_cleans_up_every_worker(self):
        workers = []

        class FailingWorker:
            def __init__(self, state, code, req):
                self.closed = False
                self.process = SimpleNamespace(returncode=None)
                workers.append(self)

            def arm(self):
                raise ev.EvaluationError('initialization failure')

            def close(self):
                self.closed = True
                self.process.returncode = -9

        events = []
        with patch.object(ev, 'Worker', FailingWorker), self.assertRaises(ev.EvaluationError):
            ev.run_batch(None, None, ev.requests(), events)
        self.assertTrue(all(w.closed for w in workers))
        self.assertEqual([w['returncode'] for w in events[0]['workers']], [-9, -9])


class IsolatedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reason = ev.availability()
        if reason:
            raise unittest.SkipTest(reason)

    def test_reference_and_broken_services(self):
        source = REFERENCE.read_text()
        controls = {
            'reference': (source, 'pass'),
            'historical_replay': (source.replace("'remaining': row[3]", "'remaining': db.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]"), 'fail'),
            'missing_ledger': (source.replace("db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))", 'pass'), 'fail'),
            'lost_rejection': (source.replace("db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))", "\n                if status == 'accepted':\n                    db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))"), 'fail'),
            'ignored_mismatch': (source.replace("row[:2] != (account, amount)", 'False'), 'fail'),
            'reinitialize': (source.replace('INSERT OR IGNORE INTO accounts', 'INSERT OR REPLACE INTO accounts'), 'fail'),
            'overdraft': (source.replace('if amount <= remaining:', 'if True:'), 'fail'),
            'runtime_error': ('class Service:\n def __init__(self,path): pass\n def apply(self,request): raise OSError("database error")\n', 'fail'),
        }
        for name, (code, expected) in controls.items():
            with self.subTest(control=name):
                result = ev.grade(answer(code))
                self.assertEqual(result['formal_status'], expected, json.dumps(result))

    def test_private_worker_surface(self):
        probe = '''
import os
import socket
from pathlib import Path
assert not Path('/code/evaluate.py').exists()
assert not Path('/code/tests').exists()
assert not Path('/code/input').exists()
assert set(os.listdir('/code')) == {'candidate.py', 'worker.py'}
assert 'HOME' not in os.environ
assert 'AWS_SECRET_ACCESS_KEY' not in os.environ
assert set(os.listdir('/sys')) == set() if Path('/sys').exists() else True
assert not any(name not in ('lo',) for _, name in socket.if_nameindex())
'''
        self.assertEqual(ev.grade(answer(probe + REFERENCE.read_text()))['formal_status'], 'pass')


if __name__ == '__main__':
    unittest.main()
