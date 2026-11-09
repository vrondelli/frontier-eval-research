"""Isolated JSONL adapter. Executed by path; does not import the evaluator."""

import contextlib
import importlib.util
import json
import os
import resource
import sys


def main():
    for limit, value in ((resource.RLIMIT_AS, 512 * 1024 * 1024),
                         (resource.RLIMIT_NOFILE, 256),
                         (resource.RLIMIT_FSIZE, 8 * 1024 * 1024),
                         (resource.RLIMIT_CPU, 10)):
        resource.setrlimit(limit, (value, value))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    protocol = sys.stdout

    def emit(value):
        raw = json.dumps(value, allow_nan=False)
        if len(raw.encode()) > 65535:
            raise ValueError("reply exceeds 64 KiB")
        protocol.write(raw + "\n")
        protocol.flush()

    with open(os.devnull, "w") as silent, contextlib.redirect_stdout(silent), contextlib.redirect_stderr(silent):
        try:
            spec = importlib.util.spec_from_file_location("submission", "/candidate.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            service = module.Service("/state/ledger.sqlite")
            emit({"event": "ready"})
            pending = None
            for raw in sys.stdin:
                message = json.loads(raw)
                action = message["action"]
                if action == "stop":
                    return
                if action == "arm":
                    pending = message["request"]
                    emit({"event": "armed"})
                elif action in ("go", "apply"):
                    request = pending if action == "go" else message["request"]
                    pending = None
                    reply = service.apply(request)
                    # Round-trip to enforce the JSON object interface.
                    emit({"event": "result", "reply": reply})
                else:
                    raise ValueError("unknown adapter action")
        except BaseException as exc:
            emit({"event": "error", "error_type": type(exc).__name__,
                  "message": str(exc)[:1000]})
            raise SystemExit(1)


if __name__ == "__main__":
    main()
