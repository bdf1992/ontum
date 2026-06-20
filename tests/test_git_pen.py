"""Done-line 0020: the git pen refuses the sweep; the guard routes raw
git add/commit to it; the watcher now sees local mutating git.

The §10 test, applied to staging: `git add .` is a locally-fine git
command — in the shared-tree fleet it must still *refuse to fit*,
because it would stage another session's uncommitted work. Pure-function
tests hit the pen's refusals directly; the guard and watcher run as real
subprocesses fed PreToolUse JSON, with the watch log pointed at a temp
file (the contract is exit codes and streams, not internals).
"""

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEN_PATH = ROOT / ".claude" / "skills" / "branch-ritual" / "git.py"
GUARD_PATH = ROOT / ".claude" / "hooks" / "command_guard.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gitpen = _load("git_pen", PEN_PATH)
guard = _load("command_guard_git", GUARD_PATH)


class TestAddRefusal(unittest.TestCase):
    """No sweep — name the paths (the parallel-fleet invariant)."""

    def test_dot_is_a_sweep(self):
        self.assertIn("sweep", gitpen.add_refusal(["."]))

    def test_every_sweep_flag_refused(self):
        for sweep in (["-A"], ["--all"], ["-u"], ["--update"], ["*"], [":/"]):
            self.assertIsNotNone(gitpen.add_refusal(sweep), sweep)

    def test_no_path_named_is_refused(self):
        self.assertIn("at least one path", gitpen.add_refusal([]))
        self.assertIsNotNone(gitpen.add_refusal(["--verbose"]))  # flags only, no path

    def test_interactive_add_refused(self):
        for flag in (["-p"], ["-i"], ["--patch"], ["--interactive"], ["-e"]):
            self.assertIn("interactive", gitpen.add_refusal(flag), flag)

    def test_named_paths_pass(self):
        self.assertIsNone(gitpen.add_refusal(["loop/reconcile.py", "tests/test_loop.py"]))
        self.assertIsNone(gitpen.add_refusal(["loop/"]))                  # a named subdir is a choice
        self.assertIsNone(gitpen.add_refusal(["--verbose", "loop/x.py"]))  # non-sweep flag + a path


class TestCommitRefusal(unittest.TestCase):
    BRANCH = "claude/git-commit-pen"

    def test_trunk_is_refused(self):
        for trunk in ("main", "master"):
            self.assertIn("trunk", gitpen.commit_refusal(trunk, ["a line"], []))

    def test_detached_head_refused(self):
        self.assertIn("detached", gitpen.commit_refusal("", ["a line"], []))

    def test_auto_stage_sweep_refused(self):
        for sweep in (["-a"], ["--all"]):
            self.assertIsNotNone(gitpen.commit_refusal(self.BRANCH, ["m"], sweep), sweep)

    def test_message_is_required(self):
        self.assertIn("message", gitpen.commit_refusal(self.BRANCH, [], []))
        self.assertIn("message", gitpen.commit_refusal(self.BRANCH, ["   "], []))  # whitespace-only

    def test_message_from_file_satisfies_parity(self):
        # -F <file> is a real message source — feature parity, not a hole
        self.assertIsNone(gitpen.commit_refusal(self.BRANCH, [], ["-F", "msg.txt"]))

    def test_interactive_commit_refused(self):
        for flag in (["-p"], ["--patch"], ["--interactive"], ["-e"]):
            self.assertIn("interactive", gitpen.commit_refusal(self.BRANCH, ["m"], flag), flag)

    def test_path_scoped_flags_stay_allowed(self):
        # -i/--include and -o/--only NAME the paths — they are not the sweep
        for ok in (["-o", "loop/x.py"], ["--only", "loop/x.py"],
                   ["-i", "loop/x.py"], ["loop/x.py"]):
            self.assertIsNone(gitpen.commit_refusal(self.BRANCH, ["m"], ok), ok)

    def test_healthy_commit_passes(self):
        self.assertIsNone(gitpen.commit_refusal(self.BRANCH, ["feat: a real line"], []))


