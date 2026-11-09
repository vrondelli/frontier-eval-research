"""Trusted, bounded, independent read-only SQLite inspection subprocess."""
import json
import sqlite3
import sys
from pathlib import Path


def inspect(state):
    root = Path(state)
    for entry in root.iterdir():
        if entry.is_symlink():
            raise ValueError('symlink in state directory')
    path = root / 'service.sqlite'
    if not path.is_file() or path.stat().st_size > 8 * 1024**2:
        raise ValueError('database missing or oversized')
    db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=0.5)
    try:
        db.execute('PRAGMA trusted_schema=OFF')
        db.enable_load_extension(False)
        ticks = 0

        def progress():
            nonlocal ticks
            ticks += 1
            return ticks > 10000

        db.set_progress_handler(progress, 100)
        if db.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
            raise ValueError('database integrity failure')
        result = {}
        columns = {
            'accounts': 'account,remaining',
            'decisions': 'key,account,amount,status,remaining',
            'ledger': 'key,account,amount',
        }
        declarations = {
            'accounts': [('account', 'TEXT', 1), ('remaining', 'INTEGER', 0)],
            'decisions': [('key', 'TEXT', 1), ('account', 'TEXT', 0),
                          ('amount', 'INTEGER', 0), ('status', 'TEXT', 0),
                          ('remaining', 'INTEGER', 0)],
            'ledger': [('key', 'TEXT', 1), ('account', 'TEXT', 0), ('amount', 'INTEGER', 0)],
        }
        for table, cols in columns.items():
            kind = db.execute('SELECT type,sql FROM sqlite_master WHERE name=?', (table,)).fetchall()
            if len(kind) != 1 or kind[0][0] != 'table' or 'VIRTUAL' in kind[0][1].upper().split():
                raise ValueError(f'{table} must be a real table')
            declared = [(r[1], r[2].upper(), r[5])
                        for r in db.execute(f'PRAGMA table_info({table})')]
            if declared != declarations[table]:
                raise ValueError(f'{table} does not have the declared columns and primary key')
            rows = db.execute(f'SELECT {cols} FROM {table} LIMIT 100').fetchall()
            if len(rows) >= 100:
                raise ValueError(f'{table} has too many rows')
            result[table] = rows
        return result
    finally:
        db.close()


if __name__ == '__main__':
    if sys.platform == 'linux':
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    try:
        print(json.dumps(inspect(sys.argv[1]), allow_nan=False))
    except Exception as exc:
        print(json.dumps({'inspection_error': str(exc)}))
        sys.exit(1)
