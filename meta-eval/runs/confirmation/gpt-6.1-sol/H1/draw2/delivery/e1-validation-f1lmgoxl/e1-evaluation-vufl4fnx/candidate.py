"""Authored positive control; never include this file in a solver prompt."""
import sqlite3


class Service:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=4, isolation_level=None)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute("CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY,remaining INTEGER)")
            self.db.execute("CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER)")
            self.db.execute("CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER)")
            self.db.executemany("INSERT OR IGNORE INTO accounts VALUES (?,100)", [("A",), ("B",)])
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def apply(self, request):
        key, account, amount = request["key"], request["account"], request["amount"]
        self.db.execute("BEGIN IMMEDIATE")
        try:
            old = self.db.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if old is not None:
                if old[:2] != (account, amount):
                    result = {"status": "payload_mismatch", "remaining": None}
                else:
                    result = {"status": old[2], "remaining": old[3]}
                self.db.commit()
                return result
            remaining = self.db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]
            status = "rejected"
            if remaining >= amount:
                status = "accepted"
                remaining -= amount
                self.db.execute("UPDATE accounts SET remaining=? WHERE account=?", (remaining, account))
                self.db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))
            self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))
            self.db.commit()
            return {"status": status, "remaining": remaining}
        except BaseException:
            self.db.rollback()
            raise
