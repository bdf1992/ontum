#!/usr/bin/env python3
"""The refusing gate for diagram specs (compose.py format).

Usage:
  python diagrams/qa.py <spec.json>

Was a checklist-runner in the SubProtocol vault; **promoted here to a refusing
gate** in the off-log-gate / mock-shame grain (diagrams/CLAUDE.md, done-line
0139):

  - a spec that fails a refusing check → **exit 2** with the reason(s) on
    **stderr** (a deny is the fail notification, never a silent pass);
  - a clean spec (or one with advisory warnings only) → **exit 0**;
  - an internal error of the gate itself → **fail open (exit 0)**, loudly on
    stderr — a broken gate must never block honest work it cannot parse.

Every refusal cites a principle in `canon.md` **by name** — never
taste-by-assertion (the module's hard rule). The canon is the named SME; this
file is its teeth. Two families of checks:

  - **renderer-fidelity** (carried over from the vault qa.py): a label wider
    than its node, a multi-line label taller than its node, a node off-canvas,
    a subgraph label overflowing its band, a chips band too short, an edge
    routed through an unrelated node (Liang–Barsky), peers squished in a row.
    These keep the drawn artifact legible (graph-drawing aesthetics, dual
    coding).
  - **canon teeth** (added here): a node type outside the closed vocabulary
    (semiotic clarity), more than two accents (perceptual discriminability),
    an unlabeled node (dual coding), an orphan node and an unreachable node
    (graph-drawing aesthetics), more than eight siblings in one
    container/row (graphic economy / complexity management), and an
    invented shape or genre (semantic transparency).

The closed node-type vocabulary is imported from `compose.py` (`NODE_TYPES`),
so the renderer and the gate can never disagree about which types exist (I-4).
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compose import NODE_TYPES, ACCENTS
except Exception:  # pragma: no cover - the gate fails open if its sibling moves
    NODE_TYPES = frozenset(
        {"pill", "rect", "rounded", "dashed", "subroutine", "hex", "rhombus", "chips"}
    )
    ACCENTS = frozenset({"cool", "warm"})

# No genre has earned a canon entry yet (canon.md: "a genre earns its place by
# the §10 test"). Until one does, any `genre` field is invented notation and is
# refused by semantic transparency. A genre lands here the day it lands in the
# canon — never per-diagram.
DECLARED_GENRES: frozenset = frozenset()

# Default-accent treatments compose.py applies when a node carries none, so the
# accent census counts what actually renders, not only what the spec spells out.
TYPE_DEFAULT_ACCENT = {"hex": "cool", "rhombus": "warm"}

MAX_ACCENTS = 2          # perceptual discriminability: the palette is two accents
MAX_SIBLINGS = 8         # complexity management / Miller's 7±2
REACH_HOPS = 4           # graph-drawing: traceable to a hub within four hops

# Font metrics, matching compose.py.
LABEL_PX = 16
TITLE_PX = 18
SUBGRAPH_LABEL_PX = 12
MONO_CHAR_W_AT_16 = 9.6
LINE_HEIGHT_EM = 1.25
NODE_SIDE_PADDING = 8
SQUISH_RATIO = 0.85


def char_width(font_px: int) -> float:
    return MONO_CHAR_W_AT_16 * (font_px / LABEL_PX)


def text_width(text: str, font_px: int = LABEL_PX) -> float:
    return len(text) * char_width(font_px)


def text_height(line_count: int, font_px: int = LABEL_PX) -> float:
    return line_count * font_px * LINE_HEIGHT_EM


def deny(issues, principle, message, ctx):
    issues.append(("error", principle, message, ctx))


def warn(issues, principle, message, ctx):
    issues.append(("warning", principle, message, ctx))


# --- renderer-fidelity checks (carried over, principle-cited) ---

def check_title(spec, issues):
    title = spec.get("title", "")
    if not title:
        return
    width, _ = spec.get("size", [900, 500])
    available = width - 32 - 16  # compose.py hardcodes title at x=32
    needed = text_width(title, TITLE_PX)
    if needed > available:
        deny(issues, "graph-drawing aesthetics (legibility)",
             f"title overflows canvas: needs ~{needed:.0f}px, available {available:.0f}px",
             f"title='{title}'")


def check_node_labels(spec, issues):
    for n in spec.get("nodes", []):
        if n.get("type") == "chips":
            continue  # chips auto-flow; label-fit doesn't apply
        label = str(n.get("label", ""))
        if not label:
            continue  # the empty-label refusal is dual coding's, below
        lines = label.split("\n")
        usable_w = n.get("w", 0) - 2 * NODE_SIDE_PADDING
        for line in lines:
            if text_width(line) > usable_w:
                deny(issues, "dual coding",
                     f"label overflows node width: line='{line}' "
                     f"needs ~{text_width(line):.0f}px, node usable {usable_w:.0f}px",
                     f"node id='{n.get('id')}'")
        usable_h = n.get("h", 0) - 2 * NODE_SIDE_PADDING
        if text_height(len(lines)) > usable_h:
            deny(issues, "dual coding",
                 f"multi-line label overflows node height: "
                 f"needs ~{text_height(len(lines)):.0f}px, node usable {usable_h:.0f}px",
                 f"node id='{n.get('id')}'")


def check_node_in_canvas(spec, issues):
    width, height = spec.get("size", [900, 500])
    for n in spec.get("nodes", []):
        if n["x"] < 0 or n["y"] < 0 or n["x"] + n["w"] > width or n["y"] + n["h"] > height:
            deny(issues, "graph-drawing aesthetics (legibility)",
                 "node extends off-canvas",
                 f"node id='{n.get('id')}' "
                 f"bounds=({n['x']},{n['y']},{n['x']+n['w']},{n['y']+n['h']}) "
                 f"canvas=({width},{height})")


def check_subgraph_rows(spec, issues):
    subgraphs = spec.get("subgraphs", [])
    by_row = {}
    for sg in subgraphs:
        by_row.setdefault(sg["y"], []).append(sg)
    for _, row in by_row.items():
        if len(row) < 2:
            continue
        max_w = max(sg["w"] for sg in row)
        for sg in row:
            if sg["w"] < max_w * SQUISH_RATIO:
                warn(issues, "graph-drawing aesthetics (legibility)",
                     f"subgraph room narrower than peers in same row (squish): "
                     f"w={sg['w']} vs max {max_w}",
                     f"label='{sg.get('label','')}'")


def check_subgraph_labels(spec, issues):
    for sg in spec.get("subgraphs", []):
        label = sg.get("label", "")
        if not label:
            continue
        usable = sg["w"] - 28  # 14px inset each side
        needed = text_width(label, SUBGRAPH_LABEL_PX)
        if needed > usable:
            deny(issues, "dual coding",
                 f"subgraph label overflows room width: "
                 f"needs ~{needed:.0f}px, room usable {usable:.0f}px",
                 f"label='{label}'")


def check_node_in_parent_subgraph(spec, issues):
    subgraphs = spec.get("subgraphs", [])
    for n in spec.get("nodes", []):
        nx1, ny1 = n["x"], n["y"]
        nx2, ny2 = n["x"] + n["w"], n["y"] + n["h"]
        for sg in subgraphs:
            sx1, sy1 = sg["x"], sg["y"]
            sx2, sy2 = sg["x"] + sg["w"], sg["y"] + sg["h"]
            inside = sx1 <= nx1 and sy1 <= ny1 and nx2 <= sx2 and ny2 <= sy2
            partially = not (nx2 <= sx1 or sx2 <= nx1 or ny2 <= sy1 or sy2 <= ny1)
            if partially and not inside:
                warn(issues, "graph-drawing aesthetics (legibility)",
                     "node partially overlaps subgraph room (extends outside)",
                     f"node id='{n.get('id')}' subgraph='{sg.get('label','')}'")


def _segment_crosses_rect(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    """Liang–Barsky-style segment vs. axis-aligned rect test."""
    if (x1 < rx1 and x2 < rx1) or (x1 > rx2 and x2 > rx2):
        return False
    if (y1 < ry1 and y2 < ry1) or (y1 > ry2 and y2 > ry2):
        return False
    if (rx1 <= x1 <= rx2 and ry1 <= y1 <= ry2) or (rx1 <= x2 <= rx2 and ry1 <= y2 <= ry2):
        return True
    dx, dy = x2 - x1, y2 - y1
    candidates = []
    if dy:
        candidates.append(((ry1 - y1) / dy, 'h'))
        candidates.append(((ry2 - y1) / dy, 'h'))
    if dx:
        candidates.append(((rx1 - x1) / dx, 'v'))
        candidates.append(((rx2 - x1) / dx, 'v'))
    for t, axis in candidates:
        if t < 0 or t > 1:
            continue
        ix, iy = x1 + t * dx, y1 + t * dy
        if axis == 'h' and rx1 <= ix <= rx2:
            return True
        if axis == 'v' and ry1 <= iy <= ry2:
            return True
    return False


def check_edges_through_nodes(spec, issues):
    """An edge segment crossing an unrelated node (not its own endpoints) →
    deny. Purchase's finding: crossings are the single largest readability
    cost. The line would lie about the graph's topology."""
    nodes = spec.get("nodes", [])
    nodes_by_id = {n["id"]: n for n in nodes}
    for edge in spec.get("edges", []):
        src_id, tgt_id = edge.get("from"), edge.get("to")
        if src_id not in nodes_by_id or tgt_id not in nodes_by_id:
            continue
        src, tgt = nodes_by_id[src_id], nodes_by_id[tgt_id]
        path = [(src["x"] + src["w"] / 2, src["y"] + src["h"] / 2)]
        for v in edge.get("via", []) or []:
            path.append((v[0], v[1]))
        path.append((tgt["x"] + tgt["w"] / 2, tgt["y"] + tgt["h"] / 2))
        flagged = set()
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            for n in nodes:
                if n["id"] in (src_id, tgt_id) or n["id"] in flagged:
                    continue
                if _segment_crosses_rect(x1, y1, x2, y2,
                                         n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]):
                    deny(issues, "graph-drawing: minimize edge crossings",
                         f"edge passes through unrelated node '{n['id']}' "
                         "— the line lies about the graph's topology",
                         f"edge {src_id}->{tgt_id} (segment {i + 1})")
                    flagged.add(n["id"])


