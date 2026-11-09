"""Trusted serial model and independent, bounded SQLite inspection."""

from contextlib import closing
import json
import sqlite3
import stat
import time
from pathlib import Path


class ContractError(Exception):
    pass


class Model:
    def __init__(self):
        self.accounts = {"A": 100, "B": 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, request):
        key, account, amount = (request[x] for x in ("key", "account", "amount"))
        prior = self.decisions.get(key)
        if prior:
            if prior[1:3] != (account, amount):
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": prior[3], "remaining": prior[4]}
        status = "accepted" if self.accounts[account] >= amount else "rejected"
        if status == "accepted":
            self.accounts[account] -= amount
            self.ledger[key] = (key, account, amount)
        remaining = self.accounts[account]
        self.decisions[key] = (key, account, amount, status, remaining)
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": sorted((k, v) for k, v in self.accounts.items()),
            "decisions": sorted(self.decisions.values()),
            "ledger": sorted(self.ledger.values()),
        }


def check_reply(actual, expected):
    if not isinstance(actual, dict) or set(actual) != {"status", "remaining"}:
        raise ContractError("reply must contain exactly status and remaining")
    if type(actual["status"]) is not str:
        raise ContractError("status must be a string")
    remaining = actual["remaining"]
    if remaining is not None and type(remaining) is not int:
        raise ContractError("remaining must be an integer or null (booleans are invalid)")
    if actual != expected:
        raise ContractError(f"reply differs: expected {expected!r}, observed {actual!r}")


def overlap_model(requests, replies):
    """Accept either serial winner, never infer a fixed scheduler order."""
    errors = []
    for order in ((0, 1), (1, 0)):
        model = Model()
        expected = {}
        for i in order:
            expected[i] = model.apply(requests[i])
        try:
            for i in range(2):
                check_reply(replies[i], expected[i])
            return model, order
        except ContractError as exc:
            errors.append(str(exc))
    raise ContractError("overlap matches neither legal serial outcome: " + "; ".join(errors))


def inspect_database(database):
    """Call only after stopping workers. No candidate module is imported here."""
    database = Path(database).absolute()
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = Path(str(database) + suffix)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            if not suffix:
                raise ContractError("database is missing")
            continue
        # Reparse points include Windows junctions; never follow inspection links.
        if (not stat.S_ISREG(metadata.st_mode) or path.is_symlink()
                or getattr(metadata, "st_file_attributes", 0) & 0x400):
            raise ContractError("database and sidecars must be regular files")
        if metadata.st_size > 8 * 1024 * 1024:
            raise ContractError("inspection file exceeds 8 MiB")
    deadline = time.monotonic() + 2
    result = {}
    columns = {
        "accounts": ("account", "remaining"),
        "decisions": ("key", "account", "amount", "status", "remaining"),
        "ledger": ("key", "account", "amount"),
    }
    uri = database.as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=0.2)) as db:
            db.enable_load_extension(False)
            db.execute("PRAGMA query_only=ON")
            db.execute("PRAGMA trusted_schema=OFF")
            db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            for table, names in columns.items():
                row = db.execute(
                    "SELECT type, sql FROM sqlite_schema WHERE name=?", (table,)
                ).fetchone()
                if not row or row[0] != "table" or "VIRTUAL" in (row[1] or "").upper():
                    raise ContractError(f"{table} must be an ordinary table")
                info = db.execute(f'PRAGMA table_info("{table}")').fetchall()
                for name in names:
                    if name not in [item[1] for item in info]:
                        raise ContractError(f"missing public column {table}.{name}")
                primary = [(item[1], item[2].upper()) for item in info if item[5]]
                if primary != [(names[0], "TEXT")]:
                    raise ContractError(f"{table} must have the declared TEXT primary key")
                expected_types = {name: ("INTEGER" if name in ("amount", "remaining")
                                         else "TEXT") for name in names}
                if any(item[2].upper() != expected_types[item[1]]
                       for item in info if item[1] in names):
                    raise ContractError(f"{table} has incorrect declared column types")
                rows = db.execute(
                    'SELECT ' + ','.join('"' + name + '"' for name in names)
                    + f' FROM "{table}" LIMIT 101'
                ).fetchall()
                if len(rows) >= 100:
                    raise ContractError(f"{table} exceeds the declared inspection row bound")
                for values in rows:
                    for name, value in zip(names, values):
                        expected_type = int if expected_types[name] == "INTEGER" else str
                        if type(value) is not expected_type:
                            raise ContractError(f"invalid SQLite storage type {table}.{name}")
                result[table] = sorted(rows)
    except (sqlite3.Error, OSError, ValueError) as exc:
        raise ContractError(f"independent inspection failed: {exc}") from exc
    return result


def check_snapshot(actual, expected):
    if actual != expected:
        raise ContractError("SQL state differs from the serial model: "
                            + json.dumps({"expected": expected, "observed": actual}))
