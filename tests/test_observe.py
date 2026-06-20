"""§10 for the Observable-as-gate (loop/observe.py, epic.relation-governed-
exploration, the forced first build: observable-as-gate).

The teeth, and the whole point: an act the ACTION-gate would ALLOW is
nonetheless REFUSED by observe.gate() because it cannot name an attributable
receipt path. The action-gate (`command_guard.py`, derived from
`fence/policy.py`) decides whether a command is in the family a session may
type — a read-only `git status` is allowed (exit 0). The consequence-gate
decides whether the act's effect can be traced back to its actor. The kill-test
takes that same allowed act, under-declares it, and proves observe.gate()
halts it — demonstrating the consequence-gate catches what the action-gate
structurally cannot (it sees the verb, never the receipt path).

Non-vacuity (the mandatory tooth): a variant that NEUTRALIZES the receipt-path
check is shown to clear the very declaration the real gate halts — so removing
or weakening the check would make the kill-test fail. A gate that always
cleared would fail every halt assertion here.
"""

import json
import os
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import observe  # noqa: E402

GUARD = ROOT / ".claude" / "hooks" / "command_guard.py"


def run_action_gate(command, watch_log):
    """The action-gate's verdict on a raw command: command_guard as the
    harness fires it — JSON on stdin, exit 0 (allow) or 2 (deny)."""
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test-observe",
    })
    env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(watch_log))
    return subprocess.run(
        [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
        capture_output=True, env=env,
    )


def well_declared(action, **overrides):
    """A fully-declared, well-formed observation of an act — the positive
    control. Its attribution path terminates at the actor, so it clears."""
    decl = {
        "actor": "ontum-node:explorer.v0",
        "action": action,
        "scope": "the working tree (read-only probe)",
        "expected_receipt": ".ai-native/log/tool-use.jsonl",
        "attribution_path": "effect -> .ai-native/log/tool-use.jsonl "
                            "-> ontum-node:explorer.v0",
        "rollback_path": "read-only — no effect to roll back",
    }
    decl.update(overrides)
    return decl


def neutralized_gate(declaration):
    """observe.gate with the receipt-path check REMOVED: the receipt fields are
    dropped from the required set and `attribution_halt` is never consulted.
    This is the gate a future hand might write if it forgot the consequence —
    and the kill-test's assertion is that the real gate does NOT behave like
    this one. If observe.gate() were ever weakened to this, the kill-test
    would fail. (The teeth made falsifiable.)"""
    decl = declaration if isinstance(declaration, dict) else {}
    base = [f for f in observe.required_fields(decl)
            if f not in observe.RECEIPT_FIELDS]
    missing = [f for f in base if not observe._present(decl.get(f))]
    if missing:
        return {"cleared": False, "halt_reason": "missing " + ", ".join(missing),
                "missing": missing}
    return {"cleared": True, "halt_reason": None, "missing": []}


class HappyPath(unittest.TestCase):
    def test_a_well_formed_declaration_clears(self):
        v = observe.gate(well_declared("git status"))
        self.assertTrue(v["cleared"], v["halt_reason"])
        self.assertIsNone(v["halt_reason"])
        self.assertEqual(v["missing"], [])


class KillTest(unittest.TestCase):
    """The consequence-gate catches what the action-gate cannot."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.watch_log = pathlib.Path(self.tmp.name) / "watch.jsonl"
        self.addCleanup(self.tmp.cleanup)

    def test_action_gate_allows_the_act(self):
        # Premise of the kill-test: `git status` is read-only, named by no
        # forbidden rule, so the action-gate lets it through. If this ever
        # changes, the kill-test's framing is wrong and we want to know.
        proc = run_action_gate("git status", self.watch_log)
        self.assertEqual(proc.returncode, 0,
                         f"action-gate unexpectedly denied git status: "
                         f"{proc.stderr.decode()}")

    def test_observe_gate_halts_the_same_allowed_act(self):
        # THE KILL-TEST: the same act the action-gate allows, declared without
        # a receipt path, is HALTED by observe.gate(). Allowed != observable.
        under_declared = {
            "actor": "ontum-node:explorer.v0",
            "action": "git status",
            "scope": "the working tree",
            "rollback_path": "read-only — nothing to roll back",
            # the ONLY thing missing is the receipt path: no expected_receipt,
            # no attribution_path. Everything an action-gate could see is here.
        }
        # the action-gate would let this command run...
        proc = run_action_gate(under_declared["action"], self.watch_log)
        self.assertEqual(proc.returncode, 0)
        # ...but observe halts it: it cannot name where its effect attributes.
        v = observe.gate(under_declared)
        self.assertFalse(v["cleared"],
                         "observe.gate cleared an un-attributable act")
        for field in observe.RECEIPT_FIELDS:
            self.assertIn(field, v["missing"])
        self.assertIn("halts", v["halt_reason"])

    def test_neutralizing_the_check_would_clear_the_kill_input(self):
        # Non-vacuity: prove the receipt-path check is what does the work. The
        # SAME under-declared act that the real gate halts is CLEARED by a gate
        # with the receipt-path check removed. So the halt is caused by the
        # check, not by something incidental — delete the check and the
        # kill-test (test_observe_gate_halts_the_same_allowed_act) goes red.
        under_declared = {
            "actor": "ontum-node:explorer.v0",
            "action": "git status",
            "scope": "the working tree",
            "rollback_path": "read-only — nothing to roll back",
        }
        self.assertTrue(neutralized_gate(under_declared)["cleared"],
                        "the neutralized gate should clear what the real gate "
                        "halts — otherwise the check is not the cause")
        self.assertFalse(observe.gate(under_declared)["cleared"])


class WellFormedness(unittest.TestCase):
    """Locally-fine declarations that still refuse to fit — the §10 bar:
    every field is named, yet the receipt path does not attribute."""

    def test_named_receipt_that_does_not_reach_the_actor_is_halted(self):
        # All fields present, a real receipt sink named — but the attribution
        # chain terminates at a DIFFERENT actor than the one declared. The
        # effect lands in a real sink that cannot be traced back to this actor.
        dangling = well_declared(
            "write a probe note",
            attribution_path="effect -> .ai-native/log/tool-use.jsonl "
                             "-> some-other-node",
        )
        v = observe.gate(dangling)
        self.assertFalse(v["cleared"],
                         "a dangling attribution chain was let through")
        self.assertEqual(v["missing"], [])  # nothing missing — it is malformed
        self.assertIn("does not terminate at the actor", v["halt_reason"])

    def test_blank_attribution_path_is_absence_not_a_name(self):
        v = observe.gate(well_declared("git status", attribution_path="   "))
        self.assertFalse(v["cleared"])
        self.assertIn("attribution_path", v["missing"])

    def test_attribution_halt_is_load_bearing_in_isolation(self):
        # The core tooth, tested directly: it bites the dangling chain and
        # passes the well-formed one. If someone weakened it to `return None`,
        # this and the well-formedness kill above both go red.
        self.assertIsNone(observe.attribution_halt(well_declared("git status")))
        self.assertIsNotNone(observe.attribution_halt(well_declared(
            "git status", attribution_path="effect -> sink -> nobody")))


class Exploratory(unittest.TestCase):
    def test_exploratory_act_requires_a_relation_id(self):
        # An act that marks itself exploratory must name the relation/probe it
        # explores; an otherwise-complete declaration without it halts.
        decl = well_declared("probe the relation", exploratory=True)
        self.assertFalse(observe.gate(decl)["cleared"])
        self.assertIn(observe.EXPLORATORY_FIELD, observe.gate(decl)["missing"])
        # named, it clears.
        decl["relation_id"] = "relation.welcome.v0"
        self.assertTrue(observe.gate(decl)["cleared"])

    def test_non_exploratory_does_not_demand_relation_id(self):
        self.assertTrue(observe.gate(well_declared("git status"))["cleared"])


class CliContract(unittest.TestCase):
    def test_cli_prints_one_result_line(self):
        proc = subprocess.run(
            [sys.executable, "-m", "loop.observe"],
            capture_output=True, cwd=str(ROOT),
            env=dict(os.environ, PYTHONPATH=str(ROOT)),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        out = proc.stdout.decode()
        result_lines = [ln for ln in out.splitlines() if ln.startswith("result:")]
        self.assertEqual(len(result_lines), 1, out)
        self.assertTrue(result_lines[0].startswith("result: done"))

    def test_json_contract_is_machine_readable(self):
        proc = subprocess.run(
            [sys.executable, "-m", "loop.observe", "--json"],
            capture_output=True, cwd=str(ROOT),
            env=dict(os.environ, PYTHONPATH=str(ROOT)),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        body = "\n".join(ln for ln in proc.stdout.decode().splitlines()
                         if not ln.startswith("result:"))
        data = json.loads(body)
        self.assertEqual(data["gate"], "observable-as-gate")
        for field in observe.RECEIPT_FIELDS:
            self.assertIn(field, data["required_fields"])


if __name__ == "__main__":
    unittest.main()
