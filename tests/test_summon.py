"""Tests for the summons surface against done-line 0008:
an atom awaiting an admitted-real node appears as a summons with the one
judge line that clears it; the owner's stamp never appears as a session
summons; a settled field summons nobody; hook mode survives garbage stdin
and a missing root and always exits 0; rendering writes nothing."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, orchestrate, reconcile, summon
from loop import temporal as T

SETPOINT = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}
L0_STAGE = "value-gate.mock.v0"
L0_REAL = "value-gate.claude.v1"
STAMP_STAGE = "owner-stamp.mock-bdo.v0"
STAMP_REAL = "owner-stamp.bdo.v1"


def make_atom(i):
    return {"atom": {
        "id": f"atom.summon-{i:02d}.v0",
        "story": {"text": f"As an AI, I need summons {i} to fire on its own, "
                          "because hand-routing is the gap every report names.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["test.summons"], "touches": [".ai-native/log"],
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
        (root / "atoms" / f"atom.summon-{i:02d}.v0.json").write_text(
            json.dumps(make_atom(i), indent=2), encoding="utf-8")
    return root


def log_bytes(root):
    out = {}
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        p = root / "log" / name
        out[name] = p.read_bytes() if p.exists() else None
    return out


class SummonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, 2)
        orchestrate.admit_setpoint(self.root, SETPOINT, by="test-bdo")
        node.admit_real(self.root, L0_STAGE, L0_REAL, by="test-bdo")
        node.admit_real(self.root, STAMP_STAGE, STAMP_REAL, by="test-bdo")
        orchestrate.orchestrate(self.root, quiet=True)  # seed; both park at L0

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def judge(self, atom_id, who=L0_REAL, verdict="accept", reason="test verdict"):
        return node.main(["judge", "--root", str(self.root), "--atom", atom_id,
                          "--node", who, "--verdict", verdict, "--reason", reason])

    def cli_text(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(summon.main(["--root", str(self.root), *argv]), 0)
        return out.getvalue()

    def hook_text(self, root, stdin_text):
        out = io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(out):
                self.assertEqual(summon.main(["--hook", "--root", str(root)]), 0)
        finally:
            sys.stdin = old_stdin
        return out.getvalue()

    def test_awaiting_atom_appears_with_the_judge_line(self):
        summons = summon.open_summons(self.root)
        self.assertEqual([s["node"] for s in summons], [L0_REAL, L0_REAL])
        text = self.cli_text()
        self.assertIn("summons: value-gate.claude.v1 — atom.summon-00.v0", text)
        self.assertIn("--node value-gate.claude.v1 --verdict", text)
        self.assertIn("result: report — 2 open summons", text)

    def test_owner_stamp_is_never_a_session_summons(self):
        self.judge("atom.summon-00.v0")               # L0 accepts atom 00
        orchestrate.orchestrate(self.root, quiet=True)  # it advances to the stamp
        summons = summon.open_summons(self.root)
        # atom 00 now awaits the owner's stamp: the inbox's item, nobody's summons
        self.assertEqual([(s["atom"]["id"], s["node"]) for s in summons],
                         [("atom.summon-01.v0", L0_REAL)])
        self.assertNotIn(STAMP_REAL, self.cli_text())

    def test_settled_field_summons_nobody(self):
        fresh = make_root(tempfile.mkdtemp(dir=self.tmp), 1)
        orchestrate.admit_setpoint(fresh, SETPOINT, by="test-bdo")
        self.assertEqual(orchestrate.orchestrate(fresh, quiet=True), 0)  # all mock
        self.assertEqual(summon.open_summons(fresh), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            summon.main(["--root", str(fresh)])
        self.assertIn("result: done — no open summons", out.getvalue())

    def test_hook_mode_briefs_without_blocking(self):
        text = self.hook_text(self.root, json.dumps(
            {"hook_event_name": "UserPromptSubmit", "prompt": "hi"}))
        self.assertIn("open summons in this repo", text)
        self.assertIn("summons: value-gate.claude.v1", text)

    def test_hook_mode_survives_garbage_and_missing_root(self):
        # garbage stdin: still exit 0, still briefs from the fold
        text = self.hook_text(self.root, "this is not json")
        self.assertIn("summons:", text)
        # missing root: silent, exit 0 — a broken hook never blocks the owner
        text = self.hook_text(Path(self.tmp) / "nowhere", "{}")
        self.assertEqual(text, "")

    # --- OP2 (done-line 0073): summon delivers outcome-pressure at wake ---

    def test_outcome_pressure_line_names_phase_and_focus(self):
        # over the real committed Causality probe-set: a morning hour leans
        # heat -> the unblocker; an evening hour leans cool -> a different,
        # closeable leaf. The line names the phase and *the focus the fold
        # computes* — not a literal id, which moves as probes resolve. The
        # contract under test is that the surface speaks the fold.
        real_root = REPO / ".ai-native"
        m_focus = T.temporal(hour=8)["temporal"]["focus"]
        e_focus = T.temporal(hour=20)["temporal"]["focus"]
        self.assertNotEqual(m_focus, e_focus, "the hour must re-emphasise differently")
        morning = summon.outcome_pressure_lines(real_root, hour=8)
        self.assertIsNotNone(morning)
        blob = "\n".join(morning)
        self.assertIn("outcome-pressure", blob)
        self.assertIn("phase build", blob)
        self.assertIn(f"focus {m_focus}", blob)
        evening = "\n".join(summon.outcome_pressure_lines(real_root, hour=20))
        self.assertIn(f"focus {e_focus}", evening)

    def test_outcome_pressure_silent_without_a_probeset(self):
        # fail-soft: a foreign/missing root has no probe-set -> no line, no crash
        self.assertIsNone(
            summon.outcome_pressure_lines(Path(self.tmp) / "elsewhere" / ".ai-native",
                                          hour=8))

    def test_hook_delivers_outcome_pressure_beside_the_gap(self):
        # the situation rides the same channel as the work-pressure; the hook
        # stays exit-0 (hook_text asserts it) and the line composes, not replaces
        text = self.hook_text(REPO / ".ai-native", "{}")
        self.assertIn("outcome-pressure", text)
        # names the fold's current top leverage (hour-independent), not a literal
        top = T.temporal(hour=8)["pressure"]["top_leverage"]["id"]
        self.assertIn(f"leverage-top {top}", text)
        self.assertIn("python -m loop.temporal", text)

    # --- done-line 0075: summon shows the slow loop's dial proposal ---

    def test_slowloop_lines_names_the_proposed_change(self):
        lines = summon.slowloop_lines(REPO / ".ai-native", hour=8)
        self.assertIsNotNone(lines)
        blob = "\n".join(lines)
        self.assertIn("slow-loop dial", blob)
        self.assertIn("step_budget_per_tick", blob)
        self.assertIn("→", blob)            # a concrete proposed change
        self.assertIn("because", blob)      # carrying its attribution

    def test_slowloop_line_marks_it_a_proposal_not_a_change(self):
        # propose != dispose, at the surface: it must not read as an instruction
        blob = "\n".join(summon.slowloop_lines(REPO / ".ai-native", hour=8))
        self.assertIn("a proposal, not a change", blob)
        self.assertIn("the outside admits it", blob)

    def test_slowloop_lines_silent_without_a_log(self):
        self.assertIsNone(
            summon.slowloop_lines(Path(self.tmp) / "nowhere" / ".ai-native", hour=8))

    def test_hook_shows_the_slowloop_proposal(self):
        text = self.hook_text(REPO / ".ai-native", "{}")
        self.assertIn("slow-loop dial", text)
        self.assertIn("python -m loop.slowloop", text)

    def test_hook_surfaces_the_owner_backlog_as_a_count(self):
        self.judge("atom.summon-00.v0")                 # L0 accepts atom 00
        orchestrate.orchestrate(self.root, quiet=True)  # it advances to the stamp
        text = self.hook_text(self.root, "{}")
        self.assertIn("1 item(s) await bdo's stamp", text)
        self.assertIn("python -m loop.node inbox", text)
        # the count is a pointer, not a briefing: no stamp briefing leaks here
        self.assertNotIn("atom.summon-00.v0", text.split("await bdo's stamp")[1])

    def test_mocked_stamp_surfaces_nothing_for_the_owner(self):
        fresh = make_root(tempfile.mkdtemp(dir=self.tmp), 1)
        orchestrate.admit_setpoint(fresh, SETPOINT, by="test-bdo")
        node.admit_real(fresh, L0_STAGE, L0_REAL, by="test-bdo")  # stamp stays mock
        orchestrate.orchestrate(fresh, quiet=True)
        self.assertNotIn("bdo's stamp", self.hook_text(fresh, "{}"))

    def test_rendering_writes_nothing(self):
        before = log_bytes(self.root)
        self.cli_text()
        self.hook_text(self.root, "{}")
        self.assertEqual(before, log_bytes(self.root))


if __name__ == "__main__":
    unittest.main()
