"""Done-line 0038: the arc-intake pen reads bdo's GitHub gesture deterministically.

The pen never judges intent — that is the session's. But it must extract the
right bytes for the session to judge: the epic an issue carries, and bdo's
own closing comment (not a bot's, not someone else's). The §10 case: a closed
issue with comments from two logins is locally fine, but the pen must pick
exactly the owner's last word — pick the wrong comment and the session reads
the wrong intent. And an issue with no marker is not ours: refused, not guessed.
"""

import importlib.util
import unittest
from pathlib import Path

PEN = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "arc-intake" / "intake.py"
_spec = importlib.util.spec_from_file_location("arc_intake", PEN)
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)


class EpicFromBody(unittest.TestCase):
    def test_round_trips_its_own_marker(self):
        body = "some briefing\n\n" + intake.marker("epic.owner-harness")
        self.assertEqual(intake.epic_from_body(body), "epic.owner-harness")

    def test_no_marker_is_not_ours(self):
        self.assertIsNone(intake.epic_from_body("a plain issue, no marker"))
        self.assertIsNone(intake.epic_from_body(""))


class BdoComment(unittest.TestCase):
    def _c(self, login, body):
        return {"author": {"login": login}, "body": body}

    def test_picks_owners_last_word_among_many(self):
        comments = [
            self._c("ontum-bot", "opened for confirmation"),
            self._c("bdf1992", "hmm, thinking"),
            self._c("someone-else", "i think yes"),
            self._c("bdf1992", "yes, land it"),
        ]
        self.assertEqual(intake.bdo_comment(comments, "bdf1992"), "yes, land it")

    def test_owner_match_is_case_insensitive(self):
        comments = [self._c("BDF1992", "go")]
        self.assertEqual(intake.bdo_comment(comments, "bdf1992"), "go")

    def test_no_owner_comment_is_empty(self):
        comments = [self._c("ontum-bot", "ping")]
        self.assertEqual(intake.bdo_comment(comments, "bdf1992"), "")
        self.assertEqual(intake.bdo_comment([], "bdf1992"), "")


class HasLabel(unittest.TestCase):
    def test_dict_and_string_shapes(self):
        self.assertTrue(intake.has_label([{"name": "intake-done"}], "intake-done"))
        self.assertTrue(intake.has_label(["intake-done"], "intake-done"))
        self.assertFalse(intake.has_label([{"name": "arc-confirm"}], "intake-done"))
        self.assertFalse(intake.has_label(None, "intake-done"))


if __name__ == "__main__":
    unittest.main()
