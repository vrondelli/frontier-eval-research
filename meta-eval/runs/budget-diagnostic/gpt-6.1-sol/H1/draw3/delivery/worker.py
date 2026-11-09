"""Sandbox entry point. Deliberately contains no oracle or benchmark imports."""
import json
import resource
import sys


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (256,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    from candidate import Service

    service = Service('/state/service.sqlite')
    request = json.loads(sys.stdin.readline())
    print(json.dumps({'armed': True}), flush=True)
    if sys.stdin.readline() != 'go\n':
        raise RuntimeError('release missing')
    result = service.apply(request)
    print(json.dumps({'reply': result}, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
