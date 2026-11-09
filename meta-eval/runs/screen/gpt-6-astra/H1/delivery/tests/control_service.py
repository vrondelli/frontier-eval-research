"""Newly authored positive control, NEVER solver input or model-performance evidence."""
import sqlite3


class Service:
    def __init__(self, path):
        self.path = path
        connection = sqlite3.connect(path, timeout=5)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER)")
            connection.execute("CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY, account TEXT, amount INTEGER, status TEXT, remaining INTEGER)")
            connection.execute("CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER)")
            connection.executemany("INSERT OR IGNORE INTO accounts VALUES (?,100)", [("A",), ("B",)])
            connection.commit()
        finally:
            connection.close()

    def apply(self, request):
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            connection.execute("BEGIN IMMEDIATE")
            key, account, amount = (request[k] for k in ("key", "account", "amount"))
            prior = connection.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if prior:
                result = {"status": prior[2], "remaining": prior[3]}
                if (account, amount) != prior[:2]:
                    result = {"status": "payload_mismatch", "remaining": None}
                connection.commit()
                return result
            remaining = connection.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]
            accepted = amount <= remaining
            if accepted:
                remaining -= amount
                connection.execute("UPDATE accounts SET remaining=? WHERE account=?", (remaining, account))
                connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))
            status = "accepted" if accepted else "rejected"
            connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))
            connection.commit()
            return {"status": status, "remaining": remaining}
        finally:
            # If an exception/unknown outcome occurs it is never converted to rejection.
            connection.close()
