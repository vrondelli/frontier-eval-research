"""Trusted independent SQL inspection, run after every worker is stopped.

Runs in a separate bounded read-only sandbox without candidate source.
"""
import json
import os
import sqlite3
import stat
import sys
import time


TABLES = {
    "accounts": [("account", "TEXT"), ("remaining", "INTEGER")],
    "decisions": [("key", "TEXT"), ("account", "TEXT"), ("amount", "INTEGER"),
                  ("status", "TEXT"), ("remaining", "INTEGER")],
    "ledger": [("key", "TEXT"), ("account", "TEXT"), ("amount", "INTEGER")],
}


def inspect(path):
    for suffix in ("", "-wal", "-shm", "-journal"):
        target = path + suffix
        if os.path.lexists(target) and not stat.S_ISREG(os.lstat(target).st_mode):
            raise ValueError("database and sidecars must be regular files")
    if not os.path.isfile(path):
        raise ValueError("database is missing")
    deadline = time.monotonic() + 2
    connection = sqlite3.connect("file:" + path + "?mode=ro", uri=True, timeout=0.1)
    try:
        connection.enable_load_extension(False)
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        if connection.execute("PRAGMA quick_check(1)").fetchone() != ("ok",):
            raise ValueError("database integrity check failed")
        result = {}
        for table, columns in TABLES.items():
            kind = connection.execute(
                "SELECT type FROM sqlite_master WHERE name=?", (table,)).fetchone()
            if kind != ("table",):
                raise ValueError(table + " must be a real table")
            ddl = connection.execute(
                "SELECT sql FROM sqlite_master WHERE name=?", (table,)).fetchone()[0]
            if "VIRTUAL" in ddl.upper().split():
                raise ValueError("virtual tables are not inspection targets")
            info = connection.execute("PRAGMA table_info(" + table + ")").fetchall()
            if [(r[1], r[2].upper()) for r in info] != columns:
                raise ValueError(table + " does not have the declared public columns")
            if [r[1] for r in info if r[5]] != [columns[0][0]]:
                raise ValueError(table + " requires the declared primary key")
            names = [name for name, _ in columns]
            rows = connection.execute(
                "SELECT " + ",".join('"' + name + '"' for name in names)
                + " FROM " + table + " ORDER BY 1 LIMIT 100").fetchall()
            if len(rows) >= 100:
                raise ValueError("inspection row limit exceeded")
            for row in rows:
                for cell, (_, declared) in zip(row, columns):
                    expected_type = str if declared == "TEXT" else int
                    if type(cell) is not expected_type:
                        raise ValueError("unexpected stored SQLite type")
            result[table] = [dict(zip(names, row)) for row in rows]
        return result
    finally:
        connection.close()


def fault(path, action):
    # Validate the public file and schema before opening it for a trusted write.
    inspect(path)
    connection = sqlite3.connect(path, timeout=0.1)
    try:
        connection.execute("PRAGMA trusted_schema=OFF")
        if action == "install":
            connection.execute('''CREATE TRIGGER e1_injected_ledger_error
                BEFORE INSERT ON ledger BEGIN
                SELECT RAISE(ABORT, 'e1 injected ledger write failure'); END''')
        elif action == "remove":
            connection.execute("DROP TRIGGER e1_injected_ledger_error")
        else:
            raise ValueError("unknown fault action")
        connection.commit()
    finally:
        connection.close()
    return {"fault": action}


if __name__ == "__main__":
    try:
        result = (fault(sys.argv[1], sys.argv[2]) if len(sys.argv) == 3
                  else {"snapshot": inspect(sys.argv[1])})
        print(json.dumps(result, allow_nan=False))
    except BaseException as error:
        print(json.dumps({"error": type(error).__name__, "detail": str(error)[:2000]}))
        sys.exit(1)
