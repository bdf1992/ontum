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
    """The records door's pure check (done-line 0172; widened to proposals
    2026-06-23): only reports/done-line/proposal markdown, nothing else.
    Non-vacuous — a single non-record path closes it, so a record PR cannot
    smuggle code/atoms/logs in under the exemption."""

    def test_reports_and_done_lines_qualify(self):
        self.assertTrue(pr_audit.records_only(
            [".ai-native/reports/0123-x.md", ".ai-native/done/0172-y.md"]))

    def test_proposals_qualify(self):
        # bdo 2026-06-23, "land blueprints as proposal-records" (#355): a
        # proposal records work *proposed*; a blueprint-only PR is records-only.
        self.assertTrue(pr_audit.records_only(
            [".ai-native/proposals/proposals-records-door.proposal.md"]))
        # mixed with the older record kinds still qualifies — all records
        self.assertTrue(pr_audit.records_only(
            [".ai-native/proposals/x.proposal.md",
             ".ai-native/reports/0123-x.md", ".ai-native/done/0188-y.md"]))

    def test_a_proposal_plus_a_code_file_closes_the_door(self):
        # the teeth stay: a proposal cannot smuggle a code change in under the
        # exemption — a single .py file makes the branch need an atom again
        self.assertFalse(pr_audit.records_only(
            [".ai-native/proposals/x.proposal.md", "loop/pr_audit.py"]))

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


