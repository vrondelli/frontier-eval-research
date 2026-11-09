"""Authored development controls. Never give these sources to a solver."""

GOOD = '''import sqlite3

class Service:
    def __init__(self, path):
        self.path = path
        connection = sqlite3.connect(path, timeout=3, isolation_level=None)
        try:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY, account TEXT,
                    amount INTEGER, status TEXT, remaining INTEGER);
                CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
            """)
            connection.execute("BEGIN IMMEDIATE")
            connection.executemany("INSERT OR IGNORE INTO accounts VALUES (?,100)", [("A",),("B",)])
            connection.commit()
        finally:
            connection.close()

    def apply(self, request):
        key, account, amount = (request[x] for x in ("key", "account", "amount"))
        connection = sqlite3.connect(self.path, timeout=3, isolation_level=None)
        try:
            connection.execute("BEGIN IMMEDIATE")
            old = connection.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if old:
                if (account, amount) != old[:2]:
                    result = {"status":"payload_mismatch", "remaining":None}
                else:
                    result = {"status":old[2], "remaining":old[3]}
            else:
                remaining = connection.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]
                status = "accepted" if remaining >= amount else "rejected"
                if status == "accepted":
                    remaining -= amount
                    connection.execute("UPDATE accounts SET remaining=? WHERE account=?", (remaining,account))
                    connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key,account,amount))
                connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key,account,amount,status,remaining))
                result = {"status":status, "remaining":remaining}
            connection.commit()
            return result
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
'''


def replace_once(source, old, new):
    assert source.count(old) == 1
    return source.replace(old, new)


BAD = {
    "stale_read_race": replace_once(
        replace_once(GOOD, '            connection.commit()\n        finally:',
                     '            connection.commit()\n'
                     '            self.initial = dict(connection.execute("SELECT account,remaining FROM accounts"))\n'
                     '        finally:'),
        'remaining = connection.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]',
        'remaining = self.initial[account]'),
    "lost_rejection": replace_once(
        GOOD,
        '                connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key,account,amount,status,remaining))',
        '                if status == "accepted":\n'
        '                    connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key,account,amount,status,remaining))'),
    "current_instead_of_historical": replace_once(
        GOOD, 'result = {"status":old[2], "remaining":old[3]}',
        'result = {"status":old[2], "remaining":connection.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]}'),
    "ignores_payload": replace_once(GOOD, 'if (account, amount) != old[:2]:', 'if False:'),
    "missing_ledger": replace_once(
        GOOD, '                    connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key,account,amount))',
        '                    pass  # omitted ledger write'),
    "commits_before_ledger": replace_once(
        GOOD, '                    connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key,account,amount))',
        '                    connection.commit()\n'
        '                    connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key,account,amount))'),
    "error_as_rejection": replace_once(
        GOOD, '            connection.rollback()\n            raise',
        '            connection.rollback()\n            return {"status":"rejected", "remaining":100}'),
}


def answer(code=GOOD):
    return {"task_id": "E1", "code": code,
            "explanation": "Authored control only; explanation quality is not asserted."}
