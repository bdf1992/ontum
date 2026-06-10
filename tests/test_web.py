"""Tests for the web inbox against done-line 0005:
the page is a pure fold rendering briefings value-first (atoms without a
briefing still render from what they have); the served verdict forms clear
items through the existing pen only; a stamp without a reason is refused."""

import json
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile, web

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_REAL = "value-gate.claude.v1"
STAMP_REAL = "owner-stamp.bdo.v1"

BRIEFING = {
    "headline": "Approve the test briefing",
    "value": "You want items judgeable in under a minute.",
    "why_now": "v0 was too thin to judge blind.",
    "if_accepted": "Briefed atoms become the norm.",
    "if_rejected": "The queue stays terse.",
    "cost_of_wrong_call": "Low; views only.",
    "mechanism": "A fold renders a page; forms post to the one pen.",
    "reading": ["loop/web.py"],
}


def make_atom(i, briefing=None):
    atom = {
        "id": f"atom.web-{i:02d}.v0",
        "story": {"text": f"As an AI, I need web atom {i} judged, because bdo wants it.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.web"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-owner-stamp"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }
    if briefing:
        atom["briefing"] = briefing
    return {"atom": atom}


class WebInboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / ".ai-native"
        (self.root / "log").mkdir(parents=True)
        (self.root / "atoms").mkdir(parents=True)
        (self.root / "atoms" / "atom.web-00.v0.json").write_text(
            json.dumps(make_atom(0, briefing=BRIEFING)), encoding="utf-8")
        (self.root / "atoms" / "atom.web-01.v0.json").write_text(
            json.dumps(make_atom(1)), encoding="utf-8")
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, "owner-stamp.mock-bdo.v0", STAMP_REAL, by="test-bdo")
        # both atoms reach the stamp: L0 stays mock here, the stamp is real
        orchestrate.orchestrate(self.root, quiet=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_render_is_value_first_and_tolerates_briefingless_atoms(self):
        page = web.render_html(self.root)
        # the briefed atom renders its layers
        self.assertIn("Approve the test briefing", page)
        self.assertIn("judgeable in under a minute", page)
        self.assertIn("why now:", page)
        self.assertIn("if you accept", page)
        self.assertIn("cost of a wrong call", page)
        self.assertIn("mechanism (only if you want it)", page)
        # value comes before mechanism (value first, mechanism after)
        self.assertLess(page.index("judgeable in under a minute"), page.index("forms post to the one pen"))
        # the gate's reasoning is on the page
        self.assertIn("what the gates said", page)
        # the briefingless atom still renders from its story
        self.assertIn("web atom 1 judged", page)
        # static render carries the clear command, not forms
        self.assertIn("python -m loop.node judge", page)
        self.assertNotIn("<form", page)

    def test_served_form_clears_through_the_one_pen(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), web.make_handler(self.root))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            page = urllib.request.urlopen(base + "/").read().decode("utf-8")
            self.assertIn("<form", page)  # served version is actionable
            data = urllib.parse.urlencode({"atom": "atom.web-00.v0", "verdict": "accept",
                                           "reason": "stamped from the page"}).encode()
            urllib.request.urlopen(base + "/judge", data=data)
            # the verdict landed as a receipt from the admitted stamp node
            fold = reconcile.Fold(self.root)
            receipts = [rc for rc in fold.receipts if rc["node"] == STAMP_REAL]
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["verdict"], "accept")
            self.assertEqual(receipts[0]["reason"], "stamped from the page")
            # and the loop carries the atom onward from it
            orchestrate.orchestrate(self.root, quiet=True)
            atoms = dict((a["id"], h) for a, h in reconcile.load_atoms(self.root))
            self.assertEqual(reconcile.atom_state(fold := reconcile.Fold(self.root),
                                                  atoms["atom.web-00.v0"]), "value_confirmed")
        finally:
            server.shutdown()

    def test_stamp_without_a_reason_is_refused(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), web.make_handler(self.root))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            data = urllib.parse.urlencode({"atom": "atom.web-00.v0", "verdict": "accept",
                                           "reason": "   "}).encode()
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(base + "/judge", data=data)
            self.assertEqual(ctx.exception.code, 400)
            fold = reconcile.Fold(self.root)
            self.assertEqual([rc for rc in fold.receipts if rc["node"] == STAMP_REAL], [])
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
