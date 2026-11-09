"""Second authored positive: conditional debit decides acceptance."""
from contextlib import closing
import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(path, timeout=2)) as db, db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY, account TEXT,
                    amount INTEGER, status TEXT, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
            ''')
            db.executemany('INSERT OR IGNORE INTO accounts VALUES (?,100)', [('A',), ('B',)])

    def apply(self, request):
        key, account, amount = request['key'], request['account'], request['amount']
        with closing(sqlite3.connect(self.path, timeout=2)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT account,amount,status,remaining FROM decisions WHERE key=?', (key,)).fetchone()
            if old:
                if (account, amount) != old[:2]:
                    return {'status': 'payload_mismatch', 'remaining': None}
                return {'status': old[2], 'remaining': old[3]}
            changed = db.execute('UPDATE accounts SET remaining=remaining-? WHERE account=? AND remaining>=?',
                                 (amount, account, amount)).rowcount
            remaining = db.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]
            status = 'accepted' if changed else 'rejected'
            if changed:
                db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))
            return {'status': status, 'remaining': remaining}
