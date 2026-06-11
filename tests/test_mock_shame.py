"""Tests for the mock-shame beat (done-line 0033): the UserPromptSubmit
hook that screams the still-mock pipeline stages into context and grows
louder the longer they sit.

The §10 case is the point: two logs that are each locally fine — one with
a `node_real` admission for a stage, one without — must produce different
rosters, and the admitted-real stage must DROP OUT of the scream. A beat
that names the same five stages forever (or names none) is doing nothing.
And the tally must refuse to fit a shrunk set: the turn the mock count
falls, the shame resets to zero — a stage going real is the only thing
that buys silence.

We drive the real hook through subprocess (its true entry: stdin in,
prose on stdout, exit 0) with CLAUDE_PROJECT_DIR pointed at a temp repo
whose log we craft, so the fold is exercised exactly as it runs live."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".claude" / "hooks" / "mock_shame.py"

ALL_MOCKS = ["value-gate.mock.v0", "owner-stamp.mock-bdo.v0",
             "placement-gate.mock.v0", "handoff-gate.mock.v0",
             "value-confirm.mock.v0"]


def make_repo(tmp, admissions=None, garbage=False):
    """A temp project whose .ai-native/log decides the still-mock set.
    `admissions` is a list of node_real records; `garbage` writes a torn
    log to prove the beat folds it away rather than dying on it."""
    log = Path(tmp) / ".ai-native" / "log"
    log.mkdir(parents=True)
    (log / "events.jsonl").write_text("", encoding="utf-8")
    (log / "receipts.jsonl").write_text("", encoding="utf-8")
    body = ""
    for adm in admissions or []:
        body += json.dumps(adm) + "\n"
    if garbage:
        body += '{"type": "node_real", "stage_node": "value-gate.mo\n'  # torn line
    (log / "admissions.jsonl").write_text(body, encoding="utf-8")
    return Path(tmp)


def node_real(stage, real):
    # the fold dedups admissions by id, so each needs a distinct one
    return {"id": "adm." + stage, "type": "node_real",
            "stage_node": stage, "real_node": real, "by": "bdo"}


def run(root, seed_state=None):
    """Fire the hook once. `seed_state` pre-writes the tally file to place
    us at a chosen turn count without N real invocations."""
    if seed_state is not None:
        (root / ".ai-native" / "mock-shame.json").write_text(
            json.dumps(seed_state), encoding="utf-8")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input="{}",
        capture_output=True, text=True, env=env)
    state = {}
    sp = root / ".ai-native" / "mock-shame.json"
    if sp.exists():
        state = json.loads(sp.read_text(encoding="utf-8"))
    return proc.returncode, proc.stdout, state


class MockShame(unittest.TestCase):
    def test_names_every_live_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(make_repo(tmp))
            self.assertEqual(code, 0)
            for node in ALL_MOCKS:
                self.assertIn(node, out)

    def test_admitted_real_drops_from_the_scream(self):
        # the §10 refusal: a node_real admission for two stages must remove
        # exactly those two from the roster — the other three still scream.
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, admissions=[
                node_real("value-gate.mock.v0", "value-gate.claude.v1"),
                node_real("owner-stamp.mock-bdo.v0", "owner-stamp.bdo.v1")])
            code, out, _ = run(root)
            self.assertEqual(code, 0)
            self.assertNotIn("value-gate.mock.v0", out)
            self.assertNotIn("owner-stamp.mock-bdo.v0", out)
            for node in ("placement-gate.mock.v0", "handoff-gate.mock.v0",
                         "value-confirm.mock.v0"):
                self.assertIn(node, out)

    def test_tally_rises_while_the_same_set_sits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            _, out1, s1 = run(root)
            self.assertEqual(s1["turns"], 1)
            self.assertIn("turn 1", out1)
            _, out2, s2 = run(root)
            self.assertEqual(s2["turns"], 2)
            self.assertIn("turn 2", out2)

    def test_tally_resets_the_turn_a_stage_goes_real(self):
        # sit on all mocks for a while, then make one real: the set shrinks,
        # the shame resets to zero, and that stage leaves the roster.
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            run(root); run(root); run(root)  # turns -> 3
            # now the log says value-gate is real
            (root / ".ai-native" / "log" / "admissions.jsonl").write_text(
                json.dumps(node_real("value-gate.mock.v0", "value-gate.claude.v1"))
                + "\n", encoding="utf-8")
            code, out, state = run(root)
            self.assertEqual(code, 0)
            self.assertEqual(state["turns"], 0)
            self.assertNotIn("value-gate.mock.v0", out)

    def test_silent_when_nothing_is_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, admissions=[
                node_real(m, m.replace("mock", "real")) for m in ALL_MOCKS])
            code, out, state = run(root)
            self.assertEqual(code, 0)
            self.assertEqual(out.strip(), "")
            self.assertEqual(state.get("turns"), 0)

    def test_grows_louder_over_time(self):
        # low tally is firm and lowercase; a high tally is an all-caps scream.
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            _, low, _ = run(root)
            self.assertIn("[mock-shame] turn 1", low)
            self.assertNotIn("[MOCK-SHAME]", low)
            _, loud, st = run(root, seed_state={"turns": 14, "mock_set": ALL_MOCKS})
            self.assertEqual(st["turns"], 15)
            self.assertIn("[MOCK-SHAME]", loud)
            self.assertIn("15 TURNS", loud)

    def test_fails_open_on_a_torn_log(self):
        # a half-written admission line must be folded away, not crash the
        # beat — the property a hard kill mid-append depends on.
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(make_repo(tmp, garbage=True))
            self.assertEqual(code, 0)
            # torn line dropped -> no real node -> still all mock, still screams
            self.assertIn("value-gate.mock.v0", out)


if __name__ == "__main__":
    unittest.main()
