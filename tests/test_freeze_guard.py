"""Tests for the freeze guard and the supersede ritual against done-line
0033: a written done-line is frozen — the guard denies Edit and Write
(overwrite) on an existing file in a `"frozen": true` records directory,
naming the painful path, while passing creation, unfrozen directories,
the config dotfile, files outside the repo, and garbage stdin; the
supersede pen is bdo's alone — it refuses every session signer outright,
writing nothing (no pending bar, no free "stop working" card), and only
on bdo's own signature writes the additive new line, leaves the original
bytes untouched, and records a `done_superseded` admission.

The §10 bar lives here: a locally-fine edit to a done-line *refuses to
fit*, and the guard notices."""

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

GUARD = REPO / ".claude" / "hooks" / "freeze_guard.py"
DONE_CFG = REPO / ".ai-native" / "done" / ".pen.json"

EXISTING_DONE = "# Done-line 0001 — first\n\n> **Done when:** it is.\n"
HONEST_REASON = ("the bar named a fold over the live log, but the log shape "
                 "changed under it and the gate it assumed no longer exists")


def make_repo(tmp):
    """A fake repo: root CLAUDE.md, a frozen done dir with one written
    line and a log dir, and an unfrozen records dir."""
    root = Path(tmp) / "repo"
    done = root / ".ai-native" / "done"
    done.mkdir(parents=True)
    (root / ".ai-native" / "log").mkdir()
    (root / "CLAUDE.md").write_text("# root\n", encoding="utf-8")
    shutil.copy(DONE_CFG, done / ".pen.json")
    (done / "0001-first.md").write_text(EXISTING_DONE, encoding="utf-8")
    # an unfrozen records dir: same shape, no frozen flag
    unfrozen = root / ".ai-native" / "reports"
    unfrozen.mkdir()
    (unfrozen / ".pen.json").write_text(json.dumps(
        {"kind": "report", "pattern": r"^\d{4}-[a-z0-9][a-z0-9-]*\.md$"}),
        encoding="utf-8")
    (unfrozen / "0001-a-report.md").write_text("# a report\n", encoding="utf-8")
    return root


class FreezeGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def guard(self, file_path, tool="Edit", stdin=None):
        payload = stdin if stdin is not None else json.dumps(
            {"tool_name": tool,
             "tool_input": {"file_path": str(file_path), "content": "x\n"}})
        proc = subprocess.run(
            [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
            capture_output=True,
            env=dict(os.environ,
                     ONTUM_REPO_ROOT=str(self.root),
                     ONTUM_TOOL_WATCH_LOG=str(Path(self.tmp) / "watch.jsonl")),
            cwd=str(self.root))
        return proc.returncode, proc.stderr.decode("utf-8", "replace")

    def test_a_written_done_line_refuses_to_be_edited(self):
        code, err = self.guard(self.root / ".ai-native" / "done" / "0001-first.md")
        self.assertEqual(code, 2)
        self.assertIn("frozen", err)
        self.assertIn("supersede-done", err)  # the refusal names the painful path

    def test_a_written_done_line_refuses_to_be_overwritten(self):
        code, err = self.guard(
            self.root / ".ai-native" / "done" / "0001-first.md", tool="Write")
        self.assertEqual(code, 2)
        self.assertIn("frozen", err)

    def test_what_the_freeze_leaves_alone(self):
        done = self.root / ".ai-native" / "done"
        # creation (no existing file) is write_guard's land, not ours
        self.assertEqual(self.guard(done / "0002-next.md")[0], 0)
        # the config dotfile is not a governed record
        self.assertEqual(self.guard(done / ".pen.json")[0], 0)
        # an unfrozen records directory stays editable
        self.assertEqual(self.guard(
            self.root / ".ai-native" / "reports" / "0001-a-report.md")[0], 0)
        # outside the repo entirely
        self.assertEqual(self.guard(Path(self.tmp) / "elsewhere.md")[0], 0)
        # a non-edit tool
        self.assertEqual(self.guard(done / "0001-first.md", tool="Bash")[0], 0)
        # garbage stdin fails open
        self.assertEqual(self.guard("", stdin="not json")[0], 0)


class SupersedeRitualTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_repo(self.tmp)
        self.done = self.root / ".ai-native" / "done"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def admissions(self):
        log = self.root / ".ai-native" / "log" / "admissions.jsonl"
        if not log.exists():
            return []
        return [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_refuses_abandoning_a_bar_never_set(self):
        code = pen.supersede_done(str(self.done), "0099", "new-line",
                                  "a new bar", HONEST_REASON, "bdo")
        self.assertEqual(code, 2)
        self.assertEqual(self.admissions(), [])  # nothing recorded

    def test_refuses_a_glib_reason(self):
        code = pen.supersede_done(str(self.done), "0001", "new-line",
                                  "a new bar", "ran out of time", "bdo")
        self.assertEqual(code, 2)
        self.assertFalse((self.done / "0002-new-line.md").exists())

    def test_a_session_cannot_supersede_at_all(self):
        # not pending, not written — a session that could author even an
        # unauthorized new bar would hold a free 'stop working' card
        for signer in ("claude", "codex", "overnight-codex", ""):  # no session signer passes
            code = pen.supersede_done(str(self.done), "0001", "new-bar",
                                      "an easier bar for myself",
                                      HONEST_REASON, signer)
            self.assertEqual(code, 2)
        # nothing was written: no new line, no admission, original untouched
        self.assertFalse((self.done / "0002-new-bar.md").exists())
        self.assertEqual(self.admissions(), [])
        self.assertEqual(
            (self.done / "0001-first.md").read_text(encoding="utf-8"), EXISTING_DONE)

    def test_only_bdo_supersede_writes_and_it_is_his_own(self):
        code = pen.supersede_done(str(self.done), "1", "owner-moved-bar",
                                  "the new bar bdo set", HONEST_REASON, "bdo")
        self.assertEqual(code, 0)  # the owner steers the bar (D-4)
        # the new line is written, additive, carrying the reflection; the
        # original is untouched history
        new = self.done / "0002-owner-moved-bar.md"
        self.assertTrue(new.exists())
        text = new.read_text(encoding="utf-8")
        self.assertIn("SUPERSEDES done-line 0001", text)
        self.assertIn(HONEST_REASON, text)
        self.assertNotIn(b"\r", new.read_bytes())  # LF bytes: identity-safe
        self.assertEqual(
            (self.done / "0001-first.md").read_text(encoding="utf-8"), EXISTING_DONE)
        # the act is on the record, authorized as bdo's own
        adm = self.admissions()
        self.assertEqual(len(adm), 1)
        self.assertEqual(adm[0]["type"], "done_superseded")
        self.assertTrue(adm[0]["authorized"])
        self.assertEqual(adm[0]["authorized_by"], "bdo")

    def test_supersede_refused_on_an_unfrozen_directory(self):
        reports = self.root / ".ai-native" / "reports"
        code = pen.supersede_done(str(reports), "0001", "x",
                                  "a bar", HONEST_REASON, "bdo")
        self.assertEqual(code, 2)  # supersede is for frozen contracts only


if __name__ == "__main__":
    unittest.main()
