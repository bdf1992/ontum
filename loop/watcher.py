#!/usr/bin/env python3
"""The session watcher (done-line 0135, tier 1): deterministic idle detection.

bdo's model (2026-06-19), verified empirically: any open session is watched;
after ~15 min of silence a program deterministically fires a probe into it via
`claude --resume <session_id> -p "<probe>"`, which the agent SEES and continues
*in the session's own context* (proven: a resumed turn recalled a prior turn's
fact and appended to the same transcript). No agent-arming, no inference in the
trigger — a pure fold over signals already on disk:

  - the **activity signal is the transcript mtime**: Claude Code writes each
    session's turns to `~/.claude/projects/<project>/<session-id>.jsonl`, so
    `now - mtime` IS the idle time. Nothing to stamp.
  - the **registry** (`session_id -> project_dir`) is written by the
    `SessionStart` registration hook (`.claude/hooks/session_register.py`) for
    EVERY new session — "enable for all new sessions" — and is needed because
    `--resume` lookup is scoped to the project directory (verified): the
    watcher must `cd` there to fire. This fold only reads it.

This module is the **pure fold** (loop/'s no-network law): it decides *which*
sessions are idle-and-eligible and emits the exact fire command. It never
spawns `claude` itself — the network-reaching firing is the edge (the
continue-probe pen / the cron line that consumes this output), exactly as the
inference gateway's HTTP lives in its pen, never in loop/.

Eligibility is gateway-bounded for real (requirement 2): a session is a probe
target only where `loop.retry.gateway_open` (the default-deny PEP) permits it —
no policy, no probe, however idle. The probe payload, once the resumed turn
lands, is the soft `loop.retry` reminder injected by the idle hook, naming the
tool-scope the gateway granted.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
import time
from pathlib import Path

IDLE_THRESHOLD_SECONDS = 15 * 60
# beyond this, a session is presumed closed, not idle — don't resurrect the dead.
OPEN_WINDOW_SECONDS = 12 * 60 * 60
REGISTRY = Path.home() / ".claude" / "ontum-sessions.json"
PROJECTS = Path.home() / ".claude" / "projects"

# The fire-rate easing setpoint (done-line 0171). Opening the probe gateway
# made a whole backlog of idle sessions eligible at once; firing them all in one
# tick is the burst shape of the llama-server kill, but as spawned `claude`
# sessions the inference-queue semaphore does not govern. So the per-tick fire
# budget is bounded the orchestrate way — eased on ingress (the due-pool depth)
# and egress (fires still draining) past a threshold — and the bound is an
# ADMITTED setpoint, never a code constant (the setpoints law). DEFAULT_EASING
# is the default-safe fallback used only when none is admitted: a conservative
# drain that can never burst, not the operator's tuning knob.
EASING_DIAL = "continue-probe.easing"
DEFAULT_EASING = {
    "threshold": 3,            # due-pool depth below which firing flows freely
    "min_per_tick": 1,         # always make at least this much progress
    "max_per_tick": 3,         # the hard ceiling — never a burst
    "egress_window_seconds": IDLE_THRESHOLD_SECONDS,  # a fire "occupies" ~this long
    "open_window_seconds": OPEN_WINDOW_SECONDS,       # the staleness ceiling, now a dial
}
EASING_KEYS = tuple(DEFAULT_EASING)

PROBE = ("[continue-probe] You have been idle a while. You hold this session's "
         "context — if you can carry your current task one safe step further "
         "within your gateway, do it; otherwise stand down and say why. This is "
         "a suggestion, not an order.")


def load_registry(path=REGISTRY):
    """{session_id: {"cwd": <project_dir>, "ts": <registered_at>}} or {}.
    Never raises — a missing/torn registry is an empty watch, not an error."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_registry(registry, path=REGISTRY):
    """Persist the registry. Best-effort — a failed write loses one session's
    registration (it re-registers next SessionStart), never blocks a session."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(registry), encoding="utf-8")
        return True
    except OSError:
        return False


def read_easing(admissions):
    """The active easing setpoint, folded from the log (done-line 0171): the
    latest admitted `continue-probe.easing` setpoint wins (each admission
    supersedes the one before, like orchestrate's dial). Falls back to
    DEFAULT_EASING when none is admitted, and PER KEY when an admission is
    partial — so a missing key never drops a guard and the budget can never go
    unbounded on a half-set dial. Pure over the admissions list."""
    value = dict(DEFAULT_EASING)
    for adm in admissions:
        if adm.get("type") == "setpoint" and adm.get("dial") == EASING_DIAL:
            v = adm.get("value")
            if isinstance(v, dict):
                for k in EASING_KEYS:
                    if k in v:
                        value[k] = v[k]
    return value


def admit_easing(root, value, by, supersedes=None):
    """Append a `continue-probe.easing` setpoint admission. `by` is whoever
    stamps it (D-4: a node never sets its own dial). Mirrors
    orchestrate.admit_setpoint; the pen reads it at runtime, never a constant.
    `root` is the `.ai-native` root (where `log/` lives)."""
    from loop.reconcile import append_line, canon, now_ts, short_hash
    adm = {
        "id": "adm." + short_hash(EASING_DIAL, canon(value), str(by), now_ts()),
        "type": "setpoint",
        "dial": EASING_DIAL,
        "value": value,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def register_session(registry, session_id, cwd, now, mtime=None,
                     open_window=OPEN_WINDOW_SECONDS):
    """The pure half of the registration hook (done-line 0135): add/refresh
    this session's (session_id -> {cwd, ts}) entry and prune the dead — any
    registered session whose transcript is gone or has been silent past the
    open window is dropped, so the registry stays the set of *plausibly-open*
    sessions and never grows unbounded. Pure: `now`/`mtime` are injected so the
    §10 teeth drive it. Returns the new registry; never mutates the input."""
    if mtime is None:
        mtime = transcript_mtime
    out = {}
    for sid, info in registry.items():
        if sid == session_id:
            continue  # re-written fresh below
        m = mtime(sid)
        if m is not None and (now - m) <= open_window:
            out[sid] = info  # still plausibly open — keep
    if session_id and cwd:
        out[session_id] = {"cwd": cwd, "ts": now}
    return out


def transcript_mtime(session_id, projects=PROJECTS):
    """The newest transcript file for a session id across all projects, and its
    mtime (the activity signal), or None if no transcript exists."""
    newest = None
    try:
        for p in Path(projects).glob(f"*/{session_id}.jsonl"):
            m = p.stat().st_mtime
            if newest is None or m > newest:
                newest = m
    except OSError:
        return None
    return newest


def idle_sessions(now, registry=None, threshold=IDLE_THRESHOLD_SECONDS,
                  open_window=OPEN_WINDOW_SECONDS, gateway=None, mtime=None):
    """The fold: every registered session whose transcript has been silent at
    least `threshold` (but within `open_window`, so it is plausibly still open)
    AND whose project the gateway permits. Pure — `now`/`gateway`/`mtime` are
    injected so the §10 teeth can drive it. Each target carries the fire
    command (`claude --resume <id> -p <probe>`) and the cwd to fire it in."""
    if gateway is None:
        from loop.retry import gateway_open as gateway
    if mtime is None:
        mtime = transcript_mtime
    reg = registry if registry is not None else load_registry()
    out = []
    for sid, info in sorted(reg.items()):
        cwd = info.get("cwd")
        if not cwd:
            continue
        m = mtime(sid)
        if m is None:
            continue
        idle = now - m
        if idle < threshold or idle > open_window:
            continue  # active, or presumed-closed
        if not gateway(Path(cwd) / ".ai-native"):
            continue  # gateway default-deny: no policy, no probe
        out.append({
            "session_id": sid, "cwd": cwd, "idle_seconds": int(idle),
            "fire": ["claude", "--resume", sid, "-p", PROBE],
            "fire_cwd": cwd,
        })
    return out


def _active_easing(root):
    """The easing setpoint folded from `root`'s log, default-safe on any error
    (a bad read must never widen the open window or unbound the budget)."""
    try:
        from loop.reconcile import Fold
        return read_easing(Fold(root).admissions)
    except Exception:
        return dict(DEFAULT_EASING)


def main(argv=None):
    from loop.reconcile import DEFAULT_ROOT, canon
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=int, default=IDLE_THRESHOLD_SECONDS,
                    help="seconds of silence before a session is a probe target")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="the .ai-native root the easing setpoint is read from")
    ap.add_argument("--json", dest="as_json", action="store_true")
    ap.add_argument("--admit-setpoint", metavar="JSON",
                    help="append a continue-probe.easing setpoint and exit, e.g. "
                         '\'{"threshold":3,"min_per_tick":1,"max_per_tick":3,'
                         '"egress_window_seconds":900,"open_window_seconds":43200}\'')
    ap.add_argument("--by", help="who admits the setpoint (required with "
                                 "--admit-setpoint, D-4)")
    args = ap.parse_args(argv)

    if args.admit_setpoint:
        if not args.by:
            print("result: needs-you — a setpoint is admitted *by* someone "
                  "(--by), never self-set (D-4)")
            return 2
        value = json.loads(args.admit_setpoint)
        unknown = [k for k in value if k not in EASING_KEYS]
        if unknown:
            print(f"result: needs-you — unknown easing key(s): {', '.join(unknown)}"
                  f"; the dials are {', '.join(EASING_KEYS)}")
            return 2
        adm = admit_easing(args.root, value, args.by)
        print(f"result: report — easing setpoint {adm['id']} admitted by "
              f"{args.by}: {canon(value)}")
        return 0

    easing = _active_easing(args.root)
    open_window = int(easing["open_window_seconds"])
    targets = idle_sessions(time.time(), threshold=args.threshold,
                            open_window=open_window)
    if args.as_json:
        print(json.dumps(targets, indent=2))
        return 0
    sp = "DEFAULT (none admitted)" if easing == DEFAULT_EASING else canon(easing)
    print(f"easing setpoint: {sp}")
    if not targets:
        print("result: done — no idle-and-eligible sessions to probe "
              "(none registered, none idle past threshold, or gateway closed)")
        return 0
    for t in targets:
        mins = t["idle_seconds"] // 60
        print(f"idle session {t['session_id']} (~{mins}m, in {t['cwd']})")
        print(f"  fire: cd {t['fire_cwd']} && claude --resume {t['session_id']} "
              f'-p "<continue-probe>"')
    print(f"result: report — {len(targets)} idle session(s) eligible to probe; "
          "the per-tick fire budget (the eased slice) is the pen's, not this "
          "fold — this names who is eligible, the pen bounds how many fire")
    return 0


if __name__ == "__main__":
    sys.exit(main())
