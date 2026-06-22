"""§10 for the trespass shame beat (tooth #3).

The teeth: a DENIED attempt is still an attempt (bdo: "it's shamed if it's
attempted"). The beat must scream when a session has a NEW trespass denial on
the watch log, stay silent when it has none, and — the discriminating part —
stay silent on replay when nothing new happened (the high-water mark), then
scream again the moment a fresh attempt lands. And the write-fence must
actually WITNESS its denials, else there is nothing to shame.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
SHAME = REPO / ".claude" / "hooks" / "trespass_shame.py"
WGUARD = REPO / ".claude" / "hooks" / "workstation_guard.py"

sys.path.insert(0, str(REPO / ".claude" / "hooks"))
import trespass_shame as ts  # noqa: E402


def _denial(session, rule):
    return json.dumps({"status": "denied", "rule": rule, "session": session})


class TrespassCount(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="trespass-count-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.log = pathlib.Path(self.tmp) / "tool-use.jsonl"

    def test_counts_only_this_sessions_trespass_denials(self):
        self.log.write_text("\n".join([
            _denial("S1", "viewport-flip"),
            _denial("S1", "foreign-worktree"),
            _denial("S2", "viewport-flip"),          # other session
            json.dumps({"status": "denied", "rule": "git-push-trunk", "session": "S1"}),  # not a trespass
            json.dumps({"status": "watched", "rule": "viewport-flip", "session": "S1"}),  # not a denial
            "broken{json",                            # torn line never happened
        ]) + "\n", encoding="utf-8")
        self.assertEqual(ts.trespass_count(self.log, "S1"), 2)
        self.assertEqual(ts.trespass_count(self.log, "S2"), 1)
        self.assertEqual(ts.trespass_count(self.log, "S3"), 0)

    def test_missing_log_is_zero(self):
        self.assertEqual(ts.trespass_count(self.log, "S1"), 0)


def run_beat(session, repo_root, watch_log):
    payload = json.dumps({"session_id": session})
    env = dict(os.environ, ONTUM_REPO_ROOT=str(repo_root),
               ONTUM_TOOL_WATCH_LOG=str(watch_log))
    proc = subprocess.run([sys.executable, str(SHAME)], input=payload,
                          text=True, capture_output=True, env=env)
    return proc.stdout


class ShameBeat(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="trespass-beat-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        (self.tmp / ".ai-native" / "log").mkdir(parents=True)
        self.log = self.tmp / ".ai-native" / "log" / "tool-use.jsonl"

    def _append(self, *lines):
        with open(self.log, "a", encoding="utf-8") as fh:
            for ln in lines:
                fh.write(ln + "\n")

    def test_silent_when_no_trespass(self):
        self.log.write_text("", encoding="utf-8")
        self.assertEqual(run_beat("S1", self.tmp, self.log).strip(), "")

    def test_shames_a_new_attempt(self):
        self._append(_denial("S1", "viewport-flip"))
        out = run_beat("S1", self.tmp, self.log)
        self.assertIn("trespass-shame", out)
        self.assertIn("worktree", out)

    def test_silent_on_replay_then_loud_again_on_a_fresh_attempt(self):
        self._append(_denial("S1", "foreign-worktree"))
        first = run_beat("S1", self.tmp, self.log)
        self.assertIn("trespass-shame", first)        # new → shamed
        replay = run_beat("S1", self.tmp, self.log)
        self.assertEqual(replay.strip(), "")          # nothing new → quiet
        self._append(_denial("S1", "viewport-flip"))  # they try again
        again = run_beat("S1", self.tmp, self.log)
        self.assertIn("trespass-shame", again)        # fresh attempt → loud again

    def test_louder_with_more_attempts(self):
        self._append(*[_denial("S1", "viewport-flip") for _ in range(8)])
        out = run_beat("S1", self.tmp, self.log)
        self.assertIn("TRESPASS-SHAME", out)          # the shout tier


class WriteFenceWitnesses(unittest.TestCase):
    """The prerequisite: a denied foreign write is RECORDED, else the shame
    beat has nothing to fold."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="wfence-witness-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.primary = self.tmp / "primary"
        self.primary.mkdir()
        _git(self.primary, "init", "-q")
        _git(self.primary, "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--allow-empty", "-q", "-m", "init")
        self.wt = self.tmp / "wt"
        _git(self.primary, "worktree", "add", "-q", "-b", "b", str(self.wt))
        self.log = self.tmp / "tool-use.jsonl"

    def test_foreign_write_denial_is_recorded(self):
        payload = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": str(self.wt / "x.py"), "content": "x"},
            "session_id": "SX",
            "cwd": str(self.primary),  # standing in the viewport, writing the wt
        })
        env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(self.log))
        proc = subprocess.run([sys.executable, str(WGUARD)], input=payload,
                              text=True, capture_output=True, cwd=str(REPO), env=env)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertTrue(self.log.exists())
        lines = [json.loads(l) for l in self.log.read_text(encoding="utf-8").splitlines() if l.strip()]
        hits = [e for e in lines if e.get("status") == "denied"
                and e.get("rule") == "foreign-worktree" and e.get("session") == "SX"]
        self.assertEqual(len(hits), 1, lines)


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), check=True,
                   capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
