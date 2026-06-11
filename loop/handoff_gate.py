#!/usr/bin/env python3
"""The handoff gate's deterministic backing — the third *kind* of real gate
is the same kind as the second: law, not judgment.

The pipeline order is value → owner-stamp → placement → **handoff** → confirm.
The value gate (first light, done-line 0040) asks judgment — "is this the
owner's value?" — and a mortal mind answers. Placement (done-line 0041) asks
law — "do two atoms refuse to share an address?" — and a fold answers. The
handoff gate asks a law question too: **is this atom ready to be handed to an
implementer, or is it hollow?** No mind is needed to see that an atom carries
no story, names no surface to build on, and declares no downstream — that is
structure, and structure is read, not judged (epic.experience-layer horizon:
"deterministic where the question is law, inference where it is judgment").

The law, in one sentence: an atom is **`ready_for_spec`** when it carries the
three things an implementer cannot start without — a non-empty story (the what
and why), at least one `incidence.touches` address (the surface the work will
occupy), and at least one `incidence.hands_off_to` seam (where the finished
work goes) — and **`send_back`** when any of the three is missing, naming
exactly which.

This is the §10 case (D-10, §10): an atom that is *locally* fine at every
earlier gate — it had value, it placed cleanly — can still be hollow at
handoff (a story with no surface, or a surface with nowhere to go), and the
gate notices. A gate whose verdict could not have been its opposite did not
gate; this one's opposite is one missing field away. A fixed-verdict mock that
always says `ready_for_spec` waves a hollow atom straight through — that is the
bug this gate exists to catch.

Pure stdlib, no git, no subprocess, no mind (the fold is data — the hard rule).
The verdict reaches the log only through the one pen (`loop.node judge`, D-4);
this module never writes a receipt itself. The law it applies is versioned
source — `.ai-native/nodes/handoff-gate.det.v1.md` — hashed onto the receipt as
`prompt_hash` (§7), exactly as the placement law's spec is, so every
deterministic verdict is attributable to the exact law that produced it.

Usage:
  python -m loop.handoff_gate --atom <id>                 # read-only: the verdict, no write
  python -m loop.handoff_gate judge --atom <id> --node <node-id> --by <who>
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import load_atoms
from loop.node import judge as land_verdict

DEFAULT_ROOT = Path(".ai-native")

# This stage's node in the pipeline; the real node id is passed at judge time
# (the admit-real mapping), never re-declared here.
STAGE_NODE = "handoff-gate.mock.v0"


def _story_text(atom):
    """The atom's story text, stripped. Tolerant of a missing/None story."""
    return ((atom.get("story", {}) or {}).get("text", "") or "").strip()


def _addresses(atom, key):
    """An atom's address set for one incidence key (touches, hands_off_to).
    Tolerant of a missing/None field — absence is what this gate reads."""
    return set((atom.get("incidence", {}) or {}).get(key, []) or [])


# The three structural requirements an implementer cannot start without, each
# a (human-name, predicate, what-is-missing) the §10 law folds over. Order is
# stable so the reason a cold reader sees is deterministic.
REQUIREMENTS = [
    ("story",
     lambda a: bool(_story_text(a)),
     "an empty story — nothing says what to build or why"),
    ("incidence.touches",
     lambda a: bool(_addresses(a, "touches")),
     "no declared surface (incidence.touches) — nowhere for the work to land"),
    ("incidence.hands_off_to",
     lambda a: bool(_addresses(a, "hands_off_to")),
     "no declared downstream (incidence.hands_off_to) — the finished work has "
     "nowhere to go"),
]


def missing_for(atom):
    """The requirements this atom fails to meet, as (name, what_is_missing).
    Pure over the single atom; order-stable."""
    return [(name, gap) for name, ok, gap in REQUIREMENTS if not ok(atom)]


def handoff_verdict(atom):
    """The deterministic verdict: (`ready_for_spec` | `send_back`, reason). The
    reason is the receipt's payload — it names every missing requirement, so a
    cold reader sees *why* it was sent back, not just *that* it was."""
    gaps = missing_for(atom)
    if gaps:
        named = "; ".join(f"{name}: {gap}" for name, gap in gaps)
        return ("send_back",
                f"{atom['id']} is not ready to hand off — {len(gaps)} of the "
                f"three things an implementer needs is missing: {named}. The "
                "atom is sent back to be completed before it becomes a spec.")
    return ("ready_for_spec",
            f"{atom['id']} is ready to hand off: it carries a story, at least "
            "one surface to build on (incidence.touches), and a declared "
            "downstream (incidence.hands_off_to) — an implementer can start "
            "without guessing.")


def verdict_for(root, atom_id):
    """Resolve one atom and return its verdict, or raise LookupError if the
    atom is not on disk."""
    target = next((a for a, _ in load_atoms(root) if a["id"] == atom_id), None)
    if target is None:
        raise LookupError(atom_id)
    return handoff_verdict(target)


# ----------------------------------------------------------------- runtime

def cmd_show(ns):
    """Read-only: compute and print the verdict without touching the log. The
    honest preview — what the gate *would* land, runnable before bdo admits the
    stage real (until then `judge` itself is refused by the seam)."""
    try:
        verdict, reason = verdict_for(ns.root, ns.atom)
    except LookupError:
        print(f"result: needs-you — atom {ns.atom} not found in {ns.root / 'atoms'}")
        return 2
    print(f"{ns.atom}: {verdict}")
    print(f"  {reason}")
    print(f"result: report — deterministic handoff verdict for {ns.atom} is "
          f"{verdict!r} (read-only; land it through loop.node judge)")
    return 0


def cmd_judge(ns):
    """Compute the verdict and land it through the one pen (D-4). The pen
    enforces the seam: if `handoff-gate.mock.v0` is not yet admitted real,
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
    ap.add_argument("--atom", required=True, help="the atom to judge for handoff")
    sub = ap.add_subparsers(dest="cmd")
    j = sub.add_parser("judge", help="compute the verdict and land it via loop.node judge")
    j.add_argument("--node", required=True,
                   help="the gate's real node id, e.g. handoff-gate.det.v1")
    j.add_argument("--by", default="handoff-gate",
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
