#!/usr/bin/env python3
"""Compose an SVG diagram from a JSON spec — the deterministic floor.

Usage:
  python diagrams/compose.py <spec.json> [--out OUTPUT.svg]

Reads a JSON spec describing nodes, subgraphs, and edges; emits a self-contained
dark-theme SVG with halftone fills, accent strokes, and monospace labels.

Ported faithfully from the SubProtocol vault (`_theme/svg/compose.py`) into its
ontum home. Two laws the port preserves (diagrams/CLAUDE.md):

  - **Explicit-position, not auto-layout.** Every node carries its own
    `x`/`y`/`w`/`h`; nothing here computes a layout. That is what keeps the
    SVG diff-stable — one node added is one diff — the `.ai-native`
    byte-deterministic grain.
  - **Byte-deterministic.** The same spec renders byte-identical SVG on every
    run: no `datetime`, no `random`, no iteration over unordered structures
    (only the spec's own ordered `nodes`/`edges`/`subgraphs` lists). The §10
    test in `tests/test_diagram.py` pins this as bytes.

Palette and the closed node-type vocabulary track `palette.md`; the gate
(`qa.py`) imports `NODE_TYPES` from here so the renderer and the gate can never
disagree about which types exist (I-4).
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from html import escape

PALETTE = {
    "surface":        "#0B0B0C",
    "surface_raised": "#141416",
    "halftone_bg":    "#0F1011",
    "halftone_dot":   "#1F2123",
    "text":           "#E6E6E6",
    "muted":          "#8C8C8F",
    "stroke":         "#3A3A3D",
    "stroke_active":  "#5C5C60",
    "cool":           "#5EB7A1",
    "warm":           "#C97A55",
}

# The two accents the palette declares. The gate refuses a diagram that uses a
# third (perceptual discriminability); kind beyond two accents is carried by
# treatment, not a third hue.
ACCENTS = frozenset({"cool", "warm"})

FONT_STACK = (
    '"JetBrains Mono", "IBM Plex Mono", "Berkeley Mono", '
    'ui-monospace, "Cascadia Code", "Fira Code", monospace'
)

LABEL_SIZE = 16
TITLE_SIZE = 18
EDGE_LABEL_SIZE = 14
CAPTION_SIZE = 12       # the foot caption's mono size
CAPTION_LINE_H = 15     # 1.25em line height at 12px
CAPTION_LEFT_X = 32     # caption left edge (compose hardcodes the title/caption gutter)
CAPTION_RIGHT_MARGIN = 8  # right breathing room before the frame edge
CAPTION_BASELINE_INSET = 18  # the last line's baseline above the frame foot
MONO_CHAR_W = 9.6  # rough per-char width at 16px monospace


def defs() -> str:
    p = PALETTE
    return f"""<defs>
  <pattern id="halftone" x="0" y="0" width="5" height="5" patternUnits="userSpaceOnUse">
    <rect width="5" height="5" fill="{p['halftone_bg']}"/>
    <circle cx="1" cy="1" r="0.6" fill="{p['halftone_dot']}"/>
  </pattern>
  <filter id="glow-cool" x="-50%" y="-50%" width="200%" height="200%">
    <feDropShadow dx="0" dy="0" stdDeviation="2.6" flood-color="{p['cool']}" flood-opacity="0.6"/>
  </filter>
  <filter id="glow-warm" x="-50%" y="-50%" width="200%" height="200%">
    <feDropShadow dx="0" dy="0" stdDeviation="2.6" flood-color="{p['warm']}" flood-opacity="0.6"/>
  </filter>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="{p['stroke_active']}"/>
  </marker>
