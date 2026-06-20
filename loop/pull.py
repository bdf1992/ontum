#!/usr/bin/env python3
"""The terminal-pull gateway (done-line 0123): the piece-scale pull queue,
and the namespace gap it makes visible.

A foreign reviewer of `exports/landing-throughput/` named this the
throughput fix above all others (`atom.landing-throughput-resp-terminal-
pull-gateway.v0`): work the gates judged good should actually reach main,
not accumulate. Verified against the live repo — the epic's discipline
(a PROPOSED finding is checked before it is acted on) — the finding holds
and sharpens.

It sharpens on `loop.merge`. The merge-node's eyes gate land-readiness at
**arc scale**: a whole arc must be confirmed *and* every declared piece
present *and* landed before anything is ready. So `loop.merge` reports
*nothing ready* while receipt-complete pieces sit under arcs that are
merely incomplete — the binding constraint. This gateway is the missing
**piece-scale** sensor: `next_landable_slice` — the ordered, capacity-
bounded queue of pieces that have passed every gate and could be pulled
*now*, without waiting for their unbuilt siblings.

It is read-only, in the grain of `digest`, `merge`, `census`, `gaps`,
`retro`: it counts and names; it never pulls, never writes, never judges.
The actual epic→main pull stays the independent merge-node's hand through
the PR pen, after bdo confirms the arc (D-4). The gateway is the *guard*
the merge-node consults, not a second pen.

No second truth (§10): it **folds the `digest` dataset** for arc and piece
state and **reuses `digest`'s divergences** for the refusal veto, rather
than re-deriving any of it. Inflight comes from the one `sense` fold; the
capacity bound is the admitted `max_inflight_atoms` dial read from the log
(a setpoint is an admitted record, never a code constant — firm invariant).

The §10 teeth, two locally-fine records that refuse to fit:

  - A confirmed arc is bdo's standing pull authority; a gate's refusal
    under it is an honest no. Each is sound alone. Together they refuse to
    fit, so a refusal under the arc **vetoes the whole arc's slice** (the
    merge-node's arc-scale precedence, held at piece scale): the gateway
    never green-lights a pull over a no, even for the refused piece's
    locally-complete siblings. The vetoing piece is named.

  - The honest gap. The reviewer's guard assumed a per-piece pull join
    exists. It does not: every `landed` receipt the merge-node writes keys
    on `(epic, pr, head)` and carries **no atom id/hash**, so the pipeline
    namespace (per-atom, content-hash) and the git-merge namespace (per-PR)
    do not join per piece. The gateway therefore **refuses to claim any
    slice piece reached main** — it surfaces the namespace gap as a named
    finding instead of fabricating the join (that join would be mercury, a
    fact the log does not carry). Making the gap visible is this node's
    first act; closing it is a later piece of the epic.

The module is `loop.pull`, not `loop.gateway`: "gateway" is already loaded
here (the inference egress, done-line 0062, and bdo's gate→gateway→patrol
economy). This organ is *a* gateway in that economy, but the file is named
for its one verb — the terminal pull — so the vocabulary does not overload
(the term-economy's own `overloaded` defect, splitting before it forms).

CLI:
  python -m loop.pull               the landable slice + the namespace gap, read-only
  python -m loop.pull --json        the raw dataset (machine-readable)

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, canon, load_atoms, load_epics,
                            superseded_atom_ids)
from loop.orchestrate import sense
from loop import digest

# A merge-node landing receipt — the git-merge namespace. It keys on
# (epic, pr, head); the atom-join fields the gateway would need to confirm a
# piece reached main are exactly what it never carries.
LANDING_VERDICTS = digest.LANDING_VERDICTS
ATOM_JOIN_FIELDS = ("artifact_id", "artifact_hash", "atom", "atom_id")


def _landed_receipts(fold):
    return [rc for rc in fold.receipts if rc.get("verdict") in LANDING_VERDICTS]


def namespace_gap(fold):
    """The honest finding: landed receipts exist and not one joins to an atom,
    so the gateway cannot confirm a single pull-ready piece reached main. A
    pure structural fold over the receipt stream.

    `joined` is the count of landed receipts carrying any atom-join field; it
    is 0 today and the finding fires whenever it stays 0 under a non-empty
    landed stream. The gateway never papers over it with an epic-level guess
    (a 'landed' receipt's epic does not name *which* piece landed)."""
    landed = _landed_receipts(fold)
    joined = sum(1 for rc in landed
                 if any(rc.get(f) for f in ATOM_JOIN_FIELDS))
    open_gap = bool(landed) and joined == 0
    return {
        "landed_receipts": len(landed),
        "joined_to_atom": joined,
        "open": open_gap,
        "finding": (
            f"{len(landed)} merge `landed` receipt(s) on the log; {joined} "
            "join to an atom. The merge namespace keys on (epic, pr, head), "
            "the pipeline namespace on content-hash — they do not join per "
            "piece, so no slice piece can be confirmed on main. Closing the "
            "join is a later piece of epic.landing-throughput-response."
        ) if open_gap else (
            "no open namespace gap: every landed receipt joins to an atom, "
            "or no landings yet"
        ),
    }


def _vetoed_epics(divergences):
    """Epics whose confirmed arc harbours a refusal — the §10 contradiction
    the digest already detected. The gateway reuses it (no second truth);
    each maps to the piece(s) that caused the veto, for a named reason."""
    veto = {}
    for x in divergences:
        if x.get("kind") == "refusal-under-confirmed-arc":
            veto.setdefault(x["epic"], []).append(x)
    return veto


def next_landable_slice(root):
    """The fold: per confirmed arc, the receipt-complete, non-superseded,
    integrity-intact pieces, ordered and split by the admitted capacity into
    pull-now and queued-behind-capacity. Composes digest + sense; re-derives
    nothing. Returns the dataset render() and --json share."""
    d = digest.digest(root)
    fold = Fold(root)
    atoms = load_atoms(root)
    epics = load_epics(root)
    superseded = superseded_atom_ids({a["id"] for a, _ in atoms})

    setpoint = d["setpoint"]
    capacity = (int(setpoint["value"]["max_inflight_atoms"])
                if setpoint and "max_inflight_atoms" in setpoint.get("value", {})
                else None)
    inflight = sense(fold, atoms, epics)["inflight"]
    headroom = max(0, capacity - inflight) if capacity is not None else None

    veto = _vetoed_epics(d["divergences"])

    landable, held = [], []
    for arc in d["arcs"]:
        if not arc.get("confirmed"):
            continue  # no pull authority — bdo has not confirmed the arc
        epic = arc["epic"]
        complete = [p for p in arc["pieces"]
                    if p.get("landed") and p.get("atom") not in superseded]
        if epic in veto:
            # the refusal vetoes the whole arc's slice (§10): two locally-fine
            # records refuse to fit, and the gateway will not pull over the no.
            reasons = "; ".join(
                f"{x['atom']} → {x['verdict']} ({x.get('reason') or 'no reason'})"
                for x in veto[epic])
            for p in complete:
                held.append({
                    "atom": p["atom"], "epic": epic,
                    "why": f"arc harbours a refusal — {reasons}",
                })
            continue
        for p in complete:
            landable.append({
                "atom": p["atom"], "epic": epic,
                "confirmed_by": arc["confirmed"].get("by"),
                "standing": p.get("standing"),
            })

    landable.sort(key=lambda s: (s["epic"], s["atom"]))
    if headroom is None:
        pull_now, queued = landable, []
    else:
        pull_now, queued = landable[:headroom], landable[headroom:]

    return {
        "setpoint": setpoint,
        "capacity": capacity,
        "inflight": inflight,
        "headroom": headroom,
        "pull_now": pull_now,
        "queued_behind_capacity": queued,
        "held": sorted(held, key=lambda h: (h["epic"], h["atom"])),
        "namespace_gap": namespace_gap(fold),
    }


def render(r):
    lines = ["# Terminal-pull gateway — the landable slice", ""]

    cap = ("unbounded (no setpoint admitted, I-8)" if r["capacity"] is None
           else f"{r['capacity']} max inflight, {r['inflight']} in-flight now "
                f"→ {r['headroom']} headroom")
    lines += [f"_capacity: {cap}_", ""]

    pull, queued, held = r["pull_now"], r["queued_behind_capacity"], r["held"]
    if pull:
        lines.append(f"## Pull now ({len(pull)}) — receipt-complete, within capacity")
        lines += [f"- `{p['atom']}` · `{p['epic']}` "
                  f"(confirmed by {p['confirmed_by']})" for p in pull]
        lines.append("")
    if queued:
        lines.append(f"## Ready, queued behind capacity ({len(queued)})")
        lines += [f"- `{p['atom']}` · `{p['epic']}`" for p in queued]
        lines.append("")
    if held:
        lines.append(f"## Held — refusal under the arc ({len(held)})")
        lines += [f"- `{h['atom']}` · `{h['epic']}` — {h['why']}" for h in held]
        lines.append("")
    if not (pull or queued or held):
        lines += ["_no confirmed arc has a receipt-complete piece to pull._", ""]

    g = r["namespace_gap"]
    mark = "⚠" if g["open"] else "·"
    lines += [f"## {mark} Namespace gap", f"- {g['finding']}", ""]

    lines.append("_read-only: the merge-node pulls confirmed-arc PRs through "
                 "the PR pen (D-4); this gateway only names what is pullable._")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    r = next_landable_slice(args.root)
    if args.json:
        print(canon(r))
    else:
        print(render(r))
        print()

    pull, queued, held = (r["pull_now"], r["queued_behind_capacity"], r["held"])
    if pull or queued or held or r["namespace_gap"]["open"]:
        print(f"result: report — {len(pull)} pullable now, {len(queued)} "
              f"queued, {len(held)} held; the merge-node drains the slice (D-4)")
    else:
        print("result: done — no confirmed-arc piece is pullable; nothing held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
