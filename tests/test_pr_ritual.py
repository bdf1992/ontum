"""Done-line 0011: the pen refuses what the ritual forbids.

The §10 test, applied to hand-off: clean commits and a green suite are
locally fine — they must still refuse to fit into a PR when the story
is unwritten, and the guard must notice raw verbs without strangling
legitimate work. Pure-function tests hit the pen's validation and body
form directly; the guard and watcher run as real subprocesses fed
PreToolUse JSON, with the watch log pointed at a temp file.
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
PEN_PATH = ROOT / ".claude" / "skills" / "branch-ritual" / "pr.py"
GUARD_PATH = ROOT / ".claude" / "hooks" / "command_guard.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pen = _load("pr_pen", PEN_PATH)


def _story(**overrides):
    story = {
        "title": "the pen writes the story",
        "landed": ["a validated story form"],
        "done_line": "0011",
        "report": "0013",
        "why": "",
        "end_state": "report",
        "flags": [],
        "red_reason": "",
    }
    story.update(overrides)
    return story


class TestStoryValidation(unittest.TestCase):
    BRANCH = "claude/busy-feynman-4hd46k"

    def test_held_story_passes(self):
        self.assertEqual(pen.validate_story(_story(), self.BRANCH), [])

    def test_storyless_create_refuses(self):
        problems = pen.validate_story(_story(title="", landed=[]), self.BRANCH)
        self.assertGreaterEqual(len(problems), 2)

    def test_auto_title_refused(self):
        # GitHub's button title for this branch — the PR #8 fingerprint
        problems = pen.validate_story(
            _story(title="Claude/busy feynman 4hd46k"), self.BRANCH)
        self.assertTrue(any("branch name" in p for p in problems))

    def test_none_requires_why(self):
        problems = pen.validate_story(_story(done_line="none"), self.BRANCH)
        self.assertTrue(any("--why" in p for p in problems))
        self.assertEqual(
            pen.validate_story(
                _story(done_line="none",
                       why="recovery of another session's stranded work"),
                self.BRANCH),
            [])

    def test_needs_you_requires_flag(self):
        problems = pen.validate_story(_story(end_state="needs-you"), self.BRANCH)
        self.assertTrue(any("--flag" in p for p in problems))
        self.assertEqual(
            pen.validate_story(
                _story(end_state="needs-you", flags=["the Core 27 awaits the pin"]),
                self.BRANCH),
            [])

    def test_end_state_vocabulary(self):
        problems = pen.validate_story(_story(end_state="finished"), self.BRANCH)
        self.assertTrue(any("--end-state" in p for p in problems))


class TestBodyForm(unittest.TestCase):
    def test_body_carries_every_section(self):
        body = pen.compose_body(_story(flags=["the Core 27 awaits the pin"]))
        for needle in ("## What landed", "## Done-line", "## Report",
                       "## End-state: `report`", "Flagged for bdo:",
                       pen.FOOTER):
            self.assertIn(needle, body)

    def test_nothing_flagged_is_said_not_omitted(self):
        self.assertIn("Nothing flagged for bdo.", pen.compose_body(_story()))

    def test_red_handoff_is_declared_in_the_body(self):
        body = pen.compose_body(
            _story(red_reason="two web tests red; scope shrunk per §9.5"))
        self.assertIn("## Red hand-off (declared)", body)

    def test_green_body_has_no_red_section(self):
        self.assertNotIn("Red hand-off", pen.compose_body(_story()))

    def test_body_is_deterministic(self):
        self.assertEqual(pen.compose_body(_story()), pen.compose_body(_story()))


class TestGuardAndWatcher(unittest.TestCase):
    def setUp(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        self.watch_log = pathlib.Path(path)
        self.addCleanup(self.watch_log.unlink)

    def _invoke(self, command, tool="Bash"):
        payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        return subprocess.run(
            [sys.executable, str(GUARD_PATH)], input=payload,
            capture_output=True, text=True, env=env)

    def _entries(self):
        text = self.watch_log.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_raw_pr_create_denied_and_recorded(self):
        proc = self._invoke('gh pr create --title "x" --body "y"')
        self.assertEqual(proc.returncode, 2)
        self.assertIn("pen", proc.stderr)
        self.assertEqual(self._entries()[0]["status"], "denied")

    def test_raw_pr_edit_denied_for_powershell_too(self):
        self.assertEqual(self._invoke("gh pr edit 8 --body z", tool="PowerShell").returncode, 2)

    def test_merge_denied_firm(self):
        proc = self._invoke("gh pr merge 9 --squash")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("stamp is bdo's", proc.stderr)

    def test_self_review_denied(self):
        self.assertEqual(self._invoke("gh pr review 9 --approve").returncode, 2)

    def test_push_to_trunk_denied_in_any_spelling(self):
        for command in ("git push origin main",
                        "git push -f origin HEAD:main",
                        "git push origin --delete main"):
            self.assertEqual(self._invoke(command).returncode, 2, command)

    def test_session_branch_push_allowed_and_watched(self):
        proc = self._invoke("git push -u origin claude/quiet-hopper-ovn8x1")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["bins"], ["git"])

    def test_branch_named_like_trunk_is_not_a_trunk_push(self):
        self.assertEqual(self._invoke("git push origin claude/fix-main-page").returncode, 0)

    def test_read_only_gh_allowed_but_watched(self):
        proc = self._invoke("gh pr view 8 --json body")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["bins"], ["gh"])

    def test_local_work_is_invisible(self):
        for command in ("python -m unittest discover -s tests",
                        "git status --porcelain",
                        "ls -la | head -5"):
            self.assertEqual(self._invoke(command).returncode, 0, command)
        self.assertEqual(self._entries(), [])

    def test_the_pen_itself_passes_the_guard(self):
        proc = self._invoke(
            "python .claude/skills/branch-ritual/pr.py create --title x")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries(), [])

    def test_report_folds_the_log(self):
        self._invoke("gh pr view 8")
        self._invoke("curl https://example.com")
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH), "--report"],
            capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("gh", proc.stdout)
        self.assertIn("curl", proc.stdout)
        self.assertIn("result: report", proc.stdout)

    def test_torn_tail_never_happened(self):
        self._invoke("gh pr view 8")
        with open(self.watch_log, "a", encoding="utf-8") as fh:
            fh.write('{"status": "watched", "bins": ["gh"')  # torn line
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH), "--report"],
            capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("gh: 1 raw call(s)", proc.stdout)


if __name__ == "__main__":
    unittest.main()
