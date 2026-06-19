"""Done-line 0102: the policy-intake pen carries bdo's gateway-policy stamps
deterministically, and refuses to ask what cannot be admitted.

The pen never judges intent (the SKILL does) and never runs the admission.
What it must get right: the (caller, surface, mind, permit) an issue carries —
all four, because `loop.inference policy` needs them — and the refusal-at-open.
The §10 cases: a half-marker (missing a field) must not parse (the pen never
hands the session a policy it guessed), and a malformed policy must be refused
at open exactly as the admission pen would. The join is pinned too (both ways):
a policy written through the one write path (loop.inference.set_policy --by bdo)
is exactly what flips the gateway from default-deny refuse to permit — the
bound the inference-as-composition layer obeys — and a non-bdo signer writes
nothing: the gesture cannot be forged from this side.
"""

import importlib.util
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


policy = _load("policy_intake",
               ROOT / ".claude" / "skills" / "policy-intake" / "policy.py")

from loop import inference  # noqa: E402
from loop.reconcile import Fold  # noqa: E402


class PolicyFromBody(unittest.TestCase):
    def test_round_trips_all_four_fields(self):
        body = "briefing\n\n" + policy.marker(
            "branch-ritual.garden", "branch-cut", "*", True)
        self.assertEqual(
            policy.policy_from_body(body),
            ("branch-ritual.garden", "branch-cut", "*", True))

    def test_deny_round_trips(self):
        body = policy.marker("c", "s", "m", False)
        self.assertEqual(policy.policy_from_body(body), ("c", "s", "m", False))

    def test_no_marker_is_not_ours(self):
        self.assertIsNone(policy.policy_from_body("a plain issue, no marker"))
        self.assertIsNone(policy.policy_from_body(""))
        self.assertIsNone(policy.policy_from_body(None))

    def test_half_marker_is_not_a_marker(self):
        # missing surface/mind/permit — the pen never hands a guessed policy.
        half = "<!-- ontum:policy-confirm caller=branch-ritual.garden -->"
        self.assertIsNone(policy.policy_from_body(half))
        half2 = ("<!-- ontum:policy-confirm caller=c surface=s mind=m -->")  # no permit
        self.assertIsNone(policy.policy_from_body(half2))

    def test_sibling_markers_are_not_ours(self):
        self.assertIsNone(policy.policy_from_body(
            "<!-- ontum:rung-confirm class=branded-subagent capability=judge -->"))
        self.assertIsNone(policy.policy_from_body(
            "<!-- ontum:realness-confirm stage=s node=n -->"))


class OpenRefusal(unittest.TestCase):
    """The pen opens only questions the admission pen could answer — its
    open_refusal IS inference.policy_refusal (one vocabulary, no drift)."""

    def test_missing_field_refused_exactly_as_admission_pen(self):
        for caller, surface, mind in [("", "s", "m"), ("c", "", "m"), ("c", "s", "")]:
            self.assertEqual(
                policy.open_refusal(caller, surface, mind),
                inference.policy_refusal(caller, surface, mind, inference.GRANTOR))
            self.assertIsNotNone(policy.open_refusal(caller, surface, mind))

    def test_wellformed_policy_opens(self):
        self.assertIsNone(
            policy.open_refusal("branch-ritual.garden", "branch-cut", "*"))


class BdoComment(unittest.TestCase):
    def _c(self, login, body):
        return {"author": {"login": login}, "body": body}

    def test_picks_owners_last_word_among_many(self):
        comments = [
            self._c("ontum-bot", "opened for confirmation"),
            self._c("bdf1992", "thinking"),
            self._c("someone-else", "i say yes"),
            self._c("bdf1992", "permit it"),
        ]
        self.assertEqual(policy.bdo_comment(comments, "bdf1992"), "permit it")

    def test_no_owner_comment_is_empty(self):
        self.assertEqual(policy.bdo_comment([self._c("bot", "ping")], "bdf1992"), "")


class PolicyFlipsTheGateway(unittest.TestCase):
    """The join (§10 both ways): default-deny refuses the caller; the policy
    written through the ONE write path — loop.inference.set_policy --by bdo,
    the act the SKILL runs on bdo's clear permit — is exactly what flips the
    gateway's authorize() to permit. And a non-bdo signer writes nothing: the
    gesture cannot be forged from this side."""

    def setUp(self):
        self.ai = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.ai, ignore_errors=True)
        (self.ai / "log").mkdir()
        self.adm = self.ai / "log" / "admissions.jsonl"

    def test_denied_before_permitted_after(self):
        caller, surface = "branch-ritual.garden", "branch-cut"
        permit, _ = inference.authorize(Fold(self.ai), caller, surface, "qwen3:14b")
        self.assertFalse(permit)  # default-deny: no thought without a rule
        adm = inference.set_policy(self.ai, caller, surface, "*", True, "bdo")
        self.assertIsNotNone(adm)
        permit2, _ = inference.authorize(Fold(self.ai), caller, surface, "qwen3:14b")
        self.assertTrue(permit2)  # the wildcard policy authorizes the call

    def test_non_bdo_signer_writes_nothing(self):
        adm = inference.set_policy(self.ai, "branch-ritual.garden", "branch-cut",
                                   "*", True, "a-session-signing-itself")
        self.assertIsNone(adm)
        self.assertFalse(self.adm.exists())
        permit, _ = inference.authorize(Fold(self.ai), "branch-ritual.garden",
                                        "branch-cut", "qwen3:14b")
        self.assertFalse(permit)  # still default-deny


if __name__ == "__main__":
    unittest.main()
