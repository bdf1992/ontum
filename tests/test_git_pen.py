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


class TestSyncRefusal(unittest.TestCase):
    """Done-line 0031: the viewport only ever moves forward to origin/main.

    The §10 case: a viewport that drifted off the trunk, or a trunk
    carrying local commits, is locally fine git — sync must still refuse
    to fit, because acting there would re-point or bury bdo's reading
    surface instead of surfacing it to him."""

    def test_off_trunk_viewport_refused(self):
        self.assertIn("not the trunk", gitpen.sync_refusal("claude/stray", 0))

    def test_detached_viewport_refused(self):
        self.assertIn("detached HEAD", gitpen.sync_refusal("", 0))

    def test_locally_ahead_trunk_refused(self):
        # never committed locally (firm) — sync surfaces, never syncs over
        reason = gitpen.sync_refusal("main", 2)
        self.assertIn("2 local commit", reason)
        self.assertIn("surface this to bdo", reason)

    def test_clean_trunk_viewport_passes(self):
        for trunk in ("main", "master"):
            self.assertIsNone(gitpen.sync_refusal(trunk, 0), trunk)


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
