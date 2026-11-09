"""Only this adapter and the submitted source are mounted into a worker."""
import contextlib
import importlib.util
import json
import os
import sys


def emit(value):
    sys.__stdout__.write(json.dumps(value, allow_nan=False, separators=(',', ':')) + '\n')
    sys.__stdout__.flush()


def main():
    candidate, path, limited = sys.argv[1:]
    if limited == 'limits':
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_NOFILE, (256,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (10,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2,) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        spec = importlib.util.spec_from_file_location('submission', candidate)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        service = module.Service(path)
    emit({'ready': True})
    # Parent waits for every ready message before releasing the batch.
    request = json.loads(sys.stdin.readline())
    try:
        with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            reply = service.apply(request)
        emit({'kind': 'reply', 'value': reply})
    except Exception as error:
        emit({'kind': 'error', 'type': type(error).__name__})


if __name__ == '__main__':
    main()
