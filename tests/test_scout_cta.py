"""§10 for the ScoutCTA contract (done-line 0141): the teeth that keep
pre-evidence motion lawful. The fixture is a valid conjecture; three
distinct refusals prove the contract cannot be lied to.

If every input passed, the contract would not be doing its job (§10): so a
fabricated/constant CTA, an ungrounded prior, and a missing expiry must each
be refused — and the hand-authored fixture must pass.
"""

import copy
import unittest
from pathlib import Path

from loop import scout_cta

REPO = scout_cta.REPO_ROOT


class TestScoutCTAContract(unittest.TestCase):
    def test_fixture_is_a_lawful_conjecture(self):
        # the hand-authored fixture: schema-valid, grounded, expiring, marked.
        problems = scout_cta.validate(REPO, scout_cta.FIXTURE)
        self.assertEqual(problems, [], problems)
        self.assertTrue(scout_cta.is_grounded(REPO, scout_cta.FIXTURE))
        # it carries its conjecture marks in its own bytes — never truth.
        self.assertEqual(scout_cta.FIXTURE["status"], "conjecture")
        self.assertFalse(scout_cta.FIXTURE["minted"])
        self.assertFalse(scout_cta.FIXTURE["truth_claim"])
        self.assertTrue(scout_cta.FIXTURE["review_required"])

    def test_ungrounded_prior_is_refused(self):
        # the ghost refusal: a prior that resolves to nothing on disk.
        bad = copy.deepcopy(scout_cta.FIXTURE)
        bad["priors_consulted"][0] = {"file": "nowhere/nope.md",
                                      "contains": "this resolves nowhere"}
        problems = scout_cta.validate(REPO, bad)
        self.assertTrue(any("ghost" in p for p in problems), problems)
        self.assertFalse(scout_cta.is_grounded(REPO, bad))

    def test_missing_expiry_is_refused(self):
        # a conjecture without decay is a ghost obligation.
        for value in ("", "   ", None):
            bad = copy.deepcopy(scout_cta.FIXTURE)
            bad["expiry"] = value
            problems = scout_cta.validate(REPO, bad)
            self.assertTrue(any("ghost obligation" in p for p in problems),
                            (value, problems))

    def test_fabricated_constant_cta_cannot_pass(self):
        # a constant CTA with hand-waved priors resolves to nothing -> refused.
        # the contract cannot mint a grounded conjecture out of fabrication.
        constant = {
            "status": "conjecture", "lobe": "scout",
            "purpose": "x", "goal": "x", "horizon": "x",
            "priors_consulted": [{"file": "made-up.md", "contains": "trust me"}],
            "uncertainty_held": "x", "why_this_move_now": "x",
            "cta": "ship the thing", "cost": "x", "risk": "x",
            "reversibility": "x", "review_required": True,
            "expiry": "next session", "truth_claim": False, "minted": False,
        }
        self.assertFalse(scout_cta.is_grounded(REPO, constant))

    def test_truth_claim_or_mint_is_refused(self):
        # the marks are mandatory: a ScoutCTA that claims truth or mints is
        # refused even if everything else grounds.
        for field in ("minted", "truth_claim"):
            bad = copy.deepcopy(scout_cta.FIXTURE)
            bad[field] = True
            problems = scout_cta.validate(REPO, bad)
            self.assertTrue(any(field in p for p in problems), (field, problems))

    def test_missing_field_is_refused(self):
        bad = copy.deepcopy(scout_cta.FIXTURE)
        del bad["cta"]
        problems = scout_cta.validate(REPO, bad)
        self.assertTrue(any("missing required field: cta" in p for p in problems),
                        problems)


if __name__ == "__main__":
    unittest.main()
