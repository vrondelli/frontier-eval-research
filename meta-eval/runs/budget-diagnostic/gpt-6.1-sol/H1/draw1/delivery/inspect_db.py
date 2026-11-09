"""Bounded independent inspector. No submitted Python runs in this process."""
import json
import os
from pathlib import Path
import sqlite3
import stat
import sys
import time


def inspect(path):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from oracle import TABLES
    path = Path(path).absolute()
    for suffix in ("", "-wal", "-shm", "-journal"):
        item = Path(str(path) + suffix)
        try:
            mode = item.lstat().st_mode
        except FileNotFoundError:
            if not suffix:
                raise ValueError("database missing")
            continue
        if not stat.S_ISREG(mode):
            raise ValueError("database and sidecars must be regular files")
    deadline = time.monotonic() + 2
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.5)
    try:
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA trusted_schema=OFF")
        con.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        types = {row[1]: row[2] for row in con.execute("PRAGMA table_list") if row[0] == "main"}
        result = {}
        for table, columns in TABLES.items():
            if types.get(table) != "table":
                raise ValueError(f"{table} must be a real table")
            info = list(con.execute(f'PRAGMA table_info("{table}")'))
            by_name = {row[1]: row for row in info}
            if any(c not in by_name for c in columns):
                raise ValueError(f"{table}: missing public columns")
            expected_types = {c: "INTEGER" if c in ("amount", "remaining") else "TEXT" for c in columns}
            if any(by_name[c][2].upper() != expected_types[c] for c in columns):
                raise ValueError(f"{table}: wrong declared column types")
            if [r[1] for r in sorted(info, key=lambda r: r[5]) if r[5]] != [columns[0]]:
                raise ValueError(f"{table}: incorrect primary key")
            names = ",".join(f'"{c}"' for c in columns)
            rows = list(con.execute(f'SELECT {names} FROM "{table}" LIMIT 100'))
            if len(rows) >= 100:
                raise ValueError(f"{table}: inspection row limit")
            result[table] = sorted([list(row) for row in rows])
        return result
    finally:
        con.close()


if __name__ == "__main__":
    if os.name == "posix":
        import resource
        for limit, value in ((resource.RLIMIT_AS, 512 * 1024**2),
                             (resource.RLIMIT_CPU, 3), (resource.RLIMIT_NOFILE, 256)):
            resource.setrlimit(limit, (value, value))
    try:
        output = json.dumps({"ok": True, "tables": inspect(sys.argv[1])}, allow_nan=False)
        if len(output.encode()) >= 65536:
            raise ValueError("inspection output exceeds 64 KiB")
        print(output)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"[:1000]}))
        raise SystemExit(1)
