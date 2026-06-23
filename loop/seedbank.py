#!/usr/bin/env python3
"""The seed bank (done-line 0093): where the harvest banks its seed.

bdo, 2026-06-16: "a seed is not automatically planted." A harvested generative
shape is *banked* as a **proposed** pattern — seen, recorded, but not yet a real
Commons pattern. **Planting** — promoting a banked seed into the Commons — is a
deliberate, separate hand: an admission (D-4), the way `loop/tags.py` promotes a
proposed vocabulary value with `admit_tag`. This module reuses that
proposed→admitted grain over the append-only log (§10, not a new mechanism); no
Pattern Commons is homed in ontum yet, so the proposed pool *is* the seed bank.

Seed and grain are states of one harvested signal (meteor/meteorite); this holds
the *seed* state and its one deliberate transition — planting. Autonomous
planting (an in-fence seed self-planting once the loop is trusted, the PR #163
auto-admit-fence applied to the Commons) is the horizon, not here.

Pure stdlib, reusing `reconcile.Fold` / `append_line` / `short_hash` / `now_ts`.
"""

import argparse
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

PROPOSED = "pattern_proposed"   # banking a seed (signed, not planted)
PLANTED = "pattern_planted"     # planting it (a deliberate second hand, D-4)


class SeedRefused(ValueError):
    """A bank or plant the seed bank refuses — it names what is missing or why
    the transition is not allowed (the §10 teeth of the bank)."""


def seeds(root):
    """Fold the bank: every banked pattern with its state. Latest proposed per
    slug wins; a slug carrying a `pattern_planted` reads `planted`, else
    `proposed`. Returns a list sorted by slug."""
    fold = Fold(Path(root))
    banked, planted = {}, {}
    for adm in fold.admissions:
        t, slug = adm.get("type"), adm.get("slug")
        if not slug:
            continue
        if t == PROPOSED:
            banked[slug] = adm
        elif t == PLANTED:
            planted[slug] = adm.get("by")
    out = []
    for slug, rec in sorted(banked.items()):
        out.append({
            "slug": slug,
            "shape": rec.get("shape"),
            "provenance": rec.get("provenance"),
            "proposed_by": rec.get("by"),
            "state": "planted" if slug in planted else "proposed",
            "planted_by": planted.get(slug),
        })
    return out


def _seed(root, slug):
    for s in seeds(root):
        if s["slug"] == slug:
            return s
    return None


def bank(root, slug, shape, *, provenance=None, by):
    """Bank a harvested shape as a PROPOSED pattern — recorded, signed, but not
    planted. Re-banking a slug supersedes (latest wins in the fold), so a season
    that re-finds the same seed folds to one. Refuses an unslugged or unsigned
    seed."""
    slug = (slug or "").strip()
    if not slug:
        raise SeedRefused("a seed needs a slug (its boring address)")
    if not (by or "").strip():
        raise SeedRefused("banking is signed (--by): who proposes this seed")
    adm = {
        "id": "adm." + short_hash(PROPOSED, slug, str(shape), str(by), now_ts()),
        "type": PROPOSED,
        "slug": slug,
        "shape": shape,
        "provenance": provenance,
        "by": by,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "admissions.jsonl", adm)
    return adm


def plant(root, slug, *, by):
    """Plant a banked seed — promote it from proposed to a real Commons pattern.
    The deliberate, separate hand (D-4). Refuses three ways (the teeth):
      - unsigned: a seed is not *automatically* planted;
      - unbanked: you cannot plant a seed that was never banked;
      - self-plant: the hand that banked a seed cannot plant it too — no one
        plants their own seed; planting is a second hand (autonomous planting,
        an in-fence self-plant, is the trusted-loop horizon, not this)."""
    by = (by or "").strip()
    if not by:
        raise SeedRefused(
            "planting is signed (--by); a seed is not automatically planted")
    seed = _seed(root, slug)
    if seed is None:
        raise SeedRefused(
            f"no banked seed {slug!r}; you cannot plant a seed never banked")
    if by == (seed["proposed_by"] or "").strip():
        raise SeedRefused(
            f"{by!r} banked {slug!r} and cannot plant it too — no one plants "
            "their own seed (D-4); planting is a second, deliberate hand "
            "(autonomous in-fence planting is the trusted-loop horizon)")
    adm = {
        "id": "adm." + short_hash(PLANTED, slug, by, now_ts()),
        "type": PLANTED,
        "slug": slug,
        "by": by,
        "authorized": True,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "admissions.jsonl", adm)
    return adm


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("bank", help="bank a harvested shape as a proposed seed")
    b.add_argument("--slug", required=True)
    b.add_argument("--shape", required=True, help="the pattern, in a line")
    b.add_argument("--provenance", default=None, help="the signals it came from")
    b.add_argument("--by", required=True)
    b.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p = sub.add_parser("plant", help="plant a banked seed (a deliberate hand, D-4)")
    p.add_argument("--slug", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = ap.parse_args(argv)

    if args.cmd == "bank":
        try:
            adm = bank(args.root, args.slug, args.shape,
                       provenance=args.provenance, by=args.by)
        except SeedRefused as e:
            print(f"result: needs-you — {e}")
            return 2
        print(f"result: report — banked seed {adm['slug']!r} as proposed "
              f"(by {adm['by']}); not planted. Plant it with a deliberate hand.")
        return 0
    if args.cmd == "plant":
        try:
            adm = plant(args.root, args.slug, by=args.by)
        except SeedRefused as e:
            print(f"result: needs-you — {e}")
            return 2
        print(f"result: report — planted seed {adm['slug']!r} into the Commons "
              f"(by {adm['by']}).")
        return 0

    root = getattr(args, "root", DEFAULT_ROOT)
    bank_state = seeds(root)
    if not bank_state:
        print("result: report — the seed bank is empty (no seed harvested yet)")
        return 0
    for s in bank_state:
        print(f"  {s['state']:9} {s['slug']} — {s['shape']}")
    print(f"result: report — {len(bank_state)} seed(s) in the bank "
          f"({sum(1 for s in bank_state if s['state'] == 'planted')} planted)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
