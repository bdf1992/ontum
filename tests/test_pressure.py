#!/usr/bin/env python3
"""§10 test for the outcome-pressure fold (done-line 0069).

The test that matters (doctrine §10): can two locally-fine probes *refuse to
fit*, and does the fold notice? Here the teeth are four, each from the
done-line's bar:

  1. uncheckable probes are refused at the door (narrative cannot enter the
     desired-reality set);
  2. discover / build / realize phases are distinguished (a discovery move is
     progress, a built capability is told from an adopted one);
  3. dependency-dormancy: an outcome probe stays dormant until its capability
     precondition is met (dependencies control nagging);
  4. unresolved probes stay visible — the fold run after a partial session
     still lists every unmet probe and never reports "done".

And the anti-fabrication check (done-line 0069: fails on a fabricated/constant
classifier): rewiring the dependency graph *moves* the top-leverage probe, so
leverage is proven computed from structure, not a constant.
"""

import json
import tempfile
import unittest
from pathlib import Path

from loop.pressure import (DEFAULT_PROBES, check_is_valid, compute, load_probes,
                           pressure, resolve_check)


def write_probes(dirpath, probes, outcome="t"):
    p = Path(dirpath) / "probes.json"
    p.write_text(json.dumps({"outcome": outcome, "probes": probes}),
                 encoding="utf-8")
    return p


def path_check(rel):
    return {"kind": "path_exists", "path": rel}


class Refusal(unittest.TestCase):
    """An uncheckable probe is not a probe (teeth 1)."""

    def test_missing_check_refused(self):
        with tempfile.TemporaryDirectory() as d:
            pp = write_probes(d, [
                {"id": "A", "class": "cap"},  # no check at all
                {"id": "B", "class": "cap", "check": path_check("x")},
            ])
            probes, refused, _ = load_probes(pp)
            self.assertEqual([p["id"] for p in probes], ["B"])
            self.assertEqual([r["probe"] for r in refused], ["A"])

    def test_unknown_check_kind_refused(self):
        with tempfile.TemporaryDirectory() as d:
            pp = write_probes(d, [
                {"id": "A", "class": "cap", "check": {"kind": "vibes"}},
            ])
            probes, refused, _ = load_probes(pp)
            self.assertEqual(probes, [])
            self.assertEqual(refused[0]["probe"], "A")

    def test_bad_class_refused(self):
        with tempfile.TemporaryDirectory() as d:
            pp = write_probes(d, [
                {"id": "A", "class": "wish", "check": path_check("x")},
            ])
            probes, refused, _ = load_probes(pp)
            self.assertEqual(probes, [])

    def test_compound_validity_is_recursive(self):
        self.assertTrue(check_is_valid(
            {"kind": "all_of", "checks": [path_check("a"), path_check("b")]}))
        self.assertFalse(check_is_valid(
            {"kind": "all_of", "checks": [path_check("a"), {"kind": "vibes"}]}))
        self.assertFalse(check_is_valid({"kind": "all_of", "checks": []}))


class Phases(unittest.TestCase):
    """discover / build / realize / met are distinguished (teeth 2)."""

    def _compute(self, d, probes, present=()):
        for rel in present:
            (Path(d) / rel).write_text("x", encoding="utf-8")
        loaded, _, _ = load_probes(write_probes(d, probes))
        return compute(loaded, Path(d), None)

    def test_discover_when_no_capability_probes(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, [
                {"id": "O", "class": "out", "check": path_check("never")},
            ])
            self.assertEqual(r["phase"], "discover")

    def test_build_when_a_capability_is_unmet(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, [
                {"id": "C", "class": "cap", "check": path_check("absent")},
            ])
            self.assertEqual(r["phase"], "build")

    def test_realize_when_caps_met_but_outcome_unmet(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, [
                {"id": "C", "class": "cap", "check": path_check("here")},
                {"id": "O", "class": "out", "depends": ["C"],
                 "check": path_check("absent")},
            ], present=["here"])
            # C met -> O is active (dep met) but unmet -> realize, not build
            self.assertEqual(r["phase"], "realize")
            self.assertIn("O", r["unmet"])

    def test_met_only_when_everything_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, [
                {"id": "C", "class": "cap", "check": path_check("here")},
            ], present=["here"])
            self.assertEqual(r["phase"], "met")


