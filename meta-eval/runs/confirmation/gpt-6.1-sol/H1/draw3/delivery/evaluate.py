#!/usr/bin/env python3
"""Standalone, standard-library E1 evaluator. Candidate code is sandbox-only."""
import argparse
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
import uuid

from oracle import Model, advance, batches, compare_snapshot

ROOT = Path(__file__).resolve().parent
REPLY_SECONDS = 6
MAX_REPLY = 64 * 1024
MAX_ANSWER = 1024 * 1024
REPETITIONS = 3


class Unavailable(Exception):
    pass


class CandidateFailure(Exception):
    pass


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_json(raw):
    def invalid_constant(value):
        raise ValueError("non-finite JSON value: " + value)
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates, parse_constant=invalid_constant)
    except RecursionError as error:
        raise ValueError("JSON nesting limit exceeded") from error


def limits():
    # Imported only on the supported Linux path, immediately before exec.
    import resource
    for name, value in ((resource.RLIMIT_AS, 512 * 1024 * 1024),
                        (resource.RLIMIT_NOFILE, 256),
                        (resource.RLIMIT_FSIZE, 8 * 1024 * 1024),
                        (resource.RLIMIT_CPU, 10), (resource.RLIMIT_CORE, 0)):
        resource.setrlimit(name, (value, value))


class Channel:
    """Bounded line reader: no blocking readline or unbounded captured output."""
    def __init__(self, process):
        self.process = process
        self.buffer = bytearray()
        self.total = 0
        os.set_blocking(process.stdout.fileno(), False)

    def send(self, value):
        try:
            self.process.stdin.write((json.dumps(value) + "\n").encode())
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise CandidateFailure("worker input closed") from error


def receive(channels, deadline):
    """Collect one line per worker concurrently, under one absolute deadline."""
    received = {}
    with selectors.DefaultSelector() as selector:
        for index, channel in enumerate(channels):
            selector.register(channel.process.stdout, selectors.EVENT_READ, index)
        while len(received) < len(channels):
            for index, channel in enumerate(channels):
                if index in received or b"\n" not in channel.buffer:
                    continue
                raw, _, rest = channel.buffer.partition(b"\n")
                channel.buffer = bytearray(rest)
                try:
                    value = parse_json(raw)
                except (ValueError, UnicodeError) as error:
                    raise CandidateFailure("worker emitted invalid JSON") from error
                received[index] = value
                selector.unregister(channel.process.stdout)
            if len(received) == len(channels):
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CandidateFailure("six-second reply deadline exceeded")
            for key, _ in selector.select(remaining):
                channel = channels[key.data]
                chunk = os.read(channel.process.stdout.fileno(), 8192)
                if not chunk:
                    raise CandidateFailure("worker exited before its protocol reply")
                channel.total += len(chunk)
                if channel.total > MAX_REPLY:
                    raise CandidateFailure("64 KiB worker output limit exceeded")
                channel.buffer.extend(chunk)
    return [received[index] for index in range(len(channels))]


def stop(process):
    forced = process.poll() is None
    if forced:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=3)
    for stream in (process.stdin, process.stdout):
        if stream:
            stream.close()
    return {"returncode": process.returncode, "stopped_by_evaluator": forced}


