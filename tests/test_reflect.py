"""Tests for the reflection fold and the reflector pen (done-line 0018):
surfaces are admitted records; the drift fold is pure (no network, no
subprocess) and computes open-on-arrival / close-on-clear; reflecting to
an unregistered surface refuses; recorded acts make re-runs no-ops; and
the §10 case — a cleared atom whose issue stays open — must show as drift,
never as silence. The pen applies drift through an injectable runner and
records each act before attempting the next, so a half-applied run
resumes instead of double-acting."""

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile, reflect, summon

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
STAMP_STAGE = "owner-stamp.mock-bdo.v0"
STAMP_REAL = "owner-stamp.bdo.v1"

_spec = importlib.util.spec_from_file_location(
    "reflect_pen", REPO / ".claude" / "skills" / "reflect" / "reflect.py")
reflect_pen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reflect_pen)


def make_atom(i):
    return {"atom": {
        "id": f"atom.reflect-{i:02d}.v0",
        "story": {"text": f"As an AI, I need reflection {i} to reach the owner "
                          "where he looks, because a real queue behind an empty "
                          "surface reads as a lie.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "briefing": {"headline": f"Reflection {i} reaches the surface",
                     "value": "the queue is visible where bdo actually looks"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.reflect"], "touches": [".ai-native/log"],
                      "must_not_collide_with": [], "hands_off_to": ["seam.value-to-owner-stamp"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending", "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def make_root(tmp, n_atoms):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    for i in range(n_atoms):
        (root / "atoms" / f"atom.reflect-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    return root


class ReflectBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 1)
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        node.admit_real(self.root, STAMP_STAGE, STAMP_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # seed; parks at L0

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def to_stamp(self, atom_id="atom.reflect-00.v0"):
        """Walk the atom to the owner's queue: L0 accepts, the loop derives."""
        node.main(["judge", "--root", str(self.root), "--atom", atom_id,
                   "--node", L0_REAL, "--verdict", "accept", "--reason", "test"])
        orchestrate.orchestrate(self.root, quiet=True)

    def stamp(self, atom_id="atom.reflect-00.v0", verdict="accept"):
        node.main(["judge", "--root", str(self.root), "--atom", atom_id,
                   "--node", STAMP_REAL, "--verdict", verdict, "--reason", "test stamp"])
        orchestrate.orchestrate(self.root, quiet=True)

    def register(self):
        reflect.admit_surface(self.root, "github-issues", "owner/repo", by="test-bdo")


class PurityTest(unittest.TestCase):
    def test_drift_fold_reaches_no_network(self):
        """The hard rule, pinned: loop/reflect.py computes, never reaches —
        outward reach lives only in the pen. Checked against what the module
        imports, not its prose (the docstring may name the rule)."""
        import ast
        source = (REPO / "loop" / "reflect.py").read_text(encoding="utf-8")
        imported = set()
        for stmt in ast.walk(ast.parse(source)):
            if isinstance(stmt, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in stmt.names}
            elif isinstance(stmt, ast.ImportFrom):
                imported.add((stmt.module or "").split(".")[0])
        for forbidden in ("subprocess", "socket", "urllib", "http", "requests"):
            self.assertNotIn(forbidden, imported)


class RegistryTest(ReflectBase):
    def test_surfaces_are_admitted_records_latest_wins(self):
        self.assertEqual(reflect.registered_surfaces(reconcile.Fold(self.root)), {})
        self.register()
        surfaces = reflect.registered_surfaces(reconcile.Fold(self.root))
        self.assertEqual(surfaces["github-issues"]["address"], "owner/repo")
        reflect.admit_surface(self.root, "github-issues", "owner/other", by="test-bdo")
        surfaces = reflect.registered_surfaces(reconcile.Fold(self.root))
        self.assertEqual(surfaces["github-issues"]["address"], "owner/other")
        reflect.admit_surface(self.root, "github-issues", None, by="test-bdo")
        self.assertEqual(reflect.registered_surfaces(reconcile.Fold(self.root)), {})

    def test_unregistered_surface_refuses(self):
        with self.assertRaises(ValueError):
            reflect.drift(self.root, "github-issues")


class DriftTest(ReflectBase):
    def test_no_drift_while_nothing_awaits_the_stamp(self):
        self.register()
        self.assertEqual(reflect.drift(self.root, "github-issues"), [])

    def test_arrival_at_the_stamp_is_an_open_act_briefed(self):
        self.register()
        self.to_stamp()
        acts = reflect.drift(self.root, "github-issues")
        self.assertEqual([a["act"] for a in acts], ["open"])
        act = acts[0]
        self.assertIn("[stamp] atom.reflect-00.v0", act["title"])
        for fragment in ("the queue is visible", "As an AI, I need reflection",
                         "accept | reject_no_value", "loop.node judge", "mirror"):
            self.assertIn(fragment, act["body"])

    def test_recorded_open_is_a_no_op_and_idempotent(self):
        self.register()
        self.to_stamp()
        act = reflect.drift(self.root, "github-issues")[0]
        for _ in range(2):  # recording twice folds to one (content-derived id)
            reflect.record_reflection(self.root, "github-issues", act["atom_id"],
                                      act["artifact_hash"], "open",
                                      "https://x/issues/1", by="test")
        self.assertEqual(reflect.drift(self.root, "github-issues"), [])
        fold = reconcile.Fold(self.root)
        opens = [ev for ev in fold.events if ev.get("type") == reflect.REFLECTED_EVENT]
        self.assertEqual(len(opens), 1)

    def test_cleared_atom_with_open_issue_must_not_fit(self):
        """§10: the stamp lands, the issue still open — that is drift, and
        the close act carries the verdict and receipt id."""
        self.register()
        self.to_stamp()
        act = reflect.drift(self.root, "github-issues")[0]
        reflect.record_reflection(self.root, "github-issues", act["atom_id"],
                                  act["artifact_hash"], "open",
                                  "https://x/issues/1", by="test")
        self.stamp()
        acts = reflect.drift(self.root, "github-issues")
        self.assertEqual([a["act"] for a in acts], ["close"])
        close = acts[0]
        self.assertEqual(close["external_ref"], "https://x/issues/1")
        self.assertIn("accept", close["comment"])
        self.assertIn("rcp.", close["comment"])
        reflect.record_reflection(self.root, "github-issues", close["atom_id"],
                                  close["artifact_hash"], "close",
                                  close["external_ref"], by="test")
        self.assertEqual(reflect.drift(self.root, "github-issues"), [])

    def test_mocked_stamp_queues_nothing(self):
        """The owner queue is defined by the admitted-real stamp; reverting
        the stamp to its mock empties the reflection too."""
        self.register()
        self.to_stamp()
        node.admit_real(self.root, STAMP_STAGE, None, by="test-bdo")
        self.assertEqual(reflect.drift(self.root, "github-issues"), [])


class PenTest(ReflectBase):
    def apply(self, run):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = reflect_pen.apply(self.root, "github-issues", by="test", run=run)
        return code, out.getvalue()

    def test_apply_opens_records_and_reruns_as_no_op(self):
        self.register()
        self.to_stamp()
        calls = []

        def fake(args):
            calls.append(args)
            return "https://github.com/owner/repo/issues/7"

        code, text = self.apply(fake)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:3], ["gh", "issue", "create"])
        self.assertIn("--repo", calls[0])
        code, text = self.apply(fake)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)  # no drift, no reach
        self.assertIn("no drift", text)

    def test_apply_refuses_unregistered_surface(self):
        code, text = self.apply(lambda args: self.fail("must not reach out"))
        self.assertEqual(code, 2)
        self.assertIn("not admitted", text)

    def test_failed_act_resumes_without_double_acting(self):
        self.register()
        self.to_stamp()
        self.register_second_awaiting()
        attempts = []

        def fail_second(args):
            attempts.append(args)
            if len(attempts) > 1:
                raise RuntimeError("gh fell over")
            return "https://github.com/owner/repo/issues/8"

        code, text = self.apply(fail_second)
        self.assertEqual(code, 2)
        self.assertIn("re-run to resume", text)
        code, text = self.apply(lambda args: "https://github.com/owner/repo/issues/9")
        self.assertEqual(code, 0)
        fold = reconcile.Fold(self.root)
        refs = sorted(ev["external_ref"] for ev in fold.events
                      if ev.get("type") == reflect.REFLECTED_EVENT)
        self.assertEqual(len(refs), 2)
        self.assertEqual(len(set(refs)), 2)  # the first act was never re-applied

    def register_second_awaiting(self):
        (self.root / "atoms" / "atom.reflect-01.v0.json").write_text(
            json.dumps(make_atom(1), indent=2), encoding="utf-8")
        orchestrate.orchestrate(self.root, quiet=True)
        self.to_stamp("atom.reflect-01.v0")


class HookTest(ReflectBase):
    def hook_text(self):
        out = io.StringIO()
        stdin = io.StringIO("{}")
        with contextlib.redirect_stdout(out):
            old = sys.stdin
            sys.stdin = stdin
            try:
                self.assertEqual(summon.main(["--root", str(self.root), "--hook"]), 0)
            finally:
                sys.stdin = old
        return out.getvalue()

    def test_hook_names_drift_and_stays_quiet_without_it(self):
        self.register()
        self.assertNotIn("surface drift", self.hook_text())
        self.to_stamp()
        text = self.hook_text()
        self.assertIn("surface drift: 1 act(s)", text)
        act = reflect.drift(self.root, "github-issues")[0]
        reflect.record_reflection(self.root, "github-issues", act["atom_id"],
                                  act["artifact_hash"], "open", "https://x/1", by="test")
        self.assertNotIn("surface drift", self.hook_text())

    def test_hook_still_writes_nothing(self):
        self.register()
        self.to_stamp()
        before = {name: (self.root / "log" / name).read_bytes()
                  for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl")}
        self.hook_text()
        for name, data in before.items():
            self.assertEqual((self.root / "log" / name).read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
