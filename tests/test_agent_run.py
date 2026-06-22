"""Tests for loop/agent_run.py — agent runs on the books, under a training
posture (bdo 2026-06-22 "run it on the books as a training program ... ensure it
gets monitored by some process"). The §10 teeth: the write seam must be
non-vacuous —

  * a receipt for a GHOST node (no governed prompt) is REFUSED — you cannot book
    an ungoverned run (if this passed, the books would carry runs attributable to
    nothing — the failure C6 exists to prevent);
  * a receipt whose prompt_hash does NOT match the node's governed hash is
    REFUSED — a run is attributable to the EXACT prompt that ran;
  * a receipt for a real, door-passing node with its true hash IS booked, and the
    monitor fold reads it back;
  * an empty run folds to count 0 — no false "all clear" from no evidence.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import agent_run, prompt_req
from loop.reconcile import append_line, now_ts

# a full, door-passing node prompt (mirrors test_prompt_req's FULL) — written
# into the temp root's nodes/ so deliver() resolves it without the real tree.
VALID_PROMPT = """# test-node.claude.v1 — a worked example for the books
version: 1.0.0 — §7
## Role
You do one bounded thing.
## You read
the section item.
## You return
one disposition.
## You will not
act beyond the one item (D-2).
## Evals
pinned in tests/test_agent_run.py.
"""


class TrainingRunBooks(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "log").mkdir()
        (self.root / "nodes").mkdir()
        (self.root / "nodes" / "test-node.claude.v1.md").write_text(
            VALID_PROMPT, encoding="utf-8")
        # the true governed hash of the prompt we just wrote
        self.node = "test-node.claude.v1"
        self.hash = prompt_req.deliver(self.root, self.node)["prompt_hash"]
        self.assertTrue(self.hash.startswith("sha256:"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_open_then_book_then_monitor_reads_it_back(self):
        run = agent_run.open_run(self.root, by="test-bdo", note="first light")
        self.assertTrue(run.startswith("atr."))
        rid = agent_run.book_receipt(
            self.root, run, self.node, self.hash,
            subject="atom.x", verdict="already-reconciled",
            reason="cited inbox + digest, nothing open")
        self.assertTrue(rid.startswith("arun."))
        d = agent_run.fold_run(self.root, run)
        self.assertEqual(d["count"], 1)                       # on the books
        self.assertEqual(d["by_verdict"], {"already-reconciled": 1})
        self.assertEqual(d["receipts"][0]["subject"], "atom.x")
        self.assertTrue(d["opener"])                          # posture visible
        self.assertFalse(d["opener"]["closed"])

    def test_ghost_node_is_refused(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        with self.assertRaises(ValueError) as cm:
            agent_run.book_receipt(self.root, run, "no-such-node.v9",
                                   "sha256:deadbeef", "atom.x", "v", "r")
        self.assertIn("ghost", str(cm.exception).lower())
        # and nothing was booked — the refusal is total
        self.assertEqual(agent_run.fold_run(self.root, run)["count"], 0)

    def test_prompt_hash_mismatch_is_refused(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        with self.assertRaises(ValueError) as cm:
            agent_run.book_receipt(self.root, run, self.node,
                                   "sha256:notthehash", "atom.x", "v", "r")
        self.assertIn("mismatch", str(cm.exception).lower())
        self.assertEqual(agent_run.fold_run(self.root, run)["count"], 0)

    def test_empty_run_is_an_empty_read_not_a_false_all_clear(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        d = agent_run.fold_run(self.root, run)
        self.assertEqual(d["count"], 0)
        self.assertEqual(d["by_verdict"], {})

    def test_close_supersedes_the_posture(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        agent_run.close_run(self.root, run, by="test-bdo")
        d = agent_run.fold_run(self.root, run)
        self.assertTrue(d["opener"]["closed"])               # closed, not erased

    def test_rebook_same_verdict_is_idempotent(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        a = agent_run.book_receipt(self.root, run, self.node, self.hash,
                                   "atom.x", "already-reconciled", "r1")
        b = agent_run.book_receipt(self.root, run, self.node, self.hash,
                                   "atom.x", "already-reconciled", "r2")
        self.assertEqual(a, b)                                # same (run,node,subject,verdict)
        self.assertEqual(agent_run.fold_run(self.root, run)["count"], 1)

    # --- hardening (redteam follow-up) ---

    def test_book_under_unopened_run_is_refused(self):
        # the run posture must exist — a receipt under a never-opened id is ungoverned
        with self.assertRaises(ValueError) as cm:
            agent_run.book_receipt(self.root, "atr.never-opened", self.node,
                                   self.hash, "atom.x", "already-reconciled", "r")
        self.assertIn("no such training run", str(cm.exception).lower())

    def test_book_under_closed_run_is_refused(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        agent_run.close_run(self.root, run, by="test-bdo")
        with self.assertRaises(ValueError) as cm:
            agent_run.book_receipt(self.root, run, self.node, self.hash,
                                   "atom.x", "already-reconciled", "r")
        self.assertIn("closed", str(cm.exception).lower())

    def test_bad_subject_is_refused(self):
        # a subject carrying shell metacharacters can never reach the books
        run = agent_run.open_run(self.root, by="test-bdo")
        for bad in ('x";rm -rf ~;echo "', "$(id)", "a b", "back`tick`"):
            with self.subTest(subject=bad):
                with self.assertRaises(ValueError) as cm:
                    agent_run.book_receipt(self.root, run, self.node, self.hash,
                                           bad, "already-reconciled", "r")
                self.assertIn("not a valid id", str(cm.exception).lower())
        self.assertEqual(agent_run.fold_run(self.root, run)["count"], 0)

    def test_divergent_verdict_rebook_is_visible_not_masked(self):
        # the escalation-erasure attack: a later already-reconciled must NOT hide
        # an earlier needs-owner — both render (verdict is in the id)
        run = agent_run.open_run(self.root, by="test-bdo")
        agent_run.book_receipt(self.root, run, self.node, self.hash,
                               "atom.x", "needs-owner", "touches the truth log")
        agent_run.book_receipt(self.root, run, self.node, self.hash,
                               "atom.x", "already-reconciled", "nothing to do")
        d = agent_run.fold_run(self.root, run)
        self.assertEqual(d["count"], 2)                       # both on the books
        self.assertEqual(d["by_verdict"], {"already-reconciled": 1, "needs-owner": 1})

    def test_overview_count_agrees_with_fold_run(self):
        run = agent_run.open_run(self.root, by="test-bdo")
        agent_run.book_receipt(self.root, run, self.node, self.hash,
                               "atom.x", "already-reconciled", "r1")
        agent_run.book_receipt(self.root, run, self.node, self.hash,
                               "atom.x", "already-reconciled", "r2")  # true dup
        ov = agent_run.overview(self.root)
        fold = agent_run.fold_run(self.root, run)
        ov_count = next(r["count"] for r in ov["runs"] if r["id"] == run)
        self.assertEqual(ov_count, fold["count"])             # one truth, not two
        self.assertEqual(ov_count, 1)
        self.assertEqual(ov.get("orphans"), [])

    def test_orphan_receipt_is_surfaced_not_hidden(self):
        # a receipt that reached the log under no opener (e.g. a raw append that
        # bypassed book_receipt) must SCREAM in overview, never vanish
        append_line(agent_run._receipts_path(self.root), {
            "id": "arun.orphan", "type": agent_run.RECEIPT_TYPE,
            "run": "atr.no-opener", "node": self.node, "prompt_hash": self.hash,
            "subject": "atom.x", "verdict": "already-reconciled", "reason": "r",
            "training": True, "ts": now_ts(),
        })
        ov = agent_run.overview(self.root)
        orphan_ids = {o["id"] for o in ov.get("orphans", [])}
        self.assertIn("atr.no-opener", orphan_ids)            # not hidden


if __name__ == "__main__":
    unittest.main()