class Sandbox:
    def __init__(self, directory, source):
        self.directory = Path(directory)
        self.state = self.directory / "state"
        self.state.mkdir()
        self.candidate = self.directory / "candidate.py"
        self.candidate.write_text(source, encoding="utf-8")
        # Copy trusted adapters separately; the grader and oracle are not mounted.
        self.worker = self.directory / "worker.py"
        self.inspector = self.directory / "inspect_state.py"
        shutil.copyfile(ROOT / "worker.py", self.worker)
        shutil.copyfile(ROOT / "inspect_state.py", self.inspector)

    def command(self, mode):
        executable = shutil.which("bwrap")
        if sys.platform != "linux" or executable is None or not Path("/usr/bin/python3").is_file():
            raise Unavailable("requires Linux, bwrap, namespaces and /usr/bin/python3")
        command = [executable, "--unshare-all", "--die-with-parent", "--new-session",
                   "--cap-drop", "ALL", "--clearenv", "--setenv", "PATH", "/usr/bin:/bin",
                   "--setenv", "HOME", "/tmp", "--setenv", "PYTHONDONTWRITEBYTECODE", "1"]
        for runtime in ("/usr", "/bin", "/lib", "/lib64"):
            if Path(runtime).exists():
                command += ["--ro-bind", runtime, runtime]
        command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--chdir", "/tmp"]
        if mode == "worker":
            command += ["--bind", str(self.state), "/state",
                        "--ro-bind", str(self.candidate), "/candidate.py",
                        "--ro-bind", str(self.worker), "/worker.py"]
            program = ["/worker.py"]
        elif mode in ("inspect", "install", "remove"):
            command += ["--ro-bind" if mode == "inspect" else "--bind", str(self.state), "/state",
                        "--ro-bind", str(self.inspector), "/inspect_state.py"]
            program = ["/inspect_state.py", "/state/ledger.sqlite"]
            if mode != "inspect":
                program.append(mode)
        else:
            program = ["-c", "print('{\"probe\":true}', flush=True)"]
        return command + ["--", "/usr/bin/python3", "-I", "-B"] + program

    def spawn(self, mode):
        return subprocess.Popen(self.command(mode), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                env={}, start_new_session=True, preexec_fn=limits)

    def preflight(self):
        process = None
        try:
            process = self.spawn("probe")
            reply = receive([Channel(process)], time.monotonic() + REPLY_SECONDS)
            if reply != [{"probe": True}]:
                raise CandidateFailure("bad isolation probe reply")
        except (OSError, subprocess.SubprocessError, CandidateFailure) as error:
            raise Unavailable("isolation preflight failed: " + str(error)) from error
        finally:
            if process is not None:
                stop(process)

    def batch(self, requests, event, allow_error=False):
        processes = []
        try:
            deadline = time.monotonic() + REPLY_SECONDS
            for _ in requests:
                processes.append(self.spawn("worker"))
            channels = [Channel(p) for p in processes]
            event["initialization_envelopes"] = receive(channels, deadline)
            if event["initialization_envelopes"] != [{"kind": "ready"}] * len(requests):
                raise CandidateFailure("service initialization failed or polluted stdout")
            for channel, request in zip(channels, requests):
                channel.send({"request": request})
            event["arming_envelopes"] = receive(channels, time.monotonic() + REPLY_SECONDS)
            if event["arming_envelopes"] != [{"kind": "armed"}] * len(requests):
                raise CandidateFailure("workers did not acknowledge their pending requests")
            event["armed_workers"] = len(channels)
            start = time.monotonic()
            for channel in channels:
                channel.send({"go": True})
            envelopes = receive(channels, start + REPLY_SECONDS)
            event["reply_elapsed_seconds"] = time.monotonic() - start
            event["envelopes"] = envelopes
            if allow_error:
                if len(envelopes) != 1:
                    raise CandidateFailure("fault probe requires one worker")
                reply = envelopes[0]
                if (type(reply) is dict and reply.get("kind") == "error"
                        and reply.get("phase") == "apply"):
                    return None
                if (type(reply) is dict and set(reply) == {"kind", "value"}
                        and reply["kind"] == "reply" and type(reply["value"]) is dict
                        and reply["value"].get("status") not in
                        ("accepted", "rejected", "payload_mismatch")):
                    return None
                raise CandidateFailure("database error was reported as a business decision")
            if any(type(x) is not dict or set(x) != {"kind", "value"}
                   or x["kind"] != "reply" for x in envelopes):
                raise CandidateFailure("candidate exception or malformed reply envelope")
            replies = [x["value"] for x in envelopes]
            event["replies"] = replies
            return replies
        finally:
            # Candidate processes are all dead before any host SQL observation.
            event["workers"] = [stop(p) for p in processes]

    def inspect(self, event):
        process = self.spawn("inspect")
        try:
            observation = receive([Channel(process)], time.monotonic() + REPLY_SECONDS)[0]
            event["inspection"] = observation
            if type(observation) is not dict or set(observation) != {"snapshot"}:
                raise CandidateFailure("independent SQL inspection failed")
            return observation["snapshot"]
        finally:
            event["inspector"] = stop(process)

    def fault(self, action, event):
        process = self.spawn(action)
        try:
            reply = receive([Channel(process)], time.monotonic() + REPLY_SECONDS)[0]
            if reply != {"fault": action}:
                raise CandidateFailure("could not " + action + " the declared SQL error probe")
            event["fault_" + action] = reply
        finally:
            event["fault_" + action + "_process"] = stop(process)


