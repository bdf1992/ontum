"""§10 tests for the session write-posture witness (done-line 0196).

Non-vacuous by construction: a session with NO write-on must fold to `reader`,
one WITH a write-on to `writer`, a SECOND write-on for the same session must
append nothing (write-once, I-2), and the pen must REFUSE an unset session id
or an empty narration. A fold that constantly returned `writer`, or a pen that
double-wrote, or one that invented a session id, fails a leg here.

Note: the BYPASS red-team (shell / pen-via-Bash / subagent paths defeating a
*gate*) belongs to **increment 2** — this witness installs no gate, so there is
nothing to bypass yet. These tests prove the witness, not a fence.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from loop import session


class SessionWitnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / ".ai-native"
        (self.root / "log").mkdir(parents=True)
        for name in ("events", "receipts", "admissions"):
            (self.root / "log" / f"{name}.jsonl").write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---- helpers ----

    def _events_path(self):
        return self.root / "log" / "events.jsonl"

    def _write_on_count(self):
        """How many session_write_on records are physically on the log."""
        n = 0
        for line in self._events_path().read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if json.loads(line).get("type") == session.WRITE_ON:
                n += 1
        return n

    def _posture_of(self, sid, registry):
        data = session.posture(self.root, registry=registry)
        return next((s for s in data["sessions"] if s["session_id"] == sid), None)

    # ---- reader vs writer (the core fold) ----

    def test_no_write_on_reads_reader(self):
        reg = {"sess-A": {"cwd": "/x", "ts": 1}}
        s = self._posture_of("sess-A", reg)
        self.assertIsNotNone(s)
        self.assertEqual(s["write_posture"], "reader")
        self.assertIsNone(s["crossed_at"])

    def test_write_on_reads_writer(self):
        rec, created = session.write_on(self.root, "sess-A", "picking up the pen")
        self.assertTrue(created)
        self.assertIsNotNone(rec)
        reg = {"sess-A": {"cwd": "/x", "ts": 1}}
        s = self._posture_of("sess-A", reg)
        self.assertEqual(s["write_posture"], "writer")
        self.assertEqual(s["crossed_at"], rec["ts"])

    def test_census_counts_split(self):
        session.write_on(self.root, "sess-W", "i will write")
        reg = {"sess-W": {"cwd": "/x", "ts": 1}, "sess-R": {"cwd": "/y", "ts": 2}}
        data = session.posture(self.root, registry=reg)
        self.assertEqual(data["census"]["writers"], 1)
        self.assertEqual(data["census"]["readers"], 1)
        self.assertEqual(data["census"]["total"], 2)

    # ---- write-once (I-2): a second declaration appends nothing ----

    def test_second_write_on_is_a_noop(self):
        rec1, created1 = session.write_on(self.root, "sess-A", "first crossing")
        self.assertTrue(created1)
        self.assertEqual(self._write_on_count(), 1)
        rec2, created2 = session.write_on(self.root, "sess-A", "trying again, harder")
        self.assertFalse(created2)
        self.assertEqual(rec2["id"], rec1["id"])  # returns the existing one
        self.assertEqual(self._write_on_count(), 1)  # NOTHING appended
        # and the original narration stands — the no-op did not overwrite it
        s = self._posture_of("sess-A", {"sess-A": {"cwd": "/x", "ts": 1}})
        self.assertEqual(s["narration"], "first crossing")

    # ---- refusals (needs-you) ----

    def test_unset_session_id_is_refused(self):
        # the CLI resolves the id from the env; unset -> needs-you, non-zero
        with mock.patch.dict("os.environ", {}, clear=True):
            rc = session.main(["--root", str(self.root), "write-on",
                               "--narration", "should be refused"])
        self.assertEqual(rc, 2)
        self.assertEqual(self._write_on_count(), 0)  # nothing invented

    def test_empty_narration_is_refused(self):
        with mock.patch.dict("os.environ",
                             {session.SESSION_ENV: "sess-A"}, clear=True):
            rc = session.main(["--root", str(self.root), "write-on",
                               "--narration", "   "])
        self.assertEqual(rc, 2)
        self.assertEqual(self._write_on_count(), 0)

    def test_pen_refuses_unset_id_directly(self):
        rec, created = session.write_on(self.root, None, "narration")
        self.assertIsNone(rec)
        self.assertFalse(created)
        self.assertEqual(self._write_on_count(), 0)

    # ---- the success path honours --root (the clobber regression) ----

    def test_main_write_on_success_honours_temp_root(self):
        """Driving main()'s SUCCESS path with --root <tmp> must land the record
        in <tmp>'s log and leave the repo's real log byte-untouched. The other
        main() tests only exercise refusal paths, which return before --root is
        used — so a subparser --root silently clobbering the top-level one to
        DEFAULT_ROOT (the live repo) hid here until now."""
        from loop.reconcile import DEFAULT_ROOT

        real_events = DEFAULT_ROOT / "log" / "events.jsonl"
        before = real_events.read_bytes() if real_events.exists() else None

        with mock.patch.dict("os.environ",
                             {session.SESSION_ENV: "sess-root"}, clear=True):
            rc = session.main(["--root", str(self.root), "write-on",
                               "--narration", "writing into the temp root, "
                               "not the live repo log"])
        self.assertEqual(rc, 0)

        # the record landed in the TEMP root, exactly once
        self.assertEqual(self._write_on_count(), 1)
        s = self._posture_of("sess-root", {"sess-root": {"cwd": "/x", "ts": 1}})
        self.assertIsNotNone(s)
        self.assertEqual(s["write_posture"], "writer")

        # and the repo's real log was NOT written (the footgun)
        after = real_events.read_bytes() if real_events.exists() else None
        self.assertEqual(before, after)

    # ---- the emergency flag is carried onto the record ----

    def test_emergency_flag_is_recorded(self):
        rec, created = session.write_on(self.root, "sess-A",
                                        "hot-fixing the heartbeat, no time",
                                        emergency=True)
        self.assertTrue(rec["emergency"])
        s = self._posture_of("sess-A", {"sess-A": {"cwd": "/x", "ts": 1}})
        self.assertTrue(s["emergency"])

    def test_non_emergency_defaults_false(self):
        rec, _ = session.write_on(self.root, "sess-A", "ordinary crossing")
        self.assertFalse(rec["emergency"])

    def test_by_and_triggering_act_carried(self):
        rec, _ = session.write_on(self.root, "sess-A", "narration",
                                  by="merge-node.v1", triggering_act="atom.x.v0")
        self.assertEqual(rec["by"], "merge-node.v1")
        self.assertEqual(rec["triggering_act"], "atom.x.v0")
        # default by is the session id
        rec2, _ = session.write_on(self.root, "sess-B", "narration")
        self.assertEqual(rec2["by"], "sess-B")

    # ---- the fold is read-only ----

    def test_fold_writes_nothing(self):
        session.write_on(self.root, "sess-A", "a crossing")
        before = self._events_path().read_bytes()
        reg = {"sess-A": {"cwd": "/x", "ts": 1}, "sess-R": {"cwd": "/y", "ts": 2}}
        for _ in range(3):
            session.posture(self.root, registry=reg)
            session.posture(self.root, registry=reg, session="sess-A")
        after = self._events_path().read_bytes()
        self.assertEqual(before, after)  # byte-identical: the fold wrote nothing

    # ---- absence is information ----

    def test_missing_log_is_absence_not_zero(self):
        self.assertIsNone(session.posture(self.tmp / "nope"))

    # ---- a pruned-from-registry writer still reads as a writer ----

    def test_crossed_session_not_in_registry_still_writer(self):
        session.write_on(self.root, "sess-gone", "crossed, then registry pruned")
        data = session.posture(self.root, registry={})  # empty registry
        s = next(x for x in data["sessions"] if x["session_id"] == "sess-gone")
        self.assertEqual(s["write_posture"], "writer")
        self.assertFalse(s["in_registry"])


if __name__ == "__main__":
    unittest.main()
