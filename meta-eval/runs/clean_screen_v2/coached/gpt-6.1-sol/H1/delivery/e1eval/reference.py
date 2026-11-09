"""Authored executable reference. Never provided to a solver or worker."""
import sqlite3
from contextlib import closing


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
            db.execute('INSERT OR IGNORE INTO accounts VALUES (?, ?)', ('A', 100))
            db.execute('INSERT OR IGNORE INTO accounts VALUES (?, ?)', ('B', 100))

    def apply(self, request):
        key, account, amount = (request[x] for x in ('key', 'account', 'amount'))
        db = sqlite3.connect(self.path, timeout=2)
        try:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT account,amount,status,remaining FROM decisions WHERE key=?', (key,)).fetchone()
            if old is not None:
                if old[:2] != (account, amount):
                    result = {'status': 'payload_mismatch', 'remaining': None}
                else:
                    result = {'status': old[2], 'remaining': old[3]}
                db.commit()
                return result
            remaining = db.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]
            if remaining >= amount:
                remaining -= amount
                status = 'accepted'
                db.execute('UPDATE accounts SET remaining=? WHERE account=?', (remaining, account))
                db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))
            else:
                status = 'rejected'
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))
            db.commit()
            return {'status': status, 'remaining': remaining}
        finally:
            db.close()
