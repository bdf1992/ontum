#!/usr/bin/env python3
"""grammar/coord.py — a reusable isometric coordinate-system diagram generator.

Step 1 of bdo's recursive coordinate-system architecture: one big, nice,
REUSABLE 3D coordinate cell — three axes + a forward arrow + open slots for
more topology — drawn as a parametric SVG group, so later steps compose many
(above / below / parallel / merged tree, then the creole fills the slots).

A new genre beside diagrams/compose.py (the box genre can't draw 3D axes).
Pure stdlib, deterministic, explicit-position — the diagrams/ grain.

    python grammar/coord.py [--out grammar/coord.svg]
"""
from __future__ import annotations

import argparse
from pathlib import Path

# true-isometric screen basis: unit step along each axis -> (dx, dy)
R = (0.866, 0.5)    # X — down-right
L = (-0.866, 0.5)   # Y — down-left
U = (0.0, -1.0)     # Z — up

PAL = {
    "bg0": "#fbfaf6", "bg1": "#f0ece1", "grid": "#e7e2d6", "ink": "#2c2823",
    "muted": "#9b948500", "muted2": "#9b9485",
    "cube": "#cdc6b6", "fTop": "#f4f0e6", "fLeft": "#e8e2d4", "fRight": "#ded7c6",
    "x": "#cf6a3f", "y": "#3f86a6", "z": "#8869b4", "fwd": "#d6a022", "slot": "#a9a292",
}
FONT = "ui-sans-serif,-apple-system,'Segoe UI',Inter,system-ui,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def pt(o, a, b, c, s):
    """Screen point for cube coeffs (a,b,c) along X,Y,Z from base o at scale s."""
    x = o[0] + (a * R[0] + b * L[0] + c * U[0]) * s
    y = o[1] + (a * R[1] + b * L[1] + c * U[1]) * s
    return (x, y)


def lerp(o, v, k, s):
    return (o[0] + v[0] * k * s, o[1] + v[1] * k * s)


def poly(points, fill, stroke, sw=1.0, op=1.0):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round" opacity="{op}"/>')


def axis(o, v, s, length, color, label, sub, marker):
    tip = lerp(o, v, length, color and s or s)  # tip beyond the unit cube
    tip = (o[0] + v[0] * length * s, o[1] + v[1] * length * s)
    lx, ly = tip
    # label chip placed just past the tip
    ox = 12 if v[0] >= 0 else -12
    anchor = "start" if v[0] >= 0 else "end"
    return f"""
    <line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{lx:.1f}" y2="{ly:.1f}"
          stroke="{color}" stroke-width="2.4" stroke-linecap="round" marker-end="url(#{marker})"/>
    <g transform="translate({lx + ox:.1f},{ly:.1f})">
      <text text-anchor="{anchor}" font-family="{MONO}" font-size="14" font-weight="700" fill="{color}" dy="-2">{label}</text>
      <text text-anchor="{anchor}" font-family="{FONT}" font-size="10.5" fill="{PAL['muted2']}" dy="13">{sub}</text>
    </g>"""


