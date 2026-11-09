"""Copied alone into a sandbox. No imports from the evaluator package."""
import json
import os
import resource
import sys
import types


def limits():
    for kind, value in ((resource.RLIMIT_AS, 512 * 1024 * 1024),
                        (resource.RLIMIT_NOFILE, 256),
                        (resource.RLIMIT_CPU, 10),
                        (resource.RLIMIT_FSIZE, 8 * 1024 * 1024),
                        (resource.RLIMIT_CORE, 0)):
        resource.setrlimit(kind, (value, value))


def emit(value):
    raw = json.dumps(value, allow_nan=False, separators=(",", ":"))
    if len(raw.encode("utf-8")) > 65535:
        raise ValueError("reply exceeds 64 KiB")
    print(raw, flush=True)


def main():
    limits()
    # Imported only after OS isolation and limits. stdout is a strict protocol.
    module = types.ModuleType("candidate")
    module.__file__ = "/candidate.py"
    sys.modules["candidate"] = module
    with open("/candidate.py", encoding="utf-8") as stream:
        source = stream.read()
    exec(compile(source, "/candidate.py", "exec"), module.__dict__)
    service = module.Service("/state/ledger.sqlite3")
    emit({"ready": True})
    for line in sys.stdin:
        command = json.loads(line)
        if command["op"] == "arm":
            pending = command["request"]
            emit({"armed": True})
        elif command["op"] == "go":
            emit({"reply": service.apply(pending)})
        elif command["op"] == "apply":
            emit({"reply": service.apply(command["request"])})
        elif command["op"] == "close":
            # Kill namespace descendants when its PID 1 exits, before inspection.
            os._exit(0)
        else:
            raise ValueError("unknown worker operation")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        try:
            emit({"worker_error": type(exc).__name__, "message": str(exc)[:1000]})
        finally:
            sys.exit(1)