def check_edges_through_label_bands(spec, issues):
    """An edge crossing a subgraph's label band (its reserved top inset) →
    deny: the label-band no-fly rule, born from a real visible collision."""
    nodes_by_id = {n["id"]: n for n in spec.get("nodes", [])}
    BAND_H = 30  # compose.py reserves ~22px for the label; a little headroom
    for edge in spec.get("edges", []):
        src_id, tgt_id = edge.get("from"), edge.get("to")
        if src_id not in nodes_by_id or tgt_id not in nodes_by_id:
            continue
        src, tgt = nodes_by_id[src_id], nodes_by_id[tgt_id]
        path = [(src["x"] + src["w"] / 2, src["y"] + src["h"] / 2)]
        for v in edge.get("via", []) or []:
            path.append((v[0], v[1]))
        path.append((tgt["x"] + tgt["w"] / 2, tgt["y"] + tgt["h"] / 2))
        for sg in spec.get("subgraphs", []):
            if not sg.get("label"):
                continue
            bx1, by1 = sg["x"], sg["y"]
            bx2, by2 = sg["x"] + sg["w"], sg["y"] + BAND_H
            for i in range(len(path) - 1):
                if _segment_crosses_rect(path[i][0], path[i][1],
                                         path[i + 1][0], path[i + 1][1],
                                         bx1, by1, bx2, by2):
                    deny(issues, "graph-drawing: minimize edge crossings",
                         f"edge crosses subgraph label band '{sg.get('label')}'",
                         f"edge {src_id}->{tgt_id}")
                    break


