"""§10 teeth for loop/rename.py — the rename ledger + deterministic applier.

The test proves the pen is NOT vacuous in both directions: a bare prose word IS
renamed (and its article repaired), and a compound (identifier / filename /
handle) is NOT — a dumb global replace would fail half of these. It also proves
the phrasing-door gate refuses a rename that would touch a code token, and that
the walk excludes the record trees.
"""
import io
import tempfile
import types
import unittest
from pathlib import Path

from loop import rename
from loop.phrasing import phrasing_only

R = [("organ", "part"), ("metabolism", "cycle")]


class RenameText(unittest.TestCase):
    def test_bare_word_is_renamed_with_case(self):
        self.assertEqual(rename.rename_text("the organ", R), "the part")
        self.assertEqual(rename.rename_text("The Organ", R), "The Part")
        self.assertEqual(rename.rename_text("an ORGAN here", R), "a PART here")

    def test_plural(self):
        self.assertEqual(rename.rename_text("two organs", R), "two parts")
        self.assertEqual(rename.rename_text("the metabolism", R), "the cycle")

    def test_article_fixed_when_renaming(self):
        # organ (vowel) -> part (consonant): "an" must become "a", not "an part"
        self.assertEqual(rename.rename_text("an organ", R), "a part")
        self.assertNotIn("an part", rename.rename_text("an organ census-like", R))

    def test_article_repaired_even_with_no_source_word(self):
        # the propagation of the fix: a PRIOR sloppy rename's "an part" is healed
        # wherever it sits, with no "organ" left to match.
        self.assertEqual(rename.rename_text("made an part", R), "made a part")
        self.assertEqual(rename.rename_text("An part senses", R), "A part senses")

    def test_compounds_are_preserved(self):
        # identifiers, filenames, dotted/hyphened handles — never touched
        for token in ("organ_gaps", "find_organs", "ORGAN_GLOBS",
                      "strategy-metabolism.md", "epic.test-metabolism",
                      "the-metabolism", "four-organ"):
            self.assertEqual(rename.rename_text(token, R), token,
                             f"{token!r} must be preserved (it is a compound)")

    def test_sentence_period_renamed_but_dotted_compound_preserved(self):
        # a trailing period is sentence punctuation -> rename through it
        self.assertEqual(rename.rename_text("see the organ. Then", R),
                         "see the part. Then")
        self.assertEqual(rename.rename_text("the harness's metabolism.", R),
                         "the harness's cycle.")
        # a dotted compound is PRESERVED — the pen cannot tell attribute access
        # (organs.append) from a handle (metabolism.md), so it conservatively
        # leaves all `word.word`; this is exactly why census.py's wholesale
        # identifier rename uses plain \b instead of the pen.
        self.assertEqual(rename.rename_text("organs.append(x)", R),
                         "organs.append(x)")
        self.assertEqual(rename.rename_text("metabolism.md", R), "metabolism.md")
        self.assertEqual(rename.rename_text("organ.py here", R), "organ.py here")

    def test_idempotent(self):
        text = "an organ and two organs in the metabolism; see strategy-metabolism.md"
        once = rename.rename_text(text, R)
        self.assertEqual(once, rename.rename_text(once, R))
        self.assertNotIn(" organ", once)   # the bare words are gone
        self.assertIn("strategy-metabolism.md", once)  # the handle survived


class PhrasingGate(unittest.TestCase):
    def test_code_touching_rename_is_refused_by_the_door(self):
        # census.py-class damage: a bare identifier `organs` would be rewritten,
        # but the phrasing door must catch it as a CODE change (so apply skips it).
        before = "organs = []\nx = 1\n"
        after = rename.rename_text(before, R)
        self.assertEqual(after, "parts = []\nx = 1\n")  # the swap happens...
        ok, why = phrasing_only("loop/census.py", before, after)
        self.assertFalse(ok)  # ...but the gate refuses it: that is code, not prose
        self.assertIsNotNone(why)

    def test_prose_in_comment_passes_the_door(self):
        before = "# the organ census\nx = 1\n"
        after = rename.rename_text(before, R)
        self.assertEqual(after, "# the part census\nx = 1\n")
        ok, _ = phrasing_only("loop/x.py", before, after)
        self.assertTrue(ok)


class Ledger(unittest.TestCase):
    def _fold(self, *adms):
        return types.SimpleNamespace(admissions=list(adms))

    def test_admitted_renames_latest_wins_and_withdraw_drops(self):
        f = self._fold(
            {"type": "rename", "from": "organ", "to": "ORGANELLE"},
            {"type": "rename", "from": "organ", "to": "part"},          # supersedes
            {"type": "rename", "from": "metabolism", "to": "cycle"},
            {"type": "rename", "from": "metabolism", "to": "cycle", "withdrawn": True},
        )
        rules = rename.admitted_renames(f)
        self.assertIn(("organ", "part"), rules)
        self.assertNotIn(("organ", "ORGANELLE"), rules)
        self.assertNotIn(("metabolism", "cycle"), rules)  # withdrawn

    def test_non_rename_admissions_ignored(self):
        self.assertEqual(rename.admitted_renames(self._fold({"type": "tag"})), [])


class Scope(unittest.TestCase):
    def test_excludes_record_trees_and_artifacts(self):
        self.assertFalse(rename._in_scope(".ai-native/log/events.jsonl"))
        self.assertFalse(rename._in_scope(".ai-native/done/0001-x.md"))
        self.assertFalse(rename._in_scope("docs/phase-2/x.md"))
        self.assertFalse(rename._in_scope("exports/qa-metabolism/01-arc.md"))
        self.assertFalse(rename._in_scope(".claude/worktrees/agent-x/loop/y.py"))
        self.assertFalse(rename._in_scope("loop/rename.py"))  # self-referential
        self.assertTrue(rename._in_scope("loop/heal.py"))
        self.assertTrue(rename._in_scope("README.md"))

    def test_scan_splits_clean_from_code_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "loop").mkdir()
            (repo / ".ai-native" / "log").mkdir(parents=True)
            (repo / "doc.md").write_text("an organ here\n", encoding="utf-8")
            (repo / "loop" / "code.py").write_text("organs = []\n", encoding="utf-8")
            (repo / ".ai-native" / "log" / "x.jsonl").write_text(
                '{"organ": 1}\n', encoding="utf-8")  # excluded tree
            clean, flagged, _ = rename.scan(repo, R)
            self.assertIn("doc.md", clean)
            self.assertIn("loop/code.py", [p for p, _ in flagged])
            self.assertNotIn(".ai-native/log/x.jsonl", clean)


if __name__ == "__main__":
    unittest.main()
