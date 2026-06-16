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
import re
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

    superseded = _superseded([p for a in arcs for p in a["pieces"]] + loose)
    divergences = _divergences(fold, arcs, ticks, since, until, superseded)

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


_VERSION_RE = re.compile(r"^(?P<base>.+)\.v(?P<ver>\d+)$")


def _base_version(atom_id):
    """Split an atom id into (base, version): 'atom.field-topology.v3' ->
    ('atom.field-topology', 3). Identity for the pipeline is the content hash
    (reconcile.py); the '.vN' suffix is the human version marker the pipeline
    restarts on. No suffix -> version 0."""
    m = _VERSION_RE.match(atom_id or "")
    if m:
        return m.group("base"), int(m.group("ver"))
    return atom_id, 0


def _superseded(pieces):
    """Atom ids whose refusal is settled history, not a live divergence: a
    *later version of the same atom* reached terminal (landed).

    The doctrine's own rule — editing an atom file makes a new version that
    restarts the pipeline from scratch; old receipts stay valid history but no
    longer apply (reconcile.py, identity-is-content-hash). A confirmed arc that
    harbours a refused piece is the digest's teeth (§10) — but a refusal a newer
    landed version already cleared is not a contradiction bdo must see; surfacing
    it cries wolf (the stale `atom.field-topology.v0` 'missed' that rode every
    digest after v1 landed and loop/field.py shipped, done-line 0078). This
    suppresses only that false *alarm*: the current/highest version's own
    refusal still fires, and the parked/refused counts keep the record."""
    top_landed = {}  # base -> highest landed version
    for p in pieces:
        if p.get("landed"):
            base, ver = _base_version(p.get("atom"))
            if ver > top_landed.get(base, -1):
                top_landed[base] = ver
    return {p.get("atom") for p in pieces
            if top_landed.get(_base_version(p.get("atom"))[0], -1)
            > _base_version(p.get("atom"))[1]}


def _divergences(fold, arcs, ticks, since, until, superseded=frozenset()):
    """Where two locally-fine records refuse to fit — the digest's teeth.

    1. refusal-under-confirmed-arc (§10): bdo confirmed the arc (his standing
       stamp), yet a gate refused a piece under it. Each side is sound on its
       own; the contradiction is what bdo asked to be surfaced richly, not
       carried silently. A refusal a *newer landed version* of the same atom
       already cleared is settled history, not a live divergence (`superseded`);
       it is skipped here so the banner never cries wolf, while the piece's
       refusal still stands in the per-arc counts as honest record.
    2. queue-over-cap: a tick whose human backlog exceeded the cap its own
       setpoint admitted — the cool valve is meant to hold it, so a breach is
       the dial and reality disagreeing.
    """
    out = []
    for arc in arcs:
        if not arc.get("confirmed"):
            continue
        for piece in arc["pieces"]:
            if piece.get("atom") in superseded:
                continue
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


def _glance(text, n=160):
    """One scannable line from a gate's reason — its first sentence, capped.
    The full reason lives in the dataset (`--json`) and on the atom; the
    digest is bdo's glance, not the transcript. The wall-of-prose reason was
    half of why the surface was unreadable (bdo, 2026-06-16)."""
    if not text:
        return "no reason given"
    head = text.strip().split(". ")[0].strip().rstrip(".")
    if len(head) > n:
        head = head[:n - 1].rstrip() + "…"
    return head


def owner_gestures(d):
    """The only things in the dataset that are bdo's *to do*: an unconfirmed
    arc with built work waiting on his standing stamp — confirm-arc unblocks
    its pieces. Everything else the loop carries. A digest that cries 'needs
    you' over session work is the surface bdo refused (2026-06-16): he opens
    it, there is no gesture, the surface lied. So 'your move' is a fold, not a
    paragraph — and it is honestly empty when nothing is on him."""
    return [a for a in d["arcs"]
            if not a.get("confirmed")
            and any(p.get("present") for p in a["pieces"])]


def _arc_line(arc):
    """One arc, collapsed to a glanceable tally line. The arc's full prose
    lives in its epic file and never changes day to day — re-dumping all of it
    every digest was the other half of the unreadability. The mark: ✓
    confirmed, ○ not."""
    mark = "✓" if arc["confirmed"] else "○"
    total = len(arc["pieces"])
    extra = []
    if arc["awaiting"]:
        extra.append(f"{arc['awaiting']} awaiting")
    if arc["parked"]:
        extra.append(f"{arc['parked']} parked")
    if arc["refused"]:
        extra.append(f"{arc['refused']} refused")
    suffix = (" · " + " · ".join(extra)) if extra else ""
    return f"- {mark} `{arc['epic']}` — {arc['landed']}/{total} landed{suffix}"


