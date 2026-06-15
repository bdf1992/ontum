#!/usr/bin/env python3
"""§10 test for the energy-per-act fold (done-line 0080).

The teeth, each from the done-line's bar:

  1. strain separates locally-valid receipts that refuse to fit one productive
     picture — a clean act, a burned act (beat spent, no yield), a fallback act
     (a second act's energy for one answer);
  2. tempo is computed over yielding acts only — a burned act's huge latency can
     never masquerade as throughput;
  3. division-by-zero is impossible (an all-burned set yields tempo None);
  4. an absent `tokens` is absence, not zero (it does not become a 0 tok/s);
  5. an empty log folds to no acts (absence, not a crash, not a fake zero);
  6. and a controlled literal on the *real* committed log — the qwen3 timeout
     rcp.eacd7effeb7b (182s, zero tokens, issues #95/#96) reads as burned.
"""

import json
import tempfile
import unittest
from pathlib import Path

from loop import energy as E
from loop.energy import (energy, energy_acts, group_by, is_burned, strain,
                         summarize)


def _acts(*receipts):
    """The act view of raw receipts — the fold's front door, no log needed."""
    return energy_acts(list(receipts))


CLEAN = {"id": "r.clean", "latency_ms": 1000, "tokens": 50, "outcome": "ok",
         "mind": "local.mistral", "type": "inference"}
BURNED = {"id": "r.burned", "latency_ms": 182000, "tokens": None,
          "outcome": "error", "mind": "local.qwen3-14b", "type": "inference"}
FALLBACK = {"id": "r.fallback", "latency_ms": 60000, "tokens": 56,
            "outcome": "ok", "mind": "local.mistral",
            "fallback_from": "local.qwen3-14b", "type": "inference"}


class Strain(unittest.TestCase):
    """Three locally-valid receipts refuse to fit one picture; the fold names
    each strain rather than averaging it away (teeth 1)."""

    def test_burned_and_fallback_are_separated(self):
        acts = _acts(CLEAN, BURNED, FALLBACK)
        st = strain(acts)
        self.assertEqual(st["burned_ids"], ["r.burned"])
        self.assertEqual(st["fallback_ids"], ["r.fallback"])

    def test_clean_act_is_neither_burned_nor_fallback(self):
        self.assertFalse(is_burned(_acts(CLEAN)[0]))
        self.assertEqual(strain(_acts(CLEAN))["burned_ids"], [])
        self.assertEqual(strain(_acts(CLEAN))["fallback_ids"], [])

    def test_wasted_latency_is_the_burned_beat_only(self):
        st = strain(_acts(CLEAN, BURNED, FALLBACK))
        self.assertEqual(st["wasted_latency_ms"], 182000)  # only the burned one

    def test_an_errored_act_with_tokens_is_still_burned(self):
        # outcome trumps yield: an error that somehow carried tokens still
        # burned the beat for a non-answer.
        a = _acts({"id": "r.e", "latency_ms": 500, "tokens": 5,
                   "outcome": "error"})[0]
        self.assertTrue(is_burned(a))


class Tempo(unittest.TestCase):
    """Tempo counts only yielding acts; a burned giant cannot fake throughput
    and the divide can never explode (teeth 2 + 3)."""

    def test_burned_latency_excluded_from_tempo(self):
        # CLEAN alone: 50 tokens / 1.0s = 50 tok/s. Add the 182s burned act —
        # if its latency leaked into tempo, the figure would collapse.
        tempo_clean = summarize(_acts(CLEAN))["tempo_tokens_per_s"]
        tempo_with_burned = summarize(_acts(CLEAN, BURNED))["tempo_tokens_per_s"]
        self.assertAlmostEqual(tempo_clean, 50.0)
        self.assertAlmostEqual(tempo_with_burned, 50.0)  # burned 182s ignored

    def test_all_burned_set_has_no_tempo_not_a_crash(self):
        s = summarize(_acts(BURNED))           # would divide by zero if naive
        self.assertIsNone(s["tempo_tokens_per_s"])
        self.assertIsNone(s["mean_tokens"])
        self.assertEqual(s["total_tokens"], 0)

    def test_zero_latency_act_never_divides(self):
        s = summarize(_acts({"id": "r.0", "latency_ms": 0, "tokens": 10,
                             "outcome": "ok"}))
        self.assertIsNone(s["tempo_tokens_per_s"])  # no positive beat to divide


