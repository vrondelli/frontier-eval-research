"""Authored positive control, never supplied to a solver as task input."""
import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        db = sqlite3.connect(path, timeout=5)
        try:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY,remaining INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER)')
            for account in ('A', 'B'):
                db.execute('INSERT OR IGNORE INTO accounts VALUES (?,100)', (account,))
            db.commit()
        finally:
            db.close()

    def apply(self, request):
        key, account, amount = request['key'], request['account'], request['amount']
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT account,amount,status,remaining FROM decisions WHERE key=?', (key,)).fetchone()
            if row:
                if row[:2] != (account, amount):
                    result = {'status': 'payload_mismatch', 'remaining': None}
                else:
                    result = {'status': row[2], 'remaining': row[3]}
            else:
                remaining = db.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]
                status = 'rejected'
                if amount <= remaining:
                    status = 'accepted'
                    remaining -= amount
                    db.execute('UPDATE accounts SET remaining=? WHERE account=?', (remaining, account))
                    db.execute('INSERT INTO ledger VALUES (?,?,?)', (key, account, amount))
                db.execute('INSERT INTO decisions VALUES (?,?,?,?,?)', (key, account, amount, status, remaining))
                result = {'status': status, 'remaining': remaining}
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
