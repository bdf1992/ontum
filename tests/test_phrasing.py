"""§10 teeth for the phrasing backdoor (done-line 0117).

The test that matters: a pedantic prose edit across all three file kinds is
accepted and the off-log gate calls its branch backed with NO atom; a code
token, a renamed/added JSON key, and a changed id/verdict value are each
REFUSED and the gate still calls that branch an off-log orphan. A fabricated
or constant-true checker cannot pass both halves — that is the bite.
"""
import unittest

from loop import phrasing
from loop import pr_audit


class TestMarkdownDoor(unittest.TestCase):
    def test_body_prose_change_is_phrasing(self):
        before = "---\nname: arc-intake\nversion: 0.1.1\n---\n\nbdo steers from GitHub on his phone.\n"
        after = "---\nname: arc-intake\nversion: 0.1.1\n---\n\nbdo steers from GitHub, wherever he is.\n"
        ok, why = phrasing.phrasing_only("a/SKILL.md", before, after)
        self.assertTrue(ok, why)

    def test_no_frontmatter_body_free(self):
        ok, _ = phrasing.phrasing_only("README.md", "the phone.\n", "any device.\n")
        self.assertTrue(ok)

    def test_changing_name_refuses(self):
        before = "---\nname: arc-intake\nversion: 0.1.1\n---\nbody\n"
        after = "---\nname: renamed\nversion: 0.1.1\n---\nbody\n"
        ok, why = phrasing.phrasing_only("a/SKILL.md", before, after)
        self.assertFalse(ok)
        self.assertIn("name", why)

    def test_changing_version_refuses(self):
        before = "---\nname: a\nversion: 0.1.0\n---\nbody\n"
        after = "---\nname: a\nversion: 0.2.0\n---\nbody\n"
        ok, why = phrasing.phrasing_only("a/SKILL.md", before, after)
        self.assertFalse(ok)

    def test_adding_frontmatter_key_refuses(self):
        before = "---\nname: a\nversion: 1\n---\nbody\n"
        after = "---\nname: a\nversion: 1\nmodel: opus\n---\nbody\n"
        ok, why = phrasing.phrasing_only("a/SKILL.md", before, after)
        self.assertFalse(ok)
        self.assertIn("key", why)


class TestPythonDoor(unittest.TestCase):
    def test_docstring_change_is_phrasing(self):
        before = 'def f():\n    """from GitHub on his phone."""\n    return 1\n'
        after = 'def f():\n    """from GitHub, wherever he is."""\n    return 1\n'
        ok, why = phrasing.phrasing_only("m.py", before, after)
        self.assertTrue(ok, why)

    def test_comment_change_is_phrasing(self):
        before = "x = 1  # on his phone\n"
        after = "x = 1  # on any device\n"
        ok, why = phrasing.phrasing_only("m.py", before, after)
        self.assertTrue(ok, why)

    def test_code_token_change_refuses(self):
        before = "x = 1  # note\n"
        after = "x = 2  # note\n"
        ok, why = phrasing.phrasing_only("m.py", before, after)
        self.assertFalse(ok)
        self.assertIn("code", why)

    def test_added_code_line_refuses(self):
        before = 'def f():\n    """doc"""\n    return 1\n'
        after = 'def f():\n    """doc"""\n    y = 5\n    return 1\n'
        ok, why = phrasing.phrasing_only("m.py", before, after)
        self.assertFalse(ok)

    def test_renaming_identifier_in_code_refuses(self):
        before = "value = compute()\n"
        after = "result = compute()\n"
        ok, why = phrasing.phrasing_only("m.py", before, after)
        self.assertFalse(ok)


