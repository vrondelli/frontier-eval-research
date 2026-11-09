"""Disposable workers and bounded, independent SQL inspection."""
import json
from contextlib import closing
import os
from pathlib import Path
import queue
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time

REPLY_SECONDS = 6
MAX_LINE = 65536
WORKER = Path(__file__).with_name('worker.py').resolve()


class Unavailable(Exception):
    pass


class WorkerFailure(Exception):
    pass


def sandbox_command(source, state, probe=False):
    if sys.platform != 'linux' or not shutil.which('bwrap') or not Path('/usr/bin/python3').is_file():
        raise Unavailable('Requires Linux, bwrap, /usr/bin/python3 and working unprivileged namespaces')
    command = ['bwrap', '--unshare-all', '--die-with-parent', '--new-session',
               '--cap-drop', 'ALL', '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin']
    for name in ('/usr', '/lib', '/lib64', '/bin'):
        if Path(name).exists():
            command += ['--ro-bind', name, name]
    command += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
                '--bind', str(state), '/state', '--ro-bind', str(source), '/candidate.py',
                '--ro-bind', str(WORKER), '/worker.py', '--chdir', '/state']
    if probe:
        return command + ['/usr/bin/python3', '-I', '-B', '-c', 'print("sandbox-ready")']
    return command + ['/usr/bin/python3', '-I', '-B', '/worker.py', '/candidate.py', '/state/ledger.db', 'limits']


def require_sandbox(source, state):
    try:
        result = subprocess.run(sandbox_command(source, state, probe=True), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=6,
                                env={}, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Unavailable('Sandbox probe failed: ' + type(error).__name__) from error
    if result.returncode or result.stdout.strip() != b'sandbox-ready':
        raise Unavailable('Sandbox probe failed: ' + result.stderr.decode('utf-8', 'replace')[:500])


class Worker:
    def __init__(self, source, state, trusted_control=False):
        # This mode is solely for repository-authored verification controls.
        # The grade CLI never exposes it for submissions.
        command = ([sys.executable, '-I', '-B', str(WORKER), str(source), str(state / 'ledger.db'), 'trusted']
                   if trusted_control else sandbox_command(source, state))
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, cwd=state, env={},
                                        start_new_session=(os.name != 'nt'))
        self.queue = queue.Queue(maxsize=4)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for _ in range(3):
                raw = self.process.stdout.readline(MAX_LINE + 1)
                if not raw or len(raw) > MAX_LINE or not raw.endswith(b'\n'):
                    self.queue.put_nowait(WorkerFailure('Missing, oversized or incomplete worker message'))
                    return
                self.queue.put_nowait(json.loads(raw))
        except Exception:
            try:
                self.queue.put_nowait(WorkerFailure('Invalid worker protocol'))
            except queue.Full:
                pass

    def read(self, deadline):
        try:
            result = self.queue.get(timeout=max(0, deadline - time.monotonic()))
        except queue.Empty as error:
            raise WorkerFailure('Six-second worker deadline exceeded') from error
        if isinstance(result, Exception):
            raise result
        return result

    def close(self):
        if os.name != 'nt':
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=2)
        self.process.stdin.close()
        self.process.stdout.close()


def run_batch(source, state, requests, trusted_control=False):
    workers = []
    records = []
    try:
        deadline = time.monotonic() + REPLY_SECONDS
        for _ in requests:
            workers.append(Worker(source, state, trusted_control))
        for worker in workers:
            if worker.read(deadline) != {'ready': True}:
                raise WorkerFailure('Expected ready acknowledgement')
        deadline = time.monotonic() + REPLY_SECONDS
        for worker, request in zip(workers, requests):
            worker.process.stdin.write(json.dumps(request).encode() + b'\n')
            worker.process.stdin.flush()
        for worker, request in zip(workers, requests):
            reply = worker.read(deadline)
            worker.process.wait(timeout=max(0.001, deadline - time.monotonic()))
            if worker.process.returncode != 0:
                raise WorkerFailure('Worker did not exit successfully')
            records.append({'request': request, 'response': reply, 'exit_code': worker.process.returncode})
        return records
    except (OSError, subprocess.TimeoutExpired) as error:
        raise WorkerFailure(type(error).__name__) from error
    finally:
        for worker in workers:
            worker.close()


def safe_database(state):
    path = state / 'ledger.db'
    for file in state.glob('ledger.db*'):
        if file.is_symlink() or not file.is_file() or file.stat().st_size > 8 * 1024**2:
            raise WorkerFailure('Database/sidecars must be regular files <=8 MiB without symlinks')
    if not path.is_file():
        raise WorkerFailure('Missing database')
    return path


def inspect(state):
    path = safe_database(state)
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=0.2)
    deadline = time.monotonic() + 2
    db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
    try:
        db.execute('PRAGMA query_only=ON')
        db.execute('PRAGMA trusted_schema=OFF')
        columns = {'accounts': [('account', 'TEXT'), ('remaining', 'INTEGER')],
                   'decisions': [('key', 'TEXT'), ('account', 'TEXT'), ('amount', 'INTEGER'),
                                 ('status', 'TEXT'), ('remaining', 'INTEGER')],
                   'ledger': [('key', 'TEXT'), ('account', 'TEXT'), ('amount', 'INTEGER')]}
        result = {}
        for name, expected in columns.items():
            kind = db.execute('SELECT type FROM sqlite_master WHERE name=?', (name,)).fetchone()
            if kind != ('table',):
                raise WorkerFailure(name + ' must be a real table')
            info = db.execute('PRAGMA table_info(' + name + ')').fetchall()
            found = {row[1]: (row[2].upper(), row[5]) for row in info}
            if any(found.get(col, (None,))[0] != typ for col, typ in expected):
                raise WorkerFailure('Missing/wrong declared columns in ' + name)
            if found[expected[0][0]][1] != 1 or any(row[5] for row in info if row[1] != expected[0][0]):
                raise WorkerFailure('Wrong primary key in ' + name)
            query = 'SELECT ' + ','.join(col for col, _ in expected) + ' FROM ' + name
            rows = db.execute(query).fetchmany(100)
            if len(rows) >= 100:
                raise WorkerFailure('Inspection requires fewer than 100 rows per table')
            for row in rows:
                if any(type(value) is not (int if typ == 'INTEGER' else str)
                       for value, (_, typ) in zip(row, expected)):
                    raise WorkerFailure('Wrong stored value types in ' + name)
            result[name] = sorted(map(list, rows))
        return result
    finally:
        db.close()


def storage_fault(state, table, install):
    path = safe_database(state)
    with closing(sqlite3.connect(path, timeout=0.2)) as db, db:
        if install:
            db.execute('CREATE TRIGGER e1_fault BEFORE INSERT ON ' + table +
                       " BEGIN SELECT RAISE(ABORT, 'e1 injected storage error'); END")
        else:
            db.execute('DROP TRIGGER e1_fault')
