"""Deterministic grader tests. These do NOT establish isolated concurrent execution."""
import contextlib
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from benchmark import load, main, save_exclusive
from evaluation import grader
from evaluation.grader import checked, core_case, identity_case
from evaluation.inspector import inspect
from evaluation.oracle import Model, choose_overlap, exact, request
from evaluation.protocol import finish, initial_view, reveal, review_template, start, validate_review
from evaluation.sandbox import CandidateError, Group, Unavailable, overlap, strict_json


REFERENCE = grader.ROOT / "examples/reference_service.py"


def authored_class(code):
    # Test fixture code only. NEVER feed a submitted answer to this helper.
    scope = {}
    exec(compile(code, "authored-control", "exec"), scope)
    return scope["Service"]


class LocalWorker:
    def __init__(self, cls, path):
        self.service = cls(str(path))

    def call(self, req):
        return self.service.apply(req)


def deterministic_case(cls, kind="core", reverse=False):
    """Exercise the scenario/oracle against known fixtures without unsafe fallback."""
    class LocalGroup:
        def __init__(self, source, state, transcript, label):
            self.state = state

        def __enter__(self):
            return [LocalWorker(cls, self.state / "ledger.sqlite") for _ in range(2)]

        def __exit__(self, *_):
            pass

    def serial_overlap(workers, requests):
        result = [None, None]
        for i in ((1, 0) if reverse else (0, 1)):
            result[i] = workers[i].call(requests[i])
        return result

    result = {"checks": [], "transcript": []}
    with tempfile.TemporaryDirectory(dir=grader.ROOT) as temp, \
            patch.object(grader, "Group", LocalGroup), \
            patch.object(grader, "overlap", serial_overlap), \
            patch.object(grader, "inspect_stopped", lambda state: inspect(state / "ledger.sqlite")):
        if kind == "core":
            core_case(REFERENCE, Path(temp), result)
        else:
            identity_case(REFERENCE, Path(temp), result, kind == "conflict")
    return result


MUTATIONS = {
    "always_accept": ("status = 'accepted' if amount <= remaining else 'rejected'", "status = 'accepted'"),
    "no_ledger": ("conn.execute('INSERT INTO ledger VALUES(?,?,?)', (key, account, amount))", "pass"),
    "lost_rejection": (
        "conn.execute('INSERT INTO decisions VALUES(?,?,?,?,?)',\n                             (key, account, amount, status, remaining))",
        "conn.execute('INSERT INTO decisions VALUES(?,?,?,?,?)',\n                             (key, account, amount, status, remaining)) if status == 'accepted' else None"),
    "recomputed_history": ("'remaining': old[3]", "'remaining': conn.execute('SELECT remaining FROM accounts WHERE account=?', (account,)).fetchone()[0]"),
    "ignores_conflict": ("if old[:2] == (account, amount)", "if True"),
    "reset_on_init": ("INSERT OR IGNORE INTO accounts", "INSERT OR REPLACE INTO accounts"),
    "reply_without_commit": ("conn.execute('COMMIT')", "conn.execute('ROLLBACK')"),
    "wrong_rejection_history": ("status, remaining))", "status, remaining if status == 'accepted' else 0))"),
}


