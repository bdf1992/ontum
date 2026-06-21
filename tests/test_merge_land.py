"""The merge-node's hand refuses by default (pr.py land verb).

land_refusal is the gate between an open PR and the trunk. Its job is to say
*no* unless every condition holds at once — so these tests are mostly the
no's: each locally-fine PR that is missing one thing must still be refused.
The §10 teeth: a green, written, mergeable PR whose arc bdo has NOT confirmed
is locally fine in every way the PR can see, yet it must not land — the
confirmation is the independent stamp (D-4), and its absence refuses to fit.
"""

import argparse
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "pr_pen", ROOT / ".claude" / "skills" / "branch-ritual" / "pr.py")
pr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pr)


def _ok_pr(**over):
    """A PR that would land: open, on main, not draft, mergeable, green,
    written story. Each test knocks out exactly one condition."""
    info = {
        "state": "OPEN",
        "baseRefName": "main",
        "headRefName": "claude/merge-node",
        "isDraft": False,
        "mergeable": "MERGEABLE",
        "title": "the merge-node's hand lands confirmed-arc work",
        "body": "A real written story for a cold reader.",
        "statusCheckRollup": [{"conclusion": "SUCCESS"}],
        "author": {"login": "claude-author"},
    }
    info.update(over)
    return info


CONF = "adm.deadbeef"  # a stand-in for a real arc_confirmed admission id
BY = "merge-node.claude.v0"


class LandRefusal(unittest.TestCase):
    def test_full_house_lands(self):
        self.assertIsNone(pr.land_refusal(_ok_pr(), CONF, BY, True, True))

    def test_unconfirmed_arc_refuses_even_when_otherwise_perfect(self):
        # the §10 case: nothing the PR can see is wrong; the missing human
        # stamp is what refuses to fit.
        reason = pr.land_refusal(_ok_pr(), None, BY, True, True)
        self.assertIsNotNone(reason)
        self.assertIn("confirm", reason.lower())

    def test_no_by_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(), CONF, "", True, True))

    def test_unadmitted_by_refuses_even_when_otherwise_perfect(self):
        # done-line 0049's §10 case: a perfect PR, a confirmed arc, and a
        # lander whose name no admission ever wrote — a free-text identity
        # is effectively mock and must not land. The default is refuse.
        reason = pr.land_refusal(_ok_pr(), CONF, BY)
        self.assertIsNotNone(reason)
        self.assertIn("not an admitted node", reason)
        self.assertIn("admit-real", reason)

    def test_missing_non_author_attestation_refuses(self):
        reason = pr.land_refusal(_ok_pr(), CONF, BY, True)
        self.assertIsNotNone(reason)
        self.assertIn("--attest-non-author", reason)

    def test_exact_author_identity_match_refuses_even_with_attestation(self):
        reason = pr.land_refusal(_ok_pr(author={"login": BY}), CONF, BY,
                                 True, True)
        self.assertIsNotNone(reason)
        self.assertIn("matches --by", reason)

    def test_draft_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(isDraft=True), CONF, BY, True, True))

    def test_not_open_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(state="MERGED"), CONF, BY, True, True))

    def test_non_main_base_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(baseRefName="epic.owner-harness"), CONF, BY, True, True))

    def test_conflicting_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(mergeable="CONFLICTING"), CONF, BY, True, True))

    def test_failing_check_refuses(self):
        self.assertIsNotNone(pr.land_refusal(
            _ok_pr(statusCheckRollup=[{"conclusion": "FAILURE"}]), CONF, BY, True, True))

    def test_pending_check_refuses(self):
        self.assertIsNotNone(pr.land_refusal(
            _ok_pr(statusCheckRollup=[{"state": "PENDING"}]), CONF, BY, True, True))

    def test_no_checks_is_green(self):
        self.assertIsNone(pr.land_refusal(_ok_pr(statusCheckRollup=[]), CONF, BY, True, True))

    def test_auto_title_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(title="claude/merge-node"), CONF, BY, True, True))

    def test_empty_body_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(body="  "), CONF, BY, True, True))


