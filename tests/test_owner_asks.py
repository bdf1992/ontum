"""Tests for the owner-ask floor (done-line 0058): a needs-you item parked
only in a session report cannot strand silently on bdo.

The hole report 0047 exposed: a session ended with five "awaiting bdo" items
written only into its report — a working-tree file he never opens. They
reached no queue and no surface. This fixes it two ways, and the §10 case is
the point in both: a locally-complete report (a well-formed needs-you
section) and a log with no reflection ack for it are each fine alone but
*refuse to fit* — the fold names the ask as unsurfaced, the drift opens an
issue, the beat screams it. The moment an 'open' reflection record carries
the group's id, the two fit again and everything goes silent.

The pure fold (loop/owner_asks.py) and the reflect drift kind are exercised
directly; the shame hook is driven through subprocess (stdin in, prose out,
exit 0) with CLAUDE_PROJECT_DIR at a crafted temp repo — the contract is
streams and exit codes, not internals (tests/CLAUDE.md)."""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import owner_asks, reconcile, reflect

HOOK = REPO / ".claude" / "hooks" / "owner_ask_shame.py"

_spec = importlib.util.spec_from_file_location(
    "reflect_pen_oa", REPO / ".claude" / "skills" / "reflect" / "reflect.py")
reflect_pen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reflect_pen)

STRANDED = """# Report 0100 — a session that parked work

## What landed

- something real

## needs-you (bdo's queue)

1. **Confirm the structure of `epic.causality-surface`** — keep it composing,
   or fold its pieces into the-field + experience-layer?
2. **Projection target:** local diagram, GitHub board, or both?

## End-state

`report` — work parked above.
"""

CLEAN = """# Report 0101 — a session that parked nothing

## needs-you

nothing — the field is clear.

## End-state

`report` — clean.
"""

NO_SECTION = """# Report 0102 — a note with no handoff

## What landed

- a fold landed; the word needs-you appears in this prose but not as a heading.

## End-state

`done`.
"""

# A report authored AFTER a baseline — its ask is new parking, the
# report-0047-class failure going forward, and must still surface and scream.
NEW_AFTER_BASELINE = """# Report 0103 — a session that parked work after the baseline

## needs-you

1. **Admit the worker node real** — or keep it mock another cycle?

## End-state

`report` — one tap parked.
"""


def make_root(tmp, reports):
    """A temp .ai-native with a log (empty jsonl) and the given reports
    ({stem: text}). The fold reads reports/; the surface/reflection records
    land in log/."""
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / name).write_text("", encoding="utf-8")
    rdir = root / "reports"
    rdir.mkdir(parents=True)
    for stem, text in reports.items():
        (rdir / f"{stem}.md").write_text(text, encoding="utf-8")
    return root


class ExtractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pulls_each_needs_you_item_as_an_ask(self):
        root = make_root(self.tmp, {"0100-stranded": STRANDED})
        groups = owner_asks.owner_ask_groups(root)
        self.assertEqual(len(groups), 1)
        g = groups[0]
        self.assertEqual(g["report_id"], "0100-stranded")
        self.assertEqual(len(g["asks"]), 2)
        self.assertIn("epic.causality-surface", g["asks"][0])
        self.assertIn("Projection target", g["asks"][1])

    def test_a_nothing_section_parks_no_ask(self):
        root = make_root(self.tmp, {"0101-clean": CLEAN})
        self.assertEqual(owner_asks.owner_ask_groups(root), [])

    def test_no_heading_means_no_ask_even_if_prose_says_needs_you(self):
        # the anchor is the scaffolded heading, not a prose mention
        root = make_root(self.tmp, {"0102-no-section": NO_SECTION})
        self.assertEqual(owner_asks.owner_ask_groups(root), [])

    def test_groups_are_per_report_and_id_is_stable(self):
        root = make_root(self.tmp, {"0100-stranded": STRANDED,
                                    "0101-clean": CLEAN,
                                    "0102-no-section": NO_SECTION})
        groups = owner_asks.owner_ask_groups(root)
        self.assertEqual([g["report_id"] for g in groups], ["0100-stranded"])
        # id is a pure function of the report id — recomputing matches
        self.assertEqual(
            groups[0]["id"],
            "ask." + reconcile.short_hash("owner-ask", "0100-stranded"))

    def test_missing_reports_dir_is_absence_not_error(self):
        root = Path(self.tmp) / "nothing-here"
        self.assertEqual(owner_asks.owner_ask_groups(root), [])


