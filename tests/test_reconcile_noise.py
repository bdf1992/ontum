"""Tests for the noise make-over (epic.owner-harness; #628):
`loop/reconcile_noise.py`. The make-over reads the open noise surfaces against
the log and silences only what the record PROVES resolved — escalating the rest
to a named conclusion (#628).

The §10 bar is the point, and it is exercised three ways (each a locally-fine
artifact that *refuses to fit*):

  1. an owner-ask referencing an UNCONFIRMED arc — a real parked ask, fine on its
     own — stays escalating, never silenced;
  2. a gate-tracker whose atom was re-versioned so the live bytes carry no
     verdict — a real settled receipt on DEAD bytes, fine on its own — stays
     escalating;
  3. the teeth proper (`partition`): a reading that CLAIMS resolved but whose
     cite is not on the log is REFUSED, and the same refusal holds over the
     transformer's inference output (a hallucinated cite is refused exactly like
     a fabricated one, a genuine cite discharges).

The fence is INERT until bdo stamps it, and is bdo's alone (--by must be bdo).
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import reconcile, reconcile_noise


def make_root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "reports").mkdir(parents=True)
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / name).write_text("", encoding="utf-8")
    return root


def add_report(root, stem, asks):
    body = ["# Report " + stem, "", "## needs-you", ""]
    body += [f"{i}. {a}" for i, a in enumerate(asks, 1)]
    body += ["", "## End-state", "", "`report`."]
    (root / "reports" / f"{stem}.md").write_text("\n".join(body), encoding="utf-8")


def confirm_arc(root, epic_id, by="bdo"):
    adm = {"id": "adm." + reconcile.short_hash("arc_confirmed", epic_id, reconcile.now_ts()),
           "type": "arc_confirmed", "epic": epic_id, "enabled": True, "by": by,
           "ts": reconcile.now_ts()}
    reconcile.append_line(root / "log" / "admissions.jsonl", adm)
    return adm["id"]


def write_atom(root, atom_id):
    """A minimal atom; returns its content hash (the live bytes' identity)."""
    raw = json.dumps({"atom": {"id": atom_id, "story": {"text": "x"}}},
                     indent=2).encode("utf-8")
    (root / "atoms" / f"{atom_id}.json").write_bytes(raw)
    import hashlib
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def add_value_receipt(root, atom_id, ahash, verdict="accept",
                      node="value-gate.claude.v1"):
    rc = {"id": "rcp." + reconcile.short_hash(node, ahash, verdict, reconcile.now_ts()),
          "type": "receipt", "node": node, "artifact_id": atom_id,
          "artifact_hash": ahash, "verdict": verdict, "reason": "judged",
          "ts": reconcile.now_ts()}
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)
    return rc["id"]


class OwnerAskTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_confirmed_arc_makes_an_ask_silenceable_with_its_cite(self):
        add_report(self.root, "0100-ask", ["Confirm the arc `epic.demo`?"])
        cite = confirm_arc(self.root, "epic.demo")
        mo = reconcile_noise.make_over(self.root)
        self.assertEqual([r["kind"] for r in mo["silenceable"]], ["owner-ask"])
        self.assertEqual(mo["silenceable"][0]["cite"], cite)
        self.assertEqual(mo["escalating"], [])

    def test_unconfirmed_arc_stays_escalating(self):
        # locally fine — a real parked ask — but the record does not resolve it
        add_report(self.root, "0101-ask", ["Confirm the arc `epic.unconfirmed`?"])
        mo = reconcile_noise.make_over(self.root)
        self.assertEqual(mo["silenceable"], [])
        self.assertEqual([r["report_id"] for r in mo["escalating"]], ["0101-ask"])
        self.assertIn("#628", mo["escalating"][0]["reason"])


class GateTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_settled_verdict_on_live_bytes_is_silenceable_regardless_of_process(self):
        ahash = write_atom(self.root, "atom.demo.v0")
        cite = add_value_receipt(self.root, "atom.demo.v0", ahash, "accept")
        mo = reconcile_noise.make_over(self.root)
        gt = [r for r in mo["silenceable"] if r["kind"] == "gate-tracker"]
        self.assertEqual([r["subject"] for r in gt], ["atom.demo.v0"])
        self.assertEqual(gt[0]["cite"], cite)
        self.assertEqual(gt[0]["verdict"], "accept")

    def test_receipt_on_dead_bytes_stays_escalating(self):
        # a verdict landed on an OLD version; the atom was then edited (new bytes,
        # unjudged). The settled receipt is on dead bytes — the live tracker holds.
        write_atom(self.root, "atom.demo.v0")  # the CURRENT bytes
        add_value_receipt(self.root, "atom.demo.v0", "sha256:deadbeef", "accept")
        mo = reconcile_noise.make_over(self.root)
        self.assertEqual([r for r in mo["silenceable"]
                          if r["kind"] == "gate-tracker"], [])
        gt = [r for r in mo["escalating"] if r["kind"] == "gate-tracker"]
        self.assertEqual([r["subject"] for r in gt], ["atom.demo.v0"])
        self.assertIn("#628", gt[0]["reason"])


