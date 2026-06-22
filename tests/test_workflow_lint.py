"""§10 teeth for the authoring bench's draft check (A2).

The check earns its place only if it is non-vacuous: the real worked example
must PASS, and each kind of fabricated defect must be REFUSED with a named
problem. A constant `ok = True` would fail this suite.
"""

import importlib.util
import pathlib
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
LINT_PATH = REPO / ".claude" / "skills" / "author-workflow" / "lint.py"
EXAMPLE = REPO / ".claude" / "workflows" / "subsystem-map.js"

_spec = importlib.util.spec_from_file_location("workflow_lint", LINT_PATH)
lint_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_mod)
lint = lint_mod.lint


def _lint_source(slug, source):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / f"{slug}.js"
        p.write_text(source, encoding="utf-8")
        return lint(str(p))


GOOD = """export const meta = {
  name: 'demo',
  description: 'Read-only demo.',
  phases: [{ title: 'Go', detail: 'do it' }],
}
phase('Go')
const r = await agent('do the thing')
return r
"""


class WorkflowLintTeeth(unittest.TestCase):
    def test_real_worked_example_passes(self):
        # the committed worked example must be a clean draft
        r = lint(str(EXAMPLE))
        self.assertTrue(r["ok"], msg=f"worked example refused: {r['problems']}")
        self.assertEqual(r["meta"]["name"], "subsystem-map")
        # it is read-only; its "No mutation." description must not flag it
        self.assertFalse(r["flags"]["mutates"])

    def test_a_clean_minimal_draft_passes(self):
        r = _lint_source("demo", GOOD)
        self.assertTrue(r["ok"], msg=r["problems"])

    def test_missing_meta_is_refused(self):
        r = _lint_source("demo", "phase('Go')\nawait agent('x')\n")
        self.assertFalse(r["ok"])
        self.assertTrue(any("meta" in p for p in r["problems"]))

    def test_name_slug_mismatch_is_refused(self):
        r = _lint_source("other-name", GOOD)  # meta.name='demo' != slug
        self.assertFalse(r["ok"])
        self.assertTrue(any("file slug" in p for p in r["problems"]))

    def test_interpolated_meta_is_refused(self):
        bad = GOOD.replace("'Read-only demo.'", "`Read-only ${x} demo.`")
        r = _lint_source("demo", bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("interpolation" in p for p in r["problems"]))

    def test_call_expression_in_meta_is_refused(self):
        bad = GOOD.replace("'Read-only demo.'", "buildDesc()")
        r = _lint_source("demo", bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("call expression" in p for p in r["problems"]))

    def test_missing_phases_key_is_refused(self):
        bad = GOOD.replace(
            "  phases: [{ title: 'Go', detail: 'do it' }],\n", "")
        r = _lint_source("demo", bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("phases" in p for p in r["problems"]))

    def test_no_primitive_is_refused(self):
        bad = """export const meta = {
  name: 'demo',
  description: 'inert.',
  phases: [{ title: 'Go' }],
}
const x = 1
return x
"""
        r = _lint_source("demo", bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("primitive" in p for p in r["problems"]))

    def test_mutation_is_flagged_not_failed(self):
        mut = """export const meta = {
  name: 'demo',
  description: 'edits files.',
  phases: [{ title: 'Go', detail: 'x' }],
}
phase('Go')
await agent('Edit the file and commit', { isolation: 'worktree' })
"""
        r = _lint_source("demo", mut)
        self.assertTrue(r["ok"], msg=r["problems"])  # well-formed
        self.assertTrue(r["flags"]["mutates"])       # but flagged for review


if __name__ == "__main__":
    unittest.main()
