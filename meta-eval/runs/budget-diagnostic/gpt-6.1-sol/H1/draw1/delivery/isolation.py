"""Fail-closed Linux/bubblewrap execution; no native/unsafe candidate fallback."""
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPLY_SECONDS = 6
MAX_REPLY = 65536


class Unavailable(Exception):
    pass


class ExecutionFailure(Exception):
    pass


def sandbox_command(state, candidate, executable):
    bwrap = shutil.which("bwrap")
    if sys.platform != "linux" or not bwrap or not Path("/usr/bin/python3").is_file():
        raise Unavailable("requires Linux, bubblewrap, /usr/bin/python3 and working unprivileged namespaces")
    cmd = [bwrap, "--unshare-all", "--die-with-parent", "--new-session", "--cap-drop", "ALL",
           "--clearenv", "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "HOME", "/tmp",
           "--setenv", "LANG", "C.UTF-8", "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev"]
    for runtime in ("/usr", "/lib", "/lib64", "/bin"):
        if Path(runtime).exists():
            cmd += ["--ro-bind", runtime, runtime]
    cmd += ["--bind", str(state), "/state", "--ro-bind", str(candidate), "/candidate.py",
            "--ro-bind", str(ROOT / "worker.py"), "/worker.py", "--chdir", "/state",
            "--", "/usr/bin/python3", "-I", "-S", *executable]
    return cmd


def check_available(state, candidate):
    cmd = sandbox_command(state, candidate, ["-c", "print('isolation-ready')"])
    try:
        result = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=6, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(f"sandbox preflight failed: {type(exc).__name__}") from exc
    if result.returncode != 0 or result.stdout != b"isolation-ready\n":
        raise Unavailable(f"sandbox preflight failed (exit {result.returncode}); no candidate executed")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON member: {key}")
            result[key] = value
        return result
    def constant(value):
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


class Worker:
    def __init__(self, state, candidate):
        self.process = subprocess.Popen(sandbox_command(state, candidate, ["/worker.py"]),
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, bufsize=0)
        self.buffer = bytearray()

    def send(self, value):
        try:
            self.process.stdin.write(json.dumps(value, separators=(",", ":")).encode() + b"\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise ExecutionFailure("worker closed its input") from exc

    def receive(self, deadline):
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            while b"\n" not in self.buffer:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise ExecutionFailure("six-second reply deadline exceeded")
                data = os.read(self.process.stdout.fileno(), 4096)
                if not data:
                    raise ExecutionFailure(f"worker ended before reply (exit {self.process.poll()})")
                self.buffer.extend(data)
                if len(self.buffer) > MAX_REPLY:
                    raise ExecutionFailure("worker reply exceeds 64 KiB")
        line, _, rest = self.buffer.partition(b"\n")
        self.buffer = bytearray(rest)
        try:
            return strict_json(line)
        except (ValueError, UnicodeError) as exc:
            raise ExecutionFailure("invalid worker JSON") from exc

    def close(self):
        # Killing bwrap tears down the private PID namespace and its descendants.
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=3)
        self.process.stdin.close()
        self.process.stdout.close()
        return self.process.returncode


def run_requests(state, candidate, requests, record):
    workers = []
    try:
        # Launch all workers before awaiting initialization.
        for _ in requests:
            workers.append(Worker(state, candidate))
        for event in ("ready", "armed"):
            deadline = time.monotonic() + REPLY_SECONDS
            for worker in workers:
                value = worker.receive(deadline)
                record.setdefault("protocol", []).append(value)
                if value != {"event": event}:
                    raise ExecutionFailure(f"expected {event}: {str(value)[:1000]}")
            if event == "ready":
                for worker, request in zip(workers, requests):
                    worker.send({"request": request})
        # Each has acknowledged the request before either is released.
        deadline = time.monotonic() + REPLY_SECONDS
        for worker in workers:
            worker.send({"go": True})
        replies = []
        for worker in workers:
            value = worker.receive(deadline)
            record.setdefault("protocol", []).append(value)
            if not isinstance(value, dict) or set(value) != {"event", "value"} or value["event"] != "reply":
                raise ExecutionFailure(f"apply did not return a business reply: {str(value)[:1000]}")
            replies.append(value["value"])
        record["replies"] = replies
        return replies
    finally:
        record["terminal_codes"] = [worker.close() for worker in workers]


def observe(state):
    try:
        result = subprocess.run([sys.executable, "-I", "-S", str(ROOT / "inspect_db.py"),
                                 str(state / "ledger.sqlite")],
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=4, check=False)
        if len(result.stdout) > MAX_REPLY:
            raise ExecutionFailure("inspection output exceeds limit")
        payload = strict_json(result.stdout)
        if result.returncode or payload.get("ok") is not True:
            raise ExecutionFailure(f"independent inspection failed: {payload}")
        return payload["tables"]
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise ExecutionFailure(f"independent inspection failed: {type(exc).__name__}") from exc
