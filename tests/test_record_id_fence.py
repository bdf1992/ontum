"""Done-line 0053: a record id minted against a stale local fold refuses to
commit — the id fold is fleet-wide, not local.

The incident is on the record: four parallel branches minted done-line 0020
with no gate in the path (the witness review that birthed
epic.experience-layer), and the directory still holds the twins. The
near-miss is tonight's: a session whose local fold said "next is 0050" while
origin/claude/the-field-reframe already held 0050-field-topology. The §10
shape both ways: the colliding mint refuses, the unchanged propagation of
the sibling's record passes — two locally-fine acts, and the fence tells
them apart by the only fact that matters (same id, same directory,
different file).
"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEN_PATH = ROOT / ".claude" / "skills" / "branch-ritual" / "git.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gitpen = _load("git_pen_fence", PEN_PATH)

FIELD = ".ai-native/done/0050-field-topology-the-first-field.md"
RUNG = ".ai-native/done/0050-rung-intake.md"


class TestRecordIdCollision(unittest.TestCase):
    def test_tonights_near_miss_refuses(self):
        # 0050-rung-intake staged while a ref holds 0050-field-topology:
        # same id, same directory, different file — the 0020 incident shape.
        reason = gitpen.record_id_collision(
            [RUNG], {"origin/claude/the-field-reframe": [FIELD]})
        self.assertIsNotNone(reason)
        self.assertIn("0050", reason)
        self.assertIn("0050-field-topology-the-first-field.md", reason)
        self.assertIn("origin/claude/the-field-reframe", reason)

    def test_propagating_the_same_file_passes(self):
        # carrying the sibling's record unchanged is how the local fold
        # learns the id is taken — propagation is the fix, not a collision.
        self.assertIsNone(gitpen.record_id_collision(
            [FIELD], {"origin/claude/the-field-reframe": [FIELD]}))

    def test_same_id_across_directories_is_no_collision(self):
        # done 0050 and report 0050 are different address spaces.
        self.assertIsNone(gitpen.record_id_collision(
            [RUNG], {"origin/x": [".ai-native/reports/0050-anything.md"]}))

    def test_non_record_paths_are_ignored(self):
        self.assertIsNone(gitpen.record_id_collision(
            ["loop/pen.py", "tests/test_pen.py"],
            {"origin/x": [FIELD]}))
        self.assertIsNone(gitpen.record_id_collision(
            [RUNG], {"origin/x": ["loop/pen.py"]}))

    def test_reports_are_fenced_too(self):
        reason = gitpen.record_id_collision(
            [".ai-native/reports/0044-mine.md"],
            {"refs/heads/other": [".ai-native/reports/0044-theirs.md"]})
        self.assertIsNotNone(reason)
        self.assertIn("reports", reason)

    def test_empty_inputs_pass(self):
        self.assertIsNone(gitpen.record_id_collision([], {}))
        self.assertIsNone(gitpen.record_id_collision(None, None))
        self.assertIsNone(gitpen.record_id_collision([RUNG], {}))

    def test_history_is_not_retro_flagged(self):
        # the twin 0020 done-lines both already exist on every ref; neither
        # is newly staged, so nothing refuses — history stands.
        twins = [".ai-native/done/0020-git-commit-pen.md",
                 ".ai-native/done/0020-reflection-automates.md"]
        self.assertIsNone(gitpen.record_id_collision(
            ["loop/pen.py"], {"origin/main": twins}))


if __name__ == "__main__":
    unittest.main()
