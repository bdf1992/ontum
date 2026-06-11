"""Done-line 0030: the experience unit refuses weather.

The §10 case for the experience: a well-formed experience over a registered
surface with a granted rung is born; strip its obligation (the terminal set),
its surface, its context, or its backing's rung and it is refused at birth —
context without obligation is weather, and weather is not an experience. The
gate is pure over the log; surface and rung are admitted into a temp root.
"""

import pathlib
import shutil
import tempfile
import unittest

from loop import experience, node, reflect


def _well_formed():
    return {
        "source_event": "surface-drift",
        "surface": "github-issues",
        "context": "atom.x awaits the owner's stamp on a registered surface",
        "expectation": {"shape": "verdict", "terminal_set": ["accept", "reject"]},
        "backing": {"class": "branded-subagent"},
    }


class TestBirthGate(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp()) / ".ai-native"
        (self.root / "log").mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root.parent, ignore_errors=True)
        # a registered surface and a backing that may judge
        reflect.admit_surface(self.root, "github-issues", "bdf1992/ontum", "bdo")
        node.admit_rung(self.root, "branded-subagent", "judge", "bdo")

    def test_well_formed_experience_is_born(self):
        self.assertIsNone(experience.experience_refusal(_well_formed(), self.root))

    def test_no_obligation_is_weather(self):
        exp = _well_formed()
        exp["expectation"]["terminal_set"] = []
        reason = experience.experience_refusal(exp, self.root)
        self.assertIn("weather", reason)

    def test_unregistered_surface_refused(self):
        exp = _well_formed()
        exp["surface"] = "slack"
        self.assertIn("not registered", experience.experience_refusal(exp, self.root))

    def test_unknown_beat_refused(self):
        exp = _well_formed()
        exp["source_event"] = "a-vibe"
        self.assertIn("source beat", experience.experience_refusal(exp, self.root))

    def test_missing_context_refused(self):
        exp = _well_formed()
        exp["context"] = "   "
        self.assertIn("context", experience.experience_refusal(exp, self.root))

    def test_backing_without_the_rung_refused(self):
        # branded-subagent holds 'judge' (granted) but not 'author'
        exp = _well_formed()
        exp["expectation"] = {"shape": "story", "terminal_set": ["conform", "route_back"]}
        reason = experience.experience_refusal(exp, self.root)
        self.assertIn("author", reason)

    def test_unknown_backing_class_refused(self):
        exp = _well_formed()
        exp["backing"] = {"class": "a-wizard"}
        self.assertIn("agent class", experience.experience_refusal(exp, self.root))


if __name__ == "__main__":
    unittest.main()
