"""Branch-ritual 0.6.1: the rescue is updatable.

The §10 pair this pins: `create --recover` opens a PR from a dead
branch, and `push` must be able to update exactly that rescue — a
conflicted recovery PR that can never be rebased-and-pushed is stranded
work wearing an open PR (the PR #20 incident). A dead branch with no
open PR still refuses, as done-line 0014 demands. Lives in its own
module so the 0.6.1 fix commits without entangling a sibling session's
in-flight edits to test_pr_ritual.py in the shared tree.
"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEN_PATH = ROOT / ".claude" / "skills" / "branch-ritual" / "pr.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pen = _load("pr_pen_push_recovery", PEN_PATH)


class TestPushRecovery(unittest.TestCase):
    """The pure refusal rule, third argument: open PRs from the branch."""

    def test_dead_branch_with_open_recovery_pr_may_push(self):
        self.assertIsNone(
            pen.push_refusal("claude/surface-reflector-ui", [12], [20]))

    def test_dead_branch_without_open_pr_still_refused(self):
        reason = pen.push_refusal("claude/surface-reflector-ui", [12], [])
        self.assertIn("dead", reason)
        self.assertIn("#12", reason)

    def test_open_pr_alone_is_simply_alive(self):
        self.assertIsNone(
            pen.push_refusal("claude/quiet-hopper-ovn8x1", [], [13]))

    def test_trunk_refusal_outranks_any_open_pr(self):
        self.assertIn("firm", pen.push_refusal("main", [1], [2]))


if __name__ == "__main__":
    unittest.main()
