#!/usr/bin/env python3
"""The standing-surface projection (done-line 0071): the pure fold under the
inbound surface twin. These tests pin the two properties the done-line names —
the projection is surface-agnostic (no vendor in the fold), and the delta is
level-triggered (unchanged -> empty, a change -> one tick, consumed -> silent).
"""

import unittest

from loop import standing


def _item(kind, number, title, branch=None):
    it = {"kind": kind, "number": number, "title": title}
    if branch:
        it["branch"] = branch
    return it


class SurfaceAgnostic(unittest.TestCase):
    """The fold names no vendor: it projects whatever normalized items it is
    handed, including kinds GitHub never emits — the 'not glued to GH' law."""

    def test_projects_arbitrary_kinds(self):
        # a surface that is not GitHub at all: a phone inbox of 'task' items
        items = [_item("task", 3, "ship the thing"),
                 _item("task", 1, "read the doc")]
        text = standing.format_standing("phone-inbox", items)
        self.assertIn("phone-inbox", text)
        self.assertIn("2 tasks open", text)
        self.assertIn("ship the thing", text)
        # nothing GitHub-shaped leaked into the pure projection
        self.assertNotIn("gh ", text)
        self.assertNotIn("github", text.lower())

    def test_github_shaped_snapshot_reads_naturally(self):
        items = [_item("issue", 113, "Daily arc digest — 2026-06-13"),
                 _item("pr", 128, "The pen is the write authority",
                       branch="claude/pen-carbon-copy")]
        text = standing.format_standing("github-issues", items)
        self.assertIn("1 issue, 8 PRs".split(",")[0], text)  # '1 issue'
        self.assertIn("issue #113", text)
        self.assertIn("pr #128", text)
        self.assertIn("(claude/pen-carbon-copy)", text)  # PR carries its branch

    def test_counts_pluralize(self):
        self.assertEqual(standing.kind_label("issue", 1), "1 issue")
        self.assertEqual(standing.kind_label("pr", 8), "8 PRs")
        self.assertEqual(standing.kind_label("task", 1), "1 task")
        self.assertEqual(standing.kind_label("task", 2), "2 tasks")

    def test_empty_open_set_is_awareness_not_silence(self):
        # SessionStart still wants a signal: 'nothing open' is information
        text = standing.format_standing("github-issues", [])
        self.assertIn("no open work", text)


class LevelTriggeredDelta(unittest.TestCase):
    """The anti-spam contract: the delta is a pure set difference over ids;
    once the baseline absorbs the change, the same snapshot ticks nothing."""

    def setUp(self):
        self.items = [_item("issue", 113, "digest"),
                      _item("pr", 128, "carbon copy"),
                      _item("pr", 123, "off-log gate")]

    def test_unchanged_set_is_empty(self):
        baseline = standing.snapshot_ids(self.items)
        delta = standing.compute_delta(baseline, self.items)
        self.assertTrue(standing.delta_is_empty(delta))
        self.assertEqual(standing.format_delta("github-issues", delta), "")

    def test_a_new_item_ticks_up_once(self):
        baseline = standing.snapshot_ids(self.items)
        grown = self.items + [_item("pr", 129, "a fresh PR")]
        delta = standing.compute_delta(baseline, grown)
        self.assertEqual(len(delta["added"]), 1)
        self.assertEqual(delta["added"][0]["number"], 129)
        self.assertEqual(delta["removed"], [])
        line = standing.format_delta("github-issues", delta)
        self.assertIn("+1 / -0", line)
        self.assertIn("a fresh PR", line)
        # the whole list is NOT re-printed — only the one change (anti-spam)
        self.assertNotIn("digest", line)
        self.assertNotIn("off-log gate", line)

    def test_a_closed_item_ticks_down(self):
        baseline = standing.snapshot_ids(self.items)
        shrunk = [it for it in self.items if it["number"] != 123]
        delta = standing.compute_delta(baseline, shrunk)
        self.assertEqual(delta["added"], [])
        self.assertEqual(delta["removed"], ["pr#123"])
        line = standing.format_delta("github-issues", delta)
        self.assertIn("-1", line)
        self.assertIn("pr#123 closed", line)

    def test_consuming_the_change_returns_to_silence(self):
        # the hook updates the baseline after ticking; the next identical poll
        # must say nothing — the property that stops the spam
        baseline = standing.snapshot_ids(self.items)
        grown = self.items + [_item("pr", 129, "fresh")]
        first = standing.compute_delta(baseline, grown)
        self.assertFalse(standing.delta_is_empty(first))
        new_baseline = standing.snapshot_ids(grown)  # hook absorbs the change
        second = standing.compute_delta(new_baseline, grown)
        self.assertTrue(standing.delta_is_empty(second))

    def test_simultaneous_add_and_remove(self):
        baseline = standing.snapshot_ids(self.items)
        churned = [_item("issue", 113, "digest"),
                   _item("pr", 128, "carbon copy"),
                   _item("pr", 130, "newer")]  # 123 gone, 130 arrived
        delta = standing.compute_delta(baseline, churned)
        self.assertEqual([it["number"] for it in delta["added"]], [130])
        self.assertEqual(delta["removed"], ["pr#123"])
        line = standing.format_delta("github-issues", delta)
        self.assertIn("+1 / -1", line)


if __name__ == "__main__":
    unittest.main()
