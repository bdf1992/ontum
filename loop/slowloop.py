#!/usr/bin/env python3
"""The slow loop's proposer (done-line 0074): outcomes reach the dial, without
signing their own line.

The doctrine's two time-scales (§14): the **fast loop** (`orchestrate`) holds
the setpoint each tick; the **slow loop** *moves the setpoint itself* from
accumulated outcomes — run hot to explore, cool to consolidate. Until now only
the fast loop existed; the dial moved only by a human's `--admit-setpoint`. The
sensing half is built (done-lines 0069 outcome-pressure, 0072 temporal, 0073
summon delivers it). This is the slow loop's reach *to* the dial.

It reaches, deliberately, only halfway — and that is the whole design. A closed
loop has no outside, but the substrate's physics is "no node signs its own line;
the owner is the last stop" (D-4). The contradiction dissolves into **propose
vs dispose**:

  - this fold may **propose** a setpoint change that is *caused by outcomes* and
    carries its attribution (the `because`);
  - the **disposition** — the actual `admit_setpoint`, the act that changes what
    the system aims at — stays an act of the **outside** and is never taken here.

The proposer is answer-agnostic. *Who* disposes — bdo forever, a standing
bounded auto-admit within named limits, or an independent judge node — is the
open question, and it is **bdo's to answer** (D-4), not this module's. So the
loop is closed enough to be *causal* (the proposal is attributable to the tick
history that caused it) and open exactly where an outside is required.

The causal content is the attribution. A cycle that adjusts a dial with no
attributable cause is not a *causal* loop — it is repetition. So a proposed
change with no evidence is refused: no outcomes on the record, no proposal.

Read-only (I-3), stdlib only. Writes nothing — never `admit_setpoint`. CLI ends
with a clear result on stdout (D-6): done | report | needs-you.

CLI:
  python -m loop.slowloop            the current dial + the proposal it would make
  python -m loop.slowloop --hour 8   a fixed moment (deterministic)
  python -m loop.slowloop --json     the dataset, machine-readable
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, canon, load_atoms
from loop.orchestrate import read_setpoint, SETPOINT_KEYS

REPO = Path(__file__).resolve().parent.parent

# the bands of the field's recent temperature that decide the proposal. cool
# is the load-bearing direction (I-7): a field that keeps hitting the human cap
# is over-driven and should consolidate; a field that never cools with work
# left to explore can afford to run hotter.
WINDOW = 12          # recent ticks the slow loop folds over
COOL_HI = 0.6        # cooled this often -> consolidate (lower the budget)
COOL_LO = 0.34       # cooled this rarely -> room to explore (raise it)
MIN_BUDGET = 1       # the temperature floor: a budget of 0 would freeze the field


def read_ticks(fold):
    """The field's outcomes on the record: every admitted tick, in order. The
    slow loop learns from these — mode (heat/cool), the deferrals, the
    pressure each tick met."""
    return [a for a in fold.admissions if a.get("type") == "tick"]


def fold_signals(root, hour, window=WINDOW):
    """Fold the outcomes the proposal is caused by — purely, over the log and
    the committed evidence. The tick history is the spine; the outcome-pressure
    phase and the hour's temporal lean compose onto it."""
    fold = Fold(Path(root))
    ticks = read_ticks(fold)
    recent = ticks[-window:] if ticks else []
    n = len(recent)
    cool = sum(1 for t in recent if t.get("mode") == "cool")
    deferred = sum(len(t.get("deferred", [])) for t in recent)

    # outcome-pressure phase (loop.pressure), if this repo carries the probe-set
    phase = unresolved = leverage = None
    repo = Path(root).resolve().parent
    from loop.pressure import DEFAULT_PROBES, pressure as pressure_fold
    probes = repo / "outcomes" / DEFAULT_PROBES.name
    if probes.exists():
        pr = pressure_fold(probes, repo=repo, root=root)
        phase = pr["phase"]
        unresolved = len(pr["partial"]) + len(pr["unmet"]) + len(pr["dormant"])
        leverage = pr["top_leverage"]["id"] if pr["top_leverage"] else None

    # the hour's temporal lean (loop.temporal)
    from loop.temporal import load_schedule, register_at
    schedule, _, _ = load_schedule(root)
    band = register_at(hour, schedule)

    return {
        "ticks_considered": n,
        "cool_count": cool,
        "cool_ratio": (cool / n) if n else None,
        "deferred_total": deferred,
        "phase": phase,
        "unresolved": unresolved,
        "leverage": leverage,
        "lean": band["lean"] if band else None,
        "register": band["register"] if band else None,
    }


