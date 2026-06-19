/* space.js — Causality's chunked coordinate volume (iterations 0010). API-first:
   addresses are DATA; the renderer only projects + routes. Default projection is a
   2D top-down grid (the reading view); z and chunk subdivision are addressable for
   the dev/3D view and recursion (chunk → subcube → sub-subcube = phrase → glyph →
   facet). A node has an ADDRESS (x,y,z[,chunk]), never a float.

   The payoff (bdo, 0010): edges route as LANES THROUGH FREE CELLS — orthogonal
   A* that goes around occupied cubes and prefers unused lanes — so connections are
   deterministic and crossing-free instead of float-overlap soup.

   window.CausalitySpace = { Space } */
(function () {
'use strict';

function Space(opts) {
  opts = opts || {};
  const S = { nx: opts.nx || 10, ny: opts.ny || 10, nz: opts.nz || 10, occ: new Map(), used: new Set() };
  const K = (x, y, z) => x + ',' + y + ',' + (z || 0);

  S.place = (id, x, y, z) => { S.occ.set(K(x, y, z), id); return S; };
  S.isOcc = (x, y, z) => S.occ.has(K(x, y, z));
  S.clear = () => { S.occ.clear(); S.used.clear(); return S; };

  // viewport fit: a centred square-cell region (the volume's z=0 face)
  S.fit = (W, H, pad) => { pad = pad == null ? 0.08 : pad;
    const c = Math.min(W * (1 - 2 * pad) / S.nx, H * (1 - 2 * pad) / S.ny);
    S.c = c; S.ox = (W - c * S.nx) / 2; S.oy = (H - c * S.ny) / 2; return S; };
  // address -> surface centre of a cell (the projection; z nudges for the dev/3D view)
  S.center = (x, y, z) => ({ x: S.ox + (x + 0.5) * S.c - (z || 0) * S.c * 0.18, y: S.oy + (y + 0.5) * S.c - (z || 0) * S.c * 0.18 });

  // orthogonal A* on the z-plane: around occupied cells, preferring unused lanes.
  // returns the list of cells {x,y}; `reserve` records them so later edges avoid them.
  S.route = (a, b, reserve) => {
    reserve = reserve !== false;
    const h = (x, y) => Math.abs(x - b.x) + Math.abs(y - b.y);
    const open = [{ x: a.x, y: a.y, g: 0, f: h(a.x, a.y), p: null }];
    const best = new Map([[K(a.x, a.y, 0), 0]]);
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    let goal = null;
    while (open.length) {
      let mi = 0; for (let i = 1; i < open.length; i++) if (open[i].f < open[mi].f) mi = i;
      const cur = open.splice(mi, 1)[0];
      if (cur.x === b.x && cur.y === b.y) { goal = cur; break; }
      for (const [dx, dy] of dirs) {
        const nx = cur.x + dx, ny = cur.y + dy;
        if (nx < 0 || ny < 0 || nx >= S.nx || ny >= S.ny) continue;
        const k = K(nx, ny, 0);
        const endpoint = (nx === b.x && ny === b.y) || (nx === a.x && ny === a.y);
        if (S.occ.has(k) && !endpoint) continue;             // route AROUND nodes
        let step = 1; if (reserve && S.used.has(k)) step += 3; // prefer unused lanes
        const g = cur.g + step;
        if (!best.has(k) || g < best.get(k)) { best.set(k, g); open.push({ x: nx, y: ny, g, f: g + h(nx, ny), p: cur }); }
      }
    }
    if (!goal) return [{ x: a.x, y: a.y }, { x: b.x, y: b.y }];  // honest fallback
    const cells = []; for (let n = goal; n; n = n.p) cells.unshift({ x: n.x, y: n.y });
    if (reserve) cells.forEach((c, i) => { if (i && i < cells.length - 1) S.used.add(K(c.x, c.y, 0)); });
    return cells;
  };

  // dev-mode seams: the grid lines of the z=0 face
  S.gridLines = () => { const L = [];
    for (let i = 0; i <= S.nx; i++) L.push([[S.ox + i * S.c, S.oy], [S.ox + i * S.c, S.oy + S.ny * S.c]]);
    for (let j = 0; j <= S.ny; j++) L.push([[S.ox, S.oy + j * S.c], [S.ox + S.nx * S.c, S.oy + j * S.c]]);
    return L; };

  return S;
}

if (typeof window !== 'undefined') window.CausalitySpace = { Space };
if (typeof module !== 'undefined' && module.exports) module.exports = { Space };
})();
