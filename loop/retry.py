#!/usr/bin/env python3
"""The inferred-retry composer (done-line 0135): the soft idle reminder.

bdo's correction (2026-06-19): the continue-beat's instant `Stop`-hook block
(done-line 0127) was the wrong primitive — it *forces* the agent to continue
after every turn, blind to whether bdo is present. What he wants is a
**reminder injected as context**: a soft, inferred suggestion that sits in
front of an idle session and says "hey — continue if you can", which the
agent reads and *decides* on. Injection, not control. After silence, not
every turn. He set four requirements; this composer meets the first two and
the hook + watcher meet the rest:

1. **Contextual to the session.** The away-trigger re-pokes the live session —
   which still holds its own transcript — so the reminder is **session-first**
   ("continue what you were doing; you have the context"); the repo backlog is
   only a fallback hint.
2. **Gateway-bounded, with a tool-scope.** `compose()` consults the real PEP
   `loop.inference` and is **default-deny**: silent until bdo admits a
   continue-probe policy. The permit also carries a **tool-scope** (the tier-2
   lever, proven empirically: a resumed session can *propose* but is tool-
   permission-gated from *executing*) — propose-only by default, widened only
   by bdo's stamp — and the reminder NAMES it, so a continued session knows how
   far its reach goes.
3+4. **"While away"** — the firing edge (`loop.watcher` + the continue-probe
   pen) resumes an idle session out of band; the idle hook
   (`.claude/hooks/idle_reminder.py`) gates the injection on a genuine ≥15-min
   gap.

The suggestion is **soft** (never `decision: block`), **decaying** (gentle →
firm → stands down at MAX, never identical nagging), and **silent** when the
session is active, escalated, or the gateway has not been opened.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

# below this gap since the last exchange, the session is "active" — no probe.
# Code constants in v0; the done-line names their graduation to admitted dials.
IDLE_THRESHOLD_SECONDS = 15 * 60
MAX_NUDGES = 4

# the gateway coordinates: a continue-probe is a (caller, surface, mind) the
# real PEP must permit. Default-deny until bdo admits the matching policy.
CALLER, SURFACE, MIND = "session", "continue-probe", "self"


def gateway_scope(root):
    """The tool-scope a continue-probe is granted here, or None if not
    permitted (done-line 0135). A default-deny fold over admitted policy
    (loop.inference): no policy → None, and the probe stays silent no matter
    how idle. A permit carries its scope — propose-only unless bdo stamped
    `full`. This is requirement 2's tier-2 half: the bound is not just may/
    may-not, it is *how far*."""
    try:
        from loop.reconcile import Fold
        from loop import inference
        return inference.policy_scope(Fold(root), CALLER, SURFACE, MIND)
    except Exception:
        return None  # fail-closed: a broken gateway read denies (never nags)


def gateway_open(root):
    """Requirement 2 — the may/may-not bound: a probe fires only where the
    gateway permits one. True iff a tool-scope is granted (any scope)."""
    return gateway_scope(root) is not None


def _scope_line(scope):
    """How the reminder names the reach the gateway granted — so a continued
    session does not over-reach a propose-only stamp, nor under-use a full one."""
    from loop import inference
    if scope == inference.FULL:
        return ("  Your gateway scope here is FULL — you may execute, not just "
                "propose. Still: only safe, in-bounds steps.")
    return ("  Your gateway scope here is PROPOSE-ONLY — draft and propose the "
            "next step, but do not execute it; leave the doing for bdo's wider "
            "stamp or a present session.")


def _decay(fire_count):
    """How the same probe reads as it repeats — gentler first, then firmer,
    then silent. fire_count is how many times it has already fired (0 = first)."""
    n = fire_count + 1
    if n == 1:
        return ("Still here? It's been quiet", f"(nudge {n})")
    if n <= MAX_NUDGES - 1:
        return ("Still idle", f"(nudge {n} of {MAX_NUDGES})")
    return ("Last nudge", f"(nudge {n} of {MAX_NUDGES} — then I stand down)")


def _fallback(root):
    """A backlog hint for *after* the session's own thread is genuinely done —
    never the headline (the session's own context is). None when the only work
    left is bdo's stamp."""
    from loop.gaps import top_gap
    gap = top_gap(root)
    if gap is None:
        return ("if you've genuinely finished, the field is clean — a "
                "passed-but-unpulled slice (python -m loop.pull) or a "
                "contribution is the next thing")
    return (f"if you've genuinely finished it, the backlog's next step is "
            f"{gap['subject']} ({gap['kind']}) — {gap['move']}")


def compose(root, idle_seconds, fire_count):
    """The soft idle reminder to inject, or None to stay silent.

    Silent when: still active; the nudge budget is spent; an escalation is
    armed; or the gateway is not open (default-deny). Otherwise a soft,
    session-first, decaying suggestion the agent reads and decides on, naming
    the tool-scope its gateway granted."""
    if idle_seconds < IDLE_THRESHOLD_SECONDS:
        return None  # active conversation — never inject
    if fire_count >= MAX_NUDGES:
        return None  # said its piece; stands down (no identical nagging)

    # escalation silences the probe (D-2: a session names its own escalation).
    from loop import patrol
    if patrol.load_state(root).get("escalate_armed"):
        return None

    # the real gateway, default-deny, with its tool-scope (requirement 2).
    scope = gateway_scope(root)
    if scope is None:
        return None

    mins = int(idle_seconds // 60)
    lead, tag = _decay(fire_count)
    fb = _fallback(root)
    lines = [
        f"[continue-probe] {lead} (~{mins}m since the last exchange) {tag}.",
        "  You still hold this session's context — if you were mid-task and can "
        "carry it one safe step further within your gateway, do that.",
        _scope_line(scope),
    ]
    if fb:
        lines.append(f"  ({fb}.)")
    lines.append(
        "  This is a SUGGESTION, not an order — continue only if it's safe and "
        "in-bounds. If you need bdo, or there's nothing safe to continue, stand "
        'down (arm: python -m loop.patrol escalate --reason "<why>").')
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--idle", type=int, default=IDLE_THRESHOLD_SECONDS)
    ap.add_argument("--fire-count", type=int, default=0)
    args = ap.parse_args(argv)
    reminder = compose(args.root, args.idle, args.fire_count)
    if reminder is None:
        scope = gateway_scope(args.root)
        gate = f"open [{scope}]" if scope else "CLOSED (default-deny)"
        print(f"result: done — the probe stays silent (gateway {gate}; or "
              "active / spent / escalated)")
        return 0
    print(reminder)
    print("result: report — the soft reminder above is what the idle hook "
          "would inject; the agent reads it and decides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
