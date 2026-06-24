"""Pins done-line 0194 — the value-gate verdict parser hardening + saved-trace
recovery.

A real opus panel stream ACCEPTED atom.diagram-canvas-first-cut.v0 but its
verdict was lost: a corrupted-.claude.json warning prefixed the headless child's
stdout, so json.loads(raw) failed in launch_claude, the `claude -p` envelope
never unwrapped, and the verdict sat DOUBLE-ESCAPED inside the envelope's
`result` string where the parser could not decode it. compile_panel counted a
failed stream and escalated a clean 2-accept-1-amend, wasting $0.82.

These tests use the THREE REAL saved traces (tests/fixtures/gate-runs/, copied
byte-for-byte from the live run) as the §10 evidence: the bug is reproduced from
the exact bytes that broke, and the fix is proven against them — never a
synthesized happy path. The pen is loaded by path (it lives under
.claude/skills/, outside the package); only its pure functions are exercised —
no gh, no claude subprocess, nothing written.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / ".claude" / "skills" / "gate" / "gate.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "gate-runs"
ATOM = "atom.diagram-canvas-first-cut.v0"

spec = importlib.util.spec_from_file_location("gate_pen_recover", GATE)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate_pen_recover"] = gate
spec.loader.exec_module(gate)


def _trace(model):
    for p in FIXTURES.glob("*.json"):
        info = json.loads(p.read_text(encoding="utf-8"))
        if info.get("model") == model:
            return info
    raise AssertionError(f"fixture for {model} not found")


class TestParserRecoversUnUnwrappedVerdict(unittest.TestCase):
    """The hardened _select_verdict / _verdict_objects. A constant `return
    ('accept', ...)` fails test_no_verdict_object; a constant `return (None,
    None)` fails test_real_opus — so neither vacuous constant survives."""

    def test_real_opus_parsed_text_yields_accept(self):
        # the exact bytes that broke: an un-unwrapped envelope (corruption
        # preamble defeated json.loads) with the verdict double-escaped inside
        # `result`. The parser recurses into the envelope and recovers it.
        info = _trace("claude-opus-4-8")
        self.assertEqual(info["parsed_text"], info["stdout"],
                         "fixture must preserve the un-unwrapped bug shape")
        verdict, reason = gate._select_verdict(info["parsed_text"])
        self.assertEqual(verdict, "accept")
        self.assertIn("owner", reason.lower())  # the mind's real reason came back too

    def test_no_verdict_object_yields_nothing(self):
        # the unconfirmable path is PRESERVED: prose that never emits a
        # structured verdict object returns nothing — never a verdict inferred
        # from words ("it accepts" in the prose must NOT become an accept).
        verdict, reason = gate._select_verdict(
            "the mind reasoned at length: it accepts, clearly — but emitted no object.")
        self.assertIsNone(verdict)
        self.assertIsNone(reason)

    def test_envelope_without_verdict_yields_nothing(self):
        # an un-unwrapped envelope whose `result` carries NO verdict object must
        # still yield nothing: the recursion recovers a real structured verdict,
        # it never fabricates one.
        env = json.dumps({"type": "result",
                          "result": "I weighed it and decided to move on. No object."})
        self.assertEqual(gate._verdict_objects(env), [])


class TestRecoverFromSavedTraces(unittest.TestCase):
    """The recovery tool: re-derive the panel from saved traces, zero new
    inference. A constant-classifier recover() can't pass — the three real
    streams disagree (accept/accept/amend), so any constant collapses them."""

    def test_recovers_all_three_streams(self):
        results, decision, verdict, detail, traces = gate.recover(ATOM, FIXTURES)
        self.assertEqual(len(traces), 3)
        bymodel = {r["model"]: r["verdict"] for r in results}
        self.assertEqual(bymodel["claude-opus-4-8"], "accept")
        self.assertEqual(bymodel["claude-haiku-4-5"], "accept")
        self.assertEqual(bymodel["claude-sonnet-4-6"], "amend")

    def test_genuine_split_escalates_not_a_parse_bug(self):
        # before the fix opus read as a FAILED stream -> escalate-by-bug; now it
        # reads `accept` and the escalation is the REAL 2-accept-1-amend split.
        results, decision, verdict, detail, traces = gate.recover(ATOM, FIXTURES)
        self.assertEqual(decision, "escalate")
        self.assertIsNone(verdict)
        self.assertTrue(all(r["ok"] for r in results),
                        "no stream is a failed/unconfirmable parse anymore")

    def test_unknown_atom_recovers_nothing(self):
        results, decision, verdict, detail, traces = gate.recover("atom.nope.v0", FIXTURES)
        self.assertEqual(traces, [])
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