class AbsenceIsNotZero(unittest.TestCase):
    """An absent field is absence, never a fabricated zero (teeth 4)."""

    def test_absent_tokens_is_none_not_zero_rate(self):
        a = _acts(BURNED)[0]
        self.assertIsNone(a["tokens"])
        self.assertIsNone(a["tempo_tokens_per_s"])  # not 0.0

    def test_act_needs_a_beat(self):
        # a receipt with no latency_ms is not a measurable act at all.
        self.assertEqual(_acts({"id": "r.x", "tokens": 9, "outcome": "ok"}), [])

    def test_bool_is_not_a_number(self):
        # JSON true must never be read as latency 1.
        self.assertEqual(_acts({"id": "r.b", "latency_ms": True}), [])


class EmptyLog(unittest.TestCase):
    """A missing/empty log folds to no acts — absence, not a crash (teeth 5)."""

    def _root(self, lines=None):
        d = tempfile.mkdtemp()
        log = Path(d) / "log"
        log.mkdir()
        for f in ("events.jsonl", "admissions.jsonl"):
            (log / f).write_text("", encoding="utf-8")
        (log / "receipts.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in (lines or [])), encoding="utf-8")
        return Path(d)

    def test_empty_log_yields_no_acts(self):
        result = energy(root=self._root())
        self.assertEqual(result["acts"], [])
        self.assertEqual(result["summary"]["acts"], 0)
        self.assertIsNone(result["summary"]["tempo_tokens_per_s"])
        self.assertEqual(result["strain"]["wasted_latency_ms"], 0)

    def test_missing_log_dir_is_absence(self):
        d = tempfile.mkdtemp()  # no log/ at all
        self.assertEqual(energy(root=Path(d))["acts"], [])

    def test_fold_over_real_shaped_log(self):
        result = energy(root=self._root([CLEAN, BURNED, FALLBACK]))
        self.assertEqual(result["summary"]["acts"], 3)
        self.assertEqual(result["strain"]["burned_ids"], ["r.burned"])
        # grouped by mind: qwen3 burned 182s, mistral carried two acts
        self.assertIn("local.qwen3-14b", result["by_mind"])
        self.assertEqual(result["by_mind"]["local.qwen3-14b"]["acts"], 1)


class Determinism(unittest.TestCase):
    """The fold is pure over its input (teeth: a fabricated/constant metric
    fails — the numbers track the receipts)."""

    def test_grouping_is_deterministic_and_keyed(self):
        a = group_by(_acts(CLEAN, BURNED, FALLBACK), "outcome")
        b = group_by(_acts(CLEAN, BURNED, FALLBACK), "outcome")
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(set(a), {"ok", "error"})

    def test_summary_tracks_the_input_not_a_constant(self):
        one = summarize(_acts(CLEAN))
        two = summarize(_acts(CLEAN, CLEAN))
        self.assertEqual(one["total_latency_ms"], 1000)
        self.assertEqual(two["total_latency_ms"], 2000)


class RealCommittedLog(unittest.TestCase):
    """A controlled literal on the real log: the qwen3 timeout that jammed the
    inference plane (issues #95/#96) is on the record forever, and it reads as
    burned — the fold senses a real strain, not a fixture's (teeth 6)."""

    def test_qwen3_timeout_reads_as_burned(self):
        result = energy()  # the repo's own committed .ai-native
        self.assertIn("rcp.eacd7effeb7b", result["strain"]["burned_ids"],
                      "the real qwen3 182s/zero-token timeout must read burned")
        # and every burned act genuinely lacks a clean yield — no false positive
        for a in result["strain"]["burned"]:
            self.assertTrue(a["outcome"] != "ok" or a["tokens"] in (None, 0))
        # tempo over the real log never divides by a burned beat
        s = result["summary"]
        self.assertTrue(s["tempo_tokens_per_s"] is None
                        or s["tempo_tokens_per_s"] > 0)


if __name__ == "__main__":
    unittest.main()
