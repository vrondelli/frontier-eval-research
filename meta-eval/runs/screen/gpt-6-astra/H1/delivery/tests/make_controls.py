"""Emit newly authored grader controls. These are not answers from evaluated models."""
from pathlib import Path
import json
import sys


def source(name):
    code = (Path(__file__).with_name("control_service.py")).read_text(encoding="utf-8")
    replacements = {
        "reference": None,
        "missing_ledger": ('connection.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))', 'pass  # deliberately missing ledger'),
        "lost_rejection": ('connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))',
                           'if accepted: connection.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))'),
        "ignore_mismatch": ('if (account, amount) != prior[:2]:', 'if False:'),
        "account_scoped_key": ('key, account, amount = (request[k] for k in ("key", "account", "amount"))',
                               'key, account, amount = (request[k] for k in ("key", "account", "amount"))\n            key = account + ":" + key'),
        "historical_remaining": ('result = {"status": prior[2], "remaining": prior[3]}',
                                 'result = {"status": prior[2], "remaining": connection.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]}'),
        "reset_on_init": ('INSERT OR IGNORE INTO accounts VALUES (?,100)', 'INSERT OR REPLACE INTO accounts VALUES (?,100)'),
        "always_reject": ('accepted = amount <= remaining', 'accepted = False'),
        "overdraw": ('accepted = amount <= remaining', 'accepted = True'),
    }
    replacement = replacements[name]
    if replacement:
        before, after = replacement
        if code.count(before) != 1:
            raise ValueError("control mutation target must occur exactly once")
        code = code.replace(before, after)
    return code


def answer(name):
    return {"task_id": "E1", "code": source(name),
            "explanation": "Authored grader control only. This placeholder is not an evaluated explanation."}


if __name__ == "__main__":
    print(json.dumps(answer(sys.argv[1] if len(sys.argv) > 1 else "reference"), indent=2))
