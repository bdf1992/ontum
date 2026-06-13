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
import subprocess
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

    def test_pen_output_is_a_zero_divergence_carbon_copy(self):
        # the loop closes (done-line 0070): whatever the pen writes must pass
        # the same definition the write guard enforces. The pen self-checks it,
        # so a non-copy never reaches disk; here we confirm the written bytes.
        self.assertEqual(pen.new(str(self.done), "the-copy", "the copy",
                                 body=GOOD_BODY), 0)
        made = self.done / "0001-the-copy.md"
        cfg = json.loads((self.done / ".pen.json").read_text(encoding="utf-8"))
        content = made.read_text(encoding="utf-8")
        self.assertEqual(pen.carbon_divergences(cfg, made.name, content, 1), [])


class FleetSafeAllocation(unittest.TestCase):
    """The fleet-safe-id done-line: the pen claims a fleet-safe id, not a
    local one. The §10 case made real — a sibling branch's higher id is
    locally invisible,
    yet the pen must allocate above it (the 0057/0058/0059 renumber saga is
    what local-only allocation costs), while a missing reach-tool falls back
    to the local fold rather than blocking the mint."""

    def _two_branch_repo(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)

        def g(*args):
            return subprocess.run(["git", *args], cwd=d, check=True,
                                  capture_output=True, text=True)

        g("init", "-q")
        g("config", "user.email", "t@example.com")
        g("config", "user.name", "t")
        done = d / ".ai-native" / "done"
        done.mkdir(parents=True)
        (done / "0005-local.md").write_text("a", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "local")
        base = g("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        # a sibling branch claims a HIGHER id, then we return to base so the
        # local working tree shows only 0005 — 0009 is invisible locally
        g("checkout", "-qb", "sibling")
        (done / "0009-sibling.md").write_text("b", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "sibling")
        g("checkout", "-q", base)
        return d, done

    def test_pen_allocates_above_the_highest_id_on_any_ref(self):
        _d, done = self._two_branch_repo()
        # local fold would say 6 (one past the visible 0005); the fleet fold
        # sees the sibling's 0009 and claims 10
        self.assertEqual(pen._fleet_next_id(done), 10)
        self.assertEqual(pen.next_id(done), 10)

    def test_falls_back_to_local_when_the_reach_tool_is_absent(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "0005-a.md").write_text("x", encoding="utf-8")
        (d / "0007-b.md").write_text("x", encoding="utf-8")
        orig = pen._PLACEMENT
        pen._PLACEMENT = Path(d) / "no-such-placement.py"
        try:
            self.assertIsNone(pen._fleet_next_id(d))  # sensor absent
            self.assertEqual(pen.next_id(d), 8)       # local fold: 0007 + 1
        finally:
            pen._PLACEMENT = orig


class CarbonDivergencesTest(unittest.TestCase):
    """The one shared definition of 'a faithful pen carbon copy' (done-line
    0070), imported by the write guard so the pen and the guard never disagree.
    Each divergence is named — the refusal is a fail notification a cold reader
    can act on."""

    def setUp(self):
        self.cfg = json.loads(DONE_CFG.read_text(encoding="utf-8"))

    def good(self):
        return "# Done-line 0002 — next\n\n> **Done when:** the fold says so.\n"

    def test_a_faithful_copy_has_no_divergences(self):
        self.assertEqual(
            pen.carbon_divergences(self.cfg, "0002-next.md", self.good(), 2), [])

    def test_each_drift_is_caught_and_named(self):
        name, good = "0002-next.md", self.good()
        # wrong id vs the expected fleet-safe next
        self.assertTrue(any("fleet-safe next id" in p for p in
            pen.carbon_divergences(self.cfg, name, good, 5)))
        # CRLF bytes the pen never emits
        self.assertTrue(any("LF only" in p for p in
            pen.carbon_divergences(self.cfg, name, good.replace("\n", "\r\n"), 2)))
        # no trailing newline
        self.assertTrue(any("end with a newline" in p for p in
            pen.carbon_divergences(self.cfg, name, good.rstrip("\n"), 2)))
        # heading id drifts from the filename id (0099 in a 0002 file)
        drift = "# Done-line 0099 — next\n\n> **Done when:** x\n"
        self.assertTrue(any("pen's heading" in p for p in
            pen.carbon_divergences(self.cfg, name, drift, 2)))
        # malformed name
        self.assertTrue(any("does not fit the form" in p for p in
            pen.carbon_divergences(self.cfg, "0002_bad.md", good, 2)))


if __name__ == "__main__":
    unittest.main()