class Dormancy(unittest.TestCase):
    """An outcome probe stays dormant until its capability precondition is
    met — dependencies control nagging (teeth 3)."""

    def _compute(self, d, probes, present=()):
        for rel in present:
            (Path(d) / rel).write_text("x", encoding="utf-8")
        loaded, _, _ = load_probes(write_probes(d, probes))
        return compute(loaded, Path(d), None)

    PROBES = [
        {"id": "C", "class": "cap", "check": path_check("cap")},
        {"id": "O", "class": "out", "depends": ["C"], "check": path_check("never")},
    ]

    def test_dormant_while_precondition_unmet(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, self.PROBES)  # cap absent
            self.assertIn("O", r["dormant"])
            self.assertNotIn("O", r["unmet"])

    def test_activates_when_precondition_met(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, self.PROBES, present=["cap"])  # cap met
            self.assertIn("O", r["unmet"])
            self.assertNotIn("O", r["dormant"])

    def test_capability_probe_never_dormant(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._compute(d, [
                {"id": "C1", "class": "cap", "check": path_check("absent")},
                {"id": "C2", "class": "cap", "depends": ["C1"],
                 "check": path_check("absent")},
            ])
            self.assertEqual(r["dormant"], [])
            self.assertIn("C2", r["unmet"])


class Visibility(unittest.TestCase):
    """The fold run after a partial session keeps every unresolved probe
    visible and never declares done (teeth 4)."""

    def test_partial_run_carries_unresolved_and_is_not_met(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "built").write_text("x", encoding="utf-8")
            loaded, _, _ = load_probes(write_probes(d, [
                {"id": "C1", "class": "cap", "check": path_check("built")},
                {"id": "C2", "class": "cap", "check": path_check("absent")},
                {"id": "C3", "class": "cap", "check": path_check("absent")},
            ]))
            r = compute(loaded, Path(d), None)
            self.assertNotEqual(r["phase"], "met")
            # the unfinished work is still there, by name — not collapsed away
            self.assertEqual(set(r["unmet"]), {"C2", "C3"})
            self.assertEqual(r["met"], ["C1"])


class Leverage(unittest.TestCase):
    """Leverage is computed from the dependency structure, not fabricated
    (done-line 0069: the test fails on a constant classifier)."""

    def _top(self, d, probes):
        loaded, _, _ = load_probes(write_probes(d, probes))
        return compute(loaded, Path(d), None)["top_leverage"]["id"]

    def test_top_leverage_follows_dependents(self):
        # A is depended on by B and C; X is depended on by no one. A wins.
        with tempfile.TemporaryDirectory() as d:
            top = self._top(d, [
                {"id": "A", "class": "cap", "check": path_check("absent")},
                {"id": "B", "class": "cap", "depends": ["A"], "check": path_check("absent")},
                {"id": "C", "class": "cap", "depends": ["A"], "check": path_check("absent")},
                {"id": "X", "class": "cap", "check": path_check("absent")},
            ])
            self.assertEqual(top, "A")

    def test_rewiring_moves_the_top(self):
        # Same probes, dependency flipped onto X: now X must win. A constant
        # classifier could not move with the graph.
        with tempfile.TemporaryDirectory() as d:
            top = self._top(d, [
                {"id": "A", "class": "cap", "check": path_check("absent")},
                {"id": "B", "class": "cap", "depends": ["X"], "check": path_check("absent")},
                {"id": "C", "class": "cap", "depends": ["X"], "check": path_check("absent")},
                {"id": "X", "class": "cap", "check": path_check("absent")},
            ])
            self.assertEqual(top, "X")


class LogRecordCheck(unittest.TestCase):
    """The use-trace check resolves against the log (the outcome-probe seam)."""

    def test_log_record_matches_substring(self):
        class FakeFold:
            receipts = [{"id": "r1", "verdict": "outcome-carried-2026"}]
            events = []
            admissions = []
        ok, ev = resolve_check(
            {"kind": "log_record", "ledger": "receipts",
             "match": {"verdict": "outcome-carried"}}, Path("."), FakeFold())
        self.assertTrue(ok)
        self.assertEqual(ev, "r1")

    def test_log_record_absent(self):
        class FakeFold:
            receipts = []
            events = []
            admissions = []
        ok, _ = resolve_check(
            {"kind": "log_record", "ledger": "receipts",
             "match": {"verdict": "nope"}}, Path("."), FakeFold())
        self.assertFalse(ok)


class RealCausalitySet(unittest.TestCase):
    """The committed Causality probe-set resolves as the done-line specifies:
    build phase, CZ1 top leverage, outcome probes carried, nothing refused."""

    def test_committed_set_is_clean_and_build_phase(self):
        r = pressure(DEFAULT_PROBES)
        self.assertEqual(r["refused"], [], "the committed set must be checkable")
        self.assertEqual(r["phase"], "build")
        self.assertEqual(r["top_leverage"]["id"], "CZ1")
        # the outcome probes are carried as continuing pressure. OUT1 is
        # dormant *until* OP2 lands and active-unmet *after* (done-line 0073
        # built OP2: summon now references the pressure fold, so OP2 resolves
        # and OUT1's precondition is met) — the durable invariant is that it is
        # carried, not which of the two it is in at a given moment. The
        # dormancy mechanism itself is proven by the synthetic Dormancy tests.
        unresolved = set(r["partial"]) | set(r["unmet"]) | set(r["dormant"])
        self.assertTrue({"CZ1", "CZ2", "CZ3", "CZ4", "OUT1", "OUT2"} <= unresolved)


if __name__ == "__main__":
    unittest.main()
