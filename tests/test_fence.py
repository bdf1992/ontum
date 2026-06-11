"""The fence registry holds its seams (done-line 0027).

Three directions of refusal, so neither surface can drift alone:

1. registry <-> command_guard behavior: every forbidden rule's match
   examples are denied by the live Claude guard (subprocess, exit 2),
   its not_match examples pass; the claude_guard cross-references cover
   the guard's whole deny-list, both ways.
2. registry <-> rendered bytes: the committed .codex/ layer equals a
   fresh render — a registry edit without a re-render fails here.
3. examples <-> prefix semantics: each rule's own match/not_match
   examples fit (or refuse to fit) its argv prefix under the documented
   Codex matching rules.
"""

import json
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fence import policy, render_codex  # noqa: E402

GUARD = ROOT / ".claude" / "hooks" / "command_guard.py"
sys.path.insert(0, str(GUARD.parent))
import command_guard  # noqa: E402

FORBIDDEN = [r for r in policy.RULES if r["decision"] == "forbidden"]
PROMPT = [r for r in policy.RULES if r["decision"] == "prompt"]


def run_guard(command, watch_log):
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test-fence",
    })
    env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(watch_log))
    return subprocess.run(
        [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
        capture_output=True, env=env,
    )


class RegistryShape(unittest.TestCase):
    def test_every_rule_carries_its_story(self):
        for rule in policy.RULES:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["decision"], ("forbidden", "prompt"))
                self.assertTrue(rule["justification"].strip())
                self.assertTrue(rule["match"], "a rule proves itself "
                                "with at least one match example")
                self.assertTrue(rule["not_match"])

    def test_examples_fit_their_rule(self):
        for rule in policy.RULES:
            for example in rule["match"]:
                with self.subTest(rule=rule["id"], example=example):
                    self.assertTrue(policy.prefix_matches(
                        shlex.split(example), rule["argv"]))
            for example in rule["not_match"]:
                with self.subTest(rule=rule["id"], example=example):
                    self.assertFalse(policy.prefix_matches(
                        shlex.split(example), rule["argv"]))


class ClaudeParity(unittest.TestCase):
    """The two surfaces refuse the same things — drift fails here."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.watch_log = pathlib.Path(self.tmp.name) / "watch.jsonl"
        self.addCleanup(self.tmp.cleanup)

    def test_forbidden_examples_are_denied_by_claude_guard(self):
        for rule in FORBIDDEN:
            for example in rule["match"]:
                with self.subTest(rule=rule["id"], example=example):
                    proc = run_guard(example, self.watch_log)
                    self.assertEqual(
                        proc.returncode, 2,
                        f"command_guard let through what the registry "
                        f"forbids: {example!r} ({proc.stderr.decode()})")

    def test_not_match_examples_pass_claude_guard(self):
        for rule in policy.RULES:
            for example in rule["not_match"]:
                with self.subTest(rule=rule["id"], example=example):
                    proc = run_guard(example, self.watch_log)
                    self.assertEqual(
                        proc.returncode, 0,
                        f"command_guard denies what the registry treats "
                        f"as outside the rule: {example!r}")

    def test_registry_covers_the_whole_claude_deny_list(self):
        # the two push rules live in command_guard's hook body, not its
        # DENY_RULES table; they are part of the deny surface all the same
        claude_ids = {rule for rule, _, _ in command_guard.DENY_RULES}
        claude_ids |= {"git-push-raw", "git-push-trunk"}
        mirrored = {gid for r in policy.RULES for gid in r["claude_guard"]}
        self.assertEqual(
            mirrored, claude_ids,
            "the deny-lists drifted: a rule was added on one surface "
            "without its twin (fence/policy.py <-> command_guard.py)")

    def test_prompt_rules_are_at_least_watched_by_claude(self):
        for rule in PROMPT:
            with self.subTest(rule=rule["id"]):
                self.assertEqual(rule["argv"][0], "git")
                self.assertIn(rule["argv"][1], command_guard.GIT_MUTATING)


class RenderedSurface(unittest.TestCase):
    """The committed .codex/ layer is exactly what the registry says."""

    @staticmethod
    def _disk(path):
        return path.read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_rules_file_is_fresh(self):
        self.assertEqual(self._disk(render_codex.RULES_OUT),
                         render_codex.render_rules(),
                         "stale render: python fence/render_codex.py")

    def test_hooks_file_is_fresh(self):
        self.assertEqual(self._disk(render_codex.HOOKS_OUT),
                         render_codex.render_hooks(),
                         "stale render: python fence/render_codex.py")

    def test_rendered_rules_are_ascii(self):
        # Starlark escape support beyond ASCII is not guaranteed in the
        # rules engine; the renderer must stay 7-bit clean
        render_codex.render_rules().encode("ascii")

    def test_union_elements_render_as_starlark_lists(self):
        self.assertIn('["gh", "pr", ["close", "reopen"]]',
                      render_codex.render_rules())

    def test_hooks_carry_only_the_summon(self):
        hooks = json.loads(render_codex.render_hooks())["hooks"]
        commands = [h["command"]
                    for groups in hooks.values()
                    for group in groups
                    for h in group["hooks"]]
        self.assertTrue(commands)
        self.assertEqual(set(commands), {"python -m loop.summon --hook"},
                         "the Codex hook surface is read-only by design "
                         "(D-10): only the summons briefing runs")


if __name__ == "__main__":
    unittest.main()