def exercise(factory, prefix=None):
    """Run exactly three isolated repetitions; factory is trusted test injection."""
    repetitions = []
    for repetition in range(REPETITIONS):
        record = {"index": repetition + 1, "checks": [], "status": "passed"}
        repetitions.append(record)
        model = Model()
        with tempfile.TemporaryDirectory(prefix="e1-eval-") as directory:
            sandbox = factory(directory)
            try:
                sandbox.preflight()
            except Unavailable as error:
                record["status"] = "unavailable"
                return "unavailable", repetitions, str(error)
            key_prefix = (prefix or uuid.uuid4().hex) + "-" + str(repetition)
            for name, requests in batches(key_prefix):
                event = {"name": name, "requests": requests}
                record["checks"].append(event)
                try:
                    if name == "other_account":
                        fault_event = {"name": "database_error_rollback", "requests": requests}
                        record["checks"].insert(-1, fault_event)
                        try:
                            sandbox.fault("install", fault_event)
                            sandbox.batch(requests, fault_event, allow_error=True)
                            fault_event["expected_tables"] = model.snapshot()
                            compare_snapshot(model, sandbox.inspect(fault_event))
                            fault_event["status"] = "passed"
                        except (ValueError, CandidateFailure, OSError, subprocess.SubprocessError) as error:
                            fault_event.update(status="failed", reason=str(error))
                            raise
                        finally:
                            if "fault_install" in fault_event:
                                sandbox.fault("remove", fault_event)
                    replies = sandbox.batch(requests, event)
                    proposed = advance(model, requests, replies)
                    event["expected_tables"] = proposed.snapshot()
                    compare_snapshot(proposed, sandbox.inspect(event))
                    model = proposed
                    event["status"] = "passed"
                except (ValueError, CandidateFailure, OSError, subprocess.SubprocessError) as error:
                    event["status"] = "failed"
                    event["reason"] = str(error)
                    record["status"] = "failed"
                    # Preserve independently inspectable failure state as well.
                    if "inspection" not in event:
                        try:
                            sandbox.inspect(event)
                        except (ValueError, CandidateFailure, OSError, subprocess.SubprocessError) as inspection_error:
                            event["inspection_error"] = str(inspection_error)
                    break
    status = "passed" if all(r["status"] == "passed" for r in repetitions) else "failed"
    return status, repetitions, None


def grade(answer, answer_sha256=None):
    result = {"task_id": "E1", "evaluation_version": 1,
              "answer_sha256": answer_sha256,
              "contract_sha256": {name: hashlib.sha256((ROOT / "input" / name).read_bytes()).hexdigest()
                                  for name in ("E1.md", "README.md")},
              "status": "invalid", "formal_status": "not_run",
              "overall_status": "invalid", "explanation_status": "not_reviewed",
              "limits": {"address_space_bytes": 512 * 1024 * 1024, "file_descriptors": 256,
                         "file_size_bytes": 8 * 1024 * 1024, "cpu_seconds": 10,
                         "reply_seconds": REPLY_SECONDS, "reply_bytes": MAX_REPLY},
              "repetitions": []}
    if type(answer) is not dict or answer.get("task_id") != "E1":
        result["reason"] = "expected an object with task_id E1"
        return result
    if type(answer.get("explanation")) is not str or not answer["explanation"].strip():
        result["reason"] = "a nonempty explanation is required"
        return result
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        result["reason"] = "alternative_format must be a Boolean"
        return result
    if answer.get("alternative_format") is True:
        if type(answer.get("alternative")) is not str or not answer["alternative"].strip():
            result["reason"] = "alternative route requires a nonempty alternative"
            return result
        result.update(status="review_required", formal_status="not_run",
                      overall_status="review_required", explanation_status="review_pending")
        return result
    if type(answer.get("code")) is not str or not answer["code"].strip():
        result["reason"] = "executable route requires a complete Service source string"
        return result
    try:
        source_bytes = answer["code"].encode("utf-8")
    except UnicodeError:
        result["reason"] = "source is not valid UTF-8 text"
        return result
    if len(source_bytes) > 256 * 1024:
        result["reason"] = "source exceeds the disclosed 256 KiB submission limit"
        return result
    # No compile, exec, import, AST plugin, or unsafe fallback in the parent.
    try:
        status, repetitions, reason = exercise(lambda directory: Sandbox(directory, answer["code"]))
    except (OSError, subprocess.SubprocessError) as error:
        status, repetitions, reason = "unavailable", [], "harness environment error: " + str(error)
    result.update(status=status, formal_status=status, repetitions=repetitions,
                  explanation_status="review_pending",
                  overall_status=("formal_pass_review_pending" if status == "passed" else status))
    if reason:
        result["reason"] = reason
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", type=Path, help="JSON with task_id, code and explanation")
    parser.add_argument("--output", type=Path, help="write a new JSON evidence file (never overwrite)")
    args = parser.parse_args(argv)
    try:
        with args.answer.open("rb") as handle:
            raw = handle.read(MAX_ANSWER + 1)
        if len(raw) > MAX_ANSWER:
            raise ValueError("answer exceeds 1 MiB")
        answer = parse_json(raw)
        result = grade(answer, hashlib.sha256(raw).hexdigest())
    except (OSError, ValueError, UnicodeError) as error:
        result = {"task_id": "E1", "status": "invalid", "formal_status": "not_run",
                  "overall_status": "invalid", "reason": str(error)}
    rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        except OSError as error:
            parser.error(str(error))
    print(rendered, end="")
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    sys.exit(main())
