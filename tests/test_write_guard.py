"""Tests for the write pen and guard against done-line 0013:
the guard denies creation in ungoverned directories (no CLAUDE.md below
the root), denies wrong-next ids, malformed names, and missing required
sections in records directories carrying .pen.json — each refusal naming
the paved path — and passes edits, dotfiles, CLAUDE.md founding, files
outside the repo, and garbage stdin; the pen allocates ids from the
directory fold, scaffolds the required sections, and writes LF bytes."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import pen

GUARD = REPO / ".claude" / "hooks" / "write_guard.py"
DONE_CFG = REPO / ".ai-native" / "done" / ".pen.json"


def make_repo(tmp):
    """A fake governed repo: root CLAUDE.md, one governed module, one
    records dir with the real done-form, one ungoverned tree."""
    root = Path(tmp) / "repo"
    (root / "mod").mkdir(parents=True)
    (root / "rec").mkdir()
    (root / "void" / "deep").mkdir(parents=True)
    (root / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
    (root / "mod" / "CLAUDE.md").write_text("# mod\n", encoding="utf-8")
    (root / "mod" / "exists.py").write_text("x = 1\n", encoding="utf-8")
    shutil.copy(DONE_CFG, root / "rec" / ".pen.json")
    (root / "rec" / "0001-first.md").write_text(
        "# Done-line 0001 — first\n\n> **Done when:** it is.\n", encoding="utf-8")
    return root


GOOD_BODY = "# Done-line 0002 — next\n\n> **Done when:** the fold says so.\n"


class WriteGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def guard(self, file_path, content="x\n", tool="Write", stdin=None):
        payload = stdin if stdin is not None else json.dumps(
            {"tool_name": tool, "tool_input": {"file_path": str(file_path), "content": content}})
        proc = subprocess.run(
            [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
            capture_output=True,
            env=dict(os.environ,
                     ONTUM_REPO_ROOT=str(self.root),
                     ONTUM_TOOL_WATCH_LOG=str(Path(self.tmp) / "watch.jsonl")),
            cwd=str(self.root))
        return proc.returncode, proc.stderr.decode("utf-8", "replace")

    def test_governed_module_and_root_level_pass(self):
        self.assertEqual(self.guard(self.root / "mod" / "new.py")[0], 0)
        self.assertEqual(self.guard(self.root / "rootfile.md")[0], 0)

    def test_ungoverned_tree_is_denied_with_the_founding_move(self):
        code, err = self.guard(self.root / "void" / "deep" / "x.md")
        self.assertEqual(code, 2)
        self.assertIn("no CLAUDE.md governs", err)
        # founding the directory is the named way through — and it passes
        self.assertEqual(self.guard(self.root / "void" / "CLAUDE.md")[0], 0)

    def test_records_form_holds_the_line(self):
        # right next id with the form: passes
        self.assertEqual(self.guard(self.root / "rec" / "0002-next.md", GOOD_BODY)[0], 0)
        # wrong next id: refused, fold named
        code, err = self.guard(self.root / "rec" / "0004-skip.md", GOOD_BODY)
        self.assertEqual(code, 2)
        self.assertIn("next id here is 0002", err)
        # malformed name: refused by pattern
        code, err = self.guard(self.root / "rec" / "0002_Bad.md", GOOD_BODY)
        self.assertEqual(code, 2)
        self.assertIn("does not fit this directory's form", err)
        # missing required sections: refused, pen named
        code, err = self.guard(self.root / "rec" / "0002-empty.md", "just text\n")
        self.assertEqual(code, 2)
        self.assertIn("required section(s) missing", err)
        self.assertIn("loop.pen", err)

    def test_what_the_guard_leaves_alone(self):
        # existing file: not a creation
        self.assertEqual(self.guard(self.root / "mod" / "exists.py")[0], 0)
        # dotfile config
        self.assertEqual(self.guard(self.root / "void" / ".pen.json")[0], 0)
        # outside the repo entirely
        self.assertEqual(self.guard(Path(self.tmp) / "elsewhere.md")[0], 0)
        # a different tool's payload
        self.assertEqual(self.guard(self.root / "void" / "x.md", tool="Edit")[0], 0)
        # garbage stdin fails open
        self.assertEqual(self.guard("", stdin="not json")[0], 0)


class RecordsPenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.rec = Path(self.tmp) / "rec"
        self.rec.mkdir()
        # the real done config is frozen; this class exercises the generic
        # fold + scaffold (the fill-later path), which is the UNFROZEN
        # contract — a frozen dir refuses scaffold-without-body outright
        # (done-line 0057, tested in test_pen.py). Strip the flag so the
        # fixture matches what these cases mean to verify.
        cfg = json.loads(DONE_CFG.read_text(encoding="utf-8"))
        cfg.pop("frozen", None)
        (self.rec / ".pen.json").write_text(json.dumps(cfg), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pen_allocates_from_the_fold_and_scaffolds_the_form(self):
        self.assertEqual(pen.new(str(self.rec), "first-line", "the first"), 0)
        made = self.rec / "0001-first-line.md"
        self.assertTrue(made.exists())
        data = made.read_bytes()
        self.assertNotIn(b"\r", data)  # LF bytes: identity-safe
        text = data.decode("utf-8")
        self.assertIn("# Done-line 0001 — the first", text)
        self.assertIn("> **Done when:**", text)
        # the next one increments — no eyeballs involved
        self.assertEqual(pen.new(str(self.rec), "second", None), 0)
        self.assertTrue((self.rec / "0002-second.md").exists())

    def test_pen_takes_the_body_in_one_move(self):
        # bdo, live: "shouldn't the tool allow you to pass along the
        # content you intended without having to edit it?" — it does now
        code = pen.new(str(self.rec), "one-move", "one move",
                       body="> **Done when:** the mint is one move, not mint-then-edit.")
        self.assertEqual(code, 0)
        text = (self.rec / "0001-one-move.md").read_text(encoding="utf-8")
        self.assertIn("# Done-line 0001 — one move", text)
        self.assertIn("the mint is one move", text)
        self.assertNotIn("<the one line", text)  # no placeholder left behind

    def test_pen_refuses_a_body_that_breaks_the_form(self):
        code = pen.new(str(self.rec), "formless", None, body="just prose")
        self.assertEqual(code, 2)
        self.assertFalse((self.rec / "0001-formless.md").exists())

    def test_pen_refusals(self):
        self.assertEqual(pen.new(str(self.rec), "Bad_Slug", None), 2)
        plain = Path(self.tmp) / "plain"
        plain.mkdir()
        self.assertEqual(pen.new(str(plain), "x", None), 2)  # no .pen.json
        self.assertEqual(pen.new(str(Path(self.tmp) / "nope"), "x", None), 2)


if __name__ == "__main__":
    unittest.main()
