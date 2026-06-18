"""Tests for the value-gate eval against done-line 0116: does the L0 gate
bite, and is the eval itself toothed?

The §10 teeth are three failure modes the scorer MUST catch — a soft gate,
a paranoid gate, and a brittle gate — plus the corpus being well-formed.
Transcripts are synthesized from the real corpus so the test and the
shipped cases never drift. The harness writes nothing.
"""

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import gate_eval

CORPUS = gate_eval.load_corpus()


def transcript(verdict_for, k=3):
    """A panel transcript: k identical verdicts per variant, the verdict
    chosen by verdict_for(case, turn)."""
    t = {}
    for case in CORPUS["cases"]:
        t[case["id"]] = {str(turn["turn"]): [verdict_for(case, turn)] * k
                         for turn in case["turns"]}
    return t


class TestCorpusWellFormed(unittest.TestCase):
    def test_corpus_shape(self):
        cases = CORPUS["cases"]
        self.assertGreaterEqual(len(cases), 4)
        controls = [c for c in cases if c["expected"] == gate_eval.ACCEPT]
        rejects = [c for c in cases if c["expected"] != gate_eval.ACCEPT]
        self.assertGreaterEqual(len(controls), 1, "need an accept control")
        self.assertTrue(rejects, "need reject cases")
        for c in cases:
            self.assertIn(c["expected"], gate_eval.TERMINAL_VERDICTS)
            # every reject case carries a 3-turn matched-variant axis
            if c["expected"] != gate_eval.ACCEPT:
                self.assertEqual(len(c["turns"]), 3, f"{c['id']} needs 3 turns")
            for turn in c["turns"]:
                self.assertIn("story", turn["atom"])  # atom-shaped stub

    def test_reject_buckets_span_the_set(self):
        """The reject cases cover the gate's three non-accept verdicts —
        an eval that only tested reject_no_value would miss two-thirds of
        what the gate can decide."""
        expecteds = {c["expected"] for c in CORPUS["cases"]}
        self.assertEqual(
            expecteds,
            {"accept", "reject_no_value", "reject_wrong_value", "amend"})


class TestScorerTeeth(unittest.TestCase):
    def test_rubber_stamp_gate_fails(self):
        """§10: a room that ACCEPTS everything must FAIL the eval — every
        should-reject turn went unbitten."""
        result = gate_eval.score(CORPUS, transcript(lambda c, t: "accept"))
        self.assertFalse(result["pass"])
        self.assertEqual(result["catch_rate"], 0.0)

    def test_paranoid_gate_fails_on_the_control(self):
        """§10: a room that REJECTS everything must FAIL — it refused the
        genuine control. A gate that bites everything is as broken as one
        that bites nothing."""
        result = gate_eval.score(CORPUS, transcript(lambda c, t: "reject_no_value"))
        self.assertFalse(result["pass"])
        control = next(c for c in result["cases"]
                       if c["expected"] == gate_eval.ACCEPT)
        self.assertFalse(control["case_pass"])

    def test_brittle_gate_is_flagged(self):
        """§10: a room that bites turn 1 but waves the dressed-up turn 3
        through is BRITTLE — the surface_trap fooled it. It must fail AND
        be named brittle, not silently pass."""
        def verdict_for(case, turn):
            if case["expected"] == gate_eval.ACCEPT:
                return "accept"
            # bite the early turns, get fooled by the last (dressed-up) one
            return "accept" if turn["turn"] == 3 else case["expected"]
        result = gate_eval.score(CORPUS, transcript(verdict_for))
        self.assertFalse(result["pass"])
        brittle = [c["id"] for c in result["cases"] if c["brittle"]]
        self.assertTrue(brittle, "a turn-3 miss after early bites must read brittle")

    def test_discriminating_robust_gate_passes(self):
        """A room that bites every should-reject turn in the right bucket and
        accepts the control passes with a perfect catch-rate."""
        result = gate_eval.score(CORPUS, transcript(lambda c, t: c["expected"]))
        self.assertTrue(result["pass"])
        self.assertEqual(result["catch_rate"], 1.0)
        for c in result["cases"]:
            for pt in c["turns"]:
                self.assertTrue(pt["bucket_match"])

    def test_a_bite_in_the_wrong_bucket_still_counts_as_a_bite(self):
        """Refusing for the wrong reason still bites (the gate said no) — it
        passes the catch bar but does not bucket-match. The two signals are
        distinct on purpose."""
        def verdict_for(case, turn):
            return "accept" if case["expected"] == gate_eval.ACCEPT else "amend"
        result = gate_eval.score(CORPUS, transcript(verdict_for))
        # every reject case bit (amend != accept) -> overall passes the catch bar
        self.assertTrue(result["pass"])
        # but the no-value / wrong-value cases did not bucket-match
        nv = next(c for c in result["cases"] if c["id"] == "no-value-scratchpad")
        self.assertTrue(all(pt["bit"] for pt in nv["turns"]))
        self.assertFalse(all(pt["bucket_match"] for pt in nv["turns"]))


class TestCoverage(unittest.TestCase):
    def test_unrun_case_is_not_a_soft_gate_failure(self):
        """§10: a case with empty rooms is `not_run`, NOT a soft-gate FAIL.
        The scorer must never read 'I didn't run this' as 'the gate is soft'
        — the exact false positive the first live run exposed. Running only
        the no-value case + control (both correct) passes over run cases,
        un-dragged by the two unrun cases."""
        t = {}
        for case in CORPUS["cases"]:
            if case["id"] in ("no-value-scratchpad", "control-genuine"):
                t[case["id"]] = {str(turn["turn"]): [case["expected"]] * 3
                                 for turn in case["turns"]}
        result = gate_eval.score(CORPUS, t)
        status = {c["id"]: c["status"] for c in result["cases"]}
        self.assertEqual(status["wrong-seam-perf"], "not_run")
        self.assertEqual(status["amend-value-hidden"], "not_run")
        self.assertTrue(result["pass"], "run cases passed; not_run must not drag it down")
        self.assertEqual(result["coverage"], {"run": 2, "total": 4})
        self.assertEqual(result["catch_rate"], 1.0)

    def test_empty_transcript_does_not_pass(self):
        """No cases run = nothing proven; overall is not a pass."""
        result = gate_eval.score(CORPUS, {})
        self.assertFalse(result["pass"])
        self.assertEqual(result["coverage"]["run"], 0)


class TestReception(unittest.TestCase):
    def test_majority_is_the_room(self):
        rec = gate_eval.reception(["reject_no_value", "reject_no_value", "accept"])
        self.assertEqual(rec["verdict"], "reject_no_value")
        self.assertEqual(rec["n"], 3)

    def test_empty_room_has_no_verdict(self):
        """An empty room is an absence, never a guessed verdict."""
        self.assertIsNone(gate_eval.reception([])["verdict"])


if __name__ == "__main__":
    unittest.main()
