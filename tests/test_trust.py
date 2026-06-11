"""Done-line 0024: the trust ladder refuses.

The §10 case for capability rungs: a class with no rung is denied everything;
a granted rung permits up to its level and no further; a later rung can lower
an earlier one (superseded, never erased); ontum-touch is LOCKED for every
class and the pen refuses to grant it; and a rung not signed by bdo refuses
(nothing grants itself a rung). The fold and the refusals are pure; the write
path runs through the node pen against a temp log.
"""

import pathlib
import shutil
import tempfile
import unittest

from loop import node, trust


class _TempLog(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        (self.root / "log").mkdir()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)


class TestLadderFold(_TempLog):
    def test_no_rung_denies_everything(self):
        self.assertFalse(trust.permits("summoned-session", "read", self.root))

    def test_a_grant_permits_up_to_its_level_and_no_higher(self):
        node.admit_rung(self.root, "summoned-session", "judge", "bdo")
        self.assertTrue(trust.permits("summoned-session", "read", self.root))
        self.assertTrue(trust.permits("summoned-session", "judge", self.root))
        self.assertFalse(trust.permits("summoned-session", "author", self.root))

    def test_supersede_can_lower_a_rung(self):
        first = node.admit_rung(self.root, "local-model", "author", "bdo")
        self.assertTrue(trust.permits("local-model", "author", self.root))
        node.admit_rung(self.root, "local-model", "read", "bdo",
                        supersedes=first["id"])
        self.assertFalse(trust.permits("local-model", "author", self.root))
        self.assertTrue(trust.permits("local-model", "read", self.root))


class TestOntumTouchLocked(_TempLog):
    def test_locked_for_every_class(self):
        for cls in trust.AGENT_CLASSES:
            self.assertFalse(trust.permits(cls, "ontum-touch", self.root), cls)

    def test_pen_refuses_to_grant_it_and_writes_nothing(self):
        adm = node.admit_rung(self.root, "local-model", "ontum-touch", "bdo")
        self.assertIsNone(adm)
        self.assertEqual(trust._admissions(self.root), [])

    def test_bdos_boundary_is_quoted_in_the_refusal(self):
        reason = trust.rung_refusal("local-model", "ontum-touch", "bdo")
        self.assertIn("LOCKED", reason)
        self.assertIn("out of this epic's remit", reason)


class TestNoSelfGrant(unittest.TestCase):
    def test_only_bdo_grants(self):
        self.assertIsNotNone(trust.rung_refusal("summoned-session", "read", "claude"))
        self.assertIsNone(trust.rung_refusal("summoned-session", "read", "bdo"))

    def test_unknown_class_and_capability_refuse(self):
        self.assertIsNotNone(trust.rung_refusal("rogue-class", "read", "bdo"))
        self.assertIsNotNone(trust.rung_refusal("summoned-session", "fly", "bdo"))


if __name__ == "__main__":
    unittest.main()
