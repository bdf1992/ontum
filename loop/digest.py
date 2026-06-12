#!/usr/bin/env python3
"""The owner's merge digest (done-line 0032): the data-rich surface bdo
watches *instead of operating the merge*.

bdo: "I no longer wish to be in charge of merging ... instead it should be
getting surfaced much more data-rich information ... based on our setpoints
and skills." This is the move done-line 0028 named and deferred — draining
the *PR* queue, not just the atom queue. Eyes before hands-off: the digest
is the surface he watches from, built before the merge-node (the next
piece) takes his hand off the wheel.

A digest is a pure fold over a span of the log — nothing it shows is a
number kept in memory (D-5). It is read-only, like summon and census: it
counts and names; it never judges, never writes, never stands in for a
node. Verdicts still land only through the one pen (D-4); outward reach
lives only in the reflector pen, never here.

It reads verdicts *generically*, never by stage name: a receipt that
advanced its stage carries a `next_suggested_event`, a refusal carries
none, and a landing is the advance into TERMINAL_EVENT. So the day the
merge-node's `{land, refuse, send_back}` receipts appear on the log, the
digest already speaks them — "landed" turns from the mock's value_confirmed
into merged-to-main for free, because nothing here is spelled out by hand.

The §10 teeth: a *confirmed* arc that harbours a *refused* piece is a
contradiction the digest must NOT smooth over. bdo's standing stamp and a
gate's honest no are each locally fine; together they refuse to fit, and
the digest surfaces that as a named divergence rather than averaging it
away. A clean span shows none — and if it always did, the check would not
be doing its job (§10).

CLI:
  python -m loop.digest                 the merge digest, all-time, read-only
  python -m loop.digest --today         only today's records
  python -m loop.digest --since 2026-06-01 --until 2026-06-10
  python -m loop.digest --json          the raw dataset (machine-readable)

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, TERMINAL_EVENT, Fold, arc_confirmation,
                            atom_state, canon, epic_of, load_atoms, load_epics,
                            now_ts, real_nodes)
from loop.orchestrate import next_action, read_setpoint


def in_span(ts, since, until):
    """A record's date (ts[:10]) within [since, until] inclusive; a None
    bound is unbounded. ISO-8601 dates sort lexically, so string compare is
    the whole test — no clock, no parsing, the fold stays pure."""
    if not ts:
        return False
    day = ts[:10]
    if since and day < since:
        return False
    if until and day > until:
        return False
    return True


def _piece(fold, atom, ahash, real_map, epics, refusals):
    """One arc piece, as it stands now and what it did in span."""
    action = next_action(fold, atom, ahash, real_map, epics=epics)
    if action is None:
        standing = "landed"
    elif action[0] == "await":
        standing = f"awaiting {action[1]}"
    elif action[0] == "parked":
        standing = "parked"
    else:
        standing = f"in-flight ({action[0]}:{action[1]})"
    mine = [rc for rc in refusals if rc.get("artifact_id") == atom["id"]]
    return {
        "atom": atom["id"],
        "present": True,
        "state": atom_state(fold, ahash),
        "standing": standing,
        "awaiting": action[0] == "await" if action else False,
        "parked": action[0] == "parked" if action else False,
        "landed": action is None,
        "refusals": mine,
    }


def digest(root, since=None, until=None):
    """The fold: a span of the log, grouped arc-first (done-line 0006).

    Returns a plain dict — the dataset bdo asked for — that render() turns
    into prose and --json emits verbatim.
    """
    fold = Fold(root)
    atoms = load_atoms(root)
    epics = load_epics(root)
    real_map = real_nodes(fold)
    setpoint = read_setpoint(fold.admissions)

    receipts = [rc for rc in fold.receipts if in_span(rc.get("ts"), since, until)]
    # generic verdict reading: the advance into TERMINAL_EVENT is a landing;
    # a receipt with no next event is a refusal — true for the mock pipeline
    # today and the merge-node's {land, refuse, send_back} the day it lands.
    landings = [rc for rc in receipts if rc.get("next_suggested_event") == TERMINAL_EVENT]
    refusals = [rc for rc in receipts if rc.get("next_suggested_event") is None]

    # attribute every present atom to its arc (or to the loose pile)
    by_epic = {}
    for atom, ahash in atoms:
        epic = epic_of(atom, epics)
        by_epic.setdefault(epic["id"] if epic else None, []).append((atom, ahash))

    arcs = []
    for epic in epics:
        present = {a["id"]: (a, h) for a, h in by_epic.get(epic["id"], [])}
        pieces = []
        for a, h in by_epic.get(epic["id"], []):
            pieces.append(_piece(fold, a, h, real_map, epics, refusals))
        # declared pieces not yet on disk — absence is information (hard rule)
        for decl in epic.get("pieces", []):
            if decl.get("atom") not in present:
                pieces.append({"atom": decl.get("atom"), "present": False,
                               "state": "not-yet-present", "standing": "unbuilt",
                               "glue": decl.get("glue"), "refusals": []})
        confirmation = arc_confirmation(fold, epic["id"])
        arcs.append({
            "epic": epic["id"],
            "arc": epic.get("arc") or epic.get("value"),
            "horizon": epic.get("horizon"),
            "confirmed": confirmation,  # the admission, or None
            "pieces": pieces,
            "landed": sum(1 for p in pieces if p.get("landed")),
            "awaiting": sum(1 for p in pieces if p.get("awaiting")),
            "parked": sum(1 for p in pieces if p.get("parked")),
            "refused": sum(len(p.get("refusals", [])) for p in pieces),
        })

    loose = [_piece(fold, a, h, real_map, epics, refusals)
             for a, h in by_epic.get(None, [])]

    # the field's behaviour over the span, folded from tick records
    ticks = [t for t in fold.admissions
             if t.get("type") == "tick" and in_span(t.get("ts"), since, until)]
    deferred_reasons = Counter(d.get("why") for t in ticks for d in t.get("deferred", []))
    field = {
        "ticks": len(ticks),
        "heat": sum(1 for t in ticks if t.get("mode") == "heat"),
        "cool": sum(1 for t in ticks if t.get("mode") == "cool"),
        "budget_spent": sum(t.get("budget_spent", 0) for t in ticks),
        "deferred": sum(len(t.get("deferred", [])) for t in ticks),
        "deferred_reasons": dict(deferred_reasons),
        "peak_backlog": max((t.get("pressure", {}).get("human_backlog", 0)
                             for t in ticks), default=0),
    }

    divergences = _divergences(fold, arcs, ticks, since, until)

    return {
        "span": {"since": since, "until": until},
        "setpoint": setpoint,
        "field": field,
        "arcs": arcs,
        "loose": loose,
        "landings": len(landings),
        "refusals": len(refusals),
        "divergences": divergences,
    }


def _divergences(fold, arcs, ticks, since, until):
    """Where two locally-fine records refuse to fit — the digest's teeth.

    1. refusal-under-confirmed-arc (§10): bdo confirmed the arc (his standing
       stamp), yet a gate refused a piece under it. Each side is sound on its
       own; the contradiction is what bdo asked to be surfaced richly, not
       carried silently.
    2. queue-over-cap: a tick whose human backlog exceeded the cap its own
       setpoint admitted — the cool valve is meant to hold it, so a breach is
       the dial and reality disagreeing.
    """
    out = []
    for arc in arcs:
        if not arc.get("confirmed"):
            continue
        for piece in arc["pieces"]:
            for rc in piece.get("refusals", []):
                out.append({
                    "kind": "refusal-under-confirmed-arc",
                    "epic": arc["epic"],
                    "atom": piece["atom"],
                    "node": rc.get("node"),
                    "verdict": rc.get("verdict"),
                    "reason": rc.get("reason"),
                    "confirmed_by": arc["confirmed"].get("by"),
                })
    caps = {a["id"]: a.get("value", {}).get("human_queue_cap")
            for a in fold.admissions if a.get("type") == "setpoint"}
    for t in ticks:
        cap = caps.get(t.get("setpoint_id"))
        backlog = t.get("pressure", {}).get("human_backlog")
        if cap is not None and backlog is not None and backlog > cap:
            out.append({"kind": "queue-over-cap", "tick": t.get("tick"),
                        "backlog": backlog, "cap": cap,
                        "setpoint_id": t.get("setpoint_id")})
    return out


def open_count(d):
    """Everything the span leaves open for bdo — the end line's one input.

    The contradiction report 0038 named (done-line 0055): the verdict used to
    sum divergences and *arc* pieces only, so a refusal on an unconfirmed
    arc's piece (which feeds no divergence) or a parked *loose* atom left the
    digest closing `done — clean span: nothing refused` under a span that
    plainly printed refusals. The end line may never claim cleaner than the
    dataset above it: any refusal receipt in span counts, and a loose atom's
    awaiting/parked standing counts exactly as an arc piece's does."""
    return (len(d["divergences"])
            + sum(a["awaiting"] + a["parked"] for a in d["arcs"])
            + sum(1 for p in d["loose"] if p.get("awaiting") or p.get("parked"))
            + d["refusals"])


