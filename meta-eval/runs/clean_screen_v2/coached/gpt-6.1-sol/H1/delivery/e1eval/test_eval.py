from copy import deepcopy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from .__main__ import load_answer
from .controls import reference_answer
from .grader import base_report, grade, request, same, storage_error, valid_reply
from .oracle import Model, serial_outcomes
from .runner import WorkerFailure, inspect, run_batch
from .schema import validate_report


class OracleTests(unittest.TestCase):
    def test_both_serial_winners(self):
        outcomes = serial_outcomes(Model(), [request('x', amount=60), request('y', amount=60)])
        self.assertEqual(len(outcomes), 2)
        self.assertEqual({tuple(r['status'] for r in replies) for _, replies in outcomes},
                         {('accepted', 'rejected'), ('rejected', 'accepted')})
        for model, _ in outcomes:
            self.assertEqual(model.accounts, {'A': 40, 'B': 100})
            self.assertEqual(len(model.ledger), 1)
            self.assertEqual(len(model.decisions), 2)

    def test_rejection_and_acceptance_history(self):
        model = Model()
        self.assertEqual(model.apply(request('x', amount=60)), {'status': 'accepted', 'remaining': 40})
        self.assertEqual(model.apply(request('y', amount=60)), {'status': 'rejected', 'remaining': 40})
        model.apply(request('z', amount=10))
        self.assertEqual(model.apply(request('y', amount=60))['remaining'], 40)
        self.assertEqual(model.apply(request('x', amount=60))['remaining'], 40)

    def test_global_identity_is_immutable(self):
        model = Model()
        model.apply(request('x', amount=60))
        before = deepcopy(model.snapshot())
        self.assertEqual(model.apply(request('x', 'B', 60)), {'status': 'payload_mismatch', 'remaining': None})
        self.assertEqual(model.apply(request('x', amount=61)), {'status': 'payload_mismatch', 'remaining': None})
        self.assertEqual(model.snapshot(), before)

    def test_duplicate_concurrency(self):
        for model, replies in serial_outcomes(Model(), [request('x', amount=60)] * 2):
            self.assertEqual(replies[0], replies[1])
            self.assertEqual(model.accounts['A'], 40)
            self.assertEqual(len(model.ledger), 1)

    def test_conflict_concurrency_both_orders(self):
        outcomes = serial_outcomes(Model(), [request('x', 'A', 10), request('x', 'B', 11)])
        for model, replies in outcomes:
            self.assertEqual(sorted(r['status'] for r in replies), ['accepted', 'payload_mismatch'])
            self.assertEqual(len(model.ledger), 1)

    def test_oracle_does_not_import_reference_or_sqlite(self):
        source = Path(__file__).with_name('oracle.py').read_text(encoding='utf-8')
        self.assertNotIn('import sqlite3', source)
        self.assertNotIn('from .reference', source)


