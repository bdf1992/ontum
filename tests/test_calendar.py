"""Tests for the calendar producer/subscriber pen (the first integration).

Decoupled pub/sub (bdo, 2026-06-22): ontum PUBLISHES a meeting record to the
calendar repo and CONSUMES its decisions back. The §10 teeth — the claims the
pen must not be able to fake:

  - `build_record` is pure: a known parked report appears as an agenda item
    (freshest first) and the manifest is typed — the record a runner/owner relies
    on, with the empty `decisions[]` return channel.
  - `publish` writes every record file AND records the publish on the log (no
    silent reach) — asserted with an injected `put_file` (no network).
  - `consume` lands a discharge decision: the owner-ask is gone afterwards, the
    discharge cites a logged `meeting_decision` event (the decoupled return leg's
    evidence), and re-consume is a no-op (idempotent — the re-run law).

The pen's reach is injected; the pure cores are exercised directly. The pen is
loaded by path like the other skill pens (tests/CLAUDE.md)."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import meeting  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "calendar_pen", REPO / ".claude" / "skills" / "calendar" / "calendar.py")
cal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cal)


def _report(stem, n):
    items = "\n".join(f"{i}. **Ask {i}** in {stem}" for i in range(1, n + 1))
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


def _events(root):
    return [json.loads(l) for l
            in (root / "log" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]


class BuildRecordTest(unittest.TestCase):
    def test_record_is_typed_and_carries_the_agenda(self):
        root = make_root(tempfile.mkdtemp(), {"0120-x": 2, "0050-y": 1})
        mid, files = cal.build_record(root, "2026-06-22")
        self.assertEqual(mid, "meeting.2026-06-22-owner-asks")
        man = "meetings/2026-06-22-owner-asks/manifest.json"
        self.assertEqual(set(files), {
            man,
            "meetings/2026-06-22-owner-asks/AGENDA.md",
            "meetings/2026-06-22-owner-asks/CLAUDE.md",
        })
        m = json.loads(files[man])
        self.assertEqual(m["type"], "owner-meeting")
        self.assertEqual(m["decisions"], [])          # the empty return channel
        report_ids = [a["report_id"] for a in m["agenda"]]
        self.assertIn("0120-x", report_ids)           # a parked report is on it
        self.assertEqual(report_ids[0], "0120-x")     # freshest first


class PublishTest(unittest.TestCase):
    def test_publish_writes_all_files_and_records_the_publish(self):
        root = make_root(tempfile.mkdtemp(), {"0100-a": 1})
        calls = []
        out = cal.publish(root, "2026-06-22", by="bdo", repo="x/calendar",
                          put_file=lambda repo, path, content, msg: calls.append(path))
        self.assertEqual(len(calls), 3)               # every record file written
        pub = [e for e in _events(root) if e.get("type") == "calendar_published"]
        self.assertEqual(len(pub), 1)                 # the reach is on the log
        self.assertEqual(pub[0]["meeting_id"], out["meeting_id"])
        self.assertEqual(len(pub[0]["files"]), 3)


class ConsumeTest(unittest.TestCase):
    def test_discharge_decision_lands_cites_evidence_and_is_idempotent(self):
        root = make_root(tempfile.mkdtemp(), {"0110-keep": 1, "0111-gone": 1})
        gid = next(g["id"] for g in meeting.live_owner_asks(root)
                   if g["report_id"] == "0111-gone")
        self.assertIn("0111-gone",
                      {it["report_id"] for it in meeting.agenda(root)["today"]})
        mid = "meeting.2026-06-22-owner-asks"
        manifest = {"id": mid, "decisions": [
            {"id": gid, "verdict": "discharge", "note": "done in the meeting",
             "by": "bdo"}]}
        out = cal.consume(root, mid, by="bdo", repo="x/calendar",
                          get_json=lambda r, p: manifest)
        self.assertEqual(len(out["applied"]), 1)
        self.assertEqual(out["applied"][0]["result"], "discharged")
        # the ask is gone (the decision landed back into ontum)
        self.assertNotIn("0111-gone",
                         {it["report_id"] for it in meeting.agenda(root)["today"]})
        # the discharge's evidence: a logged meeting_decision for this subject
        self.assertTrue(any(e.get("type") == "meeting_decision"
                            and e.get("subject") == gid for e in _events(root)))
        # re-consume lands nothing (idempotent — the re-run law)
        out2 = cal.consume(root, mid, by="bdo", repo="x/calendar",
                           get_json=lambda r, p: manifest)
        self.assertEqual(out2["applied"], [])

    def test_a_decision_keyed_by_report_id_resolves_and_discharges(self):
        # the runner sees report_id in AGENDA.md, not the opaque group id —
        # a decision keyed by report_id must still resolve and discharge.
        root = make_root(tempfile.mkdtemp(), {"0111-gone": 1})
        gid = next(g["id"] for g in meeting.live_owner_asks(root)
                   if g["report_id"] == "0111-gone")
        mid = "meeting.2026-06-22-owner-asks"
        manifest = {
            "id": mid,
            "agenda": [{"id": gid, "report_id": "0111-gone", "count": 1}],
            "decisions": [{"id": "0111-gone", "verdict": "discharge",
                           "note": "by report id", "by": "bdo"}],
        }
        out = cal.consume(root, mid, by="bdo", repo="x/calendar",
                          get_json=lambda r, p: manifest)
        self.assertEqual(out["applied"][0]["result"], "discharged")
        self.assertNotIn("0111-gone",
                         {it["report_id"] for it in meeting.agenda(root)["today"]})

    def test_a_defer_decision_is_recorded_only_not_actuated(self):
        root = make_root(tempfile.mkdtemp(), {"0110-keep": 1})
        gid = next(g["id"] for g in meeting.live_owner_asks(root)
                   if g["report_id"] == "0110-keep")
        mid = "meeting.2026-06-22-owner-asks"
        out = cal.consume(root, mid, by="bdo", repo="x/calendar",
                          get_json=lambda r, p: {"id": mid, "decisions": [
                              {"id": gid, "verdict": "defer", "note": "next time"}]})
        self.assertEqual(out["applied"][0]["result"], "recorded")
        # recorded but NOT discharged — the ask is still parked
        self.assertIn("0110-keep",
                      {it["report_id"] for it in meeting.agenda(root)["today"]})

    def test_no_manifest_on_the_surface_is_a_report_not_a_crash(self):
        root = make_root(tempfile.mkdtemp(), {"0100-a": 1})
        out = cal.consume(root, "meeting.x", by="bdo", get_json=lambda r, p: None)
        self.assertIn("error", out)
        self.assertEqual(out["applied"], [])


if __name__ == "__main__":
    unittest.main()
