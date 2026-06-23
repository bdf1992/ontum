#!/usr/bin/env python3
"""loop/section.py — named sections of the ledger (the work queues).

bdo (2026-06-21): a tender should be "free to work over a **named section** of
the log/ledger and surface work to close" — "a **process for their workflow
which consumes work**." This module is the producer half of that: a *section*
is a named, bounded slice of the loop's incomplete flow — a fold over the log
that yields the OPEN work items in one slice, plus how an item in it is closed.
The tender (the workflow, `.claude/workflows/tend.js`) is the consumer: granted
a section by name, it works the items and surfaces/closes them.

The shape is producer/consumer over the log (the same level-triggered grain as
reflect.py's pub/sub): the log produces work, the section names and folds it,
the consumer drains it. A section never holds state — it re-derives its open
set from the log every call, so a consumed item simply stops appearing.

No second truth (§10): every section COMPOSES an existing fold —
`reconcile` (the value-confirm queue), `heal` (stale parks), `gaps` (the gap
backlog), `owner_asks` (parked owner-asks). It re-derives nothing and writes
nothing. The consuming — the inference, the actual close — lives in the tender,
never here; this is the read-only queue it works.

Stdlib only; local-first; the loop/ law. `list` names the sections and their
open counts; `items --name <n>` folds one section's open work items. Ends with
a clear result line (D-6): done | report | needs-you.
"""

import argparse
import json
import sys
from pathlib import Path

from loop import gaps as gaps_mod
from loop import heal as heal_mod
from loop import owner_asks as oa_mod
from loop import reconcile
from loop.reconcile import DEFAULT_ROOT


def value_confirm_items(root):
    """The value-confirm clog: atoms that earned a value-gate accept and now
    sit at `value_accepted` awaiting the independent `value_confirmed` (D-2's
    second set of eyes). Composed from the reconcile fold, never re-derived."""
    fold = reconcile.Fold(root)
    out = []
    for atom, artifact_hash in reconcile.load_atoms(root):
        state = reconcile.atom_state(fold, artifact_hash)
        if state == "value_accepted" and atom.get("desired_state") == "value_confirmed":
            out.append({
                "id": atom["id"],
                "summary": f"{atom['id']} is value_accepted — awaiting an "
                           "independent value-confirm review (D-2)",
                "artifact_hash": artifact_hash,
            })
    return out


def stale_park_items(root):
    """Heal's stale parks: a healed bite still surfaced as an open refusal.
    Composed from heal.stale_park_findings — the same fold loop.heal renders."""
    fold = reconcile.Fold(root)
    return [{"id": f["subject"], "summary": f"{f['subject']}: {f['move']}"}
            for f in heal_mod.stale_park_findings(fold)]


def gap_items(root):
    """The gap backlog in pressure order, composed from gaps.gaps — the harness-
    generated work the idle default is meant to pick up."""
    return [{"id": f"{g['kind']}:{g['subject']}",
             "summary": f"{g['kind']} — {g['subject']}: {g['why']}",
             "move": g["move"]}
            for g in gaps_mod.gaps(root)]


def owner_ask_items(root):
    """The items parked on bdo, flattened from owner_asks.owner_ask_groups —
    one work item per parked ask, keyed to its report so a consumer can join
    back to the mirror that surfaces it."""
    out = []
    for grp in oa_mod.owner_ask_groups(root):
        for i, ask in enumerate(grp["asks"], 1):
            out.append({
                "id": f"{grp['report_id']}#{i}",
                "summary": ask,
                "report_id": grp["report_id"],
            })
    return out


# The registry: a section is a name → (one-line nature, how its work is closed,
# the fold that yields its open items). Closing is the consumer's act; the
# `closes_via` line tells the consumer which paved path advances/ends an item.
SECTIONS = {
    "value-confirm": {
        "description": "atoms at value_accepted awaiting the independent value-confirm review (the clog)",
        "closes_via": "fire a real, independent review — `python -m loop.heartbeat --drain-limit N` (the gate rail)",
        "items": value_confirm_items,
    },
    "stale-park": {
        "description": "healed bites still surfaced as open refusals on the owner views",
        "closes_via": "confirm no owner surface (inbox/digest) still shows the refusal; the fix at the source is the heal cut (D-4)",
        "items": stale_park_items,
    },
    "gaps": {
        "description": "the pressure-ordered gap backlog the harness generates",
        "closes_via": "exercise the part through the working system, or make the cited case that its silence is by design",
        "items": gap_items,
    },
    "owner-asks": {
        "description": "items parked on bdo in report needs-you sections, mirrored to GitHub",
        "closes_via": "resolve the item (cite the proof) and close the mirror through the issue pen, or shape it for bdo",
    },
}
SECTIONS["owner-asks"]["items"] = owner_ask_items


def section_items(root, name):
    """The open work items in one named section. Raises KeyError on an unknown
    name — a section is a named contract, not a free-text query."""
    if name not in SECTIONS:
        raise KeyError(name)
    return SECTIONS[name]["items"](root)


def overview(root):
    """Every section with its open-item count — the work-queue census. A
    failing fold is reported as an error count, never a crash (one broken
    section must not blind the rest)."""
    rows = []
    for name, spec in SECTIONS.items():
        try:
            n = len(spec["items"](root))
            rows.append({"name": name, "open": n, "description": spec["description"],
                         "closes_via": spec["closes_via"]})
        except Exception as e:  # noqa: BLE001 — a broken section is a finding, not a stop
            rows.append({"name": name, "open": None, "error": str(e),
                         "description": spec["description"]})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    sub = ap.add_subparsers(dest="cmd")

    lp = sub.add_parser("list", help="the named sections and their open counts")
    lp.add_argument("--json", action="store_true", help="emit the raw dataset")

    ip = sub.add_parser("items", help="the open work items in one named section")
    ip.add_argument("--name", required=True, help=f"one of: {', '.join(SECTIONS)}")
    ip.add_argument("--json", action="store_true", help="emit the raw dataset")

    args = ap.parse_args(argv)
    cmd = args.cmd or "list"

    if cmd == "items":
        if args.name not in SECTIONS:
            print(f"result: needs-you — no section named '{args.name}'; the "
                  f"named sections are: {', '.join(SECTIONS)}")
            return 2
        items = section_items(args.root, args.name)
        if args.json:
            print(json.dumps({"section": args.name, "items": items}, ensure_ascii=False))
        else:
            spec = SECTIONS[args.name]
            print(f"# section: {args.name} — {spec['description']}")
            print(f"_closes via: {spec['closes_via']}_\n")
            for it in items:
                print(f"- {it['id']}: {it['summary']}")
            verb = "report" if items else "done"
            tail = "" if items else " — the queue is empty"
            print(f"\nresult: {verb} — {len(items)} open item(s) in "
                  f"section '{args.name}'{tail}")
        return 0

    rows = overview(args.root)
    if args.json:
        print(json.dumps({"sections": rows}, ensure_ascii=False))
        return 0
    print("# named sections of the ledger — the work queues\n")
    total = 0
    for r in rows:
        if r.get("open") is None:
            print(f"- {r['name']}: ERROR ({r.get('error')}) — {r['description']}")
            continue
        total += r["open"]
        print(f"- {r['name']}: {r['open']} open — {r['description']}")
    print(f"\nresult: report — {len(rows)} named section(s), {total} open work "
          "item(s); a tender consumes one section at a time (loop.section "
          "items --name <n>)")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
