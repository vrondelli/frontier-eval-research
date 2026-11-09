"""Trusted line protocol adapter. Executed ONLY inside bubblewrap."""
import json
import os
import resource
import sys


def main():
    for limit, value in ((resource.RLIMIT_AS, 512 * 1024**2),
                         (resource.RLIMIT_NOFILE, 256),
                         (resource.RLIMIT_FSIZE, 8 * 1024**2),
                         (resource.RLIMIT_CPU, 10),
                         (resource.RLIMIT_CORE, 0)):
        resource.setrlimit(limit, (value, value))
    protocol = os.fdopen(os.dup(sys.stdout.fileno()), "w", buffering=1)
    # Normal debug output must not contaminate the protocol.
    sys.stdout = open(os.devnull, "w")

    def emit(value):
        payload = json.dumps(value, allow_nan=False, separators=(",", ":"))
        if len(payload.encode()) > 65535:
            raise ValueError("reply exceeds 64 KiB")
        protocol.write(payload + "\n")
        protocol.flush()

    try:
        import runpy
        module = runpy.run_path("/candidate.py")
        service = module["Service"]("/state/ledger.sqlite")
        emit({"event": "ready"})
        command = json.loads(sys.stdin.readline())
        if set(command) != {"request"}:
            raise ValueError("invalid arm command")
        emit({"event": "armed"})
        if json.loads(sys.stdin.readline()) != {"go": True}:
            raise ValueError("missing release")
        reply = service.apply(command["request"])
        if type(reply) is not dict:
            raise ValueError("apply must return a JSON object")
        emit({"event": "reply", "value": reply})
    except BaseException as exc:
        try:
            emit({"event": "error", "type": type(exc).__name__, "detail": str(exc)[:500]})
        finally:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
