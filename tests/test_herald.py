"""Tests for the herald against epic.landing-throughput-response: agents are
an open set, so registration is a fold over logged introductions and
reputation is distributed value earned forward along the log's provenance
edges — never a table, never an assertion.

The §10 teeth: standing must be RECOMPUTED from the log's records, not stored
or constant. A credential introduced with no acts reads 0 (the floor); a
witnessed positive act raises it; a witnessed refusal drives it negative; and
the no-launder test pins an exact computed value AND a never-acted zero in the
same fixture, so a stubbed-constant implementation can satisfy neither and
fails. The pen writes exactly one admission; the folds write nothing."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import herald, trust


def make_root(tmp):
    """A throwaway .ai-native root with the three empty log files."""
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / name).write_text("", encoding="utf-8")
    return root


def write_log(root, *, receipts=(), events=(), admissions=()):
    for name, rows in (("receipts.jsonl", receipts),
                       ("events.jsonl", events),
                       ("admissions.jsonl", admissions)):
        (root / "log" / name).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def act(rid, credential, verdict="accept", node=None):
    """A receipt attributable to `credential` as the acting node."""
    return {"id": rid, "node": node or credential, "from_node": credential,
            "artifact_id": "atom.work.v0", "artifact_hash": f"sha256:{rid}",
            "verdict": verdict, "reason": "because.", "ts": "2026-06-10T00:00:00Z"}


class TestFloorStart(unittest.TestCase):
    def test_fresh_credential_is_zero_standing_at_the_trust_floor(self):
        """A just-introduced agent has zero privilege: standing 0 and rank ==
        the trust ladder's floor rung, read from loop.trust (not invented)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            adm = herald.introduce(root, "skill.herald", "Gawain",
                                   "wandering-knight", by="bdo")
            cred = adm["credential"]
            self.assertEqual(adm["rank"], trust.CAPABILITIES[0])  # the floor, from code
            reg = herald.roster(root)
            self.assertIn(cred, reg)
            self.assertEqual(reg[cred]["rank"], trust.CAPABILITIES[0])
            rep = herald.reputation(root)
            self.assertEqual(rep["credentials"][cred]["standing"], 0)


class TestEarnedForward(unittest.TestCase):
    def test_standing_rises_only_with_a_real_act_on_the_log(self):
        """Standing derives ONLY from log records: one witnessed positive act
        lifts the acting credential; a credential that never acted stays 0."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            doer = herald.introduce(root, "skill.herald", "Doer",
                                    "field-agent", by="bdo")["credential"]
            idle = herald.introduce(root, "skill.herald", "Idle",
                                    "field-agent", by="bdo")["credential"]
            # only the existing admissions plus one positive act for `doer`
            adms = [json.loads(l) for l in
                    (root / "log" / "admissions.jsonl").read_text().splitlines() if l]
            write_log(root, admissions=adms,
                      receipts=[act("rcp.1", doer, "accept")])
            rep = herald.reputation(root)
            self.assertEqual(rep["credentials"][doer]["standing"], 1)
            self.assertEqual(rep["credentials"][doer]["exemplars"], ["rcp.1"])
            self.assertEqual(rep["credentials"][idle]["standing"], 0)  # never acted


class TestNotoriety(unittest.TestCase):
    def test_a_refusal_act_drives_standing_negative(self):
        """A witnessed refusal/violation attributed to the credential is a
        notoriety — standing goes below the floor."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            cred = herald.introduce(root, "skill.herald", "Mordred",
                                    "field-agent", by="bdo")["credential"]
            adms = [json.loads(l) for l in
                    (root / "log" / "admissions.jsonl").read_text().splitlines() if l]
            write_log(root, admissions=adms,
                      receipts=[act("rcp.bad", cred, "send_back")])
            rep = herald.reputation(root)
            self.assertEqual(rep["credentials"][cred]["notorieties"], ["rcp.bad"])
            self.assertEqual(rep["credentials"][cred]["standing"], -1)


