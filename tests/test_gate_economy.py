"""Done-line 0142: the gate randomizes its model and the run ledger folds cost
by model.

bdo's direction after the rail fix: instead of pinning one model, draw one at
random per run, record the model and its cost, and let an audit compare cost vs
impact — cost-only first (impact deferred, named, not faked), pool = all three,
surfaced through the run/sourcing stats (loop.runs), not a bespoke ledger.

The §10 teeth:
  - the model picker draws ONLY from the pool, and a pin overrides the draw;
  - the cost fold groups cost + runs by model, and a run that carried NO cost is
    counted as UNPRICED, never as $0 (a constant/fabricated fold could not tell
    a priced run from an unpriced one, nor opus's cost from haiku's);
  - record() writes model + cost onto the run event, and runs() surfaces the
    per-model economy.
"""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import runs as runs_mod

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen_econ", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


class ModelPicker(unittest.TestCase):
    def test_draw_stays_within_pool(self):
        pool = ["m-a", "m-b", "m-c"]
        seen = {gate.pick_model(pool=pool, pin=None) for _ in range(200)}
        self.assertTrue(seen)
        self.assertTrue(seen.issubset(set(pool)))

    def test_pin_overrides_the_draw(self):
        pool = ["m-a", "m-b", "m-c"]
        self.assertEqual(gate.pick_model(pool=pool, pin="m-pinned"), "m-pinned")

    def test_default_pool_is_the_three_and_excludes_the_opus_alias(self):
        self.assertEqual(len(gate.GATE_MODEL_POOL), 3)
        self.assertNotIn("opus", gate.GATE_MODEL_POOL)


def _run(model, usd, standing="moved"):
    """A folded run dict in the shape _from_event emits."""
    cost = None if usd is None else {"usd": usd, "input_tokens": 10, "output_tokens": 5}
    return {"model": model, "cost": cost, "standing": standing}


class CostFold(unittest.TestCase):
    def test_groups_cost_and_runs_by_model(self):
        events = [_run("opus", 0.08), _run("opus", 0.10),
                  _run("haiku", 0.003), _run("sonnet", 0.015)]
        econ = {b["model"]: b for b in runs_mod.model_economy(events)}
        self.assertEqual(econ["opus"]["runs"], 2)
        self.assertAlmostEqual(econ["opus"]["total_usd"], 0.18, places=6)
        self.assertAlmostEqual(econ["opus"]["avg_usd"], 0.09, places=6)
        self.assertAlmostEqual(econ["haiku"]["avg_usd"], 0.003, places=6)
        # not a constant: opus and haiku do not share an average
        self.assertNotEqual(econ["opus"]["avg_usd"], econ["haiku"]["avg_usd"])

    def test_unpriced_run_is_unpriced_not_zero(self):
        events = [_run("haiku", None), _run("haiku", 0.004)]
        b = runs_mod.model_economy(events)[0]
        self.assertEqual(b["runs"], 2)
        self.assertEqual(b["unpriced_runs"], 1)
        self.assertEqual(b["priced_runs"], 1)
        # the average is over the ONE priced run — the unpriced one is not a $0
        self.assertAlmostEqual(b["avg_usd"], 0.004, places=6)

    def test_all_unpriced_has_no_average(self):
        b = runs_mod.model_economy([_run("m", None), _run("m", None)])[0]
        self.assertIsNone(b["avg_usd"])
        self.assertEqual(b["total_usd"], 0)
        self.assertEqual(b["priced_runs"], 0)

    def test_impact_is_deferred_not_fabricated(self):
        b = runs_mod.model_economy([_run("m", 0.01)])[0]
        self.assertEqual(b["impact"], "deferred")


class RecordAndFold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / ".ai-native"
        (self.root / "log").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_writes_model_and_cost_then_fold_surfaces_it(self):
        runs_mod.record(self.root, kind="gate-judgment", by="t", moved={"advanced": 1},
                        model="claude-haiku-4-5",
                        cost={"usd": 0.003, "input_tokens": 100, "output_tokens": 20})
        d = runs_mod.runs(self.root)
        econ = {b["model"]: b for b in d["model_economy"]}
        self.assertIn("claude-haiku-4-5", econ)
        self.assertAlmostEqual(econ["claude-haiku-4-5"]["total_usd"], 0.003, places=6)
        self.assertEqual(econ["claude-haiku-4-5"]["output_tokens"], 20)


if __name__ == "__main__":
    unittest.main()
