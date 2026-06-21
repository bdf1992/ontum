"""Done-line 0146: the value gate judges deterministically-composed policy facts.

bdo's principle: "Judgement should be non-deterministic but the data being judged
should be compiled and composed from configuration and policy." The gate's
`policy_facts` fold composes — from the epic records and the admissions log,
never the atom's self-claims — the atom's arc membership, whether that arc is
confirmed, and a reconciliation of the atom's self-claimed `serves` against the
policy truth.

The §10 teeth:
  - arc membership is read from the EPIC RECORDS: an atom a real epic names is
    'backed'; an atom that self-claims an epic which does not name it is
    'NOT backed by policy' (the recent panel fault, caught deterministically);
  - confirmed vs unconfirmed arcs are distinguished from the LOG;
  - a constant fold could not tell a backed atom from an unbacked one.
"""

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen_pf", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _atom(serves):
    return {"atom": {"id": "atom.x.v0", "incidence": {"serves": serves}}}


class PolicyFacts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.epics = self.tmp / "epics"
        self.log = self.tmp / "log"
        self.epics.mkdir()
        self.log.mkdir()
        # point the gate's module paths at the temp tree
        self._save = (gate.EPICS, gate.LOG)
        gate.EPICS, gate.LOG = self.epics, self.log

    def tearDown(self):
        gate.EPICS, gate.LOG = self._save
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _epic(self, eid, pieces):
        (self.epics / f"{eid}.json").write_text(json.dumps(
            {"epic": {"id": eid, "arc": "an arc", "pieces": pieces}}), encoding="utf-8")

    def _confirm(self, eid, enabled=True):
        with (self.log / "admissions.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "arc_confirmed", "epic": eid,
                                "enabled": enabled}) + "\n")

    def test_membership_from_epic_records_not_self_claim(self):
        self._epic("epic.real", [{"atom": "atom.x.v0", "glue": "the piece"}])
        f = gate.policy_facts("atom.x.v0", _atom(["epic.real"]))
        self.assertEqual([s["id"] for s in f["arc_membership"]], ["epic.real"])
        self.assertEqual(f["reconciliation"], [{"self_claimed_epic": "epic.real",
                                                "backed_by_policy": True}])
        self.assertEqual(f["unbacked_self_claims"], [])

    def test_self_claim_not_backed_by_policy(self):
        """The recent panel fault: the atom claims epic.the-field but no epic
        names it — composed deterministically as unbacked."""
        self._epic("epic.other", [{"atom": "atom.someone-else.v0"}])
        f = gate.policy_facts("atom.x.v0", _atom(["epic.the-field"]))
        self.assertEqual(f["arc_membership"], [])
        self.assertEqual(f["unbacked_self_claims"], ["epic.the-field"])
        self.assertFalse(f["serves_confirmed_arc"])

    def test_confirmed_vs_unconfirmed_from_the_log(self):
        self._epic("epic.real", [{"atom": "atom.x.v0"}])
        f = gate.policy_facts("atom.x.v0", _atom([]))
        self.assertFalse(f["serves_confirmed_arc"])  # named but not confirmed
        self._confirm("epic.real")
        f2 = gate.policy_facts("atom.x.v0", _atom([]))
        self.assertTrue(f2["serves_confirmed_arc"])

    def test_withdrawn_confirmation_is_not_confirmed(self):
        self._epic("epic.real", [{"atom": "atom.x.v0"}])
        self._confirm("epic.real", enabled=True)
        self._confirm("epic.real", enabled=False)  # latest wins: withdrawn
        f = gate.policy_facts("atom.x.v0", _atom([]))
        self.assertFalse(f["serves_confirmed_arc"])

    def test_not_constant(self):
        self._epic("epic.real", [{"atom": "atom.x.v0"}])
        backed = gate.policy_facts("atom.x.v0", _atom([]))
        unbacked = gate.policy_facts("atom.missing.v0", _atom([]))
        self.assertTrue(backed["arc_membership"])
        self.assertEqual(unbacked["arc_membership"], [])


if __name__ == "__main__":
    unittest.main()
