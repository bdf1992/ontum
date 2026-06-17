#!/usr/bin/env python3
"""The temporal-pressure fold (done-line 0071): ambient time modulates the
quality and type of pressure — the pressure at 8am is not the pressure at 8pm.

bdo's direction (2026-06-14): the same gap should not read the same at dawn and
at dusk; the hour is itself a pressure signal. This is the ambient-time *read*
for the doctrine's slow loop (§14: run hot to explore, cool to consolidate) —
not yet the write-back into the dial, but the signal that write-back will use.

The shape mirrors `loop/pressure.py` and the rest of the loop's grain: a pure
fold, stdlib only, read-only (I-3). The one discipline time forces — and the
reason a clock-reading fold would be untestable — is that **the wall clock is
read only at the CLI edge, never inside the fold**. Every function here takes
the moment as an explicit input (an hour), so a fixed moment yields a fixed
result and a test can drive any hour it likes (the harness's own Date.now()
ban, applied to ontum).

What time changes, and what it must never change:

  - it changes **emphasis** — the lean (heat / steady / cool), which unmet
    probe is the temporal *focus*, and how the next move is phrased;
  - it must **never** change **truth** — whether a probe is met / partial /
    unmet is a fact about committed evidence, not about the hour. `modulate`
    re-orders and re-frames; it does not touch pressure's met/unmet sets.

The band schedule (hour-of-day -> register) follows the governance grain:
a default tiles the 24h in code, and an admitted `temporal_schedule` record
overrides it (setpoints are admitted, never baked — the same rule as the
orchestrator's dial). A malformed schedule — a gap or an overlap across the
24h — is refused: a schedule that does not tile the day cannot classify it.

CLI:
  python -m loop.temporal              the current register + modulated pressure
  python -m loop.temporal --hour 8     a fixed moment (deterministic, for any hour)
  python -m loop.temporal --json       the dataset, machine-readable
"""

import argparse
import json
import sys
from pathlib import Path

from loop.pressure import DEFAULT_PROBES, pressure
from loop.reconcile import DEFAULT_ROOT, Fold

REPO = Path(__file__).resolve().parent.parent

# The default band schedule: tiles [0, 24) with no gap and no overlap. Each
# band carries a register (the name of the moment), a lean (the heat/cool
# disposition, §14), and a quality (what kind of work the hour favours). Night
# is split into two bands so the schedule stays a simple linear tiling.
DEFAULT_SCHEDULE = [
    {"start": 0,  "end": 5,  "register": "night-defer",
     "lean": "cool",   "quality": "low — defer big starts; close or rest"},
    {"start": 5,  "end": 12, "register": "dawn-explore",
     "lean": "heat",   "quality": "exploratory — take the large-leverage unblocker"},
    {"start": 12, "end": 17, "register": "midday-build",
     "lean": "steady", "quality": "steady build — hold the line, ship the piece"},
    {"start": 17, "end": 22, "register": "dusk-consolidate",
     "lean": "cool",   "quality": "consolidating — close what is nearest done"},
    {"start": 22, "end": 24, "register": "night-defer",
     "lean": "cool",   "quality": "low — defer big starts; close or rest"},
]

LEANS = ("heat", "steady", "cool")


# --- the schedule (desired tiling of the day, with refusal) -----------------

