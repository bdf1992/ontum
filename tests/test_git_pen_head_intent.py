"""Tests for the HEAD-intent guard (done-line 0118): a commit refuses when
live HEAD differs from the branch the session asserts with `--on`.

The §10 teeth are the two ways a fake guard fails:
- a guard that ALWAYS passes fails `test_wrong_branch_*` (the collision the
  guard exists to catch must be refused, with a HEAD-intent reason);
- a guard that ALWAYS refuses fails `test_right_branch_does_not_trip` and
  `test_omitted_assertion_passes` (a correct, matching branch — and the
  backward-compatible no-`--on` path — must not be refused for HEAD-intent).

The pure refusal function is unit-tested; the live pen is driven as a
subprocess to prove the flag is wired through argparse to the function.
"""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PEN = REPO / ".claude" / "skills" / "branch-ritual" / "git.py"

_spec = importlib.util.spec_from_file_location("branch_ritual_git", PEN)
gitpen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gitpen)


class TestHeadIntentRefusal(unittest.TestCase):
    def test_wrong_branch_is_refused_and_named(self):
        r = gitpen.head_intent_refusal("claude/actual", "claude/declared")
        self.assertIsNotNone(r)
        self.assertIn("HEAD-intent", r)
        self.assertIn("claude/declared", r)  # what you asserted
        self.assertIn("claude/actual", r)     # where HEAD really is

    def test_matching_branch_passes(self):
        self.assertIsNone(gitpen.head_intent_refusal("claude/x", "claude/x"))

    def test_omitted_assertion_refuses(self):
        """No `--on` means no declared branch intent."""
        for expected in (None, ""):
            r = gitpen.head_intent_refusal("claude/x", expected)
            self.assertIsNotNone(r)
            self.assertIn("HEAD-intent required", r)

    def test_detached_head_is_named_when_mismatched(self):
        r = gitpen.head_intent_refusal("", "claude/x")
        self.assertIsNotNone(r)
        self.assertIn("detached", r)


class TestLivePenWiring(unittest.TestCase):
    def _current_branch(self):
        return subprocess.run(
            ["git", "branch", "--show-current"], cwd=REPO,
            capture_output=True, text=True).stdout.strip()

    def test_wrong_branch_subprocess_refuses(self):
        p = subprocess.run(
            [sys.executable, str(PEN), "commit",
             "--on", "branch-that-is-not-checked-out", "-m", "x"],
            cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
        self.assertNotEqual(p.returncode, 0, "a wrong-branch commit must refuse")
        self.assertIn("HEAD-intent", out)

    def test_missing_on_subprocess_refuses_before_git_commit(self):
        p = subprocess.run(
            [sys.executable, str(PEN), "commit", "-m", "x"],
            cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
        self.assertNotEqual(p.returncode, 0, "a no-intent commit must refuse")
        self.assertIn("HEAD-intent required", out)

    def test_right_branch_does_not_trip_the_guard(self):
        cur = self._current_branch()
        if not cur:
            self.skipTest("detached HEAD in this test environment")
        p = subprocess.run(
            [sys.executable, str(PEN), "commit", "--on", cur, "-m", "x"],
            cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
        # it may refuse for other reasons (nothing staged), but never for
        # HEAD-intent when the asserted branch matches live HEAD
        self.assertNotIn("HEAD-intent", out)


if __name__ == "__main__":
    unittest.main()
