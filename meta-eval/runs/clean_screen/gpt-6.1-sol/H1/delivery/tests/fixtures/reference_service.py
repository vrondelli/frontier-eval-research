"""Authored control, never a solver result. Do not include this in solver prompts."""
import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            for sql in (
                "CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY,remaining INTEGER)",
                "CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER)",
                "CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER)",
            ):
                db.execute(sql)
            db.executemany("INSERT OR IGNORE INTO accounts VALUES (?,100)", [("A",), ("B",)])
            db.commit()
        finally:
            db.close()

    def _connect(self):
        return sqlite3.connect(self.path, timeout=2, isolation_level=None)

    def apply(self, request):
        key, account, amount = (request[x] for x in ("key", "account", "amount"))
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if old:
                if (account, amount) != old[:2]:
                    reply = {"status": "payload_mismatch", "remaining": None}
                else:
                    reply = {"status": old[2], "remaining": old[3]}
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
