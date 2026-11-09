"""Bounded, read-only, independent public-state inspection (no candidate import)."""
from pathlib import Path
from contextlib import closing
import json
import re
import sqlite3
import sys
import time

COLUMNS = {
    "accounts": ("account", "remaining"),
    "decisions": ("key", "account", "amount", "status", "remaining"),
    "ledger": ("key", "account", "amount"),
}


def inspect(path):
    path = Path(path).absolute()
    for file in [path, *(Path(str(path) + suffix) for suffix in ("-wal", "-shm", "-journal"))]:
        if file.is_symlink() or (file.exists() and not file.is_file()):
            raise ValueError("database and sidecars must be regular, non-symlink files")
    if not path.is_file():
        raise ValueError("missing public database")
    deadline = time.monotonic() + 3
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.1)) as db:
        db.enable_load_extension(False)
        db.execute("PRAGMA trusted_schema=OFF")
        db.execute("PRAGMA query_only=ON")
        db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 65536)
        db.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, 128)
        db.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 65536)
        db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        if db.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise ValueError("database integrity check failed")
        result = {}
        for table, names in COLUMNS.items():
            kind = db.execute("SELECT type,sql FROM sqlite_schema WHERE name=?", (table,)).fetchone()
            if (not kind or kind[0] != "table" or not kind[1]
                    or re.match(r"\s*CREATE\s+VIRTUAL\s+TABLE\b", kind[1], re.IGNORECASE)):
                raise ValueError(f"{table} must be an ordinary real table")
            info = db.execute(f'PRAGMA table_info("{table}")').fetchall()
            if not set(names).issubset({row[1] for row in info}):
                raise ValueError(f"{table} missing declared columns")
            if [row[1] for row in info if row[5]] != [names[0]]:
                raise ValueError(f"{table} must have the declared single-column primary key")
            columns = ",".join(f'"{name}"' for name in names)
            rows = db.execute(f'SELECT {columns} FROM "{table}" ORDER BY "{names[0]}" LIMIT 101').fetchall()
            if len(rows) >= 100:
                raise ValueError(f"{table} exceeds the disclosed <100 row bound")
            result[table] = [list(row) for row in rows]
        return result


if __name__ == "__main__":
    try:
        if sys.platform == "linux":
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
            resource.setrlimit(resource.RLIMIT_CPU, (4, 4))
            resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
        print(json.dumps({"snapshot": inspect(sys.argv[1])}, allow_nan=False))
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {str(exc)[:2048]}"}))
        sys.exit(2)
