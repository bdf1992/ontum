"""Done-line 0044: the inbound-gesture heartbeat surfaces bdo's closed issues
on a known event, and stays silent / fails open otherwise.

The hook judges nothing — that is the session's. What it must get right is the
pure surfacing: pending gestures format a clear wake line that names the skill
to run; an empty inbox produces silence (never a noisy 'all clear'); and a
broken sensor (no surface registered, gh absent) yields silence, not a crash.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HOOK = (Path(__file__).resolve().parent.parent
        / ".claude" / "hooks" / "gesture_surface.py")
_spec = importlib.util.spec_from_file_location("gesture_surface", HOOK)
gs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gs)


class FormatSurface(unittest.TestCase):
    def test_empty_inbox_is_silent(self):
        self.assertEqual(gs.format_surface({"realness": [], "arc": []}), "")
        self.assertEqual(gs.format_surface({}), "")

    def test_realness_gesture_names_its_skill_and_words(self):
        found = {"realness": [{"number": 66, "stage": "placement-gate.mock.v0",
                               "node": "placement-gate.det.v1",
                               "comment": "yes, make it real"}], "arc": []}
        text = gs.format_surface(found)
        self.assertIn("#66", text)
        self.assertIn("placement-gate.mock.v0", text)
        self.assertIn("placement-gate.det.v1", text)
        self.assertIn("yes, make it real", text)
        self.assertIn("realness-intake", text)
        self.assertNotIn("arc-intake", text)  # no arc gestures → don't name that skill

    def test_arc_gesture_names_its_skill(self):
        found = {"realness": [], "arc": [{"number": 70, "epic": "epic.experience-layer",
                                          "comment": "ship it"}]}
        text = gs.format_surface(found)
        self.assertIn("#70", text)
        self.assertIn("epic.experience-layer", text)
        self.assertIn("arc-intake", text)
        self.assertNotIn("realness-intake", text)

    def test_both_surfaced_together(self):
        found = {"realness": [{"number": 1, "stage": "s", "node": "n", "comment": "a"}],
                 "arc": [{"number": 2, "epic": "e", "comment": "b"}]}
        text = gs.format_surface(found)
        self.assertIn("2 closed issue(s)", text)
        self.assertIn("realness-intake", text)
        self.assertIn("arc-intake", text)

    def test_no_comment_reads_as_such(self):
        found = {"realness": [{"number": 9, "stage": "s", "node": "n", "comment": ""}]}
        self.assertIn("no comment", gs.format_surface(found))

    def test_long_comment_truncated(self):
        found = {"realness": [{"number": 9, "stage": "s", "node": "n",
                               "comment": "x" * 400}]}
        line = gs.format_surface(found)
        self.assertIn("…", line)


class SurfaceRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.adm = Path(self.tmp) / "admissions.jsonl"
        self._orig = gs.ADMISSIONS
        gs.ADMISSIONS = self.adm

    def tearDown(self):
        gs.ADMISSIONS = self._orig

    def _write(self, *records):
        self.adm.write_text(
            "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

    def test_reads_registered_repo(self):
        self._write({"type": "surface", "surface": "github-issues",
                     "address": "bdf1992/ontum"})
        self.assertEqual(gs.surface_repo(), "bdf1992/ontum")

    def test_latest_admission_wins(self):
        self._write(
            {"type": "surface", "surface": "github-issues", "address": "old/repo"},
            {"type": "surface", "surface": "github-issues", "address": "new/repo"})
        self.assertEqual(gs.surface_repo(), "new/repo")

    def test_disabled_deregisters(self):
        self._write(
            {"type": "surface", "surface": "github-issues", "address": "a/b"},
            {"type": "surface", "surface": "github-issues", "address": "a/b",
             "enabled": False})
        self.assertIsNone(gs.surface_repo())

    def test_no_surface_is_none(self):
        self._write({"type": "setpoint", "value": 3})
        self.assertIsNone(gs.surface_repo())

    def test_missing_file_is_none_not_crash(self):
        gs.ADMISSIONS = Path(self.tmp) / "does-not-exist.jsonl"
        self.assertIsNone(gs.surface_repo())


class FailOpen(unittest.TestCase):
    def test_pending_on_missing_pen_is_empty(self):
        # a pen path that doesn't exist → [], never an exception
        self.assertEqual(gs._pending("nope/not-a-pen.py", "a/b"), [])


if __name__ == "__main__":
    unittest.main()
