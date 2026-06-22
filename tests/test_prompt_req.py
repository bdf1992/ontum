"""Tests for loop/prompt_req.py — the prompt-requirements door (C3; bdo
2026-06-22 "wire it"). The §10 teeth: the door must be non-vacuous —

  * an edgeless blob is REFUSED, and every missing edge is named (if this
    failed, an ungoverned prompt would ship as if it met the contract);
  * a prompt declaring all edges + version + title PASSES (not over-strict);
  * the REAL node prompts on disk all pass (the door checks the contract, not
    a spelling only one author used);
  * `deliver` halts an invalid/absent prompt (valid=False) and pins a hash to a
    valid one — the bridge that keeps a workflow agent on prompt-as-code."""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import prompt_req

FULL = """# tend-x.claude.v1 — a worked example
version: 1.0.0 — §7
## Role
You do one bounded thing.
## You read
the section item.
## You return
one disposition through the pen.
## You will not
act beyond the one item (D-2).
## Evals
pinned in tests/test_x.py.
"""

EDGELESS = "# just a title\n\nsome prose with no edges and no version.\n"


class DoorTeeth(unittest.TestCase):
    def test_full_prompt_passes(self):
        self.assertEqual(prompt_req.validate(FULL), [])

    def test_edgeless_prompt_is_refused_with_every_gap_named(self):
        problems = prompt_req.validate(EDGELESS)
        self.assertTrue(problems)                     # refused, not waved through
        joined = " ".join(problems).lower()
        for edge in ("role", "reads", "returns", "won", "evals"):
            self.assertIn(edge, joined, f"the {edge} gap must be named")
        self.assertIn("version", joined)

    def test_missing_a_single_edge_is_caught(self):
        # drop only the "won't" edge — the door must still refuse (the D-2 teeth)
        no_wont = FULL.replace("## You will not\nact beyond the one item (D-2).\n", "")
        problems = prompt_req.validate(no_wont)
        self.assertTrue(any("wont" in p for p in problems))

    def test_real_node_prompts_all_pass(self):
        root = REPO / ".ai-native"
        nodes = sorted(p.stem for p in (root / "nodes").glob("*.md"))
        self.assertTrue(nodes)                        # there are real prompts to check
        for n in nodes:
            text = prompt_req.reconcile.node_prompt(root, n)[0]
            self.assertEqual(prompt_req.validate(text), [], f"{n} should pass the door")


class DeliverBridge(unittest.TestCase):
    def test_deliver_absent_is_not_found_and_invalid(self):
        d = prompt_req.deliver(REPO / ".ai-native", "no-such-node.v9")
        self.assertFalse(d["found"])
        self.assertFalse(d["valid"])                  # halts the summon

    def test_deliver_valid_node_pins_a_hash(self):
        d = prompt_req.deliver(REPO / ".ai-native", "value-gate.claude.v1")
        self.assertTrue(d["found"])
        self.assertTrue(d["valid"])
        self.assertTrue(d["prompt_hash"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
