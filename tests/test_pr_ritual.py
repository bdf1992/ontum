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
guard = _load("command_guard", GUARD_PATH)


def _story(**overrides):
    story = {
        "title": "the pen carries the written story",
        "story": ("You found a path sitting where a story should be, so I rebuilt the "
                  "pen to carry the narrative whole — the way it carries this one — and "
                  "left whether it reads as a story to a separate reader. Nothing about "
                  "the pen forces a shape onto the writing anymore."),
        "red_reason": "",
    }
    story.update(overrides)
    return story


class TestStoryValidation(unittest.TestCase):
    BRANCH = "claude/busy-feynman-4hd46k"

    def test_held_story_passes(self):
        self.assertEqual(pen.validate_story(_story(), self.BRANCH), [])

    def test_storyless_create_refuses(self):
        # an empty title and an empty body are each not writing
        problems = pen.validate_story(_story(title="", story=""), self.BRANCH)
        self.assertGreaterEqual(len(problems), 2)

    def test_auto_title_refused(self):
        # GitHub's button title for this branch — the PR #8 fingerprint
        problems = pen.validate_story(
            _story(title="Claude/busy feynman 4hd46k"), self.BRANCH)
        self.assertTrue(any("branch name" in p for p in problems))

    def test_a_body_that_is_only_a_pointer_refuses(self):
        # the pen's deterministic floor: a path/ref where writing belongs is homework
        for pointer in (".ai-native/done/0020-x.md", "`0021-story-gate-prompt`", "0020"):
            problems = pen.validate_story(_story(story=pointer), self.BRANCH)
            self.assertTrue(any("pointer" in p for p in problems), pointer)

    def test_prose_that_mentions_a_path_is_still_writing(self):
        self.assertEqual(
            pen.validate_story(
                _story(story="I rewrote compose_body under .ai-native to carry the whole narrative"),
                self.BRANCH),
            [])

    def test_the_pen_does_not_judge_whether_it_is_a_story(self):
        # a flat, un-story-like body still passes the pen — whether it reads as a
        # story is the Reader's verdict, never the pen's (an author writes; the pen
        # carries; the reader grades)
        self.assertEqual(
            pen.validate_story(_story(story="it works. it is done. ship it."), self.BRANCH),
            [])


class TestBodyForm(unittest.TestCase):
    def test_body_is_the_narrative_it_was_handed(self):
        body = pen.compose_body(_story(story="one continuous written thing"))
        self.assertIn("one continuous written thing", body)
        self.assertIn(pen.FOOTER, body)

    def test_no_imposed_shape_survives(self):
        # neither the path-pointer schema nor the field-headers the pen used to stamp
        body = pen.compose_body(_story())
        for ghost in ("## What landed", "## Done-line", "## Report",
                      "**from** —", "**framing** —", "**need** —"):
            self.assertNotIn(ghost, body)

    def test_red_handoff_is_disclosed(self):
        body = pen.compose_body(
            _story(red_reason="two web tests red; scope shrunk per §9.5"))
        self.assertIn("declared-red suite", body)

    def test_green_body_has_no_red_line(self):
        self.assertNotIn("declared-red", pen.compose_body(_story()))

    def test_body_is_deterministic(self):
        self.assertEqual(pen.compose_body(_story()), pen.compose_body(_story()))


class TestMergeSignal(unittest.TestCase):
    """Done-line 0017: a rolling draft says so in its own body, in plain
    words; the flip out of draft is the merge-node eligibility signal."""

    def test_rolling_body_says_not_landable_yet(self):
        body = pen.compose_body(_story(), rolling=True)
        self.assertIn("not landable yet", body)
        self.assertTrue(body.startswith(pen.ROLLING_BANNER))

    def test_final_body_carries_no_banner(self):
        self.assertNotIn("not landable yet", pen.compose_body(_story()))

    def test_banner_states_the_reading_rule(self):
        # the rule the merge-node reads: not-a-draft is eligible after the arc is confirmed
        self.assertIn("merge-node after arc confirmation", pen.ROLLING_BANNER)


