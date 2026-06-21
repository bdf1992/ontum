#!/usr/bin/env python3
"""The git-tier staging rung + promotion path (done-line 0162): main as the
recorded "integrated, not yet accepted" rung a snapshot is promoted FROM, and
one readable promotion path per snapshot — local → staging → production.

The GIT-tier DEPLOYMENT face of `epic.environments` (bdo's confirmed arc). The
loop already writes a record at each end of the path — `local_deployment`
(`loop/preview.py`, the local rung) and `production_promotion`
(`loop/deploy.py`, the production rung) — but nothing named the middle rung or
read the path as one ordered thing. This adds the staging rung (a
`staging_promotion` record) and the unifying fold.

COMPOSES, never double-builds (§10): it reads `preview.local_deployments`,
`deploy.production_snapshot`, and `snapshot.resolve`/`snapshot.snapshots`. It
joins the two namespaces deploy.py and preview.py use — deploy keys production
on a COMMIT sha, preview keys local on the snapshot NAME — by resolving a
snapshot's name to its commit. It does NOT modify the landed deploy/preview
behaviour, and it never re-judges acceptance (that stays the pipeline's, D-4).

The §10 teeth — the path refuses to fit out of order:
  - only an ACCEPTED snapshot may be promoted to staging (a stale/ghost/
    unaccepted one is refused, nothing recorded);
  - the path is ORDERED — a snapshot reaches staging only after the local rung
    (a staging promotion with no prior local deployment is refused as
    out-of-order), and `promotion_path` flags any out-of-order state it reads
    (a rung reached without its predecessor — production without staging).

Stdlib, local-first, no git — a pure fold over the committed log plus one pen.

CLI:
  python -m loop.promote                       every snapshot's promotion path
  python -m loop.promote --json                the raw dataset
  python -m loop.promote gate --name <n>       exit 0 promotable-to-staging / non-zero held
  python -m loop.promote stage --name <n> --by <who>   promote a snapshot to the staging rung
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, canon, now_ts,
                            short_hash)
from loop import snapshot, preview, deploy

STAGING_TYPE = "staging_promotion"
ENVIRONMENT = "staging"
RUNGS = ("local", "staging", "production")


def staging_promotions(fold):
    """The active staging promotions, latest-by-name wins, an `enabled: false`
    one withdrawn (the admitted-record shape shared across the loop)."""
    active = {}
    for adm in fold.admissions:
        if adm.get("type") != STAGING_TYPE:
            continue
        name = adm.get("snapshot")
        if not name:
            continue
        active[name] = adm if adm.get("enabled", True) else None
    return {n: a for n, a in active.items() if a is not None}


def _local_reached(fold, name):
    return any(a.get("snapshot") == name
               for a in preview.local_deployments(fold))


def _production_reached(root, fold, commit):
    return bool(commit) and deploy.production_snapshot(root, fold) == commit


def promotion_path(name, root=DEFAULT_ROOT, fold=None):
    """The ordered path local → staging → production for one snapshot, each
    rung reached/not, and an out_of_order flag — a later rung reached without
    its predecessor (two locally-fine records that refuse to fit)."""
    fold = fold or Fold(root)
    adm = snapshot.snapshots(fold).get(name)
    commit = adm.get("commit") if adm else None
    reached = {
        "local": _local_reached(fold, name),
        "staging": name in staging_promotions(fold),
        "production": _production_reached(root, fold, commit),
    }
    out_of_order = ((reached["staging"] and not reached["local"]) or
                    (reached["production"] and not reached["staging"]))
    return {
        "name": name,
        "commit": commit,
        "exists": adm is not None,
        "reached": reached,
        "out_of_order": out_of_order,
        "reason": (
            "out-of-order: a rung is reached without its predecessor "
            "(local→staging→production); reconcile the path"
            if out_of_order else
            "path is ordered (" + " → ".join(
                r for r in RUNGS if reached[r]) + ")" if any(reached.values())
            else "not yet promoted to any environment"
        ),
    }


def gate(name, root=DEFAULT_ROOT, fold=None):
    """Is the snapshot promotable to the staging rung? Yes iff it resolves
    `accepted` AND has already reached the local rung — else held, with the
    blocking reason cited (non-accepted, or out-of-order: no local deployment
    first)."""
    fold = fold or Fold(root)
    res = snapshot.resolve(name, root, fold)
    if res is None:
        return {"promotable": False, "verdict": "unknown", "commit": None,
                "local": False,
                "reason": f"no snapshot named `{name}`"}
    accepted = res["verdict"] == "accepted"
    local = _local_reached(fold, name)
    if not accepted:
        reason = (f"snapshot `{name}` is {res['verdict']} — only an accepted "
                  "snapshot may be promoted to staging")
    elif not local:
        reason = (f"snapshot `{name}` is accepted but has not reached the local "
                  "rung — promote it locally first (out-of-order; the path is "
                  "local → staging → production)")
    else:
        reason = f"snapshot `{name}` is accepted and locally deployed — promotable to staging"
    return {"promotable": accepted and local, "verdict": res["verdict"],
            "commit": res["commit"], "local": local, "reason": reason}


def promote_staging(root, name, by, fold=None):
    """The one writer: append a `staging_promotion` for an accepted, locally-
    deployed snapshot; refuse (writing nothing) otherwise. Returns
    (admission, gate)."""
    fold = fold or Fold(root)
    g = gate(name, root, fold)
    if not g["promotable"]:
        print(f"result: needs-you — refused: {g['reason']}")
        return None, g
    if not (by or "").strip():
        print("result: needs-you — a staging promotion records who promoted it "
              "— pass --by")
        return None, g
    adm = {
        "id": "adm." + short_hash(STAGING_TYPE, name, g["commit"] or "",
                                  str(by), now_ts()),
        "type": STAGING_TYPE,
        "environment": ENVIRONMENT,
        "snapshot": name,
        "commit": g["commit"],
        "enabled": True,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm, g


def dataset(root=DEFAULT_ROOT, fold=None):
    fold = fold or Fold(root)
    names = sorted(snapshot.snapshots(fold))
    return {"paths": [promotion_path(n, root, fold) for n in names]}


def _bar(reached):
    return " ".join((f"[{r}]" if reached[r] else f" {r} ") for r in RUNGS)


def render(root):
    d = dataset(root)
    lines = ["# Promotion paths — local → staging → production", ""]
    if not d["paths"]:
        lines += ["_no snapshot to promote yet._"]
        return "\n".join(lines)
    for p in d["paths"]:
        mark = "⚠ out-of-order" if p["out_of_order"] else "·"
        lines.append(f"## `{p['name']}`  {mark}")
        lines.append(f"- {_bar(p['reached'])}  (commit `{(p['commit'] or '?')[:12]}`)")
        lines.append(f"  → {p['reason']}")
        lines.append("")
    lines.append("_read-only fold; the only writer is the `stage` pen. The local "
                 "and production rungs are read from preview.py/deploy.py (D-4)._")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("gate", help="CI seam: exit 0 promotable-to-staging / non-zero held")
    g.add_argument("--name", required=True)

    s = sub.add_parser("stage", help="promote a snapshot to the staging rung (the pen)")
    s.add_argument("--name", required=True)
    s.add_argument("--by", required=True, help="who promotes it")

    args = ap.parse_args(argv)

    if args.cmd == "gate":
        r = gate(args.name, args.root)
        print(f"gate: {'promotable' if r['promotable'] else 'held'} — {r['reason']}")
        if not r["promotable"]:
            print("result: needs-you — snapshot not promotable to staging")
            return 1
        print("result: done — promotable to the staging rung")
        return 0

    if args.cmd == "stage":
        adm, _ = promote_staging(args.root, args.name, args.by)
        if adm is None:
            return 1
        print(f"result: done — promoted `{adm['snapshot']}` to the staging rung "
              f"({adm['id']})")
        return 0

    # no subcommand: read-only status
    if args.json:
        print(canon(dataset(args.root)))
    else:
        print(render(args.root))
        print()
    d = dataset(args.root)
    ooo = [p["name"] for p in d["paths"] if p["out_of_order"]]
    if ooo:
        print(f"result: report — {len(ooo)} snapshot(s) with an out-of-order "
              f"promotion path: {', '.join(ooo)}")
        return 0
    print(f"result: done — {len(d['paths'])} promotion path(s); none out of order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
