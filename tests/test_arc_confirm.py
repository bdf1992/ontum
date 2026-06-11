"""Done-line 0028: confirming an arc is the owner's standing stamp.

The lift from stamping pieces to confirming arcs: an atom under a confirmed epic
clears the owner's stamp on his confirmation — the loop stamps it (citing the
authorization) and carries it on — while an unconfirmed atom still parks for
him. Only bdo confirms an arc. The fold and the refusals are pure; the auto-
stamp runs the real reconcile pass against a temp records root.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile

SKELETON = REPO / ".ai-native" / "atoms" / "atom.loop-skeleton.v0.json"


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "epics").mkdir(parents=True)
    shutil.copy(SKELETON, root / "atoms" / "atom.loop-skeleton.v0.json")
    (root / "epics" / "epic.test.json").write_text(json.dumps({"epic": {
        "id": "epic.test", "value": "a test arc",
        "pieces": [{"atom": "atom.loop-skeleton.v0"}]}}), encoding="utf-8")
    return root


def _owner_stamp_real(root):
    node.admit_real(root, "owner-stamp.mock-bdo.v0", "owner-stamp.bdo.v1", "bdo")


def _drive(root, passes=80):
    for _ in range(passes):
        result = reconcile.pass_once(root, quiet=True)[0]
        if result in ("done", "needs-you"):
            return result
    return "ran-out"


def _owner_receipt(root):
    text = (root / "log" / "receipts.jsonl").read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        rc = json.loads(line)
        if rc.get("node") == "owner-stamp.bdo.v1":
            return rc
    return None


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestArcConfirmationFold(_Temp):
    def test_unconfirmed_is_none(self):
        self.assertIsNone(reconcile.arc_confirmation(reconcile.Fold(self.root), "epic.test"))

    def test_confirm_then_active(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertIsNotNone(reconcile.arc_confirmation(reconcile.Fold(self.root), "epic.test"))

    def test_withdraw_returns_to_none(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        node.confirm_arc(self.root, "epic.test", "bdo", enabled=False)
        self.assertIsNone(reconcile.arc_confirmation(reconcile.Fold(self.root), "epic.test"))


class TestConfirmArcRefusals(_Temp):
    def test_only_bdo_confirms(self):
        self.assertIsNone(node.confirm_arc(self.root, "epic.test", "claude"))

    def test_unknown_epic_refused(self):
        self.assertIsNone(node.confirm_arc(self.root, "epic.nope", "bdo"))


class TestAutoStamp(_Temp):
    def setUp(self):
        super().setUp()
        _owner_stamp_real(self.root)

    def test_unconfirmed_arc_parks_at_the_owner_stamp(self):
        result = _drive(self.root)
        self.assertEqual(result, "needs-you")
        self.assertIsNone(_owner_receipt(self.root))  # the loop never stamped

    def test_confirmed_arc_auto_stamps_and_cites_authorization(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        result = _drive(self.root)
        rc = _owner_receipt(self.root)
        self.assertIsNotNone(rc)
        self.assertEqual(rc["verdict"], "accept")
        self.assertIn("authorized_by", rc)
        self.assertEqual(result, "done")  # carries on through the remaining mocks


class TestNextActionArcAware(_Temp):
    def setUp(self):
        super().setUp()
        _owner_stamp_real(self.root)
        for _ in range(8):  # advance to the owner-stamp seam, where it parks
            reconcile.pass_once(self.root, quiet=True)

    def _atom(self):
        return reconcile.load_atoms(self.root)[0]

    def test_unconfirmed_is_await(self):
        atom, ahash = self._atom()
        epics = reconcile.load_epics(self.root)
        self.assertEqual(
            orchestrate.next_action(reconcile.Fold(self.root), atom, ahash, epics=epics),
            ("await", "owner-stamp.bdo.v1"))

    def test_confirmed_is_judge(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        atom, ahash = self._atom()
        epics = reconcile.load_epics(self.root)
        self.assertEqual(
            orchestrate.next_action(reconcile.Fold(self.root), atom, ahash, epics=epics),
            ("judge", "owner-stamp.bdo.v1"))


if __name__ == "__main__":
    unittest.main()
