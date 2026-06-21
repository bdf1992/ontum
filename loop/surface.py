#!/usr/bin/env python3
"""loop/surface.py — the active-surface control plane (CTA-1).

bdo, 2026-06-21 (chat): *"you're handed a rendered surface, not a control plane
— I don't want prerendering"* and *"a safe default so you don't have to fiddle
every time."*

A mortal session blinks in and is handed the SessionStart dump — a PRERENDER: a
view someone computed, froze to text, and pushed. It is dead on arrival; a
session cannot ask it the question it did not anticipate, and cannot steer it.
This is the opposite: a LIVE plane, folded fresh on every call (the non-prerender
invariant — `tests/test_surface.py` fails if it ever serves a stale answer),
opinionated by a SAFE DEFAULT LENS so a bare touch just works, the knobs there
for when you steer.

It COMPOSES the folds that already measure each channel — no second truth (§10):
`digest()` for the per-arc cells and the field's behaviour, `gaps()` for the
parked pieces and the single top gap, the setpoint read for the dial in play. It
re-derives nothing.

The plane is split the way ontum already splits one dial (orchestrate's setpoint,
proposed by slowloop, disposed in bdo's fence) — only here over the WHOLE active
surface:

  data plane     the log (truth). Untouched.
  control plane  THIS — the live measure (cells + vitals) and, later, the knobs.
  rendered       the SessionStart dump, a digest snapshot — views PULLED from the
                 plane, never the pushed flood.

CTA-1 (here): the queried-live plane + the safe default lens, read-only. Later:
the admitted `control_map` governance dial (CTA-2), the non-prerender tooth +
repointing the SessionStart dump (CTA-3), the propose-a-dial loop on the disposer
fence (CTA-4). See `.ai-native/proposals/active-surface-control-plane.proposal.md`.

Read-only — a fold, like digest/gaps/census. Stdlib only, writes nothing, ends
with `done | report | needs-you`.

Named hole (not ghosted): v0 measures the LOG-side active surface. The live
GitHub PR/issue counts come from the standing summon hook, not a log fold; that
channel joins when the git/gh gateway makes them a folded fact (the PRs cell).
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, load_atoms, load_epics)
from loop.orchestrate import read_setpoint, sense
from loop.digest import digest
from loop import gaps


# ---------------------------------------------------------------- the safe lens
# default-safe-WHEN-UNSET (the setpoints law): a bare call answers with this. An
# admitted `control_map` dial moves it (CTA-2); never a hardcoded constant past
# this fallback. The session may override the dimension per-query (ephemeral, no
# admission) — the operating knob, distinct from the governance dial.

DEFAULT_LENS = {
    "dimension": "arc",        # how: condense the flood by arc (digest/brief's unit)
    "weights": {"confirmed-moving": 3, "awaiting-stamp": 2, "idle": 1},
    # surfacing: a cell calls for a read only at a stamp or a refusal — quiet
    # otherwise (so the map is silent when the surface is silent).
}
DIMENSIONS = ("arc",)  # v0; "flat"/"blast-radius" are later lenses (named, not faked)


def lens(admissions, dimension=None):
    """The active lens. default-safe-when-unset; the per-query `dimension` is the
    session's ephemeral override (no admission written). The admitted governance
    dial is CTA-2 — until then this is the safe default, verbatim."""
    out = dict(DEFAULT_LENS)
    if dimension:
        out["dimension"] = dimension
    return out


# ------------------------------------------------------------------- the measure
# one cell == one channel of in-flight state, measured the same way. The arc
# cells come straight off digest's arc grouping — the counts ARE digest's, never
# recomputed (no second truth).

def _weight_class(cell):
    if cell["confirmed"] and (cell["awaiting"] or cell["parked"] or cell["landed"]):
        return "confirmed-moving"
    if not cell["confirmed"] and cell["awaiting"]:
        return "awaiting-stamp"
    return "idle"


def _needs_read(cell):
    """The default surfacing lens: a gate refused (refused/parked) OR the arc
    waits at an unconfirmed stamp. An idle or confirmed-and-quiet arc stays
    ambient."""
    return bool(cell["refused"] or cell["parked"]
                or (cell["awaiting"] and not cell["confirmed"]))


def _arc_cell(arc, weights):
    cell = {
        "subject": arc["epic"],
        "arc": arc.get("arc"),
        "confirmed": bool(arc.get("confirmed")),
        "landed": arc.get("landed", 0),
        "awaiting": arc.get("awaiting", 0),
        "parked": arc.get("parked", 0),
        "refused": arc.get("refused", 0),
    }
    cell["weight_class"] = _weight_class(cell)
    cell["weight"] = weights[cell["weight_class"]]
    cell["needs_read"] = _needs_read(cell)
    # the cell's heat: how much in-flight pressure it carries right now
    cell["heat"] = cell["awaiting"] + cell["parked"] + cell["refused"]
    return cell


def plane(root=DEFAULT_ROOT, dimension=None):
    """The control plane, folded fresh. Returns the dataset; render() turns it
    into prose and --json emits it verbatim."""
    root = Path(root)
    fold = Fold(root)
    atoms = load_atoms(root)
    epics = load_epics(root)
    the_lens = lens(fold.admissions, dimension)

    d = digest(root)  # composes — arcs, field behaviour, setpoint
    weights = the_lens["weights"]

    cells, quiet_arcs = [], 0
    for arc in d["arcs"]:
        present = arc["landed"] + arc["awaiting"] + arc["parked"] + arc["refused"]
        if present or arc.get("confirmed"):
            cells.append(_arc_cell(arc, weights))
        else:
            quiet_arcs += 1  # an empty, unconfirmed arc folds into the tail, not a cell
    # cells that want a read lead; then by weight, then heat, then name
    cells.sort(key=lambda c: (not c["needs_read"], -c["weight"], -c["heat"], c["subject"]))

    # the vitals — plane-level, not per-cell
    pressure = sense(fold, atoms, epics)
    top = gaps.top_gap(root)
    setpoint = read_setpoint(fold.admissions)

    # the ambient tail — the noisy channels folded to counts, one line (knob to
    # unmute later). Bucketed straight off the gap fold; no re-derivation.
    found = gaps.gaps(root)
    ambient = {}
    for g in found:
        ambient[g["kind"]] = ambient.get(g["kind"], 0) + 1
    if quiet_arcs:
        ambient["quiet-arcs"] = quiet_arcs

    return {
        "lens": the_lens,
        "cells": cells,
        "vitals": {
            "field": pressure,
            "setpoint": (setpoint or {}).get("value"),
            "top_gap": ({"kind": top["kind"], "subject": top["subject"],
                         "move": top.get("move")} if top else None),
        },
        "ambient": ambient,
    }


# ------------------------------------------------------------------- the surface
def render(data):
    lines = []
    lens_ = data["lens"]
    lines.append(f"the active surface — by {lens_['dimension']} (live fold)")
    lines.append("")

    need = [c for c in data["cells"] if c["needs_read"]]
    quiet = [c for c in data["cells"] if not c["needs_read"]]

    if need:
        lines.append("needs a read:")
        for c in need:
            mark = "confirmed" if c["confirmed"] else "UNCONFIRMED"
            lines.append(f"  • {c['subject']} [{mark}] — "
                         f"awaiting {c['awaiting']} · parked {c['parked']} · "
                         f"refused {c['refused']} · landed {c['landed']}")
    else:
        lines.append("needs a read: nothing — the surface is quiet")

    if quiet:
        names = ", ".join(c["subject"] for c in quiet)
        lines.append("")
        lines.append(f"moving, no read needed ({len(quiet)}): {names}")

    v = data["vitals"]
    f = v["field"]
    lines.append("")
    lines.append(f"vitals: inflight {f['inflight']} · awaiting {f['awaiting']} · "
                 f"parked {f['parked']} · backlog {f['human_backlog']}"
                 + (f" · setpoint {json.dumps(v['setpoint'])}" if v["setpoint"] else ""))
    if v["top_gap"]:
        lines.append(f"  top gap: {v['top_gap']['kind']} — {v['top_gap']['subject']}")
    if data["ambient"]:
        tail = " · ".join(f"{k} {n}" for k, n in sorted(data["ambient"].items()))
        lines.append(f"  ambient: {tail}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="the active-surface control plane "
                                             "(live fold, read-only)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--dimension", help="ephemeral per-query lens override "
                    f"(one of {DIMENSIONS}); no admission written")
    ap.add_argument("--json", action="store_true", help="the raw dataset")
    args = ap.parse_args(argv)

    if args.dimension and args.dimension not in DIMENSIONS:
        print(f"result: needs-you — dimension {args.dimension!r} is a later lens "
              f"(v0 has {DIMENSIONS}); it is named, not faked")
        return 2

    data = plane(args.root, dimension=args.dimension)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render(data))
    print("result: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
