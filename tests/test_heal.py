"""Tests for the healing fold against done-line 0111: the loop senses where
its own teeth bit too sharp — read-only, propose-only.

The §10 teeth are the discriminators, and each is a test:

- a stale-park (a refusal a later passing version superseded) is caught and
  cites the real receipt ids — the line a fabricated classifier cannot fake;
- a GENUINE open park (a refusal with no later passing version) is NOT read
  as stale (it is live work, gaps' job);
- a flapping gate (advanced an earlier version, negates the live one) is
  caught — but a gate that refuses a base CONSISTENTLY (never advanced one)
  is NOT flagged: a repeated correct refusal is backpressure, not an over-bite;
- an owner-override fires only when the owner's accept lands AFTER the gate's
  refusal; the normal pipeline (owner-stamp at stage 2, a later-stage gate
  refusing at stage 4-5) is NOT an override — the exact false positive the
  real log exposed during construction;
- the fold writes nothing.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import heal
from loop.reconcile import Fold


def write_log(root, *, receipts=()):
    """Lay down a minimal .ai-native fixture: the three log files plus the
    empty atoms/epics dirs digest() walks when heal reuses its split."""
    log = root / "log"
    log.mkdir(parents=True)
    (root / "atoms").mkdir()
    (root / "epics").mkdir()
    for name, rows in (("receipts.jsonl", receipts),
                       ("admissions.jsonl", ()),
                       ("events.jsonl", ())):
        (log / name).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return root


def receipt(rid, atom_id, verdict, node="value-confirm.claude.v1",
            ts="2026-06-10T00:00:00Z", reason="because."):
    return {"id": rid, "artifact_id": atom_id, "artifact_hash": f"sha256:{rid}",
            "verdict": verdict, "node": node, "reason": reason, "ts": ts,
            "next_suggested_event": None}


class TestStalePark(unittest.TestCase):
    def test_superseded_refusal_with_live_pass_is_caught_and_cited(self):
        """§10: a gate refused v0, the live v1 then passed the same gate — the
        bite is healed and only its surfacing is stale. The finding cites both
        real receipts (the line a constant classifier cannot fake)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.neg", "atom.thing.v0", "missed"),
                receipt("rcp.pass", "atom.thing.v1", "confirmed"),
            ])
            found = heal.stale_park_findings(Fold(root))
            subjects = {f["subject"] for f in found}
            self.assertIn("atom.thing.v0", subjects)
            f0 = next(f for f in found if f["subject"] == "atom.thing.v0")
            blob = " ".join(f0["evidence"])
            self.assertIn("rcp.neg", blob)
            self.assertIn("rcp.pass", blob)

    def test_genuine_open_park_is_not_stale(self):
        """The discriminator: a refusal with NO later passing version is a
        live park, never a stale one — heal must leave it for gaps."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.neg", "atom.thing.v0", "missed"),
            ])
            self.assertEqual(heal.stale_park_findings(Fold(root)), [])

    def test_live_version_still_negated_is_not_stale(self):
        """If the live version is itself still refused, the park is live, not
        stale — even though an older version exists."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.n0", "atom.thing.v0", "missed"),
                receipt("rcp.n1", "atom.thing.v1", "missed"),
            ])
            self.assertEqual(heal.stale_park_findings(Fold(root)), [])


