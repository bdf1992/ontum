"""Tests for the relation ledger against relation-ledger.v0: the record
substrate for the relational middle band — read-only, propose-grain.

The §10 teeth are the match check that separates a PREDICTIVE bucket (a
claim its receipts bear out) from a TRIVIAL one (a claim its receipts
refute), and each is a test:

- a predictive bucket and a trivial bucket fold to opposite verdicts off
  the SAME shaped records — the only difference is whether the observed
  consequence matches the predicted one;
- the fabricated always-coherent classifier is caught: substitute a
  matcher that reads every observation as a match through the `match`
  seam, and the refuted bucket falsely reads PREDICTIVE — proof the real
  `_matches` is what does the work, not the verdict machinery around it;
- a claim with no receipts is UNTESTED, never silently predictive;
- the schema door refuses a record missing a required field;
- the fold writes nothing (it takes in-memory lists; v0 has no log).
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import relation_ledger as rl


def claim(cid, bucket, predicted):
    return {"id": cid, "bucket": bucket, "predicted_consequence": predicted}


def receipt(rid, bucket, observed):
    return {"id": rid, "bucket": bucket, "observed_consequence": observed}


def verdict_of(d, bucket):
    return next(r["verdict"] for r in d["buckets"] if r["bucket"] == bucket)


class TestPredictiveVsTrivial(unittest.TestCase):
    def test_borne_out_bucket_is_predictive(self):
        """A claim a majority of receipts bear out reads PREDICTIVE."""
        d = rl.coherence_report(
            [claim("c.warm", "warm", "expands")],
            [receipt("r1", "warm", "expands"),
             receipt("r2", "warm", "expands"),
             receipt("r3", "warm", "contracts")],
        )
        self.assertEqual(verdict_of(d, "warm"), rl.PREDICTIVE)

    def test_refuted_bucket_is_trivial(self):
        """The discriminator: the SAME shape, but the receipts refute the
        claim (none observe the prediction) — TRIVIAL, not predictive."""
        d = rl.coherence_report(
            [claim("c.warm", "warm", "expands")],
            [receipt("r1", "warm", "contracts"),
             receipt("r2", "warm", "contracts"),
             receipt("r3", "warm", "shatters")],
        )
        self.assertEqual(verdict_of(d, "warm"), rl.TRIVIAL)

    def test_predictive_and_trivial_separate_in_one_fold(self):
        """Both at once: the fold pulls the predictive bucket apart from the
        trivial one — the live split the organ exists to draw."""
        d = rl.coherence_report(
            [claim("c.warm", "warm", "expands"),
             claim("c.coin", "coin", "heads")],
            [receipt("w1", "warm", "expands"), receipt("w2", "warm", "expands"),
             receipt("c1", "coin", "heads"), receipt("c2", "coin", "tails")],
        )
        self.assertEqual(verdict_of(d, "warm"), rl.PREDICTIVE)
        self.assertEqual(verdict_of(d, "coin"), rl.TRIVIAL)  # 1/2 == not a majority
        self.assertEqual(d["predictive_fraction"], 0.5)

    def test_coin_flip_is_not_predictive(self):
        """A relation that holds no better than chance (exactly half borne
        out) compresses nothing — the bar is strict-majority, so 0.5 is
        TRIVIAL. If COHERENCE_BAR were dropped to <0.5 this would flip."""
        d = rl.coherence_report(
            [claim("c.coin", "coin", "heads")],
            [receipt("c1", "coin", "heads"), receipt("c2", "coin", "tails")],
        )
        self.assertEqual(verdict_of(d, "coin"), rl.TRIVIAL)


class TestMatchCheckIsNonVacuous(unittest.TestCase):
    """The mandated §10 teeth: prove the match check is load-bearing."""

    REFUTED = ([claim("c.warm", "warm", "expands")],
               [receipt("r1", "warm", "contracts"),
                receipt("r2", "warm", "shatters")])

    def test_real_matcher_reads_refuted_bucket_as_trivial(self):
        d = rl.coherence_report(*self.REFUTED)
        self.assertEqual(verdict_of(d, "warm"), rl.TRIVIAL)
        self.assertEqual(d["buckets"][0]["coherence_rate"], 0.0)

    def test_fabricated_always_coherent_matcher_falsely_reads_predictive(self):
        """Neutralize the check — a classifier that reads EVERY observation as
        a match — and the refuted bucket falsely reads PREDICTIVE. This is the
        bug the real `_matches` prevents; that the verdict flips here is the
        proof the check, not the surrounding machinery, separates the two."""
        fabricated = lambda observed, predicted: True
        d = rl.coherence_report(*self.REFUTED, match=fabricated)
        self.assertEqual(verdict_of(d, "warm"), rl.PREDICTIVE)
        self.assertEqual(d["buckets"][0]["coherence_rate"], 1.0)
        # and the two disagree — so the matcher is what decides the verdict
        real = rl.coherence_report(*self.REFUTED)
        self.assertNotEqual(verdict_of(real, "warm"), verdict_of(d, "warm"))


class TestHonestAbsences(unittest.TestCase):
    def test_claim_without_receipts_is_untested(self):
        d = rl.coherence_report([claim("c.warm", "warm", "expands")], [])
        self.assertEqual(verdict_of(d, "warm"), rl.UNTESTED)

    def test_receipts_without_claim_are_unclaimed(self):
        d = rl.coherence_report([], [receipt("r1", "warm", "expands")])
        self.assertEqual(verdict_of(d, "warm"), rl.UNCLAIMED)

    def test_zero_records_folds_clean(self):
        """Declared even at zero live records (the cool-valve grain)."""
        d = rl.coherence_report([], [])
        self.assertEqual(d["buckets"], [])
        self.assertEqual(d["predictive_fraction"], 0.0)


class TestSchemaDoor(unittest.TestCase):
    def test_five_kinds_declared(self):
        self.assertEqual(
            set(rl.SCHEMA),
            {"relation_claim", "relation_probe", "consequence_receipt",
             "model_candidate", "bucket_coherence_report"},
        )

    def test_record_missing_required_field_is_refused(self):
        complaints = rl.validate_record(
            "relation_claim", {"id": "c.x", "bucket": "warm"})  # no predicted_consequence
        self.assertTrue(complaints)
        self.assertIn("predicted_consequence", " ".join(complaints))

    def test_well_formed_record_passes_the_door(self):
        self.assertEqual(
            rl.validate_record("relation_claim", claim("c.x", "warm", "expands")), [])

    def test_unknown_kind_is_refused(self):
        self.assertTrue(rl.validate_record("not_a_kind", {"id": "x"}))


class TestReadOnly(unittest.TestCase):
    def test_fold_does_not_mutate_its_inputs(self):
        claims = [claim("c.warm", "warm", "expands")]
        receipts = [receipt("r1", "warm", "expands")]
        before = (list(map(dict, claims)), list(map(dict, receipts)))
        rl.coherence_report(claims, receipts)
        self.assertEqual(([dict(c) for c in claims], [dict(r) for r in receipts]),
                         before)


if __name__ == "__main__":
    unittest.main()
