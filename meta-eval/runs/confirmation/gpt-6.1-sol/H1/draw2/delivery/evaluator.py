"""E1 finite contract evaluator. CLI never executes submissions without isolation."""
import argparse
import hashlib
import json
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

from oracle import compare_trace, stages

ROOT = Path(__file__).resolve().parent
REPLY_SECONDS = 6
MAX_REPLY = 64 * 1024
REPETITIONS = 3


class EvaluationError(Exception):
    pass


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


class Sandbox:
    @staticmethod
    def command(state, candidate, probe=False):
        bwrap = shutil.which("bwrap")
        if not bwrap:
            raise EvaluationError("bubblewrap not installed")
        cmd = [bwrap, "--die-with-parent", "--new-session", "--unshare-all",
               "--cap-drop", "ALL", "--clearenv", "--setenv", "PATH", "/usr/bin",
               "--setenv", "LANG", "C.UTF-8", "--setenv", "HOME", "/tmp", "--tmpfs", "/"]
        for runtime in ("/usr", "/lib", "/lib64", "/bin"):
            if Path(runtime).exists():
                cmd.extend(["--ro-bind", runtime, runtime])
        cmd.extend(["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                    "--bind", str(state), "/state", "--chdir", "/state"])
        if probe:
            return cmd + ["/usr/bin/python3", "-I", "-B", "-c",
                          "import sqlite3,resource; print('e1-sandbox-ready')"]
        return cmd + ["--ro-bind", str(candidate), "/candidate.py",
                      "--ro-bind", str(ROOT / "worker.py"), "/worker.py",
                      "/usr/bin/python3", "-I", "-B", "/worker.py", "/candidate.py", "/state/ledger.sqlite"]

    @classmethod
    def check(cls):
        if sys.platform != "linux" or not Path("/usr/bin/python3").is_file():
            return False, "E1 execution requires Linux and /usr/bin/python3"
        # Broad read-only runtime mounts must never expose evaluation sources.
        for runtime in ("/usr", "/lib", "/lib64", "/bin"):
            if ROOT.is_relative_to(Path(runtime).resolve()):
                return False, "place the evaluator outside runtime directories (/usr, /lib, /bin)"
        try:
            with tempfile.TemporaryDirectory(prefix="e1-probe-") as temp:
                state = Path(temp)
                if any(state.resolve().is_relative_to(Path(p).resolve()) for p in ("/usr", "/lib", "/lib64", "/bin")):
                    return False, "temporary state must be outside mounted runtime directories"
                process = subprocess.run(cls.command(state, None, probe=True),
                                         capture_output=True, timeout=REPLY_SECONDS,
                                         env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
            if process.returncode or process.stdout.strip() != b"e1-sandbox-ready":
                detail = process.stderr.decode("utf-8", errors="replace")[:1000]
                return False, "isolation probe failed: " + detail
            return True, "Linux bubblewrap namespaces and Python runtime available"
        except (OSError, subprocess.TimeoutExpired, EvaluationError) as exc:
            return False, str(exc)[:1000]


class Worker:
    def __init__(self, state, candidate):
        self.started = time.monotonic()
        self.process = subprocess.Popen(Sandbox.command(state, candidate), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                        start_new_session=(os.name == "posix"),
                                        env=({"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
                                             if os.name == "posix" else None))
        self.lines = queue.Queue(maxsize=8)
        self.transcript = []
        self.overflow = threading.Event()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            while True:
                line = self.process.stdout.readline(MAX_REPLY + 1)
                try:
                    self.lines.put_nowait((time.monotonic(), line))
                except queue.Full:
                    self.overflow.set()
                    break
                if not line or len(line) > MAX_REPLY:
                    break
        except (OSError, ValueError):
            self.overflow.set()

    def send(self, value):
        try:
            self.process.stdin.write((json.dumps(value) + "\n").encode("utf-8"))
            self.process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise EvaluationError("worker input closed: " + str(exc)) from exc

    def receive(self, deadline):
        if self.overflow.is_set():
            raise EvaluationError("worker output flooded protocol")
        try:
            received_at, line = self.lines.get(timeout=max(0, deadline - time.monotonic()))
        except queue.Empty as exc:
            raise EvaluationError("worker exceeded six-second reply limit") from exc
        if received_at > deadline:
            raise EvaluationError("worker exceeded six-second reply limit")
        if not line:
            raise EvaluationError("worker exited before reply")
        if len(line) > MAX_REPLY:
            raise EvaluationError("worker exceeded 64 KiB reply limit")
        try:
            value = strict_json(line.decode("utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise EvaluationError("worker emitted invalid JSON") from exc
        if type(value) is not dict:
            raise EvaluationError("worker protocol requires an object")
        self.transcript.append(value)
        return value

    def expect(self, event, deadline):
        value = self.receive(deadline)
        if value != {"event": event}:
            raise EvaluationError("expected " + event + ": " + json.dumps(value)[:1500])

    def finish(self, deadline):
        try:
            code = self.process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise EvaluationError("worker did not terminate after reply") from exc
        self.reader.join(timeout=0.2)
        if code != 0:
            raise EvaluationError(f"worker terminal code {code}")
        if self.overflow.is_set() or self.reader.is_alive():
            raise EvaluationError("worker emitted excess output or kept stdout open")
        extra = []
        while not self.lines.empty():
            extra.append(self.lines.get_nowait()[1])
        if any(extra):
            raise EvaluationError("unexpected trailing worker output")
        return code

    def close(self):
        # Kill the entire process group, including descendants after leader exit.
        if os.name == "posix":
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif self.process.poll() is None:
            self.process.kill()
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        for stream in (self.process.stdin, self.process.stdout):
            if stream:
                stream.close()
        self.reader.join(timeout=0.2)


def validate_reply(value):
    if type(value) is not dict or set(value) != {"event", "reply"} or value["event"] != "result":
        raise EvaluationError("apply failed or invalid result envelope: " + json.dumps(value)[:1500])
    reply = value["reply"]
    if type(reply) is not dict or set(reply) != {"status", "remaining"}:
        raise EvaluationError("reply must have exactly status and remaining")
    status, remaining = reply["status"], reply["remaining"]
    if status == "payload_mismatch" and remaining is None:
        return reply
    if status in ("accepted", "rejected") and type(remaining) is int and remaining >= 0:
        return reply
    raise EvaluationError("invalid business reply types/status")


def run_requests(state, candidate, requests, observation=None):
    workers, replies, evidence = [], [], []
    if observation is None:
        observation = {}
    observation.update(replies=replies, workers=evidence)
    try:
        for _ in requests:
            workers.append(Worker(state, candidate))
            evidence.append({"armed": False, "terminal_code": None,
                             "protocol": workers[-1].transcript})
        for worker in workers:
            worker.expect("ready", worker.started + REPLY_SECONDS)
        for worker, req in zip(workers, requests):
            worker.send({"op": "arm", "request": req})
        armed_deadline = time.monotonic() + REPLY_SECONDS
        for worker, item in zip(workers, evidence):
            worker.expect("armed", armed_deadline)
            item["armed"] = True
        # Both adapters acknowledge before either apply is released. This does
        # not force any particular interleaving inside SQLite.
        released = time.monotonic()
        for worker in workers:
            worker.send({"op": "go"})
        deadline = released + REPLY_SECONDS
        for worker in workers:
            replies.append(validate_reply(worker.receive(deadline)))
        for worker, item in zip(workers, evidence):
            item["terminal_code"] = worker.finish(deadline)
        return replies, evidence
    finally:
        for worker, item in zip(workers, evidence):
            worker.close()
            item["terminal_code"] = worker.process.returncode


def snapshot(state):
    # Inspect hostile database bytes in a separate bounded trusted process.
    process = subprocess.Popen([sys.executable, "-I", "-B", str(ROOT / "inspector.py"),
                                str(state / "ledger.sqlite")], stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, start_new_session=(os.name == "posix"))
    lines = queue.Queue(maxsize=1)
    def read():
        try:
            lines.put(process.stdout.read(MAX_REPLY + 1))
        except (OSError, ValueError):
            pass
    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    try:
        try:
            raw = lines.get(timeout=3)
            process.wait(timeout=0.5)
        except (queue.Empty, subprocess.TimeoutExpired) as exc:
            raise EvaluationError("inspection timeout") from exc
        if len(raw) > MAX_REPLY:
            raise EvaluationError("inspection output exceeds 64 KiB")
        try:
            result = strict_json(raw)
        except (ValueError, UnicodeError) as exc:
            raise EvaluationError("invalid inspection output") from exc
        if process.returncode != 0 or set(result) != {"snapshot"}:
            raise EvaluationError("inspection failed: " + json.dumps(result)[:1500])
        return result["snapshot"]
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=1)
        process.stdout.close()
        reader.join(timeout=0.2)


def grade(answer):
    base = {"task_id": "E1", "evaluation_version": 1,
            "answer_sha256": hashlib.sha256(json.dumps(answer, sort_keys=True, ensure_ascii=True,
                                                      allow_nan=False).encode()).hexdigest(),
            "review": {"status": "pending", "rubric": "REVIEW-RUBRIC.md"}}
    def outcome(status, reason=None, **extra):
        result = dict(base, status=status, formal_status=status, **extra)
        result["overall_status"] = "formal_pass_review_pending" if status == "pass" else status
        if reason:
            result["reason"] = reason
        return result
    if type(answer) is not dict or answer.get("task_id") != "E1":
        return outcome("invalid", "answer must be an object with task_id E1")
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        return outcome("invalid", "nonempty explanation required; quality is reviewed separately")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        return outcome("invalid", "alternative_format must be boolean")
    if answer.get("alternative_format") is True:
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            return outcome("invalid", "alternative-format answers require nonempty alternative text")
        return outcome("review_required", "alternative architecture requires independent review",
                       formal_status_detail="not_executed")
    if not isinstance(answer.get("code"), str) or not answer["code"].strip():
        return outcome("invalid", "nonempty complete Service code string required")
    if len(answer["code"].encode("utf-8")) > 1024 * 1024:
        return outcome("invalid", "submission source exceeds 1 MiB transport bound")
    available, reason = Sandbox.check()
    if not available:
        return outcome("unavailable", reason, repetitions=[])
    repetitions = []
    # No benchmark or answer file is placed in the candidate mount.
    with tempfile.TemporaryDirectory(prefix="e1-evaluation-") as temp:
        root = Path(temp)
        candidate = root / "candidate.py"
        candidate.write_text(answer["code"], encoding="utf-8")
        for iteration in range(REPETITIONS):
            state = root / f"rep-{iteration + 1}"
            state.mkdir()
            record = {"repetition": iteration + 1, "observations": []}
            try:
                for label, requests in stages():
                    observation = {"stage": label, "requests": requests}
                    record["observations"].append(observation)
                    run_requests(state, candidate, requests, observation)
                    observation["snapshot"] = snapshot(state)
                    prefix = compare_trace(record["observations"], complete=False)
                    if prefix["status"] == "fail":
                        record["assessment"] = prefix
                        break
                else:
                    record["assessment"] = compare_trace(record["observations"])
            except (EvaluationError, OSError, subprocess.SubprocessError) as exc:
                record["assessment"] = {"status": "fail", "kind": "execution_or_inspection_error",
                                        "reason": str(exc)[:2000]}
            repetitions.append(record)
    status = "pass" if all(rep["assessment"]["status"] == "pass" for rep in repetitions) else "fail"
    return outcome(status, repetitions=repetitions, isolation=reason,
                   scope="Three finite correctness repetitions; no throughput, latency, crash-atomicity, hiring or creativity score.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", nargs="?", help="JSON answer containing task_id, code, explanation")
    parser.add_argument("--check-runtime", action="store_true")
    args = parser.parse_args()
    if args.check_runtime:
        available, reason = Sandbox.check()
        print(json.dumps({"status": "available" if available else "unavailable", "reason": reason}))
        return 0 if available else 2
    if not args.answer:
        parser.error("answer path required unless --check-runtime is used")
    try:
        path = Path(args.answer)
        if path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("answer exceeds 2 MiB transport bound")
        answer = strict_json(path.read_text(encoding="utf-8"))
        result = grade(answer)
    except (OSError, ValueError, TypeError) as exc:
        result = {"task_id": "E1", "status": "invalid", "formal_status": "invalid", "reason": str(exc)[:1000]}
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
