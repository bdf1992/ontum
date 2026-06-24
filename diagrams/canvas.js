/* diagrams/canvas.js — the editable diagram canvas (done-line 0192, the first
   cut of the editable diagram canvas; bdo-stamped CTA-A = A1 in
   .ai-native/proposals/diagram-canvas.proposal.md).

   This REUSES the schema/inspector/persistence DISCIPLINE of
   causality/canvas.js by pattern — it does NOT import or extend that artifact
   (the epic's no-double-build rule: a schema change there would break the live
   causality preset). It edits the compose.py SPEC: the spec is the truth, the
   canvas is an editor over it. The shippable picture is only ever produced by
   compose.py behind the qa.py gate — this canvas emits a spec, never an SVG,
   so it cannot ship a picture the gate refuses.

   Two halves, cleanly split so the model is testable headless:
     - the MODEL (createModel): pure JS over a spec — select, move (writes
       explicit x/y), edit attributes via a schema-driven inspector, declared
       layers, toJSON/fromJSON. No DOM. This is what canvas.persist.test.js
       exercises.
     - the VIEW (DiagramCanvas): the browser surface — an SVG render for
       editing, the inspector panel, the layer panel, drag, localStorage
       autosave, file import/export, and the export-through-the-gate path.

   No deps, vanilla JS, offline. A new part-type ships as a SCHEMA entry (here)
   plus a renderer in compose.py — not new canvas code (the agnosticism).
*/
(function () {
'use strict';

// ════════════════════════ the diagram SCHEMA ════════════════════════
// one table → part defaults + the inspector + persistence (the discipline).
const F = (key, label, kind, def, extra = {}) => Object.assign({ key, label, kind, def }, extra);

// the closed part-type vocabulary compose.py renders (mirrors compose.py
// NODE_TYPES). A new part-type is a SCHEMA entry here AND a renderer there.
const PART_TYPES = ['pill', 'rect', 'rounded', 'dashed', 'subroutine', 'hex', 'rhombus', 'chips'];
const ACCENTS = ['', 'cool', 'warm'];           // the palette is two accents (perceptual discriminability)

// fields every part carries: label/type/accent + DECLARED membership.
const COMMON = [
  F('label', 'label', 'text', 'part'),
  F('type', 'type', 'select', 'rect', { opts: PART_TYPES }),
  F('accent', 'accent', 'select', '', { opts: ACCENTS }),
  F('layer', 'layer', 'text', null),            // declared layer membership (not geometry)
  F('region', 'region', 'text', null),          // declared region membership (done-line 0151)
];
// explicit geometry — editing x/y is the no-auto-layout move (drag writes these).
const GEOM = [
  F('x', 'x', 'number', 40), F('y', 'y', 'number', 40),
  F('w', 'w', 'number', 160), F('h', 'h', 'number', 70),
];
// per-type config (today only chips carries items). A new type's config rides here.
const TYPE_CONFIG = {
  pill: [], rect: [], rounded: [], dashed: [], subroutine: [],
  hex: [], rhombus: [], chips: [F('items', 'items (csv)', 'csv', [])],
};
// the holonic attribute fields every part carries (causality/display-system.md;
// declared now, populated by a later piece — mirrors canvas.js's HOLONIC).
const HOLONIC = [
  F('sites', 'sites (csv)', 'csv', []),
  F('space', 'space', 'text', null),
  F('strata.fundamental', 'fundamental (addr)', 'text', null),
  F('strata.derived', 'derived (fold)', 'text', null),
  F('strata.learned', 'learned (model)', 'text', null),
  F('anima.strength', 'anima · weak↔strong', 'number', null),
  F('anima.tempo', 'anima · fast↔slow', 'number', null),
];
const fieldsFor = type => [...COMMON, ...GEOM, ...(TYPE_CONFIG[type] || []), ...HOLONIC];

// dotted-path get/set so the schema can address nested config (strata.derived, anima.tempo)
const getPath = (o, key) => key.split('.').reduce((v, k) => (v == null ? v : v[k]), o);
const setPath = (o, key, val) => {
  const ks = key.split('.'); const last = ks.pop();
  let t = o; for (const k of ks) { if (t[k] == null || typeof t[k] !== 'object') t[k] = {}; t = t[k]; } t[last] = val;
};

// ════════════════════════ the layer-membership preflight ════════════════════════
// Mirrors qa.py's check_layer_membership. qa.py is the AUTHORITY that gates
// compose.py; this JS mirror is an advisory preflight so the editor catches a
// layer-orphan immediately, naming the same canon principle. It is NOT a second
// source of truth — the canvas emits a spec, the gate judges it, compose.py
// renders. Used to refuse export of a spec the gate would refuse.
function layerMembershipIssues(spec) {
  const declared = new Set((spec.layers || []).map(l => l.id).filter(Boolean));
  const out = [];
  const kinds = [['node', spec.nodes], ['edge', spec.edges], ['region', spec.regions], ['subgraph', spec.subgraphs]];
  for (const [kind, arr] of kinds) {
    for (const p of (arr || [])) {
      if (p.layer == null) continue;
      if (!declared.has(p.layer)) {
        out.push({
          principle: 'C4 containment / cognitive integration',
          message: `${kind} declares layer '${p.layer}' that is not in the diagram's \`layers\` — a band that does not exist`,
          ctx: p.id || (p.from ? p.from + '->' + p.to : (p.label || '')),
        });
      }
    }
  }
  return out;
}

// ════════════════════════ spec normalize / serialize ════════════════════════
function normalize(spec) {
  spec = spec || {};
  const arr = (a, f) => (Array.isArray(a) ? a.map(f) : []);
  return {
    size: Array.isArray(spec.size) ? spec.size.slice() : [1200, 600],
    title: spec.title || '',
    caption: spec.caption || '',
    layers: arr(spec.layers, l => Object.assign({ z: 0, visible: true, locked: false }, l)),
    regions: arr(spec.regions, r => Object.assign({}, r)),
    subgraphs: arr(spec.subgraphs, s => Object.assign({}, s)),
    nodes: arr(spec.nodes, n => Object.assign({}, n)),
    edges: arr(spec.edges, e => Object.assign({}, e)),
  };
}

const NESTED = new Set(['strata', 'anima']);    // schema-managed nested objects
const IDENTITY = ['id', 'type', 'x', 'y', 'w', 'h', 'label'];
function serializeNode(n) {
  const o = {
    id: n.id, type: n.type || 'rect',
    x: Math.round(n.x), y: Math.round(n.y), w: Math.round(n.w), h: Math.round(n.h),
    label: n.label != null ? n.label : '',
  };
  for (const f of fieldsFor(n.type)) {
    if (IDENTITY.includes(f.key)) continue;
    const v = getPath(n, f.key);
    if (v == null || (Array.isArray(v) && v.length === 0)) continue;
    setPath(o, f.key, v);
  }
  // passthrough any extra key (e.g. hub, via on an edge-shaped node) the schema
  // does not name, except schema-managed nested objects already emitted above.
  for (const k of Object.keys(n)) { if (k in o || NESTED.has(k)) continue; o[k] = n[k]; }
  return o;
}
// a compose-ready spec: only non-empty top-level keys, schema-driven nodes.
function serialize(spec) {
  const out = {};
  if (spec.size) out.size = spec.size.slice();
  if (spec.title) out.title = spec.title;
  if (spec.layers && spec.layers.length) out.layers = spec.layers.map(l => Object.assign({}, l));
  if (spec.regions && spec.regions.length) out.regions = spec.regions.map(r => Object.assign({}, r));
  if (spec.subgraphs && spec.subgraphs.length) out.subgraphs = spec.subgraphs.map(s => Object.assign({}, s));
  out.nodes = (spec.nodes || []).map(serializeNode);
  out.edges = (spec.edges || []).map(e => Object.assign({}, e));
  if (spec.caption) out.caption = spec.caption;
  return out;
}

function uniqueNodeId(S, prefix) { let i = 1, id; do { id = prefix + '-' + i++; } while (S.spec.nodes.some(n => n.id === id)); return id; }
function uniqueLayerId(S) { let i = 1, id; do { id = 'layer-' + i++; } while (S.spec.layers.some(l => l.id === id)); return id; }

// ════════════════════════ the MODEL (pure, headless-testable) ════════════════════════
function createModel(spec) {
  const S = { spec: normalize(spec), selected: null, listeners: [] };
  const byId = id => S.spec.nodes.find(n => n.id === id);
  S.byId = byId;
  S.emit = () => S.listeners.forEach(fn => fn(S));
  S.onChange = fn => { if (fn) S.listeners.push(fn); return S; };

  S.select = (kind, id) => { S.selected = (id != null) ? { kind, id } : null; S.emit(); };
  S.selectedPart = () => {
    if (!S.selected) return null;
    const { kind, id } = S.selected;
    if (kind === 'node') return byId(id);
    if (kind === 'region') return S.spec.regions.find(r => r.id === id);
    return null;
  };

  S.addNode = (x, y, o = {}) => {
    const id = o.id || uniqueNodeId(S, 'part');
    const n = Object.assign({ type: 'rect', label: 'part', w: 160, h: 70 }, o, { id, x: Math.round(x), y: Math.round(y) });
    S.spec.nodes.push(n); S.emit(); return n;
  };
  S.removeNode = id => {
    S.spec.nodes = S.spec.nodes.filter(n => n.id !== id);
    S.spec.edges = S.spec.edges.filter(e => e.from !== id && e.to !== id);
    if (S.selected && S.selected.id === id) S.selected = null;
    S.emit();
  };
  S.moveNode = (id, x, y) => { const n = byId(id); if (n) { n.x = Math.round(x); n.y = Math.round(y); S.emit(); } };

  // schema-driven field edit: the inspector and any setter go through here.
  S.setField = (kind, id, key, val) => {
    const part = kind === 'node' ? byId(id) : (kind === 'region' ? S.spec.regions.find(r => r.id === id) : null);
    if (!part) return;
    const empty = (val === '' || val == null);
    if (empty && key !== 'label') {
      const ks = key.split('.');
      if (ks.length === 1) delete part[key];
      else { const parent = getPath(part, ks.slice(0, -1).join('.')); if (parent) delete parent[ks[ks.length - 1]]; }
    } else setPath(part, key, val);
    S.emit();
  };

  // ---- layers (declared membership; show/hide, lock, reorder by z) ----
  S.addLayer = (id, label) => {
    id = id || uniqueLayerId(S);
    const z = S.spec.layers.reduce((m, l) => Math.max(m, l.z || 0), -1) + 1;
    const lyr = { id, label: label || id, z, visible: true, locked: false };
    S.spec.layers.push(lyr); S.emit(); return lyr;
  };
  S.setLayerVisible = (id, v) => { const l = S.spec.layers.find(x => x.id === id); if (l) { l.visible = !!v; S.emit(); } };
  S.setLayerLocked = (id, v) => { const l = S.spec.layers.find(x => x.id === id); if (l) { l.locked = !!v; S.emit(); } };
  S.reorderLayer = (id, dir) => {
    const sorted = [...S.spec.layers].sort((a, b) => (a.z || 0) - (b.z || 0));
    const i = sorted.findIndex(l => l.id === id); if (i < 0) return;
    const j = dir < 0 ? i - 1 : i + 1; if (j < 0 || j >= sorted.length) return;
    const tz = sorted[i].z; sorted[i].z = sorted[j].z; sorted[j].z = tz; S.emit();
  };
  S.layersByZ = () => [...S.spec.layers].sort((a, b) => (a.z || 0) - (b.z || 0));
  S.layerOf = part => (part && part.layer != null) ? S.spec.layers.find(l => l.id === part.layer) : null;
  S.isLocked = part => { const l = S.layerOf(part); return !!(l && l.locked); };
  S.isVisible = part => { const l = S.layerOf(part); return l ? l.visible !== false : true; };

  // ---- persistence (toJSON / fromJSON), schema-driven ----
  S.toJSON = () => serialize(S.spec);
  S.fromJSON = (g) => {
    if (!g || !Array.isArray(g.nodes)) return false;   // a malformed restore is refused
    S.spec = normalize(g); S.selected = null; S.emit(); return true;
  };
  // the export preflight: the issues qa.py would refuse (advisory mirror).
  S.preflight = () => layerMembershipIssues(S.toJSON());
  return S;
}

// ════════════════════════ the VIEW (browser only) ════════════════════════
const PALETTE = { surface: '#0B0B0C', panel: '#141416', text: '#E6E6E6', muted: '#8C8C8F',
                  stroke: '#3A3A3D', cool: '#5EB7A1', warm: '#C97A55', sel: '#7a5ba6' };
const accentColor = a => (a === 'cool' ? PALETTE.cool : a === 'warm' ? PALETTE.warm : PALETTE.stroke);
const SVGNS = 'http://www.w3.org/2000/svg';
const STORE_KEY = 'diagram.canvas.v1';

const STARTER = {
  size: [900, 360], title: 'a fresh diagram',
  layers: [{ id: 'base', label: 'base', z: 0, visible: true, locked: false }],
  nodes: [
    { id: 'a', type: 'rect', layer: 'base', x: 80, y: 140, w: 180, h: 70, label: 'first' },
    { id: 'b', type: 'hex', layer: 'base', x: 380, y: 140, w: 180, h: 70, label: 'second', accent: 'cool' },
  ],
  edges: [{ from: 'a', to: 'b', layer: 'base' }],
};

function el(tag, attrs, kids) {
  const e = document.createElement(tag);
  for (const k in (attrs || {})) { if (k === 'style') e.style.cssText = attrs[k]; else if (k.slice(0, 2) === 'on') e[k] = attrs[k]; else e.setAttribute(k, attrs[k]); }
  for (const c of (kids || [])) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  return e;
}
function svgEl(tag, attrs) { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; }

function partPoints(n) {
  const { x, y, w, h } = n;
  if (n.type === 'hex') { const i = Math.min(h * 0.28, w * 0.18); return `${x + i},${y} ${x + w - i},${y} ${x + w},${y + h / 2} ${x + w - i},${y + h} ${x + i},${y + h} ${x},${y + h / 2}`; }
  if (n.type === 'rhombus') return `${x + w / 2},${y} ${x + w},${y + h / 2} ${x + w / 2},${y + h} ${x},${y + h / 2}`;
  return null;
}

function DiagramCanvas(opts) {
  opts = opts || {};
  const stage = opts.stage, inspectorEl = opts.inspector, layersEl = opts.layers, statusEl = opts.status;
  // restore: explicit opts.spec → localStorage → starter.
  let initial = opts.spec;
  if (!initial && opts.persist !== false) { try { const raw = localStorage.getItem(STORE_KEY); if (raw) initial = JSON.parse(raw); } catch (e) {} }
  const M = createModel(initial || STARTER);

  const status = msg => { if (statusEl) statusEl.textContent = msg; };
  const autosave = () => { if (opts.persist === false) return; try { localStorage.setItem(STORE_KEY, JSON.stringify(M.toJSON())); } catch (e) {} };

  // ---- render the SVG editing surface ----
  let drag = null;
  function renderStage() {
    if (!stage) return;
    stage.innerHTML = '';
    const [W, H] = M.spec.size;
    const svg = svgEl('svg', { xmlns: SVGNS, viewBox: `0 0 ${W} ${H}`, width: W, height: H, style: `background:${PALETTE.surface}` });
    svg.appendChild(svgEl('rect', { x: 0, y: 0, width: W, height: H, fill: PALETTE.surface }));
    // regions (behind), as declared containers
    for (const r of M.spec.regions) {
      if (!M.isVisible(r)) continue;
      svg.appendChild(svgEl('rect', { x: r.x, y: r.y, width: r.w, height: r.h, rx: 6, fill: 'none', stroke: PALETTE.stroke, 'stroke-dasharray': '2 4' }));
    }
    // edges
    const byId = id => M.byId(id);
    for (const e of M.spec.edges) {
      const s = byId(e.from), t = byId(e.to);
      if (!s || !t || !M.isVisible(s) || !M.isVisible(t) || !M.isVisible(e)) continue;
      svg.appendChild(svgEl('line', { x1: s.x + s.w / 2, y1: s.y + s.h / 2, x2: t.x + t.w / 2, y2: t.y + t.h / 2, stroke: PALETTE.muted, 'stroke-width': 1 }));
    }
    // nodes, drawn in ascending layer z (so the edit surface matches compose.py)
    const zOf = n => { const l = M.layerOf(n); return l ? (l.z || 0) : 0; };
    const drawn = M.spec.nodes.filter(M.isVisible).slice().sort((a, b) => zOf(a) - zOf(b));
    for (const n of drawn) {
      const sel = M.selected && M.selected.kind === 'node' && M.selected.id === n.id;
      const stroke = sel ? PALETTE.sel : accentColor(n.accent);
      const g = svgEl('g', { style: M.isLocked(n) ? 'cursor:not-allowed' : 'cursor:grab' });
      const pts = partPoints(n);
      if (pts) g.appendChild(svgEl('polygon', { points: pts, fill: PALETTE.panel, stroke, 'stroke-width': sel ? 2.5 : 1.5 }));
      else { const rx = n.type === 'pill' ? n.h / 2 : n.type === 'rounded' ? 14 : 4; g.appendChild(svgEl('rect', { x: n.x, y: n.y, width: n.w, height: n.h, rx, fill: PALETTE.panel, stroke, 'stroke-width': sel ? 2.5 : 1.5, 'stroke-dasharray': n.type === 'dashed' ? '4 3' : '' })); }
      const tx = svgEl('text', { x: n.x + n.w / 2, y: n.y + n.h / 2, 'text-anchor': 'middle', 'dominant-baseline': 'central', fill: PALETTE.text, 'font-family': 'ui-monospace, monospace', 'font-size': 14 });
      tx.textContent = n.label || '';
      g.appendChild(tx);
      g.addEventListener('pointerdown', ev => {
        ev.preventDefault(); M.select('node', n.id);
        if (M.isLocked(n)) { status(`'${n.id}' is on a locked layer — unlock to move`); return; }
        const pt = stagePoint(svg, ev);
        drag = { id: n.id, dx: pt.x - n.x, dy: pt.y - n.y };
        g.setPointerCapture && g.setPointerCapture(ev.pointerId);
      });
      g.addEventListener('pointermove', ev => { if (!drag || drag.id !== n.id) return; const pt = stagePoint(svg, ev); M.moveNode(n.id, pt.x - drag.dx, pt.y - drag.dy); });
      g.addEventListener('pointerup', () => { if (drag) { drag = null; autosave(); } });
      svg.appendChild(g);
    }
    svg.addEventListener('pointerdown', ev => { if (ev.target === svg) M.select(null); });
    stage.appendChild(svg);
  }
  function stagePoint(svg, ev) {
    const r = svg.getBoundingClientRect();
    const [W, H] = M.spec.size;
    return { x: Math.round((ev.clientX - r.left) / r.width * W), y: Math.round((ev.clientY - r.top) / r.height * H) };
  }

  // ---- the schema-driven inspector ----
  function renderInspector() {
    if (!inspectorEl) return;
    inspectorEl.innerHTML = '';
    const part = M.selectedPart();
    if (!part) { inspectorEl.appendChild(el('div', { style: `color:${PALETTE.muted};padding:8px` }, ['select a part to inspect'])); return; }
    const kind = M.selected.kind;
    inspectorEl.appendChild(el('div', { style: `color:${PALETTE.muted};font-size:11px;padding:4px 8px` }, [`${kind} · ${part.id}`]));
    for (const f of fieldsFor(part.type)) {
      const v = getPath(part, f.key);
      const row = el('label', { style: 'display:flex;gap:6px;align-items:center;padding:2px 8px;font-size:12px' });
      row.appendChild(el('span', { style: `width:120px;color:${PALETTE.muted}` }, [f.label]));
      let input;
      if (f.kind === 'select') {
        input = el('select', { style: inputStyle() });
        for (const o of (typeof f.opts === 'function' ? f.opts() : f.opts)) input.appendChild(el('option', { value: o }, [o === '' ? '(none)' : o]));
        input.value = v == null ? '' : v;
      } else {
        input = el('input', { type: f.kind === 'number' ? 'number' : 'text', style: inputStyle() });
        input.value = (v == null) ? '' : (Array.isArray(v) ? v.join(', ') : v);
      }
      input.addEventListener('change', () => {
        let val = input.value;
        if (f.kind === 'number') val = (val === '' ? null : Number(val));
        else if (f.kind === 'csv') val = (val.trim() === '' ? [] : val.split(',').map(s => s.trim()).filter(Boolean));
        M.setField(kind, part.id, f.key, val);
        autosave();
      });
      row.appendChild(input);
      inspectorEl.appendChild(row);
    }
    const del = el('button', { style: btnStyle(), onclick: () => { M.removeNode(part.id); autosave(); } }, ['delete part']);
    inspectorEl.appendChild(el('div', { style: 'padding:8px' }, [del]));
  }

  // ---- the layer panel (show/hide, lock, reorder) ----
  function renderLayers() {
    if (!layersEl) return;
    layersEl.innerHTML = '';
    const head = el('div', { style: 'display:flex;justify-content:space-between;align-items:center;padding:4px 8px' }, [
      el('strong', { style: `color:${PALETTE.text};font-size:12px` }, ['layers']),
      el('button', { style: btnStyle(), onclick: () => { M.addLayer(); autosave(); } }, ['+ layer']),
    ]);
    layersEl.appendChild(head);
    const sorted = M.layersByZ();
    for (let i = sorted.length - 1; i >= 0; i--) {   // top band first
      const l = sorted[i];
      const row = el('div', { style: `display:flex;gap:4px;align-items:center;padding:3px 8px;font-size:12px;color:${PALETTE.text}` });
      const vis = el('button', { title: 'show/hide', style: btnStyle(), onclick: () => { M.setLayerVisible(l.id, l.visible === false); renderAll(); autosave(); } }, [l.visible === false ? '🚫' : '👁']);
      const lock = el('button', { title: 'lock/unlock', style: btnStyle(), onclick: () => { M.setLayerLocked(l.id, !l.locked); renderAll(); autosave(); } }, [l.locked ? '🔒' : '🔓']);
      const up = el('button', { title: 'raise z', style: btnStyle(), onclick: () => { M.reorderLayer(l.id, +1); autosave(); } }, ['↑']);
      const dn = el('button', { title: 'lower z', style: btnStyle(), onclick: () => { M.reorderLayer(l.id, -1); autosave(); } }, ['↓']);
      row.appendChild(vis); row.appendChild(lock);
      row.appendChild(el('span', { style: 'flex:1' }, [`${l.label} (z${l.z})`]));
      row.appendChild(up); row.appendChild(dn);
      layersEl.appendChild(row);
    }
  }

  function inputStyle() { return `flex:1;background:${PALETTE.surface};color:${PALETTE.text};border:1px solid ${PALETTE.stroke};border-radius:3px;padding:2px 4px;font-family:ui-monospace,monospace`; }
  function btnStyle() { return `background:${PALETTE.panel};color:${PALETTE.text};border:1px solid ${PALETTE.stroke};border-radius:3px;padding:2px 6px;cursor:pointer;font-size:11px`; }

  function renderAll() { renderStage(); renderInspector(); renderLayers(); }
  M.onChange(() => { renderStage(); renderInspector(); renderLayers(); });
  M.onChange(autosave);

  // ---- file import / export, export-through-the-gate ----
  const api = {
    model: M,
    render: renderAll,
    loadSpec(spec) { M.fromJSON(normalize(spec)); status('loaded spec'); },
    importFile(file) {
      const fr = new FileReader();
      fr.onload = () => { try { const g = JSON.parse(fr.result); if (M.fromJSON(normalize(g))) status('imported ' + (file.name || 'spec')); else status('import refused: not a spec'); } catch (e) { status('import failed: ' + e.message); } };
      fr.readAsText(file);
    },
    exportSpec() {
      // the export-through-the-gate path: refuse a spec the gate would refuse.
      const issues = M.preflight();
      if (issues.length) {
        status(`export REFUSED — ${issues.length} canon violation(s): ` + issues.map(i => `[${i.principle}] ${i.message} (${i.ctx})`).join(' · '));
        return null;
      }
      const spec = M.toJSON();
      const text = JSON.stringify(spec, null, 2);
      download((spec.title || 'diagram').replace(/[^a-z0-9]+/gi, '-').toLowerCase() + '.spec.json', text);
      status('exported spec — gate it + render: python diagrams/qa.py <spec> && python diagrams/compose.py <spec>');
      return spec;
    },
  };
  function download(name, text) {
    const a = el('a', { href: URL.createObjectURL(new Blob([text], { type: 'application/json' })), download: name });
    document.body.appendChild(a); a.click(); a.remove();
  }

  renderAll();
  return api;
}

// ════════════════════════ exports ════════════════════════
const EXPORTS = { canvas: DiagramCanvas, createModel, normalize, serialize, serializeNode,
                  layerMembershipIssues, fieldsFor, getPath, setPath, PART_TYPES, ACCENTS, STARTER };
if (typeof window !== 'undefined') window.DiagramCanvas = EXPORTS;
if (typeof module !== 'undefined' && module.exports) module.exports = EXPORTS;
})();
