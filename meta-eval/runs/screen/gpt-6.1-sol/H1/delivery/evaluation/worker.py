"""Trusted transport adapter. Executed only inside bubblewrap, never imported by grader."""
import importlib.util
import json
import resource
import sys


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    spec = importlib.util.spec_from_file_location("candidate", "/candidate.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    service = module.Service("/state/ledger.sqlite")
    emit = lambda value: print(json.dumps(value, allow_nan=False), flush=True)
    emit({"event": "ready"})
    pending = None
    for line in sys.stdin:
        command = json.loads(line)
        if command["op"] == "arm" and pending is None:
            pending = command["request"]
            emit({"event": "armed"})
        elif command["op"] == "release" and pending is not None:
            request, pending = pending, None
            # Exceptions are transport failures, never synthetic business rejections.
            emit({"event": "reply", "value": service.apply(request)})
        else:
            raise ValueError("invalid worker protocol")


if __name__ == "__main__":
    main()
