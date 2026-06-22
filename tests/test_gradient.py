"""§10 test for the speed-gradient fold (done-line 0182).

Non-vacuous by construction: the untraced-band-crossing tooth must FLAG an
unarmed workflow, NOT flag one armed at its exact current bytes, and flag it
AGAIN once the bytes are edited (stale arm). A fold that skipped the
bytes-binding, or vacuously refused everything, fails legs (b) or (a)/(c).

The arm in leg (b) is a REAL review.py arm — so the workflow_armed record and
its version_hash are written by review._hash_bytes; if loop.gradient._hash_bytes
ever drifts from it (I-4), this test fails. The two definitions are pinned to
each other here, not by hope.
"""

import importlib.util
import json
import unittest
from pathlib import Path

from loop import gradient

REPO = Path(__file__).resolve().parents[1]

# Load the review pen the way it is invoked in the wild (it is not a package).
_spec = importlib.util.spec_from_file_location(
    "review_pen", REPO / ".claude" / "skills" / "review-workflow" / "review.py")
review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(review)

DEMO_JS = """export const meta = {
  name: 'demo',
  description: 'A read-only demo workflow for the gradient tooth test.',
  phases: [
    { title: 'One', detail: 'do one thing' },
  ],
}

phase('One')
const out = await agent(`trace ${args}`, { label: 'demo' })
return { out }
"""


def _write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class GradientFoldTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / ".ai-native"          # the log root
        (self.root / "log").mkdir(parents=True)
        for name in ("events", "receipts", "admissions"):
            (self.root / "log" / f"{name}.jsonl").write_text("", encoding="utf-8")
        self.wf = self.tmp / ".claude" / "workflows" / "demo.js"
        _write(self.wf, DEMO_JS)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _append(self, name, rec):
        with (self.root / "log" / f"{name}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")

    def _crossing_subjects(self):
        data = gradient.gradient(self.root)
        return {c["subject"] for c in data["crossings"]}, data

    # ---- the §10 tooth: untraced / armed-clean / stale-arm ----

    def test_unarmed_workflow_is_flagged(self):
        subjects, data = self._crossing_subjects()
        self.assertIn(".claude/workflows/demo.js", subjects)
        # not stale — it was never armed
        why = next(c["why"] for c in data["crossings"]
                   if c["subject"] == ".claude/workflows/demo.js")
        self.assertIn("no arm admission", why)

    def test_armed_current_bytes_not_flagged(self):
        adm = review.arm(str(self.wf), by="tester", root=self.tmp)
        self.assertIsNotNone(adm, "the demo workflow must pass lint and arm")
        subjects, _ = self._crossing_subjects()
        self.assertNotIn(".claude/workflows/demo.js", subjects)

    def test_stale_arm_is_flagged_again(self):
        review.arm(str(self.wf), by="tester", root=self.tmp)
        # edit the bytes after arming -> the arm no longer covers them
        _write(self.wf, DEMO_JS + "\n// edited after arming\n")
        subjects, data = self._crossing_subjects()
        self.assertIn(".claude/workflows/demo.js", subjects)
        why = next(c["why"] for c in data["crossings"]
                   if c["subject"] == ".claude/workflows/demo.js")
        self.assertIn("stale arm", why)

    def test_hash_pins_to_review(self):
        # the two _hash_bytes definitions must agree on the same bytes (I-4)
        raw = self.wf.read_bytes()
        self.assertEqual(gradient._hash_bytes(raw), review._hash_bytes(raw))

    # ---- the band profile ----

    def test_band_classification(self):
        self._append("events", {"type": "atom_event", "id": "atom.x.v0"})
        self._append("receipts", {"id": "rcp.x", "node": "value-gate.claude.v1",
                                   "verdict": "accept", "artifact_hash": "abc",
                                   "ts": "2026-06-21T00:00:00Z"})
        self._append("admissions", {"type": "tick", "id": "adm.t"})
        self._append("admissions", {"type": "setpoint", "id": "adm.s"})
        self._append("admissions", {"type": "auto_admit_fence", "id": "adm.f"})
        self._append("admissions", {"type": "node_real", "id": "adm.n"})
        self._append("admissions", {"type": "arc_confirmation", "id": "adm.a"})  # unbanded
        data = gradient.gradient(self.root)
        prof = data["profile"]
        # respond = events(1) + receipts(1) + tick(1)
        self.assertEqual(prof["fast"], 3)
        # retune = setpoint(1) + auto_admit_fence(1)
        self.assertEqual(prof["medium"], 2)
        # author = node_real(1)
        self.assertEqual(prof["slow"], 1)
        # arc_confirmation is honestly unbanded, not forced into a band
        self.assertEqual(prof["unbanded"], 1)
        self.assertIn("node_real", data["bands"]["author"]["kinds"])

    def test_missing_log_is_absence_not_zero(self):
        self.assertIsNone(gradient.gradient(self.tmp / "nope"))


if __name__ == "__main__":
    unittest.main()
