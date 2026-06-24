"""Issue #411: the headless-spawn guard is structural, not per-call.

A headless model child (`claude -p`, `claude --resume … -p …`) hangs if it
inherits the parent's live stdin (the 600s timeouts #390/#391/#393/#396, fixed
once in gate.py with stdin=DEVNULL — done-line 0168). That guard lived at ONE
call site as a lone correct call; a second spawner (continue-probe/probe.py
`_spawn`) re-introduced the exact bug. The fix moves the guard into one shared
helper, `.claude/skills/_spawn/headless.py`, that ALWAYS closes stdin with no
override.

The §10 teeth, with an injected runner so no live `claude` spawns here: EVERY
spawn the helper issues — across BOTH capture modes and BOTH detached modes —
carries stdin == subprocess.DEVNULL. Non-vacuous: the assertion reads the exact
kwarg the helper passed; drop `stdin=subprocess.DEVNULL` from the helper and
`captured.get("stdin")` is None, so all four cases fail. The sibling assertion
this mirrors lives in tests/test_gate_rail.py (~line 77) for the gate's one call.
"""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

HEADLESS_PY = REPO / ".claude" / "skills" / "_spawn" / "headless.py"
_spec = importlib.util.spec_from_file_location("_spawn_headless", HEADLESS_PY)
headless = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(headless)


def _capturing_runner():
    """A fake subprocess.run / subprocess.Popen: records the kwargs it was
    called with and returns a sentinel, so the teeth read what the helper
    passed without a live spawn."""
    captured = {}

    def runner(argv, **kw):
        captured["argv"] = argv
        captured.update(kw)
        return ("ran", argv, kw)

    return runner, captured


class HeadlessSpawnClosesStdin(unittest.TestCase):
    def test_stdin_is_devnull_across_both_capture_and_detached_modes(self):
        """The one invariant, in all four corners of the matrix. A dropped
        stdin guard reads None here and fails — this is the non-vacuous test."""
        for capture in (True, False):
            for detached in (True, False):
                with self.subTest(capture=capture, detached=detached):
                    runner, captured = _capturing_runner()
                    headless.headless_spawn(
                        ["claude", "-p", "hi"], cwd="/tmp",
                        timeout=600, detached=detached, capture=capture,
                        runner=runner)
                    self.assertEqual(captured.get("stdin"), subprocess.DEVNULL)

    def test_capture_true_pipes_and_decodes_text(self):
        runner, captured = _capturing_runner()
        headless.headless_spawn(["claude", "-p", "hi"], cwd="/tmp",
                                capture=True, runner=runner)
        self.assertEqual(captured.get("stdout"), subprocess.PIPE)
        self.assertEqual(captured.get("stderr"), subprocess.PIPE)
        self.assertTrue(captured.get("text"))

    def test_capture_false_silences_streams(self):
        runner, captured = _capturing_runner()
        headless.headless_spawn(["claude", "-p", "hi"], cwd="/tmp",
                                capture=False, runner=runner)
        self.assertEqual(captured.get("stdout"), subprocess.DEVNULL)
        self.assertEqual(captured.get("stderr"), subprocess.DEVNULL)

    def test_awaited_path_passes_timeout_detached_path_does_not(self):
        """detached=False -> subprocess.run(..., timeout=…); detached=True ->
        subprocess.Popen(...), which takes no timeout (returned unwaited)."""
        runner, captured = _capturing_runner()
        headless.headless_spawn(["claude"], cwd="/tmp", timeout=600,
                                detached=False, runner=runner)
        self.assertEqual(captured.get("timeout"), 600)

        runner, captured = _capturing_runner()
        headless.headless_spawn(["claude"], cwd="/tmp", timeout=600,
                                detached=True, runner=runner)
        self.assertNotIn("timeout", captured)

    def test_caller_owns_the_command_shape(self):
        """The helper never touches argv — the caller's command passes through
        verbatim (the helper owns only the std streams + timeout)."""
        runner, captured = _capturing_runner()
        argv = ["claude", "--resume", "abc", "-p", "continue"]
        headless.headless_spawn(argv, cwd="/work", capture=False,
                                detached=True, runner=runner)
        self.assertEqual(captured.get("argv"), argv)
        self.assertEqual(captured.get("cwd"), "/work")

    def test_no_parameter_can_override_the_closed_stdin(self):
        """The guard is immovable by contract: there is no stdin parameter, so a
        caller cannot re-open it. Passing one is a TypeError, not a silent open."""
        runner, _ = _capturing_runner()
        with self.assertRaises(TypeError):
            headless.headless_spawn(["claude"], cwd="/tmp",
                                    stdin=None, runner=runner)


if __name__ == "__main__":
    unittest.main()
