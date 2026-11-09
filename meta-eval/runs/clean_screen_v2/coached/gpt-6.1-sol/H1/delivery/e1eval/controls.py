"""Repository-authored controls, never solver input."""
from pathlib import Path


EXPLANATION = '''One BEGIN IMMEDIATE transaction encloses global-key lookup, the
allowance check, ledger insert and durable accepted/rejected decision. Exceptions
roll back; an ambiguous response must be retried with the identical global key
and payload, returning the stored historical decision. Payload changes have no
effects. SQLite serializes writers across accounts, so a hot account creates
queueing; increasing lock waits alone is not evidence of a lock cycle. Inspect
wait-for graphs and transaction traces for cycles; impose consistent acquisition
order in a multi-lock deployment. First shorten transaction duration and use
bounded admission/backpressure. Roll back that change if p99 reply latency
exceeds the agreed six-second test budget or duplicate/allowance invariants fail.
For deployment, partition or use row-level locking to allow different accounts
to progress in parallel, while preserving a global idempotency registry and
atomic coordination across its key and the account ledger. More retries do not
increase a hot account's write capacity. Production durability, backup, failover,
busy-timeout behavior and rejection history retention need explicit decisions.
These finite tests establish neither production latency nor universal safety.'''


def reference_answer():
    return {'task_id': 'E1', 'code': Path(__file__).with_name('reference.py').read_text(encoding='utf-8'),
            'explanation': EXPLANATION}


def positive_controls():
    original = reference_answer()
    second = dict(original, code=Path(__file__).with_name('conditional.py').read_text(encoding='utf-8'))
    returned_error = dict(original, code=original['code'].replace(
        '        finally:\n            db.close()',
        "        except sqlite3.Error:\n            return {'status': 'error', 'remaining': None}\n        finally:\n            db.close()"))
    return {'reference': original, 'conditional_debit': second, 'explicit_storage_error': returned_error}


def negative_controls():
    original = reference_answer()
    source = original['code']
    mutations = {
        'overspend': ("if remaining >= amount:", "if True:"),
        'missing_ledger': ("db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))", 'pass'),
        'no_debit': ("db.execute('UPDATE accounts SET remaining=? WHERE account=?', (remaining, account))", 'pass'),
        'lost_rejection': ("db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))",
                           "\n            if status == 'accepted':\n                db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))"),
        'current_replay': ("result = {'status': old[2], 'remaining': old[3]}",
                           "result = {'status': old[2], 'remaining': db.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]}"),
        'ignore_payload': ("if old[:2] != (account, amount):", 'if False:'),
        'account_scoped_key': ("WHERE key=?', (key,)", "WHERE key=? AND account=?', (key, account)"),
        'reset_initialization': ("INSERT OR IGNORE INTO accounts", "INSERT OR REPLACE INTO accounts"),
        'split_commit': ("db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))",
                         "db.commit()\n                db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))"),
        'error_as_business': ("        finally:\n            db.close()",
                              "        except sqlite3.Error:\n            return {'status': 'rejected', 'remaining': 0}\n        finally:\n            db.close()"),
        'no_transaction_race': ("db.execute('BEGIN IMMEDIATE')", "pass\n            import time\n            time.sleep(0.05)"),
        'replay_debits': ("db.commit()\n                return result",
                          "db.execute('UPDATE accounts SET remaining=remaining-1 WHERE account=?', (account,))\n                db.commit()\n                return result"),
        'boolean_remaining': ("return {'status': status, 'remaining': remaining}", "return {'status': status, 'remaining': True}"),
    }
    result = {}
    for name, (old, new) in mutations.items():
        if old not in source:
            raise AssertionError('Control mutation target missing: ' + name)
        result[name] = dict(original, code=source.replace(old, new))
    result['crash'] = dict(original, code='raise RuntimeError("authored crash control")')
    result['invalid_reply'] = dict(original, code='class Service:\n def __init__(self,path): pass\n def apply(self,r): return []\n')
    return result
