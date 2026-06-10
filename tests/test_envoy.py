"""Pins done-line 0015: the envoy pen — a sealed package of at most ten
flat files, refusals before features (§10: a locally-fine eleventh file
must not fit), byte-deterministic pen slots, authored prose never
clobbered, and a receipt on the disclosure ledger for every seal.
"""

import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PEN_PATH = ROOT / ".claude" / "skills" / "envoy" / "envoy.py"


def load_pen():
    spec = importlib.util.spec_from_file_location("envoy_under_test", PEN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


envoy = load_pen()


def make_repo(base):
    """A throwaway repo with enough surface for every pen slot: tracked
    files, two commits, numbered records — but no loop package, so the
    architecture slot also exercises its degraded path."""
    root = pathlib.Path(base)
    (root / "src").mkdir()
    (root / "src" / "alpha.py").write_bytes(
        b'"""Alpha module: the fixture\'s one real source file."""\n\n'
        b"def alpha():\n    return 42\n")
    (root / "README.md").write_bytes(b"# fixture\n\na tiny repo\n")
    (root / ".ai-native" / "done").mkdir(parents=True)
    (root / ".ai-native" / "done" / "0001-first.md").write_bytes(
        b"# Done-line 0001 - the first line\n")
    (root / ".ai-native" / "reports").mkdir()
    (root / ".ai-native" / "reports" / "0001-first.md").write_bytes(
        b"# Report 0001 - the first report\n")
    (root / "exports").mkdir()
    git = ["git", "-C", str(root)]
    for args in (["init", "-q"],
                 ["config", "user.email", "test@example.invalid"],
                 ["config", "user.name", "test-bdo"],
                 ["add", "-A"],
                 ["commit", "-q", "-m", "fixture: first commit"]):
        subprocess.run(git + args, check=True, capture_output=True)
    (root / "src" / "beta.py").write_bytes(b"def beta():\n    return 7\n")
    subprocess.run(git + ["add", "-A"], check=True, capture_output=True)
    subprocess.run(git + ["commit", "-q", "-m", "fixture: second commit"],
                   check=True, capture_output=True)
    return root


def author(path, text):
    """Replace the stub comment block with authored prose, keeping any
    marker-fenced blocks (manifest, timeline) intact — the same move a
    session makes."""
    raw = path.read_bytes().decode("utf-8")
    replaced = re.sub(r"<!-- envoy:stub.*?-->", text, raw, flags=re.S)
    path.write_bytes(replaced.encode("utf-8"))


def base_spec(slots=None):
    return {
        "package": "pkg",
        "title": "a fixture package",
        "audience": "a foreign reviewer",
        "framing": "fixture review",
        "questions": ["does the gate hold?"],
        "feedback_shape": "findings",
        "by": "test-bdo",
        "budget": {"total_tokens": 120000, "per_file_tokens": 40000},
        "slots": slots if slots is not None else [
            {"kind": "briefing", "slug": "briefing", "title": "Briefing"},
            {"kind": "arc", "slug": "arc", "title": "The arc"},
            {"kind": "repo-map", "slug": "repo-map", "title": "Map"},
            {"kind": "history", "slug": "history", "title": "History"},
            {"kind": "code", "slug": "code", "title": "Code",
             "sources": ["src/*.py"]},
        ],
    }


class EnvoyCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_repo(self._tmp.name)
        self._env = os.environ.get("ONTUM_REPO_ROOT")
        os.environ["ONTUM_REPO_ROOT"] = str(self.root)

    def tearDown(self):
        if self._env is None:
            os.environ.pop("ONTUM_REPO_ROOT", None)
        else:
            os.environ["ONTUM_REPO_ROOT"] = self._env
        self._tmp.cleanup()

    # -------------------------------------------------------------- helpers

    def write_spec(self, spec):
        pkg_dir = self.root / "exports" / spec["package"]
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / ".spec.json").write_bytes(
            json.dumps(spec, indent=2).encode("utf-8"))
        return pkg_dir

    def build(self, spec):
        pkg_dir = self.write_spec(spec)
        rc = envoy.cmd_build(types.SimpleNamespace(package=spec["package"]))
        self.assertEqual(rc, 0)
        return pkg_dir

    def author_all(self, spec, pkg_dir):
        for i, slot in enumerate(spec["slots"]):
            if envoy.SLOTS[slot["kind"]]["mode"] in ("session", "hybrid"):
                author(pkg_dir / f"{i:02d}-{slot['slug']}.md",
                       f"Authored prose for {slot['slug']}: enough words to "
                       "carry meaning to a foreign reviewer.")

    def seal(self, package, by="test-bdo"):
        return envoy.cmd_seal(types.SimpleNamespace(package=package, by=by))

    # ------------------------------------------------------------ the spec

    def test_spec_refusals(self):
        spec = base_spec()
        spec["slots"][0]["kind"] = "synthesis"  # briefing no longer first
        spec["slots"][1]["kind"] = "nonsense"
        spec["slots"][2]["slug"] = "arc"        # duplicate of slot 1's slug
        spec["slots"][4]["sources"] = []        # code without sources
        problems, _ = envoy.validate_spec(spec, self.root)
        text = "\n".join(problems)
        for needle in ("first slot must be a briefing", "unknown kind",
                       "duplicate slug", "needs", "sources"):
            self.assertIn(needle, text)

    def test_spec_refuses_eleven_slots(self):
        slots = [{"kind": "briefing", "slug": "briefing", "title": "B"}]
        slots += [{"kind": "synthesis", "slug": f"extra-{i}", "title": "X"}
                  for i in range(10)]
        problems, _ = envoy.validate_spec(base_spec(slots), self.root)
        self.assertTrue(any("ten flat files is the contract" in p
                            for p in problems))

    def test_spec_refuses_source_escaping_the_repo(self):
        outside = pathlib.Path(self._tmp.name).parent / "envoy-escape.txt"
        outside.write_bytes(b"outside\n")
        try:
            spec = base_spec()
            spec["slots"][4]["sources"] = ["../envoy-escape.txt"]
            problems, _ = envoy.validate_spec(spec, self.root)
            self.assertTrue(any("escapes the repo" in p or
                                "matches nothing" in p for p in problems))
        finally:
            outside.unlink()

    # ------------------------------------------------------------ the gate

    def test_gate_refuses_a_locally_fine_stray_file(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        self.author_all(spec, pkg_dir)
        (pkg_dir / "99-extra.md").write_bytes(
            b"# perfectly fine content\n\nthat the spec never named\n")
        problems, _, _ = envoy.gate(self.root, spec, pkg_dir)
        self.assertTrue(any("stray file '99-extra.md'" in p for p in problems))

    def test_gate_refuses_unfilled_stub_and_empty_file(self):
        spec = base_spec()
        pkg_dir = self.build(spec)  # stubs left unfilled
        problems, _, _ = envoy.gate(self.root, spec, pkg_dir)
        self.assertTrue(any("still a stub" in p for p in problems))
        self.author_all(spec, pkg_dir)
        (pkg_dir / "02-repo-map.md").write_bytes(b"  \n")
        problems, _, _ = envoy.gate(self.root, spec, pkg_dir)
        self.assertTrue(any("'02-repo-map.md' is empty" in p
                            for p in problems))

    def test_gate_refuses_budget_overruns(self):
        spec = base_spec()
        spec["budget"] = {"total_tokens": 50, "per_file_tokens": 10}
        pkg_dir = self.build(spec)
        self.author_all(spec, pkg_dir)
        problems, _, _ = envoy.gate(self.root, spec, pkg_dir)
        text = "\n".join(problems)
        self.assertIn("per-file budget", text)
        self.assertIn("total budget", text)

    def test_gate_refuses_missing_manifest_markers(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        self.author_all(spec, pkg_dir)
        (pkg_dir / "00-briefing.md").write_bytes(
            b"# Briefing\n\nauthored, but the manifest block is gone\n")
        problems, _, _ = envoy.gate(self.root, spec, pkg_dir)
        self.assertTrue(any("manifest markers" in p for p in problems))

    # ----------------------------------------------------------- the build

    def test_pen_slots_are_byte_deterministic(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        first = {p.name: p.read_bytes() for p in pkg_dir.glob("*.md")}
        rc = envoy.cmd_build(types.SimpleNamespace(package="pkg"))
        self.assertEqual(rc, 0)
        for name in ("02-repo-map.md", "03-history.md", "04-code.md"):
            self.assertEqual(first[name], (pkg_dir / name).read_bytes(),
                             f"{name} wobbled between identical builds")

    def test_rebuild_never_clobbers_authored_prose(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        briefing = pkg_dir / "00-briefing.md"
        author(briefing, "The authored briefing: bytes that must survive.")
        arc = pkg_dir / "01-arc.md"
        author(arc, "The authored arc narrative.")
        before = briefing.read_bytes()
        arc_prose = arc.read_bytes().decode("utf-8").split(
            envoy.BLOCK_BEGIN.format(name="timeline"))[0]
        envoy.cmd_build(types.SimpleNamespace(package="pkg"))
        self.assertEqual(before, briefing.read_bytes())
        self.assertTrue(arc.read_bytes().decode("utf-8")
                        .startswith(arc_prose))

    def test_arc_timeline_lands_between_the_markers(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        text = (pkg_dir / "01-arc.md").read_bytes().decode("utf-8")
        timeline = text.split(envoy.BLOCK_BEGIN.format(name="timeline"))[1]
        self.assertIn("done-line", timeline)
        self.assertIn("the first line", timeline)

    def test_code_slot_embeds_the_sources_verbatim(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        text = (pkg_dir / "04-code.md").read_bytes().decode("utf-8")
        self.assertIn("## `src/alpha.py`", text)
        self.assertIn("def alpha():", text)
        self.assertIn("def beta():", text)

    def test_repo_map_walks_only_the_committed_surface(self):
        (self.root / "untracked-noise.txt").write_bytes(b"noise\n")
        spec = base_spec()
        pkg_dir = self.build(spec)
        text = (pkg_dir / "02-repo-map.md").read_bytes().decode("utf-8")
        self.assertIn("README.md", text)
        self.assertNotIn("untracked-noise.txt", text)

    # ------------------------------------------------------------ the seal

    def test_seal_writes_the_receipt_and_reseal_is_a_noop(self):
        spec = base_spec()
        pkg_dir = self.build(spec)
        self.author_all(spec, pkg_dir)
        self.assertEqual(self.seal("pkg"), 0)
        ledger = self.root / "exports" / "log.jsonl"
        entries = [json.loads(line) for line in
                   ledger.read_bytes().decode("utf-8").splitlines()]
        self.assertEqual(len(entries), 1)
        receipt = entries[0]
        self.assertEqual(receipt["by"], "test-bdo")
        self.assertEqual(len(receipt["files"]), 5)
        for f in receipt["files"]:
            self.assertRegex(f["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(f["tokens"], 0)
        # the manifest was stamped into the briefing before hashing
        briefing = (pkg_dir / "00-briefing.md").read_bytes().decode("utf-8")
        self.assertIn("| `04-code.md` | code |", briefing)
        # unchanged bytes: a second seal appends nothing
        self.assertEqual(self.seal("pkg"), 0)
        lines = ledger.read_bytes().decode("utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        # changed bytes: a new receipt accretes — never a rewrite
        author_path = pkg_dir / "00-briefing.md"
        author_path.write_bytes(briefing.replace(
            "Authored prose", "Reshaped prose").encode("utf-8"))
        self.assertEqual(self.seal("pkg"), 0)
        lines = ledger.read_bytes().decode("utf-8").splitlines()
        self.assertEqual(len(lines), 2)

    def test_seal_refuses_while_the_gate_refuses(self):
        spec = base_spec()
        self.build(spec)  # stubs unfilled
        self.assertEqual(self.seal("pkg"), 1)
        self.assertFalse((self.root / "exports" / "log.jsonl").exists())

    # ------------------------------------------------------------- the CLI

    def test_cli_speaks_the_result_protocol(self):
        env = dict(os.environ, ONTUM_REPO_ROOT=str(self.root),
                   PYTHONIOENCODING="utf-8")
        proc = subprocess.run(
            [sys.executable, str(PEN_PATH), "list"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", env=env)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("result: report", proc.stdout)

    def test_cli_new_refuses_to_rescaffold(self):
        env = dict(os.environ, ONTUM_REPO_ROOT=str(self.root),
                   PYTHONIOENCODING="utf-8")
        for expected_rc in (0, 1):
            proc = subprocess.run(
                [sys.executable, str(PEN_PATH), "new", "twice",
                 "--title", "a package"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", env=env)
            self.assertEqual(proc.returncode, expected_rc, proc.stdout)
        self.assertIn("already exists", proc.stdout)


if __name__ == "__main__":
    unittest.main()