class UnsurfacedTest(unittest.TestCase):
    """The §10 pair on the fold: a stranded report refuses to stay hidden;
    a reflection ack makes it fit and fall silent."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, {"0100-stranded": STRANDED,
                                         "0101-clean": CLEAN})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_stranded_report_is_unsurfaced(self):
        groups = reflect.unsurfaced_owner_ask_groups(self.root)
        self.assertEqual([g["report_id"] for g in groups], ["0100-stranded"])

    def test_an_open_reflection_buys_silence(self):
        gid = owner_asks.owner_ask_groups(self.root)[0]["id"]
        reflect.record_reflection(self.root, "github-issues", "0100-stranded",
                                  gid, "open", "https://x/issues/1", by="test")
        self.assertEqual(reflect.unsurfaced_owner_ask_groups(self.root), [])

    def test_reportless_tree_short_circuits_to_empty(self):
        empty = Path(self.tmp) / "void"
        self.assertEqual(reflect.unsurfaced_owner_ask_groups(empty), [])


class DriftTest(unittest.TestCase):
    """The owner-ask-backlog drift kind: open-only, aggregate per report,
    rides the existing reflect machinery and the shared gh translator."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, {"0100-stranded": STRANDED})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def register(self):
        reflect.admit_surface(self.root, "github-issues", "owner/repo", by="test-bdo")

    def test_unregistered_surface_refuses(self):
        with self.assertRaises(ValueError):
            reflect.owner_ask_drift(self.root, "github-issues")

    def test_stranded_report_is_one_open_act(self):
        self.register()
        acts = reflect.owner_ask_drift(self.root, "github-issues")
        self.assertEqual([a["act"] for a in acts], ["open"])
        act = acts[0]
        self.assertEqual(act["artifact_hash"],
                         owner_asks.owner_ask_groups(self.root)[0]["id"])
        self.assertIn("0100-stranded", act["title"])
        self.assertIn("epic.causality-surface", act["body"])
        self.assertIn("mirror", act["body"])

    def test_recorded_open_is_a_no_op(self):
        self.register()
        act = reflect.owner_ask_drift(self.root, "github-issues")[0]
        reflect.record_reflection(self.root, "github-issues", act["atom_id"],
                                  act["artifact_hash"], "open",
                                  "https://x/issues/2", by="test")
        self.assertEqual(reflect.owner_ask_drift(self.root, "github-issues"), [])

    def test_kind_is_wired_into_the_tables(self):
        self.assertIn("owner-ask-backlog", reflect.RULE_KINDS)
        self.assertIs(reflect.DRIFT_BY_KIND["owner-ask-backlog"],
                      reflect.owner_ask_drift)

    def test_rides_the_beat_when_a_rule_enables_it(self):
        # the pen's auto verb opens the issue through the shared gh translator
        self.register()
        reflect.admit_rule(self.root, "owner-ask-backlog", "github-issues",
                           True, by="test-bdo")
        calls = []

        def fake(args):
            calls.append(args)
            if args[:3] == ["gh", "issue", "list"]:
                return "[]"  # no existing mirror — the open act mints (#547 probe)
            return "https://github.com/owner/repo/issues/3"

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = reflect_pen.auto(self.root, by="reflect-auto", run=fake)
        self.assertEqual(code, 0)
        creates = [c for c in calls if c[:3] == ["gh", "issue", "create"]]
        self.assertEqual(len(creates), 1)
        self.assertIn("auto-applied 1 act(s)", out.getvalue())
        # and the beat is now a no-op — the reflection record settled it
        with contextlib.redirect_stdout(io.StringIO()):
            code = reflect_pen.auto(self.root, by="reflect-auto",
                                    run=lambda a: self.fail("no drift, no reach"))
        self.assertEqual(code, 0)


