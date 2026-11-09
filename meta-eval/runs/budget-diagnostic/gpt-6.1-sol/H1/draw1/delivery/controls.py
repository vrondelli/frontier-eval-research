"""Authored implementation controls. Never include these in solver prompts."""
import argparse
import json
from pathlib import Path

REFERENCE = '''import sqlite3

class Service:
    def __init__(self, path):
        self.path = path
        con = sqlite3.connect(path, timeout=4.5, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            con.execute("CREATE TABLE IF NOT EXISTS accounts(account TEXT PRIMARY KEY,remaining INTEGER)")
            con.execute("CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY,account TEXT,amount INTEGER,status TEXT,remaining INTEGER)")
            con.execute("CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY,account TEXT,amount INTEGER)")
            con.execute("INSERT OR IGNORE INTO accounts VALUES('A',100)")
            con.execute("INSERT OR IGNORE INTO accounts VALUES('B',100)")
            con.commit()
        finally:
            con.close()

    def apply(self, request):
        key, account, amount = (request[k] for k in ('key','account','amount'))
        con = sqlite3.connect(self.path, timeout=4.5, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            old = con.execute("SELECT account,amount,status,remaining FROM decisions WHERE key=?", (key,)).fetchone()
            if old:
                if old[:2] != (account, amount):
                    reply = {'status':'payload_mismatch','remaining':None}
                else:
                    reply = {'status':old[2],'remaining':old[3]}
                con.commit()
                return reply
            remaining = con.execute("SELECT remaining FROM accounts WHERE account=?",(account,)).fetchone()[0]
            status = 'rejected'
            if amount <= remaining:
                remaining -= amount
                con.execute("UPDATE accounts SET remaining=? WHERE account=?",(remaining,account))
                con.execute("INSERT INTO ledger VALUES(?,?,?)",(key,account,amount))
                status = 'accepted'
            con.execute("INSERT INTO decisions VALUES(?,?,?,?,?)",(key,account,amount,status,remaining))
            con.commit()
            return {'status':status,'remaining':remaining}
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()
'''

EXPLANATION = """Each transaction begins IMMEDIATE before reading identity or allowance and commits the
debit, ledger row and immutable decision together. A rejected decision is also committed.
Initialization uses the same transaction discipline and INSERT OR IGNORE. Identity is global,
and stored account/amount must match before replaying the original status and remaining.
After an uncertain commit or lost reply, retry the same key and payload in a fresh process;
never invent a new key or turn a database exception into an insufficient-allowance rejection.

The hot-account reveal can reflect queueing without a lock cycle. SQLite permits only one
writer per database, so even distinct accounts cannot write concurrently here. Actual deadlock
reports require the database's wait-for graph, lock ordering and retry logs to diagnose; these
finite tests neither produce nor rule out production deadlocks. A row-locking database can let
different accounts proceed independently, while the same account still needs ordered admission.

First measure transaction duration and lock wait, shorten transactions and add bounded jittered
busy retries with backpressure; put no network calls inside the transaction. A bounded per-account
queue can protect a hot key and fairness, but adds queue recovery and deployment complexity.
Rollback the rollout and stop admissions on any invariant violation (negative balance, conflicting
decision or extra/missing ledger row); roll back if p99 end-to-end latency exceeds the agreed
baseline by 2x for five minutes or busy errors exceed 1%. Reconcile uncertain commits by key.
SQLite is suitable for this tiny executable contract; row locking, partitioning and global-key
coordination introduce migration and operational tradeoffs. No latency improvement is established
without workload measurements. Sharding by account must preserve global identity conflicts.
"""


def answer(control="reference"):
    code = REFERENCE
    if control == "reset_on_init":
        code = code.replace('con.commit()\n        finally:',
                            'con.execute("UPDATE accounts SET remaining=100")\n            con.commit()\n        finally:', 1)
    elif control == "lost_rejection":
        code = code.replace('con.execute("INSERT INTO decisions VALUES(?,?,?,?,?)",(key,account,amount,status,remaining))',
                            'if status == "accepted":\n                con.execute("INSERT INTO decisions VALUES(?,?,?,?,?)",(key,account,amount,status,remaining))')
    elif control == "current_remaining":
        code = code.replace("reply = {'status':old[2],'remaining':old[3]}",
                            "reply = {'status':old[2],'remaining':con.execute('SELECT remaining FROM accounts WHERE account=?',(account,)).fetchone()[0]}")
    elif control == "ignore_mismatch":
        code = code.replace("if old[:2] != (account, amount):", "if False:")
    elif control == "missing_ledger":
        code = code.replace('con.execute("INSERT INTO ledger VALUES(?,?,?)",(key,account,amount))', 'pass')
    elif control == "db_error_as_rejection":
        code = code.replace('con.execute("BEGIN IMMEDIATE")', 'raise sqlite3.OperationalError("database is locked")', 1)
        # A wrapper converting initialization failure to a fake business decision.
        code += '''
Original = Service
class Service:
    def __init__(self,path):
        try:
            self.inner=Original(path)
        except Exception:
            self.inner=None
    def apply(self,request):
        return {'status':'rejected','remaining':100}
'''
    elif control == "overspend":
        code = code.replace("if amount <= remaining:", "if True:")
    elif control != "reference":
        raise ValueError(control)
    return {"task_id": "E1", "code": code, "explanation": EXPLANATION,
            "control_label": control, "authored_control": True}


CONTROLS = ("reference", "reset_on_init", "lost_rejection", "current_remaining",
            "ignore_mismatch", "missing_ledger", "db_error_as_rejection", "overspend")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", choices=CONTROLS)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(answer(args.control), stream, indent=2)


if __name__ == "__main__":
    main()
