"""Real isolated execution. Skips explicitly when the required runtime is absent."""
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from benchmark import load
from evaluation.grader import ROOT, grade
from evaluation.sandbox import Unavailable, probe


class IsolatedExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            try:
                probe(Path(temp))
            except Unavailable as exc:
                raise unittest.SkipTest(str(exc))

    def test_authored_reference_passes_all_nine_cases(self):
        for filename in ("reference_service.py", "conditional_update_service.py"):
            with self.subTest(fixture=filename):
                answer = load(ROOT / "examples/E1.json")
                answer["code"] = (ROOT / "examples" / filename).read_text()
                report = grade(answer)
                self.assertEqual(report["formal_status"], "pass", report)
                self.assertEqual(len(report["cases"]), 9)

    def test_read_then_write_race_is_detected(self):
        answer = load(ROOT / "examples/E1.json")
        answer["code"] = answer["code"].replace("BEGIN IMMEDIATE", "BEGIN").replace(
            "status = 'accepted' if amount <= remaining else 'rejected'",
            "import time; time.sleep(0.15)\n                status = 'accepted' if amount <= remaining else 'rejected'")
        report = grade(answer)
        self.assertEqual(report["formal_status"], "fail", report)
        self.assertTrue(any(c["status"] == "fail" for c in report["cases"] if c["id"].startswith("allowance/")))

    def test_candidate_cannot_read_host_workspace_or_network(self):
        answer = load(ROOT / "examples/E1.json")
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            secret = Path(temp) / "host-secret"
            secret.write_text("host-only test sentinel")
            prefix = f'''import os, socket
assert not os.path.exists({str(secret)!r})
assert 'E1_EVALUATOR_SECRET' not in os.environ
try:
    socket.create_connection(('1.1.1.1', 443), timeout=0.1)
except OSError:
    pass
else:
    raise AssertionError('network isolation absent')
'''
            answer["code"] = prefix + answer["code"]
            with patch.dict(os.environ, {"E1_EVALUATOR_SECRET": "must-not-be-inherited"}):
                report = grade(answer)
            self.assertEqual(report["formal_status"], "pass", report)


if __name__ == "__main__":
    unittest.main()
