#!/usr/bin/env python3
"""Impact as settling (done-line 0081): the first pan of the assay.

bdo named the measurement family by metaphor — *a sieve finds gold*. The point
the metaphor carries is the one that makes a measure honest: a pan finds gold
without knowing what gold looks like. It separates by **differential settling**
— heavy sinks, light washes — so you measure by *what survives the wash*, never
by recognising the target. That is the answer to "no gold label": we never teach
a node what impact *is*; we build a medium where weight separates from tailings
by a property we can read.

Risk / Impact / Quality are pans in this rig. This is the first and coarsest —
**Impact**, run in **water** only: re-derivation, the pure fold, nothing
captured. A subject's impact is its **weight in the whole field**
(`loop.field.whole_field`), from two signals already on the log:

  - **evidence-mass** — how many records settle on the subject (the receipts,
    events and admissions the field already cites as its evidence);
  - **reach** — how many distinct arcs the subject spans (the holonic signal:
    one id raised first-class across arcs leans on more of the system).

It **calibrates, never scores absolutely** (bdo: a score is a position between
anchors). Each subject's settled position is taken between the field's own
**floor** and **ceiling** weights — a field with no spread reads *flat*, never a
fabricated number, never a divide. And it separates the pan honestly:

  - **concentrate** — the heavy residue that settled (ranked); what earns the
    finer pans and, eventually, bdo's look (the rig concentrates the river down
    to the one pan worth his stamp — epic.owner-harness made physical);
  - **tailings** — floor-weight subjects, the light stuff that washes through;
  - **unmeasured** — a surfaced gap with no record to weigh: *not* weight-zero.
    You cannot weigh ore that is not in the pan; absence is not lightness;
  - **black sand** — a subject that settled by a *single* signal while the
    other stayed at its floor. Dense junk (magnetite) settles too: the coarse
    water pan cannot tell these from gold, so it names them and points at the
    finer mesh a later, judged pan will be. This is the honest limit of one
    coarse pass, surfaced, never hidden (§10).

The anti-pattern this refuses is mercury: amalgamation captures gold into one
easy number and poisons the watershed — the single confident absolute score.
We do not reach for it.

Scope honesty: this is the *first* pan. Its shape (weight → calibrate → settle)
is a **candidate** for the shared assay schema; the schema is proven only when a
second pan (Risk's blast-radius) shares it. Until then `loop/impact.py` is one
fold, not the rig — the family is named here, not yet built.

Stdlib only, read-only (I-3). CLI ends with a clear result on stdout (D-6):
report — read-only, so never `done`-as-an-act.

CLI:
  python -m loop.impact            the field's settling, heaviest first
  python -m loop.impact --json     the dataset, machine-readable
"""

import argparse
import json
import sys
from pathlib import Path

from loop.field import _is_surfaced_gap, whole_field
from loop.reconcile import DEFAULT_ROOT

WATER = "re-derivation"  # the only medium this pan uses — a pure fold, nothing captured


def weigh(whole):
    """Aggregate every subject's raw density signals across the whole field.
    A subject is named once per appearance; its evidence-mass is the union of
    the record ids the field cites for it, its reach the set of arcs it spans.
    `gap` is true if any appearance was a surfaced gap (an honest absence)."""
    sig = {}

    def note(subject, arc, item):
        if not subject:
            return
        s = sig.setdefault(subject, {"evidence": set(), "arcs": set(),
                                     "gap": False})
        s["evidence"].update(item.get("evidence", []))
        if arc:
            s["arcs"].add(arc)
        if _is_surfaced_gap(item):
            s["gap"] = True

    # the agenda rung names the arcs themselves; each arc is a subject too.
    for it in whole.get("agenda", []):
        note(it.get("subject"), it.get("subject"), it)
    for eid, ladder in whole.get("arcs", {}).items():
        if ladder is None:
            continue
        for rung in ladder["rungs"]:
            for it in rung["items"]:
                note(it.get("subject"), eid, it)
    return sig


def _weighable(subject, s):
    """In the pan or not. A subject with any record settled on it is weighable
    (even a parked atom is real material). A surfaced gap with *no* evidence is
    a hole — unmeasured, never light: you cannot weigh what is not there."""
    return bool(s["evidence"]) or not s["gap"]


