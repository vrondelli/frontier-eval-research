"""Run by the parent interpreter, outside the candidate sandbox, with a deadline."""
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import stat
import sys


SCHEMA = {
    "accounts": [("account", "TEXT"), ("remaining", "INTEGER")],
    "decisions": [("key", "TEXT"), ("account", "TEXT"), ("amount", "INTEGER"),
                  ("status", "TEXT"), ("remaining", "INTEGER")],
    "ledger": [("key", "TEXT"), ("account", "TEXT"), ("amount", "INTEGER")],
}


def inspect(path):
    path = Path(path).absolute()
    for suffix in ("", "-wal", "-shm", "-journal"):
        target = Path(str(path) + suffix)
        if target.exists() or target.is_symlink():
            if not stat.S_ISREG(target.lstat().st_mode):
                raise ValueError("database and sidecars must be regular files")
    if not path.is_file():
        raise ValueError("missing database")
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.5)) as db:
        db.execute("PRAGMA trusted_schema=OFF")
        budget = [0]

        def progress():
            budget[0] += 1
            return int(budget[0] > 1000)

        db.set_progress_handler(progress, 1000)
        snapshot = {}
        for table, columns in SCHEMA.items():
            entry = db.execute("SELECT type,sql FROM sqlite_master WHERE name=?", (table,)).fetchone()
            if not entry or entry[0] != "table" or "VIRTUAL" in (entry[1] or "").upper():
                raise ValueError(table + " must be a real, nonvirtual table")
            info = db.execute('PRAGMA table_info("' + table + '")').fetchall()
            actual = [(r[1], r[2].upper()) for r in info]
            if actual != columns or [r[1] for r in info if r[5]] != [columns[0][0]]:
                raise ValueError(table + " has the wrong public schema or primary key")
            names = ",".join('"' + c[0] + '"' for c in columns)
            rows = db.execute('SELECT ' + names + ' FROM "' + table + '" ORDER BY 1 LIMIT 100').fetchall()
            if len(rows) >= 100:
                raise ValueError("inspection row limit exceeded")
            for row in rows:
                for value, (_, kind) in zip(row, columns):
                    expected = str if kind == "TEXT" else int
                    if type(value) is not expected:
                        raise ValueError(table + " contains an invalid value type")
            snapshot[table] = [list(row) for row in rows]
        return snapshot


if __name__ == "__main__":
    try:
        print(json.dumps({"snapshot": inspect(sys.argv[1])}, allow_nan=False))
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__ + ": " + str(exc)[:500]}))
        sys.exit(1)
