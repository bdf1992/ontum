#!/usr/bin/env python3
"""The placement gate's deterministic backing — the second *kind* of real gate.

First light (done-line 0040) made the value gate real by launching a mortal
mind: inference, "is this the owner's value?". The placement gate's question
is not judgment — it is *law*. Two atoms either can occupy the same address
or they cannot; no mind is needed to decide it, and a mind would only add
noise. So this gate is real the deterministic way: a pure fold over the
atom field that *computes* its verdict from structure (epic.experience-layer
horizon: "real gates — deterministic where the question is law, inference
where it is judgment").

The law, in one sentence: an atom under judgment **refuses to fit** when an
address it `touches` overlaps an address a sibling atom touches *and* one of
the two declared the other off-limits in `incidence.must_not_collide_with`.
That declaration is the intent; the touch-overlap is the fact; together they
are a `collision`. Absent either, the placement is `sound`.

This is the §10 case the doctrine asks for (D-10, §10): two atoms each
locally fine — each places cleanly *alone* — that refuse to fit *together*,
and the gate notices. A gate whose verdict could not have been its opposite
did not gate; this one's opposite is one `must_not_collide_with` entry away.

Pure stdlib, no git, no subprocess, no mind (the fold is data — the hard
rule). The verdict reaches the log only through the one pen
(`loop.node judge`, D-4); this module never writes a receipt itself. The law
it applies is versioned source — `.ai-native/nodes/placement-gate.det.v1.md`
— hashed onto the receipt as `prompt_hash` (§7), exactly as the inference
gate's prompt is, so every deterministic verdict is attributable to the
exact law that produced it.

Usage:
  python -m loop.placement_gate --atom <id>                 # read-only: the verdict, no write
  python -m loop.placement_gate judge --atom <id> --node <node-id> --by <who>
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import load_atoms
from loop.node import judge as land_verdict

DEFAULT_ROOT = Path(".ai-native")

# This stage's node in the pipeline, and the seam's terminal verdict set —
# both read from the single PIPELINE table, never re-declared here.
STAGE_NODE = "placement-gate.mock.v0"


def _addresses(atom, key):
    """An atom's address set for one incidence key — the addresses it touches,
    or the siblings it declares off-limits. Tolerant of a missing/None field
    (an atom that declares nothing collides with nothing)."""
    return set((atom.get("incidence", {}) or {}).get(key, []) or [])


def collisions_for(atom, field):
    """Every sibling `atom` refuses to fit, as (sibling_id, shared_addresses,
    who_declared). The law: touched-address overlap AND a mutual-exclusion
    declaration in either direction. Pure over the field; order-stable.

    A sibling is any *other* atom in the field — identity is the atom id, so
    a re-judged atom never collides with its own earlier self."""
    u_id = atom["id"]
    u_touch = _addresses(atom, "touches")
    u_forbid = _addresses(atom, "must_not_collide_with")
    out = []
    for other in field:
        o_id = other.get("id")
        if o_id == u_id:
            continue
        overlap = u_touch & _addresses(other, "touches")
        if not overlap:
            continue
        u_forbids = o_id in u_forbid
        o_forbids = u_id in _addresses(other, "must_not_collide_with")
        if u_forbids or o_forbids:
            out.append((o_id, sorted(overlap),
                        "it declares the sibling off-limits" if u_forbids
                        else "the sibling declares it off-limits"))
    return out


def placement_verdict(atom, field):
    """The deterministic verdict: (`collision` | `sound`, reason). The reason
    is the receipt's payload — it names the sibling and the shared address, so
    a cold reader sees *why* it refused, not just *that* it did."""
    cols = collisions_for(atom, field)
    if cols:
        parts = [f"{sib} over [{', '.join(addr)}] ({why})"
                 for sib, addr, why in cols]
        return ("collision",
                f"{atom['id']} refuses to fit {len(cols)} sibling(s): "
                + "; ".join(parts)
                + ". A touched address overlaps a sibling under a "
                  "must_not_collide_with declaration — the two cannot share "
                  "this placement.")
    touched = sorted(_addresses(atom, "touches"))
    return ("sound",
            f"{atom['id']} places cleanly: none of its touched address(es) "
            + (f"({', '.join(touched)}) " if touched else "")
            + "overlap a sibling it (or that sibling) declared off-limits.")


def _load_field(root):
    return [a for a, _ in load_atoms(root)]


def verdict_for(root, atom_id):
    """Resolve one atom against the field and return its verdict, or raise
    LookupError if the atom is not on disk."""
    field = _load_field(root)
    target = next((a for a in field if a["id"] == atom_id), None)
    if target is None:
        raise LookupError(atom_id)
    return placement_verdict(target, field)


# ----------------------------------------------------------------- runtime

def cmd_show(ns):
    """Read-only: compute and print the verdict without touching the log. The
    honest preview — what the gate *would* land, runnable before bdo admits
    the stage real (until then `judge` itself is refused by the seam)."""
    try:
        verdict, reason = verdict_for(ns.root, ns.atom)
    except LookupError:
        print(f"result: needs-you — atom {ns.atom} not found in {ns.root / 'atoms'}")
        return 2
    print(f"{ns.atom}: {verdict}")
    print(f"  {reason}")
    print(f"result: report — deterministic placement verdict for {ns.atom} is "
          f"{verdict!r} (read-only; land it through loop.node judge)")
    return 0


def cmd_judge(ns):
    """Compute the verdict and land it through the one pen (D-4). The pen
    enforces the seam: if `placement-gate.mock.v0` is not yet admitted real,
    `judge` refuses — this module never stands in for that stamp."""
    try:
        verdict, reason = verdict_for(ns.root, ns.atom)
    except LookupError:
        print(f"result: needs-you — atom {ns.atom} not found in {ns.root / 'atoms'}")
        return 2
    return land_verdict(ns.root, ns.atom, ns.node, verdict, reason)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--atom", required=True, help="the atom to judge for placement")
    sub = ap.add_subparsers(dest="cmd")
    j = sub.add_parser("judge", help="compute the verdict and land it via loop.node judge")
    j.add_argument("--node", required=True,
                   help="the gate's real node id, e.g. placement-gate.det.v1")
    j.add_argument("--by", default="placement-gate",
                   help="who ran the deterministic gate (provenance)")
    j.set_defaults(func=cmd_judge)
    ns = ap.parse_args(argv)
    if getattr(ns, "func", None) is None:
        return cmd_show(ns)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
