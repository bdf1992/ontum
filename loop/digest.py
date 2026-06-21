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

# A merge-node `landed` verdict is the terminal act but carries no next event;
# read it as a landing, not a refusal (retro fold 0098 surfaced the inflation).
LANDING_VERDICTS = frozenset({"landed"})

# How many landings the span narrates piece-by-piece before folding the rest
# into the trailer count. The digest is bdo's glance, not the full merge log —
# but the overflow is always *named*, never silently dropped (loop/'s law: a
# bounded surface that hides what it cut reads as "covered everything").
LANDING_NARRATIVE_CAP = 15


def _is_landing(rc):
    """A receipt that advanced the work to terminal — the explicit advance into
    TERMINAL_EVENT, or a `landed` verdict (terminal by nature, no next event)."""
    return (rc.get("next_suggested_event") == TERMINAL_EVENT
            or rc.get("verdict") in LANDING_VERDICTS)


def _is_refusal(rc):
    """A receipt that did not advance and is not a landing — a real pushed-back
    verdict. A landing is never a refusal, and a receipt carrying no verdict
    refused nothing (so neither merge landings nor verdict-less records count)."""
    return (rc.get("next_suggested_event") is None
            and not _is_landing(rc)
            and bool(rc.get("verdict")))


def _landing_line(rc):
    """One landing receipt as a narrative record — *what* reached terminal,
    named from whatever the receipt already carries. A merge-node receipt names
    its PR, branch, arc and the atoms it carried (the rich D-13 write-through);
    an in-pipeline terminal advance names its atom and the node that advanced
    it. Read generically off the receipt's own fields (never spelled out by
    stage), so a future landing shape narrates the day its receipts land — the
    same property that lets `_is_landing` already speak the merge-node's verbs."""
    atoms = rc.get("landed_atoms")
    if not atoms:
        atoms = [rc["artifact_id"]] if rc.get("artifact_id") else []
    return {
        "atoms": atoms,
        "pr": rc.get("pr"),
        "head": rc.get("head"),
        "epic": rc.get("epic"),
        "by": rc.get("pr_author") or rc.get("node"),
        "verdict": rc.get("verdict"),
        "ts": rc.get("ts"),
    }


