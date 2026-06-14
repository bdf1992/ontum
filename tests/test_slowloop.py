#!/usr/bin/env python3
"""§10 test for the slow loop's proposer (done-line 0074).

The teeth, each from the done-line's bar:

  1. propose != dispose: the proposer never mutates the log or the live
     setpoint — reading the field does not change it (it must not sign its own
     line);
  2. attribution-or-refused: every proposed change carries an evidence-bearing
     `because` (the cited tick / pressure / temporal signals); with no tick
     history there is nothing to attribute a change to, so it holds;
  3. caused by outcomes, not constant: a cool-leaning tick history proposes
     cooling and a hot history with build-phase leverage proposes heating —
     the proposal moves with the field, so a constant classifier fails;
  4. deterministic given fixed inputs.
"""

import json
import tempfile
import unittest
from pathlib import Path

from loop.reconcile import Fold
from loop.orchestrate import read_setpoint
from loop.slowloop import COOL_HI, MIN_BUDGET, fold_signals, propose, slowloop


SETPOINT = {"id": "adm.sp", "type": "setpoint", "dial": "orchestration.temperature",
            "value": {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                      "human_queue_cap": 2}, "by": "test-bdo", "supersedes": None,
            "ts": "t"}


def sig(cool_ratio, n=12, phase="build", leverage="CZ1", lean="steady",
        register="midday-build", unresolved=7):
    cool = round((cool_ratio if cool_ratio is not None else 0) * n)
    return {"ticks_considered": n, "cool_count": cool,
            "cool_ratio": cool_ratio, "deferred_total": 0, "phase": phase,
            "unresolved": unresolved, "leverage": leverage, "lean": lean,
            "register": register}


def make_root(tmp, ticks):
    """A records root with a setpoint and a tick history. `ticks` is a list of
    'cool'/'heat' modes."""
    root = Path(tmp)
    log = root / "log"
    log.mkdir()
    (log / "events.jsonl").write_text("", encoding="utf-8")
    (log / "receipts.jsonl").write_text("", encoding="utf-8")
    lines = [json.dumps(SETPOINT)]
    for i, mode in enumerate(ticks):
        lines.append(json.dumps({"id": f"adm.tick.{i}", "type": "tick",
                                 "tick": i, "mode": mode, "deferred": []}))
    (log / "admissions.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


class ProposeLogic(unittest.TestCase):
    """The proposal is caused by the folded outcomes (teeth 3), and always
    carries its attribution (teeth 2)."""

    def test_cool_heavy_history_proposes_cooling(self):
        p = propose(SETPOINT, sig(0.8))
        self.assertEqual(p["deltas"], {"step_budget_per_tick": -1})
        self.assertTrue(any("cool_ratio 0.80" in b for b in p["because"]))

    def test_hot_history_with_build_leverage_proposes_heating(self):
        p = propose(SETPOINT, sig(0.0))
        self.assertEqual(p["deltas"], {"step_budget_per_tick": 1})
        self.assertTrue(any("CZ1" in b for b in p["because"]))

    def test_hot_history_without_build_phase_holds(self):
        p = propose(SETPOINT, sig(0.0, phase="realize", leverage=None))
        self.assertEqual(p["change"], False)

    def test_balanced_field_cool_hour_proposes_cooling(self):
        p = propose(SETPOINT, sig(0.45, lean="cool", register="dusk-consolidate"))
        self.assertEqual(p["deltas"], {"step_budget_per_tick": -1})

    def test_balanced_field_heat_hour_proposes_heating(self):
        p = propose(SETPOINT, sig(0.45, lean="heat", register="dawn-explore"))
        self.assertEqual(p["deltas"], {"step_budget_per_tick": 1})

    def test_balanced_field_steady_hour_holds(self):
        p = propose(SETPOINT, sig(0.45, lean="steady"))
        self.assertEqual(p["change"], False)

    def test_every_proposal_carries_a_because(self):
        for cr in (0.0, 0.45, 0.8, None):
            p = propose(SETPOINT, sig(cr, n=(0 if cr is None else 12)))
            self.assertTrue(p["because"], f"no attribution for cool_ratio {cr}")

    def test_no_history_holds_and_says_why(self):
        # teeth 2: no outcomes -> nothing to attribute a change to -> refuse/hold
        p = propose(SETPOINT, sig(None, n=0))
        self.assertEqual(p["change"], False)
        self.assertTrue(any("no tick history" in b for b in p["because"]))

    def test_cooling_clamps_at_the_floor(self):
        floor_sp = {**SETPOINT, "value": {**SETPOINT["value"],
                                          "step_budget_per_tick": MIN_BUDGET}}
        p = propose(floor_sp, sig(0.9))
        self.assertEqual(p["change"], False)  # cannot cool below the floor
        self.assertTrue(any("floor" in b for b in p["because"]))

    def test_deterministic(self):
        self.assertEqual(propose(SETPOINT, sig(0.8)), propose(SETPOINT, sig(0.8)))


class ProposeNotDispose(unittest.TestCase):
    """Reading the field never changes it (teeth 1) — the proposer writes
    nothing and the live dial is untouched."""

    def test_slowloop_mutates_neither_log_nor_setpoint(self):
        with tempfile.TemporaryDirectory() as d:
            # a cool-heavy field proposes cooling regardless of phase, so this
            # exercises a real proposal without needing the probe-set on disk
            root = make_root(d, ["cool"] * 12)
            adm = root / "log" / "admissions.jsonl"
            before_bytes = adm.read_bytes()
            before_dial = read_setpoint(Fold(root).admissions)["value"]

            result = slowloop(root, hour=8)
            self.assertTrue(result["proposal"]["change"])  # it did propose

            self.assertEqual(adm.read_bytes(), before_bytes, "the log was mutated")
            self.assertEqual(read_setpoint(Fold(root).admissions)["value"],
                             before_dial, "the live dial moved")

    def test_no_admitted_setpoint_is_a_needs_you_not_a_guess(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "log").mkdir()
            for f in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
                (root / "log" / f).write_text("", encoding="utf-8")
            result = slowloop(root, hour=8)
            self.assertIsNone(result["setpoint"])
            self.assertIsNone(result["proposal"])


class FoldSignals(unittest.TestCase):
    """The tick history folds to the right cool_ratio — the causal spine."""

    def test_cool_ratio_from_ticks(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_root(d, ["cool"] * 9 + ["heat"] * 3)
            s = fold_signals(root, hour=8)
            self.assertEqual(s["ticks_considered"], 12)
            self.assertEqual(s["cool_count"], 9)
            self.assertAlmostEqual(s["cool_ratio"], 0.75)

    def test_end_to_end_cool_history_proposes_cooling(self):
        # the §10 path: a cool-heavy field, end to end, proposes consolidation
        with tempfile.TemporaryDirectory() as d:
            root = make_root(d, ["cool"] * 10)
            result = slowloop(root, hour=12)
            self.assertGreaterEqual(result["signals"]["cool_ratio"], COOL_HI)
            self.assertEqual(result["proposal"]["deltas"],
                             {"step_budget_per_tick": -1})


if __name__ == "__main__":
    unittest.main()
