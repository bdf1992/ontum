"""Tests for the records pen's `new` verb against done-line 0057: a
frozen records directory is write-once, so a scaffolded fill-later stub
is a dead path — freeze_guard would deny the Edit that fills it. The pen
must refuse that path at the source (frozen + no --body → needs-you, no
file written, non-zero), while leaving the two working paths exactly as
they are: the same frozen dir WITH a valid --body still mints the line,
and an unfrozen records dir WITHOUT --body still scaffolds the stub.

The §10 bar lives here: the refusal actually fires — two locally-fine
calls (frozen-no-body vs unfrozen-no-body) the one branch must tell
apart, asserted over the filesystem, not internals."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import pen

DONE_CFG = REPO / ".ai-native" / "done" / ".pen.json"

# a complete done-line body: the heading carries "# Done-line"; the body
# brings the "> **Done when:**" section the form requires
GOOD_BODY = ("Written before code, per §9.4. When this line is met, stop.\n\n"
             "> **Done when:** the bar is true.\n")


def make_repo(tmp):
    """A fake repo with a frozen `done` dir (the real form: scaffold +
    frozen + required_sections) and an unfrozen records dir that also
    declares a scaffold."""
    root = Path(tmp) / "repo"
    done = root / "done"
    done.mkdir(parents=True)
    shutil.copy(DONE_CFG, done / ".pen.json")  # frozen: true, with scaffold

    unfrozen = root / "reports"
    unfrozen.mkdir()
    cfg = json.loads(DONE_CFG.read_text(encoding="utf-8"))
    cfg.pop("frozen", None)  # same form, just not frozen
    (unfrozen / ".pen.json").write_text(json.dumps(cfg), encoding="utf-8")
    return root, done, unfrozen


class NewOnFrozenDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root, self.done, self.unfrozen = make_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _files(self, d):
        return sorted(p.name for p in d.iterdir() if p.suffix == ".md")

    def test_frozen_dir_without_body_refuses_and_writes_nothing(self):
        before = self._files(self.done)
        code = pen.new(str(self.done), "fill-me-later", "fill me later")
        self.assertEqual(code, 2)  # the dead path is refused
        self.assertEqual(self._files(self.done), before)  # nothing written

    def test_frozen_dir_with_a_valid_body_still_mints(self):
        code = pen.new(str(self.done), "in-one-move", "in one move",
                       body=GOOD_BODY)
        self.assertEqual(code, 0)  # the one-shot --body path is untouched
        written = self.done / "0001-in-one-move.md"
        self.assertTrue(written.exists())
        text = written.read_text(encoding="utf-8")
        self.assertIn("# Done-line 0001", text)
        self.assertIn("> **Done when:**", text)

    def test_unfrozen_dir_without_body_still_scaffolds(self):
        code = pen.new(str(self.unfrozen), "fill-me-later", "fill me later")
        self.assertEqual(code, 0)  # scaffold-then-fill stays valid here
        written = self.unfrozen / "0001-fill-me-later.md"
        self.assertTrue(written.exists())
        # it really is the fill-later stub, with the placeholder intact
        self.assertIn("<the one line", written.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
