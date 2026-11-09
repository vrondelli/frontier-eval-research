"""Execute subject code only in bounded Docker or qualified bubblewrap."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import uuid


def run(command, cwd, timeout=120):
    started = time.monotonic()
    cap = 16 * 1024 * 1024
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            p = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                 stdout=stdout, stderr=stderr, start_new_session=True)
        except OSError as e:
            return {"status": "unavailable", "error": str(e), "command": command, "exit_code": None}
        status = "completed"
        while p.poll() is None:
            if time.monotonic() - started > timeout:
                status = "timeout"
            if os.fstat(stdout.fileno()).st_size > cap or os.fstat(stderr.fileno()).st_size > cap:
                status = "output_limit"
            if status != "completed":
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                p.wait()
                break
            try:
                p.wait(timeout=0.05)
            except subprocess.TimeoutExpired:
                pass
        sizes = [os.fstat(f.fileno()).st_size for f in [stdout, stderr]]
        if max(sizes) > cap:
            status = "output_limit"
        stdout.seek(0); stderr.seek(0)
        out, err = stdout.read(cap).decode("utf8", "replace"), stderr.read(cap).decode("utf8", "replace")
    return {"status": status, "exit_code": p.returncode, "seconds": time.monotonic() - started,
            "stdout": out, "stderr": err, "command": command, "output_capture_cap_bytes": cap,
            "observed_stdout_bytes": sizes[0], "observed_stderr_bytes": sizes[1]}


def decode(receipt):
    if receipt.get("status") != "completed" or receipt.get("exit_code") not in (0, 1, 2):
        return None
    try:
        return json.loads(receipt.get("stdout", ""))
    except ValueError:
        return None


def verdict(value):
    if not isinstance(value, dict):
        return None
    if isinstance(value.get("report"), dict):
        # Coached wrapper and CLI adapters expose the actual native report here.
        nested = verdict(value["report"])
        if nested is not None:
            return nested
    for key in ["pass_verdict", "actual_saved_bad_cli_accepted", "all_passed", "success", "passed", "pass"]:
        if type(value.get(key)) is bool:
            return value[key]
    for key in ["formal_status", "status"]:
        if value.get(key) in ("pass", "fail"):
            return value[key] == "pass"
    if isinstance(value.get("new_eval_report"), dict):
        return verdict(value["new_eval_report"])
    return None


def doctor(root, image="python:3.14-slim"):
    result = {"platform": os.name, "linux_required": os.name == "posix", "docker": False, "bubblewrap": False}
    if shutil.which("docker"):
        probe = run(["docker", "image", "inspect", image, "--format", "{{.Id}}"], root, 20)
        result["docker"] = probe.get("exit_code") == 0
        result["image"] = image
        result["image_id"] = probe.get("stdout", "").strip()
    if shutil.which("bwrap"):
        probe = run(["bwrap", "--unshare-all", "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64", "--symlink", "usr/bin", "/bin", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "/usr/bin/python3", "-c", "print(123)"], root, 20)
        result["bubblewrap"] = probe.get("exit_code") == 0 and probe.get("stdout", "").strip() == "123"
    return result


def docker_command(mounts, code, image="python:3.14-slim", workdir="/tmp", memory="512m"):
    name = "meta-eval-" + uuid.uuid4().hex
    command = ["docker", "run", "--rm", "--name", name, "--network", "none", "--read-only",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--pids-limit", "128",
               "--memory", memory, "--cpus", "1", "--tmpfs", "/tmp:rw,nosuid,size=128m"]
    for source, target in mounts:
        command += ["--mount", f"type=bind,source={source},target={target},readonly"]
    command += ["-w", workdir, image, "python", "-B", "-c", code]
    return command


def execute_isolated(command, root, timeout=120):
    # Imported recipes are owner-side native adapters, not subject-provided host commands.
    if not command or command[0] not in {"docker", "bwrap"}:
        raise ValueError("Untrusted execution requires docker or bubblewrap")
    command = list(command)
    if command[0] == "docker":
        if "--network" not in command or command[command.index("--network") + 1] != "none":
            raise ValueError("Network must be disabled")
        if "--privileged" in command or "--read-only" not in command:
            raise ValueError("Unsafe Docker configuration")
        if "--name" in command:
            command[command.index("--name") + 1] = "meta-eval-" + uuid.uuid4().hex
        else:
            command[2:2] = ["--name", "meta-eval-" + uuid.uuid4().hex]
    result = run(command, root, timeout)
    if command[0] == "docker" and (result["status"] != "completed" or result.get("exit_code") not in (0, 1, 2)):
        cleanup = run(["docker", "rm", "-f", command[command.index("--name") + 1]], root, 20)
        result["container_cleanup_exit"] = cleanup.get("exit_code")
    result["decoded"] = decode(result)
    return result
