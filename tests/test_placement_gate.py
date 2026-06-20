"""Tests for the deterministic placement gate against done-line 0041.

The §10 bar made executable: two atoms each of which places cleanly *alone*
must refuse to fit *together* the moment one declares the other off-limits,
and a fixed-verdict mock must fail that test. Plus the seam: the verdict
reaches the log only through loop.node judge (carrying the law's prompt_hash),
and is refused until the stage is admitted real.
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

from loop import node, orchestrate, placement_gate, reconcile

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
PLACEMENT_STAGE = "placement-gate.mock.v0"
PLACEMENT_REAL = "placement-gate.det.v1"
NODE_SPEC = REPO / ".ai-native" / "nodes" / f"{PLACEMENT_REAL}.md"


def atom(aid, touches, forbid=None):
    """A minimal placeable atom: id + the two incidence fields the law reads."""
    return {"atom": {
        "id": aid,
        "story": {"text": f"As bdo, I want {aid} placed, because the loop must "
                          "refuse two atoms that cannot share an address.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.placement"], "touches": list(touches),
                      "must_not_collide_with": list(forbid or []),
                      "hands_off_to": []},
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
        shutil.copyfile(NODE_SPEC, root / "nodes" / f"{PLACEMENT_REAL}.md")
    return root


def field(*atoms):
    """The atom dicts the pure law folds over (no files)."""
    return [a["atom"] for a in atoms]


def receipts(root):
    path = root / "log" / "receipts.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


# --------------------------------------------------------------- the pure law

class PlacementLawTest(unittest.TestCase):
    """The deterministic fold: §10 teeth, no pipeline, no files."""

    def test_clean_field_is_sound(self):
        a = atom("atom.a.v0", ["loop/a.py"])
        b = atom("atom.b.v0", ["loop/b.py"])
        verdict, _ = placement_gate.placement_verdict(a["atom"], field(a, b))
        self.assertEqual(verdict, "sound")

    def test_overlap_without_declaration_is_allowed(self):
        # two atoms touching the same file is NOT a collision on its own —
        # the law needs an explicit mutual-exclusion declaration.
        a = atom("atom.a.v0", ["loop/shared.py"])
        b = atom("atom.b.v0", ["loop/shared.py"])
        verdict, _ = placement_gate.placement_verdict(a["atom"], field(a, b))
        self.assertEqual(verdict, "sound")

    def test_each_atom_is_sound_alone(self):
        # the §10 setup: locally fine. Each atom, judged against a field of
        # only itself, places cleanly.
        a = atom("atom.a.v0", ["loop/x.py"], forbid=["atom.b.v0"])
        b = atom("atom.b.v0", ["loop/x.py"])
        self.assertEqual(placement_gate.placement_verdict(a["atom"], field(a))[0], "sound")
        self.assertEqual(placement_gate.placement_verdict(b["atom"], field(b))[0], "sound")

    def test_two_locally_fine_atoms_refuse_to_fit(self):
        # the §10 teeth: together, with one declaring the other off-limits
        # over a shared address, they collide. A fixed-verdict mock that
        # always returns "sound" would wave this through — that is the bug
        # this gate exists to catch.
        a = atom("atom.a.v0", ["loop/x.py"], forbid=["atom.b.v0"])
        b = atom("atom.b.v0", ["loop/x.py"])
        verdict, reason = placement_gate.placement_verdict(a["atom"], field(a, b))
        self.assertEqual(verdict, "collision")
        self.assertIn("atom.b.v0", reason)      # names the sibling
        self.assertIn("loop/x.py", reason)      # names the shared address
        self.assertNotEqual(verdict, PLACEMENT_MOCK_VERDICT)  # opposite of the mock

    def test_declaration_either_direction(self):
        # the sibling declaring US off-limits is just as much a collision.
        a = atom("atom.a.v0", ["loop/x.py"])
        b = atom("atom.b.v0", ["loop/x.py"], forbid=["atom.a.v0"])
        self.assertEqual(
            placement_gate.placement_verdict(a["atom"], field(a, b))[0], "collision")

    def test_declaration_without_overlap_does_not_fire(self):
        # a precaution that did not trigger: declared off-limits but no shared
        # address — allowed.
        a = atom("atom.a.v0", ["loop/a.py"], forbid=["atom.b.v0"])
        b = atom("atom.b.v0", ["loop/b.py"])
        self.assertEqual(
            placement_gate.placement_verdict(a["atom"], field(a, b))[0], "sound")

    def test_a_constant_gate_cannot_pass_both(self):
        # the §10 property stated directly: no single fixed verdict is correct
        # for both a clean field and a colliding one. A mock is wrong on one.
        clean_a = atom("atom.a.v0", ["loop/a.py"])
        clean_b = atom("atom.b.v0", ["loop/b.py"])
        coll_a = atom("atom.c.v0", ["loop/x.py"], forbid=["atom.d.v0"])
        coll_b = atom("atom.d.v0", ["loop/x.py"])
        sound = placement_gate.placement_verdict(clean_a["atom"], field(clean_a, clean_b))[0]
        coll = placement_gate.placement_verdict(coll_a["atom"], field(coll_a, coll_b))[0]
        self.assertNotEqual(sound, coll)  # one prompt, both verdicts — it tracks content


# the mock's fixed verdict for this stage, read from the one PIPELINE table
PLACEMENT_MOCK_VERDICT = next(
    s["verdict"] for s in reconcile.PIPELINE if s["node"] == PLACEMENT_STAGE)


# --------------------------------------------------- the seam (on the log, D-4)

class PlacementSeamTest(unittest.TestCase):
    """The verdict lands only through loop.node judge, and only once real."""

    def setUp(self):
        # atom A declares B off-limits over a shared address: a real collision.
        self.a = atom("atom.place-a.v0", ["loop/contested.py"], forbid=["atom.place-b.v0"])
        self.b = atom("atom.place-b.v0", ["loop/contested.py"])
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, [self.a, self.b])
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _judge(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = placement_gate.main(["--root", str(self.root),
                                      "--atom", "atom.place-a.v0", "judge",
                                      "--node", PLACEMENT_REAL, "--by", "test"])
        return rc, out.getvalue()

    def test_lands_no_verdict_until_admitted_real(self):
        # placement is NOT admitted real: the mock owns the stage and advances
        # the atom straight through, so the deterministic gate is given nothing
        # to judge — it cannot inject a verdict the owner never stamped it to
        # cast. The authority guarantee: no admit-real, no placement-real
        # receipt (done-line 0028 scopes arc-confirmation to the owner-stamp,
        # not node_real — this stamp is bdo's).
        orchestrate.orchestrate(self.root, quiet=True)
        rc, _ = self._judge()
        self.assertNotEqual(rc, 0)
        self.assertEqual(
            [r for r in receipts(self.root) if r.get("node") == PLACEMENT_REAL], [])

    def test_deterministic_gate_auto_runs_no_park(self):
        # the new contract (done-line 0107): a deterministic real gate is a pure
        # fold, so the loop RUNS it itself rather than parking for a summoned
        # node that never comes — the landed-but-unsettled clog. place-b parked
        # at placement forever under the old behaviour (a real gate awaited a
        # human); now the loop auto-judges it (the collision is symmetric, so
        # place-b reads collision too). The teeth: a placement-real receipt
        # exists that the loop wrote, with NO human and NO summon. The realness
        # guard still bites for inference gates, which genuinely park
        # (test_lands_no_verdict_until_admitted_real).
        node.admit_real(self.root, PLACEMENT_STAGE, PLACEMENT_REAL, by="test-bdo")
        # no pen call, no summon — just the loop
        orchestrate.orchestrate(self.root, quiet=True)
        recs = [r for r in receipts(self.root)
                if r.get("node") == PLACEMENT_REAL
                and r.get("artifact_id") == "atom.place-b.v0"]
        self.assertEqual(len(recs), 1)              # the loop wrote it, no human
        self.assertEqual(recs[0]["verdict"], "collision")
        # the loop's verdict carries the law's attribution, like the pen's would
        spec_hash = "sha256:" + hashlib.sha256(NODE_SPEC.read_bytes()).hexdigest()
        self.assertEqual(recs[0].get("prompt_hash"), spec_hash)

    def test_collision_lands_by_the_loop_once_real(self):
        # once placement is real the loop computes its verdict and lands it
        # itself (done-line 0107): the collision reaches the record with the
        # law's prompt_hash, exactly as the pen would have written it — no park,
        # no summoned node. The check still BITES: a real collision is written
        # verbatim, not skipped.
        node.admit_real(self.root, PLACEMENT_STAGE, PLACEMENT_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # the loop auto-judges
        recs = [r for r in receipts(self.root)
                if r.get("node") == PLACEMENT_REAL
                and r.get("artifact_id") == "atom.place-a.v0"]
        self.assertEqual(len(recs), 1)
        rc_obj = recs[0]
        self.assertEqual(rc_obj["verdict"], "collision")
        # attributable to the exact law (§7): prompt_hash is the node spec's sha
        spec_hash = "sha256:" + hashlib.sha256(NODE_SPEC.read_bytes()).hexdigest()
        self.assertEqual(rc_obj.get("prompt_hash"), spec_hash)

    def test_collision_verdict_parks_not_advances(self):
        # a collision is a refusal: it does not advance to placement_sound.
        node.admit_real(self.root, PLACEMENT_STAGE, PLACEMENT_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        self._judge()
        fold = reconcile.Fold(self.root)
        ahash = next(h for a, h in reconcile.load_atoms(self.root)
                     if a["id"] == "atom.place-a.v0")
        self.assertNotEqual(reconcile.atom_state(fold, ahash), "placement_sound")

    def test_idempotent_no_double_judgement(self):
        node.admit_real(self.root, PLACEMENT_STAGE, PLACEMENT_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        self._judge()
        before = len(receipts(self.root))
        self._judge()  # write-twice is a no-op (I-2)
        self.assertEqual(len(receipts(self.root)), before)


# ---------------------------------------------------------- the read-only show

class PlacementShowTest(unittest.TestCase):
    def setUp(self):
        self.a = atom("atom.show-a.v0", ["loop/z.py"], forbid=["atom.show-b.v0"])
        self.b = atom("atom.show-b.v0", ["loop/z.py"])
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, [self.a, self.b])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_show_previews_without_writing(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = placement_gate.main(["--root", str(self.root), "--atom", "atom.show-a.v0"])
        self.assertEqual(rc, 0)
        self.assertIn("collision", out.getvalue())
        self.assertEqual(receipts(self.root), [])  # read-only: no receipt


if __name__ == "__main__":
    unittest.main()