</defs>"""


def accent_stroke(node: dict, default: str = PALETTE["stroke"]) -> str:
    a = node.get("accent")
    if a == "cool": return PALETTE["cool"]
    if a == "warm": return PALETTE["warm"]
    return default


def accent_filter_attr(node: dict, default_accent: str | None = None) -> str:
    a = node.get("accent", default_accent)
    if a == "cool": return ' filter="url(#glow-cool)"'
    if a == "warm": return ' filter="url(#glow-warm)"'
    return ""


def label_text(node: dict, cx: float, cy: float, color: str | None = None,
               size: int = LABEL_SIZE) -> str:
    color = color or PALETTE["text"]
    raw = str(node.get("label", ""))
    lines = raw.split("\n")
    n = len(lines)
    line_h = 1.25  # em
    spans = []
    for i, line in enumerate(lines):
        if i == 0:
            dy = f"{-((n - 1) * line_h) / 2:.2f}em"
        else:
            dy = f"{line_h}em"
        spans.append(f'<tspan x="{cx}" dy="{dy}">{escape(line)}</tspan>')
    return (
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="central" '
        f"font-family='{FONT_STACK}' font-size=\"{size}\" fill=\"{color}\">"
        f'{"".join(spans)}</text>'
    )


def render_pill(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    rx = h / 2
    stroke = accent_stroke(node)
    sw = 1.5 if node.get("accent") else 1
    fil = accent_filter_attr(node)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="url(#halftone)" stroke="{stroke}" stroke-width="{sw}"{fil}/>',
        label_text(node, cx, cy),
    ])


def render_rect(node, rx: int = 4):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    stroke = accent_stroke(node)
    sw = 1.5 if node.get("accent") else 1
    fil = accent_filter_attr(node)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="url(#halftone)" stroke="{stroke}" stroke-width="{sw}"{fil}/>',
        label_text(node, cx, cy),
    ])


def render_rounded(node):
    return render_rect(node, rx=14)


def render_dashed(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    stroke = accent_stroke(node)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" '
        f'fill="url(#halftone)" stroke="{stroke}" stroke-width="1" stroke-dasharray="4 3"/>',
        label_text(node, cx, cy),
    ])


def render_subroutine(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    stroke = accent_stroke(node)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" ry="2" '
        f'fill="url(#halftone)" stroke="{stroke}" stroke-width="1"/>',
        f'<line x1="{x + 8}" y1="{y}" x2="{x + 8}" y2="{y + h}" '
        f'stroke="{stroke}" stroke-width="1"/>',
        f'<line x1="{x + w - 8}" y1="{y}" x2="{x + w - 8}" y2="{y + h}" '
        f'stroke="{stroke}" stroke-width="1"/>',
        label_text(node, cx, cy),
    ])


def render_hex(node):
    """Hexagon — defaults to cool accent (tool/primitive)."""
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    inset = min(h * 0.28, w * 0.18)
    if "accent" not in node:
        node = {**node, "accent": "cool"}
    stroke = accent_stroke(node)
    fil = accent_filter_attr(node)
    pts = [
        (x + inset, y),
        (x + w - inset, y),
        (x + w, y + h / 2),
        (x + w - inset, y + h),
        (x + inset, y + h),
        (x, y + h / 2),
    ]
    pts_str = " ".join(f"{px},{py}" for px, py in pts)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<polygon points="{pts_str}" fill="url(#halftone)" stroke="{stroke}" stroke-width="1.5"{fil}/>',
        label_text(node, cx, cy),
    ])


def render_rhombus(node):
    """Rhombus — defaults to warm accent (trigger)."""
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    if "accent" not in node:
        node = {**node, "accent": "warm"}
    stroke = accent_stroke(node)
    fil = accent_filter_attr(node)
    pts = [
        (x + w / 2, y),
        (x + w, y + h / 2),
        (x + w / 2, y + h),
        (x, y + h / 2),
    ]
    pts_str = " ".join(f"{px},{py}" for px, py in pts)
    cx, cy = x + w / 2, y + h / 2
    return "\n".join([
        f'<polygon points="{pts_str}" fill="url(#halftone)" stroke="{stroke}" stroke-width="1.5"{fil}/>',
        label_text(node, cx, cy),
    ])


def render_chips(node):
    """A list of small chips, auto-flowed within the node's bounds.

    Items come from the `items` array, or from a comma-separated `label`. Each
    item can be a plain string (neutral) or a dict `{"label": str, "accent": str}`
    where accent is "cool", "warm", or omitted (neutral). A node-level `accent`
    field applies to all items that don't override.

    Per-item accent enables color grouping for cross-cutting buckets — pair with
    a small legend chips node so the colors decode. Stay within the palette: cool,
    warm, neutral. Three groups maximum.

    Chips flow left-to-right and wrap. If vertical space runs out, the last
    visible chip is replaced with a dashed "+ N more" indicator.
    """
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    raw_items = list(node.get("items") or [])
    if not raw_items and node.get("label"):
        raw_items = [s.strip() for s in str(node["label"]).split(",") if s.strip()]

    default_accent = node.get("accent")
    items = []
    for it in raw_items:
        if isinstance(it, dict):
            items.append({"label": str(it.get("label", "")), "accent": it.get("accent")})
        else:
            items.append({"label": str(it), "accent": None})

    chip_h = 22
    chip_padx = 8
    chip_font = 12
    chip_char_w = MONO_CHAR_W * (chip_font / LABEL_SIZE)
    row_gap = 5
    col_gap = 5
    inner_pad = 12

    inner_x0 = x + inner_pad
    inner_y0 = y + inner_pad
    inner_x1 = x + w - inner_pad
    inner_y1 = y + h - inner_pad

    def chip_w(text):
        return len(text) * chip_char_w + 2 * chip_padx

    def stroke_for(accent):
        if accent == "cool": return PALETTE["cool"]
        if accent == "warm": return PALETTE["warm"]
        return PALETTE["stroke"]

    placements = []
    cx, cy = inner_x0, inner_y0
    for item in items:
        cw = chip_w(item["label"])
        if cx + cw > inner_x1 and cx > inner_x0:
            cx = inner_x0
            cy += chip_h + row_gap
        if cy + chip_h > inner_y1:
            break
        placements.append((cx, cy, item, False))
        cx += cw + col_gap

    skipped = len(items) - len(placements)
    if skipped > 0 and placements:
        last_cx, last_cy, _, _ = placements[-1]
        placements[-1] = (last_cx, last_cy, {"label": f"+ {skipped + 1} more", "accent": None}, True)

    parts = []
    for cx_p, cy_p, item, is_more in placements:
        accent = item.get("accent") if not is_more else None
        if not accent:
            accent = default_accent
        stroke = stroke_for(accent)
        sw = 1.5 if accent in ("cool", "warm") else 1
        dash = ' stroke-dasharray="3 2"' if is_more else ""
        text_color = PALETTE["muted"] if is_more else PALETTE["text"]
        cw = chip_w(item["label"])
        parts.append(
            f'<rect x="{cx_p:.1f}" y="{cy_p:.1f}" width="{cw:.1f}" height="{chip_h}" '
            f'rx="3" ry="3" fill="url(#halftone)" stroke="{stroke}" stroke-width="{sw}"{dash}/>'
        )
        tx = cx_p + cw / 2
        ty = cy_p + chip_h / 2
        parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" dominant-baseline="central" '
            f"font-family='{FONT_STACK}' font-size=\"{chip_font}\" fill=\"{text_color}\">"
            f'{escape(item["label"])}</text>'
        )
    return "\n".join(parts)


NODE_RENDERERS = {
    "pill":       render_pill,
    "rect":       render_rect,
    "rounded":    render_rounded,
    "dashed":     render_dashed,
    "subroutine": render_subroutine,
    "hex":        render_hex,
    "rhombus":    render_rhombus,
    "chips":      render_chips,
}

# The closed node-type vocabulary (palette.md / graphic economy). The gate
# imports this so a node whose `type` is outside the set is refused at one
# place, never two drifting lists (I-4).
NODE_TYPES = frozenset(NODE_RENDERERS)


def render_subgraph_fill(sg: dict) -> str:
    """Halftone fill rect only — drawn at the back so edges can pass over it."""
    x, y, w, h = sg["x"], sg["y"], sg["w"], sg["h"]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" '
        f'fill="url(#halftone)" stroke="none"/>'
    )


def render_subgraph_frame(sg: dict) -> str:
    """Border stroke + label — drawn at the front so frames stay continuous."""
    x, y, w, h = sg["x"], sg["y"], sg["w"], sg["h"]
    label = sg.get("label", "")
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" '
        f'fill="none" stroke="{PALETTE["stroke"]}" stroke-width="1"/>'
    ]
    if label:
        # Subgraph labels render as type-stamps: uppercased + letter-spaced muted
        # mono, so they read as deliberate section headers rather than as
        # truncated sentences. Width math must match qa.py's label-band check.
        parts.append(
            f'<text x="{x + 14}" y="{y + 22}" text-anchor="start" '
            f"font-family='{FONT_STACK}' font-size=\"12\" fill=\"{PALETTE['muted']}\" "
            f'letter-spacing="1.2">'
            f'{escape(label.upper())}</text>'
        )
    return "\n".join(parts)


def caption_char_w() -> float:
    """Per-char advance of the 12px caption mono, derived from the 16px base
    metric so the caption tracks the same font assumption as every other
    width check (MONO_CHAR_W * 12/16 = 7.2px)."""
    return MONO_CHAR_W * (CAPTION_SIZE / LABEL_SIZE)


def wrap_caption(text: str, width_px: float) -> list[str]:
    """Word-wrap `text` to fit `width_px` at the 12px caption mono metric.

    Pure and byte-deterministic: a greedy wrap on spaces, hard-breaking any
    single word longer than a full line. This is the **one** wrap definition
    (I-4): `render_caption` here and `qa.check_caption` both import it, so the
    renderer and the gate can never disagree about how many lines a caption
    becomes — the gate counts exactly the lines that will render."""
    max_chars = max(1, int(width_px // caption_char_w()))
    lines: list[str] = []
    cur = ""
    for word in text.split(" "):
        # A single word wider than a full line is hard-broken into chunks.
        while len(word) > max_chars:
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def render_caption(spec: dict) -> str:
    """The 'what is deliberately not shown' caption — cognitive integration
    (canon §5). A spec may carry a top-level `caption` string; it renders as
    muted mono at the canvas foot so a diagram in a set always carries its own
    honesty about its boundary.

    The caption **wraps** to the canvas width (`wrap_caption`) instead of
    clipping off the right frame edge: the block sits at the foot with the
    **last** line's baseline at `height - 18` (so a caption that already fits
    on one line renders byte-identical to the un-wrapped form), and earlier
    lines stack above it at a 1.25em line height."""
    caption = spec.get("caption", "")
    if not caption:
        return ""
    width, height = spec.get("size", [900, 500])
    usable = width - CAPTION_LEFT_X - CAPTION_RIGHT_MARGIN
    lines = wrap_caption(caption, usable)
    n = len(lines)
    last_baseline = height - CAPTION_BASELINE_INSET
    parts = []
    for i, line in enumerate(lines):
        y = last_baseline - (n - 1 - i) * CAPTION_LINE_H
        parts.append(
            f'<text x="{CAPTION_LEFT_X}" y="{y}" '
            f"font-family='{FONT_STACK}' font-size=\"{CAPTION_SIZE}\" "
            f"fill=\"{PALETTE['muted']}\">"
            f'{escape(line)}</text>'
        )
    return "\n".join(parts)


def node_box(n):
    return n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]


def node_center(n):
    return n["x"] + n["w"] / 2, n["y"] + n["h"] / 2


def clip_to_box(cx, cy, tx, ty, x1, y1, x2, y2):
    """From (cx,cy) toward (tx,ty), find where the line exits box (x1..x2, y1..y2)."""
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    ts = []
    if dx > 0: ts.append((x2 - cx) / dx)
    elif dx < 0: ts.append((x1 - cx) / dx)
    if dy > 0: ts.append((y2 - cy) / dy)
    elif dy < 0: ts.append((y1 - cy) / dy)
    ts = [t for t in ts if t > 0]
    if not ts:
        return cx, cy
    t = min(ts)
    return cx + t * dx, cy + t * dy


def render_edge(edge: dict, nodes_by_id: dict) -> str:
    src = nodes_by_id[edge["from"]]
    tgt = nodes_by_id[edge["to"]]
    sx, sy = node_center(src)
    tx, ty = node_center(tgt)
    sx1, sy1, sx2, sy2 = node_box(src)
    tx1, ty1, tx2, ty2 = node_box(tgt)

    # Optional waypoints: list of [x, y] pairs the line passes through between source and target.
    via = edge.get("via", []) or []
    next_after_src = (via[0][0], via[0][1]) if via else (tx, ty)
    last_before_tgt = (via[-1][0], via[-1][1]) if via else (sx, sy)
    start_x, start_y = clip_to_box(sx, sy, next_after_src[0], next_after_src[1], sx1, sy1, sx2, sy2)
    end_x, end_y = clip_to_box(tx, ty, last_before_tgt[0], last_before_tgt[1], tx1, ty1, tx2, ty2)

    style = edge.get("style", "solid")
    dash = ' stroke-dasharray="4 3"' if style == "dashed" else ""
    marker = ' marker-end="url(#arrow)"' if style != "tether" else ""
    color = PALETTE["stroke_active"] if style != "tether" else PALETTE["stroke"]

    if via:
        pts = [(start_x, start_y)] + [(p[0], p[1]) for p in via] + [(end_x, end_y)]
        pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        parts = [
            f'<polyline points="{pts_str}" fill="none" '
            f'stroke="{color}" stroke-width="1"{dash}{marker}/>'
        ]
    else:
        parts = [
            f'<line x1="{start_x:.1f}" y1="{start_y:.1f}" '
            f'x2="{end_x:.1f}" y2="{end_y:.1f}" '
            f'stroke="{color}" stroke-width="1"{dash}{marker}/>'
        ]

    label = edge.get("label")
    if label:
        # Explicit label_x/label_y override the perpendicular-offset placement.
        # Useful when the start-end midpoint sits inside another node's frame label.
        if "label_x" in edge and "label_y" in edge:
            lx = float(edge["label_x"])
            ly = float(edge["label_y"])
        else:
            mx = (start_x + end_x) / 2
            my = (start_y + end_y) / 2
            dx = end_x - start_x
            dy = end_y - start_y
            length = (dx * dx + dy * dy) ** 0.5 or 1.0
            # Perpendicular offset, biased "above" for left-to-right and "left" for top-down.
            perp_x = dy / length
            perp_y = -dx / length
            offset = edge.get("label_offset", 11)
            lx = mx + perp_x * offset
            ly = my + perp_y * offset
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" '
            f"font-family='{FONT_STACK}' font-size=\"{EDGE_LABEL_SIZE}\" "
            f'fill="{PALETTE["muted"]}">{escape(label)}</text>'
        )
    return "\n".join(parts)


def render(spec: dict) -> str:
    width, height = spec.get("size", [900, 500])
    title = spec.get("title", "")
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    subgraphs = spec.get("subgraphs", [])
    # Regions are first-class declared structure (done-line 0151): a boundary a
    # node *belongs to* by declaration (`node.region == region.id`), not a
    # rectangle that happens to enclose it. Structurally they render like
    # subgraphs (the visual container is the same); the difference the gate
    # enforces is membership, not geometry. Drawn at the same z-layer as
    # subgraphs so frames stay continuous and edges pass over fills.
    regions = spec.get("regions", [])
    nodes_by_id = {n["id"]: n for n in nodes}

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="{PALETTE["surface"]}"/>',
        defs(),
    ]
    if title:
        out.append(
            f'<text x="32" y="38" '
            f"font-family='{FONT_STACK}' font-size=\"{TITLE_SIZE}\" font-weight=\"600\" "
            f'fill="{PALETTE["text"]}">{escape(title)}</text>'
        )
    # Z-order: subgraph fills (back) → nodes → edges → subgraph frames (front).
    # This puts arrow lines visible across room interiors but under the room's stroke and label,
    # so frames stay continuous and labels stay legible.
    for region in regions:
        out.append(render_subgraph_fill(region))
    for sg in subgraphs:
        out.append(render_subgraph_fill(sg))
    for n in nodes:
        renderer = NODE_RENDERERS.get(n["type"], render_rect)
        out.append(renderer(n))
    for e in edges:
        out.append(render_edge(e, nodes_by_id))
    for region in regions:
        out.append(render_subgraph_frame(region))
    for sg in subgraphs:
        out.append(render_subgraph_frame(sg))
    caption = render_caption(spec)
    if caption:
        out.append(caption)
    out.append("</svg>")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compose an SVG diagram from a JSON spec.")
    ap.add_argument("spec", help="Path to JSON spec file")
    ap.add_argument("--out", help="Output SVG path (default: spec stem + .svg)")
    args = ap.parse_args(argv)
    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_path = Path(args.out) if args.out else spec_path.with_suffix(".svg")
    # Write bytes, not text: text mode translates \n -> \r\n on Windows, which
    # would make the committed SVG non-deterministic across platforms and break
    # the byte-identity the §10 test pins. The bytes ARE render().encode.
    out_path.write_bytes(render(spec).encode("utf-8"))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