class TestBadVoucherVisible(unittest.TestCase):
    def test_herald_meta_reputation_falls_when_its_agent_misbehaves(self):
        """A herald sits on its agents' provenance edge: the one whose agent
        accrues a notoriety carries a lower meta-reputation than the one whose
        agent earns an exemplar — a bad voucher is visible by construction."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            good = herald.introduce(root, "herald.good", "Galahad",
                                    "field-agent", by="bdo")["credential"]
            bad = herald.introduce(root, "herald.bad", "Mordred",
                                   "field-agent", by="bdo")["credential"]
            adms = [json.loads(l) for l in
                    (root / "log" / "admissions.jsonl").read_text().splitlines() if l]
            write_log(root, admissions=adms, receipts=[
                act("rcp.good", good, "accept"),
                act("rcp.bad", bad, "send_back"),
            ])
            heralds = herald.reputation(root)["heralds"]
            self.assertEqual(heralds["herald.good"]["meta"], 1)
            self.assertEqual(heralds["herald.bad"]["meta"], -1)
            self.assertLess(heralds["herald.bad"]["meta"],
                            heralds["herald.good"]["meta"])


class TestNoLaunder(unittest.TestCase):
    def test_standing_is_recomputed_from_records_not_faked(self):
        """§10 teeth: standing must equal exactly (exemplars - notorieties)
        recomputed from the log, while an unrelated credential reads 0 — no
        single constant can satisfy both, so a fabricated/stubbed standing
        fails here. Reputation cannot be laundered onto the record."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            earner = herald.introduce(root, "skill.herald", "Earner",
                                      "field-agent", by="bdo")["credential"]
            never = herald.introduce(root, "skill.herald", "Never",
                                     "field-agent", by="bdo")["credential"]
            adms = [json.loads(l) for l in
                    (root / "log" / "admissions.jsonl").read_text().splitlines() if l]
            # two exemplars, one notoriety => net standing must be exactly 1
            write_log(root, admissions=adms, receipts=[
                act("rcp.e1", earner, "accept"),
                act("rcp.e2", earner, "confirmed"),
                act("rcp.n1", earner, "amend"),
            ])
            rep = herald.reputation(root)["credentials"]
            self.assertEqual(rep[earner]["standing"], 1)        # computed, not constant
            self.assertEqual(len(rep[earner]["exemplars"]), 2)
            self.assertEqual(len(rep[earner]["notorieties"]), 1)
            self.assertEqual(rep[never]["standing"], 0)          # nothing earned, nothing shown
            # the evidence points at the real records (a constant cites nothing)
            self.assertEqual(set(rep[earner]["exemplars"]), {"rcp.e1", "rcp.e2"})
            self.assertEqual(rep[earner]["notorieties"], ["rcp.n1"])


class TestSupersede(unittest.TestCase):
    def test_a_later_introduction_supersedes_the_earlier(self):
        """History is superseded, never erased: a re-introduction citing the
        prior admission id replaces it in the roster."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            first = herald.introduce(root, "herald.a", "Percival",
                                     "squire", by="bdo")
            herald.introduce(root, "herald.b", "Percival", "knight",
                             by="bdo", supersedes=first["id"])
            reg = herald.roster(root)
            cred = herald.credential_for("Percival", "knight", "bdo")
            # same name+by but a new title => a distinct credential survives,
            # and the superseded first introduction is gone from the roster
            self.assertIn(cred, reg)
            self.assertEqual(reg[cred]["title"], "knight")
            self.assertNotIn(first["credential"], reg)


class TestPenAndFoldContract(unittest.TestCase):
    def test_pen_writes_exactly_one_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            herald.introduce(root, "skill.herald", "Lancelot", "knight", by="bdo")
            lines = [l for l in
                     (root / "log" / "admissions.jsonl").read_text().splitlines() if l]
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["type"], "herald_introduction")

    def test_folds_write_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            herald.introduce(root, "skill.herald", "Lancelot", "knight", by="bdo")
            before = (root / "log" / "admissions.jsonl").read_bytes()
            herald.roster(root)
            herald.reputation(root)
            self.assertEqual((root / "log" / "admissions.jsonl").read_bytes(), before)

    def test_introduce_refusal_rejects_blank_fields(self):
        self.assertIsNone(herald.introduce_refusal("h", "n", "t", "bdo"))
        self.assertIsNotNone(herald.introduce_refusal("", "n", "t", "bdo"))
        self.assertIsNotNone(herald.introduce_refusal("h", "  ", "t", "bdo"))

    def test_cli_introduce_then_report_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = herald.main(["introduce", "--root", str(root),
                                  "--herald", "skill.herald", "--name", "Kay",
                                  "--title", "seneschal", "--by", "bdo"])
            self.assertEqual(rc, 0)
            self.assertIn("result: done", buf.getvalue())
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = herald.main(["--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("result: report", buf.getvalue())

    def test_cli_introduce_refuses_blank_by(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = herald.main(["introduce", "--root", str(root),
                                  "--herald", "skill.herald", "--name", "X",
                                  "--title", "Y", "--by", "   "])
            self.assertEqual(rc, 2)
            self.assertIn("result: needs-you", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
