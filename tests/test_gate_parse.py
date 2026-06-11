"""The gate pen's verdict extractor — the brittleness first-light surfaced.

A real mortal mind judged atom.rename-vars.v0 and returned a well-formed
`reject_no_value`, but the pen's original `VERDICT\\s*(\\{.*?\\})` regex never
matched it: the mind didn't emit the bare sentinel, and the non-greedy `.*?`
would truncate a reason that contained a `}`. The verdict was dropped and the
trust-rail issue (#58) was left open. The fix is a brace-matching scan that
captures any well-formed object carrying a string `verdict` key, sentinel or
not — and still prefers the object the mind tagged with VERDICT when it does.

These pin that contract so the parser can't quietly regress to dropping a
verdict the mind actually returned. The pen is loaded by path (it lives under
.claude/skills/, outside the package) and its pure functions are exercised —
no gh, no claude subprocess.
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / ".claude" / "skills" / "gate" / "gate.py"

spec = importlib.util.spec_from_file_location("gate_pen", GATE)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate_pen"] = gate
spec.loader.exec_module(gate)


def _select(text):
    """Mirror launch_claude's selection over the parsed objects, without the
    subprocess: prefer a VERDICT-tagged object, else the last well-formed one."""
    tagged = re.search(r'VERDICT\b[^\{]*(\{)', text, re.DOTALL)
    objs = gate._verdict_objects(text[tagged.start(1):]) if tagged else gate._verdict_objects(text)
    if not objs:
        objs = gate._verdict_objects(text)
    return objs[-1] if objs else None


class TestVerdictExtraction(unittest.TestCase):
    def test_bare_object_without_sentinel(self):
        # the issue-#58 shape: reasoning then a verdict object, no VERDICT word
        text = ('The atom is cosmetic, agent-serving. '
                '{"verdict": "reject_no_value", "reason": "no owner value"}')
        self.assertEqual(_select(text)["verdict"], "reject_no_value")

    def test_brace_inside_reason_does_not_truncate(self):
        # the non-greedy `.*?` bug: a `}` in the reason once cut the object short
        text = ('{"verdict": "amend", "reason": "name the missing piece (e.g. {scope}) here"}')
        v = _select(text)
        self.assertEqual(v["verdict"], "amend")
        self.assertIn("scope", v["reason"])

    def test_markdown_colon_sentinel(self):
        text = 'reasoning\n**VERDICT:** {"verdict": "accept", "reason": "serves a confirmed arc"}'
        self.assertEqual(_select(text)["verdict"], "accept")

    def test_sentinel_skips_the_example_object(self):
        # the prompt shows an example `{"verdict": "<one of ...>"}`; the tagged
        # final object is the real one and must win over the example
        text = ('format: {"verdict": "<one of the terminal verdicts>"}\n'
                'VERDICT {"verdict": "reject_wrong_value", "reason": "wrong seam"}')
        self.assertEqual(_select(text)["verdict"], "reject_wrong_value")

    def test_no_verdict_object_is_none(self):
        self.assertIsNone(_select("the mind rambled and never returned a verdict object"))

    def test_non_verdict_objects_are_ignored(self):
        # objects without a string verdict key are not candidates
        text = '{"note": "thinking"} {"verdict": "accept", "reason": "ok"} {"meta": 1}'
        self.assertEqual(_select(text)["verdict"], "accept")


if __name__ == "__main__":
    unittest.main()
