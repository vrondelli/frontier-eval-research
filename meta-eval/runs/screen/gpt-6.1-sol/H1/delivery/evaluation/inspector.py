"""Independent bounded, read-only SQLite inspection after all workers stop."""
import contextlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import sys
import time


TABLES = {
    "accounts": ("account", "remaining"),
    "decisions": ("key", "account", "amount", "status", "remaining"),
    "ledger": ("key", "account", "amount"),
}


def inspect(path):
    path = Path(path)
    for suffix in ("", "-wal", "-shm", "-journal"):
        target = Path(str(path) + suffix)
        try:
            mode = target.lstat().st_mode
        except FileNotFoundError:
            if not suffix:
                raise ValueError("public database is missing")
            continue
        if not stat.S_ISREG(mode):
            raise ValueError("database and sidecars must be regular files")
    deadline = time.monotonic() + 1.5
    with contextlib.closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=0.2)) as conn:
        conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1024 * 1024)
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA trusted_schema=OFF")
        conn.set_progress_handler(lambda: time.monotonic() > deadline, 1000)
        result = {}
        for table, columns in TABLES.items():
            definition = conn.execute(
                "SELECT type,sql FROM sqlite_master WHERE name=?", (table,)
            ).fetchone()
            if (not definition or definition[0] != "table" or not definition[1]
                    or "VIRTUAL" in definition[1].upper()):
                raise ValueError(f"{table} must be a real, non-virtual table")
            info = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
            names = {row[1] for row in info}
            if not set(columns) <= names:
                raise ValueError(f"missing public columns in {table}")
            primary = [row[1] for row in info if row[5]]
            if primary != [columns[0]]:
                raise ValueError(f"{table} must have the declared primary key")
            rows = conn.execute(f'SELECT {",".join(columns)} FROM "{table}" LIMIT 101').fetchall()
            if len(rows) >= 100:
                raise ValueError(f"{table} must have fewer than 100 rows")
            result[table] = sorted([list(row) for row in rows], key=lambda row: str(row[0]))
        return result


if __name__ == "__main__":
    # Parent also imposes a wall timeout. Never import or execute the candidate here.
    if os.name == "posix":
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    try:
        print(json.dumps({"snapshot": inspect(sys.argv[1])}, allow_nan=False))
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))
        sys.exit(2)
