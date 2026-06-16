/* canvas.js — Causality's typed pulse-routing engine, homed in ontum (done-line
   0082). Ported from the experience-foundry prototype and made the one solution:
   schema-driven (one SCHEMA drives defaults + inspector + persistence), with a
   node model widened to carry the holonic display fields the full vision lands on
   (sites / space / strata / anima — see causality/display-system.md).

   Nodes and routes are IO CHANNELS (a node = a pen: required fields, an
   operation, a typed out). A pulse is a MESSAGE carrying data; a node ACTIVATES
   when a compatible pulse arrives and sets its point by COMPUTING or INFERRING.

   Node types (what a channel DOES on arrival):
     stock/source/sink/code/inference/gate/pointer/pen/card/readout
   Routes are typed wires; an incompatible wire is refused (the seam contract).
   No deps. window.Causality.canvas(el, opts) -> controller.
*/
(function () {
'use strict';
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const TAU = Math.PI * 2;
const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());

const PIGMENT = ['#0e8a7b', '#b8742c', '#7a5ba6', '#bf4a3e', '#3f7cb6', '#6b8f3c'];
const INK = '#2b2a33', DIM = '#8d8678', PAPER = '#f6f1e7', HOT = '#d4543f', THINK = '#7a5ba6';

const TYPES = ['stock', 'source', 'sink', 'code', 'inference', 'gate', 'pointer', 'pen', 'card', 'readout'];
const GLYPH = { stock: '○', source: '▷', sink: '▽', code: 'ƒ', inference: '✦', gate: '⊟', pointer: '↪', pen: '✎', card: '▭', readout: '▥' };
// typed ports: what a node consumes / produces. a route is legal if out ⊇ in.
const PORTS = {
  stock: ['signal', 'signal'], source: ['any', 'any'], sink: ['signal', 'signal'],
  code: ['any', 'any'], inference: ['text', 'text'], gate: ['any', 'any'],
  pointer: ['any', 'any'], pen: ['any', 'receipt'], card: ['any', 'any'], readout: ['any', 'any'],
};
const assignable = (out, inn) => out === 'any' || inn === 'any' || out === inn || inn === 'signal' || out === 'signal';

const LINK_KINDS = ['impulse', 'delayed', 'proportional', 'leak'];
const POKES = { tap: { mag: 0.22 }, hold: { mag: 0.10, repeat: 6, every: 0.18 }, burst: { mag: 0.40 } };

const BRIDGE = (typeof window !== 'undefined' && window.CAUSALITY_BRIDGE) || 'http://localhost:8378/infer';

// deterministic builtin code fns (a node picks one, or writes its own body)
const FNS = {
  'build search query': d => 'site search: "' + String(d || '').trim().replace(/\s+/g, ' ').slice(0, 80) + '"',
  'uppercase': d => String(d || '').toUpperCase(),
  'word count': d => String(d || '').trim().split(/\s+/).filter(Boolean).length,
  'first sentence': d => String(d || '').split(/(?<=[.!?])\s/)[0] || '',
  'passthrough': d => d,
};

// ───────────── the type SCHEMA (one source for defaults + inspector + persistence) ─────────────
// kind: text | textarea | number | bool | select | ref | csv. `opts` is a list or
// a () => list. Every field here is what the inspector shows/edits and what
// toJSON serializes — a new node type ships as a SCHEMA entry, not new code.
const F = (key, label, kind, def, extra = {}) => Object.assign({ key, label, kind, def }, extra);
const COMMON = [F('label', 'label', 'text', 'thing'), F('expectedMs', 'expected ms', 'number', null)];
const SCHEMA = {
  stock:     [F('level', 'level', 'number', 0.5), F('drift', 'drift', 'number', null)],
  source:    [F('data', 'seed data', 'textarea', null), F('every', 'every (s)', 'number', 0.9), F('rate', 'rate', 'number', 0.14), F('autorun', 'autorun', 'bool', false)],
  sink:      [F('drain', 'drain', 'number', 0.10)],
  code:      [F('fn', 'builtin', 'select', 'passthrough', { opts: () => Object.keys(FNS) }), F('body', 'custom body (data)=>', 'textarea', null)],
  inference: [F('backend', 'backend', 'select', 'ollama', { opts: ['ollama', 'claude'] }), F('model', 'model', 'text', null), F('prompt', 'prompt ({{data}})', 'textarea', 'Answer briefly: {{data}}')],
  gate:      [F('gate.mode', 'mode', 'select', 'pass', { opts: ['pass', 'reject', 'hold', 'amend'] }), F('gate.cond', 'condition (data)=>bool', 'text', '')],
  pointer:   [F('ref', 'target node id', 'ref', null)],
  pen:       [F('required', 'required fields', 'csv', [])],
  card:      [F('card.title', 'title', 'text', 'setpoint')],
  readout:   [F('watch', 'watch node id', 'ref', null)],
};
// the holonic display fields every node carries (display-system.md C5/C7/C18); declared
// now, populated by a later piece. Serialized so they survive a reload.
const HOLONIC = [
  F('strata.fundamental', 'fundamental (addr)', 'text', null),
  F('strata.derived', 'derived (fold)', 'text', null),
  F('strata.learned', 'learned (model)', 'text', null),
  F('anima.strength', 'anima · weak↔strong', 'number', null),
  F('anima.tempo', 'anima · fast↔slow', 'number', null),
];
const EDGE_SCHEMA = [
  F('sign', 'sign (+1/−1)', 'number', 1), F('kind', 'kind', 'select', 'impulse', { opts: LINK_KINDS }),
  F('gain', 'gain', 'number', 1), F('delay', 'delay', 'number', 1),
];
// dotted-path get/set so the schema can address nested config (gate.mode, anima.strength)
const getPath = (o, key) => key.split('.').reduce((v, k) => (v == null ? v : v[k]), o);
const setPath = (o, key, val) => { const ks = key.split('.'); const last = ks.pop();
  let t = o; for (const k of ks) { if (t[k] == null || typeof t[k] !== 'object') t[k] = {}; t = t[k]; } t[last] = val; };
const fieldsFor = type => [...COMMON, ...(SCHEMA[type] || []), ...HOLONIC];

function Canvas(el, opts = {}) {
  opts = opts || {};
  const cx = el.getContext('2d');
  const S = {
    el, cx, W: 0, H: 0, t: 0, energy: 0, active: true,
    nodes: [], links: [], pulses: [], rings: [], floats: [], receipts: [],
    nextId: 1, baseline: 0.5, drift: 0.05, regen: true, poke: 'tap',
    hoverNode: null, hoverLink: null, drag: null, bridge: opts.bridge || BRIDGE,
    selected: null,   // {kind:'node'|'edge', ref} — what the inspector edits
    perms: Object.assign({ create: true, link: true, flip: true, move: true, rename: true, erase: true, tap: true, type: true, setline: true }, opts.perms || {}),
    onchange: opts.onchange || null, onevent: opts.onevent || null, onselect: opts.onselect || null,
  };
  const ev = (k, o) => S.onevent && S.onevent(k, o);
  const changed = () => S.onchange && S.onchange(S);
  S.select = (kind, ref) => { S.selected = ref ? { kind, ref } : null; S.onselect && S.onselect(S.selected, S); };

  const DPR = () => Math.min(2, devicePixelRatio || 1);
  const resize = () => {
    const d = DPR();
    S.W = el.clientWidth || el.parentElement.clientWidth;
    S.H = opts.height || el.clientHeight || el.parentElement.clientHeight;
    el.width = S.W * d; el.height = S.H * d;
    if (opts.height) el.style.height = S.H + 'px';
    cx.setTransform(d, 0, 0, d, 0, 0);
  };
  addEventListener('resize', resize); resize();
  const byId = id => S.nodes.find(n => n.id === id); S.byId = byId;

  // ───────────── model ─────────────
  S.node = (x, y, label, o = {}) => {
    const id = o.id != null ? o.id : S.nextId++;
    if (id >= S.nextId) S.nextId = id + 1;
    const n = {
      id, x, y, label: label || o.label || 'thing', type: o.type || 'stock',
      hue: o.hue || PIGMENT[id % PIGMENT.length],
      level: o.level != null ? o.level : 0.5, target: o.level != null ? o.level : 0.5,
      drift: o.drift != null ? o.drift : null, wob: (id * 7.13) % 100, was: o.was || null,
      // typed-channel config
      data: o.data != null ? o.data : null,
      fn: o.fn || 'passthrough', body: o.body || null,
      prompt: o.prompt || 'Answer briefly: {{data}}',
      model: o.model || null, backend: o.backend || 'ollama',
      gate: o.gate || { mode: 'pass', cond: '' },
      ref: o.ref != null ? o.ref : null,
      required: o.required || [],
      setline: o.setline || null, watch: o.watch != null ? o.watch : null,
      card: o.card || null, autorun: o.autorun || false,
      // analog (stock/source/sink)
      rate: o.rate != null ? o.rate : 0.14, every: o.every != null ? o.every : 0.9, clock: 0,
      boundTo: o.boundTo != null ? o.boundTo : null, drain: o.drain != null ? o.drain : 0.10,
      // holonic display fields (display-system.md) — declared, populated later
      sites: o.sites || [], space: o.space || null,
      strata: o.strata || { fundamental: null, derived: null, learned: null },
      anima: o.anima || { strength: null, tempo: null },
      // temporal expectations — measured, improved over time
      expectedMs: o.expectedMs != null ? o.expectedMs : (o.type === 'inference' ? 12000 : o.type === 'pen' ? 400 : 30),
      lastMs: null, avgMs: null, runs: 0, busy: false, lastOut: null, verdict: null,
      history: [],
    };
    S.nodes.push(n); return n;
  };
  S.link = (a, b, o = {}) => {
    const A = byId(a), B = byId(b);
    if (A && B && !assignable(PORTS[A.type][1], PORTS[B.type][0])) {
      S.floats.push({ x: (A.x + B.x) / 2, y: (A.y + B.y) / 2, t: 0, txt: PORTS[A.type][1] + ' ⇏ ' + PORTS[B.type][0], col: HOT });
      ev('refused-link', { a, b }); return null;
    }
    const l = { a, b, sign: o.sign != null ? o.sign : 1, kind: o.kind || 'impulse',
                gain: o.gain != null ? o.gain : 1, delay: o.delay != null ? o.delay : 1,
                wob: (a * 13.7 + b) % 100, strain: 0 };
    S.links.push(l); return l;
  };
  S.clear = () => { S.nodes = []; S.links = []; S.pulses = []; S.rings = []; S.floats = []; S.nextId = 1; S.select(null); changed(); };

  // ───────────── persistence (toJSON / fromJSON) — done-line 0082 ─────────────
  // schema-driven: serialize exactly the fields the SCHEMA + HOLONIC declare, plus
  // identity/geometry. A reload through fromJSON restores the graph the user built.
  const SAVE_VERSION = 1;
  S.toJSON = () => ({
    version: SAVE_VERSION, baseline: S.baseline, nextId: S.nextId,
    nodes: S.nodes.map(n => {
      const o = { id: n.id, x: Math.round(n.x), y: Math.round(n.y), type: n.type, hue: n.hue };
      for (const f of fieldsFor(n.type)) { const v = getPath(n, f.key); if (v != null) setPath(o, f.key, v); }
      if (n.setline) o.setline = n.setline; if (n.card) o.card = n.card;
      if (n.boundTo != null) o.boundTo = n.boundTo;
      return o;
    }),
    links: S.links.map(l => ({ a: l.a, b: l.b, sign: l.sign, kind: l.kind, gain: l.gain, delay: l.delay })),
  });
  S.fromJSON = (g) => {
    if (!g || !Array.isArray(g.nodes)) return false;
    S.nodes = []; S.links = []; S.pulses = []; S.rings = []; S.floats = []; S.nextId = 1; S.select(null);
    if (g.baseline != null) S.baseline = g.baseline;
    for (const o of g.nodes) S.node(o.x, o.y, o.label, o);
    if (g.nextId != null) S.nextId = Math.max(S.nextId, g.nextId);
    for (const l of (g.links || [])) S.link(l.a, l.b, l);
    changed(); return true;
  };

  S.cycles = () => {
    const out = [];
    const walk = (start, at, path, seen) => {
      for (const e of S.links) { if (e.a !== at) continue;
        if (e.b === start && path.length) { out.push([...path, e]); continue; }
        if (seen.has(e.b) || path.length > 6) continue;
        seen.add(e.b); walk(start, e.b, [...path, e], seen); seen.delete(e.b); } };
    for (const n of S.nodes) walk(n.id, n.id, [], new Set([n.id]));
    return out;
  };
  S.cycleProducts = () => S.cycles().map(c => c.reduce((p, e) => p * e.sign, 1));

  // ───────────── ink (wobble bound to system energy) ─────────────
  const amp = (k = 1) => (0.4 + S.energy * 1.9) * k;
  const wob = (x, y, seed, k = 1) => { const a = amp(k);
    return [x + Math.sin(seed * 12.9898 + S.t * 1.1) * a, y + Math.cos(seed * 78.233 + S.t * 0.85) * a]; };
  S.inkLine = (pts, seed, color, width = 2) => {
    cx.strokeStyle = color; cx.lineWidth = width; cx.lineCap = 'round'; cx.beginPath();
    pts.forEach((p, i) => { const [x, y] = wob(p[0], p[1], seed + i * 0.37); i ? cx.lineTo(x, y) : cx.moveTo(x, y); }); cx.stroke(); };
  S.inkCircle = (x, y, r, seed, color, width = 2.4) => {
    cx.strokeStyle = color; cx.lineWidth = width; cx.lineCap = 'round'; cx.beginPath();
    for (let i = 0; i <= 26; i++) { const a = (i / 26) * TAU + seed;
      const rr = r + Math.sin(a * 3 + seed * 7 + S.t * 0.7) * amp(0.8);
      const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr; i ? cx.lineTo(px, py) : cx.moveTo(px, py); } cx.stroke(); };
  S.caveat = (txt, x, y, size = 18, color = INK, rot = -0.03) => {
    cx.save(); cx.translate(x, y); cx.rotate(rot); cx.fillStyle = color; cx.font = `600 ${size}px "Caveat", cursive`;
    cx.textAlign = 'center'; cx.fillText(txt, 0, 0); cx.restore(); };

  const NODE_R = 40; S.NODE_R = NODE_R;
  const geom = e => { const A = byId(e.a), B = byId(e.b);
    const dx = B.x - A.x, dy = B.y - A.y, d = Math.hypot(dx, dy) || 1;
    const nx = -dy / d, ny = dx / d, bow = Math.min(64, d * 0.22) * (1 - 0.6 * (e.strain || 0));
    const mx = (A.x + B.x) / 2 + nx * bow, my = (A.y + B.y) / 2 + ny * bow;
    const q = tt => [(1-tt)*(1-tt)*A.x + 2*(1-tt)*tt*mx + tt*tt*B.x, (1-tt)*(1-tt)*A.y + 2*(1-tt)*tt*my + tt*tt*B.y];
    return { q, t0: Math.min(0.4, NODE_R / d * 1.1), t1: Math.max(0.6, 1 - (NODE_R + 8) / d * 1.1), A, B, d }; };
  S.geom = geom;

  // ───────────── flow + typed activation ─────────────
  S.firePulse = (nid, mag, data) => {
    const src = byId(nid);
    for (const e of S.links) if (e.a === nid && (e.kind === 'impulse' || e.kind === 'delayed') && S.pulses.length < 240) {
      const speed = e.kind === 'delayed' ? 0.45 / Math.max(0.2, e.delay) : 1.25;
      S.pulses.push({ e, t: 0, mag: mag * e.gain, hue: src && src.hue, speed, data: data !== undefined ? data : (src && src.lastOut), from: nid });
    }
  };
  S.ring = n => S.rings.push({ x: n.x, y: n.y, t: 0, hue: n.hue });

  S.activate = (n, pulse) => {
    const t0 = now();
    const finish = (ms) => { n.lastMs = ms; n.avgMs = n.avgMs == null ? ms : lerp(n.avgMs, ms, 0.3); n.runs++; };
    const sync = (fill, out, emitData) => {
      if (fill != null) n.target = clamp(fill, 0, 1);
      n.lastOut = out !== undefined ? out : (pulse ? pulse.data : null);
      finish(now() - t0); S.ring(n);
      if (emitData !== false) S.firePulse(n.id, 0.2, n.lastOut);
      ev('activate', { node: n.id, type: n.type, ms: n.lastMs }); changed();
    };
    const data = pulse ? pulse.data : n.data;

    switch (n.type) {
      case 'stock': {
        const delta = (pulse ? pulse.mag : 0.2) * (pulse ? signFromTo(pulse.from, n.id) : 1);
        n.target = clamp(n.target + delta, 0, 1);
        n.lastOut = data; finish(now() - t0); S.ring(n);
        const onward = delta * 0.72;
        const drive = Math.max(Math.abs(onward), S.regen ? Math.max(0, Math.abs(n.target - S.baseline) - 0.1) * 0.8 : 0);
        if (drive > 0.045) S.firePulse(n.id, drive * Math.sign(onward || 1), data);
        changed(); return;
      }
      case 'source': return sync(Math.min(1, n.target + 0.3), n.data);
      case 'sink':   { n.target = Math.max(0, n.target - 0.3); finish(now() - t0); S.ring(n); changed(); return; }
      case 'pointer': { finish(now() - t0); S.ring(n); if (n.ref != null) S.firePulse(n.ref, 0.2, data); ev('activate', { node: n.id, type: 'pointer' }); return; }
      case 'code': {
        let out, err = null;
        try { const f = n.body ? new Function('data', n.body) : FNS[n.fn] || FNS.passthrough; out = f(data); }
        catch (e) { err = String(e.message || e); out = null; }
        const fill = typeof out === 'number' ? clamp(out > 1 ? out / 100 : out, 0, 1) : (out != null ? 0.7 : 0.1);
        if (err) { n.verdict = 'err: ' + err; return sync(0.1, null, false); }
        n.verdict = null; return sync(fill, out);
      }
      case 'gate': {
        const g = n.gate || { mode: 'pass' };
        let ok = true;
        if (g.cond) { try { ok = !!new Function('data', 'return (' + g.cond + ')')(data); } catch (e) { ok = false; } }
        n.verdict = g.mode === 'reject' || (g.mode === 'amend' && !ok) ? 'reject' : ok ? 'pass' : 'reject';
        if (n.verdict === 'reject' && pulse && pulse.from != null) {
          finish(now() - t0); n.target = 0.85; S.floats.push({ x: n.x, y: n.y - 56, t: 0, txt: 'rejected ↩', col: HOT });
          backflow(n, pulse, data); ev('reject', { node: n.id }); changed(); return;
        }
        return sync(0.55, data);
      }
      case 'pen': {
        const missing = (n.required || []).filter(f => !(data && typeof data === 'object' && f in data));
        if (missing.length) { n.verdict = 'needs: ' + missing.join(', '); return sync(0.15, null, false); }
        n.verdict = null; const receipt = { node: n.label, at: Math.round(S.t * 1000), data };
        S.receipts.push(receipt); S.floats.push({ x: n.x, y: n.y - 56, t: 0, txt: '✎ ' + n.label, col: '#b8412e' });
        ev('pen', receipt); return sync(0.9, receipt);
      }
      case 'inference': {
        if (n.busy) return; n.busy = true; n.verdict = null;
        const prompt = (n.prompt || '{{data}}').replace('{{data}}', String(data == null ? '' : (typeof data === 'object' ? JSON.stringify(data) : data)));
        const body = JSON.stringify({ prompt, backend: n.backend, model: n.model, timeout: 120 });
        S.floats.push({ x: n.x, y: n.y - 56, t: 0, txt: 'thinking…', col: THINK });
        fetch(S.bridge, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body })
          .then(r => r.json())
          .then(j => { n.busy = false;
            if (j.error) { n.verdict = 'err'; n.target = 0.15; n.lastMs = j.ms; S.floats.push({ x: n.x, y: n.y - 56, t: 0, txt: 'error', col: HOT }); changed(); return; }
            n.lastMs = j.ms; n.avgMs = n.avgMs == null ? j.ms : lerp(n.avgMs, j.ms, 0.3); n.runs++;
            n.target = 0.9; n.lastOut = j.result; S.ring(n);
            S.firePulse(n.id, 0.25, j.result);
            ev('inference', { node: n.id, ms: j.ms, model: (j.meta && j.meta.model) }); changed();
          })
          .catch(e => { n.busy = false; n.verdict = 'bridge down'; n.target = 0.15;
            S.floats.push({ x: n.x, y: n.y - 56, t: 0, txt: 'bridge down', col: HOT }); changed(); });
        changed(); return;
      }
      default: { finish(now() - t0); return; }
    }
  };
  function signFromTo(a, b) { const e = S.links.find(l => l.a === a && l.b === b); return e ? e.sign : 1; }
  function backflow(n, pulse, data) {
    const back = S.links.find(l => l.a === n.id && l.b === pulse.from) || { a: n.id, b: pulse.from, sign: -1, kind: 'impulse', wob: 1, strain: 0 };
    S.pulses.push({ e: back, t: 0, mag: 0.2, hue: HOT, speed: 1.6, data, from: n.id, reject: true });
  }

  S.pulseNode = (n, pokeName) => {
    const pk = POKES[pokeName || S.poke] || POKES.tap;
    S.activate(n, { data: n.data, mag: pk.mag, from: null });
    if (pk.repeat) { let k = 1; const iv = setInterval(() => { if (k++ >= pk.repeat || !byId(n.id)) return clearInterval(iv); S.activate(n, { data: n.data, mag: pk.mag, from: null }); }, (pk.every || 0.18) * 1000); }
  };
  S.inject = (n, data) => { n.data = data; S.activate(n, { data, mag: 0.25, from: null }); };

  S.step = dt => {
    for (const n of S.nodes) {
      const drift = n.drift != null ? n.drift : S.drift;
      n.level += (n.target - n.level) * Math.min(1, dt * 5);
      if (n.type === 'stock' || n.type === 'card') n.target += (S.baseline - n.target) * dt * drift;
      else if (n.type !== 'inference' || !n.busy) n.target += (0.15 - n.target) * dt * 0.12;
      if (n.type === 'source' && n.boundTo == null && n.every > 0 && n.autorun) {
        n.clock += dt; if (n.clock >= n.every) { n.clock = 0; S.activate(n, { data: n.data, mag: n.rate, from: null }); }
      }
      if (n.type === 'source' && n.boundTo != null) { n.clock += dt; if (n.clock >= n.every) { n.clock = 0;
        const tgt = byId(n.boundTo); if (tgt && tgt.setline && tgt.level < tgt.setline.target) S.firePulse(n.id, n.rate, n.data); } }
      if (n.type === 'sink') n.target = Math.max(0, n.target - n.drain * dt);
      n.history.push(n.level); if (n.history.length > 600) n.history.shift();
    }
    let dev = 0; for (const n of S.nodes) dev += Math.abs(n.level - S.baseline);
    for (const e of S.links) { const A = byId(e.a), B = byId(e.b); if (!A || !B) continue;
      if (e.kind === 'proportional') B.target = clamp(B.target + (A.level - S.baseline) * e.sign * e.gain * dt * 0.9, 0, 1);
      else if (e.kind === 'leak') { const f = Math.max(0, A.level - 0.04) * e.gain * dt * 0.5; A.target = clamp(A.target - f, 0, 1); B.target = clamp(B.target + f * e.sign, 0, 1); } }
    for (let i = S.pulses.length - 1; i >= 0; i--) { const p = S.pulses[i]; p.t += dt * (p.speed || 1.25);
      if (p.t >= 1) { S.pulses.splice(i, 1); const dst = byId(p.e.b); if (dst) S.activate(dst, p); } }
    for (const e of S.links) { const A = byId(e.a), B = byId(e.b); if (!A || !B) { e.strain = 0; continue; }
      const flux = S.pulses.filter(p => p.e === e).length * 0.25 + (e.kind === 'proportional' ? Math.abs(A.level - S.baseline) : 0);
      const back = S.links.find(o => o.a === e.b && o.b === e.a); const opposed = back && back.sign !== e.sign ? 0.8 : 0;
      const off = B.setline ? Math.abs(B.level - B.setline.target) : 0;
      e.strain += (clamp(flux + opposed * Math.abs(A.level - 0.5) + off, 0, 1) - e.strain) * Math.min(1, dt * 4); }
    for (let i = S.floats.length - 1; i >= 0; i--) { S.floats[i].t += dt; if (S.floats[i].t > 2.2) S.floats.splice(i, 1); }
    if (S.nodes.length && !S.energyExternal) S.energy += (clamp(dev / S.nodes.length * 2 + S.pulses.length * 0.08, 0, 1) - S.energy) * Math.min(1, dt * 3);
  };

  S.stats = () => {
    const byType = {}; for (const n of S.nodes) byType[n.type] = (byType[n.type] || 0) + 1;
    const timed = S.nodes.filter(n => n.avgMs != null);
    return {
      nodes: S.nodes.length, links: S.links.length, byType,
      inflight: S.pulses.length, thinking: S.nodes.filter(n => n.busy).length,
      receipts: S.receipts.length,
      latency: timed.map(n => ({ node: n.label, type: n.type, avgMs: Math.round(n.avgMs), expectedMs: n.expectedMs, drift: Math.round(n.avgMs - n.expectedMs) })),
    };
  };

  // ───────────── render ─────────────
  S.render = () => {
    cx.clearRect(0, 0, S.W, S.H);
    const selEdge = S.selected && S.selected.kind === 'edge' ? S.selected.ref : null;
    const selNode = S.selected && S.selected.kind === 'node' ? S.selected.ref : null;
    for (const e of S.links) { const A = byId(e.a), B = byId(e.b); if (!A || !B) continue;
      const g = geom(e); const baseCol = e.sign > 0 ? '#0e8a7b' : HOT; const strain = e.strain || 0;
      const col = strain > 0.04 ? mix(baseCol, HOT, Math.min(0.6, strain * 0.7)) : baseCol;
      const pts = []; for (let s = g.t0; s <= g.t1; s += 0.05) { const [x, y] = g.q(s); const ph = (s - g.t0) / (g.t1 - g.t0);
        const tremor = Math.sin(ph * Math.PI) * Math.sin(S.t * 26 + e.wob) * strain * 7;
        const nx = -(B.y - A.y) / g.d, ny = (B.x - A.x) / g.d; pts.push([x + nx * tremor, y + ny * tremor]); }
      const dash = e.kind === 'delayed' ? [9, 7] : e.kind === 'leak' ? [2, 6] : null; if (dash) cx.setLineDash(dash);
      const hot = e === S.hoverLink || e === selEdge;
      S.inkLine(pts, e.wob, hot ? INK : col, (hot ? 3.4 : 2.2) + (e.kind === 'proportional' ? 1.4 : 0)); cx.setLineDash([]);
      const [hx, hy] = g.q(g.t1), [bx2, by2] = g.q(g.t1 - 0.05); const ang = Math.atan2(hy - by2, hx - bx2);
      cx.strokeStyle = col; cx.lineWidth = 2.2; cx.beginPath(); cx.moveTo(hx, hy);
      cx.lineTo(hx - Math.cos(ang - 0.5) * 13, hy - Math.sin(ang - 0.5) * 13); cx.moveTo(hx, hy);
      cx.lineTo(hx - Math.cos(ang + 0.5) * 13, hy - Math.sin(ang + 0.5) * 13); cx.stroke();
      const [sx, sy] = g.q(0.5), [wx, wy] = wob(sx, sy, e.wob); cx.fillStyle = PAPER; cx.beginPath(); cx.arc(wx, wy, 11, 0, TAU); cx.fill();
      if (e.kind === 'delayed') cx.setLineDash([4, 3]); S.inkCircle(wx, wy, 11, e.wob, hot ? INK : col, e.kind === 'proportional' ? 2.6 : 1.8); cx.setLineDash([]);
      cx.fillStyle = col; cx.font = '700 15px "Space Grotesk"'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillText(e.sign > 0 ? '+' : '−', wx, wy + 1); }
    if (S.drag && S.drag.kind === 'link') S.inkLine([[S.drag.node.x, S.drag.node.y], [S.drag.x, S.drag.y]], 5, DIM, 2);
    for (const p of S.pulses) { const g = geom(p.e); const s = g.t0 + (g.t1 - g.t0) * p.t; const [px, py] = g.q(s);
      const hue = p.reject ? HOT : (p.hue || '#e8a13c'); cx.fillStyle = hue; cx.beginPath(); cx.arc(px, py, 6 + Math.sin(S.t * 14 + p.t * 9) * 1.4, 0, TAU); cx.fill();
      cx.strokeStyle = hue + '66'; cx.lineWidth = 2; cx.beginPath(); cx.arc(px, py, 10, 0, TAU); cx.stroke();
      if (p.data != null && p.t > 0.2 && p.t < 0.8) { cx.fillStyle = DIM; cx.font = '300 8.5px "IBM Plex Mono", monospace'; cx.textAlign = 'center'; cx.fillText(snippet(p.data, 22), px, py - 12); } }
    cx.textAlign = 'center'; cx.textBaseline = 'alphabetic';
    for (const n of S.nodes) {
      if (n.type === 'card') { drawCard(n, n === selNode); continue; } if (n.type === 'readout') { drawReadout(n); continue; }
      const lv = clamp(n.level, 0, 1);
      cx.save(); cx.beginPath(); cx.arc(n.x, n.y, NODE_R - 3, 0, TAU); cx.clip();
      cx.fillStyle = 'rgba(255,252,245,.95)'; cx.fillRect(n.x - NODE_R, n.y - NODE_R, NODE_R * 2, NODE_R * 2);
      cx.fillStyle = lv > 0.78 ? 'rgba(212,84,63,.30)' : n.hue + '40'; const top = n.y + NODE_R - lv * NODE_R * 2;
      cx.beginPath(); cx.moveTo(n.x - NODE_R, n.y + NODE_R);
      for (let xx = -NODE_R; xx <= NODE_R; xx += 4) cx.lineTo(n.x + xx, top + Math.sin(xx * 0.12 + S.t * 2.4 + n.wob) * (1 + S.energy * 2));
      cx.lineTo(n.x + NODE_R, n.y + NODE_R); cx.fill(); cx.restore();
      if (n.setline) { const ty = n.y + NODE_R - n.setline.target * NODE_R * 2; cx.strokeStyle = HOT; cx.lineWidth = 1.6; cx.setLineDash([6, 5]);
        cx.beginPath(); cx.moveTo(n.x - NODE_R - 10, ty); cx.lineTo(n.x + NODE_R + 10, ty); cx.stroke(); cx.setLineDash([]); n._setlineY = ty; }
      if (n.busy) { cx.strokeStyle = THINK; cx.lineWidth = 2; const a0 = S.t * 4;
        cx.beginPath(); cx.arc(n.x, n.y, NODE_R + 8, a0, a0 + 1.8); cx.stroke(); }
      if (n === selNode) { cx.strokeStyle = THINK; cx.lineWidth = 2; cx.setLineDash([3, 4]); cx.beginPath(); cx.arc(n.x, n.y, NODE_R + 12, 0, TAU); cx.stroke(); cx.setLineDash([]); }
      S.inkCircle(n.x, n.y, NODE_R, n.wob, n === S.hoverNode ? '#0e8a7b' : (n.verdict ? HOT : INK), n === S.hoverNode ? 3 : 2.4);
      if (S.perms.link && (S.drag && S.drag.kind === 'link' || (S.hoverNode === n && !S.drag))) {
        cx.strokeStyle = 'rgba(14,138,123,.4)'; cx.lineWidth = 1.5; cx.setLineDash([4, 5]); cx.beginPath(); cx.arc(n.x, n.y, NODE_R * 0.62, 0, TAU); cx.stroke(); cx.setLineDash([]); }
      const bx = n.x - NODE_R + 7, by = n.y - NODE_R + 5; cx.fillStyle = n.hue; cx.font = '600 14px "Space Grotesk"'; cx.textAlign = 'center'; cx.textBaseline = 'middle';
      cx.fillText(GLYPH[n.type], bx, by); n._badge = [bx, by];
      if (!n.editing) { cx.textBaseline = 'alphabetic'; cx.fillStyle = INK; cx.font = '600 18px "Caveat", cursive';
        const words = n.label.split(' '); if (words.length > 2) { const mid = Math.ceil(words.length / 2);
          cx.fillText(words.slice(0, mid).join(' '), n.x, n.y - 6); cx.fillText(words.slice(mid).join(' '), n.x, n.y + 14); } else cx.fillText(n.label, n.x, n.y + 4); }
      cx.font = '500 9px "IBM Plex Mono", monospace'; cx.fillStyle = DIM; cx.textAlign = 'center';
      const lat = n.avgMs != null ? '·' + fmtMs(n.avgMs) : '';
      cx.fillText(n.type + lat, n.x, n.y + NODE_R + 15);
      if (n.verdict) { cx.fillStyle = HOT; cx.font = '600 12px "Caveat", cursive'; cx.fillText(n.verdict, n.x, n.y + NODE_R + 30); }
      if (n === S.hoverNode && n.lastOut != null) { cx.fillStyle = DIM; cx.font = '300 9px "IBM Plex Mono", monospace'; cx.fillText(snippet(n.lastOut, 34), n.x, n.y - NODE_R - 12); }
    }
    for (let i = S.rings.length - 1; i >= 0; i--) { const r = S.rings[i]; r.t += 0.016; if (r.t > 0.8) { S.rings.splice(i, 1); continue; }
      cx.globalAlpha = (1 - r.t / 0.8) * 0.7; cx.strokeStyle = r.hue || '#e8a13c'; cx.lineWidth = 2.5; cx.beginPath(); cx.arc(r.x, r.y, NODE_R + r.t * 90, 0, TAU); cx.stroke(); cx.globalAlpha = 1; }
    for (const f of S.floats) { cx.globalAlpha = clamp(1 - f.t / 2.2, 0, 1); S.caveat(f.txt, f.x, f.y - f.t * 14, 16, f.col || DIM); cx.globalAlpha = 1; }
    S.draw && S.draw(cx);
  };
  function drawCard(n, sel) { const w = 150, h = 96, x = n.x - w / 2, y = n.y - h / 2; cx.save();
    cx.fillStyle = PAPER; cx.fillRect(x, y, w, h); cx.strokeStyle = (sel || n === S.hoverNode) ? INK : '#b8412e'; cx.lineWidth = 2.5; cx.strokeRect(x + 2, y + 2, w - 4, h - 4);
    cx.fillStyle = '#b8412e'; cx.font = '500 9px "IBM Plex Mono", monospace'; cx.textAlign = 'left'; cx.fillText(((n.card && n.card.title) || 'SETPOINT').toUpperCase(), x + 12, y + 20);
    cx.lineWidth = 1; cx.beginPath(); cx.moveTo(x + 12, y + 26); cx.lineTo(x + w - 12, y + 26); cx.stroke();
    const dial = (n.card && n.card.dial) || {}; let yy = y + 42; cx.font = '500 11px "IBM Plex Mono", monospace'; cx.fillStyle = INK;
    for (const k of Object.keys(dial).slice(0, 3)) { cx.fillText(k, x + 12, yy); cx.textAlign = 'right'; cx.fillText(String(dial[k]), x + w - 12, yy); cx.textAlign = 'left'; yy += 16; }
    if (n.card && n.card.by) { cx.fillStyle = DIM; cx.font = '300 8px "IBM Plex Mono", monospace'; cx.fillText(n.card.by, x + 12, y + h - 9); } cx.restore(); }
  function drawReadout(n) { const w = 168, h = 70, x = n.x - w / 2, y = n.y - h / 2;
    const tgt = n.watch != null ? byId(n.watch) : null; const series = (tgt && tgt.history) || n.history; cx.save();
    cx.fillStyle = 'rgba(255,252,245,.7)'; cx.fillRect(x, y, w, h); S.inkLine([[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]], n.wob, 'rgba(43,42,51,.35)', 1.4);
    cx.fillStyle = DIM; cx.font = '300 8.5px "IBM Plex Mono", monospace'; cx.textAlign = 'left'; cx.fillText((tgt ? tgt.label : 'history').toUpperCase(), x + 8, y + 14);
    const hue = (tgt && tgt.hue) || n.hue; cx.strokeStyle = hue; cx.lineWidth = 1.8; cx.beginPath();
    const N = Math.min(series.length, w - 16); for (let i = 0; i < N; i++) { const v = series[series.length - N + i]; const px = x + 8 + i, py = y + h - 8 - v * (h - 22); i ? cx.lineTo(px, py) : cx.moveTo(px, py); } cx.stroke(); cx.restore(); }

  // ───────────── interaction (gesture authoring) ─────────────
  const pos = e => { const r = el.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  const pick = (x, y) => { S.hoverNode = null; S.hoverLink = null;
    for (const n of S.nodes) { const rr = n.type === 'card' ? 80 : n.type === 'readout' ? 86 : NODE_R + 10;
      if (Math.abs(x - n.x) < rr && Math.abs(y - n.y) < (n.type === 'card' ? 52 : n.type === 'readout' ? 40 : rr)) { S.hoverNode = n; return; } }
    for (const e of S.links) { const g = geom(e); for (let s = 0.15; s < 0.9; s += 0.05) { const [px, py] = g.q(s); if (Math.hypot(x - px, y - py) < 12) { S.hoverLink = e; return; } } } };
  el.addEventListener('pointermove', e => { const [x, y] = pos(e);
    if (S.drag && S.drag.kind === 'move') { S.drag.node.x = x; S.drag.node.y = y; S.drag.moved = true; }
    else if (S.drag && S.drag.kind === 'link') { S.drag.x = x; S.drag.y = y; pick(x, y); }
    else if (S.drag && S.drag.kind === 'setline') { const n = S.drag.node; n.setline.target = clamp((n.y + NODE_R - y) / (NODE_R * 2), 0, 1); }
    else pick(x, y); el.style.cursor = S.hoverNode ? 'grab' : S.hoverLink ? 'pointer' : 'crosshair'; });
  el.addEventListener('pointerdown', e => { if (e.button === 2) return; const [x, y] = pos(e); pick(x, y);
    if (S.hoverNode && S.perms.type && S.hoverNode._badge && Math.hypot(x - S.hoverNode._badge[0], y - S.hoverNode._badge[1]) < 13) {
      const n = S.hoverNode; n.type = TYPES[(TYPES.indexOf(n.type) + 1) % TYPES.length];
      n.expectedMs = n.type === 'inference' ? 12000 : n.type === 'pen' ? 400 : 30;
      if (n.type === 'card' && !n.card) n.card = { title: 'setpoint', dial: { budget: 3, cap: 2 }, by: 'you' };
      if (n.type === 'readout' && n.watch == null) { const o = S.nodes.find(m => m !== n && m.type === 'stock'); n.watch = o ? o.id : null; }
      S.drag = { kind: 'consumed' }; S.select('node', n); ev('retype', { node: n.id, type: n.type }); changed(); return; }
    if (S.hoverNode && S.perms.setline && S.hoverNode.setline && S.hoverNode._setlineY != null && Math.abs(y - S.hoverNode._setlineY) < 12 && Math.abs(x - S.hoverNode.x) < NODE_R + 12) { S.drag = { kind: 'setline', node: S.hoverNode }; return; }
    if (S.hoverNode) { const d = Math.hypot(x - S.hoverNode.x, y - S.hoverNode.y);
      const linkable = S.perms.link && S.hoverNode.type !== 'card' && S.hoverNode.type !== 'readout';
      S.drag = (linkable && d > NODE_R * 0.62) ? { kind: 'link', node: S.hoverNode, x, y } : { kind: S.perms.move ? 'move' : 'tap', node: S.hoverNode, sx: x, sy: y }; } });
  el.addEventListener('pointerup', e => { const [x, y] = pos(e);
    if (S.drag && S.drag.kind === 'link') { pick(x, y);
      if (S.hoverNode && S.hoverNode !== S.drag.node && S.hoverNode.type !== 'readout') {
        const exists = S.links.find(l => l.a === S.drag.node.id && l.b === S.hoverNode.id);
        if (exists) { if (S.perms.flip) exists.sign *= -1; } else S.link(S.drag.node.id, S.hoverNode.id, { sign: S.drag.node.type === 'sink' ? -1 : 1 }); changed();
      } else if (Math.hypot(x - S.drag.node.x, y - S.drag.node.y) < NODE_R) S.select('node', S.drag.node);   // tap node = select (inspect), not poke
    } else if (S.drag && S.drag.kind === 'move') { if (!S.drag.moved) S.select('node', S.drag.node); else changed(); }
    else if (S.hoverLink) { S.select('edge', S.hoverLink); }   // click a wire = select it (edit in inspector)
    else if (!S.hoverNode && !S.hoverLink) { S.select(null); }
    S.drag = null; });
  el.addEventListener('dblclick', e => { const [x, y] = pos(e); pick(x, y);
    if (S.hoverNode && S.perms.rename && S.hoverNode.type !== 'card' && S.hoverNode.type !== 'readout') {
      const n = S.hoverNode, inp = ensureRename(), r = el.getBoundingClientRect(); n.editing = true;
      inp.style.display = 'block'; inp.style.left = (r.left + n.x - 65) + 'px'; inp.style.top = (r.top + n.y - 16 + scrollY) + 'px';
      inp.value = n.label; inp.focus(); inp.select();
      inp.onblur = () => { n.label = inp.value || n.label; n.editing = false; inp.style.display = 'none'; S.select('node', n); changed(); };
      inp.onkeydown = ev2 => { if (ev2.key === 'Enter') inp.blur(); if (ev2.key === 'Escape') { inp.value = n.label; inp.blur(); } };
    } else if (!S.hoverNode && S.perms.create) { const n = S.node(x, y, 'new thing'); S.select('node', n); changed(); } });
  el.addEventListener('contextmenu', e => { e.preventDefault(); if (!S.perms.erase) return; const [x, y] = pos(e); pick(x, y);
    if (S.hoverNode) { S.links = S.links.filter(l => l.a !== S.hoverNode.id && l.b !== S.hoverNode.id); S.pulses = S.pulses.filter(p => p.e.a !== S.hoverNode.id && p.e.b !== S.hoverNode.id); S.nodes = S.nodes.filter(n => n !== S.hoverNode); S.select(null); S.hoverNode = null; changed(); }
    else if (S.hoverLink) { S.pulses = S.pulses.filter(p => p.e !== S.hoverLink); S.links = S.links.filter(l => l !== S.hoverLink); S.select(null); S.hoverLink = null; changed(); } });
  let renameEl = null;
  function ensureRename() { if (renameEl) return renameEl; renameEl = document.createElement('input'); renameEl.maxLength = 24;
    renameEl.style.cssText = 'position:fixed;z-index:40;display:none;font-family:"Caveat",cursive;font-size:22px;font-weight:600;border:none;border-bottom:2px solid #2b2a33;background:transparent;color:#2b2a33;outline:none;text-align:center;width:130px;padding:0 4px';
    document.body.appendChild(renameEl); return renameEl; }

  if (opts.autoloop !== false) { let last = now(); (function frame() { const t = now(), dt = Math.min(0.05, (t - last) / 1000); last = t; if (S.active) { S.t += dt; S.step(dt); S.render(); } requestAnimationFrame(frame); })(); }
  return S;
}

function mix(a, b, t) { const p = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const pa = p(a), pb = p(b); return '#' + pa.map((v, i) => Math.round(lerp(v, pb[i], t)).toString(16).padStart(2, '0')).join(''); }
function snippet(d, n) { let s = d == null ? '' : typeof d === 'object' ? JSON.stringify(d) : String(d); return s.length > n ? s.slice(0, n - 1) + '…' : s; }
function fmtMs(ms) { return ms < 1000 ? Math.round(ms) + 'ms' : (ms / 1000).toFixed(1) + 's'; }

// ───────────── templates — named starting systems & agents ─────────────
const TEMPLATES = {
  'blank page': S => S.clear(),
  'ontum controller': S => { S.clear(); const w = S.W, cx = w / 2, cy = S.H / 2, R = Math.min(w, S.H) * 0.30;
    const defs = [['the pile', 0.72], ['heat', 0.4], ['work landed', 0.35], ['owner’s pile', 0.3], ['cool', 0.25]];
    const ns = defs.map((d, i) => { const a = -Math.PI / 2 + i / 5 * TAU; return S.node(cx + Math.cos(a) * R, cy + Math.sin(a) * R * 0.8, d[0], { level: d[1], type: 'stock' }); });
    const [p, h, wk, q, c] = ns; S.link(p.id, h.id, { sign: 1 }); S.link(h.id, wk.id, { sign: 1 }); S.link(wk.id, p.id, { sign: -1 });
    S.link(wk.id, q.id, { sign: 1 }); S.link(q.id, c.id, { sign: 1 }); S.link(c.id, h.id, { sign: -1 }); q.setline = { target: 0.66, tol: 0.1 }; S.onchange && S.onchange(S); },
  'the bathtub': S => { S.clear(); const cx = S.W / 2, cy = S.H / 2;
    const tap = S.node(cx - 150, cy - 90, 'tap', { type: 'source', rate: 0.16, every: 1.4 });
    const tub = S.node(cx, cy, 'the tub', { type: 'stock', level: 0.3 }); const drain = S.node(cx + 150, cy + 90, 'drain', { type: 'sink', drain: 0.05 });
    tub.setline = { target: 0.62, tol: 0.06 }; tap.boundTo = tub.id; S.link(tap.id, tub.id, { sign: 1 }); S.link(tub.id, drain.id, { sign: 1, kind: 'leak' });
    S.node(cx, cy + 150, 'history', { type: 'readout', watch: tub.id }); S.onchange && S.onchange(S); },
  'search agent': S => { S.clear(); const cx = S.W / 2, cy = S.H / 2;
    const input = S.node(cx - 320, cy, 'user input', { type: 'source', data: 'recursive feedback loops in biology', hue: '#3f7cb6' });
    const q = S.node(cx - 110, cy, 'build query', { type: 'code', fn: 'build search query', hue: '#0e8a7b' });
    const lm = S.node(cx + 110, cy, 'search (local LM)', { type: 'inference', backend: 'ollama', hue: '#7a5ba6',
      prompt: 'You are a research assistant. Give 3 concise bullet leads for this search, no preamble:\n{{data}}' });
    const out = S.node(cx + 330, cy, 'return', { type: 'pen', hue: '#bf4a3e' });
    S.link(input.id, q.id, { sign: 1 }); S.link(q.id, lm.id, { sign: 1 }); S.link(lm.id, out.id, { sign: 1 }); S.onchange && S.onchange(S); },
};

if (typeof window !== 'undefined') window.Causality = { canvas: Canvas, templates: TEMPLATES, PIGMENT, TYPES, LINK_KINDS, POKES, GLYPH, FNS, PORTS, SCHEMA, EDGE_SCHEMA, HOLONIC, fieldsFor, getPath, setPath, assignable };
if (typeof module !== 'undefined' && module.exports) module.exports = { canvas: Canvas, templates: TEMPLATES, SCHEMA, EDGE_SCHEMA, HOLONIC, TYPES, PORTS, LINK_KINDS, fieldsFor, getPath, setPath, assignable };
})();
