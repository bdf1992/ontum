"""The git pen's `rescue` verb — preserving ANY worktree's uncommitted pile
onto a dated rescue branch (done-line 0193).

Sibling of `test_git_whiteout.py`: that proves the VIEWPORT recovery; this
proves the generalized bench rescue. Both ride the one rescue core
(`preserve_pile`, I-4) — `whiteout` aims it at the viewport and walks the clean
tree back to the trunk, `rescue` aims it at any worktree and leaves the pile
committed-and-pushed on the rescue branch. The forest-never-strands experiment:
any bench is one verb from preserved.

The §10 teeth here are two locally-fine truths that a no-op rescuer reconciles
by losing one: "the bench must end clean" and "the unsaved pile must survive."
`test_a_noop_rescuer_is_caught` proves the green assertions in
`test_rescues_and_loses_nothing` are NON-vacuous — a rescuer that did nothing
leaves the pile in the worktree and mints no rescue branch, so a green run means
real preservation happened.

Real git in temp repos: a bare `origin`, a `main` clone, and a genuine git
WORKTREE (`git worktree add`) carrying uncommitted work. No fixture touches the
real repo — everything is under a TemporaryDirectory.
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITPY = ROOT / ".claude" / "skills" / "branch-ritual" / "git.py"
_spec = importlib.util.spec_from_file_location("git_pen", GITPY)
gitpen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gitpen)


def git(args, cwd):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(cwd))


def _identity(cwd):
    git(["config", "user.email", "test@ontum.local"], cwd)
    git(["config", "user.name", "ontum-test"], cwd)


def _branches(cwd, pattern):
    return [b.strip().lstrip("* ").strip()
            for b in git(["branch", "--list", pattern], cwd).stdout.splitlines()
            if b.strip()]


class RescueLabel(unittest.TestCase):
    """The pure label fold — a ref-safe name from a worktree directory."""

    def test_dirname_is_reduced_to_ref_safe(self):
        self.assertEqual(gitpen._rescue_label("/tmp/My Bench #2"), "my-bench-2")

    def test_empty_label_falls_back(self):
        self.assertEqual(gitpen._rescue_label("/tmp/___"), "worktree")

    def test_default_label_keeps_viewport_branch_name(self):
        # the whiteout caller's branch name is unchanged by the generalization
        self.assertEqual(
            gitpen.rescue_branch_name("2026-06-23", set()),
            "claude/rescue-viewport-2026-06-23")


class BenchRescue(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.origin = tmp / "origin.git"
        git(["init", "--bare", "-q", "-b", "main", str(self.origin)], tmp)

        # seed origin/main from a main clone
        self.main = tmp / "main"
        git(["clone", "-q", str(self.origin), str(self.main)], tmp)
        _identity(self.main)
        (self.main / "tracked.txt").write_text("original\n", encoding="utf-8")
        git(["add", "-A"], self.main)
        git(["commit", "-q", "-m", "seed"], self.main)
        git(["push", "-q", "origin", "main"], self.main)

        # a real git WORKTREE off the main clone, on its own branch
        self.wt = tmp / "bench"
        git(["worktree", "add", "-q", "-b", "bench", str(self.wt)], self.main)
        _identity(self.wt)

    def tearDown(self):
        self._tmp.cleanup()

    def _dirty(self):
        """A real pile: a modified tracked file AND a new untracked file."""
        (self.wt / "tracked.txt").write_text("DIRTY EDIT\n", encoding="utf-8")
        (self.wt / "untracked.txt").write_text("new work\n", encoding="utf-8")

    def _run_rescue(self, target=None):
        proc = subprocess.run(
            [sys.executable, str(GITPY), "rescue", str(target or self.wt)],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=str(ROOT))
        return proc

    def test_rescues_and_loses_nothing(self):
        self._dirty()
        proc = self._run_rescue()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("result: done", proc.stdout)

        # the bench is now clean
        self.assertEqual(
            git(["status", "--porcelain"], self.wt).stdout.strip(), "")

        # ...and sitting on a rescue branch that holds the EXACT pile
        rescue = _branches(self.wt, "claude/rescue-bench-*")
        self.assertEqual(len(rescue), 1, f"expected one rescue branch, got {rescue}")
        rescue = rescue[0]
        self.assertEqual(
            git(["branch", "--show-current"], self.wt).stdout.strip(), rescue)
        self.assertEqual(
            git(["show", f"{rescue}:tracked.txt"], self.wt).stdout, "DIRTY EDIT\n")
        self.assertEqual(
            git(["show", f"{rescue}:untracked.txt"], self.wt).stdout, "new work\n")

        # the rescue branch reached origin (pushed, not just local)
        self.assertTrue(
            git(["ls-remote", "--heads", "origin", rescue], self.wt).stdout.strip(),
            "the rescue branch was not pushed to origin")

    def test_a_noop_rescuer_is_caught(self):
        """Non-vacuity: a rescuer that did NOTHING leaves the pile in the
        worktree and mints no rescue branch — so the green assertions in
        test_rescues_and_loses_nothing only pass because real preservation
        happened, not trivially."""
        self._dirty()
        # the no-op: do not run rescue at all
        self.assertTrue(
            git(["status", "--porcelain"], self.wt).stdout.strip(),
            "a no-op leaves the pile dirty")
        self.assertEqual(
            _branches(self.wt, "claude/rescue-bench-*"), [],
            "a no-op mints no rescue branch")

    def test_clean_worktree_is_a_safe_noop(self):
        proc = self._run_rescue()  # not dirtied
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("nothing to rescue", proc.stdout)
        self.assertEqual(_branches(self.wt, "claude/rescue-*"), [],
                         "a clean worktree must not spawn a rescue branch")
        # still on its own branch, untouched
        self.assertEqual(
            git(["branch", "--show-current"], self.wt).stdout.strip(), "bench")

    def test_detached_head_worktree_is_rescued(self):
        """A detached-HEAD worktree must be handled — branch from current HEAD."""
        detached = Path(self._tmp.name) / "detached"
        git(["worktree", "add", "-q", "--detach", str(detached), "HEAD"], self.main)
        _identity(detached)
        (detached / "tracked.txt").write_text("DETACHED EDIT\n", encoding="utf-8")

        proc = self._run_rescue(target=detached)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(
            git(["status", "--porcelain"], detached).stdout.strip(), "")
        rescue = _branches(detached, "claude/rescue-detached-*")
        self.assertEqual(len(rescue), 1, f"expected one rescue branch, got {rescue}")
        self.assertEqual(
            git(["show", f"{rescue[0]}:tracked.txt"], detached).stdout,
            "DETACHED EDIT\n")


if __name__ == "__main__":
    unittest.main()
