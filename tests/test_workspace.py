"""Tests for the claim↔workspace binding (done-line 0121): a branch belongs
to its work, and a commit asserting a claim the branch is not bound to is
refused.

The §10 teeth are the ways a fake binding fails:
- a `binding_refusal` that ALWAYS passes fails `test_collision_is_refused`
  and `test_unbound_is_refused` (the binding that can never refuse is a gauge,
  not a gate — the proposal's own non-example);
- one that ALWAYS refuses fails `test_matching_claim_passes` and
  `test_omitted_claim_passes` (a correct claim, and the backward-compatible
  no-`--claim` path, must not be refused).

The fold is exercised against a real temp log (claim → re-claim → release),
the pure refusal is unit-tested, and the live pen is driven as a subprocess
to prove `--claim` is wired through argparse to the binding check.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import workspace  # noqa: E402

PEN = REPO / ".claude" / "skills" / "branch-ritual" / "git.py"


class TestBindingRefusal(unittest.TestCase):
    """The pure refusal — no log, no git."""

    BOUND = {"claude/x": {"id": "adm.1", "claim": "atom.A", "by": "claude"}}

    def test_unbound_is_refused(self):
        r = workspace.binding_refusal("claude/x", "atom.A", {})
        self.assertIsNotNone(r)
        self.assertIn("not bound", r)
        self.assertIn("atom.A", r)

    def test_matching_claim_passes(self):
        self.assertIsNone(workspace.binding_refusal("claude/x", "atom.A", self.BOUND))

    def test_collision_is_refused(self):
        """The bite: 'I am doing work B' and 'this branch serves A' must not
        fit — the branch collision turned into a clean deny."""
        r = workspace.binding_refusal("claude/x", "atom.B", self.BOUND)
        self.assertIsNotNone(r)
        self.assertIn("atom.A", r)   # what the branch is bound to
        self.assertIn("atom.B", r)   # what you wrongly asserted

    def test_omitted_claim_passes(self):
        """Backward compatible: no `--claim` means no binding check."""
        self.assertIsNone(workspace.binding_refusal("claude/x", None, self.BOUND))
        self.assertIsNone(workspace.binding_refusal("claude/x", "", self.BOUND))

    def test_detached_head_with_claim_is_refused(self):
        r = workspace.binding_refusal("", "atom.A", {})
        self.assertIsNotNone(r)
        self.assertIn("detached", r)


class TestFold(unittest.TestCase):
    """The fold over a real temp log: claim, re-claim (supersede), release."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "log").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _claims(self):
        path = self.root / "log" / "admissions.jsonl"
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_claim_binds_the_branch(self):
        workspace.claim(self.root, "claude/x", "atom.A", "claude")
        bound = workspace.active_bindings(self.root)
        self.assertIn("claude/x", bound)
        self.assertEqual(bound["claude/x"]["claim"], "atom.A")

    def test_reclaim_supersedes_keeping_one_binding(self):
        first = workspace.claim(self.root, "claude/x", "atom.A", "claude")
        second = workspace.claim(self.root, "claude/x", "atom.B", "codex")
        # the re-claim points at the first (supersession), and the fold shows
        # exactly one live binding — the new claim
        self.assertEqual(second["supersedes"], first["id"])
        bound = workspace.active_bindings(self.root)
        self.assertEqual(len(bound), 1)
        self.assertEqual(bound["claude/x"]["claim"], "atom.B")
        self.assertEqual(bound["claude/x"]["by"], "codex")

    def test_release_frees_the_branch(self):
        workspace.claim(self.root, "claude/x", "atom.A", "claude")
        adm = workspace.release(self.root, "claude/x", "claude")
        self.assertIsNotNone(adm)
        self.assertNotIn("claude/x", workspace.active_bindings(self.root))
        # released branch is re-claimable (a fresh, non-superseding claim)
        again = workspace.claim(self.root, "claude/x", "atom.C", "claude")
        self.assertIsNone(again["supersedes"])
        self.assertEqual(workspace.active_bindings(self.root)["claude/x"]["claim"], "atom.C")

    def test_release_of_unbound_is_a_noop(self):
        self.assertIsNone(workspace.release(self.root, "claude/never", "claude"))

    def test_history_is_never_erased(self):
        """Every claim and release stands on the log — the fold reads the live
        ones, but the records are all there (no erasure)."""
        workspace.claim(self.root, "claude/x", "atom.A", "claude")
        workspace.claim(self.root, "claude/x", "atom.B", "claude")
        workspace.release(self.root, "claude/x", "claude")
        self.assertEqual(len(self._claims()), 3)  # nothing deleted


class TestLivePenWiring(unittest.TestCase):
    """Drive the git pen as a subprocess to prove `--claim` reaches the check."""

    def test_claim_for_unowned_work_refuses(self):
        """A commit asserting a `--claim` the current branch is not bound to is
        refused — whether the branch is UNBOUND ("not bound") or bound to OTHER
        work ("bound to ..., not ...", the collision). Which message fires
        depends on the live repo's binding state (this very branch is bound to
        its own atom when the dogfood ran), so the wiring proof is the stable
        part: `--claim` reaches `binding_refusal`, names the asserted claim,
        and denies cleanly."""
        p = subprocess.run(
            [sys.executable, str(PEN), "commit",
             "--claim", "atom.definitely-not-bound", "-m", "x"],
            cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
        self.assertNotEqual(p.returncode, 0,
                            "a --claim the branch is not bound to must refuse")
        self.assertIn("atom.definitely-not-bound", out)  # the asserted claim is named
        self.assertTrue("not bound" in out or "bound to" in out,
                        f"expected a binding refusal, got: {out}")

    def test_omitted_claim_does_not_trip_the_binding(self):
        p = subprocess.run(
            [sys.executable, str(PEN), "commit", "-m", "x"],
            cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
        # it may refuse for other reasons (nothing staged), but never for the
        # binding when no claim is asserted
        self.assertNotIn("not bound", out)
        self.assertNotIn("workspace binding", out.lower())


if __name__ == "__main__":
    unittest.main()