class TestFlapping(unittest.TestCase):
    def test_advance_then_negate_live_is_caught(self):
        """A gate advanced v0 and refuses the live v1 — a current self-
        contradiction. Caught, citing both receipts."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.adv", "atom.thing.v0", "ready_for_spec",
                        node="handoff-gate.det.v1"),
                receipt("rcp.neg", "atom.thing.v1", "send_back",
                        node="handoff-gate.det.v1"),
            ])
            found = heal.flapping_findings(Fold(root))
            self.assertEqual(len(found), 1)
            blob = " ".join(found[0]["evidence"])
            self.assertIn("rcp.adv", blob)
            self.assertIn("rcp.neg", blob)

    def test_consistent_refusal_is_not_flagged(self):
        """The §10 teeth: a gate that refuses a base on every version (never
        advanced one) is consistent backpressure, NOT an over-bite."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.n0", "atom.bad.v0", "reject_no_value",
                        node="value-gate.claude.v1"),
                receipt("rcp.n1", "atom.bad.v1", "reject_no_value",
                        node="value-gate.claude.v1"),
            ])
            self.assertEqual(heal.flapping_findings(Fold(root)), [])

    def test_mock_gate_never_flaps(self):
        """A .mock gate has a fixed verdict — it cannot change its mind, so it
        is excluded from the flap detector."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.adv", "atom.thing.v0", "ready_for_spec",
                        node="handoff-gate.mock.v0"),
                receipt("rcp.neg", "atom.thing.v1", "send_back",
                        node="handoff-gate.mock.v0"),
            ])
            self.assertEqual(heal.flapping_findings(Fold(root)), [])


class TestOwnerOverride(unittest.TestCase):
    def test_owner_accept_after_refusal_is_an_override(self):
        """The owner stamped accept AFTER a real gate refused the same
        artifact — the override, caught and cited."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.neg", "atom.thing.v0", "reject_no_value",
                        node="value-gate.claude.v1", ts="2026-06-10T01:00:00Z"),
                receipt("rcp.owner", "atom.thing.v0", "accept",
                        node="owner-stamp.bdo.v1", ts="2026-06-10T02:00:00Z"),
            ])
            found = heal.owner_override_findings(Fold(root))
            self.assertEqual(len(found), 1)
            blob = " ".join(found[0]["evidence"])
            self.assertIn("rcp.neg", blob)
            self.assertIn("rcp.owner", blob)

    def test_owner_stamp_before_later_gate_refusal_is_not_override(self):
        """The exact false positive the real log exposed: owner-stamp is
        pipeline stage 2; a later-stage gate refusing at stage 4-5 lands AFTER
        the stamp. The owner advanced what he never saw refused — NOT an
        override. ts-ordering is the discriminator."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.owner", "atom.thing.v0", "accept",
                        node="owner-stamp.bdo.v1", ts="2026-06-10T01:00:00Z"),
                receipt("rcp.neg", "atom.thing.v0", "missed",
                        node="value-confirm.claude.v1", ts="2026-06-10T05:00:00Z"),
            ])
            self.assertEqual(heal.owner_override_findings(Fold(root)), [])

    def test_override_suppressed_when_gate_later_healed_a_new_hash(self):
        """§10, the herald fixture (real log): a gate refused an OLD hash of an
        atom edited IN PLACE (same .v0 id), the SAME gate later ADVANCED the
        NEW hash, and the owner-stamp (arc-confirm) accepted. Identity is the
        content hash, not the .vN string — so the gate relented and this is a
        healed bite, never 'bdo overruled a tooth'. Fails on the id-string
        reading; passes once the detector is hash-aware."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                {**receipt("rcp.neg", "atom.h.v0", "send_back",
                           node="handoff-gate.det.v1", ts="2026-06-18T00:00:00Z"),
                 "artifact_hash": "sha256:OLDBYTES"},
                {**receipt("rcp.pass", "atom.h.v0", "ready_for_spec",
                           node="handoff-gate.det.v1", ts="2026-06-19T00:00:00Z"),
                 "artifact_hash": "sha256:NEWBYTES"},
                {**receipt("rcp.owner", "atom.h.v0", "accept",
                           node="owner-stamp.bdo.v1", ts="2026-06-19T00:00:01Z"),
                 "artifact_hash": "sha256:NEWBYTES"},
            ])
            self.assertEqual(heal.owner_override_findings(Fold(root)), [])


class TestReadOnly(unittest.TestCase):
    def test_fold_writes_nothing(self):
        """heal proposes; it never writes. The log bytes are unchanged by a
        full run."""
        with tempfile.TemporaryDirectory() as tmp:
            root = write_log(Path(tmp) / ".ai-native", receipts=[
                receipt("rcp.neg", "atom.thing.v0", "missed"),
                receipt("rcp.pass", "atom.thing.v1", "confirmed"),
            ])
            before = {p.name: p.read_bytes() for p in (root / "log").iterdir()}
            heal.heal(root)
            after = {p.name: p.read_bytes() for p in (root / "log").iterdir()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
