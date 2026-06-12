"""Tests for actor admission against the done-line 0049 root-cause fix.

Done-line 0049 widened the shame beat to flag *actors* — nodes that write to
the record but no node_real admission ever named (the merge-node lander wrote
20+ landings under a self-asserted identity). But the move it pointed at —
`loop.node admit-real --stage <actor> --node <id>` — was refused by the pen,
which accepted only the five PIPELINE stages. A flag that points at a pen that
rejects its own suggested move is a dead end. This pins the fix: admit-real
accepts an actor that is on the record, clearing its effective-mock flag, while
still refusing a string never seen on the record (a typo).
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, gaps


def make_root_with_actor(tmp, actor):
    """A throwaway root whose only record is one receipt written by `actor` —
    so the gaps fold sees an actor on the record with no admission naming it."""
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "log" / "receipts.jsonl").write_text(
        json.dumps({"id": "rcp.test01", "node": actor, "verdict": "landed",
                    "artifact_id": "atom.x.v0"}) + "\n", encoding="utf-8")
    return root


def admissions(root):
    path = root / "log" / "admissions.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def run(root, *argv):
    # admit-real is a subcommand with its own --root, so the verb comes first
    with contextlib.redirect_stdout(io.StringIO()) as out:
        rc = node.main(["admit-real", "--root", str(root), *argv])
    return rc, out.getvalue()


class ActorAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.actor = "merge-node.claude.v0"
        self.root = make_root_with_actor(self.tmp, self.actor)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_actor_is_flagged_before_admission(self):
        flagged = {m["actor"] for m in gaps.effective_mocks(self.root)}
        self.assertIn(self.actor, flagged)  # the gap the fold surfaces

    def test_admit_real_accepts_an_actor_on_the_record(self):
        rc, text = run(self.root, "--stage", self.actor,
                       "--node", "merge-node.claude.v1", "--by", "test-bdo")
        self.assertEqual(rc, 0)
        adms = [a for a in admissions(self.root) if a.get("type") == "node_real"]
        self.assertEqual(len(adms), 1)
        self.assertEqual(adms[0]["stage_node"], self.actor)
        self.assertEqual(adms[0]["real_node"], "merge-node.claude.v1")

    def test_admission_clears_the_flag_both_sides(self):
        run(self.root, "--stage", self.actor,
            "--node", "merge-node.claude.v1", "--by", "test-bdo")
        flagged = {m["actor"] for m in gaps.effective_mocks(self.root)}
        self.assertNotIn(self.actor, flagged)               # old id superseded
        self.assertNotIn("merge-node.claude.v1", flagged)   # new id reads real

    def test_a_string_never_on_the_record_is_still_refused(self):
        # the §10 teeth: the seam opened for real actors must still refuse a
        # typo — a node that has never written to the record.
        rc, text = run(self.root, "--stage", "never-seen.typo.v0",
                       "--node", "x.v1", "--by", "test-bdo")
        self.assertEqual(rc, 2)
        self.assertIn("neither a PIPELINE stage nor an actor", text)
        self.assertEqual(
            [a for a in admissions(self.root) if a.get("type") == "node_real"], [])

    def test_pipeline_stage_still_admits_as_before(self):
        # the fix must not break the original path: a real PIPELINE stage id
        # still admits even with no record of it in this throwaway root.
        rc, _ = run(self.root, "--stage", "placement-gate.mock.v0",
                    "--node", "placement-gate.det.v1", "--by", "test-bdo")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
