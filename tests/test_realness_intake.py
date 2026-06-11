"""Done-line 0042: the realness-intake pen reads bdo's GitHub gesture
deterministically.

The pen never judges intent (the SKILL does) and never runs admit-real. But it
must extract the right bytes for the session to judge: the (stage, node) an
issue carries — both names, because admit-real needs both — and bdo's own
closing comment (not a bot's, not someone else's). The §10 cases: a marker
naming only the stage is a half-marker, locally plausible but useless — the
pen must refuse it rather than hand the session a node it guessed; and a closed
issue with comments from two logins must yield exactly the owner's last word,
or the session reads the wrong intent and wires the loop to a judge bdo never
blessed.
"""

import importlib.util
import unittest
from pathlib import Path

PEN = (Path(__file__).resolve().parent.parent
       / ".claude" / "skills" / "realness-intake" / "realness.py")
_spec = importlib.util.spec_from_file_location("realness_intake", PEN)
realness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(realness)


class NamesFromBody(unittest.TestCase):
    def test_round_trips_both_names(self):
        body = "briefing\n\n" + realness.marker(
            "placement-gate.mock.v0", "placement-gate.det.v1")
        self.assertEqual(
            realness.names_from_body(body),
            ("placement-gate.mock.v0", "placement-gate.det.v1"))

    def test_no_marker_is_not_ours(self):
        self.assertIsNone(realness.names_from_body("a plain issue, no marker"))
        self.assertIsNone(realness.names_from_body(""))
        self.assertIsNone(realness.names_from_body(None))

    def test_half_marker_is_not_a_marker(self):
        # a marker naming only the stage (no node=) must not parse — the pen
        # never hands the session a node it had to guess (absence is information).
        half = "<!-- ontum:realness-confirm stage=placement-gate.mock.v0 -->"
        self.assertIsNone(realness.names_from_body(half))

    def test_arc_confirm_marker_is_not_ours(self):
        # arc-intake's marker must not be mistaken for a realness one.
        arc = "<!-- ontum:arc-confirm epic=epic.experience-layer -->"
        self.assertIsNone(realness.names_from_body(arc))


class BdoComment(unittest.TestCase):
    def _c(self, login, body):
        return {"author": {"login": login}, "body": body}

    def test_picks_owners_last_word_among_many(self):
        comments = [
            self._c("ontum-bot", "opened for confirmation"),
            self._c("bdf1992", "hmm, thinking"),
            self._c("someone-else", "i think yes"),
            self._c("bdf1992", "yes, make it real"),
        ]
        self.assertEqual(
            realness.bdo_comment(comments, "bdf1992"), "yes, make it real")

    def test_owner_match_is_case_insensitive(self):
        self.assertEqual(
            realness.bdo_comment([self._c("BDF1992", "go live")], "bdf1992"),
            "go live")

    def test_no_owner_comment_is_empty(self):
        self.assertEqual(
            realness.bdo_comment([self._c("ontum-bot", "ping")], "bdf1992"), "")
        self.assertEqual(realness.bdo_comment([], "bdf1992"), "")


class HasLabel(unittest.TestCase):
    def test_dict_and_string_shapes(self):
        self.assertTrue(realness.has_label([{"name": "intake-done"}], "intake-done"))
        self.assertTrue(realness.has_label(["intake-done"], "intake-done"))
        self.assertFalse(realness.has_label([{"name": "realness-confirm"}], "intake-done"))
        self.assertFalse(realness.has_label(None, "intake-done"))


if __name__ == "__main__":
    unittest.main()
