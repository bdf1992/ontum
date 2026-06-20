"""tests/test_barrier.py — the §10 teeth of the gate/fence primitive.

The test that matters (§10): can two locally-fine things refuse to fit, and
does the check notice? Here the command_guard links are each locally fine, yet
against the trunk-mutation territory's full route taxonomy they DO NOT close —
the fence is torn at the seam, and validate_fence says so. Each law (actor-blind,
not-opaque, barbed, closed) is proven to BITE, and the kill-tests show the
checks are not vacuous: neutralize a law and the corresponding assertion would
flip.
"""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fence import barrier  # noqa: E402


def good_link(**over):
    link = {
        "id": "ok",
        "predicate": {"kind": "command-regex", "over": "command",
                      "pattern": r"\bgit\s+push\b"},
        "on_match": "block",
        "reason": "a cold reader learns what to do instead here",
        "witness": ".ai-native/log/tool-use.jsonl",
    }
    link.update(over)
    return link


class BarrierLinkLaws(unittest.TestCase):
    def test_a_valid_link_passes(self):
        self.assertEqual(barrier.validate_link(good_link()), [])

    def test_decide_is_deterministic(self):
        act = {"command": "git push origin main"}
        link = good_link()
        self.assertEqual(barrier.decide(link, act), barrier.decide(link, act))
        self.assertFalse(barrier.decide(link, act)["allow"])  # it bites
        self.assertTrue(barrier.decide(link, {"command": "git status"})["allow"])

    def test_actor_blind_refuses_an_authorization_kind(self):
        # a "gateway-shaped" link that decides on who-may is REFUSED: it reads
        # outside the act's observable form. This is the discriminator.
        gateway = good_link(predicate={"kind": "actor-authorization",
                                       "role": "merge-node"})
        problems = barrier.validate_link(gateway)
        self.assertTrue(any("observable form" in p for p in problems),
                        f"an actor-authorization link was not refused: {problems}")

    def test_actor_blind_refuses_smuggled_actor_keys(self):
        # an ALLOWED kind that names an authorization concept in its predicate
        # is still refused — actor-reads cannot be smuggled in.
        sneaky = good_link(predicate={"kind": "command-regex", "over": "command",
                                      "pattern": r"x", "authorized": "bdo"})
        problems = barrier.validate_link(sneaky)
        self.assertTrue(any("smuggles actor-authorization" in p for p in problems),
                        f"a smuggled actor key was not refused: {problems}")

    def test_not_opaque_refuses_a_reasonless_link(self):
        problems = barrier.validate_link(good_link(reason="  "))
        self.assertTrue(any("opaque" in p for p in problems),
                        f"a reasonless link was not refused: {problems}")

    def test_barbed_refuses_an_unwitnessed_block(self):
        problems = barrier.validate_link(good_link(witness=""))
        self.assertTrue(any("unbarbed" in p for p in problems),
                        f"an unwitnessed block was not refused: {problems}")

    def test_the_validator_is_not_vacuous(self):
        # the kill-test for validate_link itself: a fully broken link trips
        # multiple laws at once. If validate_link ever returned [] here, the
        # teeth would be fake.
        broken = {"id": "x", "predicate": {"kind": "actor-authorization"},
                  "on_match": "maybe", "reason": "", "witness": ""}
        self.assertGreaterEqual(len(barrier.validate_link(broken)), 3)


class FenceClosure(unittest.TestCase):
    def test_our_real_git_fence_is_torn_at_the_seam(self):
        # command_guard reads the quote-stripped command, so the shelled git
        # push (its git lives in the stripped-out quotes) walks straight
        # through. The fence is open at the seam — the finding, made a test.
        torn = barrier.command_guard_fence()
        self.assertFalse(barrier.is_closed(torn))
        gaps = barrier.validate_fence(torn)
        self.assertTrue(any("shelled-git-push" in g and "seam" in g for g in gaps),
                        f"the seam tear was not detected: {gaps}")

    def test_command_guard_still_bites_the_front_and_top(self):
        # the seam tear is a real gap, not a vacuous always-fail: the front and
        # top routes ARE covered by command_guard today.
        fence = barrier.command_guard_fence()
        front = next(r for r in barrier.TRUNK_MUTATION_ROUTES if r["class"] == "front")
        top = next(r for r in barrier.TRUNK_MUTATION_ROUTES if r["class"] == "top")
        self.assertTrue(barrier.covered(fence, front["example_breach"]))
        self.assertTrue(barrier.covered(fence, top["example_breach"]))

    def test_sealing_the_seam_closes_the_fence(self):
        # adding one link that reads the RAW command seals the seam — the
        # perimeter loops closed. This is the fix the finding points at.
        sealed = barrier.closed_trunk_fence()
        self.assertEqual(barrier.validate_fence(sealed), [],
                         f"the sealed fence should be closed: "
                         f"{barrier.validate_fence(sealed)}")
        self.assertTrue(barrier.is_closed(sealed))

    def test_closure_requires_enumerating_seam_and_top(self):
        # a fence that only enumerates the front — never looked for the ways
        # around — is refused even if that one route is covered. Meshed/tall:
        # an un-enumerated class is an unguessed gap.
        front_only = {
            "territory": "trunk-mutation",
            "routes": [r for r in barrier.TRUNK_MUTATION_ROUTES
                       if r["class"] == "front"],
            "links": [dict(barrier.SEAM_LINK)],  # covers the one front route
        }
        problems = barrier.validate_fence(front_only)
        self.assertTrue(any("no 'seam'" in p for p in problems), problems)
        self.assertTrue(any("no 'top'" in p for p in problems), problems)

    def test_an_unbarbed_link_taints_the_whole_fence(self):
        # a fence is only as physical as its links: one opaque/unbarbed link
        # fails the whole perimeter (the link laws compose into the fence law).
        fence = barrier.closed_trunk_fence()
        fence["links"][0]["witness"] = ""
        self.assertFalse(barrier.is_closed(fence))


if __name__ == "__main__":
    unittest.main()
