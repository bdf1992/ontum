"""Tests for the cited sensor against done-line 0086: the data->evidence half of
the digital-experience fold reads a person's data surface read-only and emits
evidence whose citations resolve against the bytes — reusing the
`term_economy.resolve_evidence` ghost discipline (§10), never rebuilding it.

The teeth: a locally-fine evidence record must be REFUSED when its citation
points at nothing. (1) a real tmpdir corpus yields evidence whose citations all
resolve; (2) a record citing a nonexistent path is a ghost; (3) a record citing
a real file with a fabricated content anchor is a ghost; (4) the scan writes
nothing — the corpus bytes are unchanged after a scan."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from causality import cited_sensor
from causality.cited_sensor import cited, ghosts, is_ghost, scan


class CitedSensorTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "downloads").mkdir()
        (self.root / "downloads" / "MyGame-Setup.txt").write_text(
            "GameInstaller v3.2\npublisher: acme studios\n", encoding="utf-8")
        (self.root / "downloads" / "invoice-2026.csv").write_text(
            "date,amount\n2026-06-15,42.00\n", encoding="utf-8")
        (self.root / "downloads" / "empty.bin").write_bytes(b"")

    def tearDown(self):
        self._tmp.cleanup()

    # --- the happy fold ---------------------------------------------------

    def test_scan_emits_a_record_per_file(self):
        records = scan(self.root)
        files = {ev["file"] for ev in records}
        self.assertEqual(files, {
            "downloads/MyGame-Setup.txt",
            "downloads/invoice-2026.csv",
            "downloads/empty.bin",
        })

    def test_records_carry_kind_size_and_anchor(self):
        by_file = {ev["file"]: ev for ev in scan(self.root)}
        game = by_file["downloads/MyGame-Setup.txt"]
        self.assertEqual(game["kind"], "txt")
        self.assertGreater(game["size"], 0)
        self.assertEqual(game["contains"], "GameInstaller v3.2")
        # an empty file is honest by existence alone (no content anchor)
        self.assertIsNone(by_file["downloads/empty.bin"]["contains"])

    def test_real_corpus_all_citations_resolve(self):
        records = scan(self.root)
        self.assertEqual(cited(self.root, records), records)
        self.assertEqual(ghosts(self.root, records), [])

    # --- the teeth: ghosts refused ---------------------------------------

    def test_citation_to_nonexistent_path_is_a_ghost(self):
        fake = {"file": "downloads/never-existed.exe", "stratum": "file",
                "kind": "exe", "size": 10, "contains": "whatever"}
        self.assertTrue(is_ghost(self.root, fake))
        self.assertEqual(cited(self.root, [fake]), [])
        self.assertEqual(ghosts(self.root, [fake]), [fake])

    def test_fabricated_content_anchor_is_a_ghost(self):
        # the path is real, but the claimed anchor is not in the bytes
        lie = {"file": "downloads/invoice-2026.csv", "stratum": "file",
               "kind": "csv", "size": 30, "contains": "GameInstaller v3.2"}
        self.assertTrue(is_ghost(self.root, lie))
        self.assertEqual(cited(self.root, [lie]), [])

    def test_honest_record_is_not_a_ghost(self):
        true = {"file": "downloads/invoice-2026.csv", "stratum": "file",
                "kind": "csv", "size": 30, "contains": "date,amount"}
        self.assertFalse(is_ghost(self.root, true))

    # --- read-only -------------------------------------------------------

    def test_scan_writes_nothing(self):
        before = {p: p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        scan(self.root)
        cited(self.root)
        after = {p: p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        # and no new files appeared
        self.assertEqual(set(before), set(after))


if __name__ == "__main__":
    unittest.main()
