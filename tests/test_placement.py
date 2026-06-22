"""Done-line 0023: placement refuses cross-ref address collisions.

The §10 case made into a test: two records that are each locally fine must
refuse to fit when they claim one id across the fleet — and the local-fold
checks (the records pen, the write guard) that wave them through are the bug
this closes. Pure working-tree logic, then a real two-branch git repo so the
cross-ref fold is exercised, not asserted.
"""

import importlib.util
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLACEMENT_PATH = ROOT / ".claude" / "hooks" / "placement.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


placement = _load("placement", PLACEMENT_PATH)


class TestWorkingTreeFold(unittest.TestCase):
    """No git needed: the working-tree fold alone catches two records that
    claim one id in a single directory."""

    def _dir(self, *names):
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for n in names:
            (d / n).write_text("x", encoding="utf-8")
        return d

    def test_two_records_one_id_collide(self):
        d = self._dir("0020-git-commit-pen.md", "0020-reflection-automates.md")
        found = placement.collisions(d, root=d)
        self.assertIn("0020", found)
        self.assertEqual(len(found["0020"]), 2)

    def test_distinct_ids_do_not_collide(self):
        d = self._dir("0020-a.md", "0021-b.md")
        self.assertEqual(placement.collisions(d, root=d), {})

    def test_next_id_is_one_past_the_highest(self):
        d = self._dir("0020-a.md", "0022-b.md")
        self.assertEqual(placement.next_id(d, root=d), 23)


class TestCrossRefFold(unittest.TestCase):
    """The point of the pen: a sibling branch's id is seen, so a local fold's
    blind spot (the colliding 0020s) cannot reopen."""

    def _repo(self):
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)

        def g(*args):
            subprocess.run(["git", *args], cwd=d, check=True,
                           capture_output=True, text=True)

        g("init", "-q")
        g("config", "user.email", "t@example.com")
        g("config", "user.name", "t")
        done = d / ".ai-native" / "done"
        done.mkdir(parents=True)
        (done / "0001-first.md").write_text("a", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "first")
        g("checkout", "-qb", "sibling")
        # same id, different record on a sibling branch — the collision
        (done / "0001-first.md").unlink()
        (done / "0001-second.md").write_text("b", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "second")
        return d, done

    def test_collision_seen_across_branches(self):
        d, done = self._repo()
        found = placement.collisions(done, root=d)
        self.assertIn("0001", found, "the sibling branch's 0001 must be seen")
        self.assertEqual(len(found["0001"]), 2)

    def test_next_id_folds_all_branches(self):
        d, done = self._repo()
        self.assertEqual(placement.next_id(done, root=d), 2)


class TestWorktreeFold(unittest.TestCase):
    """The concurrent-mint blind spot: placement folded only the CURRENT
    checkout's working tree, so a SIBLING worktree's *uncommitted* mint was
    invisible — two parallel worktrees picked the same id and only the
    commit-check caught it (the 0149 collision). The fix folds every worktree."""

    def _repo_with_sibling_worktree(self):
        base = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        main = base / "main"
        main.mkdir()

        def g(cwd, *args):
            subprocess.run(["git", *args], cwd=cwd, check=True,
                           capture_output=True, text=True)

        g(main, "init", "-q")
        g(main, "config", "user.email", "t@example.com")
        g(main, "config", "user.name", "t")
        done = main / ".ai-native" / "done"
        done.mkdir(parents=True)
        (done / "0001-first.md").write_text("a", encoding="utf-8")
        g(main, "add", "-A")
        g(main, "commit", "-qm", "first")
        sib = base / "sib"
        g(main, "worktree", "add", "-q", "-b", "feature", str(sib))
        self.addCleanup(lambda: subprocess.run(
            ["git", "worktree", "prune"], cwd=main, capture_output=True))
        # an UNCOMMITTED mint in the sibling worktree — invisible before the fix
        (sib / ".ai-native" / "done" / "0002-second.md").write_text(
            "b", encoding="utf-8")
        return main, done

    def test_sibling_worktree_uncommitted_record_is_seen(self):
        main, done = self._repo_with_sibling_worktree()
        self.assertIn("0002", set(placement.claims(done, root=main)),
                      "a sibling worktree's uncommitted record was not folded")

    def test_next_id_skips_a_sibling_worktrees_uncommitted_mint(self):
        main, done = self._repo_with_sibling_worktree()
        self.assertEqual(placement.next_id(done, root=main), 3,
                         "next_id re-handed an id a sibling worktree already minted")


if __name__ == "__main__":
    unittest.main()
