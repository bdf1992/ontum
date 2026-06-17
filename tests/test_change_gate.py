"""Tests for the change-axis gate (done-line 0104) — the procedure's teeth.

The §10 bar is the whole point: the gate must be able to *refuse*. bdo's
committed UI split is coherent, and each broken sibling — derived by ONE
mutation of that same coherent manifest — must be refused for its own named
reason. Starting from the coherent manifest and mutating one thing is the
sharpest form of "two locally-fine modules refuse to fit": the change that
breaks the decomposition is the diff.

  (a) two modules declaring the same change-axis -> smeared-axis (one axis
      smeared across modules is a false boundary; the §10 teeth);
  (b) a module whose axis loses a required field -> incomplete-axis;
  (c) a depends_on cycle -> dependency-cycle (a false boundary);
  (d) a dependency edge whose contract is removed -> uncontracted-seam;
  (e) a seam-contract stripped of its AI-native field -> smuggled-seam
      (the confirmed fork: trust/authority/change_rate are first-class).

And the gate is not vacuous: a constant always-coherent gate fails (a)-(e);
a constant always-refuse gate fails the coherent case. A gate that does not
actually read the manifest cannot pass this suite. Findings are asserted by
SHAPE (kind + subject), never a brittle snapshot a later edit would trip.
"""

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from decompose import change_gate as cg

ANCHOR = REPO / "decompose" / "examples" / "ui-split.manifest.json"


def kinds(found):
    return {f["kind"] for f in found}


class ChangeAxisGate(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(ANCHOR.read_text("utf-8"))

    def fresh(self):
        return copy.deepcopy(self.manifest)

    # the anchor: bdo's worked example survives the change test cleanly.
    def test_anchor_is_coherent(self):
        status, found = cg.verdict(self.manifest)
        self.assertEqual(status, "coherent", f"unexpected findings: {found}")
        self.assertEqual(found, [])

    # (a) one axis smeared across two modules — the §10 teeth.
    def test_smeared_axis_refused(self):
        m = self.fresh()
        # give wiring the same reason as tokens: locally fine, refuses to fit.
        m["modules"][1]["axis"]["reason"] = m["modules"][0]["axis"]["reason"]
        status, found = cg.verdict(m)
        self.assertEqual(status, "refused")
        self.assertIn("smeared-axis", kinds(found))
        smear = next(f for f in found if f["kind"] == "smeared-axis")
        self.assertIn("tokens", smear["subject"])
        self.assertIn("wiring", smear["subject"])

    # a trivial whitespace/case difference is the SAME reason — still smeared.
    def test_smeared_axis_is_normalized(self):
        m = self.fresh()
        m["modules"][1]["axis"]["reason"] = "  Aesthetic   CHANGE "
        self.assertIn("smeared-axis", kinds(cg.findings(m)))

    # (b) an axis that cannot be reasoned about.
    def test_incomplete_axis_refused(self):
        m = self.fresh()
        del m["modules"][2]["axis"]["authority"]
        found = cg.findings(m)
        self.assertIn("incomplete-axis", kinds(found))
        inc = next(f for f in found if f["kind"] == "incomplete-axis")
        self.assertEqual(inc["subject"], "copy")
        self.assertIn("authority", inc["why"])

    # (c) a cycle is a false boundary.
    def test_dependency_cycle_refused(self):
        m = self.fresh()
        # tokens already <- wiring; make tokens depend on wiring too -> 2-cycle.
        m["modules"][0]["depends_on"] = ["wiring"]
        found = cg.findings(m)
        self.assertIn("dependency-cycle", kinds(found))

    # (d) a dependency edge that crosses no named contract.
    def test_uncontracted_seam_refused(self):
        m = self.fresh()
        # wiring still depends_on tokens, but drop the contract that covers it.
        del m["contracts"]["token-port"]
        found = cg.findings(m)
        self.assertIn("uncontracted-seam", kinds(found))
        seam = next(f for f in found if f["kind"] == "uncontracted-seam")
        self.assertIn("wiring", seam["subject"])

    # (e) the AI-native fork: a contract that smuggles its protocol past.
    def test_smuggled_seam_refused(self):
        m = self.fresh()
        del m["contracts"]["copy-style-port"]["trust"]
        found = cg.findings(m)
        self.assertIn("smuggled-seam", kinds(found))
        sm = next(f for f in found if f["kind"] == "smuggled-seam")
        self.assertEqual(sm["subject"], "copy-style-port")
        self.assertIn("trust", sm["why"])

    # a contract pointing at a non-module is also smuggled.
    def test_contract_naming_non_module_refused(self):
        m = self.fresh()
        m["contracts"]["token-port"]["between"] = ["tokens", "ghost-module"]
        found = cg.findings(m)
        self.assertIn("smuggled-seam", kinds(found))

    # the gate is not vacuous: a constant verdict cannot pass this suite.
    def test_gate_is_not_a_constant(self):
        # always-coherent would miss every break above; always-refuse would
        # miss the anchor. Proven directly: the anchor and a break disagree.
        coherent, _ = cg.verdict(self.manifest)
        broken = self.fresh()
        broken["modules"][1]["axis"]["reason"] = broken["modules"][0]["axis"]["reason"]
        refused, found = cg.verdict(broken)
        self.assertEqual(coherent, "coherent")
        self.assertEqual(refused, "refused")
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