def check_chips_capacity(spec, issues):
    MIN_H = 22 + 2 * 12
    for n in spec.get("nodes", []):
        if n.get("type") != "chips":
            continue
        if n.get("h", 0) < MIN_H:
            deny(issues, "dual coding",
                 f"chips node too short for any chip to render (need h >= {MIN_H}, got {n.get('h', 0)})",
                 f"node id='{n.get('id')}'")


# --- canon teeth (added here) ---

def check_node_types(spec, issues):
    """Semiotic clarity (canon §1): one symbol per concept. A node `type`
    outside the closed vocabulary is a symbol with no concept → deny."""
    for n in spec.get("nodes", []):
        t = n.get("type")
        if t not in NODE_TYPES:
            deny(issues, "semiotic clarity",
                 f"node type '{t}' is not in the declared node-type vocabulary "
                 f"({', '.join(sorted(NODE_TYPES))}) — a symbol with no concept",
                 f"node id='{n.get('id')}'")


def check_accent_count(spec, issues):
    """Perceptual discriminability (canon §2): the palette is two accents;
    kind beyond that is carried by treatment, not a third hue. >2 accents
    actually rendered → deny."""
    used = set()
    for n in spec.get("nodes", []):
        a = n.get("accent") or TYPE_DEFAULT_ACCENT.get(n.get("type"))
        if a:
            used.add(a)
        for it in n.get("items") or []:
            if isinstance(it, dict) and it.get("accent"):
                used.add(it["accent"])
    if len(used) > MAX_ACCENTS:
        deny(issues, "perceptual discriminability",
             f"{len(used)} accent colors used ({', '.join(sorted(used))}); "
             f"the palette is {MAX_ACCENTS} — carry further kind by treatment, not a third hue",
             "diagram-wide")


