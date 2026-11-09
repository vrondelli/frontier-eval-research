"""Authored reference for evaluator development. Never disclose to a solver."""

import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER)")
            db.execute("CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY, account TEXT, amount INTEGER, status TEXT, remaining INTEGER)")
            db.execute("CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER)")
            for account in ("A", "B"):
                db.execute("INSERT OR IGNORE INTO accounts VALUES (?,100)", (account,))
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def connect(self):
        return sqlite3.connect(self.path, timeout=4, isolation_level=None)

    def apply(self, request):
        key, account, amount = (request[name] for name in ("key", "account", "amount"))
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if prior is not None:
                if prior[:2] != (account, amount):
                    reply = {"status": "payload_mismatch", "remaining": None}
                else:
                    reply = {"status": prior[2], "remaining": prior[3]}
                db.commit()
                return reply
            remaining = db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]
            status = "accepted" if remaining >= amount else "rejected"
            if status == "accepted":
                remaining -= amount
                db.execute("UPDATE accounts SET remaining=? WHERE account=?", (remaining, account))
                db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))
            db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))
            db.commit()
            return {"status": status, "remaining": remaining}
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
