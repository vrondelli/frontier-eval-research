"""Separate bounded read-only inspection process; no candidate imports."""
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

TABLES = {
    "accounts": ("account", "remaining"),
    "decisions": ("key", "account", "amount", "status", "remaining"),
    "ledger": ("key", "account", "amount"),
}


def inspect(path):
    path = Path(path).absolute()
    for suffix in ("", "-wal", "-shm", "-journal"):
        target = Path(str(path) + suffix)
        if target.is_symlink():
            raise ValueError("database and sidecars must not be symlinks")
        if target.exists() and (not target.is_file() or target.stat().st_size > 8 * 1024 * 1024):
            raise ValueError("invalid or oversized inspection target")
    if not path.is_file():
        raise ValueError("database missing")
    deadline = time.monotonic() + 1.5
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.2)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("database integrity check failed")
        result = {}
        for table, columns in TABLES.items():
            definition = db.execute("SELECT type,sql FROM sqlite_schema WHERE name=?", (table,)).fetchone()
            if not definition or definition[0] != "table" or "VIRTUAL" in definition[1].upper():
                raise ValueError(f"{table} must be a real table")
            info = db.execute(f'PRAGMA table_info("{table}")').fetchall()
            names = {row[1] for row in info}
            if not set(columns) <= names or [row[1] for row in info if row[5]] != [columns[0]]:
                raise ValueError(f"{table} missing public columns or primary key")
            rows = db.execute(f'SELECT {",".join(chr(34)+c+chr(34) for c in columns)} FROM "{table}" LIMIT 100').fetchall()
            if len(rows) >= 100:
                raise ValueError("inspection requires fewer than 100 rows per table")
            for row in rows:
                for column, value in zip(columns, row):
                    if column in ("amount", "remaining"):
                        if type(value) is not int or value < 0 or (column == "amount" and value == 0):
                            raise ValueError(f"invalid {table}.{column}")
                    elif type(value) is not str or len(value) > 1024:
                        raise ValueError(f"invalid {table}.{column}")
            result[table] = sorted([list(row) for row in rows], key=lambda row: row[0])
        return result
    finally:
        db.close()


if __name__ == "__main__":
    try:
        if os.name == "posix":
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        print(json.dumps({"snapshot": inspect(sys.argv[1])}, allow_nan=False))
    except BaseException as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)[:1000]}))
        sys.exit(1)
