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


class InferenceVerifiedCut(unittest.TestCase):
    """The inference-verified cut (done-line 0100): a branch deletion is held
    until a deterministic content floor AND a habitual inference affirmation
    both agree. The §10 bite is that two locally-fine signals — a merged-looking
    branch and a model that says 'safe' — still refuse to fit against the hard
    truth that unlanded commits exist; and that the cut FAILS SAFE when the
    governed inference plane gives no answer (default-deny / down)."""

    # ---- the pure core: cut_verdict ----

    def test_unlanded_commit_holds_even_when_inference_affirms_safe(self):
        # the teeth: the content floor is absolute; no model verdict overrides it.
        v, reason = gitpen.cut_verdict(2, "safe")
        self.assertEqual(v, "hold")
        self.assertIn("not on origin/main", reason)

    def test_inference_unavailable_holds_a_clean_branch(self):
        # default-deny / down → unavailable → hold (fail-safe).
        self.assertEqual(gitpen.cut_verdict(0, "unavailable")[0], "hold")

    def test_inference_hold_or_uncertain_holds_a_clean_branch(self):
        self.assertEqual(gitpen.cut_verdict(0, "hold")[0], "hold")
        self.assertEqual(gitpen.cut_verdict(0, "uncertain")[0], "hold")

    def test_only_clean_and_affirmed_ever_cuts(self):
        # exhaustive: cut iff (zero unlanded AND explicit safe).
        cuts = [
            (n, v)
            for n in (0, 1, 3)
            for v in ("safe", "hold", "uncertain", "unavailable", "floor-hold")
            if gitpen.cut_verdict(n, v)[0] == "cut"
        ]
        self.assertEqual(cuts, [(0, "safe")])

    # ---- the reply parser ----

    def test_parse_verdict(self):
        self.assertEqual(gitpen.parse_inference_verdict(None), "unavailable")
        self.assertEqual(gitpen.parse_inference_verdict("SAFE: all merged"), "safe")
        self.assertEqual(gitpen.parse_inference_verdict("  hold: novel work\n"), "hold")
        self.assertEqual(gitpen.parse_inference_verdict("I think maybe?"), "uncertain")
        # the token must stand alone — "SAFEGUARD" is not an affirmation.
        self.assertEqual(gitpen.parse_inference_verdict("SAFEGUARD the branch"), "uncertain")
        self.assertEqual(gitpen.parse_inference_verdict("SAFE"), "safe")

    # ---- evidence + orchestration: verify_cut ----

    @staticmethod
    def _git_fn(cherry):
        """A fake git over the three reads branch_cut_evidence makes."""
        def fn(args):
            if args[0] == "cherry":
                return cherry
            if args[0] == "log":
                return "abc123 a novel commit"
            if args[0] == "diff":
                return " loop/x.py | 10 ++++++"
            return ""
        return fn

    def test_verify_cut_unlanded_holds_without_thinking(self):
        # an unlanded commit holds at the floor — the gateway is never consulted.
        calls = []
        def complete_fn(prompt):
            calls.append(prompt)
            return "SAFE: trust me"
        v, _ = gitpen.verify_cut("b", self._git_fn("+ abc123\n- def456"),
                                 complete_fn=complete_fn)
        self.assertEqual(v, "hold")
        self.assertEqual(calls, [])  # no thought spent on a floor-hold

    def test_verify_cut_clean_and_affirmed_cuts_and_carries_prompt_sha(self):
        seen = {}
        def complete_fn(prompt):
            seen["prompt"] = prompt
            return "SAFE: every change is upstream"
        v, _ = gitpen.verify_cut("b", self._git_fn("- abc123"),
                                 complete_fn=complete_fn)
        self.assertEqual(v, "cut")
        # prompt-as-code: the artifact's sha256 rides the prompt (→ prompt_hash
        # on the receipt), every cut attributable to the prompt that judged it.
        self.assertIn(gitpen.cut_prompt_sha(), seen["prompt"])

    def test_verify_cut_clean_but_unavailable_holds(self):
        # the gateway gives no answer (default-deny / down) → hold (fail-safe).
        v, _ = gitpen.verify_cut("b", self._git_fn(""), complete_fn=lambda p: None)
        self.assertEqual(v, "hold")

    def test_verify_cut_thinking_raises_holds_not_crashes(self):
        def boom(prompt):
            raise RuntimeError("backing exploded")
        v, _ = gitpen.verify_cut("b", self._git_fn(""), complete_fn=boom)
        self.assertEqual(v, "hold")  # fail-soft: an error never cuts


if __name__ == "__main__":
    unittest.main()
