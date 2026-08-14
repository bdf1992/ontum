"""§10 for the tool-scout skill pen (.claude/skills/tool-scout/scout.py).

No done-line: this skill was built to bdo's 15-minute window (2026-08-14),
not the full blueprint-before-build ritual — named honestly in the session
report rather than backfilling a done-line that wasn't written first (§9.4).

The teeth: an independent review (PR #751) caught that META_DESC_RE /
META_NAME_RE, when pulling a workflow's meta.name/description out of a .js
file, stopped at the first backslash-escaped quote inside the string literal
instead of the real closing quote — silently truncating any description
containing an escaped apostrophe (this repo's own tend-heal.js has one:
"...the heal stays bdo\'s, D-4)"). test_workflow_description_survives_an_
escaped_quote reproduces that exact failure mode against a fixture and would
have caught the bug before merge, per the reviewer's own suggested fix.
"""

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCOUT_PATH = REPO_ROOT / ".claude" / "skills" / "tool-scout" / "scout.py"

_spec = importlib.util.spec_from_file_location("tool_scout_scout", SCOUT_PATH)
scout = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scout)


def make_repo(tmp):
    root = pathlib.Path(tmp)
    (root / ".claude" / "skills" / "demo-skill").mkdir(parents=True)
    (root / ".claude" / "skills" / "demo-skill" / "SKILL.md").write_text(
        "---\n"
        "name: demo-skill\n"
        "description: >-\n"
        "  Finds the widget. Use when asked to find a widget or locate\n"
        "  a gadget.\n"
        "version: 0.1.0\n"
        "---\n\n# demo-skill\n",
        encoding="utf-8",
    )
    (root / ".claude" / "workflows").mkdir(parents=True)
    (root / ".claude" / "workflows" / "widget-finder.js").write_text(
        "export const meta = {\n"
        "  name: 'widget-finder',\n"
        "  description: 'Finds a widget — the heal stays bdo\\'s, D-4).',\n"
        "}\n",
        encoding="utf-8",
    )
    (root / "loop").mkdir(parents=True)
    (root / "loop" / "CLAUDE.md").write_text(
        "# loop/\n\n```sh\n"
        "python -m loop.widget --status   # read-only widget summary\n"
        "```\n",
        encoding="utf-8",
    )
    return root


class TestSources(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = make_repo(self._tmp.name)

    def test_skill_frontmatter_parses_name_and_folded_description(self):
        items = scout.index_repo_skills(str(self.root))
        self.assertEqual(len(items), 1)
        it = items[0]
        self.assertEqual(it["kind"], "skill")
        self.assertEqual(it["name"], "demo-skill")
        self.assertIn("widget", it["description"])
        self.assertIn("gadget", it["description"])

    def test_workflow_description_survives_an_escaped_quote(self):
        # the exact failure mode PR #751's review caught: a backslash-escaped
        # apostrophe inside the JS string used to cut the match short.
        items = scout.index_repo_workflows(str(self.root))
        self.assertEqual(len(items), 1)
        it = items[0]
        self.assertEqual(it["kind"], "workflow")
        self.assertEqual(it["name"], "widget-finder")
        self.assertEqual(it["description"], "Finds a widget — the heal stays bdo's, D-4).")

    def test_loop_command_description_is_the_inline_comment(self):
        items = scout.index_loop_commands(str(self.root))
        self.assertEqual(len(items), 1)
        it = items[0]
        self.assertEqual(it["kind"], "loop")
        self.assertIn("python -m loop.widget --status", it["name"])
        self.assertEqual(it["description"], "read-only widget summary")

    def test_search_ranks_by_token_overlap(self):
        items = (
            scout.index_repo_skills(str(self.root))
            + scout.index_repo_workflows(str(self.root))
            + scout.index_loop_commands(str(self.root))
        )
        results = scout.search("widget", items, top=10)
        self.assertEqual(len(results), 3)
        results_none = scout.search("nonexistent zzz", items, top=10)
        self.assertEqual(results_none, [])

    def test_index_never_writes_or_executes(self):
        # a pure fold: same inputs, same outputs, no state left behind
        before = sorted(p.name for p in self.root.rglob("*"))
        scout.build_index([str(self.root)], {"skill", "workflow", "loop"})
        after = sorted(p.name for p in self.root.rglob("*"))
        self.assertEqual(before, after)


class TestCLI(unittest.TestCase):
    def test_json_output_is_valid_and_stable_shape(self):
        proc = subprocess.run(
            [sys.executable, str(SCOUT_PATH), "git", "--kind", "path",
             "--json", "--top", "3"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["query"], "git")
        for item in data["results"]:
            self.assertEqual(set(item), {"kind", "name", "description", "source"})

    def test_no_matches_names_what_was_indexed_not_a_universal_absence(self):
        proc = subprocess.run(
            [sys.executable, str(SCOUT_PATH), "qqqxyznomatch12345",
             "--kind", "path"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("no matches", proc.stdout)
        self.assertIn("unattached repos", proc.stdout)


if __name__ == "__main__":
    unittest.main()