class NodeAdmittedIn(unittest.TestCase):
    """The lander's identity is the trunk's to answer (done-line 0049):
    admitted by a node_real's real side, superseded by its stage side,
    self-asserted when never named at all."""

    def test_never_named_is_not_admitted(self):
        self.assertFalse(pr.node_admitted_in("", "merge-node.claude.v1"))

    def test_real_side_admits(self):
        dump = ('{"type":"node_real","stage_node":"merge-node.claude.v0",'
                '"real_node":"merge-node.claude.v1","by":"bdo","id":"adm.1"}')
        self.assertTrue(pr.node_admitted_in(dump, "merge-node.claude.v1"))
        # the superseded id does not land — and never-named ids never did
        self.assertFalse(pr.node_admitted_in(dump, "merge-node.claude.v0"))
        self.assertFalse(pr.node_admitted_in(dump, "merge-node.claude.v9"))

    def test_later_supersession_revokes(self):
        dump = "\n".join([
            '{"type":"node_real","stage_node":"seat.v0","real_node":"seat.v1","by":"bdo","id":"adm.1"}',
            '{"type":"node_real","stage_node":"seat.v1","real_node":"seat.v2","by":"bdo","id":"adm.2"}',
        ])
        self.assertFalse(pr.node_admitted_in(dump, "seat.v1"))
        self.assertTrue(pr.node_admitted_in(dump, "seat.v2"))

    def test_torn_line_is_folded_away(self):
        dump = ('{"type":"node_real","stage_node":"a","real_node":"b","by":"bdo"\n'
                '{"type":"node_real","stage_node":"x","real_node":"y","by":"bdo","id":"adm.2"}')
        self.assertTrue(pr.node_admitted_in(dump, "y"))
        self.assertFalse(pr.node_admitted_in(dump, "b"))


class ArcConfirmedIn(unittest.TestCase):
    def test_latest_enabled_confirmation_wins(self):
        dump = "\n".join([
            '{"type":"arc_confirmed","epic":"e","by":"bdo","enabled":true,"id":"adm.1"}',
            '{"type":"arc_confirmed","epic":"e","by":"bdo","enabled":false,"id":"adm.2"}',
        ])
        self.assertIsNone(pr.arc_confirmed_in(dump, "e"))

    def test_only_bdo_confirms(self):
        dump = '{"type":"arc_confirmed","epic":"e","by":"claude","enabled":true,"id":"adm.x"}'
        self.assertIsNone(pr.arc_confirmed_in(dump, "e"))

    def test_confirmed_returns_id(self):
        dump = '{"type":"arc_confirmed","epic":"e","by":"bdo","enabled":true,"id":"adm.ok"}'
        self.assertEqual(pr.arc_confirmed_in(dump, "e"), "adm.ok")


class MergeReceiptReachesTheLog(unittest.TestCase):
    """The receipt is the land's only record (D-5). The bug it fixes: it was
    written to a throwaway worktree and lost, so the log was blind to real
    merges. _merge_receipt builds the record; _append_receipt_line is the
    torn-tail-tolerant write the trunk push uses — it must hold even when a
    prior line lacks its trailing newline."""

    def test_receipt_carries_the_authorization(self):
        r = pr._merge_receipt(45, "epic.owner-harness", "merge-node.claude.v0",
                              "adm.728a87a9ca48", "claude/mock-shame",
                              pr_author="claude-author",
                              non_author_attested=True)
        self.assertEqual(r["id"], "rcp.merge.45")
        self.assertEqual(r["kind"], "merge")
        self.assertEqual(r["verdict"], "landed")
        self.assertEqual(r["authorized_by"], "adm.728a87a9ca48")
        self.assertEqual(r["pr"], 45)
        self.assertEqual(r["pr_author"], "claude-author")
        self.assertTrue(r["non_author_attested"])

    def test_receipt_carries_the_landed_atoms_sorted(self):
        # D-13: the write-through carbon copy — the merge reflects *which* atoms
        # reached main, so the per-atom↔per-PR namespace can join (done-line 0124).
        r = pr._merge_receipt(7, "e", "n", "adm.x", "h",
                              landed_atoms=["atom.b.v0", "atom.a.v0"])
        self.assertEqual(r["landed_atoms"], ["atom.a.v0", "atom.b.v0"])

    def test_receipt_without_atoms_is_honest_empty_not_missing(self):
        # an empty list (a PR that landed no atom file) is distinct from the
        # missing field on the 90 pre-D-13 receipts ('never computed'); the field
        # is always present going forward so the reader can trust it.
        r = pr._merge_receipt(8, "e", "n", "adm.x", "h")
        self.assertEqual(r["landed_atoms"], [])
        self.assertIn("landed_atoms", r)

    def test_append_is_torn_tail_tolerant(self):
        import json as _json
        import tempfile
        from pathlib import Path as _P
        with tempfile.TemporaryDirectory() as d:
            p = _P(d) / "receipts.jsonl"
            p.write_bytes(b'{"id":"rcp.merge.1"}')  # a prior line with NO trailing newline
            pr._append_receipt_line(p, {"id": "rcp.merge.2"})
            ids = [_json.loads(l)["id"] for l in p.read_text().splitlines() if l.strip()]
            self.assertEqual(ids, ["rcp.merge.1", "rcp.merge.2"])


