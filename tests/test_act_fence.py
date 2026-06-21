#!/usr/bin/env python3
"""§10 teeth for the act-fence (done-line 0174).

The check that matters: the tier reads the *authorization context*, not the
verb. These tests are written to FAIL a vacuous classifier — a constant
`forgiveness` fails the forbidden/permission cases; a constant `forbidden`
fails the landing-under-arc and fence-lift cases; a verb-only classifier fails
the landing hinge (same verb, two tiers). And the consequence-gate must run
first: an unobservable act halts before any tier is read.
"""

import unittest

from loop import act_fence
from loop.act_fence import (
    FORGIVENESS, PERMISSION, FORBIDDEN, classify, evaluate, read_fence,
)


def observed(**over):
    """A fully-observable act (observe.gate clears) the tests then vary. The
    attribution path names the actor, so the consequence-gate passes and the
    test isolates the *tier* logic."""
    act = {
        "actor": "session",
        "action": "draft on a branch",
        "scope": "a branch",
        "family": "draft",
        "blast_radius": "branch",
        "reversible": True,
        "expected_receipt": "the commit object",
        "attribution_path": "commit -> branch ref -> session",
        "rollback_path": "git restore",
    }
    act.update(over)
    return act


def a_fence(forgivable=("draft", "read-fold"), id="adm.testfence"):
    return {"id": id, "type": act_fence.FENCE_TYPE, "by": "bdo",
            "forgivable": list(forgivable)}


class LandingHingeReadsContext(unittest.TestCase):
    """The load-bearing tooth: the same land-main verb is forgiveness under a
    confirmed arc and permission without one. A verb-only classifier cannot
    pass both halves."""

    def _land(self, arc_confirmed):
        return observed(action="pr.py land", family="land-main",
                        blast_radius="main", reversible=True,
                        arc_confirmed=arc_confirmed,
                        attribution_path="merge receipt -> confirm-arc -> bdo / merge-node",
                        actor="merge-node")

    def test_landing_under_confirmed_arc_is_forgiveness(self):
        tier, _ = classify(self._land(arc_confirmed=True))
        self.assertEqual(tier, FORGIVENESS)

    def test_landing_without_confirmed_arc_is_permission(self):
        tier, _ = classify(self._land(arc_confirmed=False))
        self.assertEqual(tier, PERMISSION)

    def test_the_two_differ_only_by_authorization(self):
        # identical but for arc_confirmed -> different tiers. proves the tier
        # reads the authorization context, not the verb.
        self.assertNotEqual(
            classify(self._land(True))[0], classify(self._land(False))[0])


class OwnerGesturesAreForbidden(unittest.TestCase):
    """A fence can never self-admit bdo's own authorization (D-4)."""

    def test_confirm_arc_forbidden(self):
        self.assertEqual(classify(observed(family="confirm-arc"))[0], FORBIDDEN)

    def test_admit_real_forbidden(self):
        self.assertEqual(classify(observed(family="admit-real"))[0], FORBIDDEN)

    def test_forbidden_even_with_a_fence(self):
        # a drawn fence does not lift an owner gesture to admit.
        d = evaluate(a_fence(forgivable=("confirm-arc",)),
                     observed(family="confirm-arc"))
        self.assertEqual(d["verdict"], "deny")


class WideActCannotBuyForgiveness(unittest.TestCase):
    """Declaring an outward/irreversible act `reversible` does not make it
    forgiveness — blast radius is read before reversibility for the wide bands."""

    def test_outward_plus_reversible_is_forbidden(self):
        tier, _ = classify(observed(family="outward-as-owner",
                                    blast_radius="outward", reversible=True))
        self.assertEqual(tier, FORBIDDEN)

    def test_destructive_plus_reversible_is_forbidden(self):
        tier, _ = classify(observed(family="destructive", reversible=True))
        self.assertEqual(tier, FORBIDDEN)

    def test_reversible_but_main_scoped_is_only_permission(self):
        # a reversible non-landing act on main is permission, not forgiveness.
        tier, _ = classify(observed(family="set-dial", blast_radius="main",
                                    reversible=True))
        self.assertEqual(tier, PERMISSION)


