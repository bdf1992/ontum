#!/usr/bin/env python3
"""§10 test for the test-suite economy (done-line 0171) — the fold that
types, attributes, and accounts the suite, with teeth.

Each tooth is from the done-line's bar:

  1. CLASSIFIER HONESTY — `refusal` is assigned only on *evidence* of a
     rejection (raises / exit-code / absence / reject-word), never on the
     method's NAME. A test named for a refusal whose body asserts none is
     NOT typed refusal — the mislabel teeth that keep the type from being
     a fabrication.
  2. NOT A CONSTANT — the classifier returns distinct types for distinct
     structural inputs (guard / refusal / byte-determinism / fold /
     pen-seam / integration / unit). A `return "X"` constant fails here —
     the test_term_economy bar applied to tests.
  3. UNDECIDABLE READS UNTYPED — a test that asserts nothing decisive is
     `untyped`, an honest gap, never a guessed label.
  4. MISLABEL SURFACES — the accounting names a name-claims-refusal /
     body-asserts-none test as a `mislabeled-test` finding.
  5. UNRECEIPTED CONTRACT — a frozen done-line that no test pins surfaces
     as an `unreceipted-contract` finding (a contract with no receipt).
  6. ATTRIBUTION RESOLVES, NEVER COINS — the filename convention and body
     references map to real organs; a reference to nothing is dropped.
  7. DETERMINISTIC OVER THE REAL SUITE — folding the repo's own tests/
     twice is byte-identical, and the histogram is non-trivial (the real
     suite is not all one bucket — proof the fold actually discriminates).
"""

import unittest
from pathlib import Path

from loop import suite

REPO = Path(__file__).resolve().parent.parent


def sig(name, src, subp=False):
    return suite.method_signals(name, src, subp)


class ClassifierHonesty(unittest.TestCase):
    """Tooth 1 + 3: the type comes from evidence, not the name."""

    def test_a_refusal_name_with_no_rejection_is_not_typed_refusal(self):
        # name screams refusal; body just checks a positive equality.
        s = sig("test_refuses_to_explode", "self.assertEqual(add(2, 2), 4)")
        self.assertFalse(s["asserts_rejection"])
        self.assertTrue(s["name_claims_refusal"])
        self.assertNotEqual(suite.classify(s), "refusal")

    def test_rejection_evidence_alone_makes_a_refusal(self):
        # no refusal word in the NAME — pure evidence (a raise) decides it.
        s = sig("test_does_a_thing", "with self.assertRaises(ValueError):\n    f()")
        self.assertEqual(suite.classify(s), "refusal")

    def test_an_absence_assertion_is_rejection_evidence(self):
        s = sig("test_quiet", "self.assertEqual(drift(self.root), [])")
        self.assertTrue(s["asserts_rejection"])
        self.assertEqual(suite.classify(s), "refusal")

    def test_a_test_that_asserts_nothing_is_untyped(self):
        s = sig("test_setup_only", "x = compute()\ny = x + 1")
        self.assertEqual(suite.classify(s), "untyped")


class ClassifierDiscriminates(unittest.TestCase):
    """Tooth 2: distinct structural inputs -> distinct types. A constant
    or fabricated classifier cannot pass this."""

    CASES = {
        "guard": ("test_guard",
                  "p = subprocess.run(...)\nself.assertEqual(p.returncode, 2)"),
        "refusal": ("test_x", "with self.assertRaises(ValueError):\n    f()"),
        "byte-determinism": ("test_x",
                             "self.assertEqual(a.read_bytes(), b.read_bytes())"),
        "fold": ("test_determinism",
                 "self.assertEqual(fold(r), fold(r))"),
        "pen-seam": ("test_x", "self.assertEqual(node.judge(atom), receipt)"),
        "integration": ("test_x",
                        "root = make_root(self.tmp)\nself.assertEqual(s, 'done')"),
        "unit": ("test_x", "self.assertEqual(add(2, 2), 4)"),
    }

    def test_each_signal_yields_its_own_type(self):
        got = {want: suite.classify(sig(n, s)) for want, (n, s) in self.CASES.items()}
        self.assertEqual(got, {k: k for k in self.CASES})

    def test_the_seven_types_are_not_collapsed(self):
        # at least five distinct outputs — a constant classifier yields one.
        outs = {suite.classify(sig(n, s)) for n, s in self.CASES.values()}
        self.assertGreaterEqual(len(outs), 5)