class TestBrandedPush(unittest.TestCase):
    """Done-line 0014: the pure refusal rules of the pen's push verb."""

    def test_healthy_session_branch_may_push(self):
        self.assertIsNone(pen.push_refusal("claude/quiet-hopper-ovn8x1", []))

    def test_trunk_is_refused(self):
        for trunk in ("main", "master"):
            self.assertIn("firm", pen.push_refusal(trunk, []))

    def test_detached_head_is_refused(self):
        self.assertIn("detached", pen.push_refusal("", []))

    def test_dead_branch_cannot_strand_commits(self):
        reason = pen.push_refusal("claude/busy-feynman-4hd46k", [6])
        self.assertIn("dead", reason)
        self.assertIn("#6", reason)

    def test_plain_force_does_not_exist_even_forwarded(self):
        for tokens in (["--force"], ["-f"], ["origin", "claude/x", "--force"]):
            self.assertIn("force-with-lease", pen.forward_refusal(tokens))

    def test_forwarding_has_parity_but_never_the_trunk(self):
        # parity: the everyday shapes of git push all pass through
        for tokens in ([], ["--tags"], ["--dry-run"], ["origin", "claude/x"],
                       ["origin", "--delete", "claude/dead-branch"],
                       ["upstream", "HEAD:claude/x"]):
            self.assertIsNone(pen.forward_refusal(tokens), tokens)
        # ...except the trunk, in any spelling
        for tokens in (["origin", "main"], ["origin", "HEAD:main"],
                       ["origin", "--delete", "main"], ["upstream", "master"]):
            self.assertIsNotNone(pen.forward_refusal(tokens), tokens)


class TestIntegrate(unittest.TestCase):
    """Version 0.8.0: a session integrates a piece into an epic branch, never
    main — the trunk stays bdo's (done-line 0029)."""

    def test_main_base_is_refused(self):
        for base in ("main", "master"):
            self.assertIn("bdo", pen.integrate_refusal(base))

    def test_epic_branch_base_is_allowed(self):
        self.assertIsNone(pen.integrate_refusal("claude/epic-experience-layer"))
        self.assertIsNone(pen.integrate_refusal("epic/owner-harness"))


class TestRetire(unittest.TestCase):
    """The retire verb: close a PR without landing it (work already on main,
    superseded, abandoned). The §10 bar — a locally-fine close still refuses
    to fit without a reason a cold reader can read, and a settled PR cannot
    be retired twice."""

    def test_open_pr_with_a_reason_may_retire(self):
        self.assertIsNone(pen.retire_refusal(
            "OPEN", "its content is already on main (folded into #114)"))

    def test_no_reason_refuses(self):
        self.assertIn("reason is required", pen.retire_refusal("OPEN", ""))
        self.assertIn("reason is required", pen.retire_refusal("OPEN", "   "))

    def test_a_pointer_reason_is_not_writing(self):
        # a bare path or numbered ref is homework, not a reason a cold reader reads
        for pointer in (".ai-native/done/0020-x.md", "0118", "`0118`"):
            self.assertIn("pointer", pen.retire_refusal("OPEN", pointer), pointer)

    def test_a_settled_pr_cannot_be_retired(self):
        for state in ("MERGED", "CLOSED"):
            reason = pen.retire_refusal(state, "already on main")
            self.assertIn("only an open PR", reason)
            self.assertIn(state.lower(), reason)


class TestQuotedProse(unittest.TestCase):
    """Caught live: the shame hook read a here-string commit message as
    tool heads. Quoted content is prose, never commands."""

    PS_COMMIT = (
        "git commit -m @'\n"
        "feat: the shame layer — unbranded use surfaces in-context\n\n"
        "Collection alone is silent. The branded pass via audit call.\n"
        "'@; if ($?) { git push origin claude/quiet-hopper-ovn8x1 }"
    )

    def test_here_string_words_are_not_tool_heads(self):
        self.assertEqual(guard.external_bins(self.PS_COMMIT), ["git"])

    def test_heredoc_body_is_invisible(self):
        command = (
            'gh pr edit 8 --body "$(cat <<\'EOF\'\n'
            "the curl of the wave, the ssh of the wind\n"
            'EOF\n)"'
        )
        self.assertEqual(guard.external_bins(command), ["gh"])

    def test_prose_mentioning_a_forbidden_verb_is_not_denied(self):
        # the deny rules must read the acting command, not the message. The
        # vehicle is the git pen — raw `git commit` is itself denied now
        # (done-line 0020), so the pen is the command that legitimately
        # carries a message mentioning gh verbs.
        command = ("python .claude/skills/branch-ritual/git.py commit -m @'\n"
                   "docs: explain why raw gh pr create and gh pr merge are denied\n'@")
        self.assertEqual(guard.external_bins(command), [])
        acting = guard.strip_quoted(command)
        self.assertNotIn("gh pr create", acting)

    def test_cmdlets_are_local_but_network_cmdlets_are_seen(self):
        # caught live: Remove-Item shamed as an external tool
        self.assertEqual(guard.external_bins(
            "Remove-Item -Force x.jsonl -Confirm:$false"), [])
        self.assertEqual(guard.external_bins(
            "Invoke-WebRequest https://example.com"), ["invoke-webrequest"])

    def test_quoted_trunk_word_is_not_a_trunk_push(self):
        self.assertFalse(guard.pushes_to_trunk(
            guard.strip_quoted("git commit -m 'fix the main page'")))
        self.assertTrue(guard.pushes_to_trunk(
            guard.strip_quoted("git push -f origin HEAD:main")))


