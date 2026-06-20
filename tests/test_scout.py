"""§10 for the Scout generator (done-line 0148): the teeth bite a *real*
move, closing review finding #1.

The discriminating test (§10): explore.py's grounding was vacuous because
its arc-doc antecedent always resolved. Scout grounds on substantive,
non-self-referential priors — so a real ghost move (an epic/subject with no
log activity) is REFUSED, and a grounded move never cites the epic file.
"""

import unittest
from pathlib import Path

from loop import scout, scout_cta
from loop.reconcile import DEFAULT_ROOT

ROOT = Path(DEFAULT_ROOT)
REPO = ROOT.resolve().parent
LIVE = "epic.strategy"  # confirmed on the log (confirm-arc + workspace claims)


class TestScout(unittest.TestCase):
    def test_live_purpose_grounds_non_self_referentially(self):
        out = scout.scout(ROOT, LIVE)
        # a grounded ScoutCTA, not a refusal
        self.assertEqual(out.get("status"), "conjecture", out)
        # it passes its own contract (schema + grounding + expiry)
        self.assertEqual(scout_cta.validate(REPO, out), [], out)
        self.assertTrue(out["priors_consulted"])
        # the FIX for finding #1: no prior is the epic file (non-self-referential)
        for ev in out["priors_consulted"]:
            self.assertNotIn("/epics/", ev["file"], ev)
        # marked conjecture, never truth
        self.assertFalse(out["minted"])
        self.assertFalse(out["truth_claim"])
        self.assertTrue(out["review_required"])

    def test_ghost_epic_subject_has_no_substantive_prior(self):
        # an epic/subject with no log activity grounds nothing — the teeth bite
        # a real move, not just a fabricated dict (the explore.py failure).
        priors = scout.substantive_priors(REPO, "epic.ghost-zzzzz", "atom.ghost-zzzzz.v0")
        self.assertEqual(priors, [], priors)

    def test_nonexistent_purpose_is_refused(self):
        out = scout.scout(ROOT, "epic.ghost-zzzzz")
        self.assertEqual(out.get("status"), "refused", out)

    def test_grounding_excludes_the_arc_doc_self_reference(self):
        # even where the epic file names the subject, that citation must not be
        # what grounds the move (that was the vacuous antecedent in finding #1).
        priors = scout.substantive_priors(REPO, LIVE, "atom.scout-fold.v0")
        for ev in priors:
            self.assertNotIn("/epics/", ev["file"], ev)

    def test_fabricated_cta_cannot_validate(self):
        # a constant ScoutCTA whose priors resolve nowhere is refused by the
        # contract Scout validates against before emitting.
        fab = {
            "status": "conjecture", "lobe": "scout",
            "purpose": "x", "goal": "x", "horizon": "x",
            "priors_consulted": [{"file": "made-up.md", "contains": "trust me"}],
            "uncertainty_held": "x", "why_this_move_now": "x",
            "cta": "ship it", "cost": "x", "risk": "x", "reversibility": "x",
            "review_required": True, "expiry": "soon",
            "truth_claim": False, "minted": False,
        }
        self.assertTrue(scout_cta.validate(REPO, fab))


if __name__ == "__main__":
    unittest.main()