class BaselineTest(unittest.TestCase):
    """The §10 pair on the baseline (the recency scope done-line 0058 named
    deferred): a baseline covering the standing backlog makes first activation
    SILENT — no historical flood — while an ask parked AFTER the baseline is a
    new refusal that still surfaces and screams. The two records (the report on
    disk, the baseline on the log) fit when the ask predates the guard and
    refuse to fit when it does not."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # the standing backlog: a stranded report already on disk at baseline
        self.root = make_root(self.tmp, {"0100-stranded": STRANDED,
                                         "0101-clean": CLEAN})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_baseline_records_every_present_group_signed(self):
        adm = reflect.admit_owner_ask_baseline(self.root, by="a-session")
        self.assertEqual(adm["type"], "owner_ask_baseline")
        self.assertEqual(adm["by"], "a-session")
        gid = owner_asks.owner_ask_groups(self.root)[0]["id"]
        self.assertEqual(adm["ask_ids"], [gid])

    def test_first_activation_is_silent_under_a_baseline(self):
        # (a) with a baseline over the existing asks, nothing floods bdo
        reflect.admit_owner_ask_baseline(self.root, by="a-session")
        self.assertEqual(reflect.unsurfaced_owner_ask_groups(self.root), [])
        reflect.admit_surface(self.root, "github-issues", "owner/repo", by="b")
        self.assertEqual(reflect.owner_ask_drift(self.root, "github-issues"), [])

    def test_a_new_ask_after_the_baseline_still_surfaces(self):
        # (b) an ask parked after the baseline is NOT covered — it fires
        reflect.admit_owner_ask_baseline(self.root, by="a-session")
        (self.root / "reports" / "0103-after.md").write_text(
            NEW_AFTER_BASELINE, encoding="utf-8")
        groups = reflect.unsurfaced_owner_ask_groups(self.root)
        self.assertEqual([g["report_id"] for g in groups], ["0103-after"])
        reflect.admit_surface(self.root, "github-issues", "owner/repo", by="b")
        acts = reflect.owner_ask_drift(self.root, "github-issues")
        self.assertEqual([a["act"] for a in acts], ["open"])
        self.assertIn("0103-after", acts[0]["title"])
        self.assertIn("worker node", acts[0]["body"])

    def test_baseline_is_monotonic_history_not_retro_invalidated(self):
        # a second baseline only quiets more; it never un-silences the first
        reflect.admit_owner_ask_baseline(self.root, by="a-session")
        (self.root / "reports" / "0103-after.md").write_text(
            NEW_AFTER_BASELINE, encoding="utf-8")
        reflect.admit_owner_ask_baseline(self.root, by="a-session")
        self.assertEqual(reflect.unsurfaced_owner_ask_groups(self.root), [])


class ShameHookTest(unittest.TestCase):
    """The floor, driven as it runs live: subprocess, stdin in, prose out,
    exit 0 always."""

    def run_hook(self, repo_root, stdin="{}", seed=None):
        if seed is not None:
            (repo_root / ".ai-native" / "owner-ask-shame.json").write_text(
                json.dumps(seed), encoding="utf-8")
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo_root))
        proc = subprocess.run([sys.executable, str(HOOK)], input=stdin,
                              capture_output=True, text=True, env=env)
        state = {}
        sp = repo_root / ".ai-native" / "owner-ask-shame.json"
        if sp.exists():
            state = json.loads(sp.read_text(encoding="utf-8"))
        return proc.returncode, proc.stdout, state

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = Path(self.tmp)
        make_root(self.repo, {"0100-stranded": STRANDED, "0101-clean": CLEAN})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_screams_a_stranded_report(self):
        code, out, state = self.run_hook(self.repo)
        self.assertEqual(code, 0)
        self.assertIn("owner-ask-shame", out)
        self.assertIn("0100-stranded", out)
        self.assertIn("turn 1", out)
        self.assertEqual(state["turns"], 1)

    def test_a_surfaced_ask_is_silent(self):
        # the §10 refusal, resolved: record the 'open' ack on the log, the
        # scream stops — exactly what buys silence.
        gid = owner_asks.owner_ask_groups(self.repo / ".ai-native")[0]["id"]
        reflect.record_reflection(self.repo / ".ai-native", "github-issues",
                                  "0100-stranded", gid, "open",
                                  "https://x/issues/1", by="test")
        code, out, state = self.run_hook(self.repo)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "")
        self.assertEqual(state.get("turns"), 0)

    def test_tally_rises_while_the_same_set_sits(self):
        _, _, s1 = self.run_hook(self.repo)
        self.assertEqual(s1["turns"], 1)
        _, out2, s2 = self.run_hook(self.repo)
        self.assertEqual(s2["turns"], 2)
        self.assertIn("turn 2", out2)

    def test_grows_louder_over_time(self):
        _, low, _ = self.run_hook(self.repo)
        self.assertIn("[owner-ask-shame] turn 1", low)
        self.assertNotIn("[OWNER-ASK-SHAME]", low)
        gid = owner_asks.owner_ask_groups(self.repo / ".ai-native")[0]["id"]
        _, loud, st = self.run_hook(self.repo, seed={"turns": 14, "ask_set": [gid]})
        self.assertEqual(st["turns"], 15)
        self.assertIn("[OWNER-ASK-SHAME]", loud)
        self.assertIn("15 TURNS", loud)

    def test_baseline_silences_the_floor_but_a_new_ask_still_screams(self):
        # (a) a baseline over the standing backlog: the floor is silent
        reflect.admit_owner_ask_baseline(self.repo / ".ai-native", by="a-session")
        code, out, state = self.run_hook(self.repo)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "")
        self.assertEqual(state.get("turns"), 0)
        # (b) a report parked AFTER the baseline: the floor screams it
        (self.repo / ".ai-native" / "reports" / "0103-after.md").write_text(
            NEW_AFTER_BASELINE, encoding="utf-8")
        code, out, state = self.run_hook(self.repo)
        self.assertEqual(code, 0)
        self.assertIn("owner-ask-shame", out)
        self.assertIn("0103-after", out)
        self.assertEqual(state["turns"], 1)

    def test_fails_open_on_a_reportless_repo_and_garbage_stdin(self):
        with tempfile.TemporaryDirectory() as bare:
            code, out, _ = self.run_hook(Path(bare), stdin="{not json")
            self.assertEqual(code, 0)
            self.assertEqual(out.strip(), "")


class DischargeTest(unittest.TestCase):
    """The third state the floor lacked (done-line 0065): a *resolved* ask is
    closed by CITING the log record that closed it, never by a session's
    say-so. The §10 pair: a well-formed discharge and a log missing its cited
    id are each locally fine and *refuse to fit* — the verb is the gate that
    notices, and without evidence the floor keeps screaming."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp, {"0100-stranded": STRANDED,
                                         "0101-clean": CLEAN})
        # a real closing record on the log to point a cite at
        reconcile.append_line(
            self.root / "log" / "admissions.jsonl",
            {"id": "adm.realclose01", "type": "done_superseded", "by": "bdo",
             "ts": "2026-06-13T00:00:00Z"})
        self.gid = owner_asks.owner_ask_groups(self.root)[0]["id"]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_real_cite_discharges_and_silences(self):
        adm, err = reflect.discharge_owner_ask(
            self.root, self.gid, ["adm.realclose01"],
            reason="the supersede closed it", by="a-session")
        self.assertIsNone(err)
        self.assertEqual(adm["type"], "owner_ask_discharged")
        self.assertEqual(adm["ask_id"], self.gid)
        self.assertEqual(adm["cites"], ["adm.realclose01"])
        # the floor falls silent for the whole group (both its asks)
        self.assertEqual(reflect.unsurfaced_owner_ask_groups(self.root), [])

    def test_an_absent_cite_is_refused_and_keeps_screaming(self):
        adm, err = reflect.discharge_owner_ask(
            self.root, self.gid, ["adm.doesnotexist"],
            reason="claiming closure with no evidence", by="a-session")
        self.assertIsNone(adm)
        self.assertIn("not on the log", err)
        # nothing written; the group still screams — no evidence, no silence
        self.assertEqual([g["report_id"] for g in
                          reflect.unsurfaced_owner_ask_groups(self.root)],
                         ["0100-stranded"])

    def test_a_partial_real_cite_set_is_refused_whole(self):
        adm, err = reflect.discharge_owner_ask(
            self.root, self.gid, ["adm.realclose01", "adm.fake"],
            reason="mixed evidence", by="a-session")
        self.assertIsNone(adm)
        self.assertIn("adm.fake", err)
        self.assertEqual(len(reflect.unsurfaced_owner_ask_groups(self.root)), 1)

    def test_an_unknown_ask_is_refused(self):
        adm, err = reflect.discharge_owner_ask(
            self.root, "ask.nosuchgroup", ["adm.realclose01"],
            reason="discharging a ghost", by="a-session")
        self.assertIsNone(adm)
        self.assertIn("not a live owner-ask group", err)

    def test_an_empty_cite_is_refused(self):
        adm, err = reflect.discharge_owner_ask(
            self.root, self.gid, [], reason="no evidence offered", by="a-session")
        self.assertIsNone(adm)
        self.assertIn("at least one", err)

    def test_discharge_is_monotonic_a_new_report_surfaces_afresh(self):
        # history is not retro-invalidated: discharging 0100 cannot cover a
        # later report's asks — a new report is a new group id
        reflect.discharge_owner_ask(self.root, self.gid, ["adm.realclose01"],
                                    reason="closed", by="a-session")
        (self.root / "reports" / "0103-after.md").write_text(
            NEW_AFTER_BASELINE, encoding="utf-8")
        groups = reflect.unsurfaced_owner_ask_groups(self.root)
        self.assertEqual([g["report_id"] for g in groups], ["0103-after"])

    def test_a_discharged_group_is_no_longer_offered_to_the_mirror(self):
        reflect.admit_surface(self.root, "github-issues", "owner/repo", by="b")
        self.assertEqual([a["act"] for a in
                          reflect.owner_ask_drift(self.root, "github-issues")],
                         ["open"])
        reflect.discharge_owner_ask(self.root, self.gid, ["adm.realclose01"],
                                    reason="closed", by="a-session")
        self.assertEqual(reflect.owner_ask_drift(self.root, "github-issues"), [])


if __name__ == "__main__":
    unittest.main()
