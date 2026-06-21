"""The digest's voice layer (issue #410): bounded inference narration grounded
by teeth. The fold stays truth; an inference pass narrates the dataset — but
only what the dataset can ground.

The §10 bar: inference is fluent and will, left untrusted, write a confident
headline about work that did not happen (the prose-facade failure mode). The
guard must refuse it. The case that must refuse to fit: a headline naming an
atom the span does not contain is dropped as a ghost; a flourish that cites
nothing is dropped as uncited. Proven non-vacuous — a clean headline survives,
a fabricated one is caught.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import digest_voice as voice

# the reach pen lives outside the package (it reaches; loop/ may not). Load it by
# path. Its gateway import is lazy (inside voiced()), so importing it never
# touches the network — render_voiced is pure composition.
_PEN = REPO / ".claude" / "skills" / "digest-voice" / "voice.py"
_spec = importlib.util.spec_from_file_location("digest_voice_pen", _PEN)
pen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pen)


def _dataset():
    """A minimal but realistic digest dataset — two landings, one confirmed arc
    with a piece, one loose atom, one divergence — enough vocabulary to ground
    against and to fabricate ghosts outside of."""
    return {
        "landed_in_span": [
            {"atoms": ["atom.real-one.v0"], "pr": 365, "epic": "epic.substrate",
             "by": "bdf1992"},
            {"atoms": ["atom.real-two.v0"], "pr": 363,
             "epic": "epic.inference-gateway", "by": "merge-node.claude.v1"},
        ],
        "arcs": [
            {"epic": "epic.substrate", "confirmed": {"by": "bdo"},
             "landed": 13, "total": 20, "horizon": "All five gates real.",
             "pieces": [{"atom": "atom.real-one.v0", "present": True}]},
        ],
        "loose": [{"atom": "atom.loose-real.v0"}],
        "divergences": [{"atom": "atom.real-two.v0", "epic": "epic.inference-gateway",
                         "kind": "refusal-under-confirmed-arc"}],
    }


class TestVocabulary(unittest.TestCase):
    def test_collects_atoms_prs_and_epics_from_every_corner(self):
        v = voice.vocabulary(_dataset())
        self.assertIn("atom.real-one.v0", v)       # from landings & arc piece
        self.assertIn("atom.real-two.v0", v)        # from landings & divergence
        self.assertIn("atom.loose-real.v0", v)      # from the loose pile
        self.assertIn("epic.substrate", v)
        self.assertIn("epic.inference-gateway", v)
        self.assertIn("#365", v)
        self.assertIn("#363", v)
        # a token that simply is not in the span must NOT appear
        self.assertNotIn("atom.never-happened.v0", v)


class TestClaimTokens(unittest.TestCase):
    def test_extracts_the_three_token_shapes(self):
        h = "epic.substrate hardened: atom.real-one.v0 landed in PR #365"
        self.assertEqual(voice.claim_tokens(h),
                         {"epic.substrate", "atom.real-one.v0", "#365"})

    def test_a_flourish_with_no_token_claims_nothing(self):
        self.assertEqual(voice.claim_tokens("The loop grew sharper this week"),
                         set())


class TestGroundingTheTeeth(unittest.TestCase):
    """The case that must refuse to fit."""

    def test_a_grounded_headline_survives(self):
        d = _dataset()
        kept, rejected = voice.ground(
            d, ["atom.real-one.v0 landed (#365) — epic.substrate hardens"])
        self.assertEqual(len(kept), 1)
        self.assertEqual(rejected, [])

    def test_a_ghost_atom_is_caught(self):
        # inference invents a plausible landing that never happened — the exact
        # prose-facade. The guard names the ghost and drops the headline.
        d = _dataset()
        kept, rejected = voice.ground(
            d, ["atom.never-happened.v0 shipped — a huge win for epic.substrate"])
        self.assertEqual(kept, [])
        self.assertEqual(len(rejected), 1)
        self.assertIn("atom.never-happened.v0", rejected[0]["why"])

    def test_a_ghost_pr_is_caught(self):
        d = _dataset()
        kept, rejected = voice.ground(d, ["Massive drop in PR #99999"])
        self.assertEqual(kept, [])
        self.assertIn("#99999", rejected[0]["why"])

    def test_an_uncited_flourish_is_caught(self):
        # confident specificity with nothing under it — refused for naming no
        # concrete token at all.
        d = _dataset()
        kept, rejected = voice.ground(d, ["The gateway grew teeth this week"])
        self.assertEqual(kept, [])
        self.assertIn("uncited", rejected[0]["why"])

    def test_mixed_batch_keeps_only_the_grounded(self):
        d = _dataset()
        kept, rejected = voice.ground(d, [
            "atom.real-two.v0 (#363) landed — epic.inference-gateway advances",
            "atom.fabricated.v0 also landed",            # ghost
            "Everything is better now",                   # uncited
        ])
        self.assertEqual(len(kept), 1)
        self.assertIn("atom.real-two.v0", kept[0])
        self.assertEqual(len(rejected), 2)


class TestParseHeadlines(unittest.TestCase):
    def test_strips_bullets_and_numbers_and_blanks(self):
        text = "- first line\n\n2. second line\n* third\nbare line\n"
        self.assertEqual(voice.parse_headlines(text),
                         ["first line", "second line", "third", "bare line"])

    def test_strips_wrapping_quotes_and_redundant_inner_bullets(self):
        # the real junk a small model produced: each line quote-wrapped with the
        # requested bullet echoed inside the quotes. The token must survive clean
        # so the guard can ground it.
        text = "- '- 'epic.x advances (#1)''\n"
        self.assertEqual(voice.parse_headlines(text), ["epic.x advances (#1)"])
        self.assertEqual(voice.claim_tokens(voice.parse_headlines(text)[0]),
                         {"epic.x", "#1"})


class TestBuildPrompt(unittest.TestCase):
    def test_prompt_carries_only_dataset_facts_and_states_the_rule(self):
        d = _dataset()
        p = voice.build_prompt(d)
        # the real atoms/PRs are in the prompt (inference can see them)...
        self.assertIn("atom.real-one.v0", p)
        self.assertIn("#365", p)
        self.assertIn("epic.substrate", p)
        # ...the grounding rule is stated to the model (belt; the guard is braces)
        self.assertIn("cite at least one", p.lower())
        self.assertIn("invent nothing", p.lower())
        # nothing outside the dataset leaks in
        self.assertNotIn("atom.never-happened.v0", p)


def _render_dataset():
    """The minimum a digest dataset needs for render() to run — no gestures, no
    landings; enough to prove the headline splice and the degrade path."""
    return {
        "span": {"since": None, "until": None},
        "landings": 0, "refusals": 0, "atoms_on_main": [],
        "setpoint": None,
        "field": {"ticks": 0, "heat": 0, "cool": 0, "budget_spent": 0,
                  "peak_backlog": 0, "deferred_reasons": {}},
        "arcs": [], "loose": [], "divergences": [], "landed_in_span": [],
        "phrasing": [],
    }


class TestRenderVoiced(unittest.TestCase):
    """The pen's composition: a grounded headline section is spliced in after
    the title/status line; with nothing grounded it degrades, byte-for-byte, to
    the deterministic render — voice never makes the surface worse for trying."""

    def test_headlines_splice_in_after_the_status_line(self):
        from loop import digest as D
        d = _render_dataset()
        out = pen.render_voiced(d, ["atom.x.v0 lands (#7)"], mind="local.qwen3-14b")
        self.assertIn("## ◆ Headlines", out)
        self.assertIn("- atom.x.v0 lands (#7)", out)
        self.assertIn("local.qwen3-14b", out)
        # the deterministic body still follows in full
        self.assertIn("## ◉ Tuning", out)
        # the splice lands after the title + status subline, before section 1
        lines = out.split("\n")
        self.assertTrue(lines[0].startswith("# Ontum Field Notes"))
        self.assertEqual(lines[3], "## ◆ Headlines")

    def test_no_headlines_degrades_to_the_plain_render(self):
        from loop import digest as D
        d = _render_dataset()
        self.assertEqual(pen.render_voiced(d, []), D.render(d))


if __name__ == "__main__":
    unittest.main()
