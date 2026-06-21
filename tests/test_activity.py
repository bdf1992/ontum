"""§10 for the activity-accounting fold (loop/activity.py, done-line 0143).

The fold accounts for the harness's own hooks: it reconciles the declared
data-practices register against the live .claude/settings.json wiring. Its teeth
refuse two ways — an undeclared collector (a wired hook accounted nowhere) and a
ghost (a declared entry no longer wired).

These tests prove (a) the committed register is honest — it accounts for exactly
what is wired, no more, no less — and (b) the check is NOT vacuous: a fabricated
undeclared hook, a ghost, and a codex-layer ghost are each caught. A validator
that always returned "fine" would fail every TestTeeth case.
"""

import unittest

from loop import activity


def _reg(*keys, wiring="claude", witnessed=False):
    return {"hooks": {k: {"wiring": wiring, "collects": ["x"],
                          "uses_for": "y", "sink": "z", "witnessed": witnessed}
                      for k in keys}}


class TestRegisterHonest(unittest.TestCase):
    def test_committed_register_accounts_for_live_wiring(self):
        result = activity.account(activity.REPO)
        self.assertFalse(result["register_missing"], "register not found")
        self.assertFalse(result["settings_missing"], "settings not found")
        self.assertEqual(result["violations"], [],
                         f"committed register diverges from wiring: "
                         f"{result['violations']}")

    def test_every_live_hook_is_accounted(self):
        result = activity.account(activity.REPO)
        # the floor of "account for all activity": nothing wired is undeclared.
        self.assertEqual(result["undeclared"], [], result["undeclared"])
        self.assertTrue(result["accounted"], "no hooks accounted at all")


class TestCanonicalKey(unittest.TestCase):
    """The key is what the teeth compare; it must fold phases of one hook
    together and split genuinely distinct activities of one pen apart."""

    def test_post_flag_is_same_hook(self):
        a = activity.canonical_key('python ".../command_guard.py"')
        b = activity.canonical_key('python ".../command_guard.py" --post')
        self.assertEqual(a, b)
        self.assertEqual(a, "command_guard")

    def test_module_invocation_keyed_by_last_segment(self):
        self.assertEqual(activity.canonical_key("python -m loop.summon --hook"),
                         "summon")

    def test_pen_subcommand_splits_distinct_activities(self):
        self.assertEqual(activity.canonical_key('python ".../git.py" sync --hook'),
                         "git:sync")
        self.assertEqual(activity.canonical_key('python ".../git.py" garden --hook'),
                         "git:garden")

    def test_event_positional_is_not_a_subcommand(self):
        # the codex probe is wired `probe_codex.py PreToolUse`; the event name
        # is routing, not a verb, so it folds to one key across events.
        for ev in ("PreToolUse", "PostToolUse", "PermissionRequest"):
            self.assertEqual(
                activity.canonical_key(f"python fence/probe_codex.py {ev}"),
                "probe_codex")


class TestTeeth(unittest.TestCase):
    """The check must be able to bite — fabricated divergences are caught. If
    any of these passed, the gateway's accounting would be decorative."""

    def test_clean_reconcile_has_no_violations(self):
        # positive control: register and wiring agree exactly.
        live = {"a": ["SessionStart"], "b": ["Stop"]}
        self.assertEqual(activity.validate(_reg("a", "b"), live), [])

    def test_undeclared_collector_is_caught(self):
        # a wired hook with no register entry — a silent collector.
        live = {"a": ["SessionStart"], "ghost_collector": ["UserPromptSubmit"]}
        v = activity.validate(_reg("a"), live)
        self.assertIn("ghost_collector", v)

    def test_ghost_entry_is_caught(self):
        # a claude-wired register entry whose hook is no longer wired.
        live = {"a": ["SessionStart"]}
        v = activity.validate(_reg("a", "retired_hook"), live)
        self.assertIn("retired_hook", v)

    def test_codex_entry_present_in_layer_is_not_a_violation(self):
        reg = _reg("probe_codex", wiring="codex")
        v = activity.validate(reg, live={}, codex={"probe_codex"})
        self.assertEqual(v, [])

    def test_codex_entry_absent_from_present_layer_is_a_ghost(self):
        # the codex layer IS present (a set was provided) but does not carry it.
        reg = _reg("probe_codex", wiring="codex")
        v = activity.validate(reg, live={}, codex=set())
        self.assertIn("probe_codex", v)

    def test_codex_entry_unverified_when_layer_absent_is_not_a_violation(self):
        # no codex layer on disk: deferred, not failed (done-line 0143 scope).
        reg = _reg("probe_codex", wiring="codex")
        self.assertEqual(activity.validate(reg, live={}, codex=None), [])


if __name__ == "__main__":
    unittest.main()
