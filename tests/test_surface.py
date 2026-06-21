"""Tests for the active-surface control plane (loop/surface.py, CTA-1 of the
active-surface-control-plane proposal).

The plane is a LIVE fold, not a prerender — bdo's correction, 2026-06-21: *"you're
handed a rendered surface, not a control plane — I don't want prerendering."* The
§10 tooth that matters here is exactly that invariant: the plane's answer must
CHANGE when the log changes (proof it reads truth fresh, never replays a frozen
snapshot). The test is non-vacuous — it fails if the plane ever caches its read.

Also pins: the plane re-derives no truth (its cell counts ARE digest's arc
counts — no second truth), and the default surfacing lens promotes a cell to
"needs a read" only at a stamp or a refusal.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import gaps, node, orchestrate, reconcile, surface
from loop.digest import digest

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
EPIC = "epic.surface-test"


def make_atom(i):
    return {"atom": {
        "id": f"atom.surface-{i:02d}.v0",
        "story": {"text": "As an AI, I need a live control plane so a session "
                          "orients on what is active, not a frozen flood.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": [EPIC], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-owner-stamp"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, n_atoms):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "epics").mkdir(parents=True)
    for i in range(n_atoms):
        (root / "atoms" / f"atom.surface-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    (root / "epics" / "surface-test.json").write_text(json.dumps({"epic": {
        "id": EPIC, "arc": "the active-surface control plane",
        "horizon": "a session orients on a live, steerable measure of what is active",
        "pieces": [{"atom": f"atom.surface-{i:02d}.v0"} for i in range(n_atoms)],
    }}, indent=2), encoding="utf-8")
    return root


def add_atom(root, i):
    (root / "atoms" / f"atom.surface-{i:02d}.v0.json").write_text(
        json.dumps(make_atom(i), indent=2), encoding="utf-8")


class SurfacePlaneTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def park_one(self):
        """Drive atom.surface-00 to a real refusal so its arc holds a parked
        piece — the surfacing trigger."""
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        rc = node.main(["judge", "--root", str(self.root),
                        "--atom", "atom.surface-00.v0", "--node", L0_REAL,
                        "--verdict", "reject_no_value",
                        "--reason", "test refusal: no owner value on record"])
        self.assertEqual(rc, 0)

    # -- composition: no second truth -------------------------------------

    def test_cell_counts_are_digests_counts(self):
        """The plane re-derives nothing — its cell IS digest's arc, measured."""
        self.park_one()
        d = digest(self.root)
        arc = next(a for a in d["arcs"] if a["epic"] == EPIC)
        cell = next(c for c in surface.plane(self.root)["cells"] if c["subject"] == EPIC)
        for k in ("landed", "awaiting", "parked", "refused"):
            self.assertEqual(cell[k], arc[k], f"{k} drifted from digest")

    # -- the surfacing lens -----------------------------------------------

    def test_refusal_promotes_the_cell_to_needs_read(self):
        # before any movement the arc's pieces are unborn — no in-flight signal,
        # so it is quiet (folded to the tail), not a surfaced cell
        before = [c for c in surface.plane(self.root)["cells"] if c["subject"] == EPIC]
        self.assertEqual(before, [], "a quiet arc should not surface as a cell")
        # a refusal gives the arc a parked piece — now it wants a read
        self.park_one()
        after = next(c for c in surface.plane(self.root)["cells"] if c["subject"] == EPIC)
        self.assertTrue(after["needs_read"])
        self.assertTrue(after["refused"] or after["parked"])
        # and the cell carries its weight class, not a bare count
        self.assertIn(after["weight_class"],
                      ("confirmed-moving", "awaiting-stamp", "idle"))

    # -- THE §10 tooth: live, not prerendered -----------------------------

    def test_section10_answer_changes_when_the_log_changes(self):
        """The non-prerender invariant. The same plane() call, run twice with the
        disk changed between, MUST give a different answer — proof it folds fresh
        and never replays a frozen snapshot. Fails if the plane ever caches."""
        first = surface.plane(self.root)
        before_unborn = first["vitals"]["field"]["unborn"]

        add_atom(self.root, 9)  # a new, unseeded atom appears on disk

        second = surface.plane(self.root)
        after_unborn = second["vitals"]["field"]["unborn"]
        self.assertEqual(after_unborn, before_unborn + 1,
                         "the plane served a stale read — it is prerendering, not folding")
        self.assertNotEqual(json.dumps(first, sort_keys=True),
                            json.dumps(second, sort_keys=True))

    # -- the ephemeral dimension knob -------------------------------------

    def test_unknown_dimension_is_named_not_faked(self):
        rc = surface.main(["--root", str(self.root), "--dimension", "blast-radius"])
        self.assertEqual(rc, 2)  # needs-you: a later lens, named, not faked

    def test_default_lens_is_safe_when_unset(self):
        """A bare call answers with the default lens — no admission needed."""
        data = surface.plane(self.root)
        self.assertEqual(data["lens"]["dimension"], "arc")
        self.assertEqual(data["lens"]["weights"], surface.DEFAULT_LENS["weights"])


if __name__ == "__main__":
    unittest.main()
