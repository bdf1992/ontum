#!/usr/bin/env python3
"""The continue-probe pen (done-line 0135): the firing edge.

`loop.watcher` is the pure fold — it names which registered sessions are idle
and gateway-eligible and emits the exact `claude --resume <id> -p <probe>`
command. It never spawns `claude` (the loop/ no-network law). THIS pen is the
edge that does: the standing external tick (an OS scheduler entry — Task
Scheduler on Windows, cron elsewhere — so there is no daemon, the same shape as
the daily digest) runs `probe.py --fire` every few minutes; it asks the watcher
for idle-and-eligible sessions, budgets which are actually *due* (cooldown +
a per-streak fire cap so an away session is never hammered), resumes each, and
records every firing to a gitignored trace (the trust rail — every headless
fire is on the record until the organ earns trust).

Default is **dry-run**: it prints what it *would* fire and writes nothing. Only
`--fire` actually spawns `claude` and advances the ledger — resuming a session
is real work that costs tokens, so the firing is opt-in and watched.

The budgeting (`due_targets`) is a pure function so the §10 teeth can drive it
without spawning anything. Stdlib only. result: done | report.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from loop import watcher, retry  # noqa: E402

# the per-session fire ledger and the gitignored trace live beside the registry
# under ~/.claude (per-machine state, like the transcripts), never in the repo.
LEDGER = Path.home() / ".claude" / "ontum-continue-probe.json"
TRACE = ROOT / ".ai-native" / "log" / "continue-probe-fires.jsonl"

# don't re-fire one session more often than this; and never more than this many
# times in a single idle-streak (a streak resets when the session acts after a
# fire). Borrowed from the in-session nudge budget so the two agree.
MIN_REFIRE_SECONDS = watcher.IDLE_THRESHOLD_SECONDS
MAX_FIRES = retry.MAX_NUDGES


def load_ledger(path=LEDGER):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_ledger(ledger, path=LEDGER):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(ledger), encoding="utf-8")
        return True
    except OSError:
        return False


def due_targets(idle, ledger, now, mtime=None):
    """The pure budgeting fold (done-line 0135): of the watcher's idle-and-
    eligible targets, which are actually *due* to fire, and the advanced ledger.

    A target is due iff it has cooled down (>= MIN_REFIRE since its last fire)
    AND is under the fire cap for its current idle-streak. The streak RESETS
    when the session acted after our last fire (its transcript advanced past
    last_fire) — a fresh idle period earns a fresh budget; a session that never
    moved is nudged at most MAX_FIRES times, then left alone. Pure: `now`/
    `mtime` injected so the teeth drive it; the input ledger is never mutated."""
    if mtime is None:
        mtime = watcher.transcript_mtime
    fire, new_ledger = [], dict(ledger)
    for t in idle:
        sid = t["session_id"]
        rec = ledger.get(sid, {})
        last_fire = rec.get("last_fire", 0)
        fires = int(rec.get("fires", 0))
        m = mtime(sid)
        if last_fire and m is not None and m > last_fire:
            fires = 0  # the session moved since our last fire → fresh streak
        if now - last_fire < MIN_REFIRE_SECONDS:
            continue  # cooling down
        if fires >= MAX_FIRES:
            continue  # said its piece for this streak; stand down
        fire.append(t)
        new_ledger[sid] = {"last_fire": now, "fires": fires + 1,
                           "cwd": t.get("fire_cwd")}
    return fire, new_ledger


def _trace(record):
    try:
        TRACE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass  # the trace is best-effort observability, never a gate


def _spawn(target):
    """Resume one idle session out of band. Detached (Popen, no wait) so the
    tick never blocks on a long resumed turn; the resumed `-p` lands the soft
    reminder via the idle hook. Returns True if the spawn launched."""
    try:
        subprocess.Popen(target["fire"], cwd=target["fire_cwd"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def run(now, fire=False, mtime=None):
    """Ask the watcher for idle-and-eligible sessions, budget the due ones, and
    (if `fire`) resume them. Returns (due, fired, dry_run)."""
    idle = watcher.idle_sessions(now, mtime=mtime)
    ledger = load_ledger()
    due, new_ledger = due_targets(idle, ledger, now, mtime=mtime)
    if not fire:
        return due, [], True
    fired = []
    for t in due:
        ok = _spawn(t)
        _trace({"ts": now, "session_id": t["session_id"],
                "cwd": t["fire_cwd"], "launched": ok})
        if ok:
            fired.append(t)
    save_ledger(new_ledger)
    return due, fired, False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fire", action="store_true",
                    help="actually resume the due sessions (default: dry-run, "
                         "print what would fire and write nothing)")
    args = ap.parse_args(argv)

    due, fired, dry = run(time.time(), fire=args.fire)
    if not due:
        print("result: done — no sessions due to probe (none idle-and-eligible, "
              "all cooling down, or all at their fire cap)")
        return 0
    for t in due:
        mins = t["idle_seconds"] // 60
        print(f"  {t['session_id']} (~{mins}m idle, in {t['fire_cwd']})")
    if dry:
        print(f"result: report — {len(due)} session(s) DUE to probe (dry-run; "
              "re-run with --fire to resume them). The external scheduler runs "
              "`probe.py --fire` as the standing tick.")
    else:
        print(f"result: report — fired {len(fired)}/{len(due)} due session(s); "
              f"every firing traced to {TRACE.as_posix()} (the trust rail)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
