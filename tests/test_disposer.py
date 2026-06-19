"""Done-line 0091: the slow loop's bounded auto-admit fence — bdo's chosen
disposition (2026-06-16) for the proposer's open seam (done-line 0074). The
disposer (`loop/disposer.py`) is the outside the proposer left open, wired to
bdo's standing fence.

The §10 bar: a proposal that is in-fence on one dial and out-of-fence on
another must NOT self-admit — one breached key escalates the whole proposal.
Locally fine (a heating step within budget) and locally fine (a heating step
within inflight) do not compose into a license to leave the fence on a third
dial. The disposer also never signs bdo's name and never lets the proposer sign
its own line: an auto-admitted setpoint is the loop executing the fence, citing
it as `authorized_by`.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import disposer, orchestrate, reconcile

BASE = {"step_budget_per_tick": 3, "max_inflight_atoms": 8, "human_queue_cap": 2}


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    return root


def _setpoint(value):
    return {"id": "adm.sp.test", "type": "setpoint", "value": value, "by": "bdo"}


def _state(current, proposed, because="caused by the field"):
    """A slowloop() result with a proposal we control, so the disposer's logic
    is exercised independent of the pressure machinery the proposer folds."""
    deltas = {k: proposed[k] - current[k] for k in proposed if proposed[k] != current[k]}
    return {
        "setpoint": _setpoint(current),
        "signals": {},
        "proposal": {"current": current, "proposed": proposed, "deltas": deltas,
                     "change": bool(deltas), "because": [because]},
    }


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _setpoints_on_log(self):
        fold = reconcile.Fold(self.root)
        return [a for a in fold.admissions if a.get("type") == "setpoint"]


class TestEvaluateTeeth(_Temp):
    """The decision, pure — no log needed."""

    def _fence(self, bounds):
        return {"type": disposer.FENCE_TYPE, "bounds": bounds, "by": "bdo"}

    def test_one_breached_key_escalates_the_whole_proposal(self):
        # heating step_budget 3->4 is in fence [2,5]; heating inflight 8->20 is
        # past its ceiling 12. The §10 case: the in-fence key must NOT carry the
        # out-of-fence one. The whole proposal escalates.
        f = self._fence({"step_budget_per_tick": [2, 5], "max_inflight_atoms": [4, 12]})
        d = disposer.evaluate(f, BASE, {**BASE, "step_budget_per_tick": 4,
                                        "max_inflight_atoms": 20})
        self.assertEqual(d["verdict"], "escalate")
        breached = [k for k, in_f, _ in d["reasons"] if not in_f]
        self.assertEqual(breached, ["max_inflight_atoms"])

    def test_unnamed_key_escalates(self):
        # the fence authorizes only what it names (absence is information)
        f = self._fence({"step_budget_per_tick": [2, 5]})
        d = disposer.evaluate(f, BASE, {**BASE, "max_inflight_atoms": 10})
        self.assertEqual(d["verdict"], "escalate")

    def test_heating_capped_at_ceiling(self):
        f = self._fence({"step_budget_per_tick": [2, 5]})
        at = disposer.evaluate(f, BASE, {**BASE, "step_budget_per_tick": 5})
        self.assertEqual(at["verdict"], "admit", "heating to the ceiling self-admits")
        past = disposer.evaluate(f, BASE, {**BASE, "step_budget_per_tick": 6})
        self.assertEqual(past["verdict"], "escalate", "one past the ceiling escalates")

    def test_cooling_always_admits_even_below_floor(self):
        # cooling is the safe direction; bdo: always allowed, even under lo
        f = self._fence({"step_budget_per_tick": [2, 5]})
        d = disposer.evaluate(f, BASE, {**BASE, "step_budget_per_tick": 1})
        self.assertEqual(d["verdict"], "admit")
        self.assertTrue(all(in_f for _, in_f, _ in d["reasons"]))

    def test_no_change_is_noop(self):
        f = self._fence({"step_budget_per_tick": [2, 5]})
        self.assertEqual(disposer.evaluate(f, BASE, dict(BASE))["verdict"], "noop")

    def test_no_fence_escalates_a_change(self):
        d = disposer.evaluate(None, BASE, {**BASE, "step_budget_per_tick": 4})
        self.assertEqual(d["verdict"], "escalate")


class TestAdmitAndReadFence(_Temp):
    def test_admit_refuses_unsigned(self):
        adm, err = disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 5]}, "")
        self.assertIsNone(adm)
        self.assertIn("signed", err)

    def test_admit_refuses_unknown_dial_and_bad_range(self):
        self.assertIsNone(disposer.admit_fence(self.root, {"nope": [1, 2]}, "bdo")[0])
        self.assertIsNone(disposer.admit_fence(self.root, {"step_budget_per_tick": [5, 2]}, "bdo")[0])
        self.assertIsNone(disposer.admit_fence(self.root, {}, "bdo")[0])

    def test_read_fence_takes_the_latest(self):
        disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 4]}, "bdo")
        disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 6]}, "bdo")
        f = disposer.read_fence(reconcile.Fold(self.root).admissions)
        self.assertEqual(f["bounds"]["step_budget_per_tick"], [2, 6])

    def test_read_fence_none_when_undrawn(self):
        self.assertIsNone(disposer.read_fence(reconcile.Fold(self.root).admissions))


class TestDispose(_Temp):
    """The disposition writes (or refuses to write) on the log itself."""

    def test_in_fence_proposal_self_admits_citing_the_fence(self):
        f, _ = disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 5]}, "bdo")
        state = _state(BASE, {**BASE, "step_budget_per_tick": 4})
        with mock.patch.object(disposer, "slowloop", return_value=state):
            out = disposer.dispose(self.root, hour=9)
        self.assertEqual(out["verdict"], "admit")
        sps = self._setpoints_on_log()
        self.assertEqual(len(sps), 1, "exactly one setpoint was self-admitted")
        sp = sps[0]
        self.assertEqual(sp["value"]["step_budget_per_tick"], 4)
        self.assertEqual(sp["authorized_by"], f["id"],
                         "the auto-admitted dial cites bdo's fence as its authorization")
        self.assertEqual(sp["by"], disposer.DISPOSER)
        self.assertNotEqual(sp["by"], "bdo", "the loop never signs bdo's name")
        self.assertIn("because", sp, "the auto-admitted change carries its cause")

    def test_out_of_fence_proposal_writes_nothing(self):
        disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 5]}, "bdo")
        state = _state(BASE, {**BASE, "step_budget_per_tick": 6})  # past ceiling
        with mock.patch.object(disposer, "slowloop", return_value=state):
            out = disposer.dispose(self.root, hour=9)
        self.assertEqual(out["verdict"], "escalate")
        self.assertEqual(self._setpoints_on_log(), [],
                         "an out-of-fence proposal must not move the dial")

    def test_inert_without_a_fence(self):
        state = _state(BASE, {**BASE, "step_budget_per_tick": 4})
        with mock.patch.object(disposer, "slowloop", return_value=state):
            out = disposer.dispose(self.root, hour=9)
        self.assertEqual(out["verdict"], "escalate")
        self.assertEqual(self._setpoints_on_log(), [],
                         "no fence drawn: the disposer is inert")

    def test_noop_when_proposer_holds(self):
        disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 5]}, "bdo")
        state = _state(BASE, dict(BASE))  # no change
        with mock.patch.object(disposer, "slowloop", return_value=state):
            out = disposer.dispose(self.root, hour=9)
        self.assertEqual(out["verdict"], "noop")
        self.assertEqual(self._setpoints_on_log(), [])

    def test_disposed_setpoint_reads_back_as_the_dial(self):
        # the auto-admitted record is a real setpoint the fast loop will read
        disposer.admit_fence(self.root, {"step_budget_per_tick": [2, 5]}, "bdo")
        state = _state(BASE, {**BASE, "step_budget_per_tick": 4})
        with mock.patch.object(disposer, "slowloop", return_value=state):
            disposer.dispose(self.root, hour=9)
        sp = orchestrate.read_setpoint(reconcile.Fold(self.root).admissions)
        self.assertIsNotNone(sp)
        self.assertEqual(sp["value"]["step_budget_per_tick"], 4)


if __name__ == "__main__":
    unittest.main()
