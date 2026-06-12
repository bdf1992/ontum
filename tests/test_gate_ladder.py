"""Done-line 0054: a gate launch asks the trust ladder before any mind is born.

The spawn rail gates session-level spawns at the hook layer, but gate.py
births its mind from a Python subprocess no hook ever sees — so the pen must
ask the ladder itself, or the ladder is prose at exactly the seam where real
inference runs. The §10 shape: on an empty ladder the launch refuses (and the
refusal names the gesture that fixes it, never a dead end); the admission
written through the one write path flips the same ask to permitted. No gh,
no claude subprocess — the pure refusal is hit directly, the way the gate's
verdict parser is tested.
"""

import importlib.util
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
GATE = REPO / ".claude" / "skills" / "gate" / "gate.py"

spec = importlib.util.spec_from_file_location("gate_pen_ladder", GATE)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate_pen_ladder"] = gate
spec.loader.exec_module(gate)

sys.path.insert(0, str(REPO))
from loop import node as loop_node  # noqa: E402


class LaunchAsksTheLadder(unittest.TestCase):
    def setUp(self):
        self.ai = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.ai, ignore_errors=True)
        (self.ai / "log").mkdir()

    def test_empty_ladder_refuses_and_names_the_gesture(self):
        reason = gate.launch_refusal(root=self.ai)
        self.assertIsNotNone(reason)
        self.assertIn("rung", reason)
        self.assertIn("rung-intake", reason)  # a refusal names its fix

    def test_the_admission_flips_it(self):
        adm = loop_node.admit_rung(self.ai, gate.GATE_CLASS, gate.GATE_CAP, "bdo")
        self.assertIsNotNone(adm)
        self.assertIsNone(gate.launch_refusal(root=self.ai))

    def test_a_lower_rung_does_not_cover_judging(self):
        # read < judge: a class trusted only to read still may not judge.
        loop_node.admit_rung(self.ai, gate.GATE_CLASS, "read", "bdo")
        self.assertIsNotNone(gate.launch_refusal(root=self.ai))

    def test_another_classes_rung_does_not_leak(self):
        # branded-subagent's rung (bdo's #89 gesture) must not let the
        # summoned-session class judge — rungs are per class, never pooled.
        loop_node.admit_rung(self.ai, "branded-subagent", "judge", "bdo")
        self.assertIsNotNone(gate.launch_refusal(root=self.ai))


if __name__ == "__main__":
    unittest.main()
