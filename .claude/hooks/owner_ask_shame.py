#!/usr/bin/env python3
"""UserPromptSubmit owner-ask shame (done-line 0058): a needs-you item parked
only in a report screams until it reaches bdo.

A session (report 0047) ended with FIVE items "awaiting bdo" written only
into its report — an uncommitted file in a working tree bdo never opens.
Those decisions sat invisibly parked on him: the reflect machinery mirrors
the owner-stamp *queue*, but an ad-hoc needs-you item in a report enters no
queue and reaches no surface he reads. bdo's correction (2026-06-12):
"things shouldn't be parked on me without a clear plain-English cold-read
handoff."

So this hook is the floor, the mock-shame grain pointed at owner-asks. On
every prompt:

  1. Reads the live unsurfaced owner-ask groups from the durable record (a
     fold over `.ai-native/reports/` minus the 'open' reflection acks on the
     log — never a literal): every report whose needs-you items have reached
     no surface bdo reads.
  2. Carries a tally of turns the *same* unsurfaced set has sat, in
     `.ai-native/owner-ask-shame.json` (gitignored nag state). It resets the
     moment the set shrinks: an ask reaching his inbox (an 'open' reflection
     record) is the only thing that buys its silence.
  3. Escalates its volume with the tally and names the most recent report's
     asks, so the scream is concrete — and points at the one move that quiets
     it: surface them through the reflect mirror.

The mirror is bdo's GitHub inbox via the owner-ask-backlog drift kind (the
reflect pen, once he admits the rule); this hook never reaches out and never
stands in for him (D-4). When nothing is unsurfaced it prints nothing and
resets. Fail-open, exit 0 always — a broken shame beat must never block the
owner's prompt.
"""

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def project_root():
    """The session's project anchor (CLAUDE_PROJECT_DIR) when given, else
    this checkout's root — the same resolution mock_shame and summon use."""
    return pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or ROOT)


def unsurfaced(ai_native):
    """The live unsurfaced owner-ask groups — a fold, never a literal."""
    sys.path.insert(0, str(ROOT))
    from loop.reflect import unsurfaced_owner_ask_groups
    return unsurfaced_owner_ask_groups(ai_native)


def tally(state_path, current):
    """Turns the *same* unsurfaced set has sat. Same set -> +1 (another turn
    parked on him). A shrunk set (an ask reached him) -> 0. A changed-but-not-
    shrunk set or a first sighting -> 1, start counting."""
    prior = {}
    try:
        prior = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    prev_set, prev_turns = set(prior.get("ask_set", [])), int(prior.get("turns", 0))
    cur_set = set(current)
    if not cur_set:
        turns = 0
    elif cur_set == prev_set:
        turns = prev_turns + 1
    elif cur_set < prev_set:
        turns = 0
    else:
        turns = 1
    try:
        state_path.write_text(
            json.dumps({"turns": turns, "ask_set": current}), encoding="utf-8")
    except OSError:
        pass  # the tally is nag state; failing to persist it never blocks a turn
    return turns


def banner(turns, n_asks, n_reports):
    """Louder the longer it is ignored (the shame must grow, bdo's rule)."""
    head = f"{n_asks} owner-ask(s) across {n_reports} report(s)"
    if turns <= 2:
        return (f"[owner-ask-shame] turn {turns}: {head} reached no surface "
                "bdo reads — parked only in a report file he never opens. "
                "Surface them; do not hand them off invisibly.")
    if turns <= 6:
        return (f"[owner-ask-shame] turn {turns} ignoring {head} parked on "
                "bdo. This is exactly how report 0047's five taps went "
                "invisible — a needs-you written into a working-tree file is "
                "not a handoff. Surface them, or say plainly you are not.")
    if turns <= 14:
        return (f"[OWNER-ASK-SHAME] {turns} TURNS and {head} still sit unseen "
                "by the owner. An ask he never receives is a decision you "
                "silently took for him. STOP parking work on him invisibly.")
    return (f"[OWNER-ASK-SHAME] {turns} TURNS OF LEAVING {head} STRANDED. Get "
            "them to a surface he reads this turn or tell bdo why not — "
            "nothing else here counts until they reach him.")


def scream(turns, groups):
    n_asks = sum(len(g["asks"]) for g in groups)
    print(banner(turns, n_asks, len(groups)))
    recent = groups[-1]  # sorted by report file; the latest handoff
    sample = "; ".join(recent["asks"][:3])
    more = "" if len(recent["asks"]) <= 3 else f" (+{len(recent['asks']) - 3} more)"
    print(f"[owner-ask-shame] most recent: {recent['report_id']} parks "
          f"{len(recent['asks'])} — {sample}{more}")
    print("[owner-ask-shame] surface them through the mirror bdo reads: "
          "enable it once (python -m loop.reflect rule --kind "
          "owner-ask-backlog --surface github-issues --on --by bdo), or apply "
          "by hand (python .claude/skills/reflect/reflect.py apply --surface "
          "github-issues --by <who>). Each open is receipted; the scream stops.")


def main():
    try:
        sys.stdin.read()  # the hook payload; the fold below is the truth, not it
        ai_native = project_root() / ".ai-native"
        groups = unsurfaced(ai_native)
        turns = tally(ai_native / "owner-ask-shame.json",
                      sorted(g["id"] for g in groups))
        if groups:
            scream(turns, groups)
        # nothing unsurfaced: silent. The shame is for parking on him, not the past.
    except Exception:
        pass  # fail-open: a broken shame beat never blocks the owner's prompt
    return 0


if __name__ == "__main__":
    sys.exit(main())
