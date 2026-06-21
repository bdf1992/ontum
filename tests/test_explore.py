"""§10 for the explore lobe / Scout fold (done-line 0140): the read-only fold
that turns research over priors into one marked call to action. The teeth:
a grounded move is emitted and marked proposed; an ungrounded one is refused
(the ghost refusal); a fabricated/constant emitter cannot pass; a purpose
that does not resolve is needs-you; and the fold writes nothing.
"""

import copy
import unittest
from pathlib import Path

from loop import explore
from loop.reconcile import DEFAULT_ROOT
from causality.term_economy import resolve_evidence

ROOT = Path(DEFAULT_ROOT)
REPO = ROOT.resolve().parent
PURPOSE = "epic.strategy"


class TestExplore(unittest.TestCase):
    def test_grounded_call_to_action_is_emitted_and_marked(self):
        cta = explore.call_to_action(ROOT, PURPOSE)
        self.assertTrue(cta.get("grounded"), cta)
        self.assertIn(cta["kind"], explore.KIND_ORDER)
        self.assertTrue(cta["move"])
        # marked proposed-tier, never minted (the grip floor)
        self.assertEqual(cta["provenance"], explore.PROPOSED)
        self.assertNotEqual(cta["provenance"], "minted")
        # every emitted antecedent actually resolves on disk (research over priors)
        self.assertTrue(cta["antecedents"])
        for ev in cta["antecedents"]:
            self.assertTrue(resolve_evidence(REPO, ev).get("resolved"), ev)

    def test_ungrounded_candidate_is_refused(self):
        fake = {"kind": "announce-piece", "subject": "atom.fabricated.v0",
                "move": "do a thing", "toward": PURPOSE,
                "antecedents": [{"file": "nowhere/nope.json",
                                 "contains": "atom.fabricated.v0",
                                 "source": "fabricated"}]}
        out = explore.ground(REPO, fake)
        self.assertFalse(out.get("grounded"))
        self.assertEqual(out["kind"], "refused-ungrounded")
        self.assertTrue(out["unresolved"])

    def test_constant_emitter_cannot_pass(self):
        # a constant CTA whose antecedents resolve to nothing is refused — the
        # fold cannot fabricate a grounded call to action (§10).
        constant = {"kind": "ready-for-confirm", "subject": PURPOSE,
                    "move": "ship it", "toward": PURPOSE,
                    "antecedents": [{"file": ".ai-native/log/events.jsonl",
                                     "contains": "NOT-ON-THE-LOG-zzzzz",
                                     "source": "log"}]}
        self.assertFalse(explore.ground(REPO, constant).get("grounded"))

    def test_no_purpose_is_needs_you(self):
        out = explore.call_to_action(ROOT, "epic.does-not-exist-zzz")
        self.assertFalse(out.get("grounded"))
        self.assertEqual(out["kind"], "needs-purpose")

    def test_writes_nothing(self):
        logdir = ROOT / "log"
        before = {p.name: p.read_bytes() for p in logdir.glob("*.jsonl")}
        explore.call_to_action(ROOT, PURPOSE)
        after = {p.name: p.read_bytes() for p in logdir.glob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