def propose(setpoint, signals):
    """From the folded outcomes, a *proposed* setpoint and its attribution.
    The only dial this v0 moves is the temperature (step_budget_per_tick), the
    doctrine's run-hot/run-cool dial; the human queue cap is the owner's load,
    never proposed away, and the rest is held. Writes nothing; the returned
    `disposition` names the outside's act."""
    cur = dict(setpoint["value"])
    b = int(cur["step_budget_per_tick"])
    n = signals["ticks_considered"]
    because, direction = [], 0  # -1 cool, +1 heat, 0 hold

    if n == 0:
        # no outcomes on the record: nothing to attribute a change to. A
        # proposal without a cause is refused (it would be a cycle, not causal).
        because.append("no tick history yet — nothing to attribute a change to; "
                       "hold until the field has run")
    else:
        cr = signals["cool_ratio"]
        hot = n - signals["cool_count"]
        if cr >= COOL_HI:
            direction = -1
            because.append(
                f"the field cooled in {signals['cool_count']} of {n} recent "
                f"ticks (cool_ratio {cr:.2f} >= {COOL_HI}) — the human queue kept "
                "hitting its cap; lower the exploration budget so the slow stage "
                "drains (cool to consolidate, I-7)")
        elif cr <= COOL_LO:
            if signals["phase"] == "build" and signals["leverage"]:
                direction = +1
                because.append(
                    f"the field ran hot in {hot} of {n} recent ticks (cool_ratio "
                    f"{cr:.2f} <= {COOL_LO}) with build-phase work unresolved "
                    f"({signals['unresolved']} probes, leverage "
                    f"{signals['leverage']}) — raise the budget to explore (run "
                    "hot to explore)")
            else:
                because.append(
                    f"the field rarely cooled (cool_ratio {cr:.2f}) but the "
                    f"outcome is not a build phase with leverage (phase "
                    f"{signals['phase']}) — nothing to explore toward; hold")
        else:
            lean = signals["lean"]
            if lean == "cool":
                direction = -1
                because.append(
                    f"the field is balanced (cool_ratio {cr:.2f}) and the hour "
                    f"leans cool ({signals['register']}) — consolidate: lower the "
                    "budget a step")
            elif lean == "heat" and signals["phase"] == "build" and signals["leverage"]:
                direction = +1
                because.append(
                    f"the field is balanced (cool_ratio {cr:.2f}) and the hour "
                    f"leans heat ({signals['register']}) with build-phase leverage "
                    f"{signals['leverage']} — explore: raise the budget a step")
            else:
                because.append(
                    f"the field is balanced (cool_ratio {cr:.2f}) and the hour is "
                    f"{lean} — hold")

    proposed_b = max(MIN_BUDGET, b + direction)
    if direction < 0 and proposed_b == b:
        because.append(f"(budget already at the floor {MIN_BUDGET}; cannot cool "
                       "further — hold)")
    proposed = dict(cur)
    proposed["step_budget_per_tick"] = proposed_b
    deltas = {k: proposed[k] - cur[k] for k in cur
              if isinstance(cur.get(k), (int, float)) and proposed[k] != cur[k]}

    return {
        "current": cur,
        "proposed": proposed,
        "deltas": deltas,
        "change": bool(deltas),
        "because": because,
        "signals": signals,
        "disposition": ("proposal only — the dial changes when the outside "
                        "admits it (D-4): python -m loop.orchestrate "
                        f"--admit-setpoint '{canon(proposed)}' --by <whoever>"),
    }


def slowloop(root, hour):
    """The full read: the current dial, the folded outcomes, the proposal.
    Returns None for the setpoint when none is admitted (the dial is a record,
    not a default — I-8)."""
    fold = Fold(Path(root))
    setpoint = read_setpoint(fold.admissions)
    signals = fold_signals(root, hour)
    if setpoint is None:
        return {"setpoint": None, "signals": signals, "proposal": None}
    return {"setpoint": setpoint, "signals": signals,
            "proposal": propose(setpoint, signals)}


def render(result):
    sig = result["signals"]
    if result["setpoint"] is None:
        print("slow loop — no admitted setpoint to move (I-8: the dial is an "
              "admitted record, not a default)")
        print(f"  signals: {sig['ticks_considered']} ticks, phase "
              f"{sig['phase']}, hour leans {sig['lean']}")
        return
    p = result["proposal"]
    print(f"slow loop — the dial and the proposal outcomes make for it")
    print(f"  current setpoint: {canon(p['current'])} (by {result['setpoint']['by']})")
    cr = sig["cool_ratio"]
    cr_text = f"{cr:.2f}" if cr is not None else "n/a"
    print(f"  outcomes folded: {sig['ticks_considered']} recent ticks, "
          f"cooled {sig['cool_count']} (cool_ratio {cr_text})")
    print(f"  outcome phase: {sig['phase']} · leverage {sig['leverage']} · "
          f"hour leans {sig['lean']} ({sig['register']})")
    if p["change"]:
        print(f"  PROPOSED: {canon(p['proposed'])}  (delta {canon(p['deltas'])})")
    else:
        print(f"  PROPOSED: hold — {canon(p['current'])} (no change)")
    for line in p["because"]:
        print(f"    because: {line}")
    print(f"  {p['disposition']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--hour", type=int, default=None,
                    help="hour 0-23 (default: now, read at this edge only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.hour is None:
        from datetime import datetime
        hour = datetime.now().hour
    else:
        hour = args.hour % 24

    result = slowloop(args.root, hour)
    if args.json:
        emit = dict(result)
        if result["setpoint"]:
            emit["setpoint_id"] = result["setpoint"]["id"]
        print(json.dumps(emit, indent=2, sort_keys=True, default=str))
        return 0

    render(result)
    if result["setpoint"] is None:
        print("result: needs-you — admit a setpoint before the slow loop can "
              "propose one (python -m loop.orchestrate --admit-setpoint ... --by bdo)")
        return 2
    p = result["proposal"]
    if p["change"]:
        print("result: report — a setpoint change is proposed (attributed "
              "above); it lands only when the outside admits it. The proposer "
              "never signs its own line.")
    else:
        print("result: done — the slow loop proposes no change; the dial holds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
