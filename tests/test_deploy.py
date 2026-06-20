"""Done-line 0137: the production gate (`loop.deploy`) — the live URL stops
changing without bdo's stamp.

The §10 teeth: a candidate commit and bdo's stamp are each locally fine; when
they name different snapshots they refuse to fit, and the gate HOLDS rather than
letting unstamped content reach the live surface. The control (the same candidate
once it IS the stamped snapshot) promotes clean, so the hold is the stamp's
doing, not a flaky red — and a constant/fabricated gate cannot pass both the
promote and the hold case.

It also proves the authority is bdo's alone: the pen refuses every non-bdo
signer and writes nothing, and the fold re-checks the signature so a hand-
appended promotion cannot forge the live snapshot.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import deploy, reconcile

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    return root


class ProductionGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- the unstamped passthrough transition -------------------------------

    def test_unstamped_is_passthrough_not_a_take(self):
        """Before the first stamp the gate holds no snapshot: HEAD passes
        through (landing the gate never dark-takes the live site)."""
        self.assertIsNone(deploy.production_snapshot(self.root))
        r = deploy.gate(SHA_A, self.root)
        self.assertEqual(r["verdict"], "passthrough")
        self.assertEqual(r["deploy"], SHA_A)  # serves the candidate, transitionally

    # --- bdo's stamp engages the teeth --------------------------------------

    def test_stamp_then_promote_matches(self):
        adm = deploy.promote(self.root, SHA_A, by="bdo")
        self.assertIsNotNone(adm)
        self.assertEqual(deploy.production_snapshot(self.root), SHA_A)
        r = deploy.gate(SHA_A, self.root)
        self.assertEqual(r["verdict"], "promote")
        self.assertEqual(r["deploy"], SHA_A)

    def test_unstamped_candidate_is_held_not_deployed(self):
        """The §10 refusal: a stamp on A and a candidate B are each fine; they
        refuse to fit, so the gate HOLDS and the deploy serves the stamped A,
        never the candidate B."""
        deploy.promote(self.root, SHA_A, by="bdo")
        r = deploy.gate(SHA_B, self.root)
        self.assertEqual(r["verdict"], "hold")
        self.assertEqual(r["snapshot"], SHA_A)
        self.assertEqual(r["deploy"], SHA_A)  # the stamped snapshot, not B

    def test_gate_is_not_constant(self):
        """A fabricated/constant gate cannot pass both: the SAME candidate is
        held before its stamp and promoted after — the verdict tracks the log."""
        before = deploy.gate(SHA_B, self.root)["verdict"]
        deploy.promote(self.root, SHA_A, by="bdo")
        held = deploy.gate(SHA_B, self.root)["verdict"]
        deploy.promote(self.root, SHA_B, by="bdo")
        after = deploy.gate(SHA_B, self.root)["verdict"]
        self.assertEqual(before, "passthrough")
        self.assertEqual(held, "hold")
        self.assertEqual(after, "promote")

    # --- supersession moves the live snapshot -------------------------------

    def test_superseding_promotion_moves_the_snapshot(self):
        deploy.promote(self.root, SHA_A, by="bdo")
        deploy.promote(self.root, SHA_C, by="bdo")  # latest wins
        self.assertEqual(deploy.production_snapshot(self.root), SHA_C)
        self.assertEqual(deploy.gate(SHA_A, self.root)["verdict"], "hold")
        self.assertEqual(deploy.gate(SHA_C, self.root)["verdict"], "promote")

    def test_withdraw_returns_to_passthrough(self):
        deploy.promote(self.root, SHA_A, by="bdo")
        deploy.promote(self.root, SHA_A, by="bdo", enabled=False)  # withdraw
        self.assertIsNone(deploy.production_snapshot(self.root))
        self.assertEqual(deploy.gate(SHA_A, self.root)["verdict"], "passthrough")

    # --- the authority is bdo's alone ---------------------------------------

    def test_pen_refuses_non_bdo_signer(self):
        adm = deploy.promote(self.root, SHA_A, by="claude")
        self.assertIsNone(adm)
        # nothing was written: still unstamped
        self.assertIsNone(deploy.production_snapshot(self.root))

    def test_pen_refuses_empty_snapshot(self):
        self.assertIsNone(deploy.promote(self.root, "", by="bdo"))

    def test_fold_ignores_a_forged_non_bdo_promotion(self):
        """The pen is the only writer, but the fold re-checks the signature: a
        hand-appended promotion signed by anyone but bdo is not honored."""
        forged = {
            "id": "adm.forged", "type": deploy.PROMOTION_TYPE,
            "environment": "production", "snapshot": SHA_B, "enabled": True,
            "by": "claude", "supersedes": None, "ts": reconcile.now_ts(),
        }
        reconcile.append_line(self.root / "log" / "admissions.jsonl", forged)
        self.assertIsNone(deploy.production_snapshot(self.root))
        self.assertEqual(deploy.gate(SHA_B, self.root)["verdict"], "passthrough")

    # --- the CI seam exit codes ---------------------------------------------

    def test_cli_gate_exit_codes(self):
        deploy.promote(self.root, SHA_A, by="bdo")
        self.assertEqual(
            deploy.main(["--root", str(self.root), "gate", "--candidate", SHA_A]), 0)
        self.assertEqual(
            deploy.main(["--root", str(self.root), "gate", "--candidate", SHA_B]), 1)

    def test_cli_promote_refuses_non_bdo(self):
        self.assertEqual(
            deploy.main(["--root", str(self.root), "promote",
                         "--snapshot", SHA_A, "--by", "claude"]), 1)


if __name__ == "__main__":
    unittest.main()
