"""Independent pure state machine; no SQLite, submitted code, or reference import."""
from copy import deepcopy
from itertools import permutations


class Model:
    def __init__(self):
        self.accounts = {'A': 100, 'B': 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, request):
        k, a, n = (request[x] for x in ('key', 'account', 'amount'))
        if k in self.decisions:
            old = self.decisions[k]
            if (a, n) != (old[1], old[2]):
                return {'status': 'payload_mismatch', 'remaining': None}
            return {'status': old[3], 'remaining': old[4]}
        accepted = self.accounts[a] >= n
        if accepted:
            self.accounts[a] -= n
            self.ledger[k] = [k, a, n]
        status = 'accepted' if accepted else 'rejected'
        self.decisions[k] = [k, a, n, status, self.accounts[a]]
        return {'status': status, 'remaining': self.accounts[a]}

    def snapshot(self):
        return {'accounts': sorted([[a, n] for a, n in self.accounts.items()]),
                'decisions': sorted(self.decisions.values()),
                'ledger': sorted(self.ledger.values())}


def serial_outcomes(model, requests):
    """Enumerate both legal serial orders; never choose a winner from a reply."""
    outcomes = []
    for order in permutations(range(len(requests))):
        candidate = deepcopy(model)
        replies = [None] * len(requests)
        for index in order:
            replies[index] = candidate.apply(requests[index])
        outcomes.append((candidate, replies))
    return outcomes
