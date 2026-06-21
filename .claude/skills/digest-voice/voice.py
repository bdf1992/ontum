#!/usr/bin/env python3
"""The digest voice pen — the reach half of the digest's voice layer (issue #410).

Pairs with loop/digest_voice.py (the pure core: the bounded prompt builder and
the grounding guard). This pen is the ONLY part that reaches: it folds the
digest dataset, asks the governed inference gateway for patch-notes headlines,
GROUNDS the completion against the dataset (a ghost headline is dropped and
named — loop.digest_voice.ground), and emits the deterministic render with the
surviving headlines prepended.

The split is the loop's law: the fold stays truth (loop/digest.py is pure and
stdlib), inference only narrates what the fold already computed, and the only
outward reach (the HTTP completion) lives here in a pen, never in loop/. The
call rides the sanctioned path — the gateway pen's `complete()`, default-deny
RBAC — so this pen is inert until bdo admits a policy for (digest-voice,
owner-digest, *). When inference is unavailable, unpermitted, or every proposed
headline is refused by the guard, the pen DEGRADES to the plain deterministic
render: the patch-notes structure is the floor, voice is the polish.

Usage:
  python .claude/skills/digest-voice/voice.py            # the voiced digest
  python .claude/skills/digest-voice/voice.py --dry-run  # the prompt only, no reach
  python .claude/skills/digest-voice/voice.py --json     # {headlines, rejected, mind}
  python .claude/skills/digest-voice/voice.py --today    # only today's span

result: report (read-only on the log save for the gateway's own receipts).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from loop import digest as D
from loop import digest_voice as V
from loop.reconcile import DEFAULT_ROOT, now_ts

# This pen's identity at the gateway — the (caller, surface) a policy permits.
# Default-deny means a permit is bdo's stamp:
#   python -m loop.inference policy --caller digest-voice --surface owner-digest \
#       --mind '*' --by bdo
CALLER = "digest-voice"
SURFACE = "owner-digest"


def voiced(root=None, *, since=None, until=None, route="default",
           timeout=60, by="claude"):
    """Fold the digest, ask the gateway for headlines, ground them. Returns
    (dataset, kept_headlines, rejected, gateway_result, degrade_note). The
    gateway is imported lazily so importing this module (for the pure
    composition below, or in tests) never reaches the network."""
    d = D.digest(root or DEFAULT_ROOT, since=since, until=until)
    prompt = V.build_prompt(d)

    sys.path.insert(0, str(ROOT / ".claude" / "skills" / "gateway"))
    import gateway  # the sanctioned egress; lazy so loop-side imports stay pure

    res = gateway.complete(prompt, caller=CALLER, surface=SURFACE,
                           route=route, by=by, timeout=timeout)
    kept, rejected, note = [], [], None
    if res.get("ok") and res.get("content"):
        kept, rejected = V.ground(d, V.parse_headlines(res["content"]))
        if not kept:
            note = ("inference answered but every headline was refused by the "
                    "grounding guard (no headline could be grounded to the span)")
    else:
        note = res.get("reason") or "inference unavailable"
    return d, kept, rejected, res, note


def render_voiced(d, headlines, mind=None):
    """The deterministic render with a grounded `## ◆ Headlines` section spliced
    in after the title + status line. With no surviving headline it is the plain
    render, byte-for-byte — the degrade path, so the surface never gets *worse*
    than the deterministic floor for trying."""
    body = D.render(d)
    if not headlines:
        return body
    by = f" ({mind})" if mind else ""
    block = ["## ◆ Headlines"]
    block += [f"- {h}" for h in headlines]
    block.append(f"_voiced by local inference{by}; every line grounded to the "
                 "span (loop.digest_voice.ground) — the fold below is the record._")
    block.append("")
    lines = body.split("\n")
    # render() always emits: title, status subline, blank — splice after them.
    return "\n".join(lines[:3] + block + lines[3:])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--today", action="store_true")
    ap.add_argument("--route", default="default")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--by", default="claude")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the bounded prompt only — no inference, no reach")
    ap.add_argument("--json", action="store_true",
                    help="emit {headlines, rejected, mind, note} as a dataset")
    args = ap.parse_args(argv)

    since, until = args.since, args.until
    if args.today:
        since = until = now_ts()[:10]

    if args.dry_run:
        d = D.digest(args.root, since=since, until=until)
        print(V.build_prompt(d))
        print("\nresult: report — the bounded prompt only (no reach)")
        return 0

    d, kept, rejected, res, note = voiced(
        args.root, since=since, until=until, route=args.route,
        timeout=args.timeout, by=args.by)

    if args.json:
        print(json.dumps({"headlines": kept, "rejected": rejected,
                          "mind": res.get("mind"), "note": note},
                         ensure_ascii=False, indent=2))
    else:
        print(render_voiced(d, kept, mind=res.get("mind")))
        print()

    if note:
        print(f"result: report — voiced digest degraded to the deterministic "
              f"floor: {note}")
    else:
        print(f"result: report — voiced digest: {len(kept)} grounded headline(s)"
              + (f", {len(rejected)} refused by the guard" if rejected else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
