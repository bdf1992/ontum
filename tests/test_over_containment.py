"""Tests for the over-containment counter-test — the shared shadow of T6 and
T7 (action-space and representation-space over-containment).

The §10 teeth are the discriminator, and each is a test:

- a trivially-stable signal (high coherence, but NOTHING risky/novel ever
  reached it) is FLAGGED as trivial-overcontainment — stable because untouched;
- a predictively-stable signal (variety reached it AND coherence rose from a
  low start under that input) PASSES as predictive;
- a FABRICATED signal that asserts predictiveness (and even asserts a coherence
  rise) but recorded NO trial is caught — the detector ignores the assertion and
  flags it on the `tested` leg. This is the line a vacuous classifier cannot
  hold: trust the claim and the test goes red.

The non-vacuousness proof (`test_check_is_not_vacuous`) shows that if the
`tested` leg is dropped — predictiveness read off coherence alone — the
fabricated input would wrongly pass. The test asserts the real classifier does
NOT, so weakening the check fails the suite.
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import over_containment as oc


def predictive_signal():
    """Earned stabilization: variety reached it and coherence rose from low."""
    return {
        "id": "action.gate.earned",
        "layer": "action",
        "coherence_start": 0.20,
        "coherence_now": 0.90,
        "trials": [
            {"novel": True, "refused": True},
            {"novel": True, "refused": False},
            {"novel": True, "refused": True},
        ],
    }


def trivial_signal():
    """The shadow: high coherence, but nothing risky ever reached it."""
    return {
        "id": "action.gate.untouched",
        "layer": "action",
        "coherence_start": 0.95,
        "coherence_now": 0.98,
        "trials": [],
    }


def fabricated_signal():
    """Asserts predictiveness AND a coherence rise, yet recorded no trial —
    a locally-fine-looking signal that must REFUSE to fit as predictive."""
    return {
        "id": "representation.class.pretender",
        "layer": "representation",
        "claimed_predictive": True,      # the assertion the detector must ignore
        "predictive": True,              # belt and suspenders — still ignored
        "coherence_start": 0.10,         # asserts the rise...
        "coherence_now": 0.99,           # ...to a high stable value
        "trials": [],                    # ...but nothing ever tested it
    }


class TestPredictiveStabilization(unittest.TestCase):
    def test_earned_stabilization_passes_as_predictive(self):
        r = oc.classify(predictive_signal())
        self.assertEqual(r["kind"], "predictive")
        self.assertTrue(r["tested"])
        self.assertTrue(r["rose"])
        self.assertTrue(r["stable"])

    def test_evidence_cites_measured_values_not_prose(self):
        """The finding names its own check — coherence values and trial counts,
        the line a constant classifier cannot fake."""
        r = oc.classify(predictive_signal())
        blob = " ".join(r["evidence"])
        self.assertIn("0.20", blob)
        self.assertIn("0.90", blob)
        self.assertIn("3 trial", blob)


class TestTrivialOverContainment(unittest.TestCase):
    def test_untested_high_coherence_is_flagged(self):
        """§10: a stabilization no variety ever reached is over-containment,
        however high its coherence — stable because untouched."""
        r = oc.classify(trivial_signal())
        self.assertEqual(r["kind"], "trivial-overcontainment")
        self.assertFalse(r["tested"])

    def test_incumbent_only_trials_do_not_count_as_tested(self):
        """A trial that is neither novel nor a refusal is exactly what the
        signal already expects — it cannot test a stabilization. A signal
        with only incumbent trials is still untested -> over-contained."""
        s = trivial_signal()
        s["trials"] = [{"novel": False, "refused": False},
                       {"novel": False, "refused": False}]
        r = oc.classify(s)
        self.assertEqual(r["kind"], "trivial-overcontainment")
        self.assertFalse(r["tested"])


class TestFabricatedInputIsCaught(unittest.TestCase):
    def test_asserted_predictiveness_without_a_test_is_refused(self):
        """The deliberately bad input: it claims to be predictive and even
        claims the coherence rise, but no trial ever reached it. The detector
        must derive, not trust — so it flags it."""
        r = oc.classify(fabricated_signal())
        self.assertEqual(r["kind"], "trivial-overcontainment")
        self.assertFalse(r["tested"])

    def test_check_is_not_vacuous(self):
        """Proof the `tested` leg is load-bearing. The fabricated signal has a
        coherence rise large enough to satisfy the `rose` leg and a high
        coherence_now satisfying `stable` — so a classifier that read
        predictiveness off coherence ALONE (dropping the `tested` leg) would
        wrongly pass it. We assert: the rise/stable legs ARE satisfied, yet the
        real classifier still refuses. If someone weakens classify() to ignore
        `tested`, this fabricated input would flip to predictive and this test
        goes red — the check has teeth."""
        s = fabricated_signal()
        r = oc.classify(s)
        # the two legs a coherence-only check would rely on are both true...
        self.assertTrue(r["stable"], "fabricated input IS stable")
        self.assertTrue(r["rose"], "fabricated input DOES show a rise from low")
        # ...yet it is refused, because the load-bearing `tested` leg fails.
        self.assertFalse(r["tested"])
        self.assertEqual(r["kind"], "trivial-overcontainment")

    def test_one_real_test_flips_the_same_signal_to_predictive(self):
        """The mirror image: take the fabricated signal and give it ONE genuine
        variety trial. Now it IS tested, and with its rise and stability it
        earns `predictive`. This proves the verdict turns on the test reaching
        it, not on anything asserted — the discriminator is the test itself."""
        s = fabricated_signal()
        s["trials"] = [{"novel": True, "refused": True}]
        r = oc.classify(s)
        self.assertTrue(r["tested"])
        self.assertEqual(r["kind"], "predictive")


class TestSurveyAndShape(unittest.TestCase):
    def test_survey_separates_the_two_kinds(self):
        d = oc.survey()
        self.assertEqual(d["scanned"], d["predictive"] + d["over_containment"])
        # the bundled samples include both shadows and at least one earned one
        self.assertGreaterEqual(d["over_containment"], 1)
        self.assertGreaterEqual(d["predictive"], 1)

    def test_classify_returns_only_the_two_named_kinds(self):
        for s in oc.SAMPLE_SIGNALS:
            self.assertIn(oc.classify(s)["kind"],
                          {"predictive", "trivial-overcontainment"})


if __name__ == "__main__":
    unittest.main()
