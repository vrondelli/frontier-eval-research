"""Fail-closed Linux runtime. No in-process or unsandboxed candidate fallback."""
from pathlib import Path
import json
import os
import select
import shutil
import signal
import subprocess
import sys
import time

REPLY_SECONDS = 6
MAX_REPLY = 64 * 1024


class Unavailable(RuntimeError):
    pass


class CandidateError(RuntimeError):
    pass


def prefix():
    if sys.platform != "linux" or not shutil.which("bwrap") or not Path("/usr/bin/python3").is_file():
        raise Unavailable("requires Linux, bubblewrap, unprivileged namespaces and /usr/bin/python3")
    args = [shutil.which("bwrap"), "--unshare-all", "--die-with-parent", "--new-session",
            "--cap-drop", "ALL", "--clearenv", "--setenv", "PATH", "/usr/bin",
            "--setenv", "LANG", "C.UTF-8", "--ro-bind", "/usr", "/usr"]
    for directory in ("/lib", "/lib64"):
        if Path(directory).exists():
            args += ["--ro-bind", directory, directory]
    args += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--chdir", "/tmp"]
    return args


def available():
    args = prefix() + ["/usr/bin/python3", "-I", "-S", "-c", "import sqlite3,resource; print('ok')"]
    try:
        result = subprocess.run(args, capture_output=True, timeout=6, env={}, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(str(exc)) from exc
    if result.returncode or result.stdout != b"ok\n":
        raise Unavailable("sandbox preflight failed: " + result.stderr.decode(errors="replace")[:2048])


class Worker:
    def __init__(self, source, state):
        adapter = Path(__file__).with_name("worker.py").resolve()
        args = prefix() + ["--ro-bind", str(Path(source).resolve()), "/candidate.py",
                           "--ro-bind", str(adapter), "/worker.py",
                           "--bind", str(Path(state).resolve()), "/state",
                           "/usr/bin/python3", "-I", "-S", "-u", "/worker.py"]
        self.buffer = b""
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env={}, start_new_session=True,
                                        bufsize=0)
        self.terminal = None

    def send(self, value):
        try:
            self.process.stdin.write((json.dumps(value) + "\n").encode())
            self.process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise CandidateError("worker pipe closed") from exc

    def receive(self, deadline=None):
        deadline = deadline or time.monotonic() + REPLY_SECONDS
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.process.stdout], [], [], max(0, remaining))[0]:
                raise CandidateError("six-second response deadline exceeded")
            chunk = os.read(self.process.stdout.fileno(), 4096)
            if not chunk:
                raise CandidateError(f"worker EOF (terminal={self.process.poll()})")
            self.buffer += chunk
            if len(self.buffer) > MAX_REPLY:
                raise CandidateError("reply exceeds 64 KiB")
        line, self.buffer = self.buffer.split(b"\n", 1)
        try:
            return json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (ValueError, UnicodeError) as exc:
            raise CandidateError("worker emitted invalid JSON") from exc

    def close(self):
        # EOF allows normal SQLite connection cleanup; kill the whole group if it hangs.
        if self.terminal is not None:
            return self.terminal
        try:
            self.process.stdin.close()
            self.process.wait(timeout=0.5)
        except (OSError, subprocess.TimeoutExpired):
            pass
        # Also kill any surviving descendants if the namespace leader already exited.
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.process.wait(timeout=2)
        self.terminal = {"pid": self.process.pid, "returncode": self.process.returncode}
        self.process.stdout.close()
        return self.terminal