def validate_schedule(bands):
    """Return a list of problems; empty means the schedule tiles [0,24)
    cleanly. A gap or an overlap is the teeth: a schedule that does not cover
    the day cannot classify a moment in it."""
    problems = []
    if not bands:
        return ["empty schedule — nothing to classify a moment into"]
    for b in bands:
        for key in ("start", "end", "register", "lean"):
            if key not in b:
                problems.append(f"band missing '{key}': {b}")
        if "lean" in b and b["lean"] not in LEANS:
            problems.append(f"band lean must be one of {LEANS}: {b.get('lean')}")
        s, e = b.get("start"), b.get("end")
        if not (isinstance(s, (int, float)) and isinstance(e, (int, float))):
            problems.append(f"band start/end must be numbers: {b}")
        elif not (0 <= s < e <= 24):
            problems.append(f"band must satisfy 0<=start<end<=24: {b}")
    if problems:
        return problems
    ordered = sorted(bands, key=lambda b: b["start"])
    cursor = 0
    for b in ordered:
        if b["start"] > cursor:
            problems.append(f"gap in coverage: hour {cursor} to {b['start']} "
                            "belongs to no band")
        elif b["start"] < cursor:
            problems.append(f"overlap: band starting {b['start']} overlaps "
                            f"coverage already at hour {cursor}")
        cursor = max(cursor, b["end"])
    if cursor != 24:
        problems.append(f"coverage ends at hour {cursor}, not 24 — the day is "
                        "not fully tiled")
    return problems


def load_schedule(root):
    """The default schedule, overridden by the latest admitted
    `temporal_schedule` record. An admitted schedule that does not validate is
    refused (returned as problems) — never silently dropped. Returns
    (schedule, source, problems)."""
    log = Path(root) / "log"
    if log.is_dir():
        fold = Fold(Path(root))
        admitted = [a for a in fold.admissions if a.get("type") == "temporal_schedule"]
        if admitted:
            bands = admitted[-1].get("bands", [])
            problems = validate_schedule(bands)
            if problems:
                return DEFAULT_SCHEDULE, "default (admitted schedule refused)", problems
            return bands, f"admitted ({admitted[-1].get('id', 'temporal_schedule')})", []
    return DEFAULT_SCHEDULE, "default", []


# --- classification (pure given the moment) ---------------------------------

def register_at(hour, schedule):
    """The band a moment falls in. `hour` is the explicit moment — read from
    the wall clock only by the caller at the edge, never here."""
    h = hour % 24
    for b in schedule:
        if b["start"] <= h < b["end"]:
            return b
    # a validated schedule tiles [0,24); this is unreachable for a clean one,
    # but absence is information, not a guess.
    return None


# --- modulation (emphasis changes; truth does not) --------------------------

def _notmet_cap(pressure_result):
    """The not-met capability probes — the buildable surface temporal pressure
    re-orders. Mirrors pressure's own leverage candidates."""
    by_id = pressure_result["by_id"]
    state = pressure_result["state"]
    return [pid for pid, p in by_id.items()
            if p.get("class") == "cap" and state[pid] in ("unmet", "partial")]


def _leverage(pid, pressure_result):
    """How many not-met cap probes transitively depend on this one — the
    pressure fold's own leverage measure, recomputed for ordering."""
    from loop.pressure import _transitive_deps
    by_id = pressure_result["by_id"]
    cands = set(_notmet_cap(pressure_result))
    return sum(1 for other in cands
               if other != pid and pid in _transitive_deps(other, by_id))


def _unmet_deps(pid, pressure_result):
    by_id = pressure_result["by_id"]
    met = set(pressure_result["met"])
    return sum(1 for d in by_id[pid].get("depends", []) if d not in met)