def check_labels_present(spec, issues):
    """Dual coding (canon §7): text and graphics together. A node with no
    label is graphics without text → deny."""
    for n in spec.get("nodes", []):
        if n.get("type") == "chips":
            if not (n.get("items") or n.get("label")):
                deny(issues, "dual coding",
                     "chips node carries neither items nor label — graphics without text",
                     f"node id='{n.get('id')}'")
            continue
        if not str(n.get("label", "")).strip():
            deny(issues, "dual coding",
                 "node has no label — graphics without text",
                 f"node id='{n.get('id')}'")


def check_orphans_and_reachability(spec, issues):
    """Graph-drawing aesthetics: every node reachable, no orphans.

    - a node in no edge → deny (orphan).
    - a node connected but not traceable to a hub within REACH_HOPS edge-hops
      → deny (reachability / cognitive load). Orphans are excluded here; they
      are already named once by the no-orphans rule.
    """
    nodes = spec.get("nodes", [])
    if not nodes:
        return
    ids = [n["id"] for n in nodes]
    adj = {i: set() for i in ids}
    degree = {i: 0 for i in ids}
    for e in spec.get("edges", []):
        a, b = e.get("from"), e.get("to")
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
            degree[a] += 1
            degree[b] += 1

    orphans = [i for i in ids if degree[i] == 0]
    for i in orphans:
        deny(issues, "graph-drawing: no orphans",
             "orphan node participates in no edge — it claims to belong but is wired to nothing",
             f"node id='{i}'")

    connected = [i for i in ids if degree[i] > 0]
    if not connected:
        return
    # Hubs: explicitly marked, else the max-degree connected node(s).
    marked = [n["id"] for n in nodes if n.get("hub")]
    if marked:
        hubs = set(marked)
    else:
        top = max(degree[i] for i in connected)
        hubs = {i for i in connected if degree[i] == top}

    # BFS undirected from all hubs, bounded to REACH_HOPS hops.
    dist = {h: 0 for h in hubs}
    q = deque(hubs)
    while q:
        cur = q.popleft()
        if dist[cur] >= REACH_HOPS:
            continue
        for nb in adj[cur]:
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                q.append(nb)
    for i in connected:
        if dist.get(i, REACH_HOPS + 1) > REACH_HOPS:
            deny(issues, "graph-drawing: reachability / cognitive load",
                 f"node not traceable to a hub within {REACH_HOPS} edge-hops",
                 f"node id='{i}'")


def check_sibling_count(spec, issues):
    """Graphic economy / complexity management (canon §4, §8): >8 sibling
    nodes in one container/row → deny-with-'split' (Miller's 7±2)."""
    nodes = spec.get("nodes", [])
    subgraphs = spec.get("subgraphs", [])

    def container_of(n):
        nx1, ny1 = n["x"], n["y"]
        nx2, ny2 = n["x"] + n["w"], n["y"] + n["h"]
        for idx, sg in enumerate(subgraphs):
            sx1, sy1 = sg["x"], sg["y"]
            sx2, sy2 = sg["x"] + sg["w"], sg["y"] + sg["h"]
            if sx1 <= nx1 and sy1 <= ny1 and nx2 <= sx2 and ny2 <= sy2:
                return ("subgraph", idx, sg.get("label", f"#{idx}"))
        return ("row", n["y"], f"y={n['y']}")

    groups = {}
    for n in nodes:
        key = container_of(n)
        groups.setdefault(key, []).append(n)
    for (kind, _, label), members in groups.items():
        if len(members) > MAX_SIBLINGS:
            deny(issues, "graphic economy / complexity management",
                 f"{len(members)} sibling nodes in one {kind} (max {MAX_SIBLINGS}) "
                 f"— split into a second diagram or a gated sub-graph",
                 f"{kind} '{label}'")


