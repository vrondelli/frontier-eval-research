"""Trusted sandbox adapter; intentionally does not contain the test plan/oracle."""
import importlib.util
import json
import os
import resource
import sys


def main():
    for kind, limit in ((resource.RLIMIT_AS, 512 * 1024 * 1024),
                        (resource.RLIMIT_NOFILE, 256),
                        (resource.RLIMIT_FSIZE, 8 * 1024 * 1024),
                        (resource.RLIMIT_CPU, 10), (resource.RLIMIT_CORE, 0)):
        resource.setrlimit(kind, (limit, limit))
    # Candidate prints are diagnostics, not protocol messages.
    wire = os.fdopen(os.dup(sys.stdout.fileno()), "w", buffering=1)
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

    def emit(value):
        wire.write(json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n")
        wire.flush()

    try:
        spec = importlib.util.spec_from_file_location("candidate", "/app/candidate.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        service = module.Service("/state/ledger.sqlite")
        emit({"event": "ready"})
        request = None
        for line in sys.stdin:
            command = json.loads(line)
            if command["op"] == "close":
                return
            if command["op"] == "arm":
                request = command["request"]
                emit({"event": "armed"})
            elif command["op"] == "go" and request is not None:
                try:
                    reply = service.apply(request)
                    if not isinstance(reply, dict):
                        raise TypeError("apply must return a JSON object")
                    emit({"event": "result", "reply": reply})
                except BaseException as exc:
                    emit({"event": "error", "error_type": type(exc).__name__})
                request = None
            else:
                raise ValueError("invalid adapter command")
    except BaseException as exc:
        emit({"event": "startup_error", "error_type": type(exc).__name__})
        sys.exit(1)


if __name__ == "__main__":
    main()
