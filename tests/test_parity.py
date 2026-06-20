"""§10 for the boundedness parity matrix (loop/parity.py, done-line 0115).

The matrix is the requirements mine for epic.repoprompt-parity. Its teeth are
the grip rule shared with term_economy / gaps: a citation that points to
nothing is a ghost. These tests prove (a) the committed matrix is honest —
every citation resolves — and (b) the check is NOT vacuous: a fabricated ghost
row of each verdict is caught. A validator that always returned "fine" would
fail (b).
"""

import unittest
from pathlib import Path

from loop import parity


class TestMatrixHonest(unittest.TestCase):
    def test_committed_matrix_has_no_ghosts(self):
        problems = parity.validate()
        self.assertEqual(problems, [], f"committed matrix has ghosts: {problems}")

    def test_every_row_has_a_known_verdict(self):
        for row in parity.MATRIX:
            self.assertIn(row["verdict"], parity.VERDICTS, row)

    def test_every_capability_and_bound_is_stated(self):
        for row in parity.MATRIX:
            self.assertTrue(row.get("capability"), row)
            self.assertTrue(row.get("bounds"), row)

    def test_the_epic_resolves(self):
        # build rows are meaningless if the owning epic isn't on disk.
        self.assertIsNotNone(parity.epic_atom_ids(), "epic.repoprompt-parity missing")


class TestTeeth(unittest.TestCase):
    """The check must be able to bite — a fabricated row of each verdict is
    caught. If any of these passed validation, the gate would be decorative."""

    def test_ghost_have_file_is_caught(self):
        ghost = ({"capability": "x", "bounds": "y", "verdict": "have",
                  "cites": "loop/this-file-does-not-exist.py"},)
        self.assertTrue(parity.validate(matrix=ghost), "ghost have not caught")

    def test_ghost_dont_epic_is_caught(self):
        ghost = ({"capability": "x", "bounds": "y", "verdict": "dont-double-build",
                  "cites": "epic.no-such-epic"},)
        self.assertTrue(parity.validate(matrix=ghost), "ghost epic not caught")

    def test_ghost_build_atom_is_caught(self):
        ghost = ({"capability": "x", "bounds": "y", "verdict": "build",
                  "cites": "atom.not-in-the-epic.v9"},)
        self.assertTrue(parity.validate(matrix=ghost), "ghost atom not caught")

    def test_unknown_verdict_is_caught(self):
        ghost = ({"capability": "x", "bounds": "y", "verdict": "maybe",
                  "cites": "whatever"},)
        self.assertTrue(parity.validate(matrix=ghost), "unknown verdict not caught")

    def test_a_real_have_citation_actually_resolves(self):
        # The positive control for the teeth: a real file passes.
        real = ({"capability": "x", "bounds": "y", "verdict": "have",
                 "cites": "loop/parity.py"},)
        self.assertEqual(parity.validate(matrix=real), [])


if __name__ == "__main__":
    unittest.main()
