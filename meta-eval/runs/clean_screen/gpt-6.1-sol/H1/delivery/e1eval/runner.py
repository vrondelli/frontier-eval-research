"""Linux-only candidate execution. There is deliberately no unsandboxed backend."""
import json
import math
import os
from pathlib import Path
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid

from .oracle import judge_primary, primary_plan

REPLY_SECONDS = 6.0
MAX_WIRE_BYTES = 64 * 1024
HERE = Path(__file__).resolve().parent


class Unavailable(RuntimeError):
    pass


class WorkerFailure(RuntimeError):
    pass


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def bad_constant(value):
        raise ValueError("nonfinite JSON number: " + value)

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            return bad_constant(value)
        return number

    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant, parse_float=finite_float)


class Sandbox:
    def __init__(self):
        if sys.platform != "linux":
            raise Unavailable("Linux with bubblewrap and working unprivileged namespaces is required")
        self.bwrap = shutil.which("bwrap")
        if not self.bwrap or not Path("/usr/bin/python3").is_file():
            raise Unavailable("bubblewrap and /usr/bin/python3 are required")
        try:
            probe = subprocess.run(self.base() + ["/usr/bin/python3", "-I", "-B", "-c",
                                                "print('e1-sandbox-ready')"],
                                   capture_output=True, timeout=REPLY_SECONDS, env={})
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Unavailable("isolation preflight failed: " + str(exc)) from exc
        if probe.returncode or probe.stdout.strip() != b"e1-sandbox-ready":
            raise Unavailable("isolation preflight failed: " + probe.stderr[:2048].decode("utf-8", "replace"))

    def base(self):
        command = [self.bwrap, "--die-with-parent", "--new-session", "--unshare-all",
                   "--cap-drop", "ALL", "--clearenv", "--setenv", "PATH", "/usr/bin:/bin",
                   "--setenv", "HOME", "/tmp", "--setenv", "LANG", "C.UTF-8"]
        for directory in ("/usr", "/lib", "/lib64", "/bin"):
            if Path(directory).is_dir():
                command += ["--ro-bind", directory, directory]
        return command + ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]

    def command(self, source, state):
        return self.base() + ["--dir", "/app", "--ro-bind", str(source), "/app/candidate.py",
                              "--ro-bind", str(HERE / "worker.py"), "/app/worker.py",
                              "--bind", str(state), "/state", "--chdir", "/state",
                              "--remount-ro", "/",
                              "/usr/bin/python3", "-I", "-B", "/app/worker.py"]


class Worker:
    def __init__(self, sandbox, source, state, record):
        self.record = record
        self.events = queue.Queue(maxsize=8)
        self.violation = None
        self.stderr = bytearray()
        self.process = subprocess.Popen(sandbox.command(source, state), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env={}, start_new_session=True, bufsize=0)
        record["pid"] = self.process.pid
        self.readers = [threading.Thread(target=self._stdout, daemon=True),
                        threading.Thread(target=self._stderr, daemon=True)]
        for reader in self.readers:
            reader.start()

    def _stdout(self):
        try:
            while True:
                line = self.process.stdout.readline(MAX_WIRE_BYTES + 1)
                if not line:
                    self.events.put_nowait(None)
                    return
                if len(line) > MAX_WIRE_BYTES or not line.endswith(b"\n"):
                    raise ValueError("oversize or unterminated worker message")
                self.events.put_nowait(strict_json(line.decode("utf-8")))
        except Exception as exc:
            self.violation = "invalid worker output: " + str(exc)
            try:
                self.events.put_nowait({"event": "protocol_error"})
            except queue.Full:
                pass

    def _stderr(self):
        while True:
            block = self.process.stderr.read(4096)
            if not block:
                return
            self.stderr.extend(block[:max(0, 8192 - len(self.stderr))])

    def receive(self, event, deadline=None):
        deadline = deadline if deadline is not None else time.monotonic() + REPLY_SECONDS
        try:
            message = self.events.get(timeout=max(0, deadline - time.monotonic()))
        except queue.Empty as exc:
            raise WorkerFailure("six-second deadline waiting for " + event) from exc
        if self.violation:
            raise WorkerFailure(self.violation)
        if not isinstance(message, dict) or message.get("event") != event:
            raise WorkerFailure("expected " + event + ", received " + repr(message)[:1000])
        return message

    def send(self, message):
        try:
            self.process.stdin.write((json.dumps(message) + "\n").encode())
            self.process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise WorkerFailure("worker closed its input") from exc

    def ready(self):
        self.receive("ready")

    def arm(self, request):
        self.send({"op": "arm", "request": request})
        self.receive("armed")
        self.record["request"] = request
        self.record["armed"] = True

    def result(self, deadline):
        reply = self.receive("result", deadline)["reply"]
        if not isinstance(reply, dict):
            raise WorkerFailure("reply is not a JSON object")
        self.record["reply"] = reply
        return reply

    def close(self):
        forced = False
        if self.process.poll() is None:
            try:
                self.send({"op": "close"})
                self.process.wait(timeout=1)
            except (WorkerFailure, subprocess.TimeoutExpired):
                forced = True
                try:
                    os.killpg(self.process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self.process.wait(timeout=2)
        for reader in self.readers:
            reader.join(timeout=0.5)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()
        self.record.update(exit_code=self.process.returncode, forced_stop=forced,
                           diagnostics=self.stderr.decode("utf-8", "replace"))
        if self.violation:
            self.record["protocol_error"] = self.violation
        return self.process.returncode == 0 and not forced and not self.violation


def inspect_state(state):
    try:
        process = subprocess.run([sys.executable, "-I", "-B", str(HERE / "inspect_db.py"),
                                  str(state / "ledger.sqlite")],
                                 capture_output=True, timeout=3, env={})
        if len(process.stdout) > 1024 * 1024:
            return {"error": "inspection output exceeds 1 MiB"}
        data = strict_json(process.stdout.decode("utf-8"))
        if process.returncode != 0 or "snapshot" not in data:
            return {"error": data.get("error", "inspector failed")}
        return data
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"error": "inspection failed: " + str(exc)}


