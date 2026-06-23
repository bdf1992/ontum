#!/usr/bin/env python3
"""grammar/cube.py — the coordinate cube, exploded, with planes + full ± axes.

bdo's spec + corrections (this session):
  - centred on the origin; three axes through the centre, FULL ±
  - the three PRINCIPAL PLANES of the axes exist and pass through the
    structure (X¹X², X¹X³, X²X³) — translucent sheets
  - even 3x3x3 = 27 cubies, the centre an open void → 26 labelable cubies
  - EXPLODED with airgaps; each cubie a true 3D cube (top + two sides, clean)
  - the open void recurses

Projection: a symmetric, slightly-flat isometric (top + left + right faces),
flat enough that the explosion separates every cubie instead of collapsing the
view diagonal. Pure stdlib, deterministic — the diagrams/ grain.

    python grammar/cube.py [--out grammar/cube.svg]
"""
from __future__ import annotations

import argparse
from pathlib import Path

# symmetric flat-isometric basis (screen dx,dy per unit)
AX = (0.95, 0.33)    # x — down-right
AY = (-0.95, 0.33)   # y — down-left
AZ = (0.0, -1.0)     # z — up

PAL = {
    "bg": "#fbfaf6", "ink": "#2c2823", "muted": "#9b9485", "gap": "#ffffff",
    "x": "#cf6a3f", "y": "#3f86a6", "z": "#8869b4",
    "top": "#9a7cc4", "right": "#d77b53", "left": "#5b9ab8",
    "pXY": "#d6a022", "pXZ": "#cf6a3f", "pYZ": "#3f86a6",
    "void": "#3a3d46", "lab": "#7c766a",
}
FONT = "ui-sans-serif,-apple-system,'Segoe UI',Inter,system-ui,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def S(o, x, y, z, s):
    return (o[0] + (x * AX[0] + y * AY[0] + z * AZ[0]) * s,
            o[1] + (x * AX[1] + y * AY[1] + z * AZ[1]) * s)


def quad(pts, color, op):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polygon points="{d}" fill="{color}" fill-opacity="{op}" '
            f'stroke="{PAL["gap"]}" stroke-width="1.2" stroke-linejoin="round"/>')


AXES = (AX, AY, AZ)
AXCOL = (PAL["x"], PAL["y"], PAL["z"])


def cubie(cc, hs, gi, gj, gk):
    """Only the inward + outward faces (enlarged) along the cubie's radial axis."""
    if abs(gk) >= max(abs(gi), abs(gj)) and gk != 0:
        a, sg = 2, gk
    elif abs(gi) >= abs(gj) and gi != 0:
        a, sg = 0, gi
    else:
        a, sg = 1, (gj if gj != 0 else 1)
    other = [i for i in range(3) if i != a]
    u, v = AXES[other[0]], AXES[other[1]]
    ext = hs * 1.05
    col = AXCOL[a]

    def tile(sign, mode):
        base = (cc[0] + sign * hs * AXES[a][0], cc[1] + sign * hs * AXES[a][1])
        pts = [(base[0] + (su * u[0] + sv * v[0]) * ext, base[1] + (su * u[1] + sv * v[1]) * ext)
               for su, sv in [(1, 1), (1, -1), (-1, -1), (-1, 1)]]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if mode == "in":   # inward face: a clean outline only
            return f'<polygon points="{d}" fill="none" stroke="{col}" stroke-width="1.3" stroke-opacity="0.5"/>'
        return (f'<polygon points="{d}" fill="{col}" fill-opacity="0.92" '
                f'stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>')

    return tile(-sg, "in") + tile(sg, "out")  # inward outline, then opaque outward face


def void_cubie(cc, hs):
    def C(a, b, c):
        return (cc[0] + (a * AX[0] + b * AY[0] + c * AZ[0]) * hs,
                cc[1] + (a * AX[1] + b * AY[1] + c * AZ[1]) * hs)
    es = [((-1, -1, 1), (1, -1, 1)), ((1, -1, 1), (1, 1, 1)), ((1, 1, 1), (-1, 1, 1)), ((-1, 1, 1), (-1, -1, 1)),
          ((1, -1, 1), (1, -1, -1)), ((1, 1, 1), (1, 1, -1)), ((-1, 1, 1), (-1, 1, -1))]
    out = []
    for p, q in es:
        a, b = C(*p), C(*q)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{PAL["void"]}" stroke-width="1" stroke-dasharray="2 3" opacity="0.6"/>')
    for v, col in [(AX, PAL["x"]), (AY, PAL["y"]), (AZ, PAL["z"])]:
        t = (cc[0] + v[0] * 0.6 * hs, cc[1] + v[1] * 0.6 * hs)
        out.append(f'<line x1="{cc[0]:.1f}" y1="{cc[1]:.1f}" x2="{t[0]:.1f}" y2="{t[1]:.1f}" '
                   f'stroke="{col}" stroke-width="1.2" stroke-linecap="round" opacity="0.85"/>')
    return "".join(out)


