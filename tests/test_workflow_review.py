"""§10 teeth for the workflow-authoring wrapper's review interface (A3).

The review surface must (1) render a true shaped read — blast radius and phases
read from the actual file, not asserted — and (2) gate arming: a malformed draft
cannot be armed, and arming binds to the bytes so an edit un-arms the workflow.
"""

import importlib.util
import pathlib
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO / ".claude" / "skills" / "review-workflow" / "review.py"
EXAMPLE = REPO / ".claude" / "workflows" / "subsystem-map.js"

_spec = importlib.util.spec_from_file_location("workflow_review", REVIEW_PATH)
review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(review)

MUTATING = """export const meta = {
  name: 'fixer',
  description: 'Applies a fix across files.',
  phases: [{ title: 'Find', detail: 'x' }, { title: 'Fix', detail: 'y' }],
}
phase('Find')
const hits = await agent('find the sites')
phase('Fix')
await parallel(hits.map(h => () => agent('edit and commit the fix', { isolation: 'worktree' })))
"""

MALFORMED = "phase('Go')\nawait agent('no meta block here')\n"


def _write(d, slug, src):
    p = pathlib.Path(d) / f"{slug}.js"
    p.write_text(src, encoding="utf-8")
    return p


class ReviewRenderTeeth(unittest.TestCase):
    def test_read_only_example_renders_truthfully(self):
        r = review.render(str(EXAMPLE))
        self.assertTrue(r["lint_ok"], msg=r["problems"])
        self.assertEqual(r["blast_radius"], "read-only")
        self.assertEqual(r["phases"], ["Survey", "Read", "Synthesize"])
        self.assertIn("Map a subsystem", r["what"])
        self.assertIn("read-only", r["riskiest_step"])

    def test_mutating_workflow_is_flagged_with_a_riskiest_step(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fixer", MUTATING)
            r = review.render(str(p))
            self.assertEqual(r["blast_radius"], "mutates")
            self.assertEqual(r["phases"], ["Find", "Fix"])
            self.assertIn("isolated", r["riskiest_step"])

    def test_malformed_render_carries_the_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "broken", MALFORMED)
            r = review.render(str(p))
            self.assertFalse(r["lint_ok"])
            self.assertTrue(r["problems"])


class ArmTeeth(unittest.TestCase):
    def test_malformed_cannot_be_armed(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "broken", MALFORMED)
            adm = review.arm(str(p), "tester", root=d)
            self.assertIsNone(adm)
            self.assertEqual(review.armings(d), {})  # nothing written

    def test_arm_records_and_is_readable(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fixer", MUTATING)
            r0 = review.render(str(p))
            self.assertFalse(review.is_armed("fixer", r0["version_hash"], root=d))
            adm = review.arm(str(p), "tester", root=d)
            self.assertIsNotNone(adm)
            self.assertEqual(adm["workflow"], "fixer")
            self.assertTrue(review.is_armed("fixer", r0["version_hash"], root=d))

    def test_editing_un_arms_the_workflow(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fixer", MUTATING)
            old_hash = review.render(str(p))["version_hash"]
            review.arm(str(p), "tester", root=d)
            self.assertTrue(review.is_armed("fixer", old_hash, root=d))
            # edit the workflow → new bytes → the old arming no longer applies
            p.write_text(MUTATING + "\n// a change\n", encoding="utf-8")
            new_hash = review.render(str(p))["version_hash"]
            self.assertNotEqual(new_hash, old_hash)
            self.assertFalse(review.is_armed("fixer", new_hash, root=d))

    def test_re_arming_same_bytes_is_idempotent(self):
        # I-2: a re-arm of the same bytes by the same approver folds to one id
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fixer", MUTATING)
            a1 = review.arm(str(p), "tester", root=d)
            a2 = review.arm(str(p), "tester", root=d)
            self.assertEqual(a1["id"], a2["id"])  # no wall-clock in the id

    def test_disarm_withdraws_without_an_edit(self):
        # supersede-never-erase: a dangerous workflow is un-armed on the record,
        # not by editing its bytes
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "fixer", MUTATING)
            h = review.render(str(p))["version_hash"]
            review.arm(str(p), "tester", root=d)
            self.assertTrue(review.is_armed("fixer", h, root=d))
            review.disarm(str(p), "tester", root=d)
            self.assertFalse(review.is_armed("fixer", h, root=d))
            # and it can be re-armed afterward (latest wins)
            review.arm(str(p), "tester", root=d)
            self.assertTrue(review.is_armed("fixer", h, root=d))

    def test_dangling_reference_cannot_be_armed(self):
        # the §10 fit gate also blocks arming
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "alpha",
                       MUTATING.replace("name: 'fixer'", "name: 'alpha'")
                       + "\nawait workflow('ghost')\n")
            r = review.render(str(p))
            self.assertFalse(r["fit_ok"])
            self.assertIsNone(review.arm(str(p), "tester", root=d))


if __name__ == "__main__":
    unittest.main()
