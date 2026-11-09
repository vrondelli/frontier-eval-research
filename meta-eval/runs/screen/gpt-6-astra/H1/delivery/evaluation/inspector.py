"""Trusted independent SQL inspector, executed separately after workers stop."""
import json
import os
from pathlib import Path
import sqlite3
import stat


TABLES = {
    "accounts": ("account", "remaining"),
    "decisions": ("key", "account", "amount", "status", "remaining"),
    "ledger": ("key", "account", "amount"),
}


def inspect(path):
    path = Path(path)
    for candidate in [path, *(Path(str(path) + suffix) for suffix in ("-wal", "-shm", "-journal"))]:
        if os.path.lexists(candidate):
            info = candidate.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("database/sidecars must be regular files, not symlinks")
            if info.st_size > 8 * 1024 * 1024:
                raise ValueError("database/sidecar size limit")
        elif candidate == path:
            raise ValueError("database missing")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=0.1)
    try:
        connection.enable_load_extension(False)
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("PRAGMA query_only=ON")
        # Bound malicious/corrupt database work independently of the outer timeout.
        steps = 0
        def progress():
            nonlocal steps
            steps += 1
            return int(steps > 10000)
        connection.set_progress_handler(progress, 100)
        result = {}
        for name, columns in TABLES.items():
            schema = connection.execute(
                "SELECT type,sql FROM sqlite_master WHERE name=?", (name,)).fetchone()
            if not schema or schema[0] != "table" or "VIRTUAL" in schema[1].upper():
                raise ValueError(f"{name} must be a real ordinary table")
            info = connection.execute(f'PRAGMA table_info("{name}")').fetchall()
            if not set(columns).issubset({row[1] for row in info}):
                raise ValueError(f"{name} missing required columns")
            if [(row[1], row[5]) for row in info if row[5]] != [(columns[0], 1)]:
                raise ValueError(f"{name} must use its declared primary key")
            selection = ",".join('"' + column + '"' for column in columns)
            rows = connection.execute(f'SELECT {selection} FROM "{name}" LIMIT 100').fetchall()
            if len(rows) >= 100:
                raise ValueError(f"{name} exceeds declared row bound")
            result[name] = [list(row) for row in rows]
        return result
    finally:
        connection.close()


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        print(json.dumps({"snapshot": inspect("/state/ledger.sqlite3")}, allow_nan=False))
    except Exception as exc:
        print(json.dumps({"inspection_error": type(exc).__name__, "message": str(exc)[:1000]}))
        raise SystemExit(1)