def run_repetition(sandbox, source, state, index):
    plan = primary_plan(uuid.uuid4().hex)
    record = {"repetition": index, "plan": plan, "workers": [], "replies": []}
    active = []
    launched = []
    clean = True

    def start():
        detail = {"worker": len(record["workers"]) + 1}
        record["workers"].append(detail)
        worker = Worker(sandbox, source, state, detail)
        active.append(worker)
        launched.append(worker)
        return worker

    def stop_all():
        nonlocal clean
        while active:
            worker = active.pop()
            try:
                clean = worker.close() and clean
            except Exception as exc:
                clean = False
                worker.record["cleanup_error"] = str(exc)

    try:
        # Launch BOTH before awaiting either constructor. No parent Service exists.
        pair = [start(), start()]
        for worker in pair:
            worker.ready()
        for worker, request in zip(pair, plan["overlap"]):
            worker.arm(request)
        record["both_armed_before_release"] = True
        deadline = time.monotonic() + REPLY_SECONDS
        for worker in pair:
            worker.send({"op": "go"})
        record["replies"].extend(worker.result(deadline) for worker in pair)
        stop_all()
        # Every retry, conflict and B request starts a genuinely fresh process.
        for request in plan["sequential"]:
            worker = start()
            worker.ready()
            worker.arm(request)
            deadline = time.monotonic() + REPLY_SECONDS
            worker.send({"op": "go"})
            record["replies"].append(worker.result(deadline))
            stop_all()
    except Exception as exc:
        record["execution_error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        stop_all()
    # No candidate worker may be running when the independent inspector opens SQLite.
    record["workers_exited_cleanly"] = clean
    observation = (inspect_state(state) if all(w.process.poll() is not None for w in launched)
                   else {"error": "worker shutdown was not confirmed; inspection skipped"})
    record["observation"] = observation
    judgment = judge_primary(plan, record["replies"], observation.get("snapshot"))
    record["judgment"] = judgment
    record["passed"] = (judgment["passed"] and clean and "execution_error" not in record
                         and record.get("both_armed_before_release", False))
    return record


def run_code(code):
    sandbox = Sandbox()  # Preflight before writing or executing candidate source.
    with tempfile.TemporaryDirectory(prefix="e1-evaluation-") as temporary:
        root = Path(temporary)
        source = root / "candidate.py"
        source.write_text(code, encoding="utf-8")
        records = []
        for index in range(1, 4):
            state = root / ("trial-" + str(index))
            state.mkdir()
            records.append(run_repetition(sandbox, source, state, index))
        return records