class TestGuardAndWatcher(unittest.TestCase):
    def setUp(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        self.watch_log = pathlib.Path(path)
        self.addCleanup(self.watch_log.unlink)

    def _invoke(self, command, tool="Bash", session="s1", post=False):
        payload = json.dumps({"session_id": session, "tool_name": tool,
                              "tool_input": {"command": command}})
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        args = [sys.executable, str(GUARD_PATH)] + (["--post"] if post else [])
        return subprocess.run(args, input=payload,
                              capture_output=True, text=True, env=env)

    def _use(self, command, session="s1"):
        """One full watched use: the pre hook logs, the post hook shames."""
        self._invoke(command, session=session)
        return self._invoke(command, session=session, post=True)

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
        self.assertIn("main lands only through the independent merge-node", proc.stderr)

    def test_self_review_denied(self):
        self.assertEqual(self._invoke("gh pr review 9 --approve").returncode, 2)

    def test_raw_ready_flip_denied_toward_the_pen(self):
        # the draft flip IS the merge signal (done-line 0017) — pen only
        for command in ("gh pr ready 10", "gh pr ready 10 --undo"):
            proc = self._invoke(command)
            self.assertEqual(proc.returncode, 2, command)
            self.assertIn("pen", proc.stderr)

    def test_push_to_trunk_denied_in_any_spelling(self):
        for command in ("git push origin main",
                        "git push -f origin HEAD:main",
                        "git push origin --delete main"):
            self.assertEqual(self._invoke(command).returncode, 2, command)

    def test_raw_push_is_denied_toward_the_branded_verb(self):
        # done-line 0014: even the session's own branch goes through the pen
        proc = self._invoke("git push -u origin claude/quiet-hopper-ovn8x1")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("branded push", proc.stderr)
        # rule id is the fence registry's since done-line 0029
        self.assertEqual(self._entries()[0]["rule"], "git-push")

    def test_trunk_push_still_gets_the_firm_message(self):
        proc = self._invoke("git push origin main")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("never push to main", proc.stderr)

    def test_branch_named_like_trunk_is_not_a_trunk_push(self):
        # denied like any raw push, but not with the firm trunk message
        proc = self._invoke("git push origin claude/fix-main-page")
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("never push to main", proc.stderr)

    def test_non_push_git_network_is_still_watched(self):
        proc = self._invoke("git fetch origin")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["bins"], ["git"])

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

    def test_report_splits_mutations_from_reads(self):
        # done-line 0032: a raw read is by-design-raw, not a wrapper
        # candidate; only a raw mutation nominates a wrapper.
        self._invoke("gh pr view 8")                       # read
        self._invoke("curl -X POST https://example.com")   # mutation
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH), "--report"],
            capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0)
        # the mutation is the wrapper candidate; the read is not
        self.assertIn("curl", proc.stdout.split("raw reads")[0])
        self.assertIn("next wrapper", proc.stdout)
        self.assertIn("gh", proc.stdout)            # present, under reads
        self.assertIn("result: report", proc.stdout)

    def test_unbranded_use_is_shamed_into_context(self):
        proc = self._use("gh pr view 8 --json body")
        out = json.loads(proc.stdout)
        context = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("`gh`", context)
        self.assertIn("branded", context)

    def test_shame_fires_once_per_tool_per_session(self):
        self._use("gh pr view 8")
        proc = self._use("gh pr list --state open")
        self.assertEqual(proc.stdout.strip(), "")

    def test_new_session_is_shamed_afresh_with_the_running_count(self):
        self._use("gh pr view 8", session="s1")
        proc = self._use("gh pr list", session="s2")
        context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("`gh` ×2", context)

    def test_local_work_is_never_shamed(self):
        proc = self._use("git status --porcelain")
        self.assertEqual(proc.stdout.strip(), "")

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
