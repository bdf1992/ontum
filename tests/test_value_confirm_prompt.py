"""Tests for the value-confirm prompt against done-line 0045.

value-confirm is the L0 second check — an *inference* gate, like the value gate
(first light). A mind's verdict cannot be unit-tested; what is pinned here is
the prompt's load-bearing contract, the part the loop depends on once the stage
is wired real: that the gate can say `missed` (a gate that cannot refuse is a
mock with a bigger bill — epic.experience-layer), that it judges *delivery* and
does not re-decide *value*, that it confirms on evidence not on the story's
say-so, that arc completion stays bdo's, and that it is versioned per §7. A
future edit may sharpen the wording; it may not gut the contract. Semantic
evals — does the rubric actually catch a claim/delivery gap — are owed with the
next change to the prompt (§7), and the first real `missed` on the live log is
this gate's first light.
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import reconcile

CONFIRM_STAGE = "value-confirm.mock.v0"
PROMPT_PATH = REPO / ".ai-native" / "nodes" / "value-confirm.claude.v1.md"


class ValueConfirmPromptContractTest(unittest.TestCase):
    PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
    # normalized: collapse line-wrapping so a contract test pins meaning, not
    # the prose's column width
    NORM = " ".join(PROMPT.split())

    def test_can_refuse_both_verdicts_present(self):
        # the real-able signal: the gate must be able to say no. Both verdicts
        # named, and `missed` is the refusal a fixed-verdict mock cannot reach.
        self.assertIn("confirmed | missed", self.NORM)
        self.assertIn("**`missed`**", self.NORM)

    def test_refusal_verdict_is_in_the_seam_and_not_the_mock(self):
        # the seam's terminal set carries `missed`, and the mock's fixed verdict
        # is `confirmed` — so a real `missed` is the verdict the mock never casts.
        stage = next(s for s in reconcile.PIPELINE if s["node"] == CONFIRM_STAGE)
        self.assertIn("missed", stage["terminal_expected"])
        self.assertEqual(stage["verdict"], "confirmed")
        self.assertNotEqual(stage["verdict"], "missed")

    def test_judges_delivery_not_value(self):
        # it must not re-decide whether the piece was worth doing (L0's call) —
        # only whether what was promised was delivered.
        self.assertIn("re-decide *value*", self.NORM)
        self.assertIn("whether what was promised was delivered", self.NORM)

    def test_confirms_on_evidence_not_say_so(self):
        # a claim with no delivery evidence on the record is missed, not a
        # courtesy confirmed — the second-set-of-eyes guarantee.
        self.assertIn("with no delivery evidence on the record is `missed`", self.NORM)

    def test_section_10_names_the_could_have_failed_check(self):
        self.assertIn("could not conceivably have been a `missed`", self.NORM)

    def test_arc_completion_stays_the_owners(self):
        # confirming a piece does not close the arc; arc completion is bdo's.
        self.assertIn("arc completion is bdo's", self.NORM)
        self.assertIn("D-4", self.NORM)

    def test_will_not_judge_its_own_announcement(self):
        self.assertIn("D-2", self.NORM)

    def test_versioned_per_section_7(self):
        self.assertIn("version: 1.0.0", self.NORM)


if __name__ == "__main__":
    unittest.main()
