"""Tests for the off-log-PR audit (done-line 0066): a PR that reached
GitHub outside the machinery is caught.

The hole bdo named: the atom invariant is enforced only client-side (the
PR pen refuses to open a non-atom PR), so a PR authored straight on GitHub
— #107, zero atoms, zero receipts — bypasses it and is invisible to the
loop. This pins the pure half of the gate: given the branch facts the pen
gathers, an off-log branch and the log's atom invariant *refuse to fit*
(the §10 bar) — the fold names it an orphan — while an atom-backed branch
passes clean. The two real PRs are the fixtures: #107's shape is the
orphan, #111's shape (an atom plus a receipt naming it) is the clean pass.

The reach (gh + git) is the pen's and is not exercised here; the contract
this module owns is the pure verdict over facts (loop/pr_audit.py)."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import pr_audit


class AtomIdOf(unittest.TestCase):
    def test_atom_file_yields_its_stem(self):
        self.assertEqual(
            pr_audit.atom_id_of(".ai-native/atoms/atom.inbound-envoy-seam.v0.json"),
            "atom.inbound-envoy-seam.v0")

    def test_windows_separators_normalize(self):
        self.assertEqual(
            pr_audit.atom_id_of(r".ai-native\atoms\atom.foo.v0.json"),
            "atom.foo.v0")

    def test_non_atom_path_carries_no_id(self):
        self.assertIsNone(pr_audit.atom_id_of("CLAUDE.md"))
        self.assertIsNone(pr_audit.atom_id_of("loop/pr_audit.py"))


class OrphanReason(unittest.TestCase):
    def test_no_atom_is_an_orphan(self):
        # #107's shape: a docs-only PR adds no atom at all.
        reason = pr_audit.orphan_reason(added_atom_ids=[], receipt_artifact_ids=[])
        self.assertIsNotNone(reason)
        self.assertIn("no atom", reason)

    def test_atom_without_a_receipt_is_an_orphan(self):
        # The subtler bypass: a file under atoms/ that no receipt names — it
        # never entered the pipeline, so it is not on the log in the sense
        # the invariant means.
        reason = pr_audit.orphan_reason(
            added_atom_ids=["atom.foo.v0"], receipt_artifact_ids=[])
        self.assertIsNotNone(reason)
        self.assertIn("never entered the pipeline", reason)

    def test_atom_with_a_naming_receipt_is_backed(self):
        # #111's shape: the branch adds the atom and a receipt names it.
        self.assertIsNone(pr_audit.orphan_reason(
            added_atom_ids=["atom.inbound-envoy-seam.v0"],
            receipt_artifact_ids=["atom.inbound-envoy-seam.v0"]))

    def test_one_backed_atom_carries_the_rest(self):
        # #111 adds seven atoms but only one (the seam) carries a receipt yet;
        # the others are the response payload awaiting confirm-arc. One
        # atom+receipt satisfies the invariant — the PR is on the log.
        self.assertIsNone(pr_audit.orphan_reason(
            added_atom_ids=["atom.inbound-envoy-seam.v0",
                            "atom.qa-metabolism-resp-vanity-count.v0"],
            receipt_artifact_ids=["atom.inbound-envoy-seam.v0"]))

    def test_records_only_is_backed_without_an_atom(self):
        # done-line 0172: a report/done-line-only PR is OF work, not work — it
        # needs no atom (a session report written after its work landed cannot
        # bundle retroactively and would otherwise strand off main).
        self.assertIsNone(pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[], records_only=True))

    def test_records_only_does_not_override_the_atom_need_when_false(self):
        # the door is narrow: without the records_only proof, no atom is still
        # an orphan (the reach computes records_only from the diff; any non-record
        # change makes it False).
        self.assertIsNotNone(pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[], records_only=False))


class RecordsOnly(unittest.TestCase):
    """The records door's pure check (done-line 0172): only reports/done-line
    markdown, nothing else. Non-vacuous — a single non-record path closes it,
    so a report PR cannot smuggle code/atoms/logs in under the exemption."""

    def test_reports_and_done_lines_qualify(self):
        self.assertTrue(pr_audit.records_only(
            [".ai-native/reports/0123-x.md", ".ai-native/done/0172-y.md"]))

    def test_windows_separators_normalize(self):
        self.assertTrue(pr_audit.records_only(
            [".ai-native\\reports\\0123-x.md"]))

    def test_a_single_code_file_closes_the_door(self):
        self.assertFalse(pr_audit.records_only(
            [".ai-native/reports/0123-x.md", "loop/pr_audit.py"]))

    def test_an_atom_or_log_change_closes_the_door(self):
        self.assertFalse(pr_audit.records_only(
            [".ai-native/reports/0123-x.md", ".ai-native/atoms/atom.x.v0.json"]))
        self.assertFalse(pr_audit.records_only(
            [".ai-native/reports/0123-x.md", ".ai-native/log/events.jsonl"]))

    def test_a_non_md_record_path_does_not_qualify(self):
        # a .pen.json or a stray non-md under the records dir is not a record
        self.assertFalse(pr_audit.records_only([".ai-native/done/.pen.json"]))

    def test_empty_change_set_is_not_records_only(self):
        self.assertFalse(pr_audit.records_only([]))

    def test_audit_labels_a_records_pr_backed_by_the_records_door(self):
        result = pr_audit.audit([{
            "number": 427, "headRefName": "claude/report-0123",
            "added_atom_ids": [], "receipt_artifact_ids": [],
            "records_only": True}])
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["clean"][0]["backed_by"], ["records-door"])


class Audit(unittest.TestCase):
    def test_the_two_real_pr_shapes_split(self):
        facts = [
            {"number": 107, "headRefName": "claude/compose-harness-fence",
             "author": "bdf1992", "added_atom_ids": [], "receipt_artifact_ids": []},
            {"number": 111, "headRefName": "claude/inbound-envoy-seam",
             "author": "claude",
             "added_atom_ids": ["atom.inbound-envoy-seam.v0"],
             "receipt_artifact_ids": ["atom.inbound-envoy-seam.v0"]},
        ]
        result = pr_audit.audit(facts)
        self.assertEqual([o["number"] for o in result["orphans"]], [107])
        self.assertEqual([c["number"] for c in result["clean"]], [111])
        self.assertEqual(result["clean"][0]["backed_by"],
                         ["atom.inbound-envoy-seam.v0"])

    def test_clean_field_has_no_orphans(self):
        facts = [{"number": 111, "headRefName": "b", "added_atom_ids": ["atom.x.v0"],
                  "receipt_artifact_ids": ["atom.x.v0"]}]
        self.assertEqual(pr_audit.audit(facts)["orphans"], [])


class ExitCode(unittest.TestCase):
    """The non-zero-on-orphan contract (done-line 0068): the CI gate and the
    PR pen's --range both gate on this exit code, so it is the seam where
    'visible' becomes 'blocking'. Pinned at the pure CLI both express."""

    def _run_main(self, facts):
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(facts, fh)
            path = fh.name
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return pr_audit.main([path])
        finally:
            Path(path).unlink()

    def test_orphan_exits_nonzero(self):
        # an off-log PR must turn the check red so the merge is blocked
        code = self._run_main([{"number": 107, "headRefName": "x",
                                "added_atom_ids": [], "receipt_artifact_ids": []}])
        self.assertEqual(code, 1)

    def test_atom_backed_exits_zero(self):
        code = self._run_main([{"number": 111, "headRefName": "y",
                                "added_atom_ids": ["atom.x.v0"],
                                "receipt_artifact_ids": ["atom.x.v0"]}])
        self.assertEqual(code, 0)


class ConsumerPort(unittest.TestCase):
    """The reader's port (the registry conversation, 2026-06-13): a consumer
    that is not enforcing gets the structured verdict, not the human render —
    symmetric to the --range enforcer port. Pins that --json emits parseable
    JSON carrying the orphan/clean split, and still exits non-zero on an
    orphan so a json-reading gate can also block."""

    def _json_main(self, facts):
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(facts, fh)
            path = fh.name
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = pr_audit.main([path, "--json"])
            return code, json.loads(buf.getvalue())
        finally:
            Path(path).unlink()

    def test_json_emits_the_verdict_dataset(self):
        code, data = self._json_main([
            {"number": 107, "headRefName": "x", "author": "bdf1992",
             "added_atom_ids": [], "receipt_artifact_ids": []},
            {"number": 111, "headRefName": "y", "added_atom_ids": ["atom.x.v0"],
             "receipt_artifact_ids": ["atom.x.v0"]},
        ])
        self.assertEqual(code, 1)  # an orphan present: still a blocking signal
        self.assertEqual([o["number"] for o in data["orphans"]], [107])
        self.assertEqual([c["number"] for c in data["clean"]], [111])


if __name__ == "__main__":
    unittest.main()
