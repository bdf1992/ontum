"""The git pen's :whiteout utensil — recovering a DIRTY viewport without losing
a byte (done-line 0170, #415).

Distinct from `test_whiteout.py` (the log/phrasing whiteout pen, done-line
0064): this is the GIT-pen utensil that sorts a dirty primary tree.

The deadlock #415 names: a session cannot sort a dirty viewport (the
workstation fence forbids every working-state git verb in the primary tree),
and `sync` cannot fast-forward over an unsaved tree. The pen is the one actor
sanctioned to flip the viewport, so recovery is the pen's — and it must be
PROOF-CARRYING (the whiteout shape, done-line 0064): preserve the whole pile
before cleaning, never discard.

The §10 teeth here are two locally-fine truths that must not be reconciled by
losing one: "the viewport must reach the trunk" and "the unsaved pile must
survive." A naive force-clean satisfies the first by destroying the second.
`test_naive_clean_would_lose_the_pile` proves the assertion is non-vacuous —
the WRONG recovery really does lose the pile, so a green
`test_recovers_and_loses_nothing` means real preservation happened.

Real git in temp repos: a bare `origin`, a `viewport` clone, origin advanced
beyond the viewport so there is a genuine fast-forward to make.
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "git_pen", ROOT / ".claude" / "skills" / "branch-ritual" / "git.py")
gitpen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gitpen)


def git(args, cwd, timeout=None):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=str(cwd), timeout=timeout)


def _commit_all(cwd, message):
    git(["add", "-A"], cwd)
    git(["commit", "-q", "-m", message], cwd)


def _identity(cwd):
    git(["config", "user.email", "test@ontum.local"], cwd)
    git(["config", "user.name", "ontum-test"], cwd)


class RescueBranchName(unittest.TestCase):
    """The pure naming fold — deterministic, never clobbers an earlier rescue."""

    def test_first_of_the_day_is_unsuffixed(self):
        self.assertEqual(
            gitpen.rescue_branch_name("2026-06-21", set()),
            "claude/rescue-viewport-2026-06-21")

    def test_collision_gets_the_next_free_suffix(self):
        existing = {"claude/rescue-viewport-2026-06-21",
                    "claude/rescue-viewport-2026-06-21-2"}
        self.assertEqual(
            gitpen.rescue_branch_name("2026-06-21", existing),
            "claude/rescue-viewport-2026-06-21-3")


class WhiteoutRecovery(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.origin = tmp / "origin.git"
        git(["init", "--bare", "-q", "-b", "main", str(self.origin)], tmp)

        # seed origin/main with one commit
        seed = tmp / "seed"
        git(["clone", "-q", str(self.origin), str(seed)], tmp)
        _identity(seed)
        (seed / "tracked.txt").write_text("original\n", encoding="utf-8")
        _commit_all(seed, "seed")
        git(["push", "-q", "origin", "main"], seed)
        # advance origin/main one commit beyond what the viewport will hold,
        # so there is a real fast-forward to perform after the tree is clean
        (seed / "ahead.txt").write_text("from-origin\n", encoding="utf-8")
        _commit_all(seed, "advance origin")
        git(["push", "-q", "origin", "main"], seed)
        self.origin_head = git(["rev-parse", "main"], seed).stdout.strip()

        # the viewport: a clone whose local main is one behind origin/main
        self.viewport = tmp / "viewport"
        git(["clone", "-q", str(self.origin), str(self.viewport)], tmp)
        _identity(self.viewport)
        git(["reset", "--hard", "-q", "HEAD~1"], self.viewport)  # one behind

    def tearDown(self):
        self._tmp.cleanup()

    def _dirty_the_viewport(self):
        """A real pile: a modified tracked file AND a new untracked file —
        the two kinds a naive clean discards differently."""
        (self.viewport / "tracked.txt").write_text(
            "DIRTY EDIT\n", encoding="utf-8")
        (self.viewport / "untracked.txt").write_text(
            "brand new work\n", encoding="utf-8")

    def _run_recovery(self):
        msgs = []
        # the actuator's contract: the caller (cmd_sync) has fetched origin/main
        git(["fetch", "-q", "origin", "main"], self.viewport)
        gitpen.recover_dirty_viewport(
            self.viewport, git,
            emit=lambda state, m: msgs.append((state, m)),
            bail=lambda m: (_ for _ in ()).throw(AssertionError("bailed: " + m)),
            ns=SimpleNamespace(fetch_timeout=20, hook=False, recover=True))
        return msgs

    def test_recovers_and_loses_nothing(self):
        self._dirty_the_viewport()
        msgs = self._run_recovery()

        # the viewport is clean and fast-forwarded to origin/main
        self.assertEqual(
            git(["status", "--porcelain"], self.viewport).stdout.strip(), "")
        self.assertEqual(
            git(["rev-parse", "HEAD"], self.viewport).stdout.strip(),
            self.origin_head)
        self.assertEqual(
            git(["branch", "--show-current"], self.viewport).stdout.strip(),
            "main")

        # a rescue branch exists, locally and pushed to origin
        rescue = next(
            b.strip().lstrip("* ").strip()
            for b in git(["branch", "--list", "claude/rescue-viewport-*"],
                         self.viewport).stdout.splitlines() if b.strip())
        self.assertTrue(rescue.startswith("claude/rescue-viewport-"))
        self.assertTrue(
            git(["ls-remote", "--heads", "origin", rescue],
                self.viewport).stdout.strip(),
            "the rescue branch was not pushed to origin")

        # NOTHING LOST: the rescue branch holds the EXACT pile — the dirtied
        # tracked file and the untracked file, byte-for-byte
        self.assertEqual(
            git(["show", f"{rescue}:tracked.txt"], self.viewport).stdout,
            "DIRTY EDIT\n")
        self.assertEqual(
            git(["show", f"{rescue}:untracked.txt"], self.viewport).stdout,
            "brand new work\n")

        self.assertTrue(any(state == "done" for state, _ in msgs))

    def test_naive_clean_would_lose_the_pile(self):
        """Non-vacuity: the WRONG recovery (force-clean to origin/main) really
        does destroy the pile, so the preservation assertion above is load-
        bearing, not trivially true."""
        self._dirty_the_viewport()
        git(["fetch", "-q", "origin", "main"], self.viewport)
        git(["reset", "--hard", "-q", "origin/main"], self.viewport)
        git(["clean", "-fd", "-q"], self.viewport)

        # the tracked edit is reverted and the untracked file is gone — lost
        self.assertEqual(
            (self.viewport / "tracked.txt").read_text(encoding="utf-8"),
            "original\n")
        self.assertFalse((self.viewport / "untracked.txt").exists())
        # and no rescue branch was made to hold it
        self.assertEqual(
            git(["branch", "--list", "claude/rescue-viewport-*"],
                self.viewport).stdout.strip(), "")

    def test_clean_viewport_recovery_is_a_plain_sync(self):
        """On a CLEAN viewport whiteout is just a fast-forward — no rescue
        branch, nothing lost, the trunk reached."""
        msgs = self._run_recovery()  # not dirtied
        self.assertEqual(
            git(["rev-parse", "HEAD"], self.viewport).stdout.strip(),
            self.origin_head)
        self.assertEqual(
            git(["branch", "--list", "claude/rescue-viewport-*"],
                self.viewport).stdout.strip(), "",
            "a clean viewport must not spawn a rescue branch")
        self.assertTrue(any(state == "done" for state, _ in msgs))


if __name__ == "__main__":
    unittest.main()
