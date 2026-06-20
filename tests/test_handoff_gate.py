"""Tests for the deterministic handoff gate against done-line 0043.

The §10 bar made executable: an atom that is locally fine at every earlier gate
— it had value, it placed cleanly — but is *hollow* at handoff (a story with no
surface, or a surface with no declared downstream) must `send_back`, while a
complete atom must `ready_for_spec`, and a fixed-verdict mock must fail that
test. Plus the seam: the verdict reaches the log only through loop.node judge
(carrying the law's prompt_hash), and is refused until the stage is admitted
real.
"""

import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, handoff_gate, reconcile

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
HANDOFF_STAGE = "handoff-gate.mock.v0"
HANDOFF_REAL = "handoff-gate.det.v1"
NODE_SPEC = REPO / ".ai-native" / "nodes" / f"{HANDOFF_REAL}.md"


def atom(aid, *, story=True, touches=("loop/h.py",),
         hands_off=("seam.handoff-to-confirm",)):
    """A handoff-readiness atom: the three fields the law reads, each
    independently omittable to make a hollow atom."""
    text = (f"As bdo, I want {aid} handed off, because the loop must refuse a "
            "hollow atom before it becomes a spec.") if story else ""
    return {"atom": {
        "id": aid,
        "story": {"text": text, "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.handoff"], "touches": list(touches),
                      "must_not_collide_with": [], "hands_off_to": list(hands_off)},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, atoms, with_node_spec=True):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "nodes").mkdir(parents=True)
    for a in atoms:
        aid = a["atom"]["id"]
        (root / "atoms" / f"{aid}.json").write_text(
            json.dumps(a, indent=2), encoding="utf-8")
    if with_node_spec:
        # the real law spec, so prompt_hash on the receipt is the genuine one
        shutil.copyfile(NODE_SPEC, root / "nodes" / f"{HANDOFF_REAL}.md")
    return root


def receipts(root):
    path = root / "log" / "receipts.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


# --------------------------------------------------------------- the pure law

class HandoffLawTest(unittest.TestCase):
    """The deterministic fold: §10 teeth, no pipeline, no files."""

    def test_complete_atom_is_ready(self):
        a = atom("atom.a.v0")
        verdict, _ = handoff_gate.handoff_verdict(a["atom"])
        self.assertEqual(verdict, "ready_for_spec")

    def test_missing_story_sends_back(self):
        a = atom("atom.a.v0", story=False)
        verdict, reason = handoff_gate.handoff_verdict(a["atom"])
        self.assertEqual(verdict, "send_back")
        self.assertIn("story", reason)

    def test_missing_touches_sends_back(self):
        a = atom("atom.a.v0", touches=())
        verdict, reason = handoff_gate.handoff_verdict(a["atom"])
        self.assertEqual(verdict, "send_back")
        self.assertIn("touches", reason)

    def test_missing_hands_off_to_sends_back(self):
        # locally fine at every earlier gate (it has value, it places cleanly)
        # yet hollow at handoff: a surface with nowhere to go. A fixed-verdict
        # mock that always says ready_for_spec would wave this through — the bug
        # this gate exists to catch.
        a = atom("atom.a.v0", hands_off=())
        verdict, reason = handoff_gate.handoff_verdict(a["atom"])
        self.assertEqual(verdict, "send_back")
        self.assertIn("hands_off_to", reason)
        self.assertNotEqual(verdict, HANDOFF_MOCK_VERDICT)  # opposite of the mock

    def test_send_back_names_every_gap(self):
        # a wholly hollow atom: the reason names all three, for the cold reader.
        a = atom("atom.a.v0", story=False, touches=(), hands_off=())
        verdict, reason = handoff_gate.handoff_verdict(a["atom"])
        self.assertEqual(verdict, "send_back")
        for fragment in ("story", "touches", "hands_off_to"):
            self.assertIn(fragment, reason)

    def test_a_constant_gate_cannot_pass_both(self):
        # the §10 property stated directly: no single fixed verdict is correct
        # for both a complete atom and a hollow one. A mock is wrong on one.
        complete = handoff_gate.handoff_verdict(atom("atom.c.v0")["atom"])[0]
        hollow = handoff_gate.handoff_verdict(atom("atom.h.v0", hands_off=())["atom"])[0]
        self.assertNotEqual(complete, hollow)  # one law, both verdicts — tracks content


