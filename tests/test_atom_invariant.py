"""The atom invariant, executable at the PR/merge seam (retro 0037).

The substrate has always required every particle of work to be an atom on the
log — ambient control senses field-state as a fold over the log (§15/D-5), so a
work-particle that is not an atom is invisible to the controller. Tonight's
failure was that the loop was bypassable: ~13 PRs, one real-atom receipt. These
are the brutally-small proof that the two pure refusals restore the invariant
at the breached boundary:

    1. atomless PR              refuses   (atom_backed_refusal)
    2. atom with a real receipt allows    (both refusals pass)
    3. mock-only receipt        refuses   (real_gate_refusal)

The §10 teeth (tests/CLAUDE.md): a PR whose atom carries only a *mock* verdict
is locally fine in every way the PR can see, yet must not land — a story about
a gate event is not a gate event. The refusal is what notices.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "pr_pen", ROOT / ".claude" / "skills" / "branch-ritual" / "pr.py")
pr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pr)

ATOM = "atom.rename-vars.v0"

# a real (non-mock) gate verdict for ATOM, and a mock skeleton verdict for it
REAL_RECEIPT = (
    '{"artifact_id":"%s","node":"value-gate.claude.v1","verdict":"reject_no_value",'
    '"id":"rcp.real1"}' % ATOM)
MOCK_RECEIPT = (
    '{"artifact_id":"%s","node":"value-gate.mock.v0","verdict":"accept",'
    '"id":"rcp.mock1"}' % ATOM)
OTHER_ATOM_RECEIPT = (
    '{"artifact_id":"atom.something-else.v0","node":"value-gate.claude.v1",'
    '"verdict":"accept","id":"rcp.other"}')


class AtomBackedRefusal(unittest.TestCase):
    """The PR boundary: no atom id + no backing receipt = no PR."""

    def test_1_atomless_pr_refuses(self):
        self.assertIsNotNone(pr.atom_backed_refusal("", REAL_RECEIPT))
        self.assertIsNotNone(pr.atom_backed_refusal(None, REAL_RECEIPT))

    def test_2_atom_with_a_receipt_allows(self):
        self.assertIsNone(pr.atom_backed_refusal(ATOM, REAL_RECEIPT))

    def test_atom_with_no_receipt_on_the_log_refuses(self):
        # the atom is named, but nothing on the log judged it: it never
        # entered the loop, so it is not yet PR-able.
        self.assertIsNotNone(pr.atom_backed_refusal(ATOM, OTHER_ATOM_RECEIPT))


class RealGateRefusal(unittest.TestCase):
    """The merge boundary: no real (non-mock) gate receipt = no merge."""

    def test_2_atom_with_a_real_receipt_allows(self):
        self.assertIsNone(pr.real_gate_refusal(ATOM, REAL_RECEIPT))

    def test_3_mock_only_receipt_refuses(self):
        # the §10 case: a verdict exists, the PR looks fine — but it is a
        # constant from a mock, not a real gate. It must not land.
        reason = pr.real_gate_refusal(ATOM, MOCK_RECEIPT)
        self.assertIsNotNone(reason)
        self.assertIn("mock", reason.lower())

    def test_a_real_receipt_among_mocks_lands(self):
        # history is never retro-invalidated (D-5): once a real node has
        # judged, the earlier mock receipts stand but no longer gate.
        self.assertIsNone(
            pr.real_gate_refusal(ATOM, MOCK_RECEIPT + "\n" + REAL_RECEIPT))

    def test_no_receipt_at_all_refuses(self):
        self.assertIsNotNone(pr.real_gate_refusal(ATOM, OTHER_ATOM_RECEIPT))


if __name__ == "__main__":
    unittest.main()