def check_invented_shapes_genres(spec, issues):
    """Semantic transparency (canon §3): an invented shape or genre with no
    entry in the canon → deny. The format selects a shape via `type`; an
    explicit `shape` field is invented notation, and any `genre` is undeclared
    until one earns a canon entry (the rule that refuses 'membrane
    cross-section' as a reusable genre)."""
    genre = spec.get("genre")
    if genre is not None and genre not in DECLARED_GENRES:
        deny(issues, "semantic transparency",
             f"diagram declares genre '{genre}' with no entry in the canon "
             "— invented notation a reader must memorize",
             "diagram-wide")
    for n in spec.get("nodes", []):
        if "shape" in n:
            deny(issues, "semantic transparency",
                 f"node carries an invented 'shape' field ('{n.get('shape')}') "
                 "— shape is selected by `type` from the closed vocabulary",
                 f"node id='{n.get('id')}'")
        ng = n.get("genre")
        if ng is not None and ng not in DECLARED_GENRES:
            deny(issues, "semantic transparency",
                 f"node declares genre '{ng}' with no entry in the canon",
                 f"node id='{n.get('id')}'")


def check_region_membership(spec, issues):
    """Structural containment (canon: C4 containment / cognitive integration,
    done-line 0151): regions are first-class declared boundaries, and a node
    *belongs* to one by declaration (`node.region == region.id`), not by where
    its rectangle happens to sit. Two ways the declaration can lie:

      - a node declares a region that is not in the diagram's `regions` → deny
        (a boundary that does not exist — the structural analog of an orphan);
      - a node declares a region it is geometrically *outside* → deny (the
        picture claims a containment the layout contradicts).

    A spec with no `regions` and no node `region` is untouched — the rule only
    bites a declaration, so it is backward-compatible (done-line 0151)."""
    declared = {r.get("id"): r for r in spec.get("regions", []) if r.get("id")}
    for n in spec.get("nodes", []):
        r = n.get("region")
        if r is None:
            continue
        if r not in declared:
            deny(issues, "C4 containment / cognitive integration",
                 f"node declares region '{r}' that is not in the diagram's "
                 "`regions` — a boundary that does not exist",
                 f"node id='{n.get('id')}'")
            continue
        reg = declared[r]
        nx1, ny1 = n["x"], n["y"]
        nx2, ny2 = n["x"] + n["w"], n["y"] + n["h"]
        rx1, ry1 = reg["x"], reg["y"]
        rx2, ry2 = reg["x"] + reg["w"], reg["y"] + reg["h"]
        if not (rx1 <= nx1 and ry1 <= ny1 and nx2 <= rx2 and ny2 <= ry2):
            deny(issues, "C4 containment / cognitive integration",
                 f"node declares region '{r}' but its geometry falls outside "
                 "that region's bounds — the picture claims a containment the "
                 "layout contradicts",
                 f"node id='{n.get('id')}'")


CHECKS = [
    # renderer-fidelity
    check_title,
    check_node_labels,
    check_node_in_canvas,
    check_subgraph_rows,
    check_subgraph_labels,
    check_node_in_parent_subgraph,
    check_edges_through_nodes,
    check_edges_through_label_bands,
    check_chips_capacity,
    # canon teeth
    check_node_types,
    check_accent_count,
    check_labels_present,
    check_orphans_and_reachability,
    check_sibling_count,
    check_invented_shapes_genres,
    check_region_membership,
]


def evaluate(spec):
    """Run every check, returning the issue list. Pure — no I/O."""
    issues = []
    for check in CHECKS:
        check(spec, issues)
    return issues


def main(argv=None):
    ap = argparse.ArgumentParser(description="The refusing gate for compose.py JSON specs.")
    ap.add_argument("spec", help="Path to JSON spec file")
    args = ap.parse_args(argv)

    # Fail-open boundary: a gate that cannot even parse its input must not block
    # honest work. Anything inside here that throws → exit 0, loudly on stderr.
    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        issues = evaluate(spec)
    except Exception as exc:  # noqa: BLE001 - fail open by design
        print(f"qa.py: internal error, failing open (not a deny): {exc}", file=sys.stderr)
        return 0

    errors = [i for i in issues if i[0] == "error"]
    warnings = [i for i in issues if i[0] == "warning"]

    if errors:
        print(f"DENY — {args.spec}: {len(errors)} canon violation(s)", file=sys.stderr)
        for _sev, principle, message, ctx in errors:
            print(f"  deny [{principle}] {message}\n        {ctx}", file=sys.stderr)
        if warnings:
            for _sev, principle, message, ctx in warnings:
                print(f"  warn [{principle}] {message}\n        {ctx}", file=sys.stderr)
        return 2

    if warnings:
        print(f"PASS (with {len(warnings)} warning(s)) — {args.spec}")
        for _sev, principle, message, ctx in warnings:
            print(f"  warn [{principle}] {message}")
        return 0

    print(f"PASS — {args.spec}: clean, no canon violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
