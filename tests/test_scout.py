"""§10 for the Scout generator (done-line 0148): the teeth bite at MOVE
granularity — the move-granular fix for review finding #1.

explore.py's grounding was vacuous: its arc-doc antecedent always resolved.
Scout's first cut closed the literal vacuousness (cold epics refused) but
still grounded a warm epic on "the epic id appears in the log" — a record the
loop itself writes (arc_confirmed / workspace_claimed). The fix: ground only
on priors that name the move's SUBJECT in real work or an authored bar, and
drop the loop-written admissions ledger entirely. The discriminating test: a
*confirmed* epic whose next move targets an un-worked piece is now REFUSED.
"""

import unittest
from pathlib import Path

from loop import scout, scout_cta
from loop.reconcile import DEFAULT_ROOT

ROOT = Path(DEFAULT_ROOT)
REPO = ROOT.resolve().parent
# a foundational epic with real piece work on the record (stable across the
# branch and main); GROUNDS under the move-granular rule.
WORKED = "epic.substrate"
# a confirmed/warm epic whose pieces are not yet worked; REFUSES under the
# move-granular rule even though it is touched (the residual this closes).
WARM_UNWORKED = "epic.strategy"


class TestScout(unittest.TestCase):
    def test_grounds_a_live_purpose_with_real_work(self):
        out = scout.scout(ROOT, WORKED)
        self.assertEqual(out.get("status"), "conjecture", out)
        self.assertEqual(scout_cta.validate(REPO, out), [], out)
        self.assertTrue(out["priors_consulted"])
        for ev in out["priors_consulted"]:
            # non-self-referential: never the epic file; and never the
            # loop-written governance admissions.
            self.assertNotIn("/epics/", ev["file"], ev)
            self.assertNotIn("admissions", ev["file"], ev)
        self.assertFalse(out["minted"])
        self.assertFalse(out["truth_claim"])

    def test_warm_confirmed_epic_without_piece_work_is_refused(self):
        # THE discriminator: epic.strategy is confirmed and claimed (the loop
        # wrote arc_confirmed/workspace_claimed for it), but its next move
        # targets a piece with no real work — so Scout REFUSES. The teeth bite
        # at move granularity, not merely epic-touched-vs-untouched.
        out = scout.scout(ROOT, WARM_UNWORKED)
        self.assertEqual(out.get("status"), "refused", out)

    def test_grounding_never_uses_loop_written_admissions(self):
        # substantive_priors must never cite the admissions ledger — that is
        # where the self-fulfilling arc_confirmed/workspace_claimed records live.
        priors = scout.substantive_priors(REPO, WORKED)
        self.assertTrue(priors, "expected real-work priors for a worked arc")
        for ev in priors:
            self.assertNotIn("admissions", ev["file"], ev)
            self.assertNotIn("/epics/", ev["file"], ev)

    def test_ghost_subject_has_no_substantive_prior(self):
        self.assertEqual(scout.substantive_priors(REPO, "atom.ghost-zzzzz.v0"), [])

    def test_nonexistent_purpose_is_refused(self):
        out = scout.scout(ROOT, "epic.ghost-zzzzz")
        self.assertEqual(out.get("status"), "refused", out)

    def test_fabricated_cta_cannot_validate(self):
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
