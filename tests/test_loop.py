"""Tests for the phase-1 loop skeleton against the done-line:
goal reached over passes; SIGKILL mid-run loses nothing and doubles nothing;
cache deleted + replayed from log/ is byte-identical; torn tails tolerated."""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import reconcile


def make_root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    shutil.copy(REPO / ".ai-native" / "atoms" / "atom.loop-skeleton.v0.json",
                root / "atoms" / "atom.loop-skeleton.v0.json")
    return root


def cache_bytes(root):
    out = {}
    for sub in ("queues", "offsets"):
        for p in sorted((root / sub).rglob("*")):
            if p.is_file():
                out[str(p.relative_to(root))] = p.read_bytes()
    return out


def receipt_keys(root):
    keys = []
    for line in (root / "log" / "receipts.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        try:
            rc = json.loads(line)
        except ValueError:
            continue  # torn line: didn't happen
        keys.append((rc["node"], rc["artifact_hash"]))
    return keys


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def drive(self):
        return reconcile.until_done(self.root)

    def test_atom_reaches_goal_over_multiple_passes(self):
        results = []
        for _ in range(50):
            result, state, step = reconcile.pass_once(self.root, quiet=True)
            results.append((result, state, step))
            if result == "done":
                break
        self.assertEqual(results[-1][0], "done")
        self.assertEqual(results[-1][1], "value_confirmed")
        # multiple passes, each moving one step
        self.assertGreater(len([r for r in results if r[2]]), 5)
        # exactly one receipt per (node, artifact_hash) — I-2
        keys = receipt_keys(self.root)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), len(reconcile.PIPELINE))

    def test_rerun_after_done_does_not_double_act(self):
        self.assertEqual(self.drive(), 0)
        before_e = (self.root / "log" / "events.jsonl").read_bytes()
        before_r = (self.root / "log" / "receipts.jsonl").read_bytes()
        for _ in range(3):
            result, _, step = reconcile.pass_once(self.root, quiet=True)
            self.assertEqual(result, "done")
            self.assertIsNone(step)
        self.assertEqual(before_e, (self.root / "log" / "events.jsonl").read_bytes())
        self.assertEqual(before_r, (self.root / "log" / "receipts.jsonl").read_bytes())

    def test_kill_midway_loses_nothing_doubles_nothing(self):
        env = dict(os.environ, PYTHONPATH=str(REPO))
        proc = subprocess.Popen(
            [sys.executable, "-m", "loop.reconcile", "--root", str(self.root),
             "--until-done", "--pace", "0.05"],
            cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        proc.send_signal(signal.SIGKILL)
        proc.wait()
        mid_receipts = len(receipt_keys(self.root))
        self.assertLess(mid_receipts, len(reconcile.PIPELINE), "kill landed too late to prove anything")
        # next run picks it up from the files
        self.assertEqual(self.drive(), 0)
        _, ahash = reconcile.load_atom(self.root)
        fold = reconcile.Fold(self.root)
        self.assertEqual(reconcile.atom_state(fold, ahash), "value_confirmed")
        keys = receipt_keys(self.root)
        self.assertEqual(len(keys), len(set(keys)), "doubled receipts after recovery")
        self.assertEqual(len(keys), len(reconcile.PIPELINE), "lost receipts after recovery")

    def test_torn_tail_is_dropped_and_rederived(self):
        for _ in range(4):
            reconcile.pass_once(self.root, quiet=True)
        rpath = self.root / "log" / "receipts.jsonl"
        whole = rpath.read_text().splitlines(keepends=True)
        self.assertTrue(whole, "need at least one receipt to tear")
        torn = whole[-1][: len(whole[-1]) // 2]  # half a line, no newline
        rpath.write_text("".join(whole[:-1]) + torn)
        before = len(receipt_keys(self.root))
        self.assertEqual(self.drive(), 0)
        keys = receipt_keys(self.root)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), len(reconcile.PIPELINE))
        self.assertGreaterEqual(len(keys), before, "a fully-written receipt was lost")

    def test_cache_is_a_fold_delete_and_replay_identical(self):
        self.assertEqual(self.drive(), 0)
        before = cache_bytes(self.root)
        self.assertTrue(before, "cache should exist after a run")
        shutil.rmtree(self.root / "queues")
        shutil.rmtree(self.root / "offsets")
        _, ahash = reconcile.load_atom(self.root)
        reconcile.rebuild_cache(self.root, reconcile.Fold(self.root), ahash)
        self.assertEqual(before, cache_bytes(self.root))

    def test_queue_membership_is_never_authoritative(self):
        # poison the cache: claim a pending event that the log refutes
        self.assertEqual(self.drive(), 0)
        qfile = self.root / "queues" / "author-to-value.pending.jsonl"
        qfile.write_text('{"id":"evt.fake","type":"atom.created"}\n')
        result, state, step = reconcile.pass_once(self.root, quiet=True)
        self.assertEqual(result, "done")
        self.assertIsNone(step, "a pass acted on cache instead of the log")
        # and the pass rebuilt the poisoned cache from the fold
        self.assertEqual(qfile.read_text(), "")


if __name__ == "__main__":
    unittest.main()
