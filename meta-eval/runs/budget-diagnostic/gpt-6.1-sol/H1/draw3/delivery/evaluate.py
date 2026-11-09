"""E1 evaluator: no candidate execution outside Linux bubblewrap."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
REPETITIONS = 3
REPLY_SECONDS = 6
MAX_REPLY = 64 * 1024


class EvaluationError(Exception):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def requests():
    return [
        {'key': 'overlap-1', 'account': 'A', 'amount': 60},
        {'key': 'overlap-2', 'account': 'A', 'amount': 60},
    ]


class Oracle:
    """Enumerate the two legal serial orders; never trust candidate state/replies."""
    def __init__(self):
        self.balances = {'A': 100, 'B': 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, req):
        key, account, amount = req['key'], req['account'], req['amount']
        if key in self.decisions:
            old = self.decisions[key]
            if old[:2] != [account, amount]:
                return {'status': 'payload_mismatch', 'remaining': None}
            return {'status': old[2], 'remaining': old[3]}
        status = 'accepted' if amount <= self.balances[account] else 'rejected'
        if status == 'accepted':
            self.balances[account] -= amount
            self.ledger[key] = [account, amount]
        remaining = self.balances[account]
        self.decisions[key] = [account, amount, status, remaining]
        return {'status': status, 'remaining': remaining}

    def snapshot(self):
        return {
            'accounts': [[a, n] for a, n in sorted(self.balances.items())],
            'decisions': [[k] + v for k, v in sorted(self.decisions.items())],
            'ledger': [[k] + v for k, v in sorted(self.ledger.items())],
        }


def normalize_snapshot(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {'accounts', 'decisions', 'ledger'}:
        raise EvaluationError('invalid inspection result')
    result = {}
    types = {'accounts': (str, int), 'decisions': (str, str, int, str, int),
             'ledger': (str, str, int)}
    for table, expected_types in types.items():
        rows = snapshot[table]
        if not isinstance(rows, list):
            raise EvaluationError(f'invalid {table} rows')
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) != len(expected_types):
                raise EvaluationError(f'invalid {table} row')
            if any(type(v) is not t for v, t in zip(row, expected_types)):
                raise EvaluationError(f'invalid {table} value types')
        result[table] = sorted([list(row) for row in rows])
    return result


def check_reply(actual, expected):
    if not isinstance(actual, dict) or set(actual) != {'status', 'remaining'}:
        raise EvaluationError('reply must contain exactly status and remaining')
    if type(actual['status']) is not str:
        raise EvaluationError('status must be a string')
    remaining = actual['remaining']
    if remaining is not None and type(remaining) is not int:
        raise EvaluationError('remaining must be an integer or null')
    if actual != expected:
        raise EvaluationError(f'reply differs: expected {expected}, observed {actual}')


def followups():
    one, two = requests()
    return [one, two,
            {**one, 'amount': 1}, {**two, 'account': 'B'},
            {'key': 'b-full', 'account': 'B', 'amount': 100},
            {'key': 'a-tail', 'account': 'A', 'amount': 40},
            one, two,
            {'key': 'a-empty', 'account': 'A', 'amount': 1},
            {'key': 'a-empty', 'account': 'A', 'amount': 1},
            {'key': 'b-full', 'account': 'B', 'amount': 100}]


def verify_trace(trace):
    """All observed replies and each independent checkpoint must fit one order."""
    failures = []
    for order in ((0, 1), (1, 0)):
        oracle = Oracle()
        try:
            if len(trace['overlap']) != 2 or len(trace['steps']) != len(followups()):
                raise EvaluationError('incomplete trace')
            pair = requests()
            for index in order:
                check_reply(trace['overlap'][index], oracle.apply(pair[index]))
            if normalize_snapshot(trace['after_overlap']) != oracle.snapshot():
                raise EvaluationError('on-disk state differs after overlap')
            for step, req in zip(trace['steps'], followups()):
                if step['request'] != req:
                    raise EvaluationError('request transcript differs')
                check_reply(step['reply'], oracle.apply(req))
                if normalize_snapshot(step['snapshot']) != oracle.snapshot():
                    raise EvaluationError('on-disk state differs after request')
            return {'passed': True, 'permitted_serial_order': list(order)}
        except (EvaluationError, KeyError, TypeError) as exc:
            failures.append(str(exc))
    return {'passed': False, 'order_failures': failures}


def sandbox_command(state, code):
    cmd = [shutil.which('bwrap'), '--die-with-parent', '--unshare-all', '--new-session',
           '--clearenv', '--ro-bind', '/usr', '/usr']
    for directory in ('/lib', '/lib64', '/bin'):
        if Path(directory).exists():
            cmd += ['--ro-bind', directory, directory]
    cmd += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
            '--dir', '/code', '--ro-bind', str(code), '/code/candidate.py',
            '--ro-bind', str(ROOT / 'worker.py'), '/code/worker.py',
            '--bind', str(state), '/state', '--chdir', '/state', '--remount-ro', '/',
            '--setenv', 'PATH', '/usr/bin', '--setenv', 'PYTHONDONTWRITEBYTECODE', '1',
            '--setenv', 'LC_ALL', 'C.UTF-8', '/usr/bin/python3', '-I', '-B', '-u',
            '-c', "import sys;sys.path.insert(0,'/code');exec(compile(open('/code/worker.py').read(),'/code/worker.py','exec'))"]
    return cmd


def availability():
    if sys.platform != 'linux':
        return 'Linux is required; candidate code was not executed'
    if not shutil.which('bwrap') or not Path('/usr/bin/python3').is_file():
        return 'bubblewrap and /usr/bin/python3 are required'
    # Use the real mounts and namespaces before introducing any candidate source.
    with tempfile.TemporaryDirectory(prefix='e1-preflight-') as directory:
        root = Path(directory)
        (root / 'state').mkdir()
        code = root / 'candidate.py'
        code.write_text('raise RuntimeError("preflight never imports this")\n')
        cmd = sandbox_command(root / 'state', code)
        cmd = cmd[:cmd.index('/usr/bin/python3')] + ['/usr/bin/python3', '-I', '-c', 'print("ready")']
        try:
            done = subprocess.run(cmd, capture_output=True, timeout=REPLY_SECONDS)
            if done.returncode != 0 or done.stdout != b'ready\n':
                return 'isolation preflight failed: ' + done.stderr[:2048].decode(errors='replace')
        except (OSError, subprocess.TimeoutExpired) as exc:
            return 'isolation preflight failed: ' + str(exc)
    return None


class Worker:
    def __init__(self, state, code, req):
        self.started = time.monotonic()
        self.buffer = b''
        self.process = subprocess.Popen(sandbox_command(state, code), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                        start_new_session=True, bufsize=0)
        self.process.stdin.write((canonical(req) + '\n').encode())
        self.process.stdin.flush()

    def line(self, deadline):
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            while b'\n' not in self.buffer:
                wait = deadline - time.monotonic()
                if wait <= 0 or not selector.select(wait):
                    raise EvaluationError('worker reply timeout')
                block = os.read(self.process.stdout.fileno(), 4096)
                if not block:
                    raise EvaluationError('worker exited without a complete reply')
                self.buffer += block
                if len(self.buffer) > MAX_REPLY:
                    raise EvaluationError('worker reply exceeds 64 KiB')
        line, self.buffer = self.buffer.split(b'\n', 1)
        try:
            return json.loads(line)
        except (UnicodeError, ValueError) as exc:
            raise EvaluationError('worker emitted invalid JSON') from exc

    def arm(self):
        if self.line(self.started + REPLY_SECONDS) != {'armed': True}:
            raise EvaluationError('invalid worker barrier acknowledgement')

    def release(self):
        self.deadline = time.monotonic() + REPLY_SECONDS
        self.process.stdin.write(b'go\n')
        self.process.stdin.flush()

    def result(self):
        message = self.line(self.deadline)
        if not isinstance(message, dict) or set(message) != {'reply'}:
            raise EvaluationError('invalid worker reply envelope')
        try:
            self.process.wait(timeout=max(0.001, self.deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise EvaluationError('worker did not exit after replying') from exc
        os.set_blocking(self.process.stdout.fileno(), False)
        try:
            tail = os.read(self.process.stdout.fileno(), MAX_REPLY + 1)
        except BlockingIOError as exc:
            raise EvaluationError('worker left protocol stdout open') from exc
        if self.process.returncode != 0 or self.buffer or tail:
            raise EvaluationError('worker exit failure or extraneous output')
        return message['reply']

    def close(self):
        # Kill the sandbox group even after its leader has exited. The private PID
        # namespace also prevents surviving candidate descendants after teardown.
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.process.wait(timeout=2)
        self.process.stdin.close()
        self.process.stdout.close()


def run_batch(state, code, batch, events=None):
    workers = []
    event = {'requests': batch, 'workers': []}
    if events is not None:
        events.append(event)

    def receive(worker, record):
        try:
            record['reply'] = worker.result()
            return record['reply']
        except Exception as exc:
            record['error'] = str(exc)
            raise

    try:
        for req in batch:
            workers.append(Worker(state, code, req))
            event['workers'].append({'request': req})
        # Read concurrently so waiting on a slow first worker cannot cause a
        # timely second reply to be falsely labeled as past its own deadline.
        with ThreadPoolExecutor(max_workers=len(workers)) as pool:
            armed = [pool.submit(worker.arm) for worker in workers]
            for future in armed:
                future.result()
            event['both_armed_before_release'] = len(workers) == 2
            for worker in workers:
                worker.release()
            pending = [pool.submit(receive, worker, record)
                       for worker, record in zip(workers, event['workers'])]
            return [future.result() for future in pending]
    except Exception as exc:
        event['error'] = str(exc)
        raise
    finally:
        for worker, record in zip(workers, event['workers']):
            worker.close()
            record['returncode'] = worker.process.returncode


def inspect_state(state):
    try:
        result = subprocess.run([sys.executable, '-I', str(ROOT / 'inspector.py'), str(state)],
                                capture_output=True, timeout=3)
        if result.returncode != 0:
            raise EvaluationError('independent inspection failed: ' + result.stdout[:4096].decode(errors='replace'))
        return normalize_snapshot(json.loads(result.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise EvaluationError('independent inspection failed: ' + str(exc)) from exc


def grade(answer):
    binding = digest(answer)
    base = {'task_id': 'E1', 'answer_sha256': binding,
            'evaluation_version': 1, 'review_status': 'pending',
            'explanation_quality': 'not_automatically_scored'}
    if not isinstance(answer, dict) or answer.get('task_id') != 'E1':
        return {**base, 'formal_status': 'invalid', 'reason': 'task_id must be E1'}
    if not isinstance(answer.get('explanation'), str) or not answer['explanation'].strip():
        return {**base, 'formal_status': 'invalid', 'reason': 'nonempty explanation required'}
    if answer.get('alternative_format') is True:
        if not isinstance(answer.get('alternative'), str) or not answer['alternative'].strip():
            return {**base, 'formal_status': 'invalid', 'reason': 'nonempty alternative required'}
        return {**base, 'formal_status': 'review_required', 'overall_status': 'review_required'}
    if not isinstance(answer.get('code'), str) or not answer['code'].strip():
        return {**base, 'formal_status': 'invalid', 'reason': 'complete Service source required'}
    unavailable = availability()
    if unavailable:
        return {**base, 'formal_status': 'unavailable', 'reason': unavailable}
    repetitions = []
    with tempfile.TemporaryDirectory(prefix='e1-evaluation-') as directory:
        root = Path(directory)
        code = root / 'candidate.py'
        code.write_text(answer['code'], encoding='utf-8')
        for repetition in range(REPETITIONS):
            state = root / f'state-{repetition}'
            state.mkdir()
            trace = {'repetition': repetition + 1, 'steps': [], 'execution': []}
            try:
                trace['overlap'] = run_batch(state, code, requests(), trace['execution'])
                trace['after_overlap'] = inspect_state(state)
                for req in followups():
                    reply = run_batch(state, code, [req], trace['execution'])[0]
                    trace['steps'].append({'request': req, 'reply': reply,
                                           'snapshot': inspect_state(state)})
                trace['verification'] = verify_trace(trace)
            except (EvaluationError, OSError, subprocess.SubprocessError) as exc:
                trace['verification'] = {'passed': False, 'error': str(exc)}
                try:
                    trace['failure_snapshot'] = inspect_state(state)
                except EvaluationError as inspection_error:
                    trace['inspection_error'] = str(inspection_error)
            repetitions.append(trace)
    passed = all(rep['verification']['passed'] for rep in repetitions)
    return {**base, 'formal_status': 'pass' if passed else 'fail',
            'overall_status': 'formal_pass_review_pending' if passed else 'formal_fail',
            'repetitions': repetitions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answer', type=Path, help='JSON answer containing task_id, code, explanation')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        answer = json.loads(args.answer.read_text(encoding='utf-8'))
        report = grade(answer)
    except (ValueError, OSError) as exc:
        report = {'task_id': 'E1', 'formal_status': 'invalid', 'reason': str(exc)}
    rendered = json.dumps(report, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    return 0 if report['formal_status'] == 'pass' else 2


if __name__ == '__main__':
    sys.exit(main())
