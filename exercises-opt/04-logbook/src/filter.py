"""
Augmented-Lagrangian filter for the ADMM-Filter algorithm
(see RASC-MeetingNotes.tex, section 2.1).

A filter F is a list of (eta, omega) pairs - primal and dual infeasibility
measures - where no entry dominates another.  A trial point (eta, omega) is
acceptable iff for every stored entry (eta_l, omega_l):

    eta <= beta * eta_l    OR    omega <= omega_l - gamma * eta

with constants 0 < beta, gamma < 1.
"""

import math


class Filter:
    """Non-dominated filter of (eta, omega) pairs."""

    def __init__(self, beta=0.99, gamma=1e-5):
        # Acceptance constants (notes use beta < 1, gamma < 1).
        if not (0.0 < beta < 1.0):
            raise ValueError(f"beta must be in (0, 1), got {beta}")
        if not (0.0 < gamma < 1.0):
            raise ValueError(f"gamma must be in (0, 1), got {gamma}")
        self.beta = beta
        self.gamma = gamma
        self._entries = []   # list of (eta, omega) tuples

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def is_acceptable(self, eta, omega):
        """
        True iff (eta, omega) satisfies the filter acceptance rule against
        every stored entry.  Empty filter accepts everything.
        """
        for eta_l, omega_l in self._entries:
            if not (eta <= self.beta * eta_l or omega <= omega_l - self.gamma * eta):
                return False
        return True

    def add(self, eta, omega):
        """
        Add (eta, omega) to the filter and prune any dominated entries.

        Per the algorithm in section 2.5 ("ensures eta_l > 0"), the filter
        only stores infeasible iterates: eta <= 0 is rejected with an error
        so callers cannot accidentally pollute the filter with feasible points.
        """
        if eta <= 0.0:
            raise ValueError(
                f"Filter entries require eta > 0 (got eta={eta}); "
                "feasible iterates must not be added to the filter."
            )
        # Prune entries dominated by the new one: eta_l >= eta AND omega_l >= omega.
        self._entries = [
            (e, o) for (e, o) in self._entries
            if not (e >= eta and o >= omega)
        ]
        self._entries.append((eta, omega))

    def eta_min(self):
        """
        Smallest eta in the filter (used by the restoration switch in section 2.4).
        Returns +inf when the filter is empty so callers can compare safely.
        """
        if not self._entries:
            return math.inf
        return min(e for (e, _) in self._entries)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ---- Empty filter accepts everything --------------------------------
    F = Filter(beta=0.9, gamma=0.01)
    assert F.is_acceptable(1.0, 1.0)
    assert F.is_acceptable(0.0, 0.0)
    assert len(F) == 0
    assert F.eta_min() == math.inf

    # ---- Eta <= 0 entries raise -----------------------------------------
    try:
        F.add(0.0, 5.0)
    except ValueError:
        pass
    else:
        raise AssertionError("add(eta=0, ...) should raise ValueError")
    try:
        F.add(-1.0, 5.0)
    except ValueError:
        pass
    else:
        raise AssertionError("add(eta<0, ...) should raise ValueError")
    assert len(F) == 0

    # ---- Single entry ---------------------------------------------------
    F.add(1.0, 1.0)
    assert len(F) == 1
    assert F.eta_min() == 1.0

    # Strictly inside acceptance region (small eta AND small omega)
    assert F.is_acceptable(0.5, 0.5)
    # eta <= beta * eta_l (0.9*1.0 = 0.9): accept on the eta branch
    assert F.is_acceptable(0.85, 100.0)
    # omega <= omega_l - gamma*eta (1.0 - 0.01*2.0 = 0.98): accept on omega branch
    assert F.is_acceptable(2.0, 0.97)
    # Neither branch: reject
    assert not F.is_acceptable(2.0, 1.0)
    assert not F.is_acceptable(1.0, 1.0)   # exactly the stored point

    # ---- Dominance pruning ----------------------------------------------
    F = Filter(beta=0.99, gamma=1e-5)
    F.add(2.0, 2.0)
    F.add(1.0, 3.0)   # not dominated (lower eta), not dominating (higher omega)
    F.add(3.0, 1.0)   # not dominated, not dominating (vs the others)
    assert len(F) == 3

    # New entry that dominates (2.0, 2.0): eta=1.5 < 2.0 AND omega=1.5 < 2.0.
    # It should NOT dominate (1.0, 3.0) (higher eta) or (3.0, 1.0) (higher omega).
    F.add(1.5, 1.5)
    entries = sorted(F)
    assert (2.0, 2.0) not in entries, "dominated entry should be pruned"
    assert (1.0, 3.0) in entries
    assert (3.0, 1.0) in entries
    assert (1.5, 1.5) in entries
    assert len(F) == 3

    # ---- eta_min reflects pruning ---------------------------------------
    assert F.eta_min() == 1.0

    # ---- Constructor validation -----------------------------------------
    try:
        Filter(beta=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("beta=1.0 should be rejected")

    try:
        Filter(gamma=0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("gamma=0.0 should be rejected")

    print("filter.py: all self-tests passed")
