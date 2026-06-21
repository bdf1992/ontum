"""Done-line 0138: the headless gate rail launches and leaves a trace.

The production-gate session (PR #286) could not get a verdict out of the branded
gate rail: the launched `claude -p` returned an empty result and the failure
left nothing to debug. Two root causes — no `--model` (the child 404s on the
`opus` alias) and `cwd=ROOT` (the repo's UserPromptSubmit hooks block the
headless prompt, num_turns: 0) — plus bdo's observability point: a run must
write a file.

The §10 teeth, with an injected fake runner so no live `claude` spawns here:
  - the launch command carries an explicit `--model`, and the cwd is NOT the
    repo root (the two bugs, asserted directly);
  - a trace file is written on a parse-SUCCESS run AND on a parse-FAILURE run;
  - the failure still NAMES the trace path and still raises (so the trust-rail
    issue stays open) — the vanish that this fix removes.
A constant/no-op launch_claude could not satisfy both the success and the
failure case.
"""

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import importlib.util

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


class _Proc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


def _runner_returning(stdout, stderr="", rc=0):
    captured = {}

    def runner(cmd, **kw):
        captured["cmd"] = cmd
        captured["cwd"] = kw.get("cwd")
        return _Proc(stdout=stdout, stderr=stderr, returncode=rc)

    return runner, captured


def _verdict_envelope(verdict):
    # what `claude -p --output-format json` returns: a wrapper whose `result`
    # is the model's text, ending in the VERDICT sentinel object
    sentinel = json.dumps({"verdict": verdict,
                           "reason": "the one check that could have failed: "
                                     "whether evidence resolved."})
    result = "I checked the claim against the log.\nVERDICT " + sentinel
    return json.dumps({"type": "result", "is_error": False,
                       "num_turns": 1, "result": result})


class GateRailLaunch(unittest.TestCase):
    def test_command_carries_model_and_neutral_cwd(self):
        """The two root-cause bugs, asserted directly."""
        cmd = gate._launch_cmd("the prompt", "claude-opus-4-8")
        self.assertIn("--model", cmd)
        self.assertEqual(cmd[cmd.index("--model") + 1], "claude-opus-4-8")
        # the cwd must NOT be the repo root (where the project hooks block)
        self.assertNotEqual(Path(gate._launch_cwd()).resolve(), gate.ROOT.resolve())

    def test_default_model_is_explicit_not_the_opus_alias(self):
        self.assertTrue(gate.GATE_MODEL)
        self.assertNotEqual(gate.GATE_MODEL, "opus")

    def test_success_writes_a_trace_and_uses_model_and_cwd(self):
        runner, captured = _runner_returning(_verdict_envelope("accept"))
        verdict, reason, text, trace = gate.launch_claude(
            "a self-contained prompt", atom_id="atom.x.v0",
            node_id="value-gate.claude.v1", runner=runner)
        self.assertEqual(verdict, "accept")
        self.assertTrue(Path(trace).exists())
        # the trace carries the full run for debugging
        saved = json.loads(Path(trace).read_text(encoding="utf-8"))
        self.assertEqual(saved["prompt"], "a self-contained prompt")
        self.assertIn("--model", captured["cmd"])
        self.assertNotEqual(Path(captured["cwd"]).resolve(), gate.ROOT.resolve())
        Path(trace).unlink()

    def test_empty_run_writes_a_trace_names_the_path_and_raises(self):
        """The 0-turn vanish this fix removes: an empty result still leaves a
        file, the error names it, and it raises so the issue stays open."""
        runner, _ = _runner_returning(
            json.dumps({"type": "result", "is_error": False,
                        "num_turns": 0, "result": ""}), rc=0)
        with self.assertRaises(ValueError) as cm:
            gate.launch_claude("p", atom_id="atom.y.v0",
                               node_id="value-gate.claude.v1", runner=runner)
        msg = str(cm.exception)
        self.assertIn("trace:", msg)
        # the path named in the error actually exists and holds the empty run
        path = Path(msg.split("trace:")[1].split(";")[0].strip())
        self.assertTrue(path.exists())
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["stdout"], json.dumps(
            {"type": "result", "is_error": False, "num_turns": 0, "result": ""}))
        path.unlink()

    def test_launch_redirects_stdin_to_devnull_so_it_cannot_hang(self):
        """Issue #411: the headless `claude -p` inherited the parent's stdin and
        blocked on it for the full 600s timeout — the review-queue drain's
        consumer never returned. The fix redirects the child's stdin to DEVNULL
        (a non-interactive judge never needs stdin), so the same prompt that hung
        completes. Non-vacuous: the pre-fix call passed no `stdin`, so this
        assertion fails against `kwargs.get('stdin') is None`."""
        captured = {}

        def runner(cmd, **kw):
            captured["kwargs"] = kw
            return _Proc(stdout=_verdict_envelope("accept"))

        verdict, _, _, trace = gate.launch_claude(
            "a self-contained prompt", atom_id="atom.s.v0",
            node_id="value-gate.claude.v1", runner=runner)
        self.assertEqual(verdict, "accept")
        self.assertEqual(captured["kwargs"].get("stdin"), gate.subprocess.DEVNULL)
        Path(trace).unlink()

    def test_nonzero_exit_with_empty_text_writes_trace_and_raises(self):
        runner, _ = _runner_returning("", stderr="boom", rc=1)
        with self.assertRaises(RuntimeError) as cm:
            gate.launch_claude("p", atom_id="atom.z.v0", node_id="n", runner=runner)
        msg = str(cm.exception)
        self.assertIn("trace:", msg)
        path = Path(msg.split("trace:")[1].split(";")[0].strip())
        self.assertTrue(path.exists())
        path.unlink()


if __name__ == "__main__":
    unittest.main()
