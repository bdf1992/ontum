"""§10 test for the issue pen's `open` verb — the opener that lets a session
put an owner decision on GitHub without a CLI-at-owner fallback or a raw `gh`
bypass. Non-vacuous: the refusals must fire BEFORE any gh call, and the
provenance record must land ONLY after a successful create (a refused gh write
is never recorded as if it happened). gh is injected, so no network is touched.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "issue_pen", REPO / ".claude" / "skills" / "issue" / "issue.py")
issue = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(issue)


class _FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class IssueOpenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = self.tmp / "events.jsonl"
        self.calls = []

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gh(self, ret=0, out="https://github.com/o/r/issues/777"):
        def run(args):
            self.calls.append(args)
            return _FakeProc(ret, out)
        return run

    def _records(self):
        if not self.log.exists():
            return []
        return [json.loads(ln) for ln in self.log.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def test_open_records_after_create(self):
        rec = issue.do_open("Audit request", "the body", "claude",
                            gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls[0][:2], ["issue", "create"])
        self.assertEqual(rec["type"], "issue.opened")
        self.assertEqual(rec["number"], "777")        # parsed from the URL
        self.assertEqual(rec["title"], "Audit request")
        self.assertEqual(rec["by"], "claude")
        self.assertEqual(len(self._records()), 1)     # exactly one provenance line

    def test_refuses_empty_title_before_any_gh(self):
        with self.assertRaises(ValueError):
            issue.do_open("   ", "body", "claude", gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls, [])              # no gh call
        self.assertEqual(self._records(), [])         # nothing recorded

    def test_refuses_empty_body(self):
        with self.assertRaises(ValueError):
            issue.do_open("title", "  ", "claude", gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls, [])

    def test_refuses_missing_signer(self):
        with self.assertRaises(ValueError):
            issue.do_open("title", "body", "", gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls, [])

    def test_gh_failure_writes_no_record(self):
        with self.assertRaises(RuntimeError):
            issue.do_open("title", "body", "claude",
                          gh_run=self._gh(ret=1, out=""), events_path=self.log)
        self.assertEqual(self._records(), [])         # a refused create is never recorded


class IssueReopenTest(unittest.TestCase):
    """The recovery verb (added 2026-06-21 after tend-inbox wrong-closed #348):
    un-closing carries the same accountability as closing — a reason and a
    signer, refused before any gh call, recorded only on a successful reopen."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = self.tmp / "events.jsonl"
        self.calls = []

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gh(self, ret=0):
        def run(args):
            self.calls.append(args)
            return _FakeProc(ret, "")
        return run

    def _records(self):
        if not self.log.exists():
            return []
        return [json.loads(ln) for ln in self.log.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def test_reopen_records_after_success(self):
        rec = issue.do_reopen("348", "the close was wrong", "claude",
                              gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls[0][:3], ["issue", "reopen", "348"])
        self.assertEqual(rec["type"], "issue.reopened")
        self.assertEqual(rec["reason"], "the close was wrong")
        self.assertEqual(rec["by"], "claude")
        self.assertEqual(len(self._records()), 1)

    def test_refuses_empty_reason_before_any_gh(self):
        with self.assertRaises(ValueError):
            issue.do_reopen("348", "   ", "claude", gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls, [])
        self.assertEqual(self._records(), [])

    def test_refuses_missing_signer(self):
        with self.assertRaises(ValueError):
            issue.do_reopen("348", "reason", "", gh_run=self._gh(), events_path=self.log)
        self.assertEqual(self.calls, [])

    def test_gh_failure_writes_no_record(self):
        with self.assertRaises(RuntimeError):
            issue.do_reopen("348", "reason", "claude",
                            gh_run=self._gh(ret=1), events_path=self.log)
        self.assertEqual(self._records(), [])


if __name__ == "__main__":
    unittest.main()
