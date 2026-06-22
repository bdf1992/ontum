"""§10 test for the owner-gesture index (loop/owner.py).

The index exists to END the CLI-at-owner offload — so its teeth must refuse the
very thing it replaces: an "opener" that is really a command run at bdo, or a
ghost opener that resolves to nothing. Non-vacuous: the real index validates
sound, and each fabricated defect is caught.
"""

import unittest
from pathlib import Path

from loop import owner

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / ".ai-native"          # owner._repo(ROOT) == REPO


class OwnerIndexTest(unittest.TestCase):
    def test_real_index_is_sound(self):
        # every real opener resolves on disk; no CLI-at-owner route; the one
        # no-surface gap (done-supersede) is correctly a gap
        self.assertEqual(owner.validate(root=ROOT), [])
        idx = owner.index(root=ROOT)
        self.assertTrue(any(d["kind"] == "arc-confirm" for d in idx))

    def test_ghost_opener_is_caught(self):
        bad = [{"kind": "x", "what": "w", "opener": ".claude/skills/nope/ghost.py",
                "open_verb": "ghost.py open", "label": "x", "no_surface": False}]
        probs = owner.validate(bad, root=ROOT)
        self.assertTrue(any("ghost" in p for p in probs), probs)

    def test_cli_at_owner_route_is_refused(self):
        # a resolving opener, but a verb that is a confirm command run at bdo —
        # the exact offload the index forbids
        bad = [{"kind": "x", "what": "w",
                "opener": ".claude/skills/issue/issue.py",
                "open_verb": "loop.node confirm-arc --epic e --by bdo",
                "label": "x", "no_surface": False}]
        probs = owner.validate(bad, root=ROOT)
        self.assertTrue(any("CLI-at-owner" in p for p in probs), probs)

    def test_misflagged_gap_is_caught(self):
        # claims no-surface, but a real pen resolves -> it is NOT a gap
        bad = [{"kind": "x", "what": "w",
                "opener": ".claude/skills/issue/issue.py",
                "open_verb": "issue.py open", "label": None, "no_surface": True}]
        probs = owner.validate(bad, root=ROOT)
        self.assertTrue(any("not a gap" in p for p in probs), probs)

    def test_surface_for_names_the_pen(self):
        d = owner.surface_for("arc-confirm", root=ROOT)
        self.assertIsNotNone(d)
        self.assertIn("intake.py", d["open_verb"])
        self.assertIsNone(owner.surface_for("no-such-kind", root=ROOT))

    def test_index_raises_when_unsound(self):
        # index() must never hand out routes from a broken table
        broken = list(owner.DECISIONS) + [
            {"kind": "bad", "what": "w", "opener": ".claude/skills/nope/x.py",
             "open_verb": "x", "label": None, "no_surface": False}]
        self.assertTrue(owner.validate(broken, root=ROOT))


if __name__ == "__main__":
    unittest.main()