class ContractTests(unittest.TestCase):
    def test_storage_error_is_not_business_decision(self):
        self.assertTrue(storage_error({'kind': 'error', 'type': 'OperationalError'}))
        self.assertTrue(storage_error({'kind': 'reply', 'value': {'status': 'error', 'remaining': None}}))
        self.assertFalse(storage_error({'kind': 'reply', 'value': {'status': 'rejected', 'remaining': 0}}))
        self.assertFalse(storage_error({'kind': 'reply', 'value': {'status': 'payload_mismatch', 'remaining': None}}))

    def test_reply_types_are_strict(self):
        self.assertFalse(valid_reply({'kind': 'reply', 'value': {'status': 'accepted', 'remaining': True}}))
        self.assertFalse(valid_reply({'kind': 'reply', 'value': {'status': 'rejected', 'remaining': -1}}))
        self.assertFalse(valid_reply({'kind': 'reply', 'value': {'status': 'payload_mismatch', 'remaining': 0}}))
        self.assertFalse(valid_reply({'kind': 'reply', 'value': {'status': 'accepted', 'remaining': 40, 'extra': 1}}))
        self.assertTrue(valid_reply({'kind': 'reply', 'value': {'status': 'accepted', 'remaining': 40}}))
        self.assertFalse(same(True, 1))

    def test_bad_envelopes(self):
        for answer in [[], {}, {'task_id': 'E2'}, {'task_id': 'E1', 'explanation': ''},
                       {'task_id': 'E1', 'explanation': 'x', 'code': ''},
                       {'task_id': 'E1', 'explanation': 'x', 'code': 'x', 'alternative_format': 'true'}]:
            result = grade(answer)
            self.assertEqual(result['status'], 'invalid')
            validate_report(result)

    def test_alternative_never_runs_code(self):
        result = grade({'task_id': 'E1', 'alternative_format': True, 'alternative': 'Partitioned ledger',
                        'code': 'raise RuntimeError()', 'explanation': 'Requires independent review'})
        self.assertEqual(result['status'], 'review_required')
        self.assertEqual(result['formal_status'], 'not_run')
        validate_report(result)

    def test_schema_rejects_fabricated_pass(self):
        report = base_report({}, 'trusted_control')
        report.update(status='pass', formal_status='pass', overall_status='formal_pass_review_pending')
        with self.assertRaises(ValueError):
            validate_report(report)

    def test_strict_json_parser(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            path = Path(root) / 'answer.json'
            for text in ['{"x":1,"x":2}', '{"x":NaN}', 'not JSON']:
                path.write_text(text, encoding='utf-8')
                with self.assertRaises(ValueError):
                    load_answer(path)


class RunnerTests(unittest.TestCase):
    def setup_state(self, root):
        root = Path(root)
        state = root / 'state'
        state.mkdir()
        source = root / 'candidate.py'
        source.write_text(reference_answer()['code'], encoding='utf-8')
        run_batch(source, state, [request('seed')], True)
        return source, state

    def test_inspector_rejects_views(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            _, state = self.setup_state(root)
            with closing(sqlite3.connect(state / 'ledger.db')) as db, db:
                db.execute('ALTER TABLE ledger RENAME TO hidden_ledger')
                db.execute('CREATE VIEW ledger AS SELECT * FROM hidden_ledger')
            with self.assertRaises(WorkerFailure):
                inspect(state)

    def test_inspector_rejects_wrong_primary_key(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            _, state = self.setup_state(root)
            with closing(sqlite3.connect(state / 'ledger.db')) as db, db:
                db.execute('ALTER TABLE ledger RENAME TO hidden_ledger')
                db.execute('CREATE TABLE ledger(key TEXT, account TEXT, amount INTEGER)')
            with self.assertRaises(WorkerFailure):
                inspect(state)

    def test_inspector_rejects_oversize(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            _, state = self.setup_state(root)
            with (state / 'ledger.db-journal').open('wb') as file:
                file.truncate(8 * 1024**2 + 1)
            with self.assertRaises(WorkerFailure):
                inspect(state)

    def test_inspector_row_bound(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            _, state = self.setup_state(root)
            with closing(sqlite3.connect(state / 'ledger.db')) as db, db:
                db.executemany('INSERT INTO ledger VALUES (?,?,?)', [('extra-' + str(i), 'A', 1) for i in range(100)])
            with self.assertRaises(WorkerFailure):
                inspect(state)

    def test_worker_bounds_oversized_output(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            root = Path(root)
            source = root / 'candidate.py'
            source.write_text('class Service:\n def __init__(self,p): pass\n def apply(self,r): return "x"*70000\n', encoding='utf-8')
            with self.assertRaises(WorkerFailure):
                run_batch(source, root, [request('x')], True)

    def test_deadline_and_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='.e1-test-', dir=Path.cwd()) as root:
            root = Path(root)
            source = root / 'candidate.py'
            source.write_text('import time\nclass Service:\n def __init__(self,p): time.sleep(60)\n', encoding='utf-8')
            start = time.monotonic()
            with self.assertRaises(WorkerFailure):
                run_batch(source, root, [request('x')], True)
            self.assertLess(time.monotonic() - start, 10)


if __name__ == '__main__':
    unittest.main()
