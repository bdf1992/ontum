#!/usr/bin/env python3
"""loop/brief.py — the bdo-brief node (done-line 0104).

bdo, 2026-06-17: "Can we stop putting things on me?" A "what's on you" list is
still a queue, just politely worded. This node is the structural fix — it sits
where work would otherwise land on him and re-renders it into the shape he
asked for, so the shape stops depending on a session's discipline.

Two zoom levels, one node:

  over bulk (the default)  — it FOLDS: a digest of the aggregate shape, grouped
                             by arc, with "the few that need your read" named.
                             N pieces under one arc become ONE group, never N
                             rows — a digest, not a flood in a nicer font.
  drill in (`--item <id>`) — the item's INFERENCE CONSTRUCT: the considered
                             context (each line cited to a real record), the
                             recommendation it produced and the reasoning, and
                             the one divergence seam — the judgment the fold
                             cannot make and bdo can. A peer's argument to set
                             beside his own read, never a ticket.

It COMPOSES the owner-item folds that already exist; it never re-folds them.
`orchestrate.next_action` already returns None for a settled/discharged atom
and a loop-owned step (seed/derive/judge — e.g. a confirmed arc's piece the
loop carries), so a satisfied or arc-covered item never reaches bdo here: the
discharged-ask teeth are inherited, not re-implemented (the rule "verify a
handed-off ask before surfacing it" made mechanical).

Read-only — a fold, like census/gaps/digest. Writes nothing, stdlib only, ends
with `done | report | needs-you`.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, arc_confirmation, epic_of,
                            load_atoms, load_epics, real_nodes)
from loop.orchestrate import HUMAN_NODE, next_action

UNFILED = "~unfiled"


# --------------------------------------------------------------- the pure folds
# Small pure functions, testable without a live pipeline (the gaps.py grain).

def classify_owner_items(actions, human):
    """Keep only what is genuinely bdo's, from `[(atom, ahash, action)]`.

    An `await` on his stamp, or a `parked` piece, is his. A None action
    (settled/discharged) or a loop-owned step (`seed`/`derive`/`judge` — a
    confirmed arc's pieces the loop carries) is dropped: it is not on him.
    The discharged-ask teeth, as a pure filter."""
    out = []
    for atom, ahash, action in actions:
        if action is None:
            continue
        kind, target = action
        if kind == "await" and target == human:
            out.append((atom, ahash, "stamp"))
        elif kind == "parked":
            out.append((atom, ahash, "parked"))
    return out


def receipts_for(fold, ahash):
    """The receipts on the log for this atom version, in order."""
    return [r for r in fold.receipts if r.get("artifact_hash") == ahash]


def considered_context(atom, ahash, fold):
    """The context the fold actually weighed, as `(point, cite)` pairs — each
    citing a real record (the atom file, or a receipt id). This is the
    consideration shown first-hand, not a synopsis."""
    aid = atom["id"]
    out = []
    briefing = atom.get("briefing", {}) or {}
    if briefing.get("headline"):
        out.append((briefing["headline"], f"atom:{aid}"))
    if briefing.get("value"):
        out.append((f"value — {briefing['value']}", f"atom:{aid}"))
    if briefing.get("why_now"):
        out.append((f"why now — {briefing['why_now']}", f"atom:{aid}"))
    story = (atom.get("story") or {}).get("text")
    if story:
        out.append((f"story — {story}", f"atom:{aid}"))
    for rc in receipts_for(fold, ahash):
        verdict = rc.get("verdict", "?")
        reason = rc.get("reason", "")
        out.append((f"{rc.get('node', '?')} judged {verdict} — {reason}",
                    rc.get("id", "rcp.?")))
    return out


def recommendation_for(atom, ahash, fold, epics):
    """Derive a recommendation from the records (verdicts + arc state), with the
    reasoning shown and a citation list. Deterministic in v0 — the inference
    plane enriching this is a later slot. The cites are what the teeth check:
    a recommendation grounded in nothing resolvable is refused downstream."""
    aid = atom["id"]
    rcs = receipts_for(fold, ahash)
    epic = epic_of(atom, epics)
    epic_id = epic["id"] if epic else None

    # a held refusal (a gate said no and suggested no next step) → bdo's to
    # amend or retire (D-4)
    held = [r for r in rcs if r.get("next_suggested_event") is None
            and r.get("verdict") not in (None, "accept", "confirmed")]
    if held:
        r = held[-1]
        return {
            "text": f"hold — amend or retire {aid}; do not stamp it as is",
            "reasoning": (f"{r.get('node')} refused this version "
                          f"({r.get('verdict')}: {r.get('reason')}); a refusal "
                          "is yours to amend or retire, not to wave through (D-4)"),
            "cites": [r.get("id", "rcp.?")],
        }

    accepts = [r for r in rcs if r.get("verdict") in ("accept", "confirmed")]
    if accepts and epic_id and not arc_confirmation(fold, epic_id):
        r = accepts[-1]
        return {
            "text": f"confirm the arc {epic_id} — one stamp clears this piece "
                    "and every other under it",
            "reasoning": (f"the value is judged sound ({r.get('node')}: "
                          f"{r.get('verdict')}); the only thing holding it is "
                          f"your stamp at arc scale, and {epic_id} is not yet "
                          "confirmed (done-line 0028)"),
            "cites": [r.get("id", "rcp.?"), epic_id],
        }
    if accepts:
        r = accepts[-1]
        return {
            "text": f"stamp {aid} — its value is judged sound",
            "reasoning": (f"{r.get('node')} accepted it ({r.get('verdict')}: "
                          f"{r.get('reason')}); nothing else holds it"),
            "cites": [r.get("id", "rcp.?")],
        }
    # no verdict on the record yet — the honest absence (no fabricated rec)
    return {
        "text": f"not ready for you — {aid} carries no verdict yet",
        "reasoning": "no gate has judged this version; it is the loop's to "
                     "advance before it is yours",
        "cites": [],
    }


def resolvable(cite, fold, epics, atom_ids):
    """A citation resolves when it points at a record that exists: a receipt
    id, an epic id, or an `atom:<id>` for an atom on disk."""
    if cite in {r.get("id") for r in fold.receipts}:
        return True
    if cite in {e.get("id") for e in epics}:
        return True
    if cite.startswith("atom:") and cite[5:] in atom_ids:
        return True
    return False


def uncited(recommendation, fold, epics, atom_ids):
    """The teeth (causality/term_economy grain — no evidence, no mint): a
    recommendation whose cites resolve to nothing is refused as confident.
    True means 'do not present this as grounded'."""
    cites = recommendation.get("cites") or []
    return not any(resolvable(c, fold, epics, atom_ids) for c in cites)


def group_by_arc(items, epics):
    """Fold the owner-items into arc groups (the aggregation): every piece
    under one epic collapses to one group, so the over-bulk surface is a
    digest, not a 1:1 echo. Returns `[(epic_id, epic_or_None, [items])]`,
    unfiled last."""
    buckets = {}
    for item in items:
        epic = epic_of(item["atom"], epics)
        key = epic["id"] if epic else UNFILED
        buckets.setdefault(key, {"epic": epic, "items": []})
        buckets[key]["items"].append(item)
    ordered = sorted(buckets.items(), key=lambda kv: (kv[0] == UNFILED, kv[0]))
    return [(k, v["epic"], v["items"]) for k, v in ordered]


# ----------------------------------------------------------------- the assembly

def build_items(root):
    """Compose the live owner-items from the existing folds — never re-folding
    them. Each item carries its considered context, its recommendation, and
    whether that recommendation is grounded (the teeth)."""
    fold = Fold(root)
    epics = load_epics(root)
    atoms = load_atoms(root)
    atom_ids = {a["id"] for a, _ in atoms}
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)

    actions = [(atom, ahash, next_action(fold, atom, ahash, real_map, epics))
               for atom, ahash in atoms]
    selected = classify_owner_items(actions, human)

    items = []
    for atom, ahash, kind in selected:
        rec = recommendation_for(atom, ahash, fold, epics)
        items.append({
            "id": atom["id"],
            "atom": atom,
            "ahash": ahash,
            "kind": kind,
            "considered": considered_context(atom, ahash, fold),
            "recommendation": rec,
            "uncited": uncited(rec, fold, epics, atom_ids),
            "divergence": _divergence(kind),
        })
    return items, human, fold, epics


def _divergence(kind):
    if kind == "parked":
        return ("A gate refused this; whether to amend it or retire it is a "
                "direction call only you can make (D-4).")
    return ("The fold judged the value sound; what it cannot judge is whether "
            "this is the right direction for the arc — that is your read.")


# ----------------------------------------------------------------- the surfaces

def render_digest(items, epics):
    """Over bulk: the gesture-first glance. Lead with the honest answer to
    'is anything on me?', then the aggregated arc groups — the few that need
    your read — never one row per piece."""
    if not items:
        print("Nothing needs your read — the loop is carrying everything that "
              "is the loop's to carry.")
        print("\nresult: done — nothing on you")
        return 0

    groups = group_by_arc(items, epics)
    print(f"{len(items)} item(s) need your read, across {len(groups)} arc(s):\n")
    for epic_id, epic, group in groups:
        head = f"== {epic_id}"
        if epic and epic.get("value"):
            head += f" — {epic['value']}"
        if epic_id != UNFILED:
            head += " · CONFIRMED" if epic and _confirmed(epic) else " · not yet confirmed"
        print(head)
        # one arc-level recommendation, then the pieces folded under it
        recs = {it["recommendation"]["text"] for it in group if not it["uncited"]}
        for text in sorted(recs):
            print(f"   recommend: {text}")
        for it in group:
            flag = "  [uncited — not grounded]" if it["uncited"] else ""
            print(f"     · {it['id']} ({it['kind']}){flag} — drill in: "
                  f"python -m loop.brief --item {it['id']}")
        print()
    print(f"result: report — {len(items)} need your read across {len(groups)} "
          "arc(s); drill into any one for the full argument")
    return 0


def _confirmed(epic):
    # cheap re-check from the epic's own folded state when present; the digest
    # marks confirmation only as orientation — the construct cites the record.
    return bool(epic.get("_confirmed"))


def _clip(text, n=260):
    """Keep the construct tight — bdo wants the context considered, not a ton
    of it. The line carries its citation; the full record is one lookup away."""
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render_brief(item):
    """Drill in: the inference construct for one item — the consideration shown
    first-hand, the recommendation it produced, and the divergence seam to
    compare against your own read."""
    print(f"{item['id']} — {item['kind']}\n")
    print("CONSIDERED (each line cites a record; read it for the full text):")
    for point, cite in item["considered"]:
        print(f"  · {_clip(point)}  [{cite}]")
    rec = item["recommendation"]
    print("\nRECOMMENDATION:")
    if item["uncited"]:
        print(f"  (uncited — refused as grounded: {_clip(rec['text'])})")
        print("  the cites resolve to no record on the log; treat this as a "
              "question, not an argument")
    else:
        print(f"  {_clip(rec['text'])}")
        print(f"  because: {_clip(rec['reasoning'])}")
        print(f"  cites: {', '.join(rec['cites'])}")
    print("\nWHERE WE MIGHT DIFFER (the shared space):")
    print(f"  {item['divergence']}")
    print("\nresult: report — one construct, to set beside your own read")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--item", help="drill into one item's inference construct")
    ap.add_argument("--json", action="store_true", help="emit the dataset")
    args = ap.parse_args(argv)

    items, human, fold, epics = build_items(args.root)
    # mark confirmation for the digest's orientation line (the construct still
    # cites the record itself, not this flag)
    for _, epic, group in group_by_arc(items, epics):
        if epic:
            epic["_confirmed"] = arc_confirmation(fold, epic["id"]) is not None

    if args.json:
        payload = [{k: v for k, v in it.items() if k != "atom"} for it in items]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.item:
        for it in items:
            if it["id"] == args.item:
                return render_brief(it)
        print(f"result: needs-you — no open item {args.item!r} on your desk "
              "(it may already be settled — the loop drops what is discharged)")
        return 0
    return render_digest(items, epics)


if __name__ == "__main__":
    sys.exit(main())