class CmdLandUnpacksAtomFacts(unittest.TestCase):
    """The write-through join (D-13): cmd_land reaches with git for the PR's
    atom facts BEFORE the merge and carries them on the receipt. The seam that
    breaks silently: _range_atom_facts returns THREE values
    (atom_ids, receipt_ids, phrasing_clean), and cmd_land must unpack all three
    or every land — dry-run included — dies with ValueError before anything is
    judged. No existing test exercised this path, so it shipped CI-green; these
    teeth make the crash class visible (§10), and pin that the receipt's
    landed_atoms is the FIRST facts value (the atom ids), never receipt_ids.
    """

    # the real three-value signature of _range_atom_facts, with each value
    # distinct so a fix that grabbed the wrong element is caught.
    FACTS = (["atom.alpha.v0"], ["rcp.unrelated"], True)

    def _land_ns(self, dry_run):
        return argparse.Namespace(
            number=99, epic="epic.owner-harness", by=BY, dry_run=dry_run,
            attest_non_author=True)

    def _fake_run(self, recorder=None):
        """A _run that answers gh pr view with a landable PR and swallows the
        git fetch / gh pr merge subprocess calls."""
        def run(args, *a, **k):
            if recorder is not None:
                recorder.append(args)
            if args[:3] == ["gh", "pr", "view"]:
                import json as _json
                return _json.dumps(_ok_pr())
            return ""
        return run

    def test_dry_run_unpacks_three_value_facts_without_crashing(self):
        # the crash the report names: with a 2-value unpack this raises
        # ValueError; with the real 3-value unpack it reports the atoms.
        import contextlib
        import io
        with mock.patch.object(pr, "_run", self._fake_run()), \
             mock.patch.object(pr, "_trunk_admissions", lambda: ""), \
             mock.patch.object(pr, "arc_confirmed_in", lambda *_: CONF), \
             mock.patch.object(pr, "node_admitted_in", lambda *_: True), \
             mock.patch.object(pr, "_range_atom_facts", lambda *_: self.FACTS):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                pr.cmd_land(self._land_ns(dry_run=True))
        self.assertIn("DRY RUN", out.getvalue())
        self.assertIn("atom.alpha.v0", out.getvalue())  # the atom ids, surfaced

    def test_land_receipt_carries_atom_ids_not_receipt_ids(self):
        # the real behavior, end to end: a non-dry land builds the receipt from
        # the FIRST facts value (atom ids). receipt_ids/phrasing are the off-log
        # gate's facts, not the merge receipt's — they must not leak in.
        import contextlib
        import io
        captured = {}

        def fake_push(receipt):
            captured["receipt"] = receipt
            return True

        with mock.patch.object(pr, "_run", self._fake_run()), \
             mock.patch.object(pr, "_trunk_admissions", lambda: ""), \
             mock.patch.object(pr, "arc_confirmed_in", lambda *_: CONF), \
             mock.patch.object(pr, "node_admitted_in", lambda *_: True), \
             mock.patch.object(pr, "_range_atom_facts", lambda *_: self.FACTS), \
             mock.patch.object(pr, "_push_receipt_to_trunk", fake_push):
            with contextlib.redirect_stdout(io.StringIO()):
                pr.cmd_land(self._land_ns(dry_run=False))

        self.assertIn("receipt", captured)
        self.assertEqual(captured["receipt"]["landed_atoms"], ["atom.alpha.v0"])
        # the off-log gate's receipt_ids must never be mistaken for landed atoms
        self.assertNotIn("rcp.unrelated", captured["receipt"]["landed_atoms"])


