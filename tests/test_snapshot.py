"""Done-line 0155: the snapshot acceptance unit (`loop.snapshot`) — the spine
of epic.environments, the unit a second party accepts.

The §10 teeth: a snapshot is a frozen reference to atom bytes; an atom file is
editable; each is locally fine. When they refuse to fit — the atom's live bytes
no longer match the hash the snapshot froze (STALE), or the atom names no file
at all (GHOST) — the fold notices and refuses to call the snapshot accepted. The
control (the same snapshot over a current, accepted atom) resolves `accepted`,
so the refusal is the lie's doing, not a flaky red; and a constant/fabricated
resolver cannot pass both the accepted and the stale/unaccepted case (the SAME
snapshot resolves differently as the log changes).

Acceptance is DERIVED from the pipeline's own value-gate receipts, never a
second authority: a snapshot over an unjudged or refused atom is not accepted.
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

from loop import reconcile, snapshot

COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    return root


def _atom(root, aid, body="x"):
    """Write an atom file and return its content-hash (the way load_atoms
    computes it: sha256 of the exact file bytes)."""
    raw = json.dumps({"atom": {"id": aid, "body": body}}, sort_keys=True).encode("utf-8")
    (root / "atoms" / (aid + ".json")).write_bytes(raw)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _judge(root, artifact_hash, verdict="accept", node=None):
    """Append a value-gate receipt for an atom version (the independent
    acceptance the snapshot derives, never re-judges)."""
    node = node or snapshot.VALUE_STAGE["node"]
    rc = {"id": "rcp." + reconcile.short_hash(node, artifact_hash, verdict),
          "node": node, "artifact_hash": artifact_hash, "verdict": verdict}
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)


class SnapshotSpine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- the happy spine: accepted once as one thing ------------------------

    def test_accepted_over_current_accepted_atom(self):
        h = _atom(self.root, "atom.foo.v0")
        _judge(self.root, h)
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        res = snapshot.resolve("snap1", self.root)
        self.assertEqual(res["verdict"], "accepted")
        self.assertEqual(res["offenders"], [])
        self.assertEqual(res["commit"], COMMIT_A)

    # --- the §10 teeth: a snapshot that lies about its join -----------------

    def test_stale_when_atom_edited_after_mint(self):
        """The teeth: a frozen reference and an edited atom refuse to fit. The
        control proves it was accepted before the edit, so STALE is the edit's
        doing."""
        h = _atom(self.root, "atom.foo.v0", body="original")
        _judge(self.root, h)
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        self.assertEqual(snapshot.resolve("snap1", self.root)["verdict"], "accepted")
        _atom(self.root, "atom.foo.v0", body="EDITED IN PLACE")  # live bytes change
        res = snapshot.resolve("snap1", self.root)
        self.assertEqual(res["verdict"], "stale")
        self.assertIn("atom.foo.v0", res["offenders"])

    def test_mint_refuses_ghost_binding(self):
        """A snapshot must reference a real atom; minting over a non-existent
        atom is refused at the pen and writes nothing."""
        self.assertIsNone(
            snapshot.mint(self.root, "snap1", ["atom.nope.v0"], COMMIT_A, by="claude"))
        self.assertEqual(snapshot.dataset(self.root)["snapshots"], [])

    def test_ghost_when_atom_removed_after_mint(self):
        h = _atom(self.root, "atom.foo.v0")
        _judge(self.root, h)
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        (self.root / "atoms" / "atom.foo.v0.json").unlink()
        res = snapshot.resolve("snap1", self.root)
        self.assertEqual(res["verdict"], "ghost")
        self.assertIn("atom.foo.v0", res["offenders"])

    def test_severity_ghost_beats_stale(self):
        h1 = _atom(self.root, "atom.a.v0"); _judge(self.root, h1)
        h2 = _atom(self.root, "atom.b.v0"); _judge(self.root, h2)
        snapshot.mint(self.root, "s", ["atom.a.v0", "atom.b.v0"], COMMIT_A, by="claude")
        _atom(self.root, "atom.a.v0", body="EDIT")          # a -> stale
        (self.root / "atoms" / "atom.b.v0.json").unlink()    # b -> ghost
        self.assertEqual(snapshot.resolve("s", self.root)["verdict"], "ghost")

    # --- acceptance is derived, never asserted ------------------------------

    def test_unaccepted_when_not_judged(self):
        _atom(self.root, "atom.foo.v0")  # no value-gate receipt
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        self.assertEqual(snapshot.resolve("snap1", self.root)["verdict"], "unaccepted")

    def test_unaccepted_when_refused(self):
        h = _atom(self.root, "atom.foo.v0")
        _judge(self.root, h, verdict="reject_no_value")  # an explicit no
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        self.assertEqual(snapshot.resolve("snap1", self.root)["verdict"], "unaccepted")

    def test_one_bad_atom_spoils_the_snapshot(self):
        h1 = _atom(self.root, "atom.a.v0"); _judge(self.root, h1)
        _atom(self.root, "atom.b.v0")  # unjudged
        snapshot.mint(self.root, "s", ["atom.a.v0", "atom.b.v0"], COMMIT_A, by="claude")
        res = snapshot.resolve("s", self.root)
        self.assertEqual(res["verdict"], "unaccepted")
        self.assertEqual(res["offenders"], ["atom.b.v0"])

    def test_resolver_is_not_constant(self):
        """A fabricated/constant resolver cannot pass: the SAME snapshot resolves
        unaccepted before its atom is judged and accepted after — the verdict
        tracks the log, not a literal."""
        h = _atom(self.root, "atom.foo.v0")
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        before = snapshot.resolve("snap1", self.root)["verdict"]
        _judge(self.root, h)
        after = snapshot.resolve("snap1", self.root)["verdict"]
        self.assertEqual(before, "unaccepted")
        self.assertEqual(after, "accepted")

    # --- supersession: latest-by-name wins; withdraw removes ----------------

    def test_latest_by_name_wins(self):
        h = _atom(self.root, "atom.foo.v0"); _judge(self.root, h)
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_B, by="claude")
        self.assertEqual(snapshot.resolve("snap1", self.root)["commit"], COMMIT_B)

    def test_withdraw_removes_the_snapshot(self):
        h = _atom(self.root, "atom.foo.v0"); _judge(self.root, h)
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude")
        snapshot.mint(self.root, "snap1", ["atom.foo.v0"], COMMIT_A, by="claude",
                      enabled=False)
        self.assertIsNone(snapshot.resolve("snap1", self.root))

    # --- pen refusals -------------------------------------------------------

    def test_mint_refuses_empty_name_by_and_atoms(self):
        _atom(self.root, "atom.foo.v0")
        self.assertIsNone(snapshot.mint(self.root, "", ["atom.foo.v0"], None, "claude"))
        self.assertIsNone(snapshot.mint(self.root, "s", ["atom.foo.v0"], None, ""))
        self.assertIsNone(snapshot.mint(self.root, "s", [], None, "claude"))

    # --- the CLI seam -------------------------------------------------------

    def test_cli_mint_and_resolve_exit_codes(self):
        h = _atom(self.root, "atom.foo.v0"); _judge(self.root, h)
        self.assertEqual(snapshot.main(
            ["--root", str(self.root), "mint", "--name", "s",
             "--atoms", "atom.foo.v0", "--by", "claude"]), 0)
        self.assertEqual(snapshot.main(
            ["--root", str(self.root), "resolve", "--name", "s"]), 0)
        _atom(self.root, "atom.foo.v0", body="EDIT")  # now stale
        self.assertEqual(snapshot.main(
            ["--root", str(self.root), "resolve", "--name", "s"]), 1)


if __name__ == "__main__":
    unittest.main()
