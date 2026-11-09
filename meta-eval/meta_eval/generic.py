"""Owner-manifest interface for new eval packages and end-to-end calibration."""
import json
import re
from pathlib import Path

from .core import blank, dump, inventory, score, set_check, sha
from .engine import evidence
from .runtime import doctor, docker_command, execute_isolated


def pointer(value, path):
    for part in path.strip("/").split("/") if path else []:
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def artifact_path(package, relative):
    path = (package / relative).resolve()
    if not path.is_relative_to(package) or path.is_symlink():
        raise ValueError("Artifact path escapes submitted package")
    return path


def aggregate(package, job, executed):
    op = job["operation"]
    def value(name):
        result = executed[name][0]
        if result.get("status") != "completed" or result.get("exit_code") != 0:
            raise ValueError("Dependent native observation unavailable")
        return result["decoded"]["value"]
    if op == "text_contains":
        text = artifact_path(package, job["file"]).read_text()
        return {"value": all(s in text for s in job["required"])}
    if op == "token_exposure":
        code = artifact_path(package, job["code_file"]).read_text()
        public = artifact_path(package, job["public_file"]).read_text()
        return {"value": job["token"] not in code or job["token"] in public}
    actual = [value(name) for name in job["observations"]]
    if op == "observations_valid":
        return {"value": bool(actual) and all(type(x) is bool for x in actual)}
    if op == "runner_matches":
        return {"value": value(job["runner"]) == actual}
    if op == "labels_match":
        return {"value": actual == job["labels"]}
    if op == "report_matches":
        report = json.loads(artifact_path(package, job["file"]).read_text())
        expected = len(actual) if job["metric"] == "count" else sum(a == e for a, e in zip(actual, job["labels"])) if job["metric"] == "correct_count" else actual == job["labels"]
        return {"value": type(report[job["field"]]) is type(expected) and report[job["field"]] == expected}
    raise ValueError("Unsupported safe aggregate operation")


def run_manifest(root, package, manifest_path, output, image="python:3.14-slim", calibration=False):
    package, manifest_path, output = package.resolve(), manifest_path.resolve(), output.resolve()
    if output.is_relative_to(package):
        raise ValueError("Output must be outside immutable subject")
    if manifest_path.is_relative_to(package):
        raise ValueError("Outer expected judgments must be owner-side, outside the submitted package")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema_version") != "meta-eval-owner-manifest/v1":
        raise ValueError("Unsupported owner manifest")
    before = inventory(package)
    if manifest.get("package_hashes") and manifest["package_hashes"] != before:
        raise ValueError("Submitted package differs from bound manifest")
    capabilities = doctor(root, image)
    checks, executed = blank(), {}
    output.mkdir(parents=True, exist_ok=True)
    job_ids = [job["id"] for job in manifest["jobs"]]
    if len(job_ids) != len(set(job_ids)) or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,80}", name) for name in job_ids):
        raise ValueError("Invalid or duplicate job IDs")
    for job in manifest["jobs"]:
        if job.get("kind") == "aggregate":
            try:
                observed = aggregate(package, job, executed)
                result = {"status": "completed", "exit_code": 0, "decoded": observed, "method": "trusted_host_data_only_aggregate"}
            except (KeyError, ValueError, TypeError, OSError) as e:
                result = {"status": "unavailable", "decoded": None, "reason": str(e)}
            path = output / (job["id"] + ".json")
            dump(path, result)
            executed[job["id"]] = (result, evidence(path, root))
            continue
        mounts = [(package, "/subject")]
        for mount in job.get("owner_mounts", []):
            source = (manifest_path.parent / mount["path"]).resolve()
            if not source.is_relative_to(manifest_path.parent) or source.is_symlink():
                raise ValueError("Owner fixture mount escapes manifest directory")
            if not mount["target"].startswith("/owner/") or ".." in Path(mount["target"]).parts:
                raise ValueError("Owner fixture mount must stay under /owner/")
            mounts.append((source, mount["target"]))
        command = docker_command(mounts, job["code"], image)
        result = execute_isolated(command, root, job.get("timeout", 60)) if capabilities["docker"] else {"status": "unavailable", "decoded": None}
        path = output / (job["id"] + ".json")
        dump(path, result)
        executed[job["id"]] = (result, evidence(path, root))
    seen = set()
    for rule in manifest["checks"]:
        key = rule["id"]
        if key in seen or key not in checks:
            raise ValueError("Duplicate or unrecognized scoring rule")
        seen.add(key)
        result, ev = executed[rule["job"]]
        if result.get("status") != "completed" or result.get("exit_code") != 0 or result.get("decoded") is None:
            set_check(checks, key, "unknown", "Native checker unavailable/failed; no invented subject judgment", [ev])
            continue
        try:
            actual = pointer(result["decoded"], rule["pointer"])
        except (KeyError, IndexError, TypeError, ValueError):
            set_check(checks, key, "unknown", "Owner adapter returned no required evidence field", [ev])
            continue
        if rule.get("unknown_value") == actual and "unknown_value" in rule:
            state = "unknown"
        else:
            state = "pass" if type(actual) is type(rule["expected"]) and actual == rule["expected"] else "fail"
        set_check(checks, key, state, rule["obligation"], [ev])
        checks[key]["observed_value"] = actual
        checks[key]["expected_value"] = rule["expected"]
    # A review record is a declaration bound to these exact bytes, not authenticated expertise.
    review = manifest.get("human_review", {})
    human = review.get("completed") is True and review.get("package_hashes") == before and bool(review.get("reviewer"))
    qualified = manifest.get("owner_qualification_complete") is True
    computed = score(checks, qualified=qualified, human_review=human)
    if calibration:
        computed["calibration_expectation_only"] = True
    after = inventory(package)
    if before != after:
        raise RuntimeError("Scored package changed")
    report = {"schema_version": "meta-eval-manifest-score/v1", "package": str(package), "package_hashes": before,
              "owner_manifest_sha256": sha(manifest_path), "scoring": computed, "checks": list(checks.values()),
              "execution_count": len(executed), "model_calls": 0, "subject_unchanged": True,
              "human_review_record_present": human,
              "qualification_note": "Owner-manifest checks and expected values must themselves be qualified. A declaration is not independent certification."}
    dump(output / "SCORE.json", report)
    return report