# the mock's fixed verdict for this stage, read from the one PIPELINE table
HANDOFF_MOCK_VERDICT = next(
    s["verdict"] for s in reconcile.PIPELINE if s["node"] == HANDOFF_STAGE)


# --------------------------------------------------- the seam (on the log, D-4)

class HandoffSeamTest(unittest.TestCase):
    """The verdict lands only through loop.node judge, and only once real."""

    def setUp(self):
        # a hollow atom — story + surface, but no declared downstream — that
        # advances through the earlier mock gates and parks at handoff, where
        # the real gate refuses it: a real send_back on the log.
        self.a = atom("atom.hand-a.v0", hands_off=())
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, [self.a])
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _judge(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = handoff_gate.main(["--root", str(self.root),
                                    "--atom", "atom.hand-a.v0", "judge",
                                    "--node", HANDOFF_REAL, "--by", "test"])
        return rc, out.getvalue()

    def test_lands_no_verdict_until_admitted_real(self):
        # handoff is NOT admitted real: the mock owns the stage and advances the
        # atom straight through, so the deterministic gate is given nothing to
        # judge — it cannot inject a verdict the owner never stamped it to cast.
        orchestrate.orchestrate(self.root, quiet=True)
        rc, _ = self._judge()
        self.assertNotEqual(rc, 0)
        self.assertEqual(
            [r for r in receipts(self.root) if r.get("node") == HANDOFF_REAL], [])

    def test_deterministic_gate_auto_runs_no_park(self):
        # the new contract (done-line 0107): a deterministic real gate is a pure
        # fold, so the loop RUNS it itself rather than parking for a summoned
        # node that never comes — the landed-but-unsettled clog. The old "park
        # then revert" realness scenario is gone by design: a deterministic gate
        # can no longer be "parked but not real". The realness guard still bites
        # for inference gates, which genuinely park (test
        # test_lands_no_verdict_until_admitted_real covers "no real verdict
        # without admission"). hand-a is hollow → the loop auto-judges send_back.
        node.admit_real(self.root, HANDOFF_STAGE, HANDOFF_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # the loop auto-runs it
        recs = [r for r in receipts(self.root) if r.get("node") == HANDOFF_REAL]
        self.assertEqual(len(recs), 1)               # the loop wrote it, no human
        self.assertEqual(recs[0]["verdict"], "send_back")  # the gate still bit

    def test_send_back_lands_through_the_pen_once_real(self):
        node.admit_real(self.root, HANDOFF_STAGE, HANDOFF_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # parks at the real handoff
        rc, text = self._judge()
        self.assertEqual(rc, 0)
        recs = [r for r in receipts(self.root) if r.get("node") == HANDOFF_REAL]
        self.assertEqual(len(recs), 1)
        rc_obj = recs[0]
        self.assertEqual(rc_obj["verdict"], "send_back")
        self.assertEqual(rc_obj["artifact_id"], "atom.hand-a.v0")
        # attributable to the exact law (§7): prompt_hash is the node spec's sha
        spec_hash = "sha256:" + hashlib.sha256(NODE_SPEC.read_bytes()).hexdigest()
        self.assertEqual(rc_obj.get("prompt_hash"), spec_hash)

    def test_send_back_verdict_parks_not_advances(self):
        # a send_back is a refusal: it does not advance to handoff_ready.
        node.admit_real(self.root, HANDOFF_STAGE, HANDOFF_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        self._judge()
        fold = reconcile.Fold(self.root)
        ahash = next(h for a, h in reconcile.load_atoms(self.root)
                     if a["id"] == "atom.hand-a.v0")
        self.assertNotEqual(reconcile.atom_state(fold, ahash), "handoff_ready")

    def test_idempotent_no_double_judgement(self):
        node.admit_real(self.root, HANDOFF_STAGE, HANDOFF_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        self._judge()
        before = len(receipts(self.root))
        self._judge()  # write-twice is a no-op (I-2)
        self.assertEqual(len(receipts(self.root)), before)


# ---------------------------------------------------------- the read-only show

class HandoffShowTest(unittest.TestCase):
    def setUp(self):
        self.a = atom("atom.show-a.v0", hands_off=())  # hollow → send_back
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, [self.a])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_show_previews_without_writing(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = handoff_gate.main(["--root", str(self.root), "--atom", "atom.show-a.v0"])
        self.assertEqual(rc, 0)
        self.assertIn("send_back", out.getvalue())
        self.assertEqual(receipts(self.root), [])  # read-only: no receipt


if __name__ == "__main__":
    unittest.main()
