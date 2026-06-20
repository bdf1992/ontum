#!/usr/bin/env python3
"""The session watcher (done-line 0132, tier 1): deterministic idle detection.

bdo's model (2026-06-19), verified empirically: any open session is watched;
after ~15 min of silence a program deterministically fires a probe into it via
`claude --resume <session_id> -p "<probe>"`, which the agent SEES and continues
*in the session's own context* (proven: a resumed turn recalled a prior turn's
fact and appended to the same transcript). No agent-arming, no inference in the
trigger — a pure fold over signals already on disk:

  - the **activity signal is the transcript mtime**: Claude Code writes each
    session's turns to `~/.claude/projects/<project>/<session-id>.jsonl`, so
    `now - mtime` IS the idle time. Nothing to stamp.
  - the **registry** (`session_id -> project_dir`) is needed only because
    `--resume` lookup is scoped to the project directory (verified): the
    watcher must `cd` there to fire. A SessionStart hook records it; this fold
    reads it.

This module is the **pure fold** (loop/'s no-network law): it decides *which*
sessions are idle-and-eligible and emits the exact fire command. It never
spawns `claude` itself — the network-reaching firing is the edge (a pen / the
cron line that consumes this output), exactly as the inference gateway's HTTP
lives in its pen, never in loop/.

Eligibility is gateway-bounded for real (requirement 2): a session is a probe
target only where `loop.retry.gateway_open` (the default-deny PEP) permits it —
no policy, no probe, however idle. The probe payload, once the resumed turn
lands, is the soft `loop.retry` reminder injected by the idle hook.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

IDLE_THRESHOLD_SECONDS = 15 * 60
# beyond this, a session is presumed closed, not idle — don't resurrect the dead.
OPEN_WINDOW_SECONDS = 12 * 60 * 60
REGISTRY = Path.home() / ".claude" / "ontum-sessions.json"
PROJECTS = Path.home() / ".claude" / "projects"

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
                  open_window=OPEN_WINDOW_SECONDS, gateway=None):
    """The fold: every registered session whose transcript has been silent at
    least `threshold` (but within `open_window`, so it is plausibly still open)
    AND whose project the gateway permits. Pure — `now`/`gateway` are injected
    so the §10 teeth can drive it. Each target carries the fire command."""
    if gateway is None:
        from loop.retry import gateway_open as gateway
    reg = registry if registry is not None else load_registry()
    out = []
    for sid, info in sorted(reg.items()):
        cwd = info.get("cwd")
        if not cwd:
            continue
        mtime = transcript_mtime(sid)
        if mtime is None:
            continue
        idle = now - mtime
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=int, default=IDLE_THRESHOLD_SECONDS,
                    help="seconds of silence before a session is a probe target")
    ap.add_argument("--json", dest="as_json", action="store_true")
    args = ap.parse_args(argv)

    targets = idle_sessions(time.time(), threshold=args.threshold)
    if args.as_json:
        print(json.dumps(targets, indent=2))
        return 0
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
          "the firing is the edge (a pen/cron consumes this), not this fold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
