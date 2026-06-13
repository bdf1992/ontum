"""Done-line 0026: the branded spawn rail gates a node-spawn.

The §10 case for spawns: a branded node-spawn of value-gate.claude.v1 is denied
while branded-subagent holds no judge rung, and permitted once it does; an
unbranded helper passes (watched), and a headless `claude` invocation is seen.
Pure parsing and the refusal are hit directly; the hook runs as a real
subprocess fed PreToolUse JSON, the watch log pointed at a temp file.
"""

import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUARD = ROOT / ".claude" / "hooks" / "spawn_guard.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


spawn = _load("spawn_guard", GUARD)


class TestParsing(unittest.TestCase):
    def test_brand_read_from_prompt(self):
        self.assertEqual(
            spawn.brand_of({"prompt": "do the thing\nontum-node: value-gate.claude.v1\n"}),
            "value-gate.claude.v1")

    def test_unbranded_is_none(self):
        self.assertIsNone(spawn.brand_of({"prompt": "just explore the repo"}))

    def test_headless_claude_detected(self):
        self.assertTrue(spawn.is_headless_claude("claude -p 'judge this'"))
        self.assertTrue(spawn.is_headless_claude("claude --version"))

    def test_a_dotclaude_path_is_not_headless(self):
        self.assertFalse(spawn.is_headless_claude("python .claude/hooks/x.py"))
        self.assertFalse(spawn.is_headless_claude("echo claude is great"))


class TestUnbrandedNodeActDenied(unittest.TestCase):
    """The prevention half (2026-06-13): an unbranded spawn that performs a
    node-only act is refused — the accident where a session filled the merge-node
    seat with a plain Agent. A node-fill must claim a node identity to reach the
    land/judge pens; a plain helper never does, so the deny is surgical."""

    def test_unbranded_merge_node_land_is_refused(self):
        # the exact accident: spawn instructed to run `pr.py land ... --by
        # merge-node.claude.v1`, no brand.
        reason = spawn.unbranded_nodeact_refusal({"prompt":
            "be the merge-node and land PR 115:\n"
            "python .claude/skills/branch-ritual/pr.py land --epic epic.x "
            "--by merge-node.claude.v1 115"})
        self.assertIsNotNone(reason)
        self.assertIn("ontum-node:", reason)

    def test_unbranded_gate_judge_is_refused(self):
        self.assertIsNotNone(spawn.unbranded_nodeact_refusal(
            {"prompt": "run python -m loop.node judge --node value-gate.claude.v1"}))

    def test_a_branded_node_act_is_not_refused_here(self):
        # branded -> this refusal stands down; node_spawn_refusal governs it.
        self.assertIsNone(spawn.unbranded_nodeact_refusal(
            {"prompt": "ontum-node: merge-node.claude.v1\n"
                       "pr.py land --epic epic.x --by merge-node.claude.v1 115"}))

    def test_a_plain_helper_spawn_passes(self):
        # the false-positive guard: a research spawn that touches none of the
        # node-only verbs is not a node-fill and must not be denied.
        self.assertIsNone(spawn.unbranded_nodeact_refusal(
            {"prompt": "explore the repo and summarise how the gateway folds the log"}))

    def test_by_bdo_is_not_a_node_identity(self):
        # `--by bdo` is the owner stamping a pen directly, not a node-fill — it
        # must not trip the node-identity signal (no `.<class>.v<n>`).
        self.assertIsNone(spawn.node_act_of(
            {"prompt": "register a mind: loop.minds register --backing env:X --by bdo"}))


class TestRefusalAgainstRepo(unittest.TestCase):
    """The refusal half, hermetic: a pinnable node on an empty ladder is
    refused for want of a rung (a temp root, so bdo's live grants — #89/#91,
    2026-06-12 — can't silently un-test the deny), and against the real
    records a node with no prompt cannot be pinned."""

    def test_real_node_without_rung_is_refused(self):
        ai = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        (ai / "nodes").mkdir()
        (ai / "log").mkdir()
        (ai / "nodes" / "demo.node.v1.md").write_text("# demo node prompt", encoding="utf-8")
        (ai / "log" / "admissions.jsonl").write_text("", encoding="utf-8")
        reason = spawn.node_spawn_refusal("demo.node.v1", root=ai)
        self.assertIsNotNone(reason)
        self.assertIn("rung", reason)

    def test_unknown_node_has_no_prompt_to_pin(self):
        reason = spawn.node_spawn_refusal("no.such.node.v9")
        self.assertIsNotNone(reason)
        self.assertIn("no versioned prompt", reason)