def modulate(pressure_result, band):
    """Re-emphasise the same pressure by the hour's lean. Returns a temporal
    view — order, focus, lean, re-framed next move — and **never** mutates the
    pressure result's truth (met/partial/unmet/dormant are untouched).

      heat / steady : favour the large-leverage unblocker (explore, build big)
      cool          : favour the nearest-closeable leaf (consolidate, finish)
    """
    lean = band["lean"]
    cands = _notmet_cap(pressure_result)

    if lean == "cool":
        # nearest done and actually closeable: fewest unmet deps first, then
        # partials (closest), then the leaves (low leverage), then id.
        order = sorted(cands, key=lambda p: (
            _unmet_deps(p, pressure_result),
            0 if pressure_result["state"][p] == "partial" else 1,
            _leverage(p, pressure_result),
            p))
        why = ("the hour leans cool — close what is nearest done rather than "
               "opening the big front")
    else:  # heat | steady
        # the big unblocker: most dependents first, then most-ready, then the
        # rawer gap (a wholly unmet probe before a partial — heat explores the
        # untouched front, mirroring pressure's own top-leverage tiebreak), then
        # id. The unmet-before-partial term is what keeps heat and cool distinct
        # once the leverage gradient flattens.
        order = sorted(cands, key=lambda p: (
            -_leverage(p, pressure_result),
            _unmet_deps(p, pressure_result),
            0 if pressure_result["state"][p] == "unmet" else 1,
            p))
        why = ("the hour leans hot — take the large-leverage unblocker while "
               "there is room to explore" if lean == "heat"
               else "steady hour — hold the line on the highest-leverage piece")

    focus = order[0] if order else None
    base_move = (pressure_result["by_id"][focus].get("move", "") if focus
                 else pressure_result["next_move"])
    next_move = (f"[{lean} · {band['register']}] {why}: "
                 f"{focus + ' — ' if focus else ''}{base_move}")

    return {
        "register": band["register"],
        "lean": lean,
        "quality": band["quality"],
        "focus": focus,
        "focus_why": why,
        "order": order,
        "next_move": next_move,
    }


# --- the full read ----------------------------------------------------------

def temporal(hour, probes_path=DEFAULT_PROBES, repo=REPO, root=None):
    """Classify the moment and modulate the outcome-pressure fold by it. Pure
    given `hour`."""
    root = root if root is not None else (repo / DEFAULT_ROOT)
    schedule, source, problems = load_schedule(root)
    band = register_at(hour, schedule)
    pr = pressure(probes_path, repo=repo, root=root)
    view = modulate(pr, band) if band else None
    return {
        "hour": hour,
        "schedule_source": source,
        "schedule_problems": problems,
        "band": band,
        "temporal": view,
        "pressure": pr,
    }


# --- render -----------------------------------------------------------------

def render(result):
    pr = result["pressure"]
    band = result["band"]
    print(f"temporal pressure — hour {result['hour']:02d}:00 "
          f"(schedule: {result['schedule_source']})")
    if result["schedule_problems"]:
        print("  admitted schedule REFUSED (using default):")
        for p in result["schedule_problems"]:
            print(f"    - {p}")
    if not band:
        print("  no band covers this hour — schedule does not tile the day")
        return
    v = result["temporal"]
    print(f"  register: {v['register']} · lean: {v['lean']} — {v['quality']}")
    print(f"  outcome: {pr['outcome']}")
    print(f"  phase: {pr['phase']} · leverage top: "
          f"{pr['top_leverage']['id'] if pr['top_leverage'] else '—'} · "
          f"temporal focus: {v['focus'] or '—'}")
    print(f"  next move: {v['next_move']}")
    if v["order"]:
        print("  temporal order (same probes, re-emphasised by the hour):")
        for pid in v["order"]:
            mark = pr["state"][pid]
            print(f"    [{mark}] {pid} — {pr['by_id'][pid].get('statement', pid)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hour", type=int, default=None,
                    help="hour of day 0-23 (default: now, read at this edge only)")
    ap.add_argument("--probes", type=Path, default=DEFAULT_PROBES)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.hour is None:
        # the one place the wall clock is read — the edge, never the fold.
        from datetime import datetime
        hour = datetime.now().hour
    else:
        hour = args.hour % 24

    result = temporal(hour, args.probes, root=args.root)
    if args.json:
        emit = dict(result)
        emit["pressure"] = {k: v for k, v in result["pressure"].items()
                            if k != "by_id"}
        print(json.dumps(emit, indent=2, sort_keys=True))
        return 0

    render(result)
    if result["schedule_problems"]:
        print("result: report — admitted temporal schedule refused as "
              "malformed; the default tiled the day instead")
    elif result["temporal"] and result["temporal"]["focus"]:
        print(f"result: report — the hour leans {result['temporal']['lean']}; "
              f"the temporal focus is the work, the truth is unchanged")
    else:
        print("result: done — no unresolved capability work to emphasise")
    return 0


if __name__ == "__main__":
    sys.exit(main())
