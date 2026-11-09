"""Known source mutations. These are development controls, not answer keys."""

from pathlib import Path


REFERENCE = Path(__file__).with_name("reference.py").read_text(encoding="utf-8")
EXPLANATION = "Authored development fixture; explanation quality has not been independently reviewed."


def source(name):
    text = REFERENCE
    mutations = {
        "reference": None,
        "exclusive_valid": ('db.execute("BEGIN IMMEDIATE")', 'db.execute("BEGIN EXCLUSIVE")'),
        "no_ledger": ('db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))', 'pass  # deliberately omit accepted ledger'),
        "no_rejection": ('db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))',
                         'if status == "accepted":\n                db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))'),
        "current_replay": ('"remaining": prior[3]', '"remaining": db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]'),
        "ignore_amount": ('prior[:2] != (account, amount)', 'prior[0] != account'),
        "ignore_account": ('prior[:2] != (account, amount)', 'prior[1] != amount'),
        "reset_initialization": ('INSERT OR IGNORE INTO accounts', 'INSERT OR REPLACE INTO accounts'),
        "wrong_debit": ('(remaining, account))', '(remaining - 1, account))'),
        "view_ledger": ('db.execute("CREATE TABLE IF NOT EXISTS ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER)")',
                        'db.execute("CREATE VIEW IF NOT EXISTS ledger AS SELECT key,account,amount FROM decisions WHERE status=\'accepted\'")'),
        "race": ('remaining = db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]',
                 'remaining = stale_remaining'),
        "uncommitted": None,
    }
    if name not in mutations:
        raise ValueError("unknown authored control")
    change = mutations[name]
    if change:
        assert change[0] in text
        text = text.replace(*change)
    if name == "view_ledger":
        text = text.replace('db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))', 'pass')
    if name == "uncommitted":
        start, apply = text.split("    def apply(self, request):", 1)
        text = start + "    def apply(self, request):" + apply.replace("db.commit()", "db.rollback()")
    if name == "race":
        # Deterministic development stress: read before acquiring the writer lock.
        # The evaluator itself never forces this internal interleaving.
        start, apply = text.split("    def apply(self, request):", 1)
        apply = apply.replace('db.execute("BEGIN IMMEDIATE")',
            'stale_remaining = db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]\n'
            '            import time\n            time.sleep(0.15)\n            db.execute("BEGIN IMMEDIATE")', 1)
        text = start + "    def apply(self, request):" + apply
    compile(text, "authored-control.py", "exec")
    return text


NEGATIVE_CONTROLS = ("no_ledger", "no_rejection", "current_replay", "ignore_amount",
                     "ignore_account", "reset_initialization", "wrong_debit",
                     "view_ledger", "uncommitted", "race")
