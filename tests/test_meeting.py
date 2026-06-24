"""Tests for the prepared owner-meeting agenda (done-line 0183).

The meeting is the root-cause fix for the owner-ask pile: one prepared,
ranked, budget-capped agenda instead of a per-report blind-create flood. The
§10 teeth here are the three claims the agenda must not be able to fake:

  - a *fresher* report's asks lead (rank is real, not insertion order);
  - the budget *cut* actually drops the over-budget tail to a deferred count
    (the "30 minutes" bounds the meeting — proven non-vacuous: the tail is
    non-empty and absent from `today`);
  - a *discharged* ask is gone from the agenda (surfaced is not answered, but
    discharged-with-a-cite is — the floor's third state, done-line 0065).

Pure fold exercised directly; the budget is admitted on the log and read back
(setpoints are admitted records, not literals — asserted over the log)."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import meeting, reconcile, reflect


def _report(stem, n_asks):
    items = "\n".join(f"{i}. **Ask {i}** in {stem}" for i in range(1, n_asks + 1))
    return f"# Report {stem}\n\n## needs-you\n\n{items}\n\n## End-state\n\n`report`.\n"


def make_root(tmp, reports):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / name).write_text("", encoding="utf-8")
    rdir = root / "reports"
    rdir.mkdir(parents=True)
    for stem, n in reports.items():
        (rdir / f"{stem}.md").write_text(_report(stem, n), encoding="utf-8")
    return root


class BudgetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, {"0100-a": 1})

    def test_default_is_safe_and_unadmitted(self):
        b = meeting.meeting_budget(reconcile.Fold(self.root))
        self.assertFalse(b["admitted"])
        self.assertEqual(b["per_ask_minutes"], meeting.DEFAULT_PER_ASK_MIN)
        self.assertEqual(b["above_fold"], 10)  # 30 // 3, "the thing you said"

    def test_admitted_budget_is_read_from_the_log(self):
        adm = meeting.set_budget(self.root, per_ask_minutes=10, total_minutes=20,
                                 by="test-bdo")
        self.assertIsNotNone(adm)
        # read back from the log, not the call's return — a fresh fold
        b = meeting.meeting_budget(reconcile.Fold(self.root))
        self.assertTrue(b["admitted"])
        self.assertEqual(b["above_fold"], 2)  # 20 // 10

    def test_a_nonpositive_budget_is_refused(self):
        self.assertIsNone(meeting.set_budget(self.root, 0, 30, by="test-bdo"))
        self.assertIsNone(meeting.set_budget(self.root, "x", 30, by="test-bdo"))


class RankTest(unittest.TestCase):
    def test_a_fresher_report_leads(self):
        # 0050 authored first on disk, 0120 is newer — newer must rank first.
        tmp = tempfile.mkdtemp()
        root = make_root(tmp, {"0050-old": 3, "0120-new": 1})
        data = meeting.agenda(root)
        order = [it["report_id"] for it in data["today"]]
        self.assertEqual(order[0], "0120-new")  # freshness beats item-count
        self.assertEqual(order[1], "0050-old")


class CutTest(unittest.TestCase):
    def test_budget_cut_drops_the_tail_to_deferred(self):
        tmp = tempfile.mkdtemp()
        root = make_root(tmp, {f"01{n:02d}-r": 1 for n in range(4)})  # 4 groups
        # a small budget so the cut is non-vacuous: 2 above the fold, 2 deferred
        meeting.set_budget(root, per_ask_minutes=10, total_minutes=20, by="test-bdo")
        data = meeting.agenda(root)
        self.assertEqual(len(data["today"]), 2)
        self.assertEqual(data["deferred_count"], 2)
        # the tail is genuinely absent from today (the bound bites)
        today_ids = {it["report_id"] for it in data["today"]}
        deferred_ids = {it["report_id"] for it in data["deferred"]}
        self.assertTrue(deferred_ids)
        self.assertFalse(today_ids & deferred_ids)
        # and today holds the two freshest (highest-numbered) reports
        self.assertEqual(today_ids, {"0103-r", "0102-r"})


class DischargeTest(unittest.TestCase):
    def test_a_discharged_ask_is_absent_from_the_agenda(self):
        tmp = tempfile.mkdtemp()
        root = make_root(tmp, {"0110-keep": 1, "0111-gone": 1})
        # the ask is on the agenda before discharge
        before = {it["report_id"] for it in meeting.agenda(root)["today"]}
        self.assertIn("0111-gone", before)
        # a real closing record to cite, then discharge that one group
        reconcile.append_line(root / "log" / "events.jsonl",
                              {"id": "evt.closed-it", "type": "noop"})
        gid = next(g["id"] for g in meeting.live_owner_asks(root)
                   if g["report_id"] == "0111-gone")
        adm, err = reflect.discharge_owner_ask(root, gid, ["evt.closed-it"],
                                               reason="closed by evt.closed-it",
                                               by="test-bdo")
        self.assertIsNone(err, err)
        after = {it["report_id"] for it in meeting.agenda(root)["today"]}
        self.assertNotIn("0111-gone", after)   # discharged -> gone
        self.assertIn("0110-keep", after)      # the other still parked


if __name__ == "__main__":
    unittest.main()
