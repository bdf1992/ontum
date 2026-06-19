"""The training fold proposes only what the evidence supports (done-line 0097).

The §10 bar is two training sessions and a negative control. Session A's sensor
trace carries would-deny readings {git-add ×2, git-commit ×1}; the fold's
proposal names a stricter mode guarding exactly git-add and git-commit, with the
counts. Session B's trace carries only watched (would-deny-free) readings; the
fold proposes NOTHING — it refuses to invent a mode from no evidence. If the
empty session ever yields a proposal, the fold is fabricating and the bar fails.

The fold is read-only: it reads the truth log (for the opener admission) and the
sensor trace (for the readings) and writes nothing — asserted by byte-comparing
every log before and after.
"""

import json
import pathlib
import tempfile
import unittest

from loop import train

# the opening security_mode admission ids — the train_session stamped on each
# reading. Concrete here so the test reads exactly what the guard would write.
A = "adm.trainA"
B = "adm.trainB"


def _security_mode(adm_id, session, enabled=True):
    return {"id": adm_id, "type": "security_mode", "mode": "train",
            "session": session, "enabled": enabled, "by": "bdo",
            "ts": "2026-06-16T00:00:00+00:00"}


def _would_deny(train_session, rule, surface, intent):
    return {"status": "would-deny", "rule": rule, "mode": "train",
            "train_session": train_session, "surface": surface,
            "intent": intent, "command": f"{surface} ...",
            "session": "sess-" + train_session, "ts": "2026-06-16T00:01:00+00:00"}


def _watched(train_session, bins, intent):
    return {"status": "watched", "bins": bins, "intent": intent,
            "mode": "train", "train_session": train_session,
            "command": f"{bins[0]} ...", "session": "sess-" + train_session,
            "ts": "2026-06-16T00:02:00+00:00"}


def _write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


class TrainFoldTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / ".ai-native"
        log = self.root / "log"
        # two opened training sessions on the truth log
        _write_jsonl(log / "admissions.jsonl",
                     [_security_mode(A, "sess-adm.trainA"),
                      _security_mode(B, "sess-adm.trainB")])
        _write_jsonl(log / "events.jsonl", [])
        _write_jsonl(log / "receipts.jsonl", [])
        # Session A: would-deny {git-add ×2, git-commit ×1} + one ordinary read
        # Session B (negative control): only watched, zero would-deny
        _write_jsonl(log / "tool-use.jsonl", [
            _would_deny(A, "git-add", "git", "mutate"),
            _would_deny(A, "git-add", "git", "mutate"),
            _would_deny(A, "git-commit", "git", "mutate"),
            _watched(A, ["git"], "read"),
            _watched(B, ["gh"], "read"),
            _watched(B, ["ls"], "read"),
        ])
        self.log = log

    def tearDown(self):
        self.tmp.cleanup()

    def _snapshot(self):
        return {p.name: p.read_bytes() for p in self.log.iterdir() if p.is_file()}

    def test_session_A_proposes_the_would_block_set(self):
        d = train.fold_session(self.root, A)
        p = d["proposal"]
        self.assertTrue(p["proposed"], "A has would-deny evidence; must propose")
        guards = {g["rule"]: g["evidence_count"] for g in p["guards"]}
        self.assertEqual(guards, {"git-add": 2, "git-commit": 1},
                         "the proposal must name exactly the would-block set + counts")
        self.assertEqual(d["would_block_set"], {"git-add": 2, "git-commit": 1})
        self.assertEqual(p["admits_only"], "bdo", "the cut stays bdo's (D-4)")

    def test_session_B_negative_control_proposes_nothing(self):
        d = train.fold_session(self.root, B)
        p = d["proposal"]
        # the teeth: no would-deny readings => no proposal. If this ever flips,
        # the fold is inventing a mode from no evidence.
        self.assertFalse(p["proposed"],
                         "B has zero would-deny readings; the fold must NOT propose")
        self.assertEqual(p["guards"], [])
        self.assertEqual(d["would_block_set"], {})
        self.assertEqual(d["would_deny_count"], 0)

    def test_profile_counts_intent_and_surface(self):
        d = train.fold_session(self.root, A)
        prof = d["profile"]
        self.assertEqual(prof["by_intent"].get("mutate"), 3)
        self.assertEqual(prof["by_intent"].get("read"), 1)
        self.assertEqual(prof["by_surface"].get("git"), 4)

    def test_overview_lists_sessions_with_op_counts(self):
        d = train.overview(self.root)
        by_id = {s["id"]: s for s in d["sessions"]}
        self.assertEqual(by_id[A]["op_count"], 4)
        self.assertEqual(by_id[A]["would_deny_count"], 3)
        self.assertEqual(by_id[B]["op_count"], 2)
        self.assertEqual(by_id[B]["would_deny_count"], 0)

    def test_fold_writes_nothing(self):
        before = self._snapshot()
        train.overview(self.root)
        train.fold_session(self.root, A)
        train.fold_session(self.root, B)
        train.main(["--root", str(self.root)])
        train.main(["--root", str(self.root), "--session", A])
        train.main(["--root", str(self.root), "--session", B, "--json"])
        after = self._snapshot()
        self.assertEqual(before, after, "the fold is read-only; no log byte moved")


if __name__ == "__main__":
    unittest.main()
