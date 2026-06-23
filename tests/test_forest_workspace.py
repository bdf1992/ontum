"""The VS Code workspace generator (loop/forest.py --workspace).

A generated, auto-managed `.code-workspace` is only as honest as the rule that
decides which worktrees become navigable roots. These tests pin that rule with
teeth (§10): the generator must DISTINGUISH the shapes — a generator that
included EVERY worktree (the viewport, the stranded debris, the merged-and-done
benches) or NONE of them is CAUGHT — and the load-bearing invariants hold:

  - the LIVE benches (status live-worktree / in-review) become roots;
  - the viewport (the primary checkout) and every stranded / merged worktree are
    EXCLUDED — the viewport is the leaf, not the lens, and a done/stranded bench
    is not a place to navigate to;
  - the base roots (the repo + sibling repos) come FIRST, deterministically;
  - the output parses as a valid VS Code workspace (`{folders: [...], ...}`).
"""

import json
import unittest

from pathlib import Path

from loop import forest


def _model():
    """A forest model spanning every status: a viewport, a live worktree, an
    in-review worktree, a stranded worktree, and a merged worktree — built
    through the real `build_forest` composition so the classifier (not a fixture)
    decides each status."""
    worktrees = [
        ("/repo", "main", True, 0),                 # the viewport (primary) → merged
        ("/wt/live", "claude/live", False, 2),       # open PR + dirty → live-worktree
        ("/wt/review", "claude/review", False, 0),   # open PR + clean → in-review
        ("/wt/stranded", "claude/stranded", False, 1),  # no PR + dirty → stranded
        ("/wt/merged", "claude/merged", False, 0),   # merged PR + clean → merged
    ]
    pr_states = {
        "claude/live": {"OPEN"},
        "claude/review": {"OPEN"},
        "claude/merged": {"MERGED"},
        "claude/stranded": set(),
    }
    return forest.build_forest(worktrees, [], pr_states, [], True)


def _roots():
    return [("ontum", Path("/repo")), ("gallery", Path("/repo/../gallery"))]


def _numbers():
    return {"claude/live": 100, "claude/review": 200}


class BaseRootsFirst(unittest.TestCase):
    def test_base_roots_lead_in_order(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        self.assertEqual(ws["folders"][0]["name"], "ontum")
        self.assertEqual(ws["folders"][1]["name"], "gallery")
        # the repo root path is the first folder — the viewport as the leaf root
        self.assertEqual(forest._fwd(Path("/repo")), ws["folders"][0]["path"])

    def test_live_roots_follow_base_roots(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        # the worktree roots only ever appear AFTER the two base roots
        first_wt = next(i for i, f in enumerate(ws["folders"])
                        if "live" in f["name"] or "review" in f["name"])
        self.assertGreaterEqual(first_wt, 2)


class LiveBenchesBecomeRoots(unittest.TestCase):
    def _paths(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        return {forest._fwd(f["path"]) for f in ws["folders"]}

    def test_live_and_in_review_are_roots(self):
        paths = self._paths()
        self.assertIn("/wt/live", paths)
        self.assertIn("/wt/review", paths)

    def test_stranded_and_merged_and_viewport_are_not_roots(self):
        # THE §10 BITE: a generator that included everything would pull the
        # stranded debris, the done bench, and the viewport itself in as roots.
        paths = self._paths()
        self.assertNotIn("/wt/stranded", paths)
        self.assertNotIn("/wt/merged", paths)
        # the viewport tree only ever appears as the `ontum` base root, never as
        # a worktree root (it is is_primary; the filter excludes it)
        wt_roots = [f for f in forest.build_workspace(_model(), _roots(), _numbers())["folders"]
                    if f["name"] not in ("ontum", "gallery")]
        self.assertTrue(all(f["path"] != "/repo" for f in wt_roots))

    def test_a_constant_include_everything_generator_is_caught(self):
        # exactly the live + in-review worktrees become roots — not all four
        # non-primary worktrees. An "include every worktree" generator would
        # yield 4 worktree roots; the real one yields 2.
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        wt_roots = len(ws["folders"]) - len(_roots())
        self.assertEqual(wt_roots, 2)

    def test_a_none_generator_is_caught(self):
        # an "include nothing" generator would leave only the base roots; the
        # real one adds the live benches.
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        self.assertGreater(len(ws["folders"]), len(_roots()))


class Decoration(unittest.TestCase):
    def test_status_emoji_and_pr_number_and_short_branch(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        names = [f["name"] for f in ws["folders"]]
        self.assertIn("🟢 #100 live", names)      # live-worktree, PR number, prefix dropped
        self.assertIn("🔵 #200 review", names)     # in-review

    def test_live_sorts_before_in_review(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        wt = [f["name"] for f in ws["folders"] if f["name"] not in ("ontum", "gallery")]
        self.assertEqual(wt, ["🟢 #100 live", "🔵 #200 review"])

    def test_label_drops_claude_prefix_and_falls_back_to_slug(self):
        self.assertEqual(
            forest.workspace_label({"branch": "claude/foo-bar"}, {}), "foo-bar")
        self.assertEqual(
            forest.workspace_label({"branch": None, "slug": "loose"}, {}), "loose")
        self.assertEqual(
            forest.workspace_label({"branch": "claude/x"}, {"claude/x": 7}), "#7 x")


class ValidWorkspaceOutput(unittest.TestCase):
    def test_renders_to_valid_json_with_folders_list(self):
        ws = forest.build_workspace(_model(), _roots(), _numbers())
        text = forest.render_workspace(ws)
        parsed = json.loads(text)
        self.assertIsInstance(parsed.get("folders"), list)
        self.assertIn("settings", parsed)
        self.assertTrue(text.endswith("\n"))

    def test_generation_is_deterministic(self):
        a = forest.build_workspace(_model(), _roots(), _numbers())
        b = forest.build_workspace(_model(), _roots(), _numbers())
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
