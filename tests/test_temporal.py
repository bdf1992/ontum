#!/usr/bin/env python3
"""§10 test for the temporal-pressure fold (done-line 0071).

The teeth, each from the done-line's bar:

  1. a malformed schedule — a gap or an overlap across the 24h — is refused
     (a schedule that does not tile the day cannot classify a moment in it);
  2. different moments yield different registers (no constant classifier);
  3. the modulation is deterministic given a fixed moment;
  4. a probe's met/partial/unmet truth is identical across every band — time
     changes emphasis, never reality;
  5. and the point of the whole thing: the same committed Causality probe-set
     is re-emphasised differently in the morning (heat -> the big unblocker)
     than in the evening (cool -> the nearest-closeable leaf).
"""

import json
import tempfile
import unittest
from pathlib import Path

from loop import temporal as T
from loop.temporal import (DEFAULT_SCHEDULE, load_schedule, modulate,
                           register_at, temporal, validate_schedule)


class Schedule(unittest.TestCase):
    """A schedule must tile [0,24); a gap or overlap is refused (teeth 1)."""

    def test_default_schedule_is_clean(self):
        self.assertEqual(validate_schedule(DEFAULT_SCHEDULE), [])

    def test_gap_refused(self):
        bands = [{"start": 0, "end": 5, "register": "a", "lean": "cool"},
                 {"start": 6, "end": 24, "register": "b", "lean": "heat"}]
        problems = validate_schedule(bands)
        self.assertTrue(any("gap" in p for p in problems))

    def test_overlap_refused(self):
        bands = [{"start": 0, "end": 10, "register": "a", "lean": "cool"},
                 {"start": 5, "end": 24, "register": "b", "lean": "heat"}]
        problems = validate_schedule(bands)
        self.assertTrue(any("overlap" in p for p in problems))

    def test_incomplete_coverage_refused(self):
        bands = [{"start": 0, "end": 20, "register": "a", "lean": "cool"}]
        problems = validate_schedule(bands)
        self.assertTrue(any("not fully tiled" in p or "24" in p for p in problems))

    def test_bad_lean_refused(self):
        bands = [{"start": 0, "end": 24, "register": "a", "lean": "lukewarm"}]
        self.assertTrue(any("lean" in p for p in validate_schedule(bands)))

    def test_empty_refused(self):
        self.assertTrue(validate_schedule([]))

    def test_admitted_malformed_schedule_refused_falls_to_default(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "log"
            log.mkdir()
            (log / "events.jsonl").write_text("", encoding="utf-8")
            (log / "receipts.jsonl").write_text("", encoding="utf-8")
            rec = {"id": "adm.bad", "type": "temporal_schedule",
                   "bands": [{"start": 0, "end": 20, "register": "x",
                              "lean": "cool"}]}  # gap 20-24
            (log / "admissions.jsonl").write_text(json.dumps(rec) + "\n",
                                                  encoding="utf-8")
            schedule, source, problems = load_schedule(Path(d))
            self.assertEqual(schedule, DEFAULT_SCHEDULE)
            self.assertTrue(problems)
            self.assertIn("refused", source)

    def test_admitted_valid_schedule_used(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "log"
            log.mkdir()
            (log / "events.jsonl").write_text("", encoding="utf-8")
            (log / "receipts.jsonl").write_text("", encoding="utf-8")
            bands = [{"start": 0, "end": 24, "register": "always",
                      "lean": "steady"}]
            rec = {"id": "adm.ok", "type": "temporal_schedule", "bands": bands}
            (log / "admissions.jsonl").write_text(json.dumps(rec) + "\n",
                                                  encoding="utf-8")
            schedule, source, problems = load_schedule(Path(d))
            self.assertEqual(schedule, bands)
            self.assertEqual(problems, [])
            self.assertIn("admitted", source)


class Classify(unittest.TestCase):
    """Different moments fall in different registers (teeth 2)."""

    def test_morning_and_evening_differ(self):
        morning = register_at(8, DEFAULT_SCHEDULE)
        evening = register_at(20, DEFAULT_SCHEDULE)
        self.assertNotEqual(morning["register"], evening["register"])
        self.assertEqual(morning["lean"], "heat")
        self.assertEqual(evening["lean"], "cool")

    def test_every_hour_lands_in_exactly_one_band(self):
        # a clean tiling: every hour 0..23 classifies, and to one band.
        for h in range(24):
            self.assertIsNotNone(register_at(h, DEFAULT_SCHEDULE))

    def test_hour_wraps(self):
        self.assertEqual(register_at(25, DEFAULT_SCHEDULE),
                         register_at(1, DEFAULT_SCHEDULE))


def _synthetic_pressure():
    """A minimal pressure result: A is depended on by B (leverage 1); L is a
    leaf (leverage 0). No probe is met. Enough to exercise modulation."""
    return {
        "by_id": {
            "A": {"class": "cap", "depends": [], "move": "mA", "statement": "A"},
            "B": {"class": "cap", "depends": ["A"], "move": "mB", "statement": "B"},
            "L": {"class": "cap", "depends": [], "move": "mL", "statement": "L"},
        },
        "state": {"A": "unmet", "B": "unmet", "L": "unmet"},
        "met": [], "partial": [], "unmet": ["A", "B", "L"], "dormant": [],
        "top_leverage": {"id": "A"}, "next_move": "x",
    }


class Modulate(unittest.TestCase):
    """heat favours the big unblocker; cool favours the closeable leaf —
    deterministically, and without touching truth (teeth 3 + 4)."""

    HEAT = {"register": "m", "lean": "heat", "quality": "q"}
    COOL = {"register": "e", "lean": "cool", "quality": "q"}

    def test_heat_focuses_the_unblocker(self):
        v = modulate(_synthetic_pressure(), self.HEAT)
        self.assertEqual(v["focus"], "A")        # most dependents

    def test_cool_focuses_the_leaf(self):
        v = modulate(_synthetic_pressure(), self.COOL)
        self.assertEqual(v["focus"], "L")        # nearest-closeable, unblocks none

    def test_lean_changes_the_focus(self):
        heat = modulate(_synthetic_pressure(), self.HEAT)["focus"]
        cool = modulate(_synthetic_pressure(), self.COOL)["focus"]
        self.assertNotEqual(heat, cool)

    def test_deterministic(self):
        a = modulate(_synthetic_pressure(), self.HEAT)
        b = modulate(_synthetic_pressure(), self.HEAT)
        self.assertEqual(a, b)

    def test_modulate_does_not_mutate_truth(self):
        pr = _synthetic_pressure()
        before = json.dumps(pr, sort_keys=True)
        modulate(pr, self.COOL)
        self.assertEqual(json.dumps(pr, sort_keys=True), before)


class TruthInvariant(unittest.TestCase):
    """A probe's met/partial/unmet truth is identical at every hour over the
    real committed Causality set — the clock never moves reality (teeth 4)."""

    def test_pressure_truth_constant_across_the_day(self):
        baselines = None
        for h in (3, 8, 14, 20, 23):
            pr = temporal(h)["pressure"]
            snap = (tuple(sorted(pr["met"])), tuple(sorted(pr["partial"])),
                    tuple(sorted(pr["unmet"])), tuple(sorted(pr["dormant"])),
                    pr["phase"])
            if baselines is None:
                baselines = snap
            self.assertEqual(snap, baselines,
                             f"pressure truth changed at hour {h}")


class RealCausalitySet(unittest.TestCase):
    """The point: the same committed probe-set re-emphasised by the hour
    (teeth 5). Morning heat takes the unblocker (the fold's top leverage);
    evening cool takes a different, closeable leaf; both over one unchanged
    build-phase truth. The specific ids move as probes resolve (CZ1→CZ2→CZ3…),
    so this pins the *relationship* — heat names the leverage, cool names
    something else, the clock never moves the truth — not the snapshot id."""

    def test_morning_vs_evening_emphasis(self):
        morning = temporal(8)
        evening = temporal(20)
        self.assertEqual(morning["temporal"]["lean"], "heat")
        self.assertEqual(evening["temporal"]["lean"], "cool")
        # heat takes the unblocker the fold ranks top; cool takes a leaf that
        # differs from it — the hour re-emphasises the same truth differently
        self.assertEqual(morning["temporal"]["focus"],
                         morning["pressure"]["top_leverage"]["id"])
        self.assertNotEqual(evening["temporal"]["focus"],
                            morning["temporal"]["focus"])
        # same underlying truth, different emphasis: build phase and the same
        # top leverage at both hours (the clock never moves reality)
        self.assertEqual(morning["pressure"]["phase"], "build")
        self.assertEqual(evening["pressure"]["phase"], "build")
        self.assertEqual(morning["pressure"]["top_leverage"]["id"],
                         evening["pressure"]["top_leverage"]["id"])
        self.assertNotEqual(morning["temporal"]["next_move"],
                            evening["temporal"]["next_move"])


if __name__ == "__main__":
    unittest.main()