class ReversibilityIsLoadBearing(unittest.TestCase):
    """The reversibility leg of the 'reversibility x blast-radius' cut must
    bite. The independent review of PR #450 caught it as a soft tooth: a mutant
    classify() with the `reversible` checks deleted passed all 18 original
    tests. Per section 10, the axis the bar names must be testable — these flip
    `reversible` and require the tier to move, so the mutant now fails."""

    def test_contained_but_irreversible_is_permission(self):
        # a contained act with no rollback path is PERMISSION, not forgiveness —
        # exercises the `and reversible` on the contained branch.
        tier, _ = classify(observed(family="draft", blast_radius="branch",
                                    reversible=False))
        self.assertEqual(tier, PERMISSION)

    def test_landing_confirmed_but_irreversible_is_permission(self):
        # a confirmed-arc land with no rollback path is PERMISSION — the arc
        # alone is not enough; exercises the `and reversible` on land-main.
        tier, reason = classify(observed(family="land-main", blast_radius="main",
                                         arc_confirmed=True, reversible=False))
        self.assertEqual(tier, PERMISSION)
        # and the reason must name reversibility, not lie about a missing arc.
        self.assertNotIn("without a confirmed arc", reason)


class FenceAndDefaultSafe(unittest.TestCase):
    """Default-safe: a forgiveness act escalates with no fence and self-admits
    only under one — the disposer's inert-until-stamped shape."""

    def test_forgiveness_escalates_without_a_fence(self):
        d = evaluate(None, observed(family="draft"))
        self.assertEqual(d["tier"], FORGIVENESS)
        self.assertEqual(d["verdict"], "escalate")

    def test_fence_lifts_forgiveness_to_admit(self):
        d = evaluate(a_fence(forgivable=("draft",)), observed(family="draft"))
        self.assertEqual(d["verdict"], "admit")
        self.assertEqual(d["authorized_by"], "adm.testfence")

    def test_fence_does_not_authorize_an_unnamed_scope(self):
        # a fence naming only read-fold does not admit a draft act.
        d = evaluate(a_fence(forgivable=("read-fold",)), observed(family="draft"))
        self.assertEqual(d["verdict"], "escalate")


class ObserveGatesFirst(unittest.TestCase):
    """The consequence-gate runs before any tier — an unobservable act halts."""

    def test_missing_attribution_halts_before_tier(self):
        act = observed(family="draft")
        del act["attribution_path"]
        d = evaluate(a_fence(forgivable=("draft",)), act)
        self.assertEqual(d["verdict"], "halt")
        self.assertIsNone(d["tier"])  # never even classified

    def test_attribution_not_terminating_at_actor_halts(self):
        act = observed(family="draft",
                       attribution_path="commit -> branch ref -> someone-else")
        d = evaluate(None, act)
        self.assertEqual(d["verdict"], "halt")


class ReadFenceLatestWins(unittest.TestCase):
    """The fence is a runtime fold (I-8): latest well-formed wins, malformed
    ignored, none -> inert."""

    def test_latest_wins(self):
        adms = [a_fence(("draft",), id="adm.1"),
                a_fence(("draft", "read-fold"), id="adm.2")]
        self.assertEqual(read_fence(adms)["id"], "adm.2")

    def test_malformed_ignored(self):
        adms = [a_fence(("draft",), id="adm.1"),
                {"type": act_fence.FENCE_TYPE, "by": "bdo", "forgivable": []}]
        self.assertEqual(read_fence(adms)["id"], "adm.1")  # the empty one ignored

    def test_none_when_undrawn(self):
        self.assertIsNone(read_fence([{"type": "something_else"}]))


class ClassifierIsNonVacuous(unittest.TestCase):
    """Belt-and-braces: all three tiers are reachable, so no constant classifier
    passes the suite."""

    def test_all_three_tiers_reachable(self):
        tiers = {
            classify(observed(family="draft"))[0],
            classify(observed(family="land-main", blast_radius="main",
                              arc_confirmed=False))[0],
            classify(observed(family="confirm-arc"))[0],
        }
        self.assertEqual(tiers, {FORGIVENESS, PERMISSION, FORBIDDEN})


if __name__ == "__main__":
    unittest.main()
