#!/usr/bin/env python3
"""§10 test for Causality's welcome mat (done-line 0095).

The mat must be *capable of carrying* the felt-field — which means it folds the
field from real records, never paints it. The teeth, each from the done-line:

  1. equality — every felt figure on the page is the number its fold emits
     (pulse count, total beat, tempo, lean, register all trace to the fold);
  2. no-fabrication — the page (and the anima mood) reflect DIFFERENT fixtures
     differently: a hardcoded constant cannot satisfy two logs, nor two hours;
  3. strain (the refusal) — a clean act and a burned act, each locally valid,
     refuse to fit one "all is well" first impression: the page shows the strain
     and the mood goes weak, rather than averaging it to calm;
  4. absence — an empty log renders "absence" (mood None), not a fake tempo;
  5. projection — there is no write path: the source carries no log-writing
     symbol (Causality is never a second source of truth).
"""

import json
import tempfile
import unittest
from pathlib import Path

from causality import welcome as W
from causality.welcome import _ms, _tempo_rate, felt_field, mood, render_html
from loop.energy import energy
from loop.temporal import load_schedule, register_at

CLEAN = {"id": "r.clean", "latency_ms": 1000, "tokens": 50, "outcome": "ok",
         "mind": "local.mistral", "type": "inference"}
CLEAN2 = {"id": "r.clean2", "latency_ms": 3000, "tokens": 90, "outcome": "ok",
          "mind": "local.mistral", "type": "inference"}
CLEAN3 = {"id": "r.clean3", "latency_ms": 2000, "tokens": 30, "outcome": "ok",
          "mind": "local.mistral", "type": "inference"}
BURNED = {"id": "r.burned", "latency_ms": 182000, "tokens": None,
          "outcome": "error", "mind": "local.qwen3-14b", "type": "inference"}


def _root(d, *receipts):
    """A fixture records root with a populated receipts log (the energy/temporal
    fixture grain — tempdir + log/ + the three jsonl files)."""
    log = Path(d) / "log"
    log.mkdir()
    (log / "events.jsonl").write_text("", encoding="utf-8")
    (log / "receipts.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts), encoding="utf-8")
    (log / "admissions.jsonl").write_text("", encoding="utf-8")
    return Path(d)


class Equality(unittest.TestCase):
    """Teeth 1: every felt figure on the page equals its fold's value."""

    def test_every_figure_traces_to_the_fold(self):
        with tempfile.TemporaryDirectory() as d:
            root = _root(d, CLEAN, CLEAN2)
            hour = 8  # dawn-explore, heat
            page = render_html(root, hour)

            e = energy(root=root)["summary"]
            schedule, _, _ = load_schedule(root)
            band = register_at(hour, schedule)

            self.assertEqual(e["acts"], 2)
            self.assertIn(f'class="fig">{e["acts"]}', page)            # pulse count
            self.assertIn(_ms(e["total_latency_ms"]), page)            # total beat
            self.assertIn(_ms(e["median_latency_ms"]), page)           # median beat
            self.assertIn(_tempo_rate(e["tempo_tokens_per_s"]), page)  # tempo
            self.assertIn(f'{e["total_tokens"]} tok', page)            # yield
            self.assertIn(band["lean"], page)                          # rhythm lean
            self.assertIn(band["register"], page)                      # rhythm register
            # recent act ids, freshest first (match </code> so "r.clean" can't
            # match inside "r.clean2")
            self.assertIn("r.clean2</code>", page)
            self.assertLess(page.index("r.clean2</code>"),
                            page.index("r.clean</code>"))


class NoFabrication(unittest.TestCase):
    """Teeth 2: a constant cannot satisfy two different logs, nor two hours —
    and the anima mood tracks the folds too, not a fixed word."""

    def test_pulse_count_tracks_the_log_not_a_constant(self):
        with tempfile.TemporaryDirectory() as d2:
            root2 = _root(d2, CLEAN, CLEAN2)
            two = render_html(root2, 8)
            beat2 = energy(root=root2)["summary"]["total_latency_ms"]
            with tempfile.TemporaryDirectory() as d3:
                root3 = _root(d3, CLEAN, CLEAN2, CLEAN3)
                three = render_html(root3, 8)
                beat3 = energy(root=root3)["summary"]["total_latency_ms"]
                self.assertIn('class="fig">2', two)
                self.assertIn('class="fig">3', three)
                self.assertNotEqual(beat2, beat3)
                self.assertIn(_ms(beat2), two)
                self.assertIn(_ms(beat3), three)

    def test_mood_tracks_tempo_and_strength_not_a_constant(self):
        with tempfile.TemporaryDirectory() as d:
            root = _root(d, CLEAN, CLEAN2)
            # same log, two hours -> tempo pole flips -> different mood
            vigorous = mood(felt_field(root, 8))    # heat -> fast + strong
            grounded = mood(felt_field(root, 20))   # cool -> slow + strong
            self.assertEqual(vigorous["name"], "vigorous")
            self.assertEqual(grounded["name"], "grounded")
            self.assertIn("vigorous", render_html(root, 8))
            self.assertNotIn("vigorous", render_html(root, 20))

    def test_strength_pole_tracks_strain(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            strong = mood(felt_field(_root(a, CLEAN, CLEAN2), 20))
            weak = mood(felt_field(_root(b, CLEAN, BURNED), 20))
            self.assertEqual(strong["strength"], "strong")   # all yielded
            self.assertEqual(weak["strength"], "weak")       # a burned act
            self.assertEqual(weak["name"], "guttering")      # slow + weak


class Strain(unittest.TestCase):
    """Teeth 3: a clean act and a burned act refuse to fit one calm picture."""

    def test_burned_act_surfaces_as_strain_not_averaged_away(self):
        with tempfile.TemporaryDirectory() as d:
            root = _root(d, CLEAN, BURNED)
            page = render_html(root, 8)
            st = energy(root=root)["strain"]
            self.assertEqual(st["burned_ids"], ["r.burned"])
            self.assertIn("strain", page)
            self.assertIn(_ms(st["wasted_latency_ms"]), page)  # 182.0s burned
            self.assertIn("r.burned", page)
            self.assertNotIn("no strain", page)

    def test_all_clean_reports_no_strain(self):
        with tempfile.TemporaryDirectory() as d:
            page = render_html(_root(d, CLEAN, CLEAN2), 8)
            self.assertIn("no strain", page)


class Absence(unittest.TestCase):
    """Teeth 4: an empty log is absence, not a fake figure; no mood to be in."""

    def test_empty_log_renders_absence_and_no_mood(self):
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)  # no receipts
            field = felt_field(root, 8)
            self.assertTrue(field["empty"])
            self.assertIsNone(mood(field))
            page = render_html(root, 8)
            self.assertIn("absence", page)
            self.assertNotIn("tok/s", page)  # no fabricated throughput


class Projection(unittest.TestCase):
    """Teeth 5: no second write path — the mat is read, never written through."""

    def test_source_carries_no_log_write_symbol(self):
        src = Path(W.__file__).read_text(encoding="utf-8")
        for forbidden in ("append_line", "loop.node", "judge(", "do_POST",
                           "receipts.jsonl"):
            self.assertNotIn(forbidden, src,
                             f"a welcome mat writes nothing — found {forbidden!r}")


if __name__ == "__main__":
    unittest.main()
