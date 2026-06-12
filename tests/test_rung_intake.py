"""Done-line 0051: the rung-intake pen carries bdo's trust grants
deterministically, and refuses to ask what cannot be granted.

The pen never judges intent (the SKILL does) and never runs admit-rung. What
it must get right: the (class, capability) an issue carries — both names,
because admit-rung needs both — and the refusal-at-open. The §10 cases: a
half-marker naming only the class must not parse (the pen never hands the
session a capability it guessed); and the LOCKED rung (ontum-touch) must be
refused at open — a rung-confirm issue for it would be a gesture-shaped key
to a door loop/trust.py promises stays locked, locally plausible and exactly
wrong. The join is pinned too: an admission written through the one write
path (loop.node.admit_rung) is what flips the spawn rail from refusal to
pass — the gesture this surface carries is the one the rail obeys.
"""

import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rung = _load("rung_intake", ROOT / ".claude" / "skills" / "rung-intake" / "rung.py")
spawn = _load("spawn_guard_for_rung", ROOT / ".claude" / "hooks" / "spawn_guard.py")

from loop import node as loop_node  # noqa: E402
from loop import trust  # noqa: E402


class NamesFromBody(unittest.TestCase):
    def test_round_trips_both_names(self):
        body = "briefing\n\n" + rung.marker("branded-subagent", "judge")
        self.assertEqual(rung.names_from_body(body),
                         ("branded-subagent", "judge"))

    def test_no_marker_is_not_ours(self):
        self.assertIsNone(rung.names_from_body("a plain issue, no marker"))
        self.assertIsNone(rung.names_from_body(""))
        self.assertIsNone(rung.names_from_body(None))

    def test_half_marker_is_not_a_marker(self):
        # a marker naming only the class (no capability=) must not parse — the
        # pen never hands the session a rung it had to guess.
        half = "<!-- ontum:rung-confirm class=branded-subagent -->"
        self.assertIsNone(rung.names_from_body(half))

    def test_sibling_markers_are_not_ours(self):
        self.assertIsNone(rung.names_from_body(
            "<!-- ontum:realness-confirm stage=s node=n -->"))
        self.assertIsNone(rung.names_from_body(
            "<!-- ontum:arc-confirm epic=epic.experience-layer -->"))


class OpenRefusal(unittest.TestCase):
    """The pen opens only questions the admission pen could answer."""

    def test_locked_rung_is_refused_at_open(self):
        reason = rung.open_refusal("branded-subagent", trust.LOCKED)
        self.assertIsNotNone(reason)
        self.assertIn("LOCKED", reason)

    def test_unknown_class_is_refused(self):
        self.assertIsNotNone(rung.open_refusal("self-appointed-class", "judge"))

    def test_unknown_capability_is_refused(self):
        self.assertIsNotNone(rung.open_refusal("branded-subagent", "omnipotence"))

    def test_grantable_rung_opens(self):
        self.assertIsNone(rung.open_refusal("branded-subagent", "judge"))


class BdoComment(unittest.TestCase):
    def _c(self, login, body):
        return {"author": {"login": login}, "body": body}

    def test_picks_owners_last_word_among_many(self):
        comments = [
            self._c("ontum-bot", "opened for confirmation"),
            self._c("bdf1992", "hmm"),
            self._c("someone-else", "i say yes"),
            self._c("bdf1992", "grant it"),
        ]
        self.assertEqual(rung.bdo_comment(comments, "bdf1992"), "grant it")

    def test_no_owner_comment_is_empty(self):
        self.assertEqual(rung.bdo_comment([self._c("bot", "ping")], "bdf1992"), "")


class AdmissionFlipsTheRail(unittest.TestCase):
    """The join (§10 both ways): with a prompt-pinned node and an empty
    ladder the rail refuses; the admission written through the ONE write path
    — loop.node.admit_rung, the act the SKILL runs on bdo's clear grant —
    is exactly what flips it to pass. And a non-bdo signer writes nothing:
    the gesture cannot be forged from this side."""

    def setUp(self):
        self.ai = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.ai, ignore_errors=True)
        (self.ai / "nodes").mkdir()
        (self.ai / "log").mkdir()
        (self.ai / "nodes" / "demo.node.v1.md").write_text(
            "# demo node prompt", encoding="utf-8")
        self.adm_path = self.ai / "log" / "admissions.jsonl"

    def test_refused_before_granted_after(self):
        self.assertIsNotNone(
            spawn.node_spawn_refusal("demo.node.v1", root=self.ai))
        adm = loop_node.admit_rung(self.ai, "branded-subagent", "judge", "bdo")
        self.assertIsNotNone(adm)
        self.assertIsNone(
            spawn.node_spawn_refusal("demo.node.v1", root=self.ai))
        # the admission is on the log, attributable (D-5): type, class, rung, by
        lines = [json.loads(l) for l in
                 self.adm_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        granted = [a for a in lines if a.get("type") == "trust_rung"]
        self.assertEqual(len(granted), 1)
        self.assertEqual(granted[0]["by"], "bdo")

    def test_non_bdo_signer_writes_nothing(self):
        self.assertIsNone(
            loop_node.admit_rung(self.ai, "branded-subagent", "judge",
                                 "a-session-signing-itself"))
        self.assertFalse(self.adm_path.exists())
        self.assertIsNotNone(
            spawn.node_spawn_refusal("demo.node.v1", root=self.ai))


if __name__ == "__main__":
    unittest.main()
