"""The merge-node's hand refuses by default (pr.py land verb).

land_refusal is the gate between an open PR and the trunk. Its job is to say
*no* unless every condition holds at once — so these tests are mostly the
no's: each locally-fine PR that is missing one thing must still be refused.
The §10 teeth: a green, written, mergeable PR whose arc bdo has NOT confirmed
is locally fine in every way the PR can see, yet it must not land — the
confirmation is the independent stamp (D-4), and its absence refuses to fit.
"""

import importlib.util
import unittest
from pathlib import Path

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
    }
    info.update(over)
    return info


CONF = "adm.deadbeef"  # a stand-in for a real arc_confirmed admission id
BY = "merge-node.claude.v0"


class LandRefusal(unittest.TestCase):
    def test_full_house_lands(self):
        self.assertIsNone(pr.land_refusal(_ok_pr(), CONF, BY))

    def test_unconfirmed_arc_refuses_even_when_otherwise_perfect(self):
        # the §10 case: nothing the PR can see is wrong; the missing human
        # stamp is what refuses to fit.
        reason = pr.land_refusal(_ok_pr(), None, BY)
        self.assertIsNotNone(reason)
        self.assertIn("confirm", reason.lower())

    def test_no_by_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(), CONF, ""))

    def test_draft_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(isDraft=True), CONF, BY))

    def test_not_open_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(state="MERGED"), CONF, BY))

    def test_non_main_base_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(baseRefName="epic.owner-harness"), CONF, BY))

    def test_conflicting_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(mergeable="CONFLICTING"), CONF, BY))

    def test_failing_check_refuses(self):
        self.assertIsNotNone(pr.land_refusal(
            _ok_pr(statusCheckRollup=[{"conclusion": "FAILURE"}]), CONF, BY))

    def test_pending_check_refuses(self):
        self.assertIsNotNone(pr.land_refusal(
            _ok_pr(statusCheckRollup=[{"state": "PENDING"}]), CONF, BY))

    def test_no_checks_is_green(self):
        self.assertIsNone(pr.land_refusal(_ok_pr(statusCheckRollup=[]), CONF, BY))

    def test_auto_title_refuses(self):
        self.assertIsNotNone(
            pr.land_refusal(_ok_pr(title="claude/merge-node"), CONF, BY))

    def test_empty_body_refuses(self):
        self.assertIsNotNone(pr.land_refusal(_ok_pr(body="  "), CONF, BY))


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


if __name__ == "__main__":
    unittest.main()
