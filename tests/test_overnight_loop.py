"""Done-lines 0031 and 0032: overnight-loop refuses unsafe starts.

The section 10 fit test here is a locally tempting instruction: "work
overnight" from whatever checkout happens to be open. The repo requires
that to refuse when the checkout is bdo's viewport, dirty without
acknowledgement, pointed at an unknown arc, or asked to choose work from
an unsafe branch.
"""

import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEN_PATH = ROOT / ".claude" / "skills" / "overnight-loop" / "overnight.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


overnight = _load("overnight_loop", PEN_PATH)


class TestOvernightBrief(unittest.TestCase):
    def _git(self, root, *args):
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )

    def _repo(self, branch="codex/overnight"):
        temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(temp.name)
        self.addCleanup(temp.cleanup)
        self._git(root, "init", "-b", "main")
        self._git(root, "config", "user.email", "test@example.invalid")
        self._git(root, "config", "user.name", "Test User")
        epic_dir = root / ".ai-native" / "epics"
        epic_dir.mkdir(parents=True)
        (epic_dir / "epic.test.json").write_text(
            json.dumps(
                {
                    "epic": {
                        "id": "epic.test",
                        "owner": "bdo",
                        "arc": "A test arc for overnight-loop briefing.",
                    }
                }
            ),
            encoding="utf-8",
        )
        self._git(root, "add", ".ai-native/epics/epic.test.json")
        self._git(root, "commit", "-q", "-m", "fixture")
        if branch != "main":
            self._git(root, "checkout", "-q", "-b", branch)
        return root

    def _brief(self, root, *extra):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = overnight.main(
                [
                    "brief",
                    "--repo-root",
                    str(root),
                    "--arc",
                    "epic.test",
                    "--objective",
                    "prove the overnight brief",
                    *extra,
                ]
            )
        return rc, stdout.getvalue()

    def _pickup(self, root, *extra):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = overnight.main(["pickup", "--repo-root", str(root), *extra])
        return rc, stdout.getvalue()

    def _checkpoint(self, root, *extra):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = overnight.main(["checkpoint", "--repo-root", str(root), *extra])
        return rc, stdout.getvalue()

    def test_refuses_owner_viewport_branch(self):
        root = self._repo(branch="main")
        rc, out = self._brief(root)
        self.assertEqual(rc, 1)
        self.assertIn("refused", out)
        self.assertIn("owner viewport", out)

    def test_refuses_non_session_branch(self):
        root = self._repo(branch="feature/overnight")
        rc, out = self._brief(root)
        self.assertEqual(rc, 1)
        self.assertIn("not a session branch", out)

    def test_refuses_dirty_tree_without_acknowledgement(self):
        root = self._repo()
        (root / "scratch.txt").write_text("inherited work\n", encoding="utf-8")
        rc, out = self._brief(root)
        self.assertEqual(rc, 1)
        self.assertIn("dirty tree", out)
        self.assertIn("--allow-dirty", out)

    def test_refuses_unknown_arc(self):
        root = self._repo()
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = overnight.main(
                [
                    "brief",
                    "--repo-root",
                    str(root),
                    "--arc",
                    "epic.missing",
                    "--objective",
                    "prove the overnight brief",
                ]
            )
        self.assertEqual(rc, 1)
        self.assertIn("unknown arc `epic.missing`", stdout.getvalue())
        self.assertIn("epic.test", stdout.getvalue())

    def test_valid_brief_names_contract(self):
        root = self._repo()
        rc, out = self._brief(root)
        self.assertEqual(rc, 0)
        self.assertIn("overnight-loop brief", out)
        self.assertIn("branch: codex/overnight", out)
        self.assertIn("arc: epic.test", out)
        self.assertIn("authority:", out)
        self.assertIn("stop conditions:", out)
        self.assertIn("python -m unittest discover -s tests -v", out)
        self.assertIn("result: report - overnight-loop brief ready", out)

    def test_dirty_tree_can_be_explicitly_inherited(self):
        root = self._repo()
        (root / "scratch.txt").write_text("inherited work\n", encoding="utf-8")
        rc, out = self._brief(root, "--allow-dirty")
        self.assertEqual(rc, 0)
        self.assertIn("dirty start: allowed (1 path(s))", out)

    def test_pickup_recommends_known_arc_without_summons(self):
        root = self._repo()
        rc, out = self._pickup(root)
        self.assertEqual(rc, 0)
        self.assertIn("overnight-loop pickup", out)
        self.assertEqual(out.count("recommended arc:"), 1)
        self.assertEqual(out.count("next story:"), 1)
        self.assertIn("recommended arc: epic.test", out)
        self.assertIn("next story: test arc pickup", out)
        self.assertIn("open summons read: none", out)
        self.assertIn("first commands:", out)
        self.assertIn("stop conditions:", out)
        self.assertIn("python -m unittest tests.test_overnight_loop -v", out)
        self.assertIn("result: report - overnight-loop pickup recommends epic.test", out)

    def test_pickup_refuses_unknown_requested_arc(self):
        root = self._repo()
        rc, out = self._pickup(root, "--arc", "epic.missing")
        self.assertEqual(rc, 1)
        self.assertIn("unknown arc `epic.missing`", out)
        self.assertIn("epic.test", out)

    def test_pickup_refuses_owner_viewport_branch(self):
        root = self._repo(branch="main")
        rc, out = self._pickup(root)
        self.assertEqual(rc, 1)
        self.assertIn("owner viewport", out)

    def test_pickup_refuses_dirty_tree_without_acknowledgement(self):
        root = self._repo()
        (root / "scratch.txt").write_text("inherited work\n", encoding="utf-8")
        rc, out = self._pickup(root)
        self.assertEqual(rc, 1)
        self.assertIn("dirty tree", out)
        self.assertIn("--allow-dirty", out)

    def test_checkpoint_continues_before_eight(self):
        root = self._repo()
        rc, out = self._checkpoint(root, "--now", "2026-06-11T00:06:25")
        self.assertEqual(rc, 0)
        self.assertIn("overnight-loop checkpoint", out)
        self.assertIn("stop time: 08:00", out)
        self.assertIn("decision: continue", out)
        self.assertIn("overnight.py pickup", out)
        self.assertIn("result: report - before 08:00; continue overnight loop", out)

    def test_checkpoint_hands_off_at_eight(self):
        root = self._repo()
        rc, out = self._checkpoint(root, "--now", "2026-06-11T08:00:00")
        self.assertEqual(rc, 0)
        self.assertIn("decision: handoff", out)
        self.assertIn("loop.pen new reports", out)
        self.assertIn("result: done - 08:00 reached; hand off the overnight loop", out)

    def test_checkpoint_refuses_owner_viewport_branch(self):
        root = self._repo(branch="main")
        rc, out = self._checkpoint(root, "--now", "2026-06-11T00:06:25")
        self.assertEqual(rc, 1)
        self.assertIn("owner viewport", out)

    def test_checkpoint_refuses_dirty_tree_without_acknowledgement(self):
        root = self._repo()
        (root / "scratch.txt").write_text("inherited work\n", encoding="utf-8")
        rc, out = self._checkpoint(root, "--now", "2026-06-11T00:06:25")
        self.assertEqual(rc, 1)
        self.assertIn("dirty tree", out)
        self.assertIn("--allow-dirty", out)


if __name__ == "__main__":
    unittest.main()
