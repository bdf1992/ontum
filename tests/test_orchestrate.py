"""Tests for the fast ambient loop against done-line 0002:
>=2 atoms reach goal under a budget read from an admitted setpoint; and the
flood test — atoms seeded faster than the rate-limited mock human can clear
them — proves the cool path (I-7): the human queue never exceeds its admitted
cap at any tick, inflow is shed, and the field still reaches done."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import orchestrate, reconcile

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}


def make_atom(i):
    return {"atom": {
        "id": f"atom.flood-{i:02d}.v0",
        "story": {"text": f"As an AI, I need flood atom {i} to reach goal, "
                          "because bdo wants the cool path proven.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.flood"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-placement"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, n_atoms):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    for i in range(n_atoms):
        (root / "atoms" / f"atom.flood-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    return root


def tick_records(root):
    admissions, _ = orchestrate.read_admissions(root)
    return [a for a in admissions if a.get("type") == "tick"]


def receipt_keys(root):
    keys = []
    for line in (root / "log" / "receipts.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rc = json.loads(line)
        keys.append((rc["node"], rc["artifact_hash"]))
    return keys


def all_states(root):
    fold = reconcile.Fold(root)
    return {atom["id"]: reconcile.atom_state(fold, ahash)
            for atom, ahash in reconcile.load_atoms(root)}


class OrchestrateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_two_atoms_reach_goal_under_admitted_budget(self):
        root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, quiet=True), 0)
        self.assertEqual(set(all_states(root).values()), {"value_confirmed"})
        ticks = tick_records(root)
        self.assertTrue(ticks, "no tick was admitted to the log")
        for t in ticks:
            self.assertLessEqual(t["budget_spent"], SETPOINT["step_budget_per_tick"])
        # I-2 across many atoms sharing one log: one receipt per (node, hash)
        keys = receipt_keys(root)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), 2 * len(reconcile.PIPELINE))

    def test_no_admitted_setpoint_is_needs_you(self):
        root = make_root(self.tmp, 2)
        self.assertEqual(orchestrate.orchestrate(root, quiet=True), 2)
        # I-8: without the dial, the loop acted on nothing
        self.assertFalse((root / "log" / "events.jsonl").exists())

    def test_latest_admission_wins_never_mutates(self):
        root = make_root(self.tmp, 2)
        first = orchestrate.admit_setpoint(root, dict(SETPOINT, step_budget_per_tick=1), by="test-bdo")
        orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo", supersedes=first["id"])
        admissions, _ = orchestrate.read_admissions(root)
        setpoint = orchestrate.read_setpoint(admissions)
        self.assertEqual(setpoint["value"]["step_budget_per_tick"], 3)
        self.assertEqual(setpoint["supersedes"], first["id"])
        # the superseded admission is still in the log, unmutated
        self.assertEqual(admissions[0]["id"], first["id"])
        self.assertEqual(admissions[0]["value"]["step_budget_per_tick"], 1)

    def test_flood_cool_path_holds_the_cap_without_stalling(self):
        """Report 0002 §5: the test that matters. A drainer floods the human
        queue without bound; the loop must throttle its own inflow instead."""
        root = make_root(self.tmp, 6)  # 6 atoms >> human_queue_cap of 2
        orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, quiet=True), 0)
        ticks = tick_records(root)
        # the cap held at every tick
        backlogs = [t["pressure"]["human_backlog"] for t in ticks]
        self.assertLessEqual(max(backlogs), SETPOINT["human_queue_cap"],
                             f"human queue exceeded its admitted cap: {backlogs}")
        # the loop actually cooled — and specifically shed its own inflow
        cool_ticks = [t for t in ticks if t["mode"] == "cool"]
        self.assertTrue(cool_ticks, "the loop only ever sped up: the control law isn't doing its job")
        reasons = [d["why"] for t in ticks for d in t["deferred"]]
        self.assertIn("cool: inflow shed", reasons)
        # and cooling never meant stalling: every cool tick still spent budget
        for t in cool_ticks:
            self.assertGreaterEqual(t["budget_spent"], 1)
        # the whole field still reached goal, with no doubled receipts
        self.assertEqual(set(all_states(root).values()), {"value_confirmed"})
        keys = receipt_keys(root)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), 6 * len(reconcile.PIPELINE))

    def test_interrupted_run_resumes_from_the_log(self):
        root = make_root(self.tmp, 4)
        orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, max_ticks=3, quiet=True), 2)
        states = set(all_states(root).values())
        self.assertNotEqual(states, {"value_confirmed"}, "3 ticks finished everything: nothing was interrupted")
        # a fresh control session picks the field up from the files alone
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, quiet=True), 0)
        self.assertEqual(set(all_states(root).values()), {"value_confirmed"})
        keys = receipt_keys(root)
        self.assertEqual(len(keys), len(set(keys)), "doubled receipts after resume")
        self.assertEqual(len(keys), 4 * len(reconcile.PIPELINE))
        # two sessions can sense the same pressure at the same tick number in
        # the same second — their tick ids must still be distinct lines
        raw_ticks = [line for line in
                     (root / "log" / "admissions.jsonl").read_text().splitlines()
                     if line.strip() and json.loads(line).get("type") == "tick"]
        self.assertEqual(len(raw_ticks), len(tick_records(root)),
                         "tick ids collided across sessions: history hidden by the fold")

    def test_rerun_after_done_writes_nothing(self):
        root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, quiet=True), 0)
        before = {p.name: p.read_bytes() for p in (root / "log").iterdir()}
        self.assertEqual(orchestrate.orchestrate(root, human_rate=1, quiet=True), 0)
        after = {p.name: p.read_bytes() for p in (root / "log").iterdir()}
        self.assertEqual(before, after, "a settled field was written to")


def _landed_receipt(atom_ids, rid="rcp.merge.test"):
    """A merge-node landing receipt carrying the D-13 per-atom join — the
    independent lander's `landed_atoms`."""
    return {"id": rid, "kind": "merge", "node": "merge-node.claude.v1",
            "verdict": "landed", "epic": "epic.test", "pr": 999,
            "landed_atoms": list(atom_ids), "ts": "2026-06-20T00:00:00Z"}


