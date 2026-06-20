"""§10 for the workstation write-fence (done-line 0147).

The teeth: a target path is the same string wherever a session stands. The
fence must refuse a Write/Edit into it when the session stands in a DIFFERENT
worktree (a sibling bench, or the viewport) and allow the very same write when
the session stands in the tree that owns the path. The verdict turns on the
SESSION's payload cwd, not the process cwd — so the test runs the guard from a
neutral dir and moves only the payload cwd, proving the discrimination is on
location, not on where the hook happens to run.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = REPO / ".claude" / "hooks" / "workstation_guard.py"

sys.path.insert(0, str(REPO / ".claude" / "hooks"))
import workstation_guard as g  # noqa: E402


def run_guard(file_path, session_cwd, tool_name="Write"):
    key = "notebook_path" if tool_name == "NotebookEdit" else "file_path"
    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": {key: str(file_path), "content": "x"},
        "session_id": "test-write-fence",
        "cwd": str(session_cwd),
    })
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=payload, text=True, capture_output=True, cwd=str(REPO),
    )
    return proc.returncode, proc.stderr


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), check=True,
                   capture_output=True, text=True)


class WriteFence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ws-write-fence-")
        self.addCleanup(self._cleanup)
        self.primary = pathlib.Path(self.tmp) / "primary"
        self.primary.mkdir()
        _git(self.primary, "init", "-q")
        _git(self.primary, "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--allow-empty", "-q", "-m", "init")
        self.wt = pathlib.Path(self.tmp) / "wt"
        _git(self.primary, "worktree", "add", "-q", "-b", "wtbranch", str(self.wt))
        self.wt_file = self.wt / "loop" / "new.py"
        self.primary_file = self.primary / "loop" / "new.py"
        self.outside = pathlib.Path(self.tmp) / "not-a-repo" / "f.txt"

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- the discriminating teeth: same path, two benches ---
    def test_own_worktree_write_allowed(self):
        rc, err = run_guard(self.wt_file, session_cwd=self.wt)
        self.assertEqual(rc, 0, err)

    def test_write_into_a_worktree_from_the_viewport_denied(self):
        rc, err = run_guard(self.wt_file, session_cwd=self.primary)
        self.assertEqual(rc, 2, err)
        self.assertIn("WORKSTATION", err)

    def test_write_into_the_viewport_from_a_worktree_denied(self):
        rc, err = run_guard(self.primary_file, session_cwd=self.wt)
        self.assertEqual(rc, 2, err)

    def test_own_viewport_write_allowed(self):
        # a session standing in the viewport writing the viewport is not foreign
        # (tooth #1 governs git-flips; the source fix keeps write-sessions out)
        rc, err = run_guard(self.primary_file, session_cwd=self.primary)
        self.assertEqual(rc, 0, err)

    # --- not-a-workstation paths are never fenced ---
    def test_path_in_no_git_tree_allowed(self):
        rc, err = run_guard(self.outside, session_cwd=self.wt)
        self.assertEqual(rc, 0, err)

    # --- the edit tools are covered too, not just Write ---
    def test_edit_into_foreign_worktree_denied(self):
        rc, err = run_guard(self.wt_file, session_cwd=self.primary, tool_name="Edit")
        self.assertEqual(rc, 2, err)

    def test_notebookedit_into_foreign_worktree_denied(self):
        rc, err = run_guard(self.wt / "n.ipynb", session_cwd=self.primary,
                            tool_name="NotebookEdit")
        self.assertEqual(rc, 2, err)


class ForeignWorktreeUnit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ws-write-unit-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.primary = pathlib.Path(self.tmp) / "primary"
        self.primary.mkdir()
        _git(self.primary, "init", "-q")
        _git(self.primary, "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "--allow-empty", "-q", "-m", "init")
        self.wt = pathlib.Path(self.tmp) / "wt"
        _git(self.primary, "worktree", "add", "-q", "-b", "b", str(self.wt))

    def test_foreign_detected_across_benches(self):
        self.assertIsNotNone(g.foreign_worktree(self.wt / "x.py", str(self.primary)))
        self.assertIsNotNone(g.foreign_worktree(self.primary / "x.py", str(self.wt)))

    def test_own_bench_is_not_foreign(self):
        self.assertIsNone(g.foreign_worktree(self.wt / "x.py", str(self.wt)))
        self.assertIsNone(g.foreign_worktree(self.primary / "x.py", str(self.primary)))

    def test_non_repo_path_is_not_foreign(self):
        outside = pathlib.Path(self.tmp) / "elsewhere" / "f.txt"
        self.assertIsNone(g.foreign_worktree(outside, str(self.wt)))


if __name__ == "__main__":
    unittest.main()
