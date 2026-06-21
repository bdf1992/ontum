"""Done-line 0162: the git-tier staging rung + promotion path (`loop.promote`)
— main as the recorded staging rung, and one ordered path local → staging →
production per snapshot.

The §10 teeth: the promotion path refuses to fit out of order. Only an ACCEPTED
snapshot may be promoted to staging, and only after it reached the local rung; a
non-accepted or not-yet-local snapshot is refused with nothing recorded. The
path fold flags an out-of-order state it reads (production reached without
staging). The control (an accepted, locally-deployed snapshot) promotes clean,
and the same snapshot is refused before its local deployment and promotes after
— the gate is not a constant.

Acceptance and the production rung are read from snapshot.resolve / deploy /
preview, never re-derived here.
"""

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import deploy, preview, promote, reconcile, snapshot

COMMIT = "a" * 40


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    return root


def _atom(root, aid, body="x"):
    raw = json.dumps({"atom": {"id": aid, "body": body}}, sort_keys=True).encode("utf-8")
    (root / "atoms" / (aid + ".json")).write_bytes(raw)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _judge(root, artifact_hash, verdict="accept"):
    node = snapshot.VALUE_STAGE["node"]
    rc = {"id": "rcp." + reconcile.short_hash(node, artifact_hash, verdict),
          "node": node, "artifact_hash": artifact_hash, "verdict": verdict}
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)


def _staged(root):
    return promote.staging_promotions(reconcile.Fold(root))


class StagingRung(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _accepted(self, name="snap", aid="atom.foo.v0", body="x", commit=COMMIT):
        h = _atom(self.root, aid, body)
        _judge(self.root, h)
        snapshot.mint(self.root, name, [aid], commit, by="claude")
        return name

    def _local(self, name="snap"):
        adm, _ = preview.deploy_local(self.root, name, by="claude")
        return adm

    # --- the happy rung: accepted + locally deployed promotes to staging ----

    def test_promotes_accepted_locally_deployed(self):
        self._accepted("snap")
        self._local("snap")
        adm, g = promote.promote_staging(self.root, "snap", by="claude")
        self.assertIsNotNone(adm)
        self.assertEqual(adm["environment"], "staging")
        self.assertIn("snap", _staged(self.root))
        path = promote.promotion_path("snap", self.root)
        self.assertTrue(path["reached"]["local"])
        self.assertTrue(path["reached"]["staging"])
        self.assertFalse(path["out_of_order"])

    # --- §10 teeth: refuse non-accepted / out-of-order, record nothing -------

    def test_refuses_non_accepted(self):
        _atom(self.root, "atom.foo.v0")  # never judged
        snapshot.mint(self.root, "snap", ["atom.foo.v0"], COMMIT, by="claude")
        # even if "locally deployed" were attempted, preview refuses unaccepted;
        # promote must refuse at the gate regardless.
        adm, g = promote.promote_staging(self.root, "snap", by="claude")
        self.assertIsNone(adm)
        self.assertEqual(g["verdict"], "unaccepted")
        self.assertEqual(_staged(self.root), {})

    def test_refuses_out_of_order_without_local(self):
        self._accepted("snap")           # accepted but NOT locally deployed
        adm, g = promote.promote_staging(self.root, "snap", by="claude")
        self.assertIsNone(adm)
        self.assertTrue(g["verdict"] == "accepted")
        self.assertFalse(g["local"])
        self.assertEqual(_staged(self.root), {})

    def test_path_flags_production_without_staging(self):
        """A snapshot whose commit reached production but never reached staging
        is an out-of-order path the fold names (two locally-fine records —
        a production promotion and an empty staging rung — refuse to fit)."""
        self._accepted("snap", commit=COMMIT)
        deploy.promote(self.root, COMMIT, by="bdo")  # production reached
        path = promote.promotion_path("snap", self.root)
        self.assertTrue(path["reached"]["production"])
        self.assertFalse(path["reached"]["staging"])
        self.assertTrue(path["out_of_order"])

    # --- the gate is not vacuous -------------------------------------------

    def test_gate_not_constant(self):
        self._accepted("snap")
        before = promote.gate("snap", self.root)["promotable"]   # no local yet
        self._local("snap")
        after = promote.gate("snap", self.root)["promotable"]
        self.assertFalse(before)
        self.assertTrue(after)

    def test_missing_by_refused(self):
        self._accepted("snap")
        self._local("snap")
        adm, g = promote.promote_staging(self.root, "snap", by="")
        self.assertIsNone(adm)
        self.assertTrue(g["promotable"])
        self.assertEqual(_staged(self.root), {})

    # --- the CI seam --------------------------------------------------------

    def test_gate_cli_exit_codes(self):
        self._accepted("snap")
        self.assertEqual(
            promote.main(["--root", str(self.root), "gate", "--name", "snap"]), 1)
        self._local("snap")
        self.assertEqual(
            promote.main(["--root", str(self.root), "gate", "--name", "snap"]), 0)

    def test_stage_cli_records(self):
        self._accepted("snap")
        self._local("snap")
        self.assertEqual(
            promote.main(["--root", str(self.root), "stage", "--name", "snap",
                          "--by", "claude"]), 0)
        self.assertIn("snap", _staged(self.root))


if __name__ == "__main__":
    unittest.main()
