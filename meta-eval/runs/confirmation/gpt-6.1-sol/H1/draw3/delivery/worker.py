"""Read-only candidate adapter copied into the Linux sandbox, never the oracle."""
import importlib.util
import json
import sys

PHASE = "initialization"

def emit(value):
    print(json.dumps(value, separators=(",", ":"), allow_nan=False), flush=True)


def main():
    global PHASE
    # Both workers must finish construction and acknowledge the same request
    # before the parent releases either apply call.
    spec = importlib.util.spec_from_file_location("submission", "/candidate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service = module.Service("/state/ledger.sqlite")
    emit({"kind": "ready"})
    command = json.loads(sys.stdin.readline())
    if set(command) != {"request"}:
        raise ValueError("invalid arm command")
    emit({"kind": "armed"})
    if json.loads(sys.stdin.readline()) != {"go": True}:
        raise ValueError("invalid release")
    PHASE = "apply"
    result = service.apply(command["request"])
    emit({"kind": "reply", "value": result})


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        emit({"kind": "error", "phase": PHASE,
              "error": type(error).__name__, "detail": str(error)[:2000]})
        sys.exit(1)