class TestInvocationRootRefusal(unittest.TestCase):
    def test_matching_root_passes(self):
        self.assertIsNone(gitpen.invocation_root_refusal(ROOT, ROOT))

    def test_missing_git_root_refuses(self):
        reason = gitpen.invocation_root_refusal(ROOT, None)
        self.assertIn("not inside a git worktree", reason)

    def test_mismatched_git_root_refuses(self):
        reason = gitpen.invocation_root_refusal(ROOT, ROOT.parent)
        self.assertIn("pen/worktree mismatch", reason)
        self.assertIn(str(ROOT.resolve()), reason)

    def test_pen_invoked_from_another_repo_refuses_before_git_add(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
            proc = subprocess.run(
                [sys.executable, str(PEN_PATH), "add", "x.py"],
                cwd=tmp, capture_output=True, text=True)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("pen/worktree mismatch", out)


class TestSyncRefusal(unittest.TestCase):
    """Done-line 0031, amended 2026-06-11 (rules expect support, not offload):
    a viewport stranded off the trunk is the session's to RESTORE, not bdo's
    to be handed. sync_refusal now stops only what cannot be auto-acted —
    local commits sitting on main. The off-trunk case moved to restore_blocked,
    which refuses a restore *only* to preserve work it would lose.

    The §10 case: a clean, pushed off-trunk viewport is locally fine and the
    old rule surfaced it to bdo; the new rule restores it (restore_blocked is
    None). The refusal now fires on the opposite shape — uncommitted/unpushed
    work — because acting *there* would lose it."""

    def test_off_trunk_is_not_a_sync_refusal_anymore(self):
        # off-trunk is handled by restore, no longer a flat refusal
        self.assertIsNone(gitpen.sync_refusal("claude/stray", 0))

    def test_locally_ahead_trunk_refused(self):
        # main is never committed locally (firm); the session branches + PRs it
        reason = gitpen.sync_refusal("main", 2)
        self.assertIn("2 local commit", reason)
        self.assertNotIn("surface this to bdo", reason)

    def test_clean_trunk_viewport_passes(self):
        for trunk in ("main", "master"):
            self.assertIsNone(gitpen.sync_refusal(trunk, 0), trunk)


class TestRestoreBlocked(unittest.TestCase):
    """The new teeth: a stranded viewport restores to main when its work is
    safe (clean + pushed), and is blocked only to preserve work a restore
    would lose — never handed to bdo."""

    def test_clean_and_pushed_restores(self):
        self.assertIsNone(gitpen.restore_blocked(clean=True, pushed=True))

    def test_uncommitted_blocks_to_preserve(self):
        reason = gitpen.restore_blocked(clean=False, pushed=True)
        self.assertIn("uncommitted", reason)
        self.assertIn("never bdo's", reason)

    def test_unpushed_blocks_to_preserve(self):
        reason = gitpen.restore_blocked(clean=True, pushed=False)
        self.assertIn("not on origin", reason)
        self.assertIn("never bdo's", reason)


class TestGitGuard(unittest.TestCase):
    def setUp(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        self.watch_log = pathlib.Path(path)
        self.addCleanup(self.watch_log.unlink)

    def _invoke(self, command, tool="Bash", session="s1"):
        payload = json.dumps({"session_id": session, "tool_name": tool,
                              "tool_input": {"command": command}})
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        return subprocess.run([sys.executable, str(GUARD_PATH)], input=payload,
                              capture_output=True, text=True, env=env)

    def _entries(self):
        text = self.watch_log.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_raw_git_add_denied_toward_the_pen(self):
        proc = self._invoke("git add foo.py bar.py")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("git pen", proc.stderr)
        # rule ids are the fence registry's since done-line 0029
        self.assertEqual(self._entries()[0]["rule"], "git-add")

    def test_raw_git_commit_denied_toward_the_pen(self):
        proc = self._invoke('git commit -m "x"')
        self.assertEqual(proc.returncode, 2)
        self.assertIn("branded through the git pen", proc.stderr)
        self.assertEqual(self._entries()[0]["rule"], "git-commit")

    def test_commit_denied_in_powershell_too(self):
        self.assertEqual(self._invoke("git add x.py", tool="PowerShell").returncode, 2)

    def test_commit_tree_plumbing_is_not_the_commit_verb(self):
        # the lookahead spares git commit-tree (plumbing); still watched, not denied
        proc = self._invoke("git commit-tree abc123")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["bins"], ["git"])

    def test_the_git_pen_passes_the_guard(self):
        for verb in ("add loop/x.py", 'commit -m "feat: a line"'):
            proc = self._invoke(f"python .claude/skills/branch-ritual/git.py {verb}")
            self.assertEqual(proc.returncode, 0, verb)
        self.assertEqual(self._entries(), [])

    def test_local_mutating_git_is_now_watched(self):
        # the farm half: standalone local mutation is visible so the next
        # verb to brand nominates itself (it was invisible before 0020)
        for command in ("git checkout -b claude/x", "git branch -D claude/dead",
                        "git merge claude/feature", "git rebase main",
                        "git worktree add ../wt"):
            self.assertEqual(self._invoke(command).returncode, 0, command)
        bins = [e["bins"] for e in self._entries()]
        self.assertEqual(bins, [["git"]] * 5)

    def test_read_only_git_stays_invisible(self):
        # denying a look would diverge from the gh precedent, not match it
        for command in ("git status --porcelain", "git log --oneline -5",
                        "git diff --cached", "git show HEAD"):
            self.assertEqual(self._invoke(command).returncode, 0, command)
        self.assertEqual(self._entries(), [])


if __name__ == "__main__":
    unittest.main()