def atoms_on_main(fold):
    """The per-atom↔per-PR join, read from the log alone (D-13): the set of
    artifact_ids a merge receipt records as having reached main via its
    `landed_atoms`. This is the reading half of the write-through carbon copy —
    the answer to "did atom X reach main?" that the pre-D-13 merge receipt could
    not give (it recorded only *that* a PR landed, never *which* atoms, so the
    two namespaces could not join — the terminal-pull gateway's namespace gap,
    done-line 0123). A `landed` receipt with no `landed_atoms` is lossy history
    (the 90 pre-D-13 merges) and contributes nothing here — it cannot, honestly,
    name an atom it never carried. Pure fold; no git, no network."""
    on_main = set()
    for rc in fold.receipts:
        if rc.get("verdict") in LANDING_VERDICTS:
            on_main.update(rc.get("landed_atoms") or [])
    return on_main


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
    # generic verdict reading (corrected, retro fold 0098): a landing is the
    # advance into TERMINAL_EVENT OR a `landed` verdict (which carries no next
    # event — it IS terminal); a refusal is a non-advancing, non-landing verdict.
    # The old "no next event == refusal" counted all 77 merge landings as
    # refusals (the 58-where-~7-were-real inflation retro surfaced).
    landings = [rc for rc in receipts if _is_landing(rc)]
    refusals = [rc for rc in receipts if _is_refusal(rc)]
    # the span's narrative, not just its tally: each landing named (PR, atoms,
    # arc, who), most-recent-first so the story leads with the latest. The bare
    # count never told bdo *which* work reached main — the thing the span exists
    # to carry (bdo: the digest must support more of the narrative that unfolded).
    landed_in_span = [_landing_line(rc) for rc in
                      sorted(landings, key=lambda r: r.get("ts") or "", reverse=True)]

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
    for arc in arcs:
        for piece in arc["pieces"]:
            if piece.get("atom") in superseded:
                piece["superseded"] = True
                piece["standing"] = "superseded history"
        _refresh_arc_counts(arc)
    for piece in loose:
        if piece.get("atom") in superseded:
            piece["superseded"] = True
            piece["standing"] = "superseded history"
    divergences = _divergences(fold, arcs, ticks, since, until, superseded)

    # the prose stream — phrasing-lane edits in span, so the light lane (done-line
    # 0117) is visible here and bdo is never blind to it (his correction, 2026-06-18)
    phrasing_in_span = [
        {"id": a.get("id"), "by": a.get("by"), "reason": a.get("reason"),
         "files": [f.get("path") for f in a.get("files", [])]}
        for a in fold.admissions
        if a.get("type") == "phrasing" and in_span(a.get("ts"), since, until)
    ]

    return {
        "span": {"since": since, "until": until},
        "setpoint": setpoint,
        "field": field,
        "arcs": arcs,
        "loose": loose,
        "landings": len(landings),
        "landed_in_span": landed_in_span,
        "refusals": len(refusals),
        "divergences": divergences,
        "phrasing": phrasing_in_span,
        # the per-atom↔per-PR join (D-13): which atoms a merge receipt confirms
        # reached main. All-time, not span — "on main" is a standing fact, not a
        # window. Empty until the first post-D-13 land carries its atoms.
        "atoms_on_main": sorted(atoms_on_main(fold)),
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


def _is_live_piece(piece):
    return (not piece.get("superseded")
            and piece.get("standing") not in ("landed", "unbuilt",
                                              "superseded history"))


def _refresh_arc_counts(arc):
    pieces = [p for p in arc["pieces"] if not p.get("superseded")]
    arc["total"] = len(pieces)
    arc["landed"] = sum(1 for p in pieces if p.get("landed"))
    arc["awaiting"] = sum(1 for p in pieces if p.get("awaiting"))
    arc["parked"] = sum(1 for p in pieces if p.get("parked"))
    arc["refused"] = sum(len(p.get("refusals", [])) for p in pieces)
    arc["history"] = sum(1 for p in arc["pieces"] if p.get("superseded"))
    return arc


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
            + sum(1 for p in d["loose"] if _is_live_piece(p))
            + d["refusals"])


def _span_label(span):
    since, until = span.get("since"), span.get("until")
    if not since and not until:
        return "all time"
    if since and since == until:
        return since
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


def _bar(landed, total, width=10):
    """A progress bar for an arc — the patch-notes glance at how far it has
    come (▰ done, ▱ to go). Pure from the counts; an empty arc reads all-empty
    and never divides by zero. Restrained block glyphs, not a coloured emoji —
    the repo's own quiet vocabulary (bdo: 'not emoji like that but close')."""
    if not total:
        return "▱" * width
    filled = max(0, min(width, round(landed / total * width)))
    return "▰" * filled + "▱" * (width - filled)


def _arc_line(arc):
    """One arc, collapsed to a glanceable tally line with a progress bar. The
    arc's full prose lives in its epic file and never changes day to day —
    re-dumping all of it every digest was half of the unreadability. The mark:
    ✓ confirmed, ○ not; the bar is the patch-notes 'how far along' at a glance."""
    mark = "✓" if arc["confirmed"] else "○"
    total = arc.get("total", len(arc["pieces"]))
    extra = []
    if arc["awaiting"]:
        extra.append(f"{arc['awaiting']} awaiting")
    if arc["parked"]:
        extra.append(f"{arc['parked']} parked")
    if arc["refused"]:
        extra.append(f"{arc['refused']} refused")
    if arc.get("history"):
        extra.append(f"{arc['history']} history")
    suffix = (" · " + " · ".join(extra)) if extra else ""
    return (f"- {mark} `{arc['epic']}` {_bar(arc['landed'], total)} "
            f"{arc['landed']}/{total} landed{suffix}")


def _loose_live(d):
    return [p for p in d["loose"] if _is_live_piece(p)]


