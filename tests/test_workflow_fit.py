"""§10 teeth for the workflow wrapper's CROSS-FILE fit check.

The doctrine's real bar (not the easy one): can two LOCALLY-FINE workflows refuse
to fit, and does the gate notice? The seam is workflow composition — a workflow
may invoke another by name (`workflow('slug')`). A workflow that is valid ALONE
but references a missing or malformed sibling is the misfit `lint` (a per-file
cell check) cannot see. These tests prove `fit` catches it — and that it does not
fire on a clean reference (non-vacuous both ways).
"""

import importlib.util
import pathlib
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
LINT_PATH = REPO / ".claude" / "skills" / "author-workflow" / "lint.py"
EXAMPLE = REPO / ".claude" / "workflows" / "subsystem-map.js"

_spec = importlib.util.spec_from_file_location("workflow_lint", LINT_PATH)
lint_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_mod)

ALPHA = """export const meta = {
  name: 'alpha',
  description: 'composes beta.',
  phases: [{ title: 'Go', detail: 'x' }],
}
phase('Go')
const r = await workflow('beta')
return r
"""

BETA = """export const meta = {
  name: 'beta',
  description: 'a helper.',
  phases: [{ title: 'Do', detail: 'y' }],
}
phase('Do')
return await agent('do the thing')
"""

BETA_BROKEN = "phase('Do')\nawait agent('no meta block')\n"  # lints as malformed


def _write(d, slug, src):
    p = pathlib.Path(d) / f"{slug}.js"
    p.write_text(src, encoding="utf-8")
    return p


class FitTeeth(unittest.TestCase):
    def test_two_locally_fine_workflows_fit_when_the_sibling_exists(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "alpha", ALPHA)
            _write(d, "beta", BETA)
            # both pass the cell check on their own
            self.assertTrue(lint_mod.lint(str(a))["ok"])
            self.assertTrue(lint_mod.lint(str(pathlib.Path(d) / "beta.js"))["ok"])
            f = lint_mod.fit(str(a))
            self.assertTrue(f["ok"], msg=f["dangling"])
            self.assertEqual(f["refs"], ["beta"])

    def test_a_locally_fine_workflow_refuses_to_fit_a_missing_sibling(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "alpha", ALPHA)  # references beta, which is absent
            self.assertTrue(lint_mod.lint(str(a))["ok"])  # valid ALONE
            f = lint_mod.fit(str(a))
            self.assertFalse(f["ok"])  # but refuses to fit
            self.assertTrue(any("beta" in x for x in f["dangling"]))

    def test_a_malformed_sibling_is_a_misfit(self):
        with tempfile.TemporaryDirectory() as d:
            a = _write(d, "alpha", ALPHA)
            _write(d, "beta", BETA_BROKEN)  # beta exists but is malformed
            f = lint_mod.fit(str(a))
            self.assertFalse(f["ok"])
            self.assertTrue(any("malformed" in x for x in f["dangling"]))

    def test_no_references_fits_trivially(self):
        # the real worked example invokes no sibling workflow
        f = lint_mod.fit(str(EXAMPLE))
        self.assertTrue(f["ok"])
        self.assertEqual(f["refs"], [])


if __name__ == "__main__":
    unittest.main()
