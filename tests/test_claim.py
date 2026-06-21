"""§10 for the Claim part (done-line 0158): Claim bounds a valid conjecture
and REFUSES an unlawful one — and never proves.

The discriminating test: Claim runs the ScoutCTA contract first, so an
invalid/ungrounded conjecture cannot be bounded (you cannot give an edge to
something that was never a lawful conjecture). Every claim it produces is
bounded (exit_condition + expiry) and carries no truth.
"""

import copy
import unittest
from pathlib import Path

from loop import claim, scout_cta
from loop.reconcile import DEFAULT_ROOT

REPO = Path(DEFAULT_ROOT).resolve().parent
VALID = scout_cta.FIXTURE  # a real, grounded ScoutCTA


class TestClaim(unittest.TestCase):
    def test_claims_a_valid_conjecture(self):
        out = claim.claim(REPO, VALID)
        self.assertEqual(out.get("status"), "claimed_frontier", out)
        self.assertIn(out["claim_type"], claim.CLAIM_TYPES)
        # bounded: a non-empty exit_condition AND expiry
        self.assertTrue(out["exit_condition"].strip())
        self.assertTrue(str(out["expiry"]).strip())

    def test_claim_never_proves(self):
        out = claim.claim(REPO, VALID)
        self.assertFalse(out["minted"])
        self.assertFalse(out["truth_claim"])
        self.assertEqual(out["provenance"], "proposed")

    def test_refuses_invalid_conjecture_missing_expiry(self):
        bad = copy.deepcopy(VALID)
        bad["expiry"] = ""
        out = claim.claim(REPO, bad)
        self.assertEqual(out.get("status"), "refused", out)

    def test_refuses_ungrounded_conjecture(self):
        bad = copy.deepcopy(VALID)
        bad["priors_consulted"] = [{"file": "nowhere/nope.md", "contains": "ghost"}]
        out = claim.claim(REPO, bad)
        self.assertEqual(out.get("status"), "refused", out)

    def test_claim_type_is_derived_not_constant(self):
        # different moves -> different claim types (the derivation reads the CTA)
        watch_cta = copy.deepcopy(VALID)
        watch_cta["why_this_move_now"] = "[open-question] a fork to monitor"
        branch_cta = copy.deepcopy(VALID)
        branch_cta["why_this_move_now"] = "[advance-parked] resume the atom"
        self.assertEqual(claim.claim(REPO, watch_cta)["claim_type"], "watch")
        self.assertEqual(claim.claim(REPO, branch_cta)["claim_type"], "branch")


if __name__ == "__main__":
    unittest.main()
