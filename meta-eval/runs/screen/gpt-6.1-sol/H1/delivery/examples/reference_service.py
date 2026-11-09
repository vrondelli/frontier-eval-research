"""Authored positive control. Keep out of solver prompts."""
import contextlib
import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        with contextlib.closing(sqlite3.connect(path, timeout=4)) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY, account TEXT,
                    amount INTEGER, status TEXT, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
                INSERT OR IGNORE INTO accounts VALUES('A', 100);
                INSERT OR IGNORE INTO accounts VALUES('B', 100);
            ''')

    def apply(self, request):
        key, account, amount = (request[k] for k in ('key', 'account', 'amount'))
        conn = sqlite3.connect(self.path, timeout=4, isolation_level=None)
        try:
            conn.execute('BEGIN IMMEDIATE')
            old = conn.execute('SELECT account,amount,status,remaining FROM decisions WHERE key=?',
                               (key,)).fetchone()
            if old:
                result = ({'status': old[2], 'remaining': old[3]} if old[:2] == (account, amount)
                          else {'status': 'payload_mismatch', 'remaining': None})
            else:
                remaining = conn.execute('SELECT remaining FROM accounts WHERE account=?',
                                         (account,)).fetchone()[0]
                status = 'accepted' if amount <= remaining else 'rejected'
                if status == 'accepted':
                    remaining -= amount
                    conn.execute('UPDATE accounts SET remaining=? WHERE account=?', (remaining, account))
                    conn.execute('INSERT INTO ledger VALUES(?,?,?)', (key, account, amount))
                conn.execute('INSERT INTO decisions VALUES(?,?,?,?,?)',
                             (key, account, amount, status, remaining))
                result = {'status': status, 'remaining': remaining}
            conn.execute('COMMIT')
            return result
        except BaseException:
            if conn.in_transaction:
                conn.execute('ROLLBACK')
            raise
        finally:
            conn.close()
