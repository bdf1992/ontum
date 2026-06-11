"""Tests for the gap fold against done-line 0048:
the loop's own gaps become the work a session is handed. The priority
ranking is deterministic and the §10 case holds — with two kinds present
the higher-pressure kind wins the hook line (a locally-fine lower gap
refuses to lead); each kind renders with its one concrete move; a clean
field prints no gap line in hook mode; the hook stays fail-open; the
fold writes nothing."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import gaps, node, orchestrate, reconcile, summon

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
ALL_MOCKS = sorted(s["node"] for s in reconcile.PIPELINE if ".mock" in s["node"])


def make_atom(i):
    return {"atom": {
        "id": f"atom.gaps-{i:02d}.v0",
        "story": {"text": f"As an AI, I need gap {i} to become the work I am "
                          "handed, because surfaced-but-unworked is the gap.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.gaps"], "touches": [".ai-native/log"],
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
        (root / "atoms" / f"atom.gaps-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    return root


def log_bytes(root):
    out = {}
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        p = root / "log" / name
        out[name] = p.read_bytes() if p.exists() else None
    return out


def admit_all_real(root):
    """Admit every still-mock stage; a stage already real keeps its node —
    re-admitting would supersede the judge whose receipts are on record."""
    real = reconcile.real_nodes(reconcile.Fold(root))
    for stage in ALL_MOCKS:
        if stage not in real:
            node.admit_real(root, stage, stage.replace(".mock", ".test-judge"),
                            by="test-bdo")


class GapFoldTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 1)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def park_the_atom(self):
        """Drive atom.gaps-00 to a real refusal: the value gate rejects it
        and the held-by receipt (no advancing event) parks it."""
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)
        rc = node.main(["judge", "--root", str(self.root),
                        "--atom", "atom.gaps-00.v0", "--node", L0_REAL,
                        "--verdict", "reject_no_value",
                        "--reason", "test refusal: no owner value on record"])
        self.assertEqual(rc, 0)

    # -- the ranking ------------------------------------------------------

    def test_fresh_root_mock_stages_top(self):
        found = gaps.gaps(self.root)
        self.assertEqual([g["subject"] for g in found if g["kind"] == "mock-stage"],
                         ALL_MOCKS)
        top = gaps.top_gap(self.root)
        self.assertEqual(top["kind"], "mock-stage")
        self.assertIn("admit-real --stage", top["move"])

    def test_section10_higher_pressure_kind_wins(self):
        # two kinds present at once: a parked piece (locally fine — its
        # refusal is settled history) and still-mock stages. The mock
        # stages must win the top line; the parked gap refuses to lead.
        self.park_the_atom()
        kinds = [g["kind"] for g in gaps.gaps(self.root)]
        self.assertIn("parked-piece", kinds)
        self.assertIn("mock-stage", kinds)
        self.assertLess(kinds.index("mock-stage"), kinds.index("parked-piece"))
        self.assertEqual(gaps.top_gap(self.root)["kind"], "mock-stage")

        # the moment every stage is admitted real, the parked piece IS the
        # top gap — same field, new highest pressure
        admit_all_real(self.root)
        top = gaps.top_gap(self.root)
        self.assertEqual(top["kind"], "parked-piece")
        self.assertEqual(top["subject"], "atom.gaps-00.v0")
        self.assertIn("reject_no_value", top["why"])
        self.assertIn("amend the atom", top["move"])

    def test_clean_field_has_no_gaps(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 0)
        admit_all_real(self.root)
        self.assertEqual(gaps.gaps(self.root), [])
        self.assertIsNone(gaps.top_gap(self.root))

    def test_organ_kinds_idle_before_dormant(self):
        # a real census fixture, no mocking: two organs in the temp repo —
        # a writer that is wired (entrypoint) but has never landed a word
        # on the record, and a file nothing references at all
        admit_all_real(self.root)
        (self.root / "atoms" / "atom.gaps-00.v0.json").unlink()
        organ_dir = Path(self.tmp) / "loop"
        organ_dir.mkdir()
        (organ_dir / "idle.py").write_text(
            'if __name__ == "__main__":\n    print("append_line stub")\n',
            encoding="utf-8")
        (organ_dir / "dead.py").write_text("x = 1\n", encoding="utf-8")
        found = gaps.gaps(self.root)
        self.assertEqual([(g["kind"], g["subject"]) for g in found],
                         [("idle-organ", "loop/idle.py"),
                          ("dormant-organ", "loop/dead.py")])
        self.assertIn("bdo", found[1]["move"])  # the cut stays the owner's

    def test_drift_kind_renders_with_move(self):
        admit_all_real(self.root)
        (self.root / "atoms" / "atom.gaps-00.v0.json").unlink()
        with mock.patch.object(gaps, "registered_surfaces",
                               return_value={"github-issues": {}}), \
             mock.patch.object(gaps, "drift", return_value=["a1", "a2"]):
            top = gaps.top_gap(self.root)
        self.assertEqual(top["kind"], "surface-drift")
        self.assertEqual(top["subject"], "github-issues")
        self.assertIn("2 act(s)", top["why"])
        self.assertIn("loop.reflect", top["move"])

    # -- the surfaces -----------------------------------------------------

    def hook_text(self):
        out = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO("not json")), \
             contextlib.redirect_stdout(out):
            self.assertEqual(summon.main(["--root", str(self.root), "--hook"]), 0)
        return out.getvalue()

    def test_hook_hands_the_top_gap(self):
        text = self.hook_text()
        self.assertIn("the next gap (mock-stage)", text)
        self.assertIn("the move:", text)
        self.assertIn("python -m loop.gaps", text)

    def test_hook_silent_on_a_clean_field(self):
        admit_all_real(self.root)
        (self.root / "atoms" / "atom.gaps-00.v0.json").unlink()
        self.assertNotIn("the next gap", self.hook_text())

    def test_hook_fail_open_on_a_broken_root(self):
        # a missing root is an absence, not a field of mock stages: the
        # hook stays silent and exits 0 (it runs in repos that are not
        # this one)
        self.root = Path(self.tmp) / "nowhere" / ".ai-native"
        self.assertEqual(gaps.gaps(self.root), [])
        self.assertEqual(self.hook_text(), "")

    def test_cli_result_lines(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(gaps.main(["--root", str(self.root)]), 0)
        self.assertIn("result: report —", out.getvalue())
        self.assertIn("gap: mock-stage —", out.getvalue())

        admit_all_real(self.root)
        (self.root / "atoms" / "atom.gaps-00.v0.json").unlink()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(gaps.main(["--root", str(self.root)]), 0)
        self.assertIn("result: done —", out.getvalue())

    def test_the_fold_writes_nothing(self):
        self.park_the_atom()
        before = log_bytes(self.root)
        gaps.gaps(self.root)
        gaps.top_gap(self.root)
        self.assertEqual(log_bytes(self.root), before)


if __name__ == "__main__":
    unittest.main()
