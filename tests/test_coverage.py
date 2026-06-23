"""The discovered-coverage fold's classifier (loop/coverage.py) + the file-touch
sensor (.claude/hooks/file_touch.py).

A per-file mask is only as honest as the rule that decides discovered vs
undiscovered. These tests pin that rule with teeth (§10): the pure classifier
must DISTINGUISH the two shapes — a constant or fabricated classifier
(everything 'discovered') is CAUGHT — and the load-bearing bite must hold:

  - a TRACKED file no session ever touched reads `undiscovered`;
  - a file the touch log records (read OR edited) reads `discovered`.

It also checks the fold writes nothing (read-only) and reads the log it is given,
and that the sensor hook, fed a sample Read hook-stdin, appends one correct
record — and, fed malformed stdin, exits 0 without writing.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from loop import coverage

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".claude" / "hooks" / "file_touch.py"


class FileStatus(unittest.TestCase):
    def test_touched_is_discovered(self):
        self.assertEqual(
            coverage.file_status("loop/forest.py", {"loop/forest.py"}),
            "discovered")

    def test_never_touched_is_undiscovered(self):
        # THE §10 BITE: a tracked file absent from the discovered set is
        # undiscovered — a classifier that called it discovered would paint a
        # false 'attention reached here'.
        self.assertEqual(
            coverage.file_status("loop/forest.py", set()), "undiscovered")

    def test_classifier_is_not_constant(self):
        # a fabricated 'always discovered' classifier would collapse these; the
        # real one must spread across the vocabulary.
        discovered = {"a/touched.py"}
        seen = {
            coverage.file_status("a/touched.py", discovered),
            coverage.file_status("a/untouched.py", discovered),
        }
        self.assertEqual(seen, {"discovered", "undiscovered"})


class CoverageFold(unittest.TestCase):
    def _model(self):
        tracked = ["loop/forest.py", "loop/coverage.py", "tests/test_x.py",
                   "docs/never_opened.md"]
        discovered = {"loop/forest.py", "loop/coverage.py"}
        return coverage.coverage(tracked, discovered)

    def test_counts_split_discovered_and_undiscovered(self):
        d = self._model()
        self.assertEqual(d["totals"]["tracked"], 4)
        self.assertEqual(d["totals"]["discovered"], 2)
        self.assertEqual(d["totals"]["undiscovered"], 2)

    def test_per_file_status_is_correct(self):
        d = self._model()
        by_path = {f["path"]: f["status"] for f in d["files"]}
        self.assertEqual(by_path["loop/forest.py"], "discovered")
        self.assertEqual(by_path["docs/never_opened.md"], "undiscovered")

    def test_per_directory_counts(self):
        d = self._model()
        self.assertEqual(d["dirs"]["loop"],
                         {"discovered": 2, "undiscovered": 0, "total": 2})
        self.assertEqual(d["dirs"]["docs"],
                         {"discovered": 0, "undiscovered": 1, "total": 1})

    def test_all_discovered_is_not_vacuously_constant(self):
        # if every tracked file is touched, the fold says so — but the same fold
        # spreads when one is not (the non-vacuous proof: it is the input that
        # decides, never a constant).
        all_touched = coverage.coverage(["a.py", "b.py"], {"a.py", "b.py"})
        self.assertEqual(all_touched["totals"]["undiscovered"], 0)
        one_missing = coverage.coverage(["a.py", "b.py"], {"a.py"})
        self.assertEqual(one_missing["totals"]["undiscovered"], 1)


class DiscoveredSet(unittest.TestCase):
    def test_reads_the_log_read_only_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "file-touch.jsonl"
            log.write_text(
                json.dumps({"ts": "t", "session": "s", "action": "read",
                            "path": "loop/forest.py"}) + "\n"
                + json.dumps({"ts": "t", "session": "s", "action": "edit",
                              "path": "loop/coverage.py"}) + "\n"
                + "{ torn tail not json\n",  # torn line is dropped
                encoding="utf-8")
            before = log.read_bytes()
            got = coverage.discovered_set(log)
            self.assertEqual(got, {"loop/forest.py", "loop/coverage.py"})
            # read-only: the fold touched no byte of the log it read.
            self.assertEqual(log.read_bytes(), before)

    def test_absent_log_is_empty_set(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                coverage.discovered_set(Path(td) / "missing.jsonl"), set())


class FileTouchSensor(unittest.TestCase):
    """The sensor hook, end to end via subprocess (the real stdin contract)."""

    def _run(self, stdin_obj, log_path):
        env = dict(os.environ, ONTUM_FILE_TOUCH_LOG=str(log_path))
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(stdin_obj), text=True,
            capture_output=True, env=env, timeout=30)
        return proc

    def test_read_appends_one_record(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "ft.jsonl"
            proc = self._run({
                "tool_name": "Read",
                "session_id": "sess-1",
                "tool_input": {"file_path": str(REPO / "loop" / "forest.py")},
            }, log)
            self.assertEqual(proc.returncode, 0)
            lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["action"], "read")
            self.assertEqual(rec["session"], "sess-1")
            self.assertEqual(rec["path"], "loop/forest.py")
            self.assertIn("ts", rec)

    def test_edit_records_edit_action(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "ft.jsonl"
            self._run({
                "tool_name": "MultiEdit",
                "session_id": "sess-2",
                "tool_input": {"file_path": str(REPO / "loop" / "coverage.py")},
            }, log)
            rec = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(rec["action"], "edit")
            self.assertEqual(rec["path"], "loop/coverage.py")

    def test_non_file_tool_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "ft.jsonl"
            proc = self._run({"tool_name": "Bash", "session_id": "s",
                              "tool_input": {"command": "ls"}}, log)
            self.assertEqual(proc.returncode, 0)
            self.assertFalse(log.exists())

    def test_no_concrete_path_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "ft.jsonl"
            self._run({"tool_name": "Read", "session_id": "s",
                       "tool_input": {}}, log)
            self.assertFalse(log.exists())

    def test_malformed_stdin_exits_zero_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "ft.jsonl"
            env = dict(os.environ, ONTUM_FILE_TOUCH_LOG=str(log))
            proc = subprocess.run(
                [sys.executable, str(HOOK)],
                input="{ this is not json", text=True,
                capture_output=True, env=env, timeout=30)
            self.assertEqual(proc.returncode, 0)
            self.assertFalse(log.exists())


if __name__ == "__main__":
    unittest.main()
