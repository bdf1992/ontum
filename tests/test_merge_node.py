"""Done-line 0033 (the hand): the merge-node lands a confirmed-arc PR on main.

bdo amended `bdo merges` (2026-06-11): he no longer merges — an independent
merge-node lands what he confirmed. The guard is the safety: it refuses by
default and lands only a confirmed-arc, green, written, non-draft,
non-conflicting PR based on main, as a named node.

The §10 bar: a PR that is perfect on every mechanical axis — open, green,
written, non-draft, based on main — must STILL refuse to land when bdo has
not confirmed its arc. "Mechanically ready" and "authorized" are each locally
fine, and they refuse to fit: the merge-node never lands an unauthorized arc,
because bdo's confirmation is the independent approval that keeps no one
signing their own line (D-4). The guard logic is tested pure; the gh/git
plumbing is the thin shell around it.
"""

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEN_PATH = ROOT / ".claude" / "skills" / "branch-ritual" / "pr.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pr = _load("pr_pen_mn", PEN_PATH)


def _ready_pr(**over):
    """A PR that is mechanically perfect — every axis green but the one the
    test bends."""
    info = {
        "state": "OPEN", "baseRefName": "main", "headRefName": "claude/x",
        "isDraft": False, "mergeable": "MERGEABLE",
        "title": "a real written title, not the branch", "body": "the story.",
        "statusCheckRollup": [], "author": {"login": "bdf1992"},
    }
    info.update(over)
    return info


class TestTheTeeth(unittest.TestCase):
    """§10: mechanical readiness is not authorization."""

    def test_perfect_pr_without_arc_confirmation_refuses(self):
        reason = pr.land_refusal(_ready_pr(), confirmation=None,
                                 by="merge-node.v0", by_admitted=True)
        self.assertIsNotNone(reason)
        self.assertIn("confirmed", reason)

    def test_same_pr_with_confirmation_would_land(self):
        # the control: the only thing that changed is bdo's confirmation
        self.assertIsNone(
            pr.land_refusal(_ready_pr(), confirmation="adm.arc.1",
                            by="merge-node.v0", by_admitted=True))


class TestGuards(unittest.TestCase):
    def _refused(self, info, conf="adm.arc.1", by="merge-node.v0",
                 by_admitted=True):
        return pr.land_refusal(info, conf, by, by_admitted)

    def test_unnamed_node_refuses(self):  # no one signs their own line
        self.assertIsNotNone(self._refused(_ready_pr(), by=""))

    def test_closed_pr_refuses(self):
        self.assertIsNotNone(self._refused(_ready_pr(state="MERGED")))

    def test_non_main_base_refuses(self):
        self.assertIn("integrate", self._refused(_ready_pr(baseRefName="epic.x")))

    def test_draft_refuses(self):
        self.assertIn("draft", self._refused(_ready_pr(isDraft=True)))

    def test_conflicting_refuses(self):
        self.assertIn("conflict", self._refused(_ready_pr(mergeable="CONFLICTING")))

    def test_auto_title_refuses(self):
        self.assertIsNotNone(self._refused(_ready_pr(title="claude/x")))

    def test_empty_body_refuses(self):
        self.assertIsNotNone(self._refused(_ready_pr(body="  ")))

    def test_all_green_and_confirmed_lands(self):
        self.assertIsNone(self._refused(_ready_pr()))


class TestChecksGreen(unittest.TestCase):
    def test_no_checks_is_green(self):
        self.assertTrue(pr.checks_green([]))
        self.assertTrue(pr.checks_green(None))

    def test_all_success_is_green(self):
        self.assertTrue(pr.checks_green(
            [{"conclusion": "SUCCESS"}, {"state": "SUCCESS"}, {"conclusion": "SKIPPED"}]))

    def test_a_pending_check_is_not_green(self):
        self.assertFalse(pr.checks_green([{"state": "PENDING"}]))

    def test_a_failure_is_not_green(self):
        self.assertFalse(pr.checks_green([{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}]))


class TestArcConfirmedIn(unittest.TestCase):
    def _log(self, *records):
        import json
        return "\n".join(json.dumps(r) for r in records)

    def test_confirmed_by_bdo_returns_id(self):
        text = self._log({"id": "adm.1", "type": "arc_confirmed",
                          "epic": "epic.x", "by": "bdo", "enabled": True})
        self.assertEqual(pr.arc_confirmed_in(text, "epic.x"), "adm.1")

    def test_confirmed_by_non_bdo_is_none(self):
        text = self._log({"id": "adm.1", "type": "arc_confirmed",
                          "epic": "epic.x", "by": "claude", "enabled": True})
        self.assertIsNone(pr.arc_confirmed_in(text, "epic.x"))

    def test_withdrawn_returns_none(self):
        text = self._log(
            {"id": "adm.1", "type": "arc_confirmed", "epic": "epic.x", "by": "bdo", "enabled": True},
            {"id": "adm.2", "type": "arc_confirmed", "epic": "epic.x", "by": "bdo", "enabled": False})
        self.assertIsNone(pr.arc_confirmed_in(text, "epic.x"))

    def test_absent_is_none(self):
        self.assertIsNone(pr.arc_confirmed_in("", "epic.x"))

    def test_torn_line_tolerated(self):
        text = '{"id":"adm.1","type":"arc_confirmed","epic":"epic.x","by":"bdo"\n' \
               + '{"id":"adm.2","type":"arc_confirmed","epic":"epic.x","by":"bdo","enabled":true}'
        self.assertEqual(pr.arc_confirmed_in(text, "epic.x"), "adm.2")


if __name__ == "__main__":
    unittest.main()
