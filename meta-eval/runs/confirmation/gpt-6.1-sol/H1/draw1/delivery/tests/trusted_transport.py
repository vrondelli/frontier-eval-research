"""UNSANDBOXED, TEST-ONLY: runs a named authored control, never a submitted file.

This checks process/SQLite behavior on Windows too. It does not validate bwrap.
The production evaluator has no path to this transport.
"""

import json
import multiprocessing
from pathlib import Path

from controls.fixtures import source
from e1eval.oracle import ContractError


def child(connection, state, control):
    try:
        namespace = {}
        exec(compile(source(control), "authored-control.py", "exec"), namespace)
        service = namespace["Service"](str(Path(state) / "ledger.sqlite"))
        connection.send({"event": "ready"})
        pending = None
        while True:
            message = connection.recv()
            if message["action"] == "stop":
                break
            if message["action"] == "arm":
                pending = message["request"]
                connection.send({"event": "armed"})
            else:
                request = pending if message["action"] == "go" else message["request"]
                pending = None
                reply = json.loads(json.dumps(service.apply(request)))
                connection.send({"event": "result", "reply": reply})
    except BaseException as exc:
        connection.send({"event": "error", "message": str(exc)})
    finally:
        connection.close()


class TrustedWorker:
    def __init__(self, state, control):
        # source() validates the name. An arbitrary candidate path is rejected.
        source(control)
        context = multiprocessing.get_context("spawn")
        self.connection, other = context.Pipe()
        self.process = context.Process(target=child, args=(other, str(state), control))
        self.process.start()
        other.close()

    def send(self, action, request=None):
        self.connection.send({"action": action, "request": request})

    def receive(self, expected):
        if not self.connection.poll(6):
            raise ContractError("trusted control timed out")
        value = self.connection.recv()
        if value.get("event") != expected:
            raise ContractError(str(value))
        return value

    def close(self):
        try:
            self.send("stop")
        except (OSError, EOFError):
            pass
        self.process.join(1)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(2)
        self.connection.close()
        return self.process.exitcode
