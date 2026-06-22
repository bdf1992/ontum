"""The whole-tree forest fold's decoration classifier (loop/forest.py).

A generated, auto-managed surface over the whole forest is only as honest as the
rule that decides each work-item's status. These tests pin that rule with teeth
(§10): the two pure classifiers must DISTINGUISH the shapes — a constant or
fabricated classifier (everything 'merged', everything 'landed') is CAUGHT — and
the two load-bearing bites must hold:

  - a STRANDED worktree (uncommitted work) can never be flagged `merged`, even
    when its branch landed (the garden merged-but-dirty case: the work wins);
  - a PARKED atom can never read `merged`/landed (a gate's honest no is never
    smoothed into 'it landed').

It also checks the whole-model composition (`build_forest`) carries the bites
through to the surface, and that the fold is read-only (rendering writes nothing).
"""

import unittest

from loop import forest


class GitNodeStatus(unittest.TestCase):
    def test_merged_and_clean_is_merged(self):
        # clean tree, branch landed, no open PR → merged.
        self.assertEqual(
            forest.git_node_status(0, False, True, True), "merged")

    def test_merged_but_dirty_is_stranded_not_merged(self):
        # THE §10 BITE: branch landed AND work unsaved — the work wins; a
        # classifier that called this `merged` would lose the unsaved work.
        self.assertEqual(
            forest.git_node_status(3, False, True, True), "stranded")

    def test_open_pr_with_dirty_worktree_is_live(self):
        self.assertEqual(
            forest.git_node_status(2, True, False, True), "live-worktree")

    def test_open_pr_clean_is_in_review(self):
        self.assertEqual(
            forest.git_node_status(0, True, False, True), "in-review")

    def test_open_pr_outranks_merged(self):
        # a reused branch with both PRs is still in flight — never merged.
        self.assertIn(
            forest.git_node_status(0, True, True, True),
            ("in-review", "live-worktree"))

    def test_committed_no_pr_is_stranded(self):
        self.assertEqual(
            forest.git_node_status(0, False, False, False), "stranded")

    def test_loose_branch_open_pr_is_in_review(self):
        # a loose branch has no tree to be dirty → in-review, never live-worktree.
        self.assertEqual(
            forest.git_node_status(0, True, False, False), "in-review")

    def test_merged_is_the_only_landed_shape(self):
        # exhaustive over the input cube: `merged` iff (clean AND merged-PR AND
        # no open PR). A constant `merged` classifier fails every other row.
        merged_inputs = [
            (u, o, m, w)
            for u in (0, 2)
            for o in (True, False)
            for m in (True, False)
            for w in (True, False)
            if forest.git_node_status(u, o, m, w) == "merged"
        ]
        self.assertEqual(merged_inputs, [(0, False, True, True),
                                         (0, False, True, False)])


class AtomNodeStatus(unittest.TestCase):
    def test_parked_atom_is_never_merged(self):
        # THE §10 BITE: a gate refused it — `parked-atom`, not `merged`, even if
        # some signal claims it is on main.
        self.assertEqual(
            forest.atom_node_status(("parked", None), False), "parked-atom")
        self.assertEqual(
            forest.atom_node_status(("parked", None), True), "parked-atom")

    def test_on_main_is_merged(self):
        self.assertEqual(forest.atom_node_status(("await", "n"), True), "merged")

    def test_settled_is_merged(self):
        self.assertEqual(forest.atom_node_status(None, False), "merged")

    def test_awaiting_is_in_review(self):
        self.assertEqual(
            forest.atom_node_status(("await", "value-gate.claude.v1"), False),
            "in-review")

    def test_in_flight_is_in_review(self):
        self.assertEqual(forest.atom_node_status(("judge", "x"), False), "in-review")

    def test_classifier_is_not_constant(self):
        # a fabricated 'always merged' classifier would collapse these; the real
        # one must spread across the vocabulary.
        seen = {
            forest.atom_node_status(("parked", None), False),
            forest.atom_node_status(None, False),
            forest.atom_node_status(("await", "n"), False),
        }
        self.assertEqual(seen, {"parked-atom", "merged", "in-review"})


class BuildForestComposition(unittest.TestCase):
    """The whole-model fold carries both bites through to the surface."""

    def _model(self):
        worktrees = [
            ("/repo", "main", True, 4),                       # the viewport (leaf)
            ("/wt/landed-dirty", "claude/x", False, 3),       # merged PR + dirty
            ("/wt/clean-landed", "claude/y", False, 0),       # merged PR + clean
            ("/wt/active", "claude/z", False, 1),             # open PR + dirty
        ]
        loose = ["claude/stale"]
        pr_states = {
            "claude/x": {"MERGED"},
            "claude/y": {"MERGED"},
            "claude/z": {"OPEN"},
            "claude/stale": set(),
        }
        atom_rows = [
            ("atom.parked.v0", "sha256:a", "value_accepted", ("parked", None), False),
            ("atom.landed.v0", "sha256:b", "value_confirmed", None, True),
            ("atom.flying.v0", "sha256:c", "created", ("await", "value-gate"), False),
        ]
        return forest.build_forest(worktrees, loose, pr_states, atom_rows, True)

    def test_dirty_landed_worktree_is_stranded_in_model(self):
        d = self._model()
        landed_dirty = next(w for w in d["worktrees"] if w["slug"] == "landed-dirty")
        self.assertEqual(landed_dirty["status"], "stranded")
        clean_landed = next(w for w in d["worktrees"] if w["slug"] == "clean-landed")
        self.assertEqual(clean_landed["status"], "merged")

    def test_parked_atom_is_parked_in_model(self):
        d = self._model()
        parked = next(a for a in d["atoms"] if a["atom"] == "atom.parked.v0")
        self.assertEqual(parked["status"], "parked-atom")
        landed = next(a for a in d["atoms"] if a["atom"] == "atom.landed.v0")
        self.assertEqual(landed["status"], "merged")

    def test_counts_sum_to_node_total(self):
        d = self._model()
        total = sum(d["totals"].values())
        self.assertEqual(sum(d["counts"].values()), total)

    def test_render_is_pure_string(self):
        # read-only: rendering returns text and touches no file.
        out = forest.render(self._model())
        self.assertIn("parked-atom", out)
        self.assertIn("stranded", out)
        self.assertIsInstance(out, str)

    def test_open_count_catches_the_pressure(self):
        d = self._model()
        # one parked atom + the stranded landed-dirty worktree + the stale loose
        # branch (no PR) → at least the parked atom and a stranded node.
        self.assertGreaterEqual(forest.open_count(d), 2)


if __name__ == "__main__":
    unittest.main()
