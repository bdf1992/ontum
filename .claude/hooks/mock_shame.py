#!/usr/bin/env python3
"""UserPromptSubmit shame beat (done-line 0033): the mock count screams.

A session built a ledger that reported "every run moved work" while every
"verdict" was a constant hardcoded into a mock node — a state machine
shuffling JSON with the answers written into the source (report 0033 §the
45-line context; bdo's foot-down). bdo's correction, on the record: ANY
mock service or namespace must be SCREAMED into the context window, every
turn, with a shame that GROWS the longer it is ignored and only goes quiet
when a stage is actually made real.

So this hook, on every prompt:

  1. Reads the live still-mock set from the LOG (a fold, never a literal):
     the PIPELINE stages whose node id is `.mock` and that no `node_real`
     admission has replaced. This set is truth; the tally below is only
     pressure.
  2. Carries a tally of turns the *same* mock set has sat unaddressed,
     persisted in `.ai-native/mock-shame.json` (gitignored nag state —
     deletable; the log is the truth it points at). The tally RESETS the
     moment the set shrinks: a stage going real is the only thing that
     buys silence.
  3. Escalates its volume with the tally — firm, then loud, then all-caps
     — and names every still-mock node so the scream is concrete.

When no mock stages remain, it prints nothing and resets the tally: the
shame is for sitting on mocks, not for having once had them. Fail-open,
exit 0 always — a broken shame beat must never block the owner's prompt.
"""

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ".ai-native/mock-shame.json"


def project_root():
    """The session's project anchor (CLAUDE_PROJECT_DIR) when given, else
    this checkout's root — same resolution loop.summon uses for its hook."""
    return pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or ROOT)


def still_mock(ai_native):
    """The mock stages the log has NOT yet made real — a fold, never a code
    literal. A PIPELINE node is mock if its id carries `.mock`; it stops
    being mock the instant a node_real admission names a replacement."""
    sys.path.insert(0, str(ROOT))
    from loop.reconcile import PIPELINE, Fold, real_nodes
    real = real_nodes(Fold(ai_native))
    mocks = [s["node"] for s in PIPELINE if ".mock" in s["node"]]
    return sorted(n for n in mocks if n not in real)


def tally(state_path, current):
    """Turns the *same* mock set has sat. Same set → +1 (another turn
    ignored). A shrunk set (a stage went real) → 0, and we say so. A
    changed-but-not-shrunk set or a first sighting → 1, start counting."""
    prior = {}
    try:
        prior = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    prev_set, prev_turns = set(prior.get("mock_set", [])), int(prior.get("turns", 0))
    cur_set = set(current)
    if not cur_set:
        turns, shrank = 0, bool(prev_set)  # clean: no shame to count
    elif cur_set == prev_set:
        turns, shrank = prev_turns + 1, False
    elif cur_set < prev_set:
        turns, shrank = 0, True
    else:
        turns, shrank = 1, False
    try:
        state_path.write_text(
            json.dumps({"turns": turns, "mock_set": current}), encoding="utf-8")
    except OSError:
        pass  # the tally is nag state; failing to persist it never blocks a turn
    return turns, shrank


def banner(turns):
    """Louder the longer it is ignored (bdo: the shame must grow)."""
    if turns <= 2:
        return (f"[mock-shame] turn {turns}: mock pipeline stages are still "
                "sitting. Name them; do not narrate work around them.")
    if turns <= 6:
        return (f"[mock-shame] turn {turns} ignoring mock code. This is exactly "
                "how performative work hides — a constant dressed as a verdict. "
                "Make a stage real, or say plainly you are choosing not to.")
    if turns <= 14:
        return (f"[MOCK-SHAME] {turns} TURNS and these stages still stamp a fixed "
                "verdict with no judgement. Every 'advanced' line the loop emits "
                "is a mock moving fake work. STOP dressing it as progress.")
    return (f"[MOCK-SHAME] {turns} TURNS OF IGNORING THIS. The ledger measures a "
            "mock moving fake work and you keep letting it advance. Make a stage "
            "REAL this turn or tell bdo why not — nothing else here counts until "
            "one does.")


def scream(turns, mocks):
    print(banner(turns))
    print(f"[mock-shame] {len(mocks)} stage(s) STILL MOCK (fixed verdict, no "
          f"judgement): {', '.join(mocks)}")
    print("[mock-shame] make one real — do not build around it: "
          "python -m loop.node admit-real --stage <mock-node> --node <real-node> --by <who>")


def main():
    try:
        sys.stdin.read()  # the hook payload; the fold below is the truth, not it
        ai_native = project_root() / ".ai-native"
        mocks = still_mock(ai_native)
        turns, _shrank = tally(ai_native / "mock-shame.json", mocks)
        if mocks:
            scream(turns, mocks)
        # no mocks: silent. The shame is for sitting on them, not for the past.
    except Exception:
        pass  # fail-open: a broken shame beat never blocks the owner's prompt
    return 0


if __name__ == "__main__":
    sys.exit(main())
