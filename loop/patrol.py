#!/usr/bin/env python3
"""The patrol escalate-marker (done-line 0127, retired-and-slimmed at 0135).

History: done-line 0127 built the **continue-beat** — a `Stop`-hook that
*forced* a session to continue every turn (`{"decision":"block"}`) unless an
escalation was armed. bdo's correction (2026-06-19): that was the wrong
primitive — it continues blind to whether he is present, after *every* turn, not
after silence. Done-line 0135 retired the forcing block and replaced it with the
**soft idle reminder** (`loop/retry.py` + `.claude/hooks/idle_reminder.py`): an
inferred, gateway-scoped suggestion injected *after a genuine idle gap*, which
the agent reads and DECIDES on. Injection, not control.

What survives, and why this module still exists: the **escalate marker** — a
session's deliberate stand-down. When a session hits a needs-you, is blocked on
bdo's stamp, or genuinely needs him, it runs `python -m loop.patrol escalate
--reason "<why>"`; that arms a marker the soft reminder reads (`retry.compose`
goes silent while it is armed). The forcing `decide` fold is gone; this marker —
the session naming its own escalation (D-2: the patrol never guesses one) — is
what the new soft part composes.

The marker is gitignored nag-state (`.ai-native/patrol.json`, the
`mock-shame.json` precedent — ephemeral session state, never the truth log).

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

STATE_NAME = "patrol.json"


def _state_path(root):
    return Path(root) / STATE_NAME


def load_state(root):
    """The per-working-tree marker state, or an empty start. Never raises —
    a missing or torn file reads as no escalation armed (the fold-over-the-log
    grain: absence is a clean start, not an error)."""
    try:
        return json.loads(_state_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(root, state):
    """Persist the marker state. Failing to persist never blocks a turn —
    the worst case is the soft reminder speaks once more before standing down."""
    try:
        _state_path(root).write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def arm_escalate(root, reason):
    """The session's deliberate stand-down (D-2: a session names its own
    escalation; the patrol never guesses one). Arms the marker the soft
    reminder reads to go silent. Writes nag-state only — never the truth log."""
    state = load_state(root)
    state["escalate_armed"] = True
    state["escalate_reason"] = reason or "escalation requested"
    save_state(root, state)


def disarm_escalate(root):
    """Clear an armed marker — the soft reminder may speak again. Used when a
    session resolves what it escalated for, or starts fresh."""
    state = load_state(root)
    state["escalate_armed"] = False
    state.pop("escalate_reason", None)
    save_state(root, state)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    sub = ap.add_subparsers(dest="cmd")
    esc = sub.add_parser("escalate", help="arm a stand-down: silence the soft "
                         "continue-probe for this session (needs-you / blocked / "
                         "nothing to do)")
    esc.add_argument("--reason", required=True,
                     help="one line: why this session needs to stop")
    sub.add_parser("disarm", help="clear an armed escalation marker")
    args = ap.parse_args(argv)

    if args.cmd == "escalate":
        arm_escalate(args.root, args.reason)
        print(f"result: done — escalate marker armed ({args.reason}); the soft "
              "continue-probe stays silent for this session until disarmed")
        return 0
    if args.cmd == "disarm":
        disarm_escalate(args.root)
        print("result: done — escalate marker cleared; the soft continue-probe "
              "may speak again")
        return 0

    # default: read-only status — is an escalation armed?
    state = load_state(args.root)
    armed = bool(state.get("escalate_armed"))
    if armed:
        print(f"patrol — escalation ARMED: {state.get('escalate_reason')}")
        print("  the soft continue-probe is silent for this session "
              "(disarm: python -m loop.patrol disarm)")
    else:
        print("patrol — no escalation armed; the soft continue-probe is free "
              "to speak after an idle gap (if the gateway is open)")
    print('result: report — read-only marker state; arm with: python -m '
          'loop.patrol escalate --reason "<why>"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
