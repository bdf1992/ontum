"""Done-line 0122: the reconcile verb's teeth — it prepares a branch for
the merge-node but refuses to author a resolution.

The §10 test, applied to the land-chain cascade: GitHub reads the union'd
append-only logs as a conflict every time the trunk advances, so a confirmed
branch must re-merge main before it lands. `reconcile` does that *mechanical*
half in an isolated worktree — but a real (non-log) content conflict is two
locally-fine edits that refuse to fit, and the merge-node may not paper over
it. These pure-function tests pin the two refusals: wrong target, and a real
conflict that must go back to a session on the branch.
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


pen = _load("pr_pen", PEN_PATH)


class TestReconcileRefusal(unittest.TestCase):
    def test_open_main_pr_is_reconcilable(self):
        self.assertIsNone(pen.reconcile_refusal("OPEN", "main"))

    def test_a_closed_pr_has_no_branch_to_reconcile(self):
        reason = pen.reconcile_refusal("MERGED", "main")
        self.assertIsNotNone(reason)
        self.assertIn("open", reason.lower())

    def test_a_non_trunk_base_is_integrate_not_reconcile(self):
        # a piece PR onto an epic branch is governed by `integrate`; reconcile
        # exists only for the trunk cascade
        reason = pen.reconcile_refusal("OPEN", "epic.the-field")
        self.assertIsNotNone(reason)
        self.assertIn("integrate", reason)


class TestReconcileConflictRefusal(unittest.TestCase):
    def test_logs_only_merge_proceeds(self):
        # the union driver resolves the append-only logs, so nothing is left
        # in conflict — the merge is clean and reconcile pushes
        self.assertIsNone(pen.reconcile_conflict_refusal([]))
        self.assertIsNone(pen.reconcile_conflict_refusal(["", "  "]))

    def test_a_real_conflict_refuses_and_names_the_path(self):
        # two locally-fine edits to a doc that refuse to fit — the merge-node
        # surfaces it, never resolves it
        reason = pen.reconcile_conflict_refusal(["loop/CLAUDE.md"])
        self.assertIsNotNone(reason)
        self.assertIn("loop/CLAUDE.md", reason)
        self.assertIn("session", reason)

    def test_many_conflicts_are_listed_sorted(self):
        reason = pen.reconcile_conflict_refusal(["b.py", "a.py"])
        self.assertIn("a.py, b.py", reason)


if __name__ == "__main__":
    unittest.main()
