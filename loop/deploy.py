#!/usr/bin/env python3
"""The production gate (done-line 0137): the live URL stops changing without
bdo's stamp.

The first buildable slice of `epic.environments` (bdo's confirmed arc, PR
#277). Today `.github/workflows/pages.yml` deploys `main`'s HEAD to the live
surface bdo judges on (`bdf1992.github.io/ontum`) on every push, with no owner
stamp — the one promotion that escapes him (epic glue, `atom.production-gate.v0`).
This module closes that gap with the smallest real teeth, in the repo's
established grain: a pure deterministic checker (the `atom-invariant` /
`loop.phrasing` shape) whose authority is the owner stamp. The gate *executes*
bdo's gesture; it never invents a verdict (the `.github/` law and the arc's
second guardrail — a server surface enforces TOWARD truth, never as a second
authority).

The spine is **non-circular by deploying the stamped snapshot, never HEAD**:
production is the latest non-superseded snapshot bdo authorized, so the act of
recording a stamp (which is itself a commit) can never become unstamped live
content. A `production_promotion` admission (`by: bdo`, a `snapshot` commit sha,
supersedable) is bdo's stamp — the same authority shape as `confirm-arc` and
`supersede-done` (bdo-only, latest wins, an `enabled: false` withdraws). Before
the first stamp the gate is in a loud **unstamped passthrough** transition: it
reports HEAD as the deploy target and says the first owner promotion engages the
gate — so landing this never dark-takes the live site, the way `atom-invariant`
engages only on bdo's branch-protection gesture.

Read-only and propose-only here: the only writer is bdo's stamp through the one
pen verb (`promote`), which refuses every non-bdo signer (D-4). Stdlib only, no
network, no git (loop/'s law) — a pure fold over the committed log.

The GitHub-gesture intake rail (a session running `promote --by bdo` on bdo's
closed-issue comment — the `realness-intake` / `policy-intake` shape) is the
activation path; it is named in the done-line, not built here.

CLI:
  python -m loop.deploy                       the production snapshot + deploy target, read-only
  python -m loop.deploy --json                the raw dataset (machine-readable)
  python -m loop.deploy gate --candidate <sha>  CI seam: exit 0 promote / non-zero hold
  python -m loop.deploy promote --snapshot <sha> --by bdo   bdo's stamp (the one writer)
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, canon, now_ts,
                            short_hash)

PROMOTION_TYPE = "production_promotion"
ENVIRONMENT = "production"


def production_promotion(fold):
    """The active `production_promotion` admission, or None — the latest
    non-superseded one bdo authorized. Mirrors `arc_confirmation` (done-line
    0028): latest admission wins, an `enabled: false` one withdraws (superseded,
    never erased). Only bdo-signed records are eligible — the pen is the only
    writer and refuses every other signer, but the fold re-checks the signature
    so a hand-appended line cannot forge a promotion."""
    active = None
    for adm in fold.admissions:
        if adm.get("type") != PROMOTION_TYPE:
            continue
        if (adm.get("by") or "").strip().lower() != "bdo":
            continue
        active = adm if adm.get("enabled", True) else None
    return active


def production_snapshot(root=DEFAULT_ROOT, fold=None):
    """The current production snapshot sha (the stamped, live-authorized
    commit), or None when no stamp stands yet (the unstamped-passthrough
    transition)."""
    fold = fold or Fold(root)
    adm = production_promotion(fold)
    return adm.get("snapshot") if adm else None


def gate(candidate, root=DEFAULT_ROOT, fold=None):
    """The gate verdict for a candidate commit sha. `promote` iff the candidate
    is the stamped production snapshot; `hold` otherwise, with a cited reason.

    The §10 teeth: a candidate and a stamp are each locally fine; when they name
    different snapshots they refuse to fit, and the gate holds rather than
    letting unstamped content reach the live surface. Returns a dataset dict."""
    fold = fold or Fold(root)
    adm = production_promotion(fold)
    snapshot = adm.get("snapshot") if adm else None
    cand = (candidate or "").strip()

    if snapshot is None:
        return {
            "verdict": "passthrough",
            "candidate": cand,
            "snapshot": None,
            "deploy": cand,
            "reason": (
                "production is UNSTAMPED — no `production_promotion` on the log. "
                "The gate is in transition: HEAD passes through to the live "
                "surface, and bdo's first promotion engages the teeth. Stamp "
                "with: python -m loop.deploy promote --snapshot <sha> --by bdo"
            ),
        }
    if cand and cand == snapshot:
        return {
            "verdict": "promote",
            "candidate": cand,
            "snapshot": snapshot,
            "deploy": snapshot,
            "reason": (
                f"candidate {cand[:12]} is the stamped production snapshot "
                f"(promoted by {adm.get('by')} at {adm.get('ts')})"
            ),
        }
    return {
        "verdict": "hold",
        "candidate": cand,
        "snapshot": snapshot,
        "deploy": snapshot,
        "reason": (
            f"candidate {cand[:12] or '(none)'} is not the stamped production "
            f"snapshot {snapshot[:12]} — the live surface only moves on bdo's "
            "stamp; the deploy serves the stamped snapshot, not the candidate"
        ),
    }


def promote(root, snapshot, by, enabled=True, supersedes=None):
    """bdo's stamp: append one `production_promotion` admission authorizing the
    live surface to serve `snapshot`. The one writer of this module, and bdo's
    alone — production promotion is the owner's gesture, the same authority as
    `confirm-arc` (it executes, it never judges). Returns the admission, or None
    on refusal (already printed)."""
    if (by or "").strip().lower() != "bdo":
        print("result: needs-you — promoting to production is the owner's stamp "
              "— --by must be bdo (the live surface only moves on his gesture; "
              "the gate executes it, nothing promotes its own work, D-4)")
        return None
    snap = (snapshot or "").strip()
    if not snap:
        print("result: needs-you — a promotion names the snapshot it authorizes "
              "— pass --snapshot <commit-sha>")
        return None
    adm = {
        "id": "adm." + short_hash(PROMOTION_TYPE, snap, str(enabled), str(by), now_ts()),
        "type": PROMOTION_TYPE,
        "environment": ENVIRONMENT,
        "snapshot": snap,
        "enabled": bool(enabled),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def render(root):
    fold = Fold(root)
    adm = production_promotion(fold)
    lines = ["# Production gate — the live surface only moves on bdo's stamp", ""]
    if adm is None:
        lines += [
            "_status: **UNSTAMPED PASSTHROUGH** (transition)._",
            "",
            "No `production_promotion` stands on the log. The gate is built and "
            "engaged in CI, but holds no snapshot yet: HEAD passes through to the "
            "live surface until bdo's first promotion, which engages the teeth.",
            "",
            "Stamp the live snapshot with:",
            "    python -m loop.deploy promote --snapshot <commit-sha> --by bdo",
        ]
    else:
        lines += [
            f"_status: **stamped**. Live snapshot: `{adm['snapshot']}`._",
            "",
            f"- promoted by **{adm.get('by')}** at {adm.get('ts')}",
            f"- admission `{adm.get('id')}`",
            "",
            "The live surface serves this snapshot and will not move until bdo "
            "promotes another. A candidate commit that is not this snapshot is "
            "**held** by the gate (`python -m loop.deploy gate --candidate <sha>`).",
        ]
    lines += [
        "",
        "_read-only fold; the only writer is bdo's stamp through `promote` (D-4)._",
    ]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("gate", help="CI seam: exit 0 on promote/passthrough, "
                                    "non-zero on hold")
    g.add_argument("--candidate", required=True,
                   help="the commit sha being considered for the live surface")

    p = sub.add_parser("promote", help="bdo's stamp: authorize a snapshot for "
                                       "the live surface (the one writer)")
    p.add_argument("--snapshot", required=True,
                   help="the commit sha to promote to production")
    p.add_argument("--by", required=True,
                   help="who promotes it (D-4: bdo only — the owner's gesture)")
    p.add_argument("--off", action="store_true",
                   help="withdraw the promotion (back to unstamped passthrough)")
    p.add_argument("--supersedes", default=None,
                   help="a prior promotion id this replaces")

    args = ap.parse_args(argv)

    if args.cmd == "gate":
        r = gate(args.candidate, args.root)
        if args.json:
            print(canon(r))
        else:
            print(f"gate: {r['verdict']} — {r['reason']}")
            print(f"deploy target: {r['deploy'][:12] if r['deploy'] else '(none)'}")
        # hold is the only blocking verdict; promote and passthrough proceed
        if r["verdict"] == "hold":
            print("result: needs-you — the candidate is not the stamped snapshot; "
                  "the live surface holds")
            return 1
        print(f"result: done — {r['verdict']}")
        return 0

    if args.cmd == "promote":
        adm = promote(args.root, args.snapshot, args.by,
                      enabled=not args.off, supersedes=args.supersedes)
        if adm is None:
            return 1
        verb = "withdrawn" if args.off else "promoted"
        print(f"result: done — production {verb}: snapshot {adm['snapshot'][:12]} "
              f"by {adm['by']} ({adm['id']})")
        return 0

    # no subcommand: read-only status
    if args.json:
        print(canon(gate("", args.root)))
    else:
        print(render(args.root))
        print()
    snap = production_snapshot(args.root)
    if snap:
        print(f"result: done — production stamped to {snap[:12]}")
    else:
        print("result: report — production UNSTAMPED (passthrough); "
              "awaiting bdo's first promotion gesture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
