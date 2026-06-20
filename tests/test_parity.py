"""§10 for the boundedness parity matrix (loop/parity.py, done-line 0115).

The matrix is the requirements mine for epic.repoprompt-parity. Its teeth are
the grip rule shared with term_economy / gaps: a citation that points to
nothing is a ghost. These tests prove (a) the committed matrix is honest —
every citation resolves — and (b) the check is NOT vacuous: a fabricated ghost
row of each verdict is caught. A validator that always returned "fine" would
fail (b).

Done-line 0132 sharpens the `have` tooth: a `have` must carry `evidence` its
cited file actually contains, so a row cannot stand on a real file that does
not do the claimed thing (the ghost-in-spirit that let the multi-root row
falsely claim field.py folds three repos). The new teeth-tests prove an
evidence-free have and a present-file-but-absent-evidence have are both caught.
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

    def test_a_real_have_citation_with_evidence_resolves(self):
        # The positive control for the teeth: a real file whose evidence it
        # contains passes.
        real = ({"capability": "x", "bounds": "y", "verdict": "have",
                 "cites": "loop/parity.py", "evidence": "boundedness"},)
        self.assertEqual(parity.validate(matrix=real), [])

    def test_a_have_without_evidence_is_caught(self):
        # The sharper tooth (done-line 0132): file-exists is not proof. A have
        # that cites a real file but carries no evidence cannot stand.
        bare = ({"capability": "x", "bounds": "y", "verdict": "have",
                 "cites": "loop/parity.py"},)
        self.assertTrue(parity.validate(matrix=bare),
                        "an evidence-free have was let through")

    def test_a_have_whose_evidence_is_absent_is_caught(self):
        # The ghost-in-spirit this whole tooth exists for — the exact shape of
        # the false multi-root row: a REAL file, but it does not contain the
        # claimed evidence, so the row does not prove its claim.
        ghost_in_spirit = ({"capability": "Multi-root", "bounds": "y",
                            "verdict": "have", "cites": "loop/field.py",
                            "evidence": "holonsearch"},)
        problems = parity.validate(matrix=ghost_in_spirit)
        self.assertTrue(problems, "a real file with absent evidence was let through")
        self.assertIn("ghost-in-spirit", problems[0])


if __name__ == "__main__":
    unittest.main()