def _span_label(span):
    since, until = span.get("since"), span.get("until")
    if not since and not until:
        return "all time"
    return f"{since or 'start'} … {until or 'now'}"


def render(d):
    """The dataset as prose, divergences first — they are what needs bdo."""
    lines = ["# Merge digest", f"_span: {_span_label(d['span'])}_", ""]

    div = d["divergences"]
    if div:
        lines.append(f"## ⚠ Divergences ({len(div)}) — these need you")
        for x in div:
            if x["kind"] == "refusal-under-confirmed-arc":
                lines.append(
                    f"- **{x['atom']}** refused under confirmed arc "
                    f"`{x['epic']}` (you confirmed it): {x['node']} → "
                    f"`{x['verdict']}` — {x.get('reason') or 'no reason given'}")
            elif x["kind"] == "queue-over-cap":
                lines.append(
                    f"- **queue over cap** at tick {x['tick']}: backlog "
                    f"{x['backlog']} > cap {x['cap']} ({x['setpoint_id']})")
        lines.append("")
    else:
        lines += ["## Divergences", "_none — every confirmed arc's pieces fit, "
                  "the cap held_", ""]

    sp = d["setpoint"]
    lines.append("## Dials in play")
    if sp:
        lines.append(f"- setpoint `{sp['id']}` by {sp.get('by')}: "
                     f"`{canon(sp['value'])}`")
    else:
        lines.append("- no setpoint admitted (I-8: the dial is an admitted "
                     "record, not a default)")
    f = d["field"]
    lines.append(f"- field: {f['ticks']} ticks ({f['heat']} heat / {f['cool']} "
                 f"cool), {f['budget_spent']} steps spent, {f['deferred']} "
                 f"deferred, peak backlog {f['peak_backlog']}")
    if f["deferred_reasons"]:
        why = ", ".join(f"{k}×{v}" for k, v in sorted(f["deferred_reasons"].items()))
        lines.append(f"  - deferrals: {why}")
    lines.append("")

    lines.append(f"## Arcs ({len(d['arcs'])})")
    for arc in d["arcs"]:
        mark = (f"confirmed by {arc['confirmed'].get('by')}"
                if arc["confirmed"] else "unconfirmed")
        lines.append(f"\n### {arc['epic']} — {mark}")
        if arc.get("arc"):
            lines.append(f"_{arc['arc']}_")
        lines.append(f"- {arc['landed']} landed · {arc['awaiting']} awaiting · "
                     f"{arc['parked']} parked · {arc['refused']} refused")
        for p in arc["pieces"]:
            lines.append(f"  - `{p['atom']}` — {p.get('standing', p.get('state'))}")
    if d["loose"]:
        lines.append(f"\n### (no arc) — {len(d['loose'])} loose atom(s)")
        for p in d["loose"]:
            lines.append(f"  - `{p['atom']}` — {p.get('standing')}")
    lines.append("")
    lines.append(f"_{d['landings']} landing(s), {d['refusals']} refusal(s) "
                 f"in span_")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--since", help="inclusive lower date bound, YYYY-MM-DD")
    ap.add_argument("--until", help="inclusive upper date bound, YYYY-MM-DD")
    ap.add_argument("--today", action="store_true",
                    help="only today's records (UTC); the only place a clock is read")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    since, until = args.since, args.until
    if args.today:
        since = until = now_ts()[:10]

    d = digest(args.root, since=since, until=until)
    if args.json:
        print(canon(d))
    else:
        print(render(d))
        print()
    # a divergence, a refusal in span, or anything still open — arc piece or
    # loose atom — is a report bdo should read; only a span that saw none of
    # it is done. Read-only either way (D-6).
    if open_count(d):
        print(f"result: report — {len(d['divergences'])} divergence(s), "
              f"{d['refusals']} refusal(s) in span; the surface is yours to read (D-4)")
    else:
        print("result: done — clean span: nothing refused, nothing awaiting you")
    return 0


if __name__ == "__main__":
    sys.exit(main())