class ReceiptsDoor(unittest.TestCase):
    """The RAW door's teeth (done-line 0187, bdo's RAW vs RAI cut): a PR whose
    ONLY change is appended receipt lines is backed without an atom iff every
    appended line RE-DERIVES to its stored id. A RAW append is a deterministic
    fact that proves itself by recomputation; a fabricated or tampered line is
    RAI/smuggling and refuses the whole PR. This is the #617 stranded-acceptance
    fix: the door that the old extension-blind gate refused for carrying `.jsonl`
    instead of `.md`.

    `REAL_RECEIPT` is a genuine value-gate receipt off the live log — its id
    re-derives by the exact derivation `make_receipt` minted it with, so the
    fixtures are grounded in real bytes, not a constant the checker could be
    written to satisfy vacuously (§10)."""

    REAL_RECEIPT = {
        "id": "rcp.d0facd1da7dc",
        "event_id": "evt.a8859493a9b5",
        "node": "value-gate.claude.v1",
        "artifact_id": "atom.agent-runs-on-the-books-hardening.v0",
        "artifact_hash": ("sha256:c67b9275f9157f39b19999e892dd4fb98f4"
                          "8ce9784754da5313cd32a820cf798"),
        "verdict": "accept",
        "next_suggested_event": "value.accepted",
    }

    def test_a_real_receipt_re_derives(self):
        # the load-bearing leg: a faithful append proves itself
        self.assertTrue(pr_audit.receipt_rederives(self.REAL_RECEIPT))

    def test_tampering_any_keyed_field_breaks_the_derivation(self):
        # change the hash the receipt claims to have judged — the id no longer
        # recomputes, so the line is exposed as not-a-fact (the §10 flip)
        tampered = {**self.REAL_RECEIPT,
                    "artifact_hash": "sha256:" + "0" * 64}
        self.assertFalse(pr_audit.receipt_rederives(tampered))
        # and the node it claims to be (a smuggled different judge)
        self.assertFalse(pr_audit.receipt_rederives(
            {**self.REAL_RECEIPT, "node": "owner.bdo"}))

    def test_a_fabricated_id_is_refused(self):
        fake = {**self.REAL_RECEIPT, "id": "rcp.deadbeef0000"}
        self.assertFalse(pr_audit.receipt_rederives(fake))

    def test_a_missing_keyed_field_does_not_re_derive(self):
        for missing in ("event_id", "node", "artifact_id", "artifact_hash", "id"):
            rc = {k: v for k, v in self.REAL_RECEIPT.items() if k != missing}
            self.assertFalse(pr_audit.receipt_rederives(rc), missing)

    def test_a_merge_receipt_id_scheme_does_not_re_derive(self):
        # a rcp.merge.NNN land receipt is minted by a different scheme and no PR
        # appends one — the door must refuse it, not admit it
        self.assertFalse(pr_audit.receipt_rederives(
            {"id": "rcp.merge.549", "node": "merge-node.claude.v1",
             "artifact_id": "atom.x.v0", "verdict": "landed"}))

    def test_receipts_only_door_admits_a_re_deriving_append(self):
        # the whole-PR verdict: receipts-only + every line re-derives -> backed
        self.assertIsNone(pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[],
            receipts_only=True, added_receipts=[self.REAL_RECEIPT]))

    def test_receipts_only_door_refuses_a_fabricated_append(self):
        reason = pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[],
            receipts_only=True,
            added_receipts=[{**self.REAL_RECEIPT, "id": "rcp.deadbeef0000"}])
        self.assertIsNotNone(reason)
        self.assertIn("does NOT re-derive", reason)

    def test_one_bad_line_poisons_the_whole_batch(self):
        # a real receipt alongside a tampered one still refuses (no slipping a
        # fake in behind a real append)
        tampered = {**self.REAL_RECEIPT, "artifact_hash": "sha256:" + "0" * 64,
                    "id": "rcp.d0facd1da7dc"}
        reason = pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[],
            receipts_only=True, added_receipts=[self.REAL_RECEIPT, tampered])
        self.assertIsNotNone(reason)

    def test_receipts_only_with_no_parseable_append_is_refused(self):
        # a receipts-only diff that adds nothing re-derivable (e.g. a history
        # edit) has nothing to back
        reason = pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[],
            receipts_only=True, added_receipts=[])
        self.assertIsNotNone(reason)
        self.assertIn("nothing here to re-derive", reason)

    def test_receipts_only_false_falls_back_to_needing_an_atom(self):
        # the door is narrow: when the change set is NOT receipts-only (the reach
        # found another touched file, or removed log history), a re-deriving
        # receipt does not exempt the PR — it still needs an atom
        reason = pr_audit.orphan_reason(
            added_atom_ids=[], receipt_artifact_ids=[],
            receipts_only=False, added_receipts=[self.REAL_RECEIPT])
        self.assertIsNotNone(reason)
        self.assertIn("no atom", reason)

    def test_receipts_only_file_scope_is_non_vacuous(self):
        self.assertTrue(pr_audit.receipts_only([".ai-native/log/receipts.jsonl"]))
        # a single other path closes it — no work can ride a receipt append
        self.assertFalse(pr_audit.receipts_only(
            [".ai-native/log/receipts.jsonl", "loop/pr_audit.py"]))
        self.assertFalse(pr_audit.receipts_only(
            [".ai-native/log/receipts.jsonl", ".ai-native/log/events.jsonl"]))
        self.assertFalse(pr_audit.receipts_only([]))

    def test_audit_labels_a_receipts_pr_backed_by_the_receipts_door(self):
        result = pr_audit.audit([{
            "number": 656, "headRefName": "claude/strand-acceptance",
            "added_atom_ids": [], "receipt_artifact_ids": [],
            "receipts_only": True, "added_receipts": [self.REAL_RECEIPT]}])
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["clean"][0]["backed_by"], ["receipts-door"])

    def test_audit_orphans_a_fabricated_receipts_pr(self):
        result = pr_audit.audit([{
            "number": 999, "headRefName": "claude/smuggle",
            "added_atom_ids": [], "receipt_artifact_ids": [],
            "receipts_only": True,
            "added_receipts": [{**self.REAL_RECEIPT, "id": "rcp.deadbeef0000"}]}])
        self.assertEqual([o["number"] for o in result["orphans"]], [999])


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