def coord_cell(o, s, title):
    """One coordinate cell as an SVG group string. Reusable: call with any (o, s)."""
    # the 8 cube corners we need
    c000 = pt(o, 0, 0, 0, s)            # origin (== c111 in iso)
    cX = pt(o, 1, 0, 0, s)             # 100
    cY = pt(o, 0, 1, 0, s)             # 010
    cZ = pt(o, 0, 0, 1, s)             # 001
    cXY = pt(o, 1, 1, 0, s)            # 110 (bottom)
    cXZ = pt(o, 1, 0, 1, s)            # 101 (upper-right)
    cYZ = pt(o, 0, 1, 1, s)            # 011 (upper-left)
    parts = []
    # three visible faces (top / left / right) sharing the centre — the "faces & bounds"
    parts.append(poly([cZ, cXZ, c000, cYZ], PAL["fTop"], PAL["cube"], 1.0))     # top
    parts.append(poly([cY, cXY, c000, cYZ], PAL["fLeft"], PAL["cube"], 1.0))    # left
    parts.append(poly([cX, cXY, c000, cXZ], PAL["fRight"], PAL["cube"], 1.0))   # right
    # open slots — dashed ghost stubs that say "capacity for more topology"
    for (vx, vy), tag in [((0.45, -0.78), ""), ((-0.45, -0.78), ""), ((0.0, 1.02), "")]:
        sx, sy = o[0] + vx * 0.92 * s, o[1] + vy * 0.92 * s
        parts.append(f'<line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
                     f'stroke="{PAL["slot"]}" stroke-width="1.4" stroke-dasharray="2 6" opacity=".8"/>')
        parts.append(f'<rect x="{sx-5:.1f}" y="{sy-5:.1f}" width="10" height="10" rx="2" '
                     f'transform="rotate(45 {sx:.1f} {sy:.1f})" fill="none" stroke="{PAL["slot"]}" stroke-width="1.4"/>')
    # the three axes (drawn over the faces), extended past the unit cube for the heads
    parts.append(axis(o, R, s, 1.34, PAL["x"], "X¹", "axis · dim 1", "arX"))
    parts.append(axis(o, L, s, 1.34, PAL["y"], "X²", "axis · dim 2", "arY"))
    parts.append(axis(o, U, s, 1.34, PAL["z"], "X³", "axis · dim 3", "arZ"))
    # the forward arrow — the flow / composition direction (toward the next cell)
    fy = o[1] - 0.30 * s
    parts.append(f'<line x1="{cXZ[0]+6:.1f}" y1="{fy:.1f}" x2="{cXZ[0]+0.95*s:.1f}" y2="{fy:.1f}" '
                 f'stroke="{PAL["fwd"]}" stroke-width="3.4" stroke-linecap="round" marker-end="url(#arF)"/>')
    parts.append(f'<text x="{cXZ[0]+0.5*s:.1f}" y="{fy-10:.1f}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="13" font-weight="700" fill="{PAL["fwd"]}">FORWARD</text>')
    parts.append(f'<text x="{cXZ[0]+0.5*s:.1f}" y="{fy+18:.1f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="10" fill="{PAL["muted2"]}">to the next cell</text>')
    # origin
    parts.append(f'<circle cx="{o[0]:.1f}" cy="{o[1]:.1f}" r="4.5" fill="{PAL["ink"]}"/>')
    parts.append(f'<text x="{o[0]+9:.1f}" y="{o[1]+18:.1f}" font-family="{MONO}" font-size="11" fill="{PAL["muted2"]}">origin</text>')
    # title
    parts.append(f'<text x="{o[0]:.1f}" y="{o[1]-1.62*s:.1f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="17" font-weight="650" fill="{PAL["ink"]}">{title}</text>')
    parts.append(f'<text x="{o[0]:.1f}" y="{o[1]-1.62*s+20:.1f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="11.5" fill="{PAL["muted2"]}">a reusable cell · 3 axes + forward + open slots</text>')
    return "<g>" + "\n".join(parts) + "</g>"


def defs():
    heads = ""
    for mid, col in [("arX", PAL["x"]), ("arY", PAL["y"]), ("arZ", PAL["z"]), ("arF", PAL["fwd"])]:
        heads += (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" '
                  f'markerHeight="7.5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
    return f"""<defs>
      <radialGradient id="bg" cx="50%" cy="34%" r="80%">
        <stop offset="0%" stop-color="{PAL['bg0']}"/><stop offset="100%" stop-color="{PAL['bg1']}"/>
      </radialGradient>
      <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
        <circle cx="1.2" cy="1.2" r="1.1" fill="{PAL['grid']}"/>
      </pattern>
      <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#2a2418" flood-opacity="0.10"/>
      </filter>
      {heads}
    </defs>"""


def render(width=980, height=780):
    o = (470, 470)
    s = 196
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="url(#bg)"/>
  <rect width="{width}" height="{height}" fill="url(#dots)"/>
  {defs()}
  <g filter="url(#soft)">{coord_cell(o, s, "Coordinate System")}</g>
  <text x="32" y="{height-26}" font-family="{MONO}" font-size="11" fill="{PAL['muted2']}">grammar/coord.py · step 1 — the reusable cell (above / below / parallel / tree compose from this)</text>
</svg>"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="grammar.coord")
    ap.add_argument("--out", default="grammar/coord.svg")
    a = ap.parse_args(argv)
    Path(a.out).write_text(render(), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