class SettleOnMainTest(unittest.TestCase):
    """The follow-through road (done-line for the landing-throughput arc): an
    atom whose work the independent merge-node landed on main is settled — it
    stops counting as inflight — so work closes in the wild instead of dying one
    step past the value-gate. The teeth: an un-landed new version never rides a
    sibling version's landing (§10)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_landed_atom_with_seed_settles_and_drains_inflight(self):
        root = make_root(self.tmp, 1)
        (atom, ahash), = reconcile.load_atoms(root)
        # the atom has only been announced (seed) and stalled — the clog shape:
        # a derivable next step, so it counts as inflight, never settled.
        reconcile.append_line(root / "log" / "events.jsonl",
                              {"type": orchestrate.SEED_EVENT, "artifact_hash": ahash,
                               "id": "evt.seed", "ts": "2026-06-20T00:00:00Z"})
        fold = reconcile.Fold(root)
        self.assertIsNotNone(
            orchestrate.next_action(fold, atom, ahash, on_main=set()),
            "an un-landed announced atom must still have a step — it is inflight")
        # the independent merge-node lands it; its landed_atoms join names the id
        reconcile.append_line(root / "log" / "receipts.jsonl",
                              _landed_receipt([atom["id"]]))
        fold = reconcile.Fold(root)
        self.assertIsNone(
            orchestrate.next_action(fold, atom, ahash),
            "a landed atom must settle — the merge-node's landing is the "
            "deciding acceptance (D-13 join x D-2)")
        # and the whole-field fold counts it settled, not inflight (clog drains)
        pressure = orchestrate.sense(fold, reconcile.load_atoms(root))
        self.assertEqual(pressure["inflight"], 0, "the landed atom still clogs inflight")
        self.assertEqual(pressure["settled"], 1)

    def test_unlanded_new_version_refuses_to_ride_a_landing(self):
        """§10 teeth: the id reached main, but the current bytes are a fresh
        in-place edit (no seed for THIS hash). The un-landed version must NOT be
        settled by its sibling's landing — a landed id is not a blank cheque."""
        root = make_root(self.tmp, 1)
        (atom, ahash), = reconcile.load_atoms(root)
        # a prior version landed (the id is in landed_atoms) ...
        reconcile.append_line(root / "log" / "receipts.jsonl",
                              _landed_receipt([atom["id"]]))
        # ... but the current bytes never got a seed event (a new, un-landed hash)
        fold = reconcile.Fold(root)
        self.assertEqual(
            orchestrate.next_action(fold, atom, ahash),
            ("seed", orchestrate.SEED_EVENT),
            "an un-landed version rode its sibling's landing — the join is too loose")


if __name__ == "__main__":
    unittest.main()
