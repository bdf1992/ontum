#!/usr/bin/env python3
"""The continue-probe pen (done-line 0135): the firing edge.

`loop.watcher` is the pure fold — it names which registered sessions are idle
and gateway-eligible and emits the exact `claude --resume <id> -p <probe>`
command. It never spawns `claude` (the loop/ no-network law). THIS pen is the
edge that does: the standing external tick (an OS scheduler entry — Task
Scheduler on Windows, cron elsewhere — so there is no daemon, the same shape as
the daily digest) runs `probe.py --fire` every few minutes; it asks the watcher
for idle-and-eligible sessions, selects which are *due* (cooldown + a per-streak
fire cap so an away session is never hammered), bounds them by the EASED fire
budget (done-line 0171), resumes only that slice, and records every firing to a
gitignored trace (the trust rail — every headless fire is on the record until
the part earns trust).

The easing (done-line 0171): opening the probe gateway made a whole backlog of
idle sessions due at once — firing them all in one tick is the burst shape of
the llama-server kill, but as spawned `claude` sessions the inference-queue
semaphore does not govern. So the per-tick fire budget is the orchestrate heat/
cool law on the probe-fire plane: it flows freely below a pool-depth threshold
and, above it, eases between a floor and a ceiling against recent EGRESS (fires
still draining), bounded by an ADMITTED setpoint (`continue-probe.easing`),
never a code constant. A deep backlog drains in eased waves, never a burst.

Default is **dry-run**: it prints what it *would* fire and writes nothing. Only
`--fire` actually spawns `claude` and advances the ledger — resuming a session
is real work that costs tokens, so the firing is opt-in and watched.

Selection (`due_targets`), accounting (`advance_ledger`) and the eased budget
(`eased_budget`) are pure functions so the §10 teeth drive them without spawning
anything — and selection is split from accounting so a session the budget defers
this tick is NOT marked fired (the slice-after-advance starvation bug). Stdlib
only. result: done | report.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# the shared headless-spawn helper (issue #411): `.claude/skills` is this file's
# parent's parent — on the path so the one stdin=DEVNULL guard reaches here too.
_SKILLS_DIR = Path(__file__).resolve().parents[1]
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))

from loop import watcher, retry  # noqa: E402
from _spawn.headless import headless_spawn  # noqa: E402

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
    """Pure SELECTION (done-line 0171, split from accounting): of the watcher's
    idle-and-eligible targets, which are *eligible* to fire this tick. Returns
    the eligible list — each target annotated with `fires_if_fired`, the streak
    count to record IF it actually fires. The ledger is NOT advanced here; that
    is `advance_ledger`'s job and it advances only the sessions actually fired,
    so a target the eased budget defers this tick is never marked fired and
    never starves (the slice-after-advance bug this split closes).

    A target is eligible iff it has cooled down (>= MIN_REFIRE since its last
    fire) AND is under the fire cap for its current idle-streak. The streak
    RESETS when the session acted after our last fire (its transcript advanced
    past last_fire) — a fresh idle period earns a fresh budget; a session that
    never moved is nudged at most MAX_FIRES times, then left alone. Pure: `now`/
    `mtime` injected so the teeth drive it; the input ledger is never mutated."""
    if mtime is None:
        mtime = watcher.transcript_mtime
    out = []
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
        out.append(dict(t, fires_if_fired=fires + 1))
    return out


def advance_ledger(ledger, fired, now):
    """Pure ACCOUNTING (done-line 0171): the new ledger after `fired` sessions
    actually fired this tick — each gets last_fire=now and the `fires_if_fired`
    that `due_targets` computed for it. ONLY fired sessions advance; an eligible
    session the budget deferred keeps its prior ledger entry untouched, so its
    cooldown does not start and it is first in line next tick. The input ledger
    is never mutated."""
    out = dict(ledger)
    for t in fired:
        out[t["session_id"]] = {
            "last_fire": now,
            "fires": int(t.get("fires_if_fired", 1)),
            "cwd": t.get("fire_cwd"),
        }
    return out


def recent_egress(now, window, trace=TRACE):
    """The egress signal (done-line 0171): how many fires launched within the
    last `window` seconds — sessions presumed still draining. A pure read over
    the fires trace; only launched fires count, a torn line is dropped (the
    fold's tolerance), and a missing trace reads as 0 (no drain in flight, so
    the budget opens fully — the safe default is to make progress, not stall)."""
    cutoff = now - window
    n = 0
    try:
        with Path(trace).open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("launched") and float(rec.get("ts", 0)) >= cutoff:
                        n += 1
                except (ValueError, TypeError, AttributeError):
                    continue  # torn / non-dict / non-numeric ts — never happened
    except OSError:
        return 0
    return n


def eased_budget(due_depth, egress, easing):
    """The eased per-tick fire budget (done-line 0171): the orchestrate heat/
    cool law on the probe-fire plane, a pure function the §10 teeth drive.

    At or below `threshold` due sessions the pressure is low — firing flows
    freely (up to the hard ceiling). ABOVE the threshold the easing engages: the
    budget opens to `max_per_tick` minus what is still draining (`egress`),
    floored at `min_per_tick` so progress never stalls, and is never more than
    the backlog itself. So a deep backlog drains in eased waves, and as earlier
    fires age out of the egress window the budget eases back open."""
    threshold = int(easing["threshold"])
    lo = int(easing["min_per_tick"])
    hi = max(lo, int(easing["max_per_tick"]))  # a mis-set min never exceeds max
    if due_depth <= 0:
        return 0
    if due_depth <= threshold:
        return min(due_depth, hi)  # below threshold: flow freely, ceiling holds
    eased = max(lo, min(hi, hi - egress))  # ease open by drained headroom
    return min(eased, due_depth)


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
    reminder via the idle hook. Returns True if the spawn launched.

    Through the shared helper (issue #411): it ALWAYS sets stdin=subprocess.DEVNULL,
    closing the inherited-stdin hang this detached `claude --resume … -p …` used
    to leave open (it set stdout/stderr to DEVNULL but left stdin inherited — the
    same #390/#391 hang gate.py already fixed at its one call site). capture=False
    keeps the fire-and-forget output redirect; detached returns the Popen unwaited."""
    try:
        headless_spawn(target["fire"], cwd=target["fire_cwd"],
                       detached=True, capture=False)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def read_easing_setpoint(root=None):
    """The active easing setpoint for this repo, through the one shared reader
    (watcher.active_easing — the setpoints law, default-safe on any error so a
    bad read never bursts). `root` is the `.ai-native` directory."""
    ai = Path(root) if root else ROOT / ".ai-native"
    return watcher.active_easing(ai)


