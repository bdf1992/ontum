#!/usr/bin/env python3
"""The consequence graph - v0 (done-line 0167): the auditable tier-1 plane.

A foreign peer-architect reviewed the consequence-graph + mark-to-market
proposal (envoy package consequence-graph) and returned GO for the
smallest real piece: a read-only fold that materializes the tier-1
consequence-graph PLANE from the log, folds cited marks onto it, runs one
bounded decaying propagation pass, and REFUSES any mark whose citation
does not resolve. bdo confirmed the arc (epic.consequence-graph-response).
This is that piece.

The plane is NOT the whole consequence memory - it is the auditable
projection of it (the reviewer's correction). Like every surface in the
repo it is a FOLD over the append-only log (loop.reconcile.Fold), never a
second source of truth: nodes are subjects already on the record, edges
are literal log facts (tier 1 only - no inferred causal edges), marks
cite the log record that minted them, and propagation is bounded so a
signal that reached everywhere (and so meant nothing) cannot form.

What makes it a CONSEQUENCE view and not a prettier provenance view:
cited consequence nodes - a changed state distinct from the work-unit,
carried by the repair signal a healed bite leaves and by declared
consequence.observed log events. Provenance says what touched what; this
says what was minted, where the signal travels, and what must now be seen.

Edges are directional and propagation flows along that direction (receipt
-> the atom it judged; a consequence -> the work it is of; a version ->
its base; a version -> its arc). Two hard rules keep the signal from
smearing (the reviewer's): authored_by/judged_by edges render but carry
decay 0.0 (an actor is a sink - no super-spreader through --by), and an
arc receives aggregation but never fans back out to its sibling pieces.
Channels (drag, repair) stay separate and never net across type - a thing
can be loved and broken.

The section-10 tooth (tests/test_consequence_graph.py, non-vacuous): a
mark or consequence whose citation does not resolve against the log is
REFUSED and listed as a gap - the term-economy ghost refusal, here on
marks. The test proves it bites a real bad citation, that drag propagates
with decay but never crosses an actor hub or to an arc sibling, and that
two runs are byte-identical.

Out of scope (done-line 0167, named not invented away): tier-2 inferred
edges, exemplar/value marks and the money gesture, the consequence volume
/ generated faces, and any actuation. Read-only, witness before actuator.

CLI:
  python -m loop.consequence_graph            the plane, prose, read-only
  python -m loop.consequence_graph --json     the raw dataset (deterministic)
  python -m loop.consequence_graph --root <p> fold an alternate .ai-native

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, canon, load_epics
from loop.digest import _base_version
from loop.heal import ADVANCING_VERDICTS, NEGATING_VERDICTS


# --- the propagation law: the reviewer's table; the bound that keeps signal ---

RADIUS = 2
THRESHOLD = 0.20
# per-edge-kind decay applied per hop; 0.0 = renders but never propagates.
DECAY = {
    "consequence_of": 0.85,
    "finding_for": 0.80,
    "receipt_for": 0.75,
    "version_of": 0.70,
    "member_of_arc": 0.35,
    "judged_by": 0.00,
    "authored_by": 0.00,
}
# v0 channels - failure(drag) and repair only; exemplar/value deferred (0167).
V0_CHANNELS = ("drag", "repair")
# a mark may not flow OUT of these node kinds: an actor is a sink (no super-
# spreader through --by); an arc receives aggregation but never fans to siblings.
NO_FANOUT_KINDS = {"actor", "arc"}


def _node(nid, kind, label, source, record_id):
    return {"id": nid, "kind": kind, "label": label,
            "ref": {"source": source, "record_id": record_id}}


def _mark(mid, mtype, channel, target, weight, record_id, contains, reason):
    return {"id": mid, "type": mtype, "channel": channel, "target": target,
            "weight": weight, "reason": reason,
            "citation": {"source": "log", "record_id": record_id,
                         "contains": contains}}


def build(root):
    """Fold the tier-1 plane: nodes, edges, cited marks, gaps, and one
    bounded decaying propagation pass. Pure and deterministic for a given
    log - the property the test pins."""
    fold = Fold(root)
    epics = load_epics(root)

    # every log record by id, for citation resolution (the section-10 tooth).
    record_text = {}
    for rec in fold.events + fold.receipts + fold.admissions:
        rid = rec.get("id")
        if rid:
            record_text[rid] = canon(rec)

    def resolves(record_id, contains=None):
        """A citation resolves when its record exists on the log and, if a
        contains substring is named, that record actually carries it - the
        ghost-in-spirit guard. The term-economy tooth, on marks."""
        if not record_id or record_id not in record_text:
            return False
        return not contains or contains in record_text[record_id]

    nodes, edges = {}, {}
    marks, gaps = [], []

    def add_node(n):
        nodes.setdefault(n["id"], n)

    def add_edge(frm, to, kind, semantics, record_id):
        eid = f"edge:{kind}:{frm}=>{to}"
        edges.setdefault(eid, {
            "id": eid, "from": frm, "to": to, "kind": kind, "tier": "real",
            "semantics": semantics,
            "ref": {"source": "log", "record_id": record_id}})

    # --- atoms, version lineage, authorship (from atom.created) ---
    hash_to_version = {}
    for ev in fold.events:
        if ev.get("type") != "atom.created":
            continue
        aid = ev.get("artifact_id")
        evid = ev.get("id")
        if not aid:
            continue
        base, _ = _base_version(aid)
        vid = f"atom_version:{aid}"
        bid = f"atom_base:{base}"
        add_node(_node(vid, "atom_version", aid, "log", evid))
        add_node(_node(bid, "atom_base", base, "log", evid))
        add_edge(vid, bid, "version_of", "lineage", evid)
        if ev.get("artifact_hash"):
            hash_to_version[ev["artifact_hash"]] = vid
        actor = ev.get("from_node")
        if actor:
            anode = f"actor:{actor}"
            add_node(_node(anode, "actor", actor, "log", evid))
            add_edge(vid, anode, "authored_by", "authorship", evid)

    # --- arcs and membership (from the epic files; arcs are file-truth) ---
    for epic in epics:
        eid = epic["id"]
        arcid = f"arc:{eid}"
        add_node(_node(arcid, "arc", eid, "epic", eid))
        for piece in epic.get("pieces", []):
            pa = piece.get("atom")
            vid = f"atom_version:{pa}"
            if vid in nodes:
                add_edge(vid, arcid, "member_of_arc", "containment", eid)

    # --- receipts: nodes, judged_by, receipt_for, and FAILURE (drag) marks ---
    for rc in fold.receipts:
        rid = rc.get("id")
        if not rid:
            continue
        verdict = rc.get("verdict")
        vid = hash_to_version.get(rc.get("artifact_hash"))
        rnode = f"receipt:{rid}"
        label = verdict or rc.get("kind") or "receipt"
        add_node(_node(rnode, "receipt", label, "log", rid))
        if vid:
            add_edge(rnode, vid, "receipt_for", "judgment", rid)
        node = rc.get("node")
        if node:
            anode = f"actor:{node}"
            add_node(_node(anode, "actor", node, "log", rid))
            add_edge(rnode, anode, "judged_by", "authorship", rid)
        if verdict in NEGATING_VERDICTS and vid:
            if resolves(rid, verdict):
                marks.append(_mark(f"mark:failure:{rid}", "failure", "drag",
                                   vid, 1.0, rid, verdict,
                                   f"negating verdict {verdict}"))
            else:
                gaps.append({"id": f"gap:failure:{rid}",
                             "reason": "citation does not resolve (ghost)",
                             "citation": rid})

    # --- repair: a healed bite is a CONSEQUENCE node (a changed state) ---
    # a base negated on an old version and advanced on a strictly newer one.
    by_base = defaultdict(list)
    for rc in fold.receipts:
        vid = hash_to_version.get(rc.get("artifact_hash"))
        if not vid:
            continue
        aid = vid.split("atom_version:", 1)[1]
        base, ver = _base_version(aid)
        by_base[base].append((ver, rc.get("verdict"), rc.get("id"), vid))
    for base in sorted(by_base):
        rows = by_base[base]
        neg = [r for r in rows if r[1] in NEGATING_VERDICTS]
        adv = [r for r in rows if r[1] in ADVANCING_VERDICTS]
        if not neg or not adv:
            continue
        min_neg = min(r[0] for r in neg)
        later = [r for r in adv if r[0] > min_neg]
        if not later:
            continue
        ver, verdict, rid, vid = max(later, key=lambda r: r[0])
        if not resolves(rid, verdict):
            gaps.append({"id": f"gap:repair:{base}",
                         "reason": "citation does not resolve (ghost)",
                         "citation": rid})
            continue
        cnode = f"consequence:bite-healed:{base}"
        add_node(_node(cnode, "consequence", f"bite healed on {base}",
                       "log", rid))
        add_edge(cnode, vid, "consequence_of", "consequence", rid)
        marks.append(_mark(f"mark:repair:{base}", "repair", "repair", cnode,
                           1.0, rid, verdict,
                           "healed bite: negated then advanced"))

    # --- declared consequence.observed: cited consequence nodes (the tooth) ---
    for ev in fold.events:
        if ev.get("type") != "consequence.observed":
            continue
        cid = ev.get("id")
        target = ev.get("target")
        channel = ev.get("channel", "drag")
        cite = ev.get("citation") or {}
        rec_id = cite.get("record_id")
        contains = cite.get("contains")
        gid = f"gap:consequence:{cid}"
        clabel = ev.get("label", "observed consequence")
        if channel not in V0_CHANNELS:
            gaps.append({"id": gid,
                         "reason": f"channel {channel!r} not a v0 channel",
                         "citation": rec_id})
            continue
        if not resolves(rec_id, contains):
            gaps.append({"id": gid,
                         "reason": "citation does not resolve (ghost)",
                         "citation": rec_id})
            continue
        if target not in nodes:
            gaps.append({"id": gid,
                         "reason": f"target {target!r} is not a node on the plane",
                         "citation": rec_id})
            continue
        cnode = f"consequence:{cid}"
        add_node(_node(cnode, "consequence", clabel, "log", rec_id))
        add_edge(cnode, target, "consequence_of", "consequence", rec_id)
        marks.append(_mark(f"mark:consequence:{cid}", "observed", channel,
                           cnode, 1.0, rec_id, contains, clabel))

    field = _propagate(marks, edges, nodes)

    return {
        "view": "consequence-graph-v0",
        "mode": "read_only",
        "tier": "tier_1_real_edges_only",
        "nodes": sorted(nodes.values(), key=lambda n: n["id"]),
        "edges": sorted(edges.values(), key=lambda e: e["id"]),
        "marks": sorted(marks, key=lambda m: m["id"]),
        "gaps": sorted(gaps, key=lambda g: g["id"]),
        "field": [{"channel": ch, "node": n, "weight": round(w, 6)}
                  for ch in sorted(field)
                  for n, w in sorted(field[ch].items())],
        "scanned": {"events": len(fold.events), "receipts": len(fold.receipts),
                    "admissions": len(fold.admissions), "epics": len(epics),
                    "nodes": len(nodes), "edges": len(edges),
                    "marks": len(marks), "gaps": len(gaps)},
    }


def _propagate(marks, edges, nodes):
    """One bounded, typed, decaying pass per mark (BFS to RADIUS, cut at
    THRESHOLD). Strongest path wins per node per mark; same-channel
    contributions sum; channels never mix. An actor or arc node receives a
    contribution but never fans it onward (the no-smear rule)."""
    adj = defaultdict(list)
    for e in edges.values():
        adj[e["from"]].append((e["to"], e["kind"]))
    field = defaultdict(lambda: defaultdict(float))
    for m in marks:
        ch = m["channel"]
        start = m["target"]
        best = {}
        queue = [(start, m["weight"], 0)]
        while queue:
            node, w, depth = queue.pop(0)
            if node != start and w < THRESHOLD:
                continue
            if node in best and best[node] >= w:
                continue
            best[node] = w
            if depth >= RADIUS:
                continue
            kind = nodes.get(node, {}).get("kind")
            if depth > 0 and kind in NO_FANOUT_KINDS:
                continue  # arc/actor receive, never fan onward
            for to, ekind in adj.get(node, []):
                nw = w * DECAY.get(ekind, 0.0)
                if nw >= THRESHOLD:
                    queue.append((to, nw, depth + 1))
        for node, w in best.items():
            field[ch][node] += w
    return field


def render(out):
    """The owner/developer prose surface - the plane as a glance."""
    s = out["scanned"]
    head = (f"Folded {s['events']} events, {s['receipts']} receipts, "
            f"{s['epics']} epics into {s['nodes']} nodes / {s['edges']} edges.")
    tally = f"{s['marks']} cited mark(s), {s['gaps']} refused citation(s)."
    lines = ["# Consequence graph - v0 (read-only tier-1 plane)", "",
             head, tally, ""]
    by_ch = defaultdict(list)
    for row in out["field"]:
        by_ch[row["channel"]].append((row["node"], row["weight"]))
    for ch in ("drag", "repair"):
        rows = by_ch.get(ch, [])
        title = "Drag field (failure)" if ch == "drag" else "Repair field"
        lines += [f"## {title}", ""]
        if not rows:
            lines += ["    (none)", ""]
            continue
        for node, w in sorted(rows, key=lambda r: (-r[1], r[0])):
            lines.append(f"    {w:6.3f}  {node}")
        lines.append("")
    lines += ["## Refused citations (ghosts - named, never placed)", ""]
    if not out["gaps"]:
        lines += ["    (none - every citation resolves)", ""]
    else:
        for g in out["gaps"]:
            lines.append(f"    {g['id']}: {g['reason']} (cite: {g.get('citation')})")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="consequence_graph.py",
        description="The consequence graph v0 - the auditable tier-1 plane.")
    ap.add_argument("--json", action="store_true",
                    help="emit the deterministic dataset instead of prose")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="the .ai-native root to fold (default: .ai-native)")
    ns = ap.parse_args(argv)
    out = build(ns.root)
    if ns.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(render(out))
    n = len(out["gaps"])
    if n:
        print(f"\nresult: report - {n} refused citation(s) (ghosts); the plane "
              "stands, the ghosts named, never placed (the section-10 tooth bit)")
    else:
        print(f"\nresult: done - the tier-1 plane folded: {len(out['nodes'])} "
              f"nodes, {len(out['marks'])} cited marks, read-only")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
