"""Linux bubblewrap transport. There is deliberately no unsandboxed fallback."""

import json
import os
import queue
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from .oracle import ContractError

REPLY_SECONDS = 6
MAX_REPLY = 65536


class Unavailable(Exception):
    pass


def sandbox_command(state, candidate, program):
    binary = shutil.which("bwrap")
    if sys.platform != "linux" or not binary or not Path("/usr/bin/python3").is_file():
        raise Unavailable("requires Linux, bubblewrap and /usr/bin/python3")
    command = [binary, "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
               "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "LANG", "C.UTF-8"]
    for path in ("/usr", "/bin", "/lib", "/lib64"):
        if Path(path).exists():
            command += ["--ro-bind", path, path]
    if Path("/etc/ld.so.cache").exists():
        command += ["--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache"]
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--bind", str(state), "/state", "--ro-bind", str(candidate), "/candidate.py",
                "--chdir", "/state"]
    if program == "probe":
        command += ["--", "/usr/bin/python3", "-I", "-B", "-c",
                    "import sqlite3,resource; print('E1_SANDBOX_READY')"]
    else:
        command += ["--ro-bind", str(Path(__file__).with_name("worker.py")), "/worker.py",
                    "--", "/usr/bin/python3", "-I", "-B", "/worker.py"]
    return command


def preflight(state, candidate):
    try:
        result = subprocess.run(sandbox_command(state, candidate, "probe"),
                                capture_output=True, timeout=REPLY_SECONDS,
                                env={"PATH": "/usr/bin:/bin"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(f"isolation preflight failed: {exc}") from exc
    if result.returncode or result.stdout.strip() != b"E1_SANDBOX_READY":
        raise Unavailable("bubblewrap preflight failed: " + result.stderr.decode(errors="replace")[:1500])


class Worker:
    def __init__(self, state, candidate):
        self.deadline = time.monotonic() + REPLY_SECONDS
        self.process = subprocess.Popen(sandbox_command(state, candidate, "worker"),
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, start_new_session=True,
                                        env={"PATH": "/usr/bin:/bin"})
        self.events = queue.Queue(maxsize=8)
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            while True:
                raw = self.process.stdout.readline(MAX_REPLY + 1)
                if not raw:
                    self.events.put_nowait((time.monotonic(), ContractError("worker closed its output")))
                    return
                if len(raw) > MAX_REPLY or not raw.endswith(b"\n"):
                    raise ContractError("worker output exceeded 64 KiB")
                try:
                    event = json.loads(raw)
                except (ValueError, UnicodeError) as exc:
                    raise ContractError("worker produced invalid JSON") from exc
                self.events.put_nowait((time.monotonic(), event))
        except (Exception,) as exc:
            try:
                self.events.put_nowait((time.monotonic(), exc))
            except queue.Full:
                pass

    def send(self, action, request=None):
        self.deadline = time.monotonic() + REPLY_SECONDS
        value = {"action": action}
        if request is not None:
            value["request"] = request
        try:
            self.process.stdin.write((json.dumps(value) + "\n").encode())
            self.process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise ContractError(f"worker input failed: {exc}") from exc

    def receive(self, event):
        try:
            received_at, value = self.events.get(timeout=max(0, self.deadline - time.monotonic()))
        except queue.Empty as exc:
            raise ContractError("worker reply timed out after six seconds") from exc
        if received_at > self.deadline:
            raise ContractError("worker reply arrived after its six-second deadline")
        if isinstance(value, BaseException):
            raise ContractError(str(value))
        if not isinstance(value, dict) or value.get("event") != event:
            raise ContractError(f"expected {event}, observed {value!r}")
        return value

    def close(self):
        try:
            self.send("stop")
            self.process.wait(timeout=0.3)
        except (ContractError, subprocess.TimeoutExpired):
            pass
        if self.process.poll() is None:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait(timeout=2)
        for stream in (self.process.stdin, self.process.stdout):
            stream.close()
        self.reader.join(timeout=1)
        return self.process.returncode
