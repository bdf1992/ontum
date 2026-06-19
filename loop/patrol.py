#!/usr/bin/env python3
"""The continue-beat (done-line 0127): ambient auto-continuation, silent on escalation.

bdo's ask (2026-06-18): "sometimes I'm here but I got AFK and I want
something to encourage agents to just continue working, and stopping if
and when they need me — and if the request is escalate then they stop the
reminders. Otherwise I don't need to prompt and prompt."

This module is the *decision* of a `Stop`-hook beat: when a session's turn
ends, should the patrol nudge it to continue, or stay silent and let it
stop? It is the session-level instance of the landing-throughput epic's
principle — a silent patrol that adds no bureaucracy
(`atom.…patrol-stays-silent-no-bureaucracy`): it senses, it does not judge,
and it is quiet unless there is a reason to speak.

The honest limit (named on the done-line): a `Stop` hook continues a
session that is *still running*. It cannot wake a process that already
exited — true AFK "wake it later" is a separate, timed layer (a scheduled
cloud routine), deferred. This beat makes "I don't need to prompt and
prompt" true for a *live* session.

## The decision (a pure function)

`decide(state, session_id, gap, owner_present)` is pure — no IO — so the
§10 teeth can hold it to derived behaviour (a constant decider fails). It
returns the action, the line to speak, and the next `state` to persist:

- **continue** — the field has work this session can carry (a `gap`), or
  the field is clean but bdo's standing direction is *find the next work,
  never wait* (an empty backlog does **not** silence the patrol — his
  deliberate choice; the ceiling is the backstop). The beat increments.
- **silent** (the agent stops, the nudges cease) when any of:
  - the **escalate marker** is armed — a session ran `loop.patrol
    escalate` because it hit a needs-you, is blocked on bdo's stamp, or
    genuinely needs him. Consumed on this stop (one stand-down per arm).
  - the **ceiling** is reached — the safety backstop against an AFK
    session burning unbounded tokens; it stands down and surfaces.
  - **parked-at-stamp** — the *only* work left is bdo's stamp (`gap` is
    None and the owner backlog is non-empty). Nothing a session can
    carry, so nudging past his stamp would be the bureaucracy the atom
    forbids. (A non-empty owner backlog alone never silences: a session
    keeps working non-stamp gaps.)

## The escalate marker

A session that needs bdo runs `python -m loop.patrol escalate --reason
"<why>"`. That **arms** a stand-down in the gitignored nag-state
`.ai-native/continue-beat.json` (the `mock-shame.json` precedent — ephemeral
session state, never the truth log). The next `Stop` consumes the arm and
the patrol goes silent. needs-you / parked-at-stamp are realized this way
too — a `Stop` hook cannot read a mid-session needs-you, so the agent
raises it deliberately. Within one working tree the active session is
serialized, so the arm is naturally scoped to the session that set it; the
rare same-tree interleave is named on the done-line as a v0 limit.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

# The safety ceiling: how many beats the patrol will auto-continue one
# session before standing down and surfacing. A code constant in v0; the
# done-line names its graduation to an *admitted dial* (--by bdo, the
# setpoint shape) as the next increment — it is dial-like, not an invariant.
CEILING = 12

STATE_NAME = "continue-beat.json"


def _state_path(root):
    return Path(root) / STATE_NAME


def load_state(root):
    """The per-working-tree nag-state, or an empty start. Never raises —
    a missing or torn file reads as a fresh patrol (the fold-over-the-log
    grain: absence is a clean start, not an error)."""
    try:
        return json.loads(_state_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(root, state):
    """Persist the nag-state. Failing to persist never blocks a turn —
    the worst case is one extra beat (the count didn't advance)."""
    try:
        _state_path(root).write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def _instruction(gap, beat, ceiling):
    """The line fed back to the model to make it continue. It carries the
    work, the beat budget, and the one-command way to stand the patrol
    down — so a session always knows both how to continue and how to stop."""
    head = (f"[continue-beat] beat {beat}/{ceiling} — no owner gesture is "
            "needed and there is work; keep going, do not stop and wait.")
    if gap is not None:
        why = gap["why"]
        if len(why) > 200:
            why = why[:200].rstrip() + " …"
        body = [
            f"  the next gap ({gap['kind']}): {gap['subject']} — {why}",
            f"  the move: {gap['move']}",
            "  full backlog: python -m loop.gaps",
        ]
    else:
        # empty backlog does NOT silence (bdo's choice): find the next work.
        body = [
            "  the gaps fold is clean — do not wait for direction: pull the "
            "next passed-but-unpulled slice (python -m loop.pull) or find the "
            "next contribution.",
        ]
    tail = [
        "  IF you hit a needs-you, are blocked on bdo's stamp, or genuinely "
        "need bdo (or there is truly nothing a session can do): run",
        '    python -m loop.patrol escalate --reason "<one line>"',
        "  then stop — that silences the patrol for this session. Otherwise "
        "continue.",
    ]
    return "\n".join([head] + body + tail)


def decide(state, session_id, gap, owner_present):
    """Pure: given the prior state, this session's id, the top self-
    serviceable gap (or None), and whether bdo's stamp queue is non-empty,
    return the beat decision. No IO — the §10 teeth depend on this.

    Returns a dict: {action: 'continue'|'silent', line, beat, ceiling,
    state} where `state` is the next nag-state to persist."""
    ceiling = CEILING

    # 1. the escalate marker, armed by a session that needs bdo. Consume it
    #    (one stand-down per arm) and go silent.
    if state.get("escalate_armed"):
        reason = state.get("escalate_reason") or "escalation requested"
        nxt = {"session_id": session_id, "beats": 0, "escalate_armed": False}
        return {"action": "silent", "beat": int(state.get("beats", 0)),
                "ceiling": ceiling, "state": nxt,
                "line": f"[continue-beat] escalate marker consumed — standing "
                        f"down for this session ({reason})."}

    # a new session starts a fresh patrol (fresh beats, no stale escalation).
    fresh = state.get("session_id") != session_id
    beats = 0 if fresh else int(state.get("beats", 0))

    # 2. the ceiling: the AFK token backstop. Stand down and surface; a new
    #    session (new id) gets a fresh ceiling.
    if beats >= ceiling:
        nxt = {"session_id": session_id, "beats": beats, "escalate_armed": False}
        return {"action": "silent", "beat": beats, "ceiling": ceiling,
                "state": nxt,
                "line": f"[continue-beat] ceiling ({ceiling}) reached — "
                        "standing down. Surface a digest for bdo "
                        "(python -m loop.digest) or leave a report."}

    # 3. parked-at-stamp: the ONLY work left is bdo's. Don't nudge past his
    #    stamp (a non-empty owner queue alone never silences — only when it
    #    is the sole remaining work).
    if gap is None and owner_present:
        nxt = {"session_id": session_id, "beats": beats, "escalate_armed": False}
        return {"action": "silent", "beat": beats, "ceiling": ceiling,
                "state": nxt,
                "line": "[continue-beat] the only work left is bdo's stamp — "
                        "nothing a session can carry; standing down "
                        "(parked-at-stamp). python -m loop.node inbox"}

    # 4. continue — there is a gap, or the field is clean and bdo's standing
    #    direction is to keep looking (the ceiling backstops an empty spin).
    new_beats = beats + 1
    nxt = {"session_id": session_id, "beats": new_beats, "escalate_armed": False}
    return {"action": "continue", "beat": new_beats, "ceiling": ceiling,
            "state": nxt, "line": _instruction(gap, new_beats, ceiling)}


def decide_from_root(root, session_id):
    """Gather the live inputs (the folds this beat composes, never re-derives)
    and decide, persisting the next state. `root` is the .ai-native dir."""
    from loop.gaps import top_gap
    from loop.summon import owner_backlog
    gap = top_gap(root)
    owner_present = bool(owner_backlog(root))
    state = load_state(root)
    res = decide(state, session_id, gap, owner_present)
    save_state(root, res["state"])
    return res


def arm_escalate(root, reason):
    """The session's deliberate stand-down (D-2: a session names its own
    escalation; the patrol never guesses one). Arms the marker the next
    Stop consumes. Writes nag-state only — never the truth log."""
    state = load_state(root)
    state["escalate_armed"] = True
    state["escalate_reason"] = reason or "escalation requested"
    save_state(root, state)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    sub = ap.add_subparsers(dest="cmd")
    esc = sub.add_parser("escalate", help="arm a stand-down: silence the "
                         "patrol for this session (needs-you / blocked / nothing to do)")
    esc.add_argument("--reason", required=True,
                     help="one line: why this session needs to stop")
    args = ap.parse_args(argv)

    if args.cmd == "escalate":
        arm_escalate(args.root, args.reason)
        print(f"result: done — escalate marker armed ({args.reason}); the next "
              "Stop stands the patrol down for this session")
        return 0

    # default: read-only status — the patrol's current state and what it
    # would decide right now (no session change, so it does not advance).
    state = load_state(args.root)
    sid = state.get("session_id", "—")
    beats = int(state.get("beats", 0))
    armed = bool(state.get("escalate_armed"))
    print(f"continue-beat — session {sid}: beat {beats}/{CEILING}"
          f"{', escalate armed' if armed else ''}")
    try:
        from loop.gaps import top_gap
        from loop.summon import owner_backlog
        gap = top_gap(args.root)
        owner_present = bool(owner_backlog(args.root))
        preview = decide(state, sid if sid != "—" else "preview",
                         gap, owner_present)
        print(f"  would: {preview['action']}")
        print(f"  {preview['line'].splitlines()[0]}")
    except Exception as e:  # read-only status must never crash the surface
        print(f"  (could not preview the decision: {e})")
    print("result: report — read-only patrol state; "
          'escalate with: python -m loop.patrol escalate --reason "<why>"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
