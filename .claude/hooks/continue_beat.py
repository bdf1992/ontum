#!/usr/bin/env python3
"""The continue-beat hook (done-line 0127): wired to Stop.

When a session's turn ends, this beat decides — through the pure
`loop.patrol.decide` fold — whether to nudge the session to continue or
stay silent and let it stop. It is bdo's ask made ambient: "I don't need
to prompt and prompt" for a *live* session, and "if the request is
escalate then they stop the reminders."

- To **continue**: print `{"decision":"block","reason":<the next move>}`
  on stdout and exit 0 — Claude Code feeds the reason back as the next
  instruction, so the session keeps working with no prompt from bdo.
- To **stand down** (escalated / ceiling / parked-at-stamp): print
  nothing and exit 0 — the session stops, the nudges cease.

Fail-SAFE means fail-to-STOP here, the *opposite* of the other beats'
fail-open-and-continue: any internal error or malformed payload lets the
session stop. A bug that always-continued would trap an AFK session
burning unbounded tokens — the one failure mode this beat must never have.
It writes only the gitignored nag-state (via the pen), never the log.
"""

import json
import os
import sys
from pathlib import Path


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # malformed payload → fail-safe: let the session stop

    try:
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
        sys.path.insert(0, str(root))
        from loop import patrol
        session_id = payload.get("session_id") or "default"
        ai_native = root / "ai-native" if (root / "ai-native").is_dir() \
            else root / ".ai-native"
        res = patrol.decide_from_root(ai_native, session_id)
        if res["action"] == "continue":
            # block the stop and hand the model its next move
            print(json.dumps({"decision": "block", "reason": res["line"]}))
        # silent: print nothing, the session stops
    except Exception:
        return 0  # fail-safe to STOP: never trap a session in a broken beat
    return 0


if __name__ == "__main__":
    sys.exit(main())
