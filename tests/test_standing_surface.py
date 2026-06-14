#!/usr/bin/env python3
"""The standing-surface hook (done-line 0071): the adapter/baseline/throttle
layer over the pure projection. These tests pin the behaviours that only the
hook owns — silence when nothing is registered, an adapterless kind named (not
guessed), the SessionStart picture vs the UserPromptSubmit delta, and the
throttle that keeps the per-prompt poll from taxing every turn.

The hook lives outside the package (`.claude/hooks/`), so it is loaded by path.
Its one network reach (the gh adapter) is replaced by a fake here — the test
never touches GitHub, which is the 'not glued' property made executable.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HOOK_PATH = (Path(__file__).resolve().parents[1]
             / ".claude" / "hooks" / "standing_surface.py")


def _load_hook():
    spec = importlib.util.spec_from_file_location("standing_surface", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _item(kind, number, title, branch=None):
    it = {"kind": kind, "number": number, "title": title}
    if branch:
        it["branch"] = branch
    return it


class HookBehaviour(unittest.TestCase):
    def setUp(self):
        self.hook = _load_hook()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.hook.STATE = Path(self.tmp.name) / "standing-state.json"
        # default: a registered github-issues surface with a fake adapter
        self._snapshot = [_item("issue", 113, "digest"),
                          _item("pr", 128, "carbon copy")]
        self.hook.registered_github_surface = lambda: (
            "github-issues", "github-issues", "owner/repo")
        self.hook.ADAPTERS = {"github-issues": lambda addr: list(self._snapshot)}

    def _run(self, name, now, sid="s1"):
        return self.hook.run({"hook_event_name": name, "session_id": sid}, now)

    def test_silent_when_nothing_registered(self):
        self.hook.registered_github_surface = lambda: None
        self.assertEqual(self._run("SessionStart", 1000.0), "")

    def test_adapterless_kind_is_named_at_start_silent_after(self):
        self.hook.registered_github_surface = lambda: (
            "phone-inbox", "phone-inbox", "addr")
        self.hook.ADAPTERS = {"github-issues": lambda a: []}  # no phone adapter
        start = self._run("SessionStart", 1000.0)
        self.assertIn("phone-inbox", start)
        self.assertIn("no adapter", start)
        # named, never an actual gh-shaped guess: no gh command was emitted
        self.assertNotIn("gh issue", start)
        self.assertNotIn("gh pr", start)
        self.assertEqual(self._run("UserPromptSubmit", 2000.0), "")

    def test_sessionstart_paints_full_picture_and_seeds_baseline(self):
        text = self._run("SessionStart", 1000.0)
        self.assertIn("issue #113", text)
        self.assertIn("pr #128", text)
        state = json.loads(self.hook.STATE.read_text(encoding="utf-8"))
        self.assertEqual(len(state["s1"]["baseline"]), 2)

    def test_delta_ticks_up_past_the_throttle(self):
        self._run("SessionStart", 1000.0)  # baseline = {113, 128}
        self._snapshot.append(_item("pr", 129, "fresh PR"))
        # well past the throttle window
        later = 1000.0 + self.hook.POLL_THROTTLE_SECONDS + 1
        text = self._run("UserPromptSubmit", later)
        self.assertIn("+1 / -0", text)
        self.assertIn("fresh PR", text)
        self.assertNotIn("digest", text)  # only the change, not the whole list

    def test_throttle_blocks_the_poll_within_the_window(self):
        self._run("SessionStart", 1000.0)
        self._snapshot.append(_item("pr", 129, "fresh PR"))
        # within the window: no fetch, no tick, even though the surface changed
        soon = 1000.0 + self.hook.POLL_THROTTLE_SECONDS - 1
        self.assertEqual(self._run("UserPromptSubmit", soon), "")

    def test_consuming_the_change_returns_to_silence(self):
        self._run("SessionStart", 1000.0)
        self._snapshot.append(_item("pr", 129, "fresh PR"))
        t1 = 1000.0 + self.hook.POLL_THROTTLE_SECONDS + 1
        self.assertNotEqual(self._run("UserPromptSubmit", t1), "")  # ticks once
        t2 = t1 + self.hook.POLL_THROTTLE_SECONDS + 1
        self.assertEqual(self._run("UserPromptSubmit", t2), "")  # then silent

    def test_parallel_sessions_keep_separate_baselines(self):
        # one managing session + a fleet sibling must not reset each other
        self._run("SessionStart", 1000.0, sid="A")
        self._snapshot.append(_item("pr", 129, "fresh"))
        self._run("SessionStart", 1000.0, sid="B")  # B baselines the grown set
        t = 1000.0 + self.hook.POLL_THROTTLE_SECONDS + 1
        # A still sees the +1 it never absorbed; B (baselined later) is silent
        self.assertIn("+1", self._run("UserPromptSubmit", t, sid="A"))
        self.assertEqual(self._run("UserPromptSubmit", t, sid="B"), "")


if __name__ == "__main__":
    unittest.main()
