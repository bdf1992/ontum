"""Tests for the first real node against done-line 0003:
an admitted-real stage is never auto-judged (the atom parks naming the
awaited node); a summoned verdict lands through loop/node.py — idempotent,
D-2-guarded, terminal-set-checked; a real accept advances, a real reject
parks; and atoms settled under mock receipts never regress when realness
is admitted."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
STAMP_STAGE = "owner-stamp.mock-bdo.v0"
STAMP_REAL = "owner-stamp.bdo.v1"


def make_atom(i):
    return {"atom": {
        "id": f"atom.real-{i:02d}.v0",
        "story": {"text": f"As an AI, I need real atom {i} judged for real, "
                          "because bdo wants a gate that can say no.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.real-l0"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-owner-stamp"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, n_atoms):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    for i in range(n_atoms):
        (root / "atoms" / f"atom.real-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    return root


def states(root):
    fold = reconcile.Fold(root)
    return {atom["id"]: reconcile.atom_state(fold, ahash)
            for atom, ahash in reconcile.load_atoms(root)}


def receipt_count(root):
    path = root / "log" / "receipts.jsonl"
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text().splitlines() if line.strip())


class RealNodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        node.admit_real(self.root, STAMP_STAGE, STAMP_REAL, by="test-bdo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def judge(self, atom_id, who=L0_REAL, verdict="accept", reason="test verdict"):
        return node.main(["judge", "--root", str(self.root), "--atom", atom_id,
                          "--node", who, "--verdict", verdict, "--reason", reason])

    def test_real_stage_is_never_auto_judged(self):
        self.assertEqual(orchestrate.orchestrate(self.root, quiet=True), 2)
        # both atoms were seeded, then parked awaiting the real L0 — no
        # receipt was written by the loop
        self.assertEqual(receipt_count(self.root), 0)
        fold = reconcile.Fold(self.root)
        atoms = reconcile.load_atoms(self.root)
        pressure = orchestrate.sense(fold, atoms)
        self.assertEqual(pressure["awaiting"], 2)
        for atom, ahash in atoms:
            self.assertEqual(orchestrate.next_action(fold, atom, ahash), ("await", L0_REAL))

    def test_summoned_accept_advances_to_the_real_stamp(self):
        orchestrate.orchestrate(self.root, quiet=True)
        self.assertEqual(self.judge("atom.real-00.v0"), 0)
        # idempotent: the same verdict twice is a no-op (I-2)
        self.assertEqual(self.judge("atom.real-00.v0"), 0)
        self.assertEqual(receipt_count(self.root), 1)
        # the loop now advances atom 00 to the stamp seam and parks there
        self.assertEqual(orchestrate.orchestrate(self.root, quiet=True), 2)
        fold = reconcile.Fold(self.root)
        atoms = dict((a["id"], (a, h)) for a, h in reconcile.load_atoms(self.root))
        a0, h0 = atoms["atom.real-00.v0"]
        self.assertEqual(reconcile.atom_state(fold, h0), "value_accepted")
        self.assertEqual(orchestrate.next_action(fold, a0, h0), ("await", STAMP_REAL))
        # bdo's queue is real backlog now: the sensor sees it
        pressure = orchestrate.sense(fold, reconcile.load_atoms(self.root))
        self.assertEqual(pressure["human_backlog"], 1)
        # the real stamp lands; mocks carry the atom the rest of the way
        self.assertEqual(self.judge("atom.real-00.v0", who=STAMP_REAL,
                                    reason="stamped: value serves the owner"), 0)
        self.assertEqual(orchestrate.orchestrate(self.root, quiet=True), 2)  # 01 still awaits L0
        self.assertEqual(states(self.root)["atom.real-00.v0"], "value_confirmed")

    def test_real_reject_parks_the_atom(self):
        orchestrate.orchestrate(self.root, quiet=True)
        self.assertEqual(self.judge("atom.real-01.v0", verdict="reject_no_value",
                                    reason="story serves the agent's appetite, not the owner's"), 0)
        self.assertEqual(orchestrate.orchestrate(self.root, quiet=True), 2)
        fold = reconcile.Fold(self.root)
        atoms = dict((a["id"], (a, h)) for a, h in reconcile.load_atoms(self.root))
        a1, h1 = atoms["atom.real-01.v0"]
        # the reject receipt holds the atom at created: no advance, no retry
        self.assertEqual(reconcile.atom_state(fold, h1), "created")
        self.assertEqual(orchestrate.next_action(fold, a1, h1), ("parked", None))

    def test_seam_contract_is_enforced(self):
        orchestrate.orchestrate(self.root, quiet=True)
        # wrong identity: the seam awaits the admitted node, nobody else
        self.assertEqual(self.judge("atom.real-00.v0", who="imposter.v0"), 2)
        # wrong verdict: not in the seam's terminal set
        self.assertEqual(self.judge("atom.real-00.v0", verdict="lgtm"), 2)
        # D-2: the event's announcer may not judge it
        node.admit_real(self.root, L0_STAGE, reconcile.SEED_NODE, by="test-bdo")
        self.assertEqual(self.judge("atom.real-00.v0", who=reconcile.SEED_NODE), 2)
        self.assertEqual(receipt_count(self.root), 0)

    def test_settled_mock_receipts_never_regress(self):
        fresh = make_root(tempfile.mkdtemp(dir=self.tmp), 2)
        orchestrate.admit_setpoint(fresh, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(fresh, quiet=True), 0)  # all mock
        before = (fresh / "log" / "receipts.jsonl").read_bytes()
        node.admit_real(fresh, L0_STAGE, L0_REAL, by="test-bdo")
        node.admit_real(fresh, STAMP_STAGE, STAMP_REAL, by="test-bdo")
        # realness admitted after the fact: history stands, nothing reopens
        self.assertEqual(orchestrate.orchestrate(fresh, quiet=True), 0)
        self.assertEqual(set(states(fresh).values()), {"value_confirmed"})
        self.assertEqual(before, (fresh / "log" / "receipts.jsonl").read_bytes())

    def inbox_text(self, root=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(node.main(["inbox", "--root", str(root or self.root)]), 0)
        return out.getvalue()

    def test_inbox_shows_open_items_and_how_to_clear_them(self):
        orchestrate.orchestrate(self.root, quiet=True)
        # both atoms still await the L0 summons: nothing is bdo's yet
        text = self.inbox_text()
        self.assertIn("0 item(s) awaiting your stamp, 2 awaiting summons", text)
        # atom 00 passes L0 and reaches the stamp: it is bdo's, fully briefed
        self.judge("atom.real-00.v0", reason="serves the owner")
        orchestrate.orchestrate(self.root, quiet=True)
        text = self.inbox_text()
        self.assertIn("atom.real-00.v0 — awaiting your stamp", text)
        self.assertIn("real atom 0 judged for real", text)         # the story
        self.assertIn("serves the owner", text)                     # L0's reasoning
        self.assertIn("--node owner-stamp.bdo.v1 --verdict", text)  # the clear line
        # atom 01 is rejected by L0: it parks as bdo's to amend, with the why
        self.judge("atom.real-01.v0", verdict="reject_no_value", reason="no owner value found")
        orchestrate.orchestrate(self.root, quiet=True)
        text = self.inbox_text()
        self.assertIn("atom.real-01.v0 — parked", text)
        self.assertIn("no owner value found", text)
        # clearing uses the one existing pen; the inbox then empties
        self.judge("atom.real-00.v0", who=STAMP_REAL, reason="stamped")
        orchestrate.orchestrate(self.root, quiet=True)
        text = self.inbox_text()
        self.assertIn("0 item(s) awaiting your stamp, 0 awaiting summons, 1 parked", text)

    def test_inbox_hides_a_superseded_park_but_keeps_a_live_one(self):
        """The stale-park phantom (heal.py): a version a higher sibling
        replaces must not surface as a live owner park — its receipt is
        history, not work. §10 teeth: a non-superseded park still must show,
        so the filter cannot just be hiding parks. Same situation for both
        (rejected then parked) — only supersession differs."""
        orchestrate.orchestrate(self.root, quiet=True)
        # both atoms rejected by the real L0 -> both park as the owner's
        self.judge("atom.real-00.v0", verdict="reject_no_value",
                   reason="no owner value (this one stays live)")
        self.judge("atom.real-01.v0", verdict="reject_no_value",
                   reason="no owner value (this one gets superseded)")
        orchestrate.orchestrate(self.root, quiet=True)
        # before supersession both parks surface (the starting condition)
        text = self.inbox_text()
        self.assertIn("atom.real-00.v0 — parked", text)
        self.assertIn("atom.real-01.v0 — parked", text)
        # a higher version of real-01 lands on disk: v0 is now history, not work
        v1 = make_atom(1)
        v1["atom"]["id"] = "atom.real-01.v1"
        (self.root / "atoms" / "atom.real-01.v1.json").write_text(
            json.dumps(v1, indent=2), encoding="utf-8")
        text = self.inbox_text()
        # the superseded park is gone from the owner's surface ...
        self.assertNotIn("atom.real-01.v0 — parked", text)
        # ... but the live park is untouched (the teeth: not a blanket hide)
        self.assertIn("atom.real-00.v0 — parked", text)
        self.assertIn("1 parked", text)

    def test_inbox_with_mocked_stamp_owns_nothing(self):
        fresh = make_root(tempfile.mkdtemp(dir=self.tmp), 1)
        orchestrate.admit_setpoint(fresh, SETPOINT, by="test-bdo")
        text = self.inbox_text(fresh)
        self.assertIn("the owner stamp is still mocked", text)
        self.assertIn("0 item(s) awaiting your stamp", text)

    def test_reverting_to_mock_is_a_superseding_admission(self):
        orchestrate.orchestrate(self.root, quiet=True)
        node.admit_real(self.root, L0_STAGE, None, by="test-bdo")   # revert L0
        node.admit_real(self.root, STAMP_STAGE, None, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(self.root, quiet=True), 0)
        self.assertEqual(set(states(self.root).values()), {"value_confirmed"})


if __name__ == "__main__":
    unittest.main()
