#!/usr/bin/env python3
"""The bounded-run fold (done-line 0087): the world as proposed bounds.

bdo, 2026-06-15: "every directory and file inside my digital world can be
AI-native," and — correcting the apparent paradox of 40h of games against
building a company — "this is actually three different bounded runs," each with
its own set of expectations and control surface. This fold is the step that
reads a person's cited evidence and proposes those bounds.

It clusters the cited sensor's evidence by data locality into **proposed**
bounded-run candidates. Each candidate carries the holonic slots a bound needs —
`purpose` (mission/vision/values), `anima` (expected rhythm/tempo),
`control_surface` — but leaves them **unset**: they are *declared input* the
person confirms (D-4), never values the fold infers. Reality is folded; purpose
is declared. The machine proposes the bound; it does not tell the person who
they are.

The teeth are the reused ghost discipline (§10): a candidate must be backed by
resolvable evidence — a locality whose citations resolve to nothing is refused,
not emitted. Nothing here is minted: every candidate is `proposed` until a human
stamp lifts it.

Pure stdlib + the reused sensor. Read-only: it derives and reports, mints
nothing.
"""

import argparse

from causality import cited_sensor

STATUS_PROPOSED = "proposed"
KIND = "bounded-run"
# the holonic slots a bound declares — present on every candidate, unset until
# the person declares them (declared-input, never inferred)
DECLARED_SLOTS = ("purpose", "anima", "control_surface")


def _locality(rel_path):
    """The bound a file belongs to by locality: its top-level directory, or
    '(root)' for a file directly under the data surface. The filesystem is the
    first, honest bounding — a 'company' spanning many folders or a file serving
    two bounds is the boundary-drawing edge named in the outcome, resolved later
    by reference, not ownership; this v0 proposes the directory bound."""
    head, sep, _ = rel_path.partition("/")
    return head if sep else "(root)"


def _candidate(locality, backing):
    cand = {
        "id": f"bound/{locality}",
        "kind": KIND,
        "status": STATUS_PROPOSED,
        "locality": locality,
        "members": len(backing),
        "evidence": backing,
    }
    # the declared-input slots: present, but the fold never fills them — that is
    # the person's to declare (D-4). Inferring a purpose here would be the
    # machine telling the person who they are (the outcome's non-example).
    for slot in DECLARED_SLOTS:
        cand[slot] = None
    return cand


def fold(data_root, *, evidence=None):
    """Cluster cited evidence into proposed bounded-run candidates by locality.

    Returns (candidates, refused). `evidence` defaults to a fresh read-only scan
    of the data surface; only resolvable records back a candidate (the reused
    ghost discipline), and a locality with no resolvable backing is refused —
    named, never silently dropped. Deterministic: localities are sorted."""
    records = cited_sensor.scan(data_root) if evidence is None else evidence
    by_locality = {}
    for ev in records:
        by_locality.setdefault(_locality(ev["file"]), []).append(ev)

    candidates, refused = [], []
    for locality, evs in sorted(by_locality.items()):
        backing = [e for e in evs if not cited_sensor.is_ghost(data_root, e)]
        if not backing:
            refused.append({
                "locality": locality,
                "why": "no resolvable evidence backs this bound "
                       "(ghost-only citations)",
            })
            continue
        candidates.append(_candidate(locality, backing))
    return candidates, refused


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("data_root", help="the data surface to fold (read-only)")
    args = ap.parse_args(argv)
    candidates, refused = fold(args.data_root)
    for c in candidates:
        print(f"  proposed bound: {c['id']} "
              f"[{c['members']} member(s); purpose/anima/control_surface unset]")
    for r in refused:
        print(f"  refused: {r['locality']} — {r['why']}")
    print(f"result: report — folded {args.data_root} into {len(candidates)} "
          f"proposed bounded-run(s), {len(refused)} locality(ies) refused "
          "(every bound proposed, none minted)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