class TeethTest(unittest.TestCase):
    """The §10 teeth proper, directly and non-vacuously: a fabricated resolution
    is refused; a genuine one is silenceable."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)
        # one real record to cite
        reconcile.append_line(self.root / "log" / "admissions.jsonl",
                              {"id": "adm.real01", "type": "arc_confirmed",
                               "epic": "epic.x", "by": "bdo", "ts": "2026-06-22T00:00:00Z"})
        self.fold = reconcile.Fold(self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_real_cite_is_silenceable(self):
        rows = [{"kind": "owner-ask", "subject": "ask.real", "resolved": True,
                 "cite": "adm.real01", "reason": "ok"}]
        silenceable, escalating = reconcile_noise.partition(rows, self.fold)
        self.assertEqual(len(silenceable), 1)
        self.assertEqual(escalating, [])

    def test_a_fabricated_cite_is_refused_and_escalates(self):
        rows = [{"kind": "owner-ask", "subject": "ask.fake", "resolved": True,
                 "cite": "adm.ghost", "reason": "claiming closure with no evidence"}]
        silenceable, escalating = reconcile_noise.partition(rows, self.fold)
        self.assertEqual(silenceable, [])
        self.assertEqual(len(escalating), 1)
        self.assertTrue(escalating[0]["refused"])
        self.assertFalse(escalating[0]["resolved"])
        self.assertIn("REFUSED", escalating[0]["reason"])

    def test_a_missing_cite_is_refused(self):
        rows = [{"kind": "gate-tracker", "subject": "atom.y", "resolved": True,
                 "cite": None, "reason": "no cite"}]
        silenceable, escalating = reconcile_noise.partition(rows, self.fold)
        self.assertEqual(silenceable, [])
        self.assertTrue(escalating[0]["refused"])


class TransformerTest(unittest.TestCase):
    """Wave 2 — the teeth hold OVER inference output. A fake `infer` stands in
    for the gateway-backed completion (loop/ never reaches a model)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)
        add_report(self.root, "0200-free", ["Should we keep the basin lexicon live "
                                            "or freeze it?"])
        reconcile.append_line(self.root / "log" / "admissions.jsonl",
                              {"id": "adm.closer01", "type": "tag", "by": "bdo",
                               "ts": "2026-06-22T00:00:00Z"})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_infer_degrades_to_escalation_by_name(self):
        out = reconcile_noise.transform_unresolved(self.root, infer=None)
        self.assertEqual(len(out), 1)
        self.assertFalse(out[0]["resolved"])
        self.assertFalse(out[0]["transformed"])
        self.assertIn("inference unavailable", out[0]["reason"])

    def test_a_hallucinated_cite_is_refused(self):
        def hallucinate(prompt, fold):
            return {"resolved": True, "cite": "adm.doesnotexist",
                    "sound": "these asks were about lexicon governance"}
        out = reconcile_noise.transform_unresolved(self.root, infer=hallucinate)
        self.assertFalse(out[0]["resolved"])
        self.assertIn("NOT on the log", out[0]["reason"])
        # the synthesized sound is still surfaced — useful even when refused
        self.assertIn("lexicon governance", out[0]["sound"])

    def test_a_verified_cite_resolves_with_its_sound(self):
        def real(prompt, fold):
            return {"resolved": True, "cite": "adm.closer01",
                    "sound": "these asks were one lexicon-governance decision"}
        out = reconcile_noise.transform_unresolved(self.root, infer=real)
        self.assertTrue(out[0]["resolved"])
        self.assertEqual(out[0]["cite"], "adm.closer01")
        self.assertIn("verified on the log", out[0]["reason"])


class FenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)
        # two proven-resolved owner-asks
        for i, ep in enumerate(("epic.a", "epic.b")):
            add_report(self.root, f"030{i}-ask", [f"Confirm `{ep}`?"])
            confirm_arc(self.root, ep)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_inert_until_a_fence_is_drawn(self):
        p = reconcile_noise.plan(self.root)
        self.assertIsNone(p["fence"])
        self.assertEqual(p["authorized"], [])  # nothing self-silences
        self.assertEqual(len(p["held_for_cap"]), 2)  # proposed only

    def test_a_session_cannot_draw_the_fence(self):
        adm, err = reconcile_noise.admit_noise_fence(self.root, 10, by="claude")
        self.assertIsNone(adm)
        self.assertIn("bdo", err)

    def test_bdo_fence_authorizes_up_to_its_cap(self):
        adm, err = reconcile_noise.admit_noise_fence(self.root, 1, by="bdo")
        self.assertIsNone(err)
        p = reconcile_noise.plan(self.root)
        self.assertEqual(len(p["authorized"]), 1)   # capped
        self.assertEqual(len(p["held_for_cap"]), 1)  # overflow held, not dropped

    def test_withdrawn_fence_is_inert_again(self):
        reconcile_noise.admit_noise_fence(self.root, 10, by="bdo")
        reconcile_noise.admit_noise_fence(self.root, 0, by="bdo", enabled=False)
        p = reconcile_noise.plan(self.root)
        self.assertIsNone(p["fence"])
        self.assertEqual(p["authorized"], [])


class DigestLineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_useful_sound_names_what_resolved_and_what_remains(self):
        add_report(self.root, "0400-ok", ["Confirm `epic.ok`?"])
        confirm_arc(self.root, "epic.ok")
        add_report(self.root, "0401-no", ["Confirm `epic.pending`?"])
        line = reconcile_noise.make_over(self.root)["digest_line"]
        self.assertIn("reconciled 1 owner-ask", line)
        self.assertIn("genuinely still need you", line)
        self.assertIn("0401-no", line)


if __name__ == "__main__":
    unittest.main()
