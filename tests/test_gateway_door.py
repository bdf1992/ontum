"""Tests for the ambient gateway door (done-line 0126, The Polity).

Distinct from `tests/test_gateway.py` (done-line 0062, the *inference* gateway):
this exercises `loop/gateway.py`, the typed-message **door** of the ambient
gateway — a different seam, the term-overload flagged in the session report.

The §10 case is the point and it carries the teeth: two messages of the **same
registered type** must be told apart — one that carries the type's required
fields is `typed`; one missing a field is refused → `dead-letter`, with the
missing field named. A door that typed both, or refused both, would not be a
gate (§13.9). The rest pins the registry fold (core + admitted, proposed-tier)
and the one write (`admit_type`, signed, core un-shadowable)."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import gateway
from loop.reconcile import Fold


def make_root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for f in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / f).write_text("", encoding="utf-8")
    return root


class TheDoor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = make_root(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def fold(self):
        return Fold(self.root)

    # --- the §10 bite: same type, one fits, one refused -------------------
    def test_same_type_one_fits_one_refused(self):
        fold = self.fold()
        complete = {"type": "tool-request", "caller": "patrol",
                    "action": "read", "resource": "gaps-backlog"}
        incomplete = {"type": "tool-request", "caller": "patrol",
                      "action": "read"}  # missing `resource`

        ok = gateway.type_message(fold, complete)
        bad = gateway.type_message(fold, incomplete)

        self.assertEqual(ok["outcome"], gateway.TYPED)
        self.assertEqual(ok["type"], "tool-request")
        self.assertEqual(bad["outcome"], gateway.DEAD_LETTER)
        self.assertEqual(bad["missing"], ["resource"])
        self.assertIn("resource", bad["reason"])
        # the teeth: the two locally-fine-looking messages did NOT fare alike
        self.assertNotEqual(ok["outcome"], bad["outcome"])

    def test_empty_value_counts_as_missing(self):
        # a present-but-empty field is missing — the door checks substance
        bad = gateway.type_message(self.fold(), {
            "type": "work-item", "seam": "owner-stamp", "subject": ""})
        self.assertEqual(bad["outcome"], gateway.DEAD_LETTER)
        self.assertEqual(bad["missing"], ["subject"])

    # --- the other refusals at the door ----------------------------------
    def test_untyped_dead_letters(self):
        bad = gateway.type_message(self.fold(), {"caller": "x"})
        self.assertEqual(bad["outcome"], gateway.DEAD_LETTER)
        self.assertIn("untyped", bad["reason"])

    def test_unknown_type_dead_letters_as_proposed(self):
        bad = gateway.type_message(self.fold(), {"type": "frobnicate", "a": 1})
        self.assertEqual(bad["outcome"], gateway.DEAD_LETTER)
        self.assertEqual(bad["type_status"], "proposed")
        self.assertIn("frobnicate", bad["reason"])

    def test_non_object_dead_letters(self):
        for junk in ("just a string", ["a", "list"], 42, None):
            res = gateway.type_message(self.fold(), junk)
            self.assertEqual(res["outcome"], gateway.DEAD_LETTER)

    # --- a core round-trip ------------------------------------------------
    def test_core_type_round_trips(self):
        res = gateway.type_message(self.fold(), {
            "type": "work-item", "seam": "gaps", "subject": "mock-stage"})
        self.assertEqual(res["outcome"], gateway.TYPED)
        self.assertEqual(res["type_status"], "core")

    # --- the registry fold: admitted extensions (proposed-tier) ----------
    def test_admitted_type_extends_registry(self):
        # unknown before admission → proposed; admit → registered → validates
        before = gateway.type_message(self.fold(), {
            "type": "chat-message", "target": "s1", "content": "hi"})
        self.assertEqual(before["outcome"], gateway.DEAD_LETTER)

        gateway.admit_type(self.root, "chat-message",
                           ["target", "content"], "a session-addressed message",
                           by="claude")

        fold = self.fold()
        self.assertEqual(gateway.type_status(fold, "chat-message"), "admitted")
        after = gateway.type_message(fold, {
            "type": "chat-message", "target": "s1", "content": "hi"})
        self.assertEqual(after["outcome"], gateway.TYPED)
        self.assertEqual(after["type_status"], "admitted")
        # and an admitted type bites too, on its own required fields
        miss = gateway.type_message(fold, {"type": "chat-message", "target": "s1"})
        self.assertEqual(miss["outcome"], gateway.DEAD_LETTER)
        self.assertEqual(miss["missing"], ["content"])

    def test_withdraw_supersedes(self):
        gateway.admit_type(self.root, "chat-message", ["target"], "", by="claude")
        self.assertEqual(gateway.type_status(self.fold(), "chat-message"), "admitted")
        gateway.admit_type(self.root, "chat-message", [], "", by="claude",
                           withdrawn=True)
        self.assertEqual(gateway.type_status(self.fold(), "chat-message"), "proposed")

    # --- the pen's refusals (governed, signed, core-protected) -----------
    def test_admit_unsigned_refused(self):
        self.assertIsNotNone(gateway.type_refusal("chat-message", by=""))
        self.assertIsNone(gateway.admit_type(self.root, "chat-message",
                                              ["target"], "", by=""))

    def test_core_cannot_be_shadowed(self):
        self.assertIsNotNone(gateway.type_refusal("tool-request", by="claude"))
        self.assertIsNone(gateway.admit_type(self.root, "tool-request",
                                             ["x"], "", by="claude"))
        # core spec is unchanged after a shadow attempt is refused
        self.assertEqual(
            gateway.registry(self.fold())["tool-request"]["required"],
            ("caller", "action", "resource"))


if __name__ == "__main__":
    unittest.main()
