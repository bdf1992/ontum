"""Done-line 0052: the seats bdo's open realness gestures admit are
prompt-pinned versioned source (§7).

Issues #82 and #83 ask bdo to admit merge-node.claude.v1 and
story-author.session.v1. When those admissions land, the seats they name
must already be pinnable: a versioned prompt in .ai-native/nodes/ whose
sha256 the spawn rail records at every branded spawn. The §10 shape: against
the repo's real records, the rail's refusal for these ids must be for want
of a RUNG (bdo's #89 gesture, out of this line's scope) and never "no
versioned prompt" — a seat the rail cannot pin is a seat whose admission
would land on air.
"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
AI_ROOT = ROOT / ".ai-native"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


spawn = _load("spawn_guard_for_seats", ROOT / ".claude" / "hooks" / "spawn_guard.py")

from loop.reconcile import node_prompt  # noqa: E402

SEATS = ["merge-node.claude.v1", "story-author.session.v1"]


class SeatsArePinnable(unittest.TestCase):
    def test_each_admitted_seat_has_a_versioned_prompt(self):
        for seat in SEATS:
            text, phash = node_prompt(AI_ROOT, seat)
            self.assertTrue(phash, f"{seat} has no versioned prompt to pin")
            # the prompt is a contract, not a stub: it names its role and
            # what the seat will not do (the refusal half is the contract).
            self.assertIn("## Role", text)
            self.assertIn("## You will not", text)

    def test_rail_refusal_is_for_the_rung_never_the_prompt(self):
        for seat in SEATS:
            reason = spawn.node_spawn_refusal(seat)
            if reason is None:
                # bdo granted the rung (#89): the branded spawn passes —
                # the stronger truth, nothing left to pin here.
                continue
            self.assertIn("rung", reason,
                          f"{seat}: refusal should be the ladder's, got: {reason}")
            self.assertNotIn("no versioned prompt", reason)


if __name__ == "__main__":
    unittest.main()