def run(now, fire=False, mtime=None, easing=None):
    """Select the eligible due sessions, bound them by the eased fire budget,
    and (if `fire`) resume only the freshest-idle slice. The ledger advances
    only for sessions actually fired. Returns (selected, fired, dry_run, budget).
    `easing` is injected for the teeth; otherwise read from the log."""
    if easing is None:
        easing = read_easing_setpoint()
    open_window = int(easing["open_window_seconds"])
    idle = watcher.idle_sessions(now, open_window=open_window, mtime=mtime)
    ledger = load_ledger()
    selected = due_targets(idle, ledger, now, mtime=mtime)
    egress = recent_egress(now, int(easing["egress_window_seconds"]))
    budget = eased_budget(len(selected), egress, easing)
    # freshest-idle first: the most recently active sessions most likely still
    # hold live, resumable context; the long-stale drain in later ticks (or age
    # out past the open window). Deterministic tiebreak on session id.
    ordered = sorted(selected, key=lambda t: (t["idle_seconds"], t["session_id"]))
    to_fire = ordered[:budget]
    if not fire:
        return selected, [], True, budget
    fired = []
    for t in to_fire:
        ok = _spawn(t)
        _trace({"ts": now, "session_id": t["session_id"],
                "cwd": t["fire_cwd"], "launched": ok})
        if ok:
            fired.append(t)
    save_ledger(advance_ledger(ledger, fired, now))
    return selected, fired, False, budget


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fire", action="store_true",
                    help="actually resume the due sessions (default: dry-run, "
                         "print what would fire and write nothing)")
    args = ap.parse_args(argv)

    selected, fired, dry, budget = run(time.time(), fire=args.fire)
    if not selected:
        print("result: done — no sessions due to probe (none idle-and-eligible, "
              "all cooling down, or all at their fire cap)")
        return 0
    ordered = sorted(selected, key=lambda t: (t["idle_seconds"], t["session_id"]))
    deferred = max(0, len(selected) - budget)
    for t in ordered[:budget]:
        mins = t["idle_seconds"] // 60
        print(f"  fire: {t['session_id']} (~{mins}m idle, in {t['fire_cwd']})")
    if dry:
        print(f"result: report — {len(selected)} eligible, fire budget {budget} "
              f"this tick ({deferred} eased back to a later tick); re-run with "
              "--fire. The external scheduler runs `probe.py --fire` as the tick.")
    else:
        print(f"result: report — fired {len(fired)}/{budget} (of {len(selected)} "
              f"eligible, {deferred} eased back to a later tick); every firing "
              f"traced to {TRACE.as_posix()} (the trust rail)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
