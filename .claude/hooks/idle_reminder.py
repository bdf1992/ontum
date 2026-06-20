#!/usr/bin/env python3
"""The idle continue-probe (done-line 0132): a soft reminder, injected.

Wired to UserPromptSubmit — the confirmed soft-injection lever (a Stop hook
can only force-continue or stop; it cannot softly inject). bdo's model: when
a session has sat idle ~15 min and someone picks it back up (a real return,
or an external timer's tick while away), drop a *soft, inferred, gateway-
bounded, fire-count-aware* reminder in front of the agent — "hey, continue if
you can" — and let the agent READ it and DECIDE. Injection, not control; the
opposite of the retired continue-beat block.

This hook is the WHEN+DELIVERY; loop.retry.compose is the WHAT. It measures
the gap since the last exchange (a timestamp in gitignored nag-state, the
mock-shame.json grain), and on a ≥threshold gap injects the composed reminder
as additionalContext (stdout on UserPromptSubmit is shown to the model). It
decays across consecutive idle injections and resets the moment the
conversation is active again.

The honest limit (named on the done-line): this fires on an *event* — a real
prompt, or an external re-invocation. To nudge while bdo is *truly away*
(no event at all), an external timer must re-invoke the session (local
cron / cloud routine); that is the separable second half. This hook is the
reliable in-repo heart and is useful on its own as a re-orientation when a
session is resumed after a gap.

Read-only on the log; writes only its own nag-state. Fail-open, exit 0 always.
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = "idle-reminder.json"


def main():
    try:
        sys.stdin.read()  # the hook payload; the nag-state below is the clock
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ROOT)
        ai_native = root / ".ai-native"
        sys.path.insert(0, str(root))
        from loop import retry

        now = time.time()
        state_path = ai_native / STATE
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
        last_ts = float(state.get("last_ts", now))
        fire_count = int(state.get("fire_count", 0))
        idle = max(0.0, now - last_ts)

        reminder = retry.compose(ai_native, idle, fire_count)
        if reminder:
            print(reminder)
            new_fire = fire_count + 1
        else:
            new_fire = 0  # active / nothing to say — reset the decay

        try:
            state_path.write_text(
                json.dumps({"last_ts": now, "fire_count": new_fire}),
                encoding="utf-8")
        except OSError:
            pass  # nag-state; failing to persist never blocks the prompt
    except Exception:
        pass  # fail-open: a broken probe never blocks the owner's prompt
    return 0


if __name__ == "__main__":
    sys.exit(main())