class OracleTests(unittest.TestCase):
    def test_explicit_histories(self):
        model = Model()
        self.assertEqual(model.apply(request("one")), {"status": "accepted", "remaining": 40})
        self.assertEqual(model.apply(request("two")), {"status": "rejected", "remaining": 40})
        self.assertEqual(model.apply(request("later", amount=1)), {"status": "accepted", "remaining": 39})
        self.assertEqual(model.apply(request("two")), {"status": "rejected", "remaining": 40})
        self.assertEqual(model.apply(request("one", "B")), {"status": "payload_mismatch", "remaining": None})
        self.assertEqual(model.snapshot()["ledger"], [["later", "A", 1], ["one", "A", 60]])

    def test_both_race_orders_and_impossible_outcome(self):
        accepted = {"status": "accepted", "remaining": 40}
        rejected = {"status": "rejected", "remaining": 40}
        for replies in ([accepted, rejected], [rejected, accepted]):
            self.assertEqual(choose_overlap(request("x"), request("y"), replies).accounts["A"], 40)
        with self.assertRaises(AssertionError):
            choose_overlap(request("x"), request("y"), [accepted, accepted])

    def test_types_and_exact_keys(self):
        self.assertFalse(exact(1, True))
        self.assertFalse(exact(40, 40.0))
        self.assertFalse(exact({"status": "accepted"}, {"status": "accepted", "remaining": 40}))

    def test_duplicate_and_nonfinite_json_rejected(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(raw)


class ScenarioControls(unittest.TestCase):
    def test_authored_positive_both_serial_orders(self):
        for fixture in (REFERENCE, REFERENCE.with_name("conditional_update_service.py")):
            cls = authored_class(fixture.read_text())
            for reverse in (False, True):
                for kind in ("core", "duplicate", "conflict"):
                    with self.subTest(fixture=fixture.name, reverse=reverse, kind=kind):
                        result = deterministic_case(cls, kind, reverse)
                        self.assertTrue(result["checks"])
                        self.assertTrue(all(check["pass"] for check in result["checks"]))

    def test_authored_negative_controls(self):
        source = REFERENCE.read_text()
        for name, (before, after) in MUTATIONS.items():
            with self.subTest(mutation=name):
                self.assertIn(before, source)
                cls = authored_class(source.replace(before, after))
                with self.assertRaises((CandidateError, sqlite3.Error)):
                    deterministic_case(cls)

    def test_canned_replies_cannot_hide_wrong_disk_state(self):
        with self.assertRaises(CandidateError):
            checked("disk", {"accounts": [["A", -20]]}, {"accounts": [["A", 40]]}, [])

    def test_barrier_arms_both_before_either_release(self):
        events = []

        class Transport:
            def __init__(self, label):
                self.label = label

            def send(self, command):
                events.append((self.label, command["op"]))

            def receive(self, event, deadline):
                events.append((self.label, event))
                return {"status": "accepted", "remaining": 40}

        overlap([Transport("left"), Transport("right")], [request("x"), request("y")])
        self.assertEqual(events[:6], [("left", "arm"), ("right", "arm"),
                                     ("left", "armed"), ("right", "armed"),
                                     ("left", "release"), ("right", "release")])

    def test_group_spawns_both_before_waiting(self):
        events = []

        class Transport:
            def __init__(self, *args):
                self.label = args[-1]
                events.append(("spawn", self.label))

            def receive(self, *args):
                events.append(("ready", self.label))

            def stop(self):
                events.append(("stop", self.label))

        with patch("evaluation.sandbox.Worker", Transport):
            with Group(None, None, [], "test"):
                pass
        self.assertEqual([kind for kind, _ in events], ["spawn", "spawn", "ready", "ready", "stop", "stop"])


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=grader.ROOT)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite"
        self.cls = authored_class(REFERENCE.read_text())
        self.cls(str(self.path))

    def test_independent_public_tables(self):
        self.cls(str(self.path)).apply(request("one"))
        self.assertEqual(inspect(self.path)["accounts"], [["A", 40], ["B", 100]])

    def test_views_are_not_public_tables(self):
        with contextlib.closing(sqlite3.connect(self.path)) as conn:
            conn.executescript("ALTER TABLE ledger RENAME TO hidden; CREATE VIEW ledger AS SELECT * FROM hidden;")
        with self.assertRaisesRegex(ValueError, "real"):
            inspect(self.path)

    def test_primary_key_required(self):
        with contextlib.closing(sqlite3.connect(self.path)) as conn:
            conn.executescript("DROP TABLE ledger; CREATE TABLE ledger(key TEXT,account TEXT,amount INTEGER);")
        with self.assertRaisesRegex(ValueError, "primary key"):
            inspect(self.path)

    def test_sidecar_directory_rejected(self):
        Path(str(self.path) + "-wal").mkdir()
        with self.assertRaisesRegex(ValueError, "regular"):
            inspect(self.path)

    def test_row_limit(self):
        with contextlib.closing(sqlite3.connect(self.path)) as conn:
            conn.executemany("INSERT INTO ledger VALUES(?, 'A', 1)", [(str(i),) for i in range(100)])
            conn.commit()
        with self.assertRaisesRegex(ValueError, "100"):
            inspect(self.path)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.answer = json.loads((grader.ROOT / "examples/E1.json").read_text())

    def test_inputs_still_bound(self):
        self.assertEqual(len(grader.bindings()), 2)

    def test_reference_json_matches_authored_assets(self):
        self.assertEqual(self.answer["code"], REFERENCE.read_text(encoding="utf-8"))
        self.assertEqual(self.answer["explanation"], REFERENCE.with_name("reference_explanation.txt").read_text(encoding="utf-8"))

    def test_reveal_is_withheld_initially(self):
        view = initial_view()["prompt"]
        for secret in ("F6.", "hot-account", "deadlock", "rollback trigger"):
            self.assertNotIn(secret, view)
        state = reveal(start(), self.answer)
        self.assertIn("F6.", state["view"]["prompt"])
        state["initial_answer"]["explanation"] += " altered"
        with self.assertRaisesRegex(ValueError, "changed"):
            finish(state, self.answer)

    def test_staged_finish_and_exclusive_files(self):
        state = reveal(start(), self.answer)
        with patch("evaluation.protocol.grade", return_value={"formal_status": "pass"}):
            result = finish(state, self.answer)
        self.assertTrue(result["staged"])
        with tempfile.TemporaryDirectory(dir=grader.ROOT) as temp:
            path = Path(temp) / "state.json"
            save_exclusive(path, state)
            self.assertEqual(load(path), state)
            with self.assertRaises(FileExistsError):
                save_exclusive(path, state)

    def test_alternative_receives_review_not_execution(self):
        answer = {"task_id": "E1", "alternative_format": True,
                  "alternative": "per-account sequencer", "explanation": "manual assessment needed"}
        with patch.object(grader, "probe", side_effect=AssertionError("must not execute")):
            self.assertEqual(grader.grade(answer)["formal_status"], "review_required")

    def test_unavailable_never_executes_candidate(self):
        self.answer["code"] = "raise RuntimeError('never execute outside sandbox')"
        with patch.object(grader, "probe", side_effect=Unavailable("test isolation unavailable")):
            report = grader.grade(self.answer)
        self.assertEqual(report["formal_status"], "unavailable")
        self.assertEqual(report["cases"], [])

    def test_invalid_answers(self):
        for answer in ({}, [], {"task_id": "E1", "code": "pass", "explanation": ""},
                       {"task_id": "E1", "alternative_format": "yes", "explanation": "x"}):
            self.assertEqual(grader.grade(answer)["formal_status"], "invalid")

    def test_review_binding_and_quotes(self):
        review = review_template(self.answer, "reviewer-A")
        review["independence_declaration"] = "I did not author this answer."
        for entry in review["criteria"].values():
            entry.update(rating=1, quotes=["BEGIN IMMEDIATE"], rationale="Test structural validation only.")
        self.assertEqual(validate_review(self.answer, review)["review_status"], "structurally_valid")
        bad = copy.deepcopy(review)
        bad["criteria"]["atomic_boundary"]["quotes"] = ["this quotation does not exist"]
        with self.assertRaises(ValueError):
            validate_review(self.answer, bad)
        changed = dict(self.answer, explanation=self.answer["explanation"] + " edited")
        with self.assertRaises(ValueError):
            validate_review(changed, review)


if __name__ == "__main__":
    unittest.main()
