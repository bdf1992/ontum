"""Tests for prompts-as-code against done-line 0009:
the summons delivers the node's versioned prompt with its sha256; the
receipt records the prompt hash in force at judgment (verdicts attributable
to the exact prompt that judged); editing the prompt changes the hash on
later receipts but never reopens earlier ones (I-2); a node without a
prompt file still summons and judges — absence is information."""

import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile, summon

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
PROMPT_SRC = REPO / ".ai-native" / "nodes" / "value-gate.claude.v1.md"


def make_atom(i):
    return {"atom": {
        "id": f"atom.prompted-{i:02d}.v0",
        "story": {"text": f"As an AI, I need verdict {i} attributable to the prompt "
                          "that judged it, because wording that gates is code (§7).",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.prompts"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-owner-stamp"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, n_atoms, with_prompt=True):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    for i in range(n_atoms):
        (root / "atoms" / f"atom.prompted-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    if with_prompt:
        (root / "nodes").mkdir(parents=True)
        shutil.copy(PROMPT_SRC, root / "nodes" / f"{L0_REAL}.md")
    return root


def receipts(root):
    path = root / "log" / "receipts.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class PromptsAsCodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # seed; both park at L0

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def prompt_hash(self):
        data = (self.root / "nodes" / f"{L0_REAL}.md").read_bytes()
        return "sha256:" + hashlib.sha256(data).hexdigest()

    def judge(self, atom_id, verdict="accept", reason="test verdict"):
        return node.main(["judge", "--root", str(self.root), "--atom", atom_id,
                          "--node", L0_REAL, "--verdict", verdict, "--reason", reason])

    def test_summons_delivers_the_prompt_with_its_hash(self):
        summons = summon.open_summons(self.root)
        self.assertEqual(len(summons), 2)
        for s in summons:
            self.assertIn("the L0 value gate", s["prompt_text"])
            self.assertEqual(s["prompt_hash"], self.prompt_hash())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            summon.main(["--root", str(self.root)])
        text = out.getvalue()
        self.assertIn(f"prompt-version: {self.prompt_hash()}", text)
        self.assertIn("your operating prompt, versioned (§7)", text)

    def test_receipt_records_the_prompt_in_force(self):
        first_hash = self.prompt_hash()
        self.assertEqual(self.judge("atom.prompted-00.v0"), 0)
        rc0 = [r for r in receipts(self.root) if r["artifact_id"] == "atom.prompted-00.v0"][0]
        self.assertEqual(rc0["prompt_hash"], first_hash)
        # the prompt sharpens; the next verdict carries the new version
        path = self.root / "nodes" / f"{L0_REAL}.md"
        path.write_bytes(path.read_bytes() + b"\n- sharpened: one more check.\n")
        self.assertEqual(self.judge("atom.prompted-01.v0"), 0)
        rc1 = [r for r in receipts(self.root) if r["artifact_id"] == "atom.prompted-01.v0"][0]
        self.assertEqual(rc1["prompt_hash"], self.prompt_hash())
        self.assertNotEqual(rc0["prompt_hash"], rc1["prompt_hash"])
        # the earlier receipt never reopens: same bytes on the log (I-2, D-5)
        rc0_again = [r for r in receipts(self.root) if r["artifact_id"] == "atom.prompted-00.v0"][0]
        self.assertEqual(rc0, rc0_again)

    def test_absent_prompt_is_information_not_error(self):
        bare = make_root(tempfile.mkdtemp(dir=self.tmp), 1, with_prompt=False)
        orchestrate.admit_setpoint(bare, SETPOINT, by="test-bdo")
        node.admit_real(bare, L0_STAGE, L0_REAL, by="test-bdo")
        orchestrate.orchestrate(bare, quiet=True)
        summons = summon.open_summons(bare)
        self.assertEqual(len(summons), 1)
        self.assertIsNone(summons[0]["prompt_text"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            summon.main(["--root", str(bare)])
        self.assertNotIn("prompt-version", out.getvalue())
        self.assertEqual(node.main(["judge", "--root", str(bare),
                                    "--atom", "atom.prompted-00.v0", "--node", L0_REAL,
                                    "--verdict", "accept", "--reason", "no prompt file, judged on summons"]), 0)
        self.assertNotIn("prompt_hash", receipts(bare)[0])

    def test_mock_receipts_carry_no_prompt_field(self):
        plain = make_root(tempfile.mkdtemp(dir=self.tmp), 1, with_prompt=True)
        orchestrate.admit_setpoint(plain, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(plain, quiet=True), 0)  # all mock
        self.assertTrue(receipts(plain))
        for rc in receipts(plain):
            self.assertNotIn("prompt_hash", rc)


if __name__ == "__main__":
    unittest.main()
