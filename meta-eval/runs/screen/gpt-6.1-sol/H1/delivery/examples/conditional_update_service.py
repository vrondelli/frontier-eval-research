"""Second authored positive control: insert-first identity and conditional debit."""
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

    def apply(self, req):
        conn = sqlite3.connect(self.path, timeout=4, isolation_level=None)
        key, account, amount = req['key'], req['account'], req['amount']
        try:
            conn.execute('BEGIN')
            # The first database operation is a write; it serializes identity
            # ownership without a deferred read-transaction upgrade race.
            inserted = conn.execute(
                'INSERT OR IGNORE INTO decisions VALUES(?,?,?, ?,?)',
                (key, account, amount, 'pending', 0)).rowcount
            if not inserted:
                old = conn.execute('SELECT account,amount,status,remaining FROM decisions WHERE key=?',
                                   (key,)).fetchone()
                result = ({'status': old[2], 'remaining': old[3]} if old[:2] == (account, amount)
                          else {'status': 'payload_mismatch', 'remaining': None})
            else:
                updated = conn.execute(
                    'UPDATE accounts SET remaining=remaining-? WHERE account=? AND remaining>=?',
                    (amount, account, amount)).rowcount
                status = 'accepted' if updated else 'rejected'
                remaining = conn.execute('SELECT remaining FROM accounts WHERE account=?',
                                         (account,)).fetchone()[0]
                if updated:
                    conn.execute('INSERT INTO ledger VALUES(?,?,?)', (key, account, amount))
                conn.execute('UPDATE decisions SET status=?,remaining=? WHERE key=?',
                             (status, remaining, key))
                result = {'status': status, 'remaining': remaining}
            conn.execute('COMMIT')
            return result
        except BaseException:
            if conn.in_transaction:
                conn.execute('ROLLBACK')
            raise
        finally:
            conn.close()