class Accounting(unittest.TestCase):
    """Teeth 4 + 5: the census names the gaps over synthetic records."""

    def _rec(self, **kw):
        base = {"id": "t::a", "file": "tests/test_a.py", "name": "test_a",
                "type": "unit", "asserts_rejection": True,
                "name_claims_refusal": False, "has_docstring": True,
                "organs": [], "pins": []}
        base.update(kw)
        return base

    def test_mislabeled_test_surfaces(self):
        tests = [self._rec(name="test_refuses_x", name_claims_refusal=True,
                           asserts_rejection=False, type="unit")]
        view = suite.account(tests, {}, set())
        kinds = {g["kind"] for g in view["gaps"]}
        self.assertIn("mislabeled-test", kinds)

    def test_a_real_refusal_is_not_mislabeled(self):
        tests = [self._rec(name="test_refuses_x", name_claims_refusal=True,
                           asserts_rejection=True, type="refusal")]
        view = suite.account(tests, {}, set())
        self.assertNotIn("mislabeled-test", {g["kind"] for g in view["gaps"]})

    def test_unpinned_frozen_done_line_surfaces(self):
        tests = [self._rec(pins=["0001"])]
        view = suite.account(tests, {}, {"0001", "0002"})
        gap = next(g for g in view["gaps"] if g["kind"] == "unreceipted-contract")
        self.assertIn("0002", gap["sample"])
        self.assertNotIn("0001", gap.get("sample", []))

    def test_untested_organ_surfaces(self):
        tests = [self._rec(organs=["loop.census"])]
        view = suite.account(tests, {"loop.census": "loop/census.py",
                                     "loop.gaps": "loop/gaps.py"}, set())
        untested = next(g for g in view["gaps"] if g["kind"] == "untested-organ")
        self.assertEqual(untested["subject"], "loop.gaps")


class Attribution(unittest.TestCase):
    """Tooth 6: resolve against the real inventory; never coin a target."""

    INV = {"loop.census": "loop/census.py", "loop.gaps": "loop/gaps.py",
           "hook.freeze_guard": ".claude/hooks/freeze_guard.py"}

    def test_filename_convention_maps_to_its_organ(self):
        self.assertEqual(suite.attribute_organs("test_census", "x = 1", self.INV),
                         {"loop.census"})

    def test_a_body_reference_resolves(self):
        self.assertEqual(
            suite.attribute_organs("test_misc", "from loop.gaps import x", self.INV),
            {"loop.gaps"})

    def test_a_reference_to_nothing_is_dropped(self):
        self.assertEqual(
            suite.attribute_organs("test_misc", "loop.does_not_exist", self.INV),
            set())

    def test_done_line_pins_are_read_from_text(self):
        self.assertEqual(
            suite.attribute_pins("pins done-line 0029 and cites §10 / D-4"),
            {"0029"})


class RealSuite(unittest.TestCase):
    """Tooth 7: deterministic and discriminating over the repo's own tests."""

    def test_fold_is_byte_deterministic(self):
        import json
        a = json.dumps(suite.fold(REPO), sort_keys=True)
        b = json.dumps(suite.fold(REPO), sort_keys=True)
        self.assertEqual(a, b)

    def test_the_histogram_is_non_trivial(self):
        view = suite.fold(REPO)
        # every test lands in exactly one bucket
        self.assertEqual(sum(view["by_type"].values()), view["totals"]["tests"])
        # the real suite spreads across kinds — not all one bucket
        nonempty = [k for k, n in view["by_type"].items() if n > 0]
        self.assertGreaterEqual(len(nonempty), 4)
        for kind in ("guard", "refusal", "unit"):
            self.assertGreater(view["by_type"][kind], 0, kind)


if __name__ == "__main__":
    unittest.main()
