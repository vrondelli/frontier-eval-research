"""Linux-only subprocess boundary. There is deliberately no in-process fallback."""
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import time


MAX_REPLY = 65536
REPLY_SECONDS = 6
HERE = Path(__file__).resolve().parent


class Unavailable(RuntimeError):
    pass


class CandidateError(RuntimeError):
    pass


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"non-JSON constant: {value}")
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def base_command(state):
    command = [shutil.which("bwrap"), "--die-with-parent", "--unshare-all",
               "--cap-drop", "ALL", "--clearenv", "--ro-bind", "/usr", "/usr"]
    for name in ("/lib", "/lib64", "/bin"):
        if Path(name).exists():
            command += ["--ro-bind", name, name]
    return command + ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                      "--bind", str(state), "/state", "--chdir", "/state",
                      "--setenv", "PATH", "/usr/bin:/bin",
                      "--setenv", "LANG", "C.UTF-8"]


def require_runtime():
    if not sys.platform.startswith("linux"):
        raise Unavailable("requires Linux, bubblewrap and working unprivileged namespaces")
    if not shutil.which("bwrap") or not Path("/usr/bin/python3").is_file():
        raise Unavailable("requires bwrap and /usr/bin/python3")


def probe(state):
    require_runtime()
    code = ("import json,sys,sqlite3; assert sys.version_info >= (3,11); "
            "print(json.dumps({'python':sys.version,'sqlite':sqlite3.sqlite_version,'platform':sys.platform}))")
    command = base_command(state) + ["/usr/bin/python3", "-I", "-c", code]
    try:
        result = subprocess.run(command, env={}, capture_output=True, timeout=6)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(f"isolation probe failed: {exc}") from exc
    if result.returncode != 0:
        raise Unavailable("isolation probe failed: " + result.stderr[:2000].decode(errors="replace"))
    try:
        runtime = strict_json(result.stdout.decode())
        if not isinstance(runtime, dict) or set(runtime) != {"python", "sqlite", "platform"}:
            raise ValueError("invalid runtime metadata")
    except (ValueError, UnicodeError) as exc:
        raise Unavailable("invalid isolation probe response") from exc
    return runtime


class Worker:
    def __init__(self, source, state, transcript, label):
        self.transcript, self.label = transcript, label
        self.buffer = bytearray()
        self.stderr = bytearray()
        self.closed = False
        command = base_command(state) + [
            "--ro-bind", str(source), "/candidate.py",
            "--ro-bind", str(HERE / "worker.py"), "/worker.py",
            "/usr/bin/python3", "-I", "-u", "/worker.py",
        ]
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env={}, start_new_session=True)
        self.selector = selectors.DefaultSelector()
        for stream in (self.process.stdout, self.process.stderr):
            os.set_blocking(stream.fileno(), False)
            self.selector.register(stream, selectors.EVENT_READ)

    def send(self, command):
        self.transcript.append({"worker": self.label, "send": command})
        try:
            self.process.stdin.write((json.dumps(command) + "\n").encode())
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise CandidateError(f"{self.label}: worker stopped before command") from exc

    def receive(self, expected_event, deadline=None):
        deadline = deadline if deadline is not None else time.monotonic() + REPLY_SECONDS
        while True:
            if b"\n" in self.buffer:
                line, _, rest = self.buffer.partition(b"\n")
                self.buffer = bytearray(rest)
                try:
                    value = strict_json(line.decode("utf-8"))
                except (ValueError, UnicodeError) as exc:
                    raise CandidateError(f"{self.label}: invalid protocol JSON") from exc
                self.transcript.append({"worker": self.label, "receive": value})
                if not isinstance(value, dict) or value.get("event") != expected_event:
                    raise CandidateError(f"{self.label}: expected {expected_event}")
                if expected_event == "reply":
                    if set(value) != {"event", "value"}:
                        raise CandidateError("invalid reply envelope")
                    return value["value"]
                if value != {"event": expected_event}:
                    raise CandidateError("invalid acknowledgement")
                return None
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CandidateError(f"{self.label}: six-second response deadline exceeded")
            events = self.selector.select(remaining)
            for key, _ in events:
                data = os.read(key.fileobj.fileno(), 8192)
                if not data:
                    self.selector.unregister(key.fileobj)
                    if key.fileobj is self.process.stdout:
                        raise CandidateError(f"{self.label}: exited without {expected_event}; "
                                             + self.stderr.decode(errors="replace"))
                    continue
                if key.fileobj is self.process.stdout:
                    self.buffer.extend(data)
                    if len(self.buffer) > MAX_REPLY:
                        raise CandidateError(f"{self.label}: response exceeds 64 KiB")
                else:
                    self.stderr.extend(data)
                    if len(self.stderr) > MAX_REPLY:
                        raise CandidateError(f"{self.label}: excessive stderr")

    def call(self, request):
        self.send({"op": "arm", "request": request})
        self.receive("armed")
        self.send({"op": "release"})
        return self.receive("reply")

    def stop(self):
        if self.closed:
            return
        self.closed = True
        # Kill the entire sandbox group before reading SQLite. With its private PID
        # namespace, killing the sandbox init also removes candidate descendants.
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.process.wait(timeout=3)
        self.transcript.append({"worker": self.label, "terminal_code": self.process.returncode,
                                "termination": "evaluator_cleanup",
                                "stderr": self.stderr.decode(errors="replace")})
        self.selector.close()
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()


class Group:
    def __init__(self, source, state, transcript, label):
        self.workers = []
        self.source, self.state, self.transcript, self.label = source, state, transcript, label

    def __enter__(self):
        try:
            # Spawn BOTH before waiting for ready: initialization also overlaps.
            for index in range(2):
                self.workers.append(Worker(self.source, self.state, self.transcript,
                                           f"{self.label}/{index}"))
            deadline = time.monotonic() + REPLY_SECONDS
            for worker in self.workers:
                worker.receive("ready", deadline)
            return self.workers
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        for worker in self.workers:
            worker.stop()


def overlap(workers, requests):
    for worker, request in zip(workers, requests):
        worker.send({"op": "arm", "request": request})
    deadline = time.monotonic() + REPLY_SECONDS
    for worker in workers:
        worker.receive("armed", deadline)
    # No apply executes until BOTH processes acknowledge their request.
    deadline = time.monotonic() + REPLY_SECONDS
    for worker in workers:
        worker.send({"op": "release"})
    return [worker.receive("reply", deadline) for worker in workers]


def inspect_stopped(state):
    try:
        result = subprocess.run(
            [sys.executable, "-I", str(HERE / "inspector.py"), str(state / "ledger.sqlite")],
            env={}, capture_output=True, timeout=3,
        )
        if len(result.stdout) > 1024 * 1024:
            raise CandidateError("inspection output exceeded limit")
        value = strict_json(result.stdout.decode())
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise CandidateError(f"independent inspection failed: {exc}") from exc
    if result.returncode or "snapshot" not in value:
        raise CandidateError(f"independent inspection failed: {value}")
    return value["snapshot"]
