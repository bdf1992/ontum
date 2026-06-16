#!/usr/bin/env python3
"""Harvest at a Stop (done-line 0094): the stopping point becomes a harvest.

bdo, 2026-06-16: "if a loop maker hits a stopping point they should be creative."
This is the creative move. When the loop-maker returns a `Stop`, instead of going
idle the system farms the run's recorded teeth-signals (loop/signals) for what
they reveal, and sorts the yield by **generativity** — recurrence is the *tell*:

- **grain** — a one-off signal: a *grain of insight*, consumed now (named, used).
- **seed** — a recurring shape: generative, **banked** as a proposed pattern in
  the seed bank (loop/seedbank), to grow future seasons.

Two things this does NOT do, by design (the §10 teeth, the meteor→meteorite
transitions): it never **plants** (banking is proposed; planting into the Commons
is a separate, deliberate hand — D-4; autonomous in-fence planting is the
trusted-loop horizon), and it never consumes a generative shape as mere grain
(seed eaten) nor banks a one-off as seed (noise in the bank).

Composes the existing pieces (§10): `signals` is the field, `seedbank` is where
seed lands, `loopmaker` is the Stop that triggers the farm. Pure stdlib.
"""

import argparse
import re
from pathlib import Path

from loop import loopmaker, seedbank, signals
from loop.reconcile import DEFAULT_ROOT

DEFAULT_RECURRENCE = 2          # the tell for generativity: seen >= this -> seed
_SLUG = re.compile(r"[^a-z0-9]+")


def _slug(kind):
    return _SLUG.sub("-", kind.lower()).strip("-") or "signal"


def harvest(epic_id, root, *, by, recurrence=DEFAULT_RECURRENCE):
    """Fold the recorded signals into grain (one-off insights, consumed) and
    seed (recurring shapes, banked as proposed). Banks each recurring shape; it
    never plants. Returns {grain, seed, planted} — `planted` is always empty:
    planting is a separate deliberate hand."""
    by_kind = {}
    for sig in signals.read(root):
        by_kind.setdefault(sig.get("kind", "?"), []).append(sig)

    grain, seed = [], []
    for kind, items in sorted(by_kind.items()):
        if len(items) >= recurrence:
            # a recurring shape — seed. Bank it proposed (never planted).
            slug = _slug(kind)
            shape = f"recurring teeth-signal {kind!r} (x{len(items)})"
            provenance = f"harvest of {epic_id}: {len(items)} firings of {kind}"
            seedbank.bank(root, slug, shape, provenance=provenance, by=by)
            seed.append(slug)
        else:
            # a one-off — grain: a consumable insight, named and used now.
            one = items[0]
            grain.append({
                "kind": kind,
                "subject": one.get("subject"),
                "insight": one.get("why"),
            })
    return {"grain": grain, "seed": seed, "planted": []}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("epic_id", help="the arc whose stopping point to harvest")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--by", default="harvest")
    ap.add_argument("--recurrence", type=int, default=DEFAULT_RECURRENCE)
    args = ap.parse_args(argv)

    result = loopmaker.operate(args.epic_id, root=args.root)
    if isinstance(result, loopmaker.Increment):
        print(f"result: report — {args.epic_id} is not at a stopping point "
              f"(next: {result.atom}); no harvest. Build, don't farm.")
        return 0

    # a Stop — farm it
    h = harvest(args.epic_id, args.root, by=args.by, recurrence=args.recurrence)
    print(f"result: report — harvested the stop of {args.epic_id} "
          f"(stop: {result.reason}):")
    for g in h["grain"]:
        print(f"  grain (insight): {g['kind']} — {g['insight']}")
    for slug in h["seed"]:
        print(f"  seed (banked, proposed): {slug}")
    print(f"  planted: none — planting is a deliberate hand (D-4); "
          f"plant a seed with `python -m loop.seedbank plant --slug <s> --by <who>`")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
