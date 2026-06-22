#!/usr/bin/env python3
"""The session registration hook (done-line 0135): wired to SessionStart.

"Enable for all new sessions." Every session that opens here records itself —
`session_id -> {cwd, ts}` — into the watch registry (`~/.claude/ontum-sessions
.json`), so the external watcher (`loop.watcher`) can later find an idle one and
fire the soft continue-probe into it via `claude --resume`. The registry maps
id -> project dir because `--resume` lookup is scoped to the project directory
(verified empirically); the watcher must `cd` there to fire.

This hook is the WHEN+WHERE (it learns this session's id and cwd from the
SessionStart payload); `loop.watcher.register_session` is the WHAT (the pure
add-and-prune fold). It prunes dead sessions on every registration, so the
registry stays the set of plausibly-open sessions and never grows unbounded.

Read-only on the log; writes only the gitignored-by-location registry under
~/.claude (outside the repo, like the projects transcripts). Fail-open, exit 0
always — a broken registration never blocks a session from starting.
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    try:
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ROOT)
        sys.path.insert(0, str(root))
        from loop import watcher

        session_id = payload.get("session_id")
        # the cwd the session runs in (where --resume must be fired); prefer the
        # payload, fall back to the project dir / process cwd.
        cwd = (payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
               or str(root))
        if session_id:
            reg = watcher.load_registry()
            reg = watcher.register_session(reg, session_id, cwd, time.time())
            watcher.save_registry(reg)
    except Exception:
        pass  # fail-open: registration never gates the session
    return 0


if __name__ == "__main__":
    sys.exit(main())
