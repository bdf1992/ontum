"""The issue pen records its acts and the fence forbids the raw door (#412).

Pins the issue-pen work: a governed GitHub issue mutation goes through the
pen, which records the act on the log with provenance, and raw `gh issue`
mutations are denied by the live command_guard (closing the prompt-parity
hole) while reads stay raw-and-watched.

Two kinds of teeth, both proven non-vacuous:

1. The pen records a well-formed issue.closed / issue.commented event, and
   REFUSES an empty reason / missing --by before any gh call (no record, no
   reach). A pen that recorded regardless, or skipped the refusal, fails.
2. The live command_guard DENIES `gh issue close 5` (exit 2) and does NOT
   deny `gh issue view 5` / `gh issue list` (exit 0). A vacuous guard that
   denied everything would fail the read assertions; one that denied nothing
   (the prompt-parity hole) would fail the close assertion.
"""

import json
import os
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "issue"))

import issue  # noqa: E402


class FakeGh:
    """A stand-in for the gh CLI: records argv, returns a chosen exit code,
    never touches the network."""

    def __init__(self, returncode=0, stderr=""):
        self.calls = []
        self.returncode = returncode
        self.stderr = stderr

    def __call__(self, args):
        self.calls.append(list(args))

        class _Proc:
            pass

        p = _Proc()
        p.returncode = self.returncode
        p.stdout = ""
        p.stderr = self.stderr
        return p


class IssuePenRecords(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.events = pathlib.Path(self.tmp.name) / "events.jsonl"
        self.addCleanup(self.tmp.cleanup)

    def _events(self):
        if not self.events.exists():
            return []
        return [json.loads(l) for l in
                self.events.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_close_appends_wellformed_event(self):
        fake = FakeGh()
        rec = issue.do_close(5, "the work landed elsewhere", "claude",
                             gh_run=fake, events_path=self.events)
        # the gh reach: close + the reason as a closing comment
        self.assertEqual(fake.calls[0][:3], ["issue", "close", "5"])
        self.assertIn("--comment", fake.calls[0])
        self.assertIn("the work landed elsewhere", fake.calls[0])
        # the provenance record, on the log, well-formed
        events = self._events()
        self.assertEqual(len(events), 1)
        obj = events[-1]
        self.assertEqual(obj["type"], "issue.closed")
        self.assertEqual(obj["number"], 5)
        self.assertEqual(obj["by"], "claude")
        self.assertEqual(obj["reason"], "the work landed elsewhere")
        self.assertEqual(obj["kind"], "issue-governance")
        self.assertTrue(obj["id"].startswith("evt."))
        self.assertTrue(obj["ts"].endswith("Z"))
        self.assertEqual(obj, rec)

    def test_comment_appends_wellformed_event(self):
        fake = FakeGh()
        issue.do_comment(7, "a note on the record", "bdo",
                         gh_run=fake, events_path=self.events)
        self.assertEqual(fake.calls[0][:3], ["issue", "comment", "7"])
        self.assertIn("--body", fake.calls[0])
        obj = self._events()[-1]
        self.assertEqual(obj["type"], "issue.commented")
        self.assertEqual(obj["number"], 7)
        self.assertEqual(obj["by"], "bdo")
        self.assertEqual(obj["body"], "a note on the record")
        self.assertEqual(obj["kind"], "issue-governance")

    def test_empty_reason_is_refused_no_reach_no_record(self):
        fake = FakeGh()
        with self.assertRaises(ValueError):
            issue.do_close(5, "   ", "claude", gh_run=fake, events_path=self.events)
        self.assertEqual(fake.calls, [])           # never reached gh
        self.assertEqual(self._events(), [])       # nothing on the log

    def test_missing_by_is_refused_no_reach_no_record(self):
        fake = FakeGh()
        with self.assertRaises(ValueError):
            issue.do_close(5, "a real reason", "", gh_run=fake, events_path=self.events)
        self.assertEqual(fake.calls, [])
        self.assertEqual(self._events(), [])

    def test_empty_body_comment_is_refused(self):
        fake = FakeGh()
        with self.assertRaises(ValueError):
            issue.do_comment(7, "", "bdo", gh_run=fake, events_path=self.events)
        self.assertEqual(fake.calls, [])
        self.assertEqual(self._events(), [])

    def test_no_record_when_gh_fails(self):
        # gh refused the close — the provenance must NOT claim it happened
        fake = FakeGh(returncode=1, stderr="could not find issue")
        with self.assertRaises(RuntimeError):
            issue.do_close(5, "a real reason", "claude",
                           gh_run=fake, events_path=self.events)
        self.assertEqual(self._events(), [])


GUARD = ROOT / ".claude" / "hooks" / "command_guard.py"


def run_guard(command, watch_log):
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test-issue-pen",
    })
    env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(watch_log))
    import subprocess
    return subprocess.run(
        [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
        capture_output=True, env=env,
    )


class FenceForbidsRawIssueMutation(unittest.TestCase):
    """The behavioral fence test: the prompt-parity hole is closed for the
    Claude surface — raw `gh issue` mutations are denied, reads pass."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.watch_log = pathlib.Path(self.tmp.name) / "watch.jsonl"
        self.addCleanup(self.tmp.cleanup)

    def test_raw_issue_close_is_denied(self):
        proc = run_guard("gh issue close 5", self.watch_log)
        self.assertEqual(
            proc.returncode, 2,
            f"command_guard let raw `gh issue close` through — the prompt-parity "
            f"hole is open ({proc.stderr.decode()})")

    def test_raw_issue_create_and_comment_are_denied(self):
        for cmd in ("gh issue create --title t --body b",
                    "gh issue comment 5 --body x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(run_guard(cmd, self.watch_log).returncode, 2)

    def test_issue_reads_are_not_denied(self):
        # reads are witnessed, not gated (the repo's asymmetry); a guard that
        # denied these would be vacuous teeth — this is what proves the test
        # is not just "deny everything".
        for cmd in ("gh issue view 5", "gh issue list", "gh issue status"):
            with self.subTest(cmd=cmd):
                self.assertEqual(
                    run_guard(cmd, self.watch_log).returncode, 0,
                    f"command_guard denied a read it should witness: {cmd!r}")


if __name__ == "__main__":
    unittest.main()
