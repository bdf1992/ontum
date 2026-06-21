"""Done-line 0161: the local-preview deployment face (`loop.preview`) — serve a
named snapshot on localhost, recorded as a promotion to the local env.

The §10 teeth: you do not preview a lie. Only an ACCEPTED snapshot is serveable
to the local env; a snapshot that resolves stale, ghost, or unaccepted is
refused at the gate and NOTHING is recorded. The control (an accepted snapshot)
deploys and records exactly one local_deployment, so the refusal is the lie's
doing; and the SAME snapshot is refused before its atom is accepted and deploys
after — the gate is not a constant.

Acceptance is read from snapshot.resolve (which derives it from the pipeline's
receipts), never re-judged here.
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

from loop import preview, reconcile, snapshot

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


def _ledger(root):
    return preview.local_deployments(reconcile.Fold(root))


class LocalPreview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _accepted_snapshot(self, name="snap", aid="atom.foo.v0", body="x"):
        h = _atom(self.root, aid, body)
        _judge(self.root, h)
        snapshot.mint(self.root, name, [aid], COMMIT, by="claude")
        return name

    # --- the happy face: an accepted snapshot deploys + records -------------

    def test_accepted_deploys_and_records(self):
        self._accepted_snapshot("snap")
        adm, g = preview.deploy_local(self.root, "snap", by="claude")
        self.assertIsNotNone(adm)
        self.assertTrue(g["deployable"])
        self.assertEqual(adm["environment"], "local")
        self.assertEqual(adm["snapshot"], "snap")
        self.assertEqual(len(_ledger(self.root)), 1)  # exactly one record

    # --- the §10 teeth: a snapshot that lies is refused, nothing recorded ---

    def test_stale_refused_nothing_recorded(self):
        self._accepted_snapshot("snap", body="original")
        _atom(self.root, "atom.foo.v0", body="EDITED")  # -> stale
        adm, g = preview.deploy_local(self.root, "snap", by="claude")
        self.assertIsNone(adm)
        self.assertEqual(g["verdict"], "stale")
        self.assertEqual(_ledger(self.root), [])

    def test_ghost_refused_nothing_recorded(self):
        self._accepted_snapshot("snap")
        (self.root / "atoms" / "atom.foo.v0.json").unlink()  # -> ghost
        adm, g = preview.deploy_local(self.root, "snap", by="claude")
        self.assertIsNone(adm)
        self.assertEqual(g["verdict"], "ghost")
        self.assertEqual(_ledger(self.root), [])

    def test_unaccepted_refused_nothing_recorded(self):
        _atom(self.root, "atom.foo.v0")  # never judged
        snapshot.mint(self.root, "snap", ["atom.foo.v0"], COMMIT, by="claude")
        adm, g = preview.deploy_local(self.root, "snap", by="claude")
        self.assertIsNone(adm)
        self.assertEqual(g["verdict"], "unaccepted")
        self.assertEqual(_ledger(self.root), [])

    def test_unknown_snapshot_refused(self):
        adm, g = preview.deploy_local(self.root, "nope", by="claude")
        self.assertIsNone(adm)
        self.assertFalse(g["deployable"])
        self.assertEqual(_ledger(self.root), [])

    # --- the gate is not vacuous -------------------------------------------

    def test_gate_not_constant(self):
        """The SAME snapshot is held before its atom is accepted and deployable
        after — the gate tracks the log, not a literal."""
        h = _atom(self.root, "atom.foo.v0")
        snapshot.mint(self.root, "snap", ["atom.foo.v0"], COMMIT, by="claude")
        before = preview.gate("snap", self.root)["deployable"]
        _judge(self.root, h)
        after = preview.gate("snap", self.root)["deployable"]
        self.assertFalse(before)
        self.assertTrue(after)

    # --- a deployment records who served it --------------------------------

    def test_missing_by_refused(self):
        self._accepted_snapshot("snap")
        adm, g = preview.deploy_local(self.root, "snap", by="")
        self.assertIsNone(adm)          # accepted, but no signer
        self.assertTrue(g["deployable"])
        self.assertEqual(_ledger(self.root), [])

    # --- the CI seam --------------------------------------------------------

    def test_gate_cli_exit_codes(self):
        self._accepted_snapshot("snap", body="orig")
        self.assertEqual(
            preview.main(["--root", str(self.root), "gate", "--name", "snap"]), 0)
        _atom(self.root, "atom.foo.v0", body="EDIT")  # -> stale
        self.assertEqual(
            preview.main(["--root", str(self.root), "gate", "--name", "snap"]), 1)

    def test_serve_cli_records_without_blocking(self):
        self._accepted_snapshot("snap")
        rc = preview.main(["--root", str(self.root), "serve", "--name", "snap",
                           "--by", "claude", "--no-serve"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(_ledger(self.root)), 1)


if __name__ == "__main__":
    unittest.main()
