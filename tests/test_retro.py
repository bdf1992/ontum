"""Tests for the retrospective fold against done-line 0098: the loop reads
its own history for recurring patterns.

The §10 teeth: a churn pattern planted in a fixture log (an atom carrying
two negating verdicts before it could land) MUST be caught and its finding
MUST cite the planted receipt ids — a fabricated/constant classifier has no
real record to point at and fails here. A clean fixture surfaces nothing
(and if it never could, the detector is not doing its job). The dead-valve
fires only on a meaningful, one-sided run. The fold writes nothing."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import retro


def write_log(root, *, receipts=(), admissions=(), events=()):
    """Lay down a minimal .ai-native fixture: the three log files plus the
    empty atoms/epics dirs digest() walks when retro reuses it."""
    log = root / "log"
    log.mkdir(parents=True)
    (root / "atoms").mkdir()
    (root / "epics").mkdir()
    for name, rows in (("receipts.jsonl", receipts),
                       ("admissions.jsonl", admissions),
                       ("events.jsonl", events)):
        (log / name).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return root


def receipt(rid, atom_id, verdict, node="some-gate.v1", reason="because."):
    return {"id": rid, "artifact_id": atom_id, "artifact_hash": f"sha256:{rid}",
            "verdict": verdict, "node": node, "reason": reason,
            "ts": "2026-06-10T00:00:00Z", "next_suggested_event": None}


def tick(i, mode):
    return {"id": f"adm.tick.{i:04d}", "type": "tick", "tick": i, "mode": mode,
            "budget_spent": 1, "deferred": [], "pressure": {"human_backlog": 0},
            "ts": "2026-06-10T00:00:00Z"}


class TestChurn(unittest.TestCase):
    def test_repeated_negating_verdicts_are_caught_and_cited(self):
        """§10: an atom sent back twice before landing is churn, and the
        finding points at the real receipt ids — the line a constant
        classifier cannot fake."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.aaa", "atom.flaky.v0", "send_back"),
                receipt("rcp.bbb", "atom.flaky.v0", "amend"),
                receipt("rcp.ccc", "atom.flaky.v0", "landed"),
                receipt("rcp.ddd", "atom.clean.v0", "accept"),
            ])
            found = retro.churn_findings(retro.Fold(root))
            subjects = {f["subject"] for f in found}
            self.assertIn("atom.flaky", subjects)
            self.assertNotIn("atom.clean", subjects)  # one negating ≠ churn
            flaky = next(f for f in found if f["subject"] == "atom.flaky")
            blob = " ".join(flaky["evidence"])
            self.assertIn("rcp.aaa", blob)  # cites the real records (teeth)
            self.assertIn("rcp.bbb", blob)
            self.assertTrue(flaky["evidence"], "a finding must carry evidence")

    def test_multiple_versions_are_churn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.v0", "atom.redo.v0", "accept"),
                receipt("rcp.v1", "atom.redo.v1", "accept"),
            ])
            found = retro.churn_findings(retro.Fold(root))
            self.assertEqual([f["subject"] for f in found], ["atom.redo"])

    def test_clean_history_surfaces_no_churn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.1", "atom.a.v0", "accept"),
                receipt("rcp.2", "atom.b.v0", "landed"),
            ])
            self.assertEqual(retro.churn_findings(retro.Fold(root)), [])


class TestDeadValve(unittest.TestCase):
    def test_one_sided_run_over_sample_fires(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native",
                             admissions=[tick(i, "heat") for i in range(1, 9)])
            found = retro.dead_valve_findings(retro.Fold(root))
            self.assertEqual([f["subject"] for f in found], ["orchestrate:cool"])
            self.assertIn("adm.tick.0001", " ".join(found[0]["evidence"]))

    def test_a_mixed_run_has_no_dead_valve(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [tick(i, "heat") for i in range(1, 6)] + \
                   [tick(i, "cool") for i in range(6, 9)]
            root = write_log(Path(tmp) / ".ai-native", admissions=rows)
            self.assertEqual(retro.dead_valve_findings(retro.Fold(root)), [])

    def test_below_sample_is_not_yet_a_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native",
                             admissions=[tick(i, "heat") for i in range(1, 4)])
            self.assertEqual(retro.dead_valve_findings(retro.Fold(root)), [])


class TestFoldContract(unittest.TestCase):
    def test_clean_field_reports_done_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.1", "atom.a.v0", "accept")],
                admissions=[tick(i, "heat") for i in range(1, 4)])
            before = (root / "log" / "receipts.jsonl").read_bytes()
            d = retro.retro(root)
            self.assertEqual(d["findings"], [])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = retro.main(["--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("result: done", buf.getvalue())
            self.assertEqual((root / "log" / "receipts.jsonl").read_bytes(),
                             before)  # read-only

    def test_every_finding_carries_a_move_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.a", "atom.x.v0", "send_back"),
                receipt("rcp.b", "atom.x.v0", "amend")],
                admissions=[tick(i, "heat") for i in range(1, 9)])
            d = retro.retro(root)
            self.assertTrue(d["findings"])
            for f in d["findings"]:
                self.assertTrue(f["evidence"], f"{f['subject']} has no evidence")
                self.assertTrue(f["move"], f"{f['subject']} has no move")


if __name__ == "__main__":
    unittest.main()
