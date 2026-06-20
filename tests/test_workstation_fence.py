"""§10 for the workstation fence (done-line 0145).

The teeth: a tree/HEAD-flipping git verb is syntactically identical wherever
it runs — `git switch main` is valid git in any tree. The fence must refuse it
in bdo's VIEWPORT (the primary tree) and accept the very same command inside a
linked worktree. A test that only checked "switch is denied" would be a static
deny-list; this one proves the gate discriminates on LOCATION, not syntax —
two locally-fine invocations, one refused, one allowed, and the guard notices
the difference (the §10 bar). Reads and the branded git pen are allowed in the
viewport; that is the line between organizing and flipping.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = REPO / ".claude" / "hooks" / "command_guard.py"

sys.path.insert(0, str(REPO / ".claude" / "hooks"))
import command_guard as g  # noqa: E402


def run_guard(command, cwd, watch_log):
    """Run the live guard as the harness would (subprocess, stdin payload),
    with logs pointed at a throwaway path so the test never touches truth."""
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test-workstation-fence",
    })
    env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(watch_log))
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=payload, text=True, capture_output=True, cwd=str(cwd), env=env,
    )
    return proc.returncode, proc.stderr


class FlipParsing(unittest.TestCase):
    """git_viewport_flip names the flipping verb and only the flipping verb."""

    def test_flipping_verbs_are_named(self):
        for cmd, verb in [
            ("git switch main", "switch"),
            ("git checkout -b claude/x", "checkout"),
            ("git reset --hard origin/main", "reset"),
            ("git restore .", "restore"),
            ("git clean -fd", "clean"),
            ("git merge origin/main", "merge"),
            ("git rebase main", "rebase"),
            ("git cherry-pick abc", "cherry-pick"),
            ("git revert abc", "revert"),
            ("git stash", "stash"),
        ]:
            self.assertEqual(g.git_viewport_flip(cmd), verb, cmd)

    def test_reads_and_organizing_are_not_flips(self):
        for cmd in [
            "git status", "git log --oneline", "git diff", "git show HEAD",
            "git branch", "git branch --list", "git branch -a", "git branch -v",
            "git worktree add -b claude/x ../ontum-wt/x origin/main",
            "git worktree remove ../ontum-wt/x", "git fetch origin",
            "python .claude/skills/branch-ritual/git.py sync",
            "git tag --list",
        ]:
            self.assertIsNone(g.git_viewport_flip(cmd), cmd)

    def test_branch_flips_only_when_it_mutates(self):
        self.assertEqual(g.git_viewport_flip("git branch -D foo"), "branch")
        self.assertEqual(g.git_viewport_flip("git branch -m old new"), "branch")
        self.assertEqual(g.git_viewport_flip("git branch newbranch"), "branch")
        self.assertIsNone(g.git_viewport_flip("git branch --list feature/*"))

    def test_stash_flips_only_when_it_mutates(self):
        # the false-positive the review caught: list/show are reads
        self.assertIsNone(g.git_viewport_flip("git stash list"))
        self.assertIsNone(g.git_viewport_flip("git stash show -p"))
        self.assertEqual(g.git_viewport_flip("git stash"), "stash")
        self.assertEqual(g.git_viewport_flip("git stash pop"), "stash")
        self.assertEqual(g.git_viewport_flip("git stash drop"), "stash")

    def test_global_options_do_not_hide_the_verb(self):
        # the -C bypass the review caught: -C/-c must not be read as the verb
        self.assertEqual(g.git_viewport_flip("git -C /some/path switch main"), "switch")
        self.assertEqual(g.git_viewport_flip("git -c user.name=x reset --hard"), "reset")
        self.assertEqual(g.git_viewport_flip("git --no-pager switch main"), "switch")
        self.assertEqual(g.dash_c_paths("git -C ../wt switch main"), ["../wt"])
        self.assertEqual(g.dash_c_paths("git switch main"), [])


class ViewportVsWorktree(unittest.TestCase):
    """The gate's discriminating teeth: same command, two locations."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ws-fence-")
        self.addCleanup(self._cleanup)
        self.primary = pathlib.Path(self.tmp) / "primary"
        self.primary.mkdir()
        self.watch = pathlib.Path(self.tmp) / ".ai-native" / "log" / "tool-use.jsonl"
        env = dict(user_email="t@t", user_name="t")
        _git(self.primary, "init", "-q")
        _git(self.primary, "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--allow-empty", "-q", "-m", "init")
        self.wt = pathlib.Path(self.tmp) / "wt"
        _git(self.primary, "worktree", "add", "-q", "-b", "wtbranch", str(self.wt))

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_flip_denied_in_the_viewport(self):
        rc, err = run_guard("git switch main", self.primary, self.watch)
        self.assertEqual(rc, 2, err)
        self.assertIn("VIEWPORT", err)
        self.assertIn("git.py sync", err)  # the refusal names the paved path

    def test_same_flip_allowed_in_a_worktree(self):
        rc, err = run_guard("git switch main", self.wt, self.watch)
        self.assertEqual(rc, 0, err)

    def test_read_allowed_in_the_viewport(self):
        rc, err = run_guard("git status", self.primary, self.watch)
        self.assertEqual(rc, 0, err)

    def test_branded_pen_allowed_in_the_viewport(self):
        rc, err = run_guard(
            "python .claude/skills/branch-ritual/git.py sync",
            self.primary, self.watch)
        self.assertEqual(rc, 0, err)

    def test_organizing_worktrees_allowed_in_the_viewport(self):
        rc, err = run_guard(
            "git worktree add -b claude/y ../ontum-wt/y origin/main",
            self.primary, self.watch)
        self.assertEqual(rc, 0, err)

    def test_dash_C_at_the_viewport_from_a_worktree_is_denied(self):
        # the -C bypass: standing in a worktree, retargeting git at the
        # viewport must still be refused — the tree touched, not cwd, decides
        rc, err = run_guard(
            f"git -C {self.primary} switch main", self.wt, self.watch)
        self.assertEqual(rc, 2, err)

    def test_dash_C_at_a_worktree_from_the_viewport_is_allowed(self):
        # the mirror: standing in the viewport, retargeting git at a worktree
        # is a worker editing its own bench by path — allowed
        rc, err = run_guard(
            f"git -C {self.wt} switch main", self.primary, self.watch)
        self.assertEqual(rc, 0, err)

    def test_stash_read_allowed_in_the_viewport(self):
        rc, err = run_guard("git stash list", self.primary, self.watch)
        self.assertEqual(rc, 0, err)


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), check=True,
                   capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
