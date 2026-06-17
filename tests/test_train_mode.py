"""train — the first security mode — observes and tags but never blocks
(done-line 0096).

The §10 bar is one operation under two postures with a negative control:
`git add .` is denied (exit 2) with NO mode admitted — the control — and the
*same bytes* are allowed (exit 0) and recorded as `would-deny` once a signed
`security_mode` admission opens train for that session. The divergence is the
proof; if the control ever returns 0 the deny path is dead and train proves
nothing.

The mode is an admitted record, never a constant: the test opens it through
the one pen (`loop.node mode-train`), which is bdo-gated — a session signer
writes nothing and is refused. The guard reads the posture at hook time from
a pure log fold (`reconcile.active_mode`); the same `ONTUM_TOOL_WATCH_LOG`
override points both the sensor trace and the admissions fold at one temp
root, so this exercises the live guard, not internals.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD = ROOT / ".claude" / "hooks" / "command_guard.py"

GIT_ADD = "git add ."  # one locally-fine op the fence forbids (rule git-add)


def run_guard(command, watch_log, session):
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": session,
    })
    env = dict(os.environ, ONTUM_TOOL_WATCH_LOG=str(watch_log))
    return subprocess.run(
        [sys.executable, str(GUARD)], input=payload.encode("utf-8"),
        capture_output=True, env=env,
    )


def run_node(args, root):
    return subprocess.run(
        [sys.executable, "-m", "loop.node", *args, "--root", str(root)],
        capture_output=True, cwd=str(ROOT),
    )


def records(watch_log, status):
    if not watch_log.exists():
        return []
    out = []
    for line in watch_log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # torn tail: it never happened
        if entry.get("status") == status:
            out.append(entry)
    return out


class TrainMode(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = pathlib.Path(self.tmp.name)
        # AI_NATIVE_ROOT in the guard is WATCH_LOG.parent.parent, so place the
        # sensor trace inside a real `.ai-native/log` — the admissions fold the
        # posture reads lands right beside it.
        self.ai_native = base / ".ai-native"
        self.watch_log = self.ai_native / "log" / "tool-use.jsonl"
        self.admissions = self.ai_native / "log" / "admissions.jsonl"
        self.session = "S"

    def test_train_observes_where_normal_denies(self):
        # 1. negative control: no mode admitted -> the firm line holds.
        control = run_guard(GIT_ADD, self.watch_log, self.session)
        self.assertEqual(control.returncode, 2,
                         "control failed: git add . must be DENIED with no "
                         "train admitted — if this is 0 the deny path is dead")
        denied = records(self.watch_log, "denied")
        self.assertTrue(any(r["rule"] == "git-add" for r in denied),
                        "the control must leave a denied record on the trace")
        self.assertFalse(records(self.watch_log, "would-deny"),
                         "no would-deny may exist before train is opened")

        # 2. open train for this session through the one pen (admitted record).
        opened = run_node(
            ["mode-train", "start", "--session", self.session, "--by", "bdo"],
            self.ai_native)
        self.assertEqual(opened.returncode, 0, opened.stderr.decode())
        adm = [json.loads(l) for l in
               self.admissions.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(adm), 1)
        self.assertEqual(adm[0]["type"], "security_mode")
        self.assertEqual(adm[0]["mode"], "train")
        self.assertTrue(adm[0]["enabled"])
        opener_id = adm[0]["id"]

        # 3. SAME bytes, same session -> now allowed and recorded would-deny.
        trained = run_guard(GIT_ADD, self.watch_log, self.session)
        self.assertEqual(trained.returncode, 0, trained.stderr.decode())
        self.assertEqual(trained.stderr, b"",
                         "train blocks nothing and says nothing on stderr")
        would = records(self.watch_log, "would-deny")
        self.assertEqual(len(would), 1)
        wd = would[0]
        self.assertEqual(wd["rule"], "git-add")
        self.assertEqual(wd["intent"], "mutate")
        self.assertEqual(wd["mode"], "train")
        self.assertEqual(wd["train_session"], opener_id)
        self.assertEqual(wd["surface"], "git")

        # 4. THE DIVERGENCE: one op, two postures, the rule on the record.
        self.assertNotEqual(control.returncode, trained.returncode,
                            "train must diverge from normal on the same op")
        self.assertEqual((control.returncode, trained.returncode), (2, 0))

    def test_a_session_cannot_unguard_itself(self):
        # the bdo-gate: a session signer writes nothing and is refused.
        refused = run_node(
            ["mode-train", "start", "--session", self.session, "--by", "claude"],
            self.ai_native)
        self.assertEqual(refused.returncode, 2)
        self.assertFalse(self.admissions.exists() and
                         self.admissions.read_text(encoding="utf-8").strip(),
                         "a refused mode-train must write NOTHING to the log")

    def test_stop_closes_back_to_normal(self):
        # open then stop -> the latest admission wins, posture is normal again,
        # and the same op is denied once more.
        run_node(["mode-train", "start", "--session", self.session, "--by", "bdo"],
                 self.ai_native)
        run_node(["mode-train", "stop", "--session", self.session, "--by", "bdo"],
                 self.ai_native)
        after = run_guard(GIT_ADD, self.watch_log, self.session)
        self.assertEqual(after.returncode, 2,
                         "stop must close train — the guard blocks again")

    def test_unreadable_fold_stays_normal(self):
        # train never silently un-guards: with no admissions fold at all the
        # posture defaults to normal and the op is denied.
        from importlib import import_module
        sys.path.insert(0, str(GUARD.parent))
        cg = import_module("command_guard")
        # active_mode over an empty/missing fold returns ("normal", None)
        from loop.reconcile import Fold, active_mode
        posture, opener = active_mode(Fold(self.ai_native), self.session)
        self.assertEqual((posture, opener), ("normal", None))
        _ = cg  # the live module is what the subprocess runs; import asserts it loads


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    unittest.main()