class TestJsonDoor(unittest.TestCase):
    def test_prose_field_value_change_is_phrasing(self):
        before = '{"epic": {"id": "e", "horizon": "open it on your phone"}}'
        after = '{"epic": {"id": "e", "horizon": "open it from any device"}}'
        ok, why = phrasing.phrasing_only("e.json", before, after)
        self.assertTrue(ok, why)

    def test_glue_in_list_is_phrasing(self):
        before = '{"pieces": [{"atom": "a.v0", "glue": "on his phone"}]}'
        after = '{"pieces": [{"atom": "a.v0", "glue": "anywhere"}]}'
        ok, why = phrasing.phrasing_only("e.json", before, after)
        self.assertTrue(ok, why)

    def test_renaming_key_refuses(self):
        before = '{"horizon": "x"}'
        after = '{"vision": "x"}'
        ok, why = phrasing.phrasing_only("e.json", before, after)
        self.assertFalse(ok)
        self.assertIn("key", why)

    def test_non_prose_string_value_refuses(self):
        # an id is a string but NOT a prose field — must be byte-identical
        before = '{"id": "atom.v0", "value": "prose"}'
        after = '{"id": "atom.v1", "value": "prose"}'
        ok, why = phrasing.phrasing_only("e.json", before, after)
        self.assertFalse(ok)

    def test_verdict_value_refuses(self):
        before = '{"verdict": "accept", "value": "x"}'
        after = '{"verdict": "refuse", "value": "x"}'
        ok, why = phrasing.phrasing_only("r.json", before, after)
        self.assertFalse(ok)

    def test_number_value_refuses(self):
        before = '{"value": "x", "cap": 8}'
        after = '{"value": "x", "cap": 12}'
        ok, why = phrasing.phrasing_only("s.json", before, after)
        self.assertFalse(ok)

    def test_added_key_refuses(self):
        before = '{"value": "x"}'
        after = '{"value": "x", "extra": "y"}'
        ok, why = phrasing.phrasing_only("s.json", before, after)
        self.assertFalse(ok)


class TestUncoveredKinds(unittest.TestCase):
    def test_yaml_workflow_refuses(self):
        ok, why = phrasing.phrasing_only("w.yml", "a: 1\n", "a: 2\n")
        self.assertFalse(ok)
        self.assertIn("not covered", why)


class TestBranchAndGate(unittest.TestCase):
    def test_all_prose_marked_branch_is_clean_and_backed_without_atom(self):
        changes = [
            {"path": "CLAUDE.md", "before": "on phone\n", "after": "anywhere\n"},
            {"path": "m.py",
             "before": 'x = 1  # phone\n', "after": 'x = 1  # anywhere\n'},
        ]
        covered = {"CLAUDE.md", "m.py"}  # both marked through the pen
        clean, reasons = phrasing.branch_phrasing_clean(changes, covered)
        self.assertTrue(clean, reasons)
        # the off-log gate: phrasing-clean is backed with NO atom, NO receipt
        self.assertIsNone(pr_audit.orphan_reason([], [], phrasing_clean=True))

    def test_prose_but_unmarked_refuses_never_blind(self):
        # bdo's correction: prose-only is not enough — the pen mark is required,
        # so every light-lane edit leaves a visible record (never blind)
        changes = [{"path": "CLAUDE.md", "before": "on phone\n",
                    "after": "anywhere\n"}]
        clean, reasons = phrasing.branch_phrasing_clean(changes, covered_paths=set())
        self.assertFalse(clean)
        self.assertTrue(any("not marked" in r or "blind" in r for r in reasons))

    def test_one_code_change_disqualifies_branch_and_gate_orphans_it(self):
        changes = [
            {"path": "CLAUDE.md", "before": "on phone\n", "after": "anywhere\n"},
            {"path": "m.py", "before": "x = 1\n", "after": "x = 2\n"},  # code!
        ]
        covered = {"CLAUDE.md", "m.py"}  # marked, but m.py is still real code
        clean, reasons = phrasing.branch_phrasing_clean(changes, covered)
        self.assertFalse(clean)
        self.assertTrue(any("m.py" in r for r in reasons))
        # not phrasing-clean and no atom → still an off-log orphan
        self.assertIsNotNone(pr_audit.orphan_reason([], [], phrasing_clean=False))

    def test_empty_branch_is_not_clean(self):
        clean, _ = phrasing.branch_phrasing_clean([], set())
        self.assertFalse(clean)

    def test_phrasing_edits_fold_is_visible_newest_first(self):
        admissions = [
            {"type": "tick"},
            {"type": "phrasing", "id": "adm.a", "by": "claude", "ts": "t1",
             "reason": "one", "files": [{"path": "A.md"}]},
            {"type": "phrasing", "id": "adm.b", "by": "claude", "ts": "t2",
             "reason": "two", "files": [{"path": "B.md"}, {"path": "C.json"}]},
        ]
        edits = phrasing.phrasing_edits(admissions)
        self.assertEqual([e["id"] for e in edits], ["adm.b", "adm.a"])  # newest first
        self.assertEqual(edits[0]["files"], ["B.md", "C.json"])

    def test_atom_door_still_works_unchanged(self):
        # the original atom-backed path is untouched: atom + naming receipt = backed
        self.assertIsNone(pr_audit.orphan_reason(["atom.x.v0"], ["atom.x.v0"]))
        self.assertIsNotNone(pr_audit.orphan_reason(["atom.x.v0"], []))


if __name__ == "__main__":
    unittest.main()
