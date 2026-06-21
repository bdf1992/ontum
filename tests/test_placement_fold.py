"""Tests for the placement fold (done-line 0159): a worker belongs in its own
worktree, not the viewport (the shared trunk primary checkout).

(Filed as `test_placement_fold` because `test_placement.py` is already taken by
the unrelated `.claude/hooks/placement.py` cross-ref id-collision fold — a name
collision noted in the session report; overwriting that file would drop its
tests.)

The §10 teeth are NON-VACUOUS by construction: the SAME worker (same claim, same
branch) must be REFUSED when its cwd is the viewport and PASS when its cwd is its
correct placement path. A `placement_refusal` that always passes fails
`test_the_bite` (the trespass would slip through); one that always refuses fails
the same test (a worker in its own tree must not be refused) and
`test_no_claim_is_left_alone`. The two locally-fine facts — "this checkout is the
trunk" and "I am a worker serving claim W" — must refuse to fit.
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import placement  # noqa: E402


class TestPlacementPath(unittest.TestCase):
    """The derived placement path — pure, deterministic."""

    def test_placement_path(self):
        self.assertEqual(
            placement.placement_path("claude/foo-bar"), "../ontum-wt/foo-bar"
        )

    def test_placement_path_no_branch(self):
        self.assertIsNone(placement.placement_path(""))
        self.assertIsNone(placement.placement_path(None))

    def test_branch_slug(self):
        self.assertEqual(placement.branch_slug("claude/a/b"), "b")
        self.assertEqual(placement.branch_slug("x"), "x")
        self.assertEqual(placement.branch_slug(""), "")


class TestTheBite(unittest.TestCase):
    """The §10 bite, proven non-vacuous: ONE worker, two cwds, two verdicts."""

    BRANCH = "claude/placement-gateway"
    CLAIM = "atom.placement-fold.v0"
    VIEWPORT = "/repo/ontum"
    WT_ROOT = "/repo/ontum-wt"

    def test_the_bite(self):
        # The same worker (same claim, same branch) is refused in the viewport
        # and passes in its own placement — both sides, one test, the teeth.
        placed = placement.placement_path(self.BRANCH, self.WT_ROOT)

        refused = placement.placement_refusal(
            self.VIEWPORT, self.BRANCH, self.CLAIM, self.VIEWPORT, self.WT_ROOT
        )
        self.assertIsInstance(refused, str)
        self.assertTrue(refused)
        # the refusal names the placement it should have instead
        self.assertIn(placed, refused)

        passed = placement.placement_refusal(
            placed, self.BRANCH, self.CLAIM, self.VIEWPORT, self.WT_ROOT
        )
        self.assertIsNone(passed)

    def test_no_claim_is_left_alone(self):
        # A reader / the viewport's own owner session is not a worker: opt-in.
        r = placement.placement_refusal(
            self.VIEWPORT, self.BRANCH, None, self.VIEWPORT, self.WT_ROOT
        )
        self.assertIsNone(r)

    def test_wrong_tree_is_refused(self):
        # A worker in neither the viewport nor its own placement is in the wrong tree.
        r = placement.placement_refusal(
            "/repo/ontum-wt/some-other", self.BRANCH, self.CLAIM,
            self.VIEWPORT, self.WT_ROOT,
        )
        self.assertIsInstance(r, str)
        self.assertTrue(r)


class TestPlacementStatus(unittest.TestCase):
    """The census over the session registry: three sessions, three verdicts."""

    def test_classifies_three(self):
        viewport = "/repo/ontum"
        wt_root = "/repo/ontum-wt"
        registry = {
            "s-view": {"cwd": "/repo/ontum"},
            "s-placed": {"cwd": "/repo/ontum-wt/x"},
            "s-else": {"cwd": "/tmp/random"},
        }
        rows = placement.placement_status(registry, viewport, wt_root)
        by_session = {r["session"]: r["verdict"] for r in rows}
        self.assertEqual(by_session["s-view"], "in-viewport")
        self.assertEqual(by_session["s-placed"], "placed")
        self.assertEqual(by_session["s-else"], "elsewhere")


if __name__ == "__main__":
    unittest.main()
