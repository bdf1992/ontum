"""Done-line 0150: the guaranteed review queue — landed work gets a real review,
never a clog or a leak.

The root cause (bdo, 2026-06-20): the terminal gate `value-confirm.claude.v1`
*parks* landed work awaiting a judge, and nothing fired that judge — so finished
atoms piled into a clog (inflight 24 against a cap of 8). A queue is healthy only
with a guaranteed consumer. This proves the consumer — the gate pen's `drain` —
turns the clog into a real queue.

The §10 teeth: two locally-identical atoms in the same queue settle *differently*
on their real verdict, and neither the no-clog nor the no-leak property may be
vacuous. The review is injected (a scripted verdict through the REAL one pen, no
live spawn):

  - `confirmed`      -> the atom reaches settled                 (NO CLOG)
  - `missed`         -> the atom does NOT settle, stays surfaced (honest, not
                                                                  force-cleared)
  - no verdict       -> the atom does NOT settle, stays queued   (NO LEAK +
                                                                  retried next pass)
  - a second drain   -> fires nothing already judged             (idempotent)

A constant "settle everything" processor fails the `missed` and no-verdict cases;
a no-op processor fails the `confirmed` case. The fold is forced to discriminate.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import orchestrate, reconcile
from loop import node as node_pen
from loop.summon import open_summons

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

CONFIRM_NODE = "value-confirm.claude.v1"
SETPOINT = {"step_budget_per_tick": 5, "max_inflight_atoms": 50, "human_queue_cap": 50}


def _atom(slug):
    return {"atom": {
        "id": f"atom.{slug}.v0",
        "story": {"text": f"As an AI, I need {slug} to land, because bdo wants "
                          "the review queue proven.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.queue"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [],
                      "hands_off_to": ["seam.value-to-placement"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending",
                     "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def _make_root(tmp, slugs):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    for s in slugs:
        (root / "atoms" / f"atom.{s}.v0.json").write_text(
            json.dumps(_atom(s), indent=2), encoding="utf-8")
    # Admit value-confirm REAL so the loop PARKS landed work there (the queue).
    reconcile.append_line(root / "log" / "admissions.jsonl", {
        "id": "adm.test-value-confirm-real", "type": "node_real",
        "stage_node": "value-confirm.mock.v0", "real_node": CONFIRM_NODE,
        "by": "test-bdo", "ts": "2026-06-20T00:00:00Z"})
    orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
    # Drive every atom up to the value-confirm seam: the mock stages above
    # auto-pass (the owner-stamp mock is driven as the human, so human_rate must
    # cover every atom), and the one real gate (value-confirm) parks — the queue.
    orchestrate.orchestrate(root, human_rate=len(slugs) + 1, quiet=True)
    return root


def _settled(root):
    fold = reconcile.Fold(root)
    return {atom["id"] for atom, ahash in reconcile.load_atoms(root)
            if orchestrate.next_action(fold, atom, ahash) is None}


def _queued(root):
    return {s["atom"]["id"] for s in open_summons(root) if s["node"] == CONFIRM_NODE}


def _vc_verdicts(root, atom_id):
    """Every value-confirm verdict on the log for this atom (by content hash)."""
    fold = reconcile.Fold(root)
    ahash = next(h for a, h in reconcile.load_atoms(root) if a["id"] == atom_id)
    return [rc.get("verdict") for rc in fold.receipts
            if rc.get("node") == CONFIRM_NODE and rc.get("artifact_hash") == ahash]


class ReviewQueueDrain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # three locally-identical atoms; only their real verdict will differ.
        self.root = _make_root(self.tmp, ["alpha", "bravo", "charlie"])

    def test_the_queue_forms(self):
        """Precondition: landed work parks at value-confirm — the queue exists."""
        self.assertEqual(_queued(self.root),
                         {"atom.alpha.v0", "atom.bravo.v0", "atom.charlie.v0"})
        self.assertEqual(_settled(self.root), set())

    def test_drain_no_clog_no_leak_surfaces_misses_and_is_idempotent(self):
        confirms = {"atom.alpha.v0"}
        misses = {"atom.bravo.v0"}
        # charlie gets NO verdict — a review that returned nothing.
        fired_log = []

        def fake_review(records_root, atom_id, node_id, by):
            fired_log.append(atom_id)
            if atom_id in confirms:
                node_pen.judge(records_root, atom_id, node_id, "confirmed",
                               "fake review: the work is on main, claim delivered")
            elif atom_id in misses:
                node_pen.judge(records_root, atom_id, node_id, "missed",
                               "fake review: claim/delivery gap")
            # else: no verdict lands — the atom must stay queued (retry).
            return 0

        # --- pass 1: the processor drains the queue ---
        fired = gate.drain(self.root, node=CONFIRM_NODE, review=fake_review)
        self.assertEqual({f["atom"] for f in fired},
                         {"atom.alpha.v0", "atom.bravo.v0", "atom.charlie.v0"})
        # drain only FIRES reviews (writes verdicts via the one pen); the loop
        # then derives the terminal for a confirmed atom — its level-triggered
        # half. human_rate=0 so a missed atom is NOT human-advanced.
        orchestrate.orchestrate(self.root, human_rate=0, quiet=True)

        settled = _settled(self.root)
        # NO CLOG: the confirmed atom reached settled.
        self.assertIn("atom.alpha.v0", settled)
        # honest, not force-cleared: the missed atom did NOT settle, and carries
        # exactly one `missed` receipt (surfaced, not advanced).
        self.assertNotIn("atom.bravo.v0", settled)
        self.assertEqual(_vc_verdicts(self.root, "atom.bravo.v0"), ["missed"])
        # NO LEAK: the un-reviewed atom did NOT settle, and is still queued for a
        # retry — nothing settles without a real verdict behind it.
        self.assertNotIn("atom.charlie.v0", settled)
        self.assertIn("atom.charlie.v0", _queued(self.root))
        # the ONLY settled atom is the one with a real `confirmed` verdict.
        self.assertEqual(settled, {"atom.alpha.v0"})
        self.assertEqual(_vc_verdicts(self.root, "atom.alpha.v0"), ["confirmed"])

        # --- pass 2: idempotent — fires nothing already judged ---
        fired_log.clear()
        fired2 = gate.drain(self.root, node=CONFIRM_NODE, review=fake_review)
        self.assertEqual({f["atom"] for f in fired2}, {"atom.charlie.v0"},
                         "a second pass must re-fire only the un-judged atom")
        self.assertNotIn("atom.alpha.v0", fired_log)
        self.assertNotIn("atom.bravo.v0", fired_log)
        # no double-judging: alpha/bravo still carry exactly one verdict each.
        self.assertEqual(_vc_verdicts(self.root, "atom.alpha.v0"), ["confirmed"])
        self.assertEqual(_vc_verdicts(self.root, "atom.bravo.v0"), ["missed"])

    def test_dry_run_fires_nothing(self):
        fired = gate.drain(self.root, node=CONFIRM_NODE, dry_run=True)
        self.assertEqual(len(fired), 3)
        self.assertTrue(all(f["fired"] == "dry-run" for f in fired))
        # nothing settled, nothing left the queue.
        self.assertEqual(_settled(self.root), set())
        self.assertEqual(len(_queued(self.root)), 3)


if __name__ == "__main__":
    unittest.main()
