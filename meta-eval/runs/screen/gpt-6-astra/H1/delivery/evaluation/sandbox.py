"""Linux bubblewrap runner. Deliberately has no unsandboxed execution fallback."""
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import time


REPLY_SECONDS = 6.0
REPLY_BYTES = 64 * 1024
HERE = Path(__file__).resolve().parent


class Unavailable(Exception):
    pass


class WorkerFailure(Exception):
    pass


def decode_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError("duplicate JSON key")
            out[key] = value
        return out
    def constant(value):
        raise ValueError("nonfinite JSON number")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


class Sandbox:
    def __init__(self):
        if sys.platform != "linux":
            raise Unavailable("E1 execution requires Linux, bubblewrap and unprivileged namespaces")
        self.bwrap = shutil.which("bwrap")
        if not self.bwrap or not Path("/usr/bin/python3").is_file():
            raise Unavailable("bubblewrap or /usr/bin/python3 is missing")

    def command(self, state, candidate=None, script="worker.py", readonly=False):
        args = [self.bwrap, "--die-with-parent", "--unshare-all", "--new-session",
                "--cap-drop", "ALL", "--clearenv", "--setenv", "PATH", "/usr/bin",
                "--setenv", "HOME", "/tmp", "--setenv", "LANG", "C.UTF-8"]
        # Runtime libraries only; never bind the workspace, input, home or host /tmp.
        for directory in ("/usr/lib", "/usr/lib64", "/lib", "/lib64"):
            if Path(directory).exists():
                args += ["--ro-bind", directory, directory]
        args += ["--ro-bind", "/usr/bin/python3", "/usr/bin/python3",
                 "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                 "--ro-bind" if readonly else "--bind", str(Path(state).resolve()), "/state",
                 "--ro-bind", str(HERE / script), "/worker.py", "--chdir", "/state"]
        if candidate is not None:
            args += ["--ro-bind", str(Path(candidate).resolve()), "/candidate.py"]
        return args + ["--", "/usr/bin/python3", "-I", "-S", "-B", "-u", "/worker.py"]

    def preflight(self, state):
        command = self.command(state)
        command[-1:] = ["-c", 'print("e1-isolation-ready")']
        try:
            completed = subprocess.run(command, capture_output=True, timeout=REPLY_SECONDS,
                                       env={}, close_fds=True)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Unavailable(f"isolation probe failed: {type(exc).__name__}") from exc
        if completed.returncode or completed.stdout.strip() != b"e1-isolation-ready":
            raise Unavailable("isolation probe failed: " +
                              completed.stderr[:2000].decode("utf-8", errors="replace"))

    def worker(self, state, candidate):
        return Channel(self.command(state, candidate))

    def inspect(self, state):
        # Public state is parsed in another namespace, read-only, with its own limits.
        channel = Channel(self.command(state, script="inspector.py", readonly=True))
        try:
            result = channel.read()
            channel.finish()
            if not isinstance(result, dict) or set(result) != {"snapshot"}:
                raise WorkerFailure("independent SQL inspection failed: " + repr(result)[:2000])
            return result["snapshot"]
        finally:
            channel.stop()


class Channel:
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env={}, close_fds=True,
                                        start_new_session=True, bufsize=0)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = bytearray()
        self.returncode = None
        self.closed = False

    def send(self, value):
        try:
            data = (json.dumps(value, allow_nan=False) + "\n").encode("utf-8")
            # All evaluator commands are tiny and fit within an empty pipe atomically.
            if len(data) > 4096:
                raise WorkerFailure("internal command size limit")
            self.process.stdin.write(data)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise WorkerFailure("worker closed its input") from exc

    def read(self, deadline=None):
        deadline = deadline if deadline is not None else time.monotonic() + REPLY_SECONDS
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise WorkerFailure("six-second reply deadline exceeded")
            chunk = os.read(self.process.stdout.fileno(), REPLY_BYTES + 1)
            if not chunk:
                raise WorkerFailure("worker exited without a complete reply")
            self.buffer.extend(chunk)
            if len(self.buffer) > REPLY_BYTES:
                raise WorkerFailure("reply exceeds 64 KiB")
        line, _, rest = self.buffer.partition(b"\n")
        self.buffer = bytearray(rest)
        try:
            return decode_json(line.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise WorkerFailure("worker emitted invalid JSON") from exc

    def finish(self):
        try:
            self.returncode = self.process.wait(timeout=REPLY_SECONDS)
        except subprocess.TimeoutExpired as exc:
            raise WorkerFailure("worker did not terminate") from exc
        if self.returncode != 0:
            raise WorkerFailure(f"worker exited with code {self.returncode}")
        # A completed request gets one response, never an ignored extra response.
        trailing = self.process.stdout.read(REPLY_BYTES + 1)
        if self.buffer or trailing:
            raise WorkerFailure("worker emitted unsolicited output")

    def close(self):
        self.send({"op": "close"})
        self.finish()

    def stop(self):
        if self.closed:
            return
        self.closed = True
        # bwrap's PID namespace is torn down on exit. Also kill its outer group.
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.process.wait(timeout=REPLY_SECONDS)
        self.returncode = self.process.returncode
        self.selector.close()
        for stream in (self.process.stdin, self.process.stdout):
            stream.close()
