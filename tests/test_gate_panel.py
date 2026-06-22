"""Done-line 0143: the gate panel — a share of runs judge with ALL models and
compile.

bdo's direction (the impact half of the gate economy): a percentage of runs fan
out to all models in parallel, each its own stream, and compile at the end —
generating per-snapshot model comparisons naturally. His rule: unanimous-or-
escalate (a unanimous room advances; any split, or any failed stream, escalates
to bdo — the split is the signal, never papered into a verdict) at ~25%.

The §10 teeth, with an injected fake runner (no live spawn):
  - a unanimous panel compiles to the shared verdict;
  - a split panel escalates with NO verdict (a constant compile could not tell a
    split from a consensus);
  - a panel with a failed stream escalates (unanimity unconfirmable);
  - the rate bound holds (0 never panels, 1 always);
  - the snapshot-comparison fold groups by atom and flags agreement vs split.
"""

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import runs as runs_mod

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen_panel", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


class _Proc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


def _envelope(verdict, usd=0.01):
    sentinel = json.dumps({"verdict": verdict, "reason": "judged"})
    return json.dumps({"type": "result", "is_error": False, "num_turns": 1,
                       "result": "reasoning\nVERDICT " + sentinel,
                       "total_cost_usd": usd,
                       "usage": {"input_tokens": 10, "output_tokens": 5}})


def _runner_by_model(verdict_for_model):
    """A fake runner that returns a per-model verdict, keyed off the --model arg
    in the command. `verdict_for_model` maps model id -> verdict, or to the
    sentinel 'FAIL' to simulate a stream that returns no parseable verdict."""
    def runner(cmd, **kw):
        m = cmd[cmd.index("--model") + 1]
        v = verdict_for_model.get(m, "accept")
        if v == "FAIL":
            return _Proc(stdout=json.dumps({"type": "result", "num_turns": 0,
                                            "result": ""}), returncode=0)
        return _Proc(stdout=_envelope(v))
    return runner


class PanelSelection(unittest.TestCase):
    def test_rate_bounds(self):
        self.assertFalse(gate.should_panel(rate=0))
        self.assertTrue(gate.should_panel(rate=1))


class PanelFanOutAndCompile(unittest.TestCase):
    def setUp(self):
        self.pool = ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5"]

    def _trace_cleanup(self, results):
        # run_panel writes a trace per successful stream; nothing to clean for
        # FAIL streams (no verdict) — but the success ones wrote files; leave
        # them in the temp dir (gitignored), harmless.
        pass

    def test_unanimous_panel_compiles_to_the_shared_verdict(self):
        runner = _runner_by_model({m: "accept" for m in self.pool})
        results = gate.run_panel("p", "atom.x.v0", "value-gate.claude.v1",
                                 pool=self.pool, runner=runner)
        self.assertEqual(len(results), 3)
        decision, verdict, detail = gate.compile_panel(results)
        self.assertEqual(decision, "unanimous")
        self.assertEqual(verdict, "accept")

    def test_split_panel_escalates_with_no_verdict(self):
        runner = _runner_by_model({"claude-opus-4-8": "accept",
                                   "claude-sonnet-4-6": "accept",
                                   "claude-haiku-4-5": "reject_no_value"})
        results = gate.run_panel("p", "atom.y.v0", "value-gate.claude.v1",
                                 pool=self.pool, runner=runner)
        decision, verdict, detail = gate.compile_panel(results)
        self.assertEqual(decision, "escalate")
        self.assertIsNone(verdict)
        self.assertIn("split", detail)

    def test_failed_stream_escalates_unconfirmable(self):
        runner = _runner_by_model({"claude-opus-4-8": "accept",
                                   "claude-sonnet-4-6": "accept",
                                   "claude-haiku-4-5": "FAIL"})
        results = gate.run_panel("p", "atom.z.v0", "value-gate.claude.v1",
                                 pool=self.pool, runner=runner)
        decision, verdict, detail = gate.compile_panel(results)
        self.assertEqual(decision, "escalate")
        self.assertIsNone(verdict)
        self.assertIn("unconfirmable", detail)

    def test_compile_is_not_constant(self):
        """A unanimous and a split room must NOT compile alike."""
        u = gate.compile_panel([{"model": "a", "verdict": "accept", "ok": True},
                                {"model": "b", "verdict": "accept", "ok": True}])
        s = gate.compile_panel([{"model": "a", "verdict": "accept", "ok": True},
                                {"model": "b", "verdict": "amend", "ok": True}])
        self.assertEqual(u[0], "unanimous")
        self.assertEqual(s[0], "escalate")


class SnapshotComparisonFold(unittest.TestCase):
    def _run(self, atom, model, verdict, usd=0.01):
        return {"atom": atom, "model": model, "verdict": verdict,
                "cost": {"usd": usd}, "standing": "moved"}

    def test_groups_by_atom_and_flags_agreement(self):
        events = [self._run("atom.a", "opus", "accept"),
                  self._run("atom.a", "haiku", "accept"),
                  self._run("atom.b", "opus", "accept"),
                  self._run("atom.b", "haiku", "reject_no_value")]
        cmp = {c["atom"]: c for c in runs_mod.snapshot_comparisons(events)}
        self.assertTrue(cmp["atom.a"]["agreed"])
        self.assertFalse(cmp["atom.b"]["agreed"])  # the split surfaces

    def test_single_model_atom_is_not_a_comparison(self):
        events = [self._run("atom.solo", "opus", "accept")]
        self.assertEqual(runs_mod.snapshot_comparisons(events), [])


class RecordCarriesAtomAndVerdict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / ".ai-native"
        (self.root / "log").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_then_comparison_fold(self):
        for m, v in [("opus", "accept"), ("haiku", "reject_no_value")]:
            runs_mod.record(self.root, kind="gate-judgment", by="t",
                            moved={"advanced": 1}, model=m,
                            cost={"usd": 0.02}, atom="atom.panel.v0", verdict=v)
        d = runs_mod.runs(self.root)
        cmp = d["snapshot_comparisons"]
        self.assertEqual(len(cmp), 1)
        self.assertEqual(cmp[0]["atom"], "atom.panel.v0")
        self.assertFalse(cmp[0]["agreed"])


if __name__ == "__main__":
    unittest.main()