class ConfirmIsBdosStamp(unittest.TestCase):
    """`confirm` pushes bdo's arc stamp to the trunk so the merge-node can
    read it (the seam confirm-arc alone never crossed). It is the owner's
    act: anyone but bdo is refused before any git runs (D-4)."""

    def test_refuses_non_bdo_before_touching_git(self):
        ns = argparse.Namespace(epic="epic.owner-harness", by="claude", off=False)
        with self.assertRaises(SystemExit):
            pr.cmd_confirm(ns)

    def test_refuses_empty_by(self):
        ns = argparse.Namespace(epic="epic.owner-harness", by="", off=False)
        with self.assertRaises(SystemExit):
            pr.cmd_confirm(ns)


class ConfirmFromRefValidatesNeverBypasses(unittest.TestCase):
    """`confirm --from-ref` resolves issue #245's deadlock — an epic introduced
    by an unlanded PR (its record only on the PR branch, not the trunk) can be
    confirmed by reading the epic from that ref. The §10 teeth: --from-ref
    RELOCATES where the epic is validated; it is never a bypass. A ref that does
    not actually carry the epic must still refuse — epic_id_in_blob is that pure
    check, over the bytes git hands back."""

    EPIC = "epic.three-marks"
    BLOB = '{"epic": {"id": "epic.three-marks", "owner": "bdo"}}'

    def test_ref_carrying_the_epic_validates(self):
        self.assertTrue(pr.epic_id_in_blob(self.BLOB, self.EPIC))

    def test_ref_carrying_a_different_epic_is_refused(self):
        # the teeth: the ref exists and is a valid epic file, but for ANOTHER
        # arc — confirming this epic against it must not pass (not a bypass).
        other = '{"epic": {"id": "epic.owner-harness"}}'
        self.assertFalse(pr.epic_id_in_blob(other, self.EPIC))

    def test_absent_or_garbage_blob_is_refused(self):
        # an empty blob (the file does not exist at the ref) or non-JSON is no
        # epic at all — never read as carrying it.
        for blob in ("", "   ", "not json", "{}", '{"epic": {}}', "[]"):
            self.assertFalse(pr.epic_id_in_blob(blob, self.EPIC))


class EstablishPlanIsTheBootstrapDecision(unittest.TestCase):
    """The pure decision `cmd_confirm` makes about a new arc (the
    confirm-new-arc-bootstrap hardening). The §10 teeth: a brand-new arc with
    NO source ref is refused with the paved path named — never waved through to
    a raw "nothing to commit" git failure."""

    def test_epic_on_trunk_confirms(self):
        action, _ = pr.establish_plan(True, "")
        self.assertEqual(action, "confirm")

    def test_epic_on_trunk_confirms_even_with_a_ref(self):
        # already on the trunk wins regardless of a ref — no re-establishment
        action, _ = pr.establish_plan(True, "claude/intro")
        self.assertEqual(action, "confirm")

    def test_new_epic_with_a_source_ref_establishes(self):
        action, _ = pr.establish_plan(False, "claude/intro")
        self.assertEqual(action, "establish")

    def test_new_epic_without_a_source_ref_refuses_naming_the_flag(self):
        action, reason = pr.establish_plan(False, "")
        self.assertEqual(action, "refuse")
        self.assertIn("--from-ref", reason)  # the paved path is named

    def test_blank_ref_is_treated_as_no_ref(self):
        action, reason = pr.establish_plan(False, "   ")
        self.assertEqual(action, "refuse")
        self.assertIn("--from-ref", reason)


if __name__ == "__main__":
    unittest.main()