def render(d):
    """The dataset as patch notes — readable cold, sectioned, with progress
    bars, calls-to-action, and a place to weigh in.

    bdo (2026-06-21, issue #410): the digest was 'boring to read and hard for
    reading cold' and should be 'more inspired by great patch notes' — PoE /
    Warframe / LoL / Destiny — and 'interactive with CTAs and places for me to
    comment on'. So this keeps everything the 2026-06-16 redesign won (lead with
    the honest answer to 'is anything on me?'; the §10 teeth terse and
    ownership-marked; the arcs collapsed, their prose left in their epic files)
    and layers the patch-notes grammar on top: a TL;DR status line, themed
    sections, a progress bar per arc, a tickable CTA on each thing that is
    actually a move, and a `▸ your note:` anchor where bdo replies.

    Strictly deterministic — every word here is a fact the fold already
    computed (atom ids, arc horizons, gate reasons, counts). No editorial
    voice is invented; that flavour layer is a *separate* bounded inference
    narration over this same dataset (loop/digest_voice.py + the digest-voice
    pen), grounded by a guard, never the pure fold writing prose it cannot
    ground (the digest stays truth; reach lives elsewhere)."""
    lines = [f"# Ontum Field Notes — {_span_label(d['span'])}"]

    # the TL;DR status line — the patch-notes headline AND the honest answer to
    # 'is anything on me?' in one glance (gesture-first, the rule bdo won).
    gestures = owner_gestures(d)
    on_you = (f"{len(gestures)} arc(s) waiting on you" if gestures
              else "nothing waiting on you")
    on_main = d.get("atoms_on_main", [])
    lines += [f"_{d['landings']} landed · {d['refusals']} refused · "
              f"{len(on_main)} on main · {on_you}_", ""]

    # 1. → Your call — the only thing here that is bdo's to do, as a tickable
    #    CTA with the exact verb and a `▸ your note:` anchor to reply on.
    if gestures:
        lines.append(f"## → Your call ({len(gestures)})")
        for g in gestures:
            built = sum(1 for p in g["pieces"] if p.get("present"))
            lines.append(
                f"- [ ] **Confirm `{g['epic']}`** → "
                f"`loop.node confirm-arc --epic {g['epic']} --by bdo` "
                f"(or close its confirm-issue with a yes) — lands its "
                f"{built} built piece(s)")
            if g.get("horizon"):
                lines.append(f"    ↳ horizon: _{_glance(g['horizon'])}_")
        lines += ["  ▸ _your note:_", ""]
    else:
        loose = _loose_live(d)
        if loose:
            lines += ["## → Your call",
                      f"**Your call:** nothing on you — every arc with live "
                      f"work is confirmed; {len(loose)} loose atom(s) are "
                      "outside an arc and need a session to route or retire "
                      "them.", ""]
        else:
            lines += ["## → Your call",
                      "**Your call:** nothing — every arc with live work is "
                      "confirmed; the loop is carrying its pieces.", ""]

    # 2. ⚠ Frictions — the §10 teeth (the patch-notes 'Known Issues'): where two
    #    locally-fine records refuse to fit, terse, marked with whose move it is.
    div = d["divergences"]
    if div:
        lines.append(f"## ⚠ Frictions ({len(div)}) — what refuses to fit")
        lines.append("_the loop carries each unless marked **(yours)**._")
        for x in div:
            if x["kind"] == "refusal-under-confirmed-arc":
                lines.append(
                    f"- `{x['atom']}` · `{x['epic']}` → **{x['verdict']}**")
                lines.append(f"    ↳ _why:_ {_glance(x.get('reason'))} — a "
                             "session rebuilds and re-announces.")
            elif x["kind"] == "queue-over-cap":
                lines.append(
                    f"- **queue over cap** at tick {x['tick']}: backlog "
                    f"{x['backlog']} > cap {x['cap']} — re-dial if it recurs "
                    f"**(yours)**.")
        lines += ["  ▸ _your note:_", ""]

    # 3. ▰ Shipped — what reached terminal, most-recent first (the marquee),
    #    capped, the overflow always *named* (loop/'s law); each line carries
    #    its PR so the count is honest and the cut is never silent.
    landed = d.get("landed_in_span", [])
    if landed:
        lines.append(f"## ▰ Shipped ({len(landed)})")
        for ev in landed[:LANDING_NARRATIVE_CAP]:
            atoms = ", ".join(f"`{a}`" for a in ev["atoms"]) or "_(no atom named)_"
            pr = f"PR #{ev['pr']} — " if ev.get("pr") else ""
            where = f" · `{ev['epic']}`" if ev.get("epic") else ""
            by = f" — {ev['by']}" if ev.get("by") else ""
            lines.append(f"- {pr}{atoms}{where}{by}")
        overflow = len(landed) - LANDING_NARRATIVE_CAP
        if overflow > 0:
            lines.append(f"- _…+{overflow} earlier landing(s) in span, folded "
                         "into the arc bars below_")
        lines.append("")

    # 4. Arcs — a progress bar and tally per arc; only a non-quiet arc expands
    #    its live pieces (landed/unbuilt pieces stay folded into the bar).
    lines.append(f"## Arcs ({len(d['arcs'])}) — {d['landings']} landing(s) in span")
    for arc in d["arcs"]:
        lines.append(_arc_line(arc))
        if arc["awaiting"] or arc["parked"] or arc["refused"]:
            for p in arc["pieces"]:
                st = p.get("standing", p.get("state"))
                if st not in ("landed", "unbuilt", "superseded history"):
                    lines.append(f"    - `{p['atom']}` — {st}")
    if d["loose"]:
        lines.append(f"- ○ (no arc) — {len(d['loose'])} loose atom(s)")
        for p in d["loose"]:
            if p.get("standing") not in ("landed", "unbuilt",
                                         "superseded history"):
                lines.append(f"    - `{p['atom']}` — {p.get('standing')}")
    lines.append("")

    # 5. ◉ Tuning — the field and the dial in play (the patch-notes 'balance
    #    changes'), with a CTA to re-dial and a place to weigh in.
    sp = d["setpoint"]
    f = d["field"]
    dial = (f"`{canon(sp['value'])}` by {sp.get('by')}" if sp
            else "no setpoint admitted (I-8)")
    lines += ["## ◉ Tuning (the field)",
              f"- **dial:** {dial}",
              f"- {f['ticks']} ticks ({f['heat']} heat / {f['cool']} cool), "
              f"{f['budget_spent']} steps, peak backlog {f['peak_backlog']}"]
    if f["deferred_reasons"]:
        why = ", ".join(f"{k}×{v}" for k, v in sorted(f["deferred_reasons"].items()))
        lines.append(f"- _most-deferred:_ {why}")
    lines += ["- [ ] **Re-dial?** → `loop.orchestrate --admit-setpoint "
              "'{…}' --by bdo` if the deferral mix looks wrong",
              "  ▸ _your note:_", ""]

    # 6. ✎ Light lane — the phrasing-lane edits, so you are never blind to it.
    ph = d.get("phrasing", [])
    if ph:
        lines.append(f"## ✎ Light lane ({len(ph)}) — prose edits, no atom")
        for e in ph:
            files = ", ".join(f"`{p}`" for p in e["files"])
            lines.append(f"- {_glance(e.get('reason'))} — by {e.get('by')} "
                         f"({files})")
        lines.append("")

    lines.append(f"_{d['landings']} landing(s), {d['refusals']} refusal(s) "
                 f"in span._")
    if on_main:
        lines.append(f"_{len(on_main)} atom(s) confirmed on main (D-13 join)._")
    lines.append("_Reply on any ▸ line or tick a CTA box to weigh in; the loop "
                 "reads your stamps, not your prose (D-4)._")
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
    opens = open_count(d)
    if opens:
        print(f"result: report — {len(d['divergences'])} divergence(s), "
              f"{d['refusals']} refusal(s), {opens} open item(s) in span; "
              "the surface is yours to read (D-4)")
    else:
        print("result: done — clean span: nothing refused, nothing awaiting you")
    return 0


if __name__ == "__main__":
    sys.exit(main())
