"""Adapter executed ONLY inside bubblewrap. It has no evaluator or oracle access."""
import importlib.util
import json
import resource
import sys


def emit(value):
    print(json.dumps(value, allow_nan=False, separators=(",", ":")), flush=True)


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (256,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (10,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    spec = importlib.util.spec_from_file_location("candidate", "/candidate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service = module.Service("/state/ledger.sqlite")
    emit({"event": "ready"})
    for line in sys.stdin:
        command = json.loads(line)
        if command["op"] == "arm":
            emit({"event": "armed"})
            release = json.loads(sys.stdin.readline())
            if release != {"op": "go"}:
                raise ValueError("invalid barrier release")
        elif command["op"] != "apply":
            raise ValueError("invalid command")
        # Exceptions are execution failures, never business rejections.
        try:
            emit({"event": "reply", "value": service.apply(command["request"])})
        except Exception as exc:
            emit({"event": "error", "type": type(exc).__name__, "message": str(exc)[:1024]})


if __name__ == "__main__":
    main()