def plane(o, v1, v2, h, color):
    cs = [(o[0] + (a * v1[0] + b * v2[0]) * h, o[1] + (a * v1[1] + b * v2[1]) * h)
          for a, b in [(1, 1), (1, -1), (-1, -1), (-1, 1)]]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in cs)
    return (f'<polygon points="{pts}" fill="{color}" fill-opacity="0.05" '
            f'stroke="{color}" stroke-opacity="0.30" stroke-width="1.1" stroke-dasharray="3 4"/>')


def sign(n):
    return "＋" if n > 0 else ("－" if n < 0 else "0")


def render(W=1540, H=1340):
    o = (770, 660)
    spread = 244
    hs = 40
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
            f'<rect width="{W}" height="{H}" fill="{PAL["bg"]}"/>',
            '<defs>' + "".join(
                f'<marker id="m{m}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" '
                f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>'
                for m, c in [("x", PAL["x"]), ("y", PAL["y"]), ("z", PAL["z"])]) + '</defs>',
            f'<text x="44" y="52" font-family="{FONT}" font-size="19" font-weight="650" fill="{PAL["ink"]}">'
            f'Coordinate cube — exploded · planes + full ± axes · 26 cubies + void</text>',
            f'<text x="44" y="74" font-family="{FONT}" font-size="12.5" fill="{PAL["muted"]}">'
            f'three principal planes through the centre · each cubie a 3D cube with room to label · the void recurses</text>']

    # principal planes through the centre (behind), reaching just past the shell
    ph = spread * 1.28
    body.append(plane(o, AX, AY, ph, PAL["pXY"]))
    body.append(plane(o, AX, AZ, ph, PAL["pXZ"]))
    body.append(plane(o, AY, AZ, ph, PAL["pYZ"]))

    # ± axes through the centre (behind the cubies)
    axlen = spread * 2.1
    for v, col, lab, mk in [(AX, PAL["x"], "X¹", "mx"), (AY, PAL["y"], "X²", "my"), (AZ, PAL["z"], "X³", "mz")]:
        pos = (o[0] + v[0] * axlen, o[1] + v[1] * axlen)
        neg = (o[0] - v[0] * axlen, o[1] - v[1] * axlen)
        body.append(f'<line x1="{neg[0]:.1f}" y1="{neg[1]:.1f}" x2="{pos[0]:.1f}" y2="{pos[1]:.1f}" '
                    f'stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>')
        body.append(f'<line x1="{o[0]:.1f}" y1="{o[1]:.1f}" x2="{pos[0]:.1f}" y2="{pos[1]:.1f}" '
                    f'stroke="{col}" stroke-width="2.2" stroke-linecap="round" marker-end="url(#{mk})"/>')
        ox = 14 if v[0] > 0.1 else (-14 if v[0] < -0.1 else 0)
        anc = "start" if v[0] > 0.1 else ("end" if v[0] < -0.1 else "middle")
        body.append(f'<text x="{pos[0]+ox:.1f}" y="{pos[1]:.1f}" text-anchor="{anc}" '
                    f'font-family="{MONO}" font-size="13" font-weight="700" fill="{col}">+{lab}</text>')
        body.append(f'<text x="{neg[0]-ox:.1f}" y="{neg[1]:.1f}" text-anchor="{anc}" '
                    f'font-family="{MONO}" font-size="11.5" font-weight="600" fill="{col}" opacity="0.6">−{lab}</text>')

    # cubies, painter-sorted by screen height (top/far first, bottom/near last)
    grid = [(gi, gj, gk) for gi in (-1, 0, 1) for gj in (-1, 0, 1) for gk in (-1, 0, 1)]
    grid.sort(key=lambda g: AX[1] * g[0] + AY[1] * g[1] + AZ[1] * g[2])
    for (gi, gj, gk) in grid:
        cc = S(o, gi, gj, gk, spread)
        if (gi, gj, gk) == (0, 0, 0):
            body.append(void_cubie(cc, hs))
            body.append(f'<text x="{cc[0]:.1f}" y="{cc[1]+hs*1.95:.1f}" text-anchor="middle" '
                        f'font-family="{MONO}" font-size="10" fill="{PAL["muted"]}">void · recurs</text>')
            continue
        body.append(cubie(cc, hs, gi, gj, gk))
        body.append(f'<text x="{cc[0]:.1f}" y="{cc[1]+hs*1.95:.1f}" text-anchor="middle" '
                    f'font-family="{MONO}" font-size="10" fill="{PAL["lab"]}">{sign(gi)}{sign(gj)}{sign(gk)}</text>')
    body.append("</svg>")
    return "\n".join(body)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="grammar.cube")
    ap.add_argument("--out", default="grammar/cube.svg")
    a = ap.parse_args(argv)
    Path(a.out).write_text(render(), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
