"""Authored positive control; do not expose this file to a solver."""
import sqlite3
from contextlib import closing


class Service:
    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(path, timeout=4)) as db:
            db.execute("PRAGMA busy_timeout=4000")
            db.executescript('''
                CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS decisions(
                    key TEXT PRIMARY KEY, account TEXT, amount INTEGER, status TEXT, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
                INSERT OR IGNORE INTO accounts VALUES ('A',100);
                INSERT OR IGNORE INTO accounts VALUES ('B',100);
            ''')

    def apply(self, request):
        key, account, amount = (request[field] for field in ("key", "account", "amount"))
        # The writer reservation covers identity lookup, balance check and all writes.
        db = sqlite3.connect(self.path, timeout=4)
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if old:
                result = ({"status": old[2], "remaining": old[3]} if old[:2] == (account, amount)
                          else {"status": "payload_mismatch", "remaining": None})
            else:
                remaining = db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]
                status = "rejected"
                if remaining >= amount:
                    status, remaining = "accepted", remaining - amount
                    db.execute("UPDATE accounts SET remaining=? WHERE account=?", (remaining, account))
                    db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))
                db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))
                result = {"status": status, "remaining": remaining}
            db.commit()
            return result
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
