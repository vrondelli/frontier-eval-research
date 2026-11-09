"""Trusted one-request adapter. Production use is exclusively through bubblewrap."""
import importlib.util
import json
import os
import sys


def limits():
    if os.name == "posix":
        import resource
        for kind, bound in ((resource.RLIMIT_AS, 512 * 1024 * 1024),
                            (resource.RLIMIT_NOFILE, 256),
                            (resource.RLIMIT_CPU, 10),
                            (resource.RLIMIT_FSIZE, 8 * 1024 * 1024),
                            (resource.RLIMIT_CORE, 0)):
            resource.setrlimit(kind, (bound, bound))


def emit(value):
    print(json.dumps(value, allow_nan=False, separators=(",", ":")), flush=True)


def read():
    line = sys.stdin.buffer.readline(65537)
    if not line or len(line) > 65536:
        raise ValueError("missing or oversized parent command")
    return json.loads(line)


def main():
    limits()
    spec = importlib.util.spec_from_file_location("candidate", sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service = module.Service(sys.argv[2])
    emit({"event": "ready"})
    command = read()
    if command.get("op") != "arm":
        raise ValueError("expected arm")
    req = command["request"]
    emit({"event": "armed"})
    if read() != {"op": "go"}:
        raise ValueError("expected go")
    result = service.apply(req)
    if type(result) is not dict or set(result) != {"status", "remaining"}:
        raise ValueError("apply must return exactly status and remaining")
    status, remaining = result["status"], result["remaining"]
    if status not in ("accepted", "rejected", "payload_mismatch"):
        raise ValueError("unknown business status")
    if status == "payload_mismatch":
        if remaining is not None:
            raise ValueError("mismatch remaining must be null")
    elif type(remaining) is not int or remaining < 0:
        raise ValueError("remaining must be a nonnegative integer")
    emit({"event": "result", "reply": result})


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        # Exceptions are execution failures, never synthetic rejected decisions.
        emit({"event": "error", "kind": type(exc).__name__, "detail": str(exc)[:1000]})
        sys.exit(1)