def settle(whole):
    """Weigh, calibrate against the field's own floor and ceiling, and separate
    the pan: concentrate / tailings / black sand / unmeasured. Pure over the
    field. `settled` is None for every subject when the field has no spread
    (a flat field cannot calibrate a position — no divide, no fake number)."""
    sig = weigh(whole)

    rows, unmeasured = [], []
    for subject, s in sorted(sig.items()):
        ev, reach = len(s["evidence"]), len(s["arcs"])
        if not _weighable(subject, s):
            unmeasured.append({"subject": subject, "why": "a surfaced gap with "
                               "no record to weigh — not in the pan"})
            continue
        rows.append({"subject": subject, "evidence_mass": ev, "reach": reach,
                     "weight": ev + reach})

    weights = [r["weight"] for r in rows]
    floor = min(weights) if weights else None
    ceiling = max(weights) if weights else None
    spread = (ceiling - floor) if weights else 0
    floor_ev = min((r["evidence_mass"] for r in rows), default=0)
    floor_reach = min((r["reach"] for r in rows), default=0)

    for r in rows:
        # the calibrated position between the field's own anchors. A flat field
        # (spread 0) cannot place a subject between equal anchors — None, not 0.
        r["settled"] = ((r["weight"] - floor) / spread) if spread else None
        # black sand: settled (above the floor) by a SINGLE signal — the other
        # stayed at its own floor. Relative, not a magic constant.
        above_ev = r["evidence_mass"] > floor_ev
        above_reach = r["reach"] > floor_reach
        r["settles"] = r["weight"] > floor
        r["black_sand"] = r["settles"] and (above_ev ^ above_reach)

    rows.sort(key=lambda r: (-r["weight"], r["subject"]))
    concentrate = [r for r in rows if r["settles"]]
    tailings = [r for r in rows if not r["settles"]]
    black_sand = [r for r in rows if r["black_sand"]]
    return {
        "medium": WATER,
        "weighed": len(rows),
        "floor": floor, "ceiling": ceiling,
        "flat": bool(rows) and spread == 0,
        "rows": rows,
        "concentrate": concentrate,
        "tailings": tailings,
        "black_sand": black_sand,
        "unmeasured": unmeasured,
    }


def impact(root=None):
    """The full read: fold the whole field, then pan it. Read-only."""
    root = Path(root) if root is not None else Path(DEFAULT_ROOT)
    return settle(whole_field(root))


# --- render -----------------------------------------------------------------

def _pos(settled):
    return "—" if settled is None else f".{int(round(settled * 100)):02d}"


def render(result):
    print("impact — the field's settling (the first assay pan; "
          f"medium: {result['medium']}, nothing captured)")
    if not result["weighed"]:
        print("  the pan is empty — no weighable subject in the field "
              "(absence, not a zero)")
        if result["unmeasured"]:
            print(f"  ({len(result['unmeasured'])} unmeasured gap(s) — holes, "
                  "not light material)")
        return
    span = (f"flat (no spread — positions uncalibrated)" if result["flat"]
            else f"floor {result['floor']} .. ceiling {result['ceiling']}")
    print(f"  weighed {result['weighed']} subject(s) in water · {span}")

    print("  concentrate (heaviest settles first):")
    for r in result["concentrate"][:12]:
        tag = " · black sand" if r["black_sand"] else ""
        print(f"    {r['subject']} — weight {r['weight']} (settled "
              f"{_pos(r['settled'])}) · {r['evidence_mass']} evidence, "
              f"{r['reach']} reach{tag}")
    if len(result["concentrate"]) > 12:
        print(f"    … (+{len(result['concentrate']) - 12} more settled)")

    if result["black_sand"]:
        print("  black sand (settled by a single liquid — the coarse pan "
              "cannot tell these from gold; a finer mesh is the discriminator):")
        for r in result["black_sand"][:8]:
            by = "evidence" if r["evidence_mass"] > r["reach"] else "reach"
            print(f"    {r['subject']} — heavy in {by} only "
                  f"({r['evidence_mass']} evidence, {r['reach']} reach)")

    if result["tailings"]:
        names = ", ".join(r["subject"] for r in result["tailings"][:6])
        more = (f" (+{len(result['tailings']) - 6})"
                if len(result["tailings"]) > 6 else "")
        print(f"  tailings (washed through — floor weight {result['floor']}): "
              f"{len(result['tailings'])} — {names}{more}")
    if result["unmeasured"]:
        print(f"  unmeasured (not in the pan — a surfaced gap with no record "
              f"to weigh): {len(result['unmeasured'])}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT),
                    help="records root (default: .ai-native)")
    ap.add_argument("--json", action="store_true", help="emit the dataset")
    args = ap.parse_args(argv)

    result = impact(root=args.root)
    if args.json:
        emit = dict(result)
        # sets are already counted into ints; rows carry plain numbers
        print(json.dumps(emit, indent=2, sort_keys=True))
        return 0

    render(result)
    if not result["weighed"]:
        print("result: report — the field weighs nothing yet; the pan reads "
              "what is there (water only), and there is no material to settle")
        return 0
    top = result["concentrate"][0]["subject"] if result["concentrate"] else "—"
    bs = len(result["black_sand"])
    note = (f"; {bs} black-sand flagged (the coarse mesh's honest limit — a "
            "finer, judged pan is the next mesh)" if bs else "")
    print(f"result: report — {result['weighed']} subject(s) weighed in water, "
          f"heaviest settler {top}{note}. Read-only; the cut stays bdo's (D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