class TestPermittedOnceGranted(unittest.TestCase):
    """Give the class its rung and a pinnable prompt in a temp records root —
    the same spawn now passes."""

    def test_granted_rung_permits_a_pinned_node(self):
        ai = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        (ai / "nodes").mkdir()
        (ai / "log").mkdir()
        (ai / "nodes" / "demo.node.v1.md").write_text("# demo node prompt", encoding="utf-8")
        rung = {"type": "trust_rung", "agent_class": "branded-subagent",
                "capability": "judge", "by": "bdo", "id": "adm.test", "ts": "t"}
        (ai / "log" / "admissions.jsonl").write_text(json.dumps(rung) + "\n", encoding="utf-8")
        self.assertIsNone(spawn.node_spawn_refusal("demo.node.v1", root=ai))


class TestHook(unittest.TestCase):
    def setUp(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        self.watch_log = pathlib.Path(path)
        self.addCleanup(self.watch_log.unlink)

    def _invoke(self, payload, post=False):
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.watch_log))
        args = [sys.executable, str(GUARD)] + (["--post"] if post else [])
        return subprocess.run(args, input=json.dumps(payload),
                              capture_output=True, text=True, env=env)

    def _entries(self):
        text = self.watch_log.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_unbranded_agent_passes_and_is_watched(self):
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"prompt": "explore the repo"}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["status"], "spawn-unbranded")

    def test_branded_spawn_of_unpinnable_node_denied(self):
        # The hook reads the live records, where bdo granted the judge rungs
        # (#89/#91) — so the rung-deny is pinned hermetically above, and the
        # hook's deny path is exercised by what still cannot pass: a node
        # with no versioned prompt to pin.
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"prompt": "ontum-node: no.such.node.v9\njudge it"}})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("no versioned prompt", proc.stderr)
        self.assertEqual(self._entries()[0]["status"], "spawn-denied")
        self.assertEqual(self._entries()[0]["node"], "no.such.node.v9")

    def test_branded_spawn_of_granted_node_permits_and_pins(self):
        # The stronger truth after bdo's grants: a branded spawn of a real,
        # prompt-pinned node passes, and the rail records the prompt hash.
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"prompt": "ontum-node: value-gate.claude.v1\njudge it"}})
        self.assertEqual(proc.returncode, 0)
        entry = self._entries()[0]
        self.assertEqual(entry["status"], "spawn")
        self.assertEqual(entry["node"], "value-gate.claude.v1")
        self.assertTrue(entry["prompt_hash"])

    def test_unbranded_node_fill_spawn_is_denied_by_the_hook(self):
        # the accident, end to end: the live PreToolUse hook refuses an
        # unbranded merge-node spawn (exit 2) and names the brand it needs.
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"description": "land PR 115",
                                            "prompt": "pr.py land --epic epic.x "
                                            "--by merge-node.claude.v1 115"}})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("ontum-node:", proc.stderr)
        self.assertEqual(self._entries()[0]["status"], "spawn-denied-unbranded")

    def test_plain_helper_agent_still_passes_the_hook(self):
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"prompt": "search for the term economy doc"}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["status"], "spawn-unbranded")

    def test_headless_claude_is_a_spawn(self):
        proc = self._invoke({"tool_name": "Bash", "session_id": "s1",
                             "tool_input": {"command": "claude -p 'go'"}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries()[0]["kind"], "headless")

    def test_a_plain_shell_command_is_not_a_spawn(self):
        proc = self._invoke({"tool_name": "Bash", "session_id": "s1",
                             "tool_input": {"command": "echo hello"}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._entries(), [])

    def test_post_shames_an_unbranded_spawn_once(self):
        proc = self._invoke({"tool_name": "Agent", "session_id": "s1",
                             "tool_input": {"prompt": "explore"}}, post=True)
        ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("unbranded spawn", ctx)


if __name__ == "__main__":
    unittest.main()
