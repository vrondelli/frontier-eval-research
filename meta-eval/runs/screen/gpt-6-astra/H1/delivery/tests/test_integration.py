"""Real isolated process checks. Skips explicitly when Linux isolation is absent."""
import tempfile
import unittest

from evaluation.runner import grade
from evaluation.sandbox import Sandbox, Unavailable
from tests.make_controls import answer


class LinuxIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            sandbox = Sandbox()
            with tempfile.TemporaryDirectory() as state:
                sandbox.preflight(state)
        except Unavailable as exc:
            raise unittest.SkipTest(str(exc))

    def test_authored_reference_passes_three_real_process_repetitions(self):
        result = grade(answer("reference"))
        self.assertEqual(result["formal_status"], "pass", result)
        self.assertEqual(len(result["repetitions"]), 3)
        self.assertEqual(result["overall_status"], "formal_pass_review_pending")

    def test_faulty_implementations_fail(self):
        for name in ("missing_ledger", "lost_rejection", "ignore_mismatch", "account_scoped_key",
                     "historical_remaining", "reset_on_init", "always_reject", "overdraw"):
            with self.subTest(control=name):
                result = grade(answer(name))
                self.assertEqual(result["formal_status"], "fail", result)

    def test_database_exception_is_not_a_business_decision(self):
        code = 'class Service:\n def __init__(self, path): pass\n def apply(self, request): raise RuntimeError("database error")'
        result = grade({"task_id": "E1", "code": code, "explanation": "Authored error control."})
        self.assertEqual(result["formal_status"], "fail", result)
        self.assertTrue(any("raw_responses" in phase for repetition in result["repetitions"]
                            for phase in repetition["phases"]))


if __name__ == "__main__":
    unittest.main()
