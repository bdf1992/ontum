#!/usr/bin/env python3
"""The merge-node's eyes (done-line 0033): a read-only land-readiness
sensor, per arc.

The digest (done-line 0032) gave bdo eyes on the whole field; this gives
the *merge-node* its eyes on a single arc — the judgement "is this arc safe
to land on main?" It is the first sensor of a new kind of meaning (report
0004 §3): land-safety. Eyes before the hand.

It decides; it never acts. It merges nothing and writes nothing — the
actual epic→main land is the separate, hard-gated PR pen the independent
merge-node runs after bdo confirms the arc (D-4). This module reuses the
digest fold rather than re-deriving state: the merge-node and the owner
watch the same log, one for a verdict, one for a glance.

The verdict per confirmed arc:
  ready_to_land  confirmed by bdo, every declared piece present and landed,
                 no divergence touching it.
  refuse         a divergence touches it — most sharply, a confirmed arc
                 harbouring a *refused* piece (§10): "all pieces present"
                 and "a gate said no" are each locally fine, and they refuse
                 to fit. The sensor must never green-light over that no, even
                 if the piece's atom now reads landed.
  not_ready      unconfirmed, or a piece is still unbuilt or unlanded — the
                 normal "in progress", not a fault.

CLI:
  python -m loop.merge          land-readiness across the arcs, read-only

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT
from loop import digest

READY, REFUSE, NOT_READY = "ready_to_land", "refuse", "not_ready"


def assess(arc, divergences):
    """One arc's land-readiness, folded from its digest entry. Pure — the
    order is the safety order: an unconfirmed arc is never assessed for
    faults (nothing to land), but a confirmed one is vetoed by a refusal
    before any 'still in progress' reading, so a landed-but-refused arc
    reads refuse, never ready_to_land."""
    epic = arc["epic"]
    refused = [d for d in divergences
               if d.get("kind") == "refusal-under-confirmed-arc"
               and d.get("epic") == epic]

    if not arc.get("confirmed"):
        return {"epic": epic, "verdict": NOT_READY,
                "reasons": [f"arc not confirmed by bdo "
                            f"(loop.node confirm-arc --epic {epic} --by bdo)"]}
    if refused:
        return {"epic": epic, "verdict": REFUSE,
                "reasons": [f"{d['atom']}: {d['node']} → {d['verdict']} "
                            f"({d.get('reason') or 'no reason'})" for d in refused]}

    unbuilt = [p["atom"] for p in arc["pieces"] if not p.get("present")]
    unlanded = [p["atom"] for p in arc["pieces"]
                if p.get("present") and not p.get("landed")]
    if unbuilt or unlanded:
        reasons = []
        if unbuilt:
            reasons.append(f"unbuilt: {', '.join(unbuilt)}")
        if unlanded:
            reasons.append(f"not yet landed: {', '.join(unlanded)}")
        return {"epic": epic, "verdict": NOT_READY, "reasons": reasons}

    return {"epic": epic, "verdict": READY,
            "reasons": [f"confirmed by {arc['confirmed'].get('by')}, "
                        f"{arc['landed']} piece(s) landed, no divergence"]}


def readiness(root, since=None, until=None):
    """The fold: digest the log, then assess each arc for land-safety. A
    field cap-breach is surfaced as a global caution, not a per-arc veto —
    past queue heat is field health, not this arc's fault."""
    d = digest.digest(root, since=since, until=until)
    arcs = [assess(arc, d["divergences"]) for arc in d["arcs"]]
    cautions = [x for x in d["divergences"] if x.get("kind") == "queue-over-cap"]
    return {"arcs": arcs, "cautions": cautions}


def render(r):
    lines = ["# Land-readiness", ""]
    order = {READY: 0, REFUSE: 1, NOT_READY: 2}
    glyph = {READY: "✓ ready to land", REFUSE: "✗ refuse",
             NOT_READY: "· not ready"}
    for a in sorted(r["arcs"], key=lambda a: (order.get(a["verdict"], 9), a["epic"])):
        lines.append(f"## {a['epic']} — {glyph.get(a['verdict'], a['verdict'])}")
        for why in a["reasons"]:
            lines.append(f"  - {why}")
    if r["cautions"]:
        lines.append("")
        lines.append(f"_field caution: {len(r['cautions'])} tick(s) breached "
                     "the human-queue cap — the field ran hot (loop.orchestrate)_")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = ap.parse_args(argv)

    r = readiness(args.root)
    print(render(r))
    print()
    ready = [a for a in r["arcs"] if a["verdict"] == READY]
    refused = [a for a in r["arcs"] if a["verdict"] == REFUSE]
    if ready or refused:
        print(f"result: report — {len(ready)} arc(s) ready to land, "
              f"{len(refused)} refused; bdo confirms arcs and the independent "
              "merge-node lands confirmed PRs through pr.py land (D-4)")
    else:
        print("result: report — no arc ready to land yet "
              "(none confirmed-and-complete); read-only, nothing acted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
