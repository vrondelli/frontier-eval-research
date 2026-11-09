"""Pure contract model. Candidate code is never imported here."""
import copy
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class Model:
    def __init__(self):
        self.accounts = {"A": 100, "B": 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, request):
        key, account, amount = (request[x] for x in ("key", "account", "amount"))
        if key in self.decisions:
            old = self.decisions[key]
            if (account, amount) != (old[1], old[2]):
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": old[3], "remaining": old[4]}
        remaining = self.accounts[account]
        status = "accepted" if amount <= remaining else "rejected"
        if status == "accepted":
            remaining -= amount
            self.accounts[account] = remaining
            self.ledger[key] = [key, account, amount]
        self.decisions[key] = [key, account, amount, status, remaining]
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": [[a, self.accounts[a]] for a in sorted(self.accounts)],
            "decisions": [self.decisions[k] for k in sorted(self.decisions)],
            "ledger": [self.ledger[k] for k in sorted(self.ledger)],
        }


def primary_plan(prefix):
    first = {"key": prefix + "-x", "account": "A", "amount": 60}
    second = {"key": prefix + "-y", "account": "A", "amount": 60}
    # Both identity dimensions are changed separately, for both decisions.
    rest = [copy.copy(first), copy.copy(second)]
    for original in (first, second):
        rest += [dict(original, amount=61), dict(original, account="B")]
    rest += [{"key": prefix + "-b", "account": "B", "amount": 100}]
    return {"overlap": [first, second], "sequential": rest}


def expected_primary(plan):
    outcomes = []
    for order in ((0, 1), (1, 0)):
        model = Model()
        replies = [None, None]
        for index in order:
            replies[index] = model.apply(plan["overlap"][index])
        replies += [model.apply(req) for req in plan["sequential"]]
        outcomes.append({"serial_order": list(order), "replies": replies,
                         "snapshot": model.snapshot()})
    return outcomes


def judge_primary(plan, replies, snapshot):
    outcomes = expected_primary(plan)
    reply_matches = [o for o in outcomes if canonical(o["replies"]) == canonical(replies)]
    disk_matches = [o for o in outcomes if canonical(o["snapshot"]) == canonical(snapshot)]
    consistent = [o for o in reply_matches if o in disk_matches]
    checks = {
        "overlap_has_one_accept_and_one_reject": any(
            canonical(o["replies"][:2]) == canonical(replies[:2]) for o in outcomes),
        "fresh_process_replays_are_exact": len(replies) >= 4 and
            canonical(replies[0:2]) == canonical(replies[2:4]),
        "amount_and_account_conflicts_change_nothing": len(replies) == 9 and all(
            canonical(r) == canonical({"status": "payload_mismatch", "remaining": None})
            for r in replies[4:8]),
        "other_account_can_spend_100": len(replies) == 9 and
            canonical(replies[-1]) == canonical({"status": "accepted", "remaining": 0}),
        "all_replies_match_a_serial_history": bool(reply_matches),
        "independent_tables_match_a_serial_history": bool(disk_matches),
        "replies_and_tables_match_the_same_history": bool(consistent),
    }
    return {"passed": all(checks.values()), "checks": checks,
            "matched_serial_orders": [o["serial_order"] for o in consistent],
            "expected_alternatives": outcomes}