def render(d):
    """The dataset as a scannable glance — your-move first, then what refuses
    to fit, then the field, then arcs collapsed to one line each.

    The redesign (bdo, 2026-06-16: 'honestly hard to read and make gestures
    about'): the old render led with a paragraph-long divergence under a
    'these need you' banner — over work that was a session's to rebuild, not
    his — and then re-dumped nine full arc descriptions and every atom every
    single day. Two failures: unreadable (volume) and ungesturable (it
    promised a gesture that wasn't there). So: lead with the honest answer to
    'is anything on me?', keep the §10 teeth but terse and ownership-marked,
    and collapse the arcs (their prose is in their epic files)."""
    lines = [f"# Arc digest — {_span_label(d['span'])}", ""]

    # 1. the line bdo opens the digest for: is anything actually his to do?
    gestures = owner_gestures(d)
    if gestures:
        names = ", ".join(f"`{g['epic']}`" for g in gestures)
        lines += [f"**Your move — confirm {len(gestures)} arc(s):** {names}.",
                  "Each has built work waiting on your stamp; close its "
                  "confirm-issue with a yes and the loop lands its pieces.", ""]
    else:
        lines += ["**Your move:** nothing — every arc with live work is "
                  "confirmed; the loop is carrying its pieces.", ""]

    # 2. the §10 teeth: where two locally-fine records refuse to fit. Kept,
    #    but terse and marked with whose move it is — most are the loop's.
    div = d["divergences"]
    if div:
        lines.append(f"## ⚠ Divergences ({len(div)}) — what refuses to fit")
        lines.append("_surfaced for your eyes; the loop carries each unless "
                     "marked **(yours)**._")
        for x in div:
            if x["kind"] == "refusal-under-confirmed-arc":
                lines.append(
                    f"- `{x['atom']}` · `{x['epic']}` → **{x['verdict']}**: "
                    f"{_glance(x.get('reason'))} — a session rebuilds and "
                    f"re-announces.")
            elif x["kind"] == "queue-over-cap":
                lines.append(
                    f"- **queue over cap** at tick {x['tick']}: backlog "
                    f"{x['backlog']} > cap {x['cap']} — re-dial if it recurs "
                    f"**(yours)**.")
        lines.append("")

    # 3. the field, one glance — the dial in play and how it ran
    sp = d["setpoint"]
    f = d["field"]
    dial = (f"`{canon(sp['value'])}` by {sp.get('by')}" if sp
            else "no setpoint admitted (I-8)")
    lines += ["## The field at a glance",
              f"- dial {dial}",
              f"- {f['ticks']} ticks ({f['heat']} heat / {f['cool']} cool), "
              f"{f['budget_spent']} steps, peak backlog {f['peak_backlog']}"]
    if f["deferred_reasons"]:
        why = ", ".join(f"{k}×{v}" for k, v in sorted(f["deferred_reasons"].items()))
        lines.append(f"- deferrals: {why}")
    lines.append("")

    # 4. arcs — collapsed to one tally line each; only a non-quiet arc expands
    #    its live pieces (landed/unbuilt pieces stay folded into the tally).
    lines.append(f"## Arcs ({len(d['arcs'])}) — {d['landings']} landing(s) in span")
    for arc in d["arcs"]:
        lines.append(_arc_line(arc))
        if arc["awaiting"] or arc["parked"] or arc["refused"]:
            for p in arc["pieces"]:
                st = p.get("standing", p.get("state"))
                if st not in ("landed", "unbuilt"):
                    lines.append(f"    - `{p['atom']}` — {st}")
    if d["loose"]:
        lines.append(f"- ○ (no arc) — {len(d['loose'])} loose atom(s)")
        for p in d["loose"]:
            if p.get("standing") not in ("landed", "unbuilt"):
                lines.append(f"    - `{p['atom']}` — {p.get('standing')}")
    lines.append("")
    lines.append(f"_{d['landings']} landing(s), {d['refusals']} refusal(s) "
                 f"in span._")
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
