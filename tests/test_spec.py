"""§10 non-vacuity tests for loop/spec.py (node 1 — spec identity + versioning).

The test that matters (doctrine §10): editing a spec IN PLACE — same filename,
new bytes — must mint a new version the fold SEES, and a content-hash split is
what makes that true. A reading keyed by slug/id-string would collapse the two
versions (the heal/#424 hole); these tests fail on such an impl.
"""
import tempfile
import unittest
from pathlib import Path

from loop import spec


def _root():
    d = Path(tempfile.mkdtemp())
    (d / ".ai-native" / "specs").mkdir(parents=True)
    (d / ".ai-native" / "log").mkdir(parents=True)
    return d


def _write(root, name, text):
    p = spec.specs_dir(root) / name
    p.write_bytes(text.encode("utf-8"))
    return p


class SpecIdentity(unittest.TestCase):
    def test_inplace_edit_mints_new_version_the_fold_sees(self):
        root = _root()
        p = _write(root, "login.requirement.md", "v1: the owner logs in")
        spec.record_version(root, p, by="claude", reason="initial")
        h1 = spec.head(root, "login.requirement")

        # edit IN PLACE — same filename, new bytes
        p.write_bytes(b"v2: the owner logs in with a passkey")
        spec.record_version(root, p, by="claude", reason="passkey")
        h2 = spec.head(root, "login.requirement")

        self.assertNotEqual(h1, h2)
        f = spec.fold(root)["login.requirement"]
        self.assertEqual(f["head"], h2)
        self.assertIn(h1, f["superseded"])
        self.assertEqual(len(f["versions"]), 2)  # the fold sees BOTH

    def test_non_vacuous_idstring_split_collapses(self):
        # Proof the content-hash split is load-bearing: a broken reading that
        # keys versions by SLUG-string (ignoring content hash) cannot see the
        # in-place edit — it collapses the two versions to one. If the fold
        # were ever replaced by such an impl, the test above fails.
        root = _root()
        p = _write(root, "x.requirement.md", "a")
        spec.record_version(root, p, by="c", reason="i")
        p.write_bytes(b"b")
        spec.record_version(root, p, by="c", reason="e")

        recs = spec._spec_admissions(root)
        by_idstring = {r["spec"] for r in recs if r["type"] == spec.SPEC_VERSION}
        by_hash = {r["content_hash"] for r in recs if r["type"] == spec.SPEC_VERSION}
        self.assertEqual(len(by_idstring), 1)  # slug-string collapses to one
        self.assertEqual(len(by_hash), 2)      # content-hash distinguishes two

    def test_idempotent_same_bytes(self):
        root = _root()
        p = _write(root, "y.requirement.md", "same")
        spec.record_version(root, p, by="c", reason="1")
        spec.record_version(root, p, by="c", reason="2")  # identical bytes
        f = spec.fold(root)["y.requirement"]
        self.assertEqual(len(f["versions"]), 1)
        self.assertEqual(len(f["superseded"]), 0)

    def test_supersession_names_both_hashes_no_retro_invalidation(self):
        root = _root()
        p = _write(root, "z.requirement.md", "one")
        spec.record_version(root, p, by="c", reason="1")
        h1 = spec.head(root, "z.requirement")
        p.write_bytes(b"two")
        spec.record_version(root, p, by="c", reason="2")
        h2 = spec.head(root, "z.requirement")

        recs = spec._spec_admissions(root)
        sup = [r for r in recs if r["type"] == spec.SPEC_SUPERSEDED]
        self.assertEqual(len(sup), 1)
        self.assertEqual(sup[0]["old_hash"], h1)
        self.assertEqual(sup[0]["new_hash"], h2)
        # history untouched: the v1 version record still stands on the log
        vers = {r["content_hash"] for r in recs if r["type"] == spec.SPEC_VERSION}
        self.assertIn(h1, vers)

    def test_state_derived_from_log_not_files(self):
        # D-8: delete the spec file; the recorded version still stands.
        root = _root()
        p = _write(root, "w.requirement.md", "content")
        spec.record_version(root, p, by="c", reason="1")
        h = spec.head(root, "w.requirement")
        p.unlink()
        self.assertEqual(spec.head(root, "w.requirement"), h)


if __name__ == "__main__":
    unittest.main()
