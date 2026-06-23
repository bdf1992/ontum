"""The fence registry holds its seams (done-lines 0027, 0029).

Parity between the surfaces is structural — command_guard derives its
deny-list from the registry — so what's left to refuse is behavior and
freshness:

1. registry <-> command_guard behavior: every forbidden rule's match
   examples are denied by the live Claude guard (subprocess, exit 2),
   its not_match examples pass; the derived table is exactly the
   registry's forbidden rows; a registry that can't load degrades
   loudly, never silently.
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

    def test_claude_deny_list_is_the_registry(self):
        # structural parity (done-line 0029): the guard's table is a
        # derivation, not a twin — ids and messages come from the registry
        derived = {(rid, msg) for rid, _, msg in command_guard.DENY_RULES}
        expected = {(r["id"], r["justification"]) for r in FORBIDDEN}
        self.assertEqual(derived, expected)

    def test_degraded_fence_is_loud_not_silent(self):
        # _deny_rules() under a broken registry: empty list, a degraded
        # entry on the watch log — never an exception, never quiet
        import unittest.mock as mock
        recorded = []
        with mock.patch.object(command_guard, "record", recorded.append), \
             mock.patch.dict(sys.modules, {"fence": None}):
            rules = command_guard._deny_rules()
        self.assertEqual(rules, ())
        self.assertEqual([e["status"] for e in recorded], ["degraded"])

    def test_prompt_rules_are_at_least_watched_by_claude(self):
        # A prompt rule is not denied by the Claude guard — only `forbidden`
        # rows compile into DENY_RULES. Its teeth are on the Codex surface
        # (it prompts) and the registry record. The invariant that keeps a
        # prompt rule honest on the Claude side is that the guard at least
        # *watches* its surface, so the act is never invisible: a git verb
        # the watcher tracks (GIT_MUTATING), or a non-local external head
        # (gh, ...) external_bins always records.
        for rule in PROMPT:
            head = rule["argv"][0]
            with self.subTest(rule=rule["id"]):
                if head == "git":
                    verbs = rule["argv"][1]
                    verbs = verbs if isinstance(verbs, tuple) else (verbs,)
                    for verb in verbs:
                        self.assertIn(
                            verb, command_guard.GIT_MUTATING,
                            f"{rule['id']}: git prompt rule names a verb the "
                            f"watcher does not track: {verb}")
                else:
                    self.assertNotIn(head, command_guard.LOCAL_HEADS)
                    self.assertTrue(
                        command_guard.external_bins(rule["match"][0]),
                        f"{rule['id']}: prompt-rule surface {head!r} is not "
                        "watched by the guard")


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

    def test_hooks_carry_only_summon_heartbeat_and_probe(self):
        hooks = json.loads(render_codex.render_hooks())["hooks"]
        commands = [h["command"]
                    for groups in hooks.values()
                    for group in groups
                    for h in group["hooks"]]
        self.assertTrue(commands)
        for command in commands:
            self.assertTrue(
                command == "python -m loop.summon --hook"
                or command == "python -m loop.heartbeat --hook"
                or command.startswith("python fence/probe_codex.py "),
                f"unexpected hook command: {command!r} — the Codex hook "
                "surface carries only the safe heartbeat tick, the summons "
                "briefing, and the seam probe")

    def test_session_start_runs_heartbeat_before_summon(self):
        hooks = json.loads(render_codex.render_hooks())["hooks"]
        commands = [h["command"]
                    for group in hooks["SessionStart"]
                    for h in group["hooks"]]
        self.assertEqual(commands[:2], [
            "python -m loop.heartbeat --hook",
            "python -m loop.summon --hook",
        ])

    def test_probe_events_cover_the_tool_seam(self):
        hooks = json.loads(render_codex.render_hooks())["hooks"]
        probed = {event for event, groups in hooks.items()
                  for group in groups for h in group["hooks"]
                  if h["command"].startswith("python fence/probe_codex.py")}
        self.assertEqual(
            probed, {"PreToolUse", "PostToolUse", "PermissionRequest"},
            "the probe observes exactly the seams the watcher and the "
            "apply_patch guard will be designed against (done-line 0029)")


if __name__ == "__main__":
    unittest.main()
