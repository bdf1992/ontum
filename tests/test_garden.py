"""The worktree gardener's safety classifier (git.py garden_verdict).

An auto-pruner that runs on every SessionStart is only as safe as the rule
that decides what it removes. These tests pin that rule: it prunes exactly one
shape — a clean worktree whose branch has merged — and surfaces every other
shape rather than destroy it. The §10 bite is the merged-but-dirty case: the
branch is done *and* the tree holds unsaved work, two locally-fine facts that
refuse to fit, and the gardener must keep the work, not the tidiness.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "git_pen", ROOT / ".claude" / "skills" / "branch-ritual" / "git.py")
gitpen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gitpen)
verdict = gitpen.garden_verdict


class GardenVerdict(unittest.TestCase):
    def test_merged_and_clean_prunes(self):
        self.assertEqual(verdict(0, False, True)[0], "prune")

    def test_merged_but_dirty_surfaces_not_prunes(self):
        # the §10 case: branch landed, work unsaved — the work wins.
        v, reason = verdict(3, False, True)
        self.assertEqual(v, "surface")
        self.assertIn("uncommitted", reason)

    def test_open_pr_is_kept_even_if_dirty(self):
        # an active workbench mid-task is not a chore.
        self.assertEqual(verdict(5, True, False)[0], "keep")

    def test_open_pr_outranks_merged(self):
        # a reused branch with both PRs is still in flight — never pruned.
        self.assertEqual(verdict(0, True, True)[0], "keep")

    def test_dirty_no_pr_surfaces(self):
        self.assertEqual(verdict(2, False, False)[0], "surface")

    def test_clean_committed_no_pr_surfaces(self):
        # committed but never PR'd — stranded, never silently pruned.
        v, reason = verdict(0, False, False)
        self.assertEqual(v, "surface")
        self.assertIn("no PR", reason)

    def test_only_merged_clean_is_ever_pruned(self):
        # exhaustive over the boolean cube: prune iff (clean, no open, merged).
        prune_inputs = [
            (u, o, m)
            for u in (0, 1)
            for o in (True, False)
            for m in (True, False)
            if verdict(u, o, m)[0] == "prune"
        ]
        self.assertEqual(prune_inputs, [(0, False, True)])


if __name__ == "__main__":
    unittest.main()
