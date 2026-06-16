/* inspector.test.js — the §10 check for CZ2 (per-node / per-edge configuration):
   selecting a node renders the config panel FOR ITS TYPE, selecting an edge renders
   the route config, and a field edited THROUGH THE PANEL survives a save→reload
   round-trip. This drives inspector.js's own DOM path — the canvas.persist test
   covers the serialization core; this covers the panel that edits it.

   Headless, no deps: a minimal DOM shim (createElement + addEventListener/fire) lets
   us mount the real inspector and fire the real input events. Teeth: the panel must
   be type-discriminating (an inference panel has no gate field), and a panel edit
   whose commit event never fires must NOT persist (so T3's persistence is caused by
   the commit wiring, not by anything else).

   Run: node causality/inspector.test.js   (exit 0 = passed) */
'use strict';

// ── minimal DOM the inspector touches ────────────────────────────────────────
function makeEl(tag) {
  const el = {
    tagName: tag, children: [], _on: {}, _html: '',
    className: '', textContent: '', htmlFor: '', id: '',
    value: '', checked: false, type: '', placeholder: '', selected: false,
    style: {}, onclick: null,
    classList: { _s: new Set(), add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); }, contains(c) { return this._s.has(c); } },
    appendChild(c) { this.children.push(c); return c; },
    addEventListener(t, h) { (this._on[t] = this._on[t] || []).push(h); },
    fire(t) { (this._on[t] || []).forEach(h => h()); },
  };
  Object.defineProperty(el, 'innerHTML', { get() { return this._html; }, set(v) { this._html = v; this.children = []; } });
  return el;
}
// the engine touches these at construction (no rendering with autoloop off)
global.window = global;
global.document = { createElement: makeEl };
global.devicePixelRatio = 1;
global.performance = { now: () => 0 };
global.addEventListener = () => {};
function stubCanvasEl() {
  const ctx = new Proxy({}, { get: () => () => {} });
  return { getContext: () => ctx, clientWidth: 1280, clientHeight: 720,
           parentElement: { clientWidth: 1280, clientHeight: 720 },
           addEventListener: () => {}, getBoundingClientRect: () => ({ left: 0, top: 0 }),
           style: {}, width: 0, height: 0 };
}

const C = require('./canvas.js');
require('./inspector.js');   // populates window.CausalityInspector via the IIFE
const Inspector = global.CausalityInspector;

let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('  ✗ ' + msg); fails++; } else console.log('  ✓ ' + msg); };

// recursive find: the input element whose id matches, anywhere under the panel
function findById(node, id) {
  if (node.id === id) return node;
  for (const c of node.children) { const hit = findById(c, id); if (hit) return hit; }
  return null;
}
function hasText(node, txt) {
  if (node.textContent === txt) return true;
  return node.children.some(c => hasText(c, txt));
}
// the inspector's own id scheme: 'f_' + key.replace(/\W/g,'_') + '_' + (id ?? 'e')
const fieldId = (key, target) => 'f_' + key.replace(/\W/g, '_') + '_' + (target && target.id != null ? target.id : 'e');

// ── build a graph and mount the real inspector on a panel ─────────────────────
const panel = makeEl('div');
const S = C.canvas(stubCanvasEl(), { autoloop: false });
Inspector.mount(S, panel);
C.templates['search agent'](S);                  // gives an inference node + routes
const lm = S.nodes.find(n => n.type === 'inference');
const gate = S.node(40, 60, 'a gate', { type: 'gate' });   // a second type, to discriminate
const edge = S.links[0];
ok(lm && gate && edge, 'fixture: inference node, gate node, and an edge exist');

// ── T1: per-node config is FOR ITS TYPE (teeth: not a dump of every field) ────
S.select('node', lm);
ok(!!findById(panel, fieldId('prompt', lm)), 'inference panel shows its typed field (prompt)');
ok(!findById(panel, fieldId('gate.mode', lm)), 'inference panel does NOT show another type\'s field (gate.mode)');

S.select('node', gate);
ok(!!findById(panel, fieldId('gate.mode', gate)), 'gate panel shows its typed field (gate.mode)');
ok(!findById(panel, fieldId('prompt', gate)), 'gate panel does NOT show the inference field (prompt)');

// ── T2: per-edge config renders the route's fields ────────────────────────────
S.select('edge', edge);
ok(hasText(panel, 'route'), 'edge selection renders the route panel');
ok(!!findById(panel, fieldId('sign', edge)) && !!findById(panel, fieldId('gain', edge)), 'route panel shows edge-schema fields (sign, gain)');

// ── T3: a NODE field edited through the panel persists across save→reload ─────
S.select('node', lm);
const promptInp = findById(panel, fieldId('prompt', lm));
promptInp.value = 'PANEL-EDITED {{data}}';
promptInp.fire('input');                          // the real commit path: setPath + onchange
const json = JSON.parse(JSON.stringify(S.toJSON()));
const S2 = C.canvas(stubCanvasEl(), { autoloop: false });
S2.fromJSON(json);
const lm2 = S2.nodes.find(n => n.label === lm.label);
ok(lm2 && lm2.prompt === 'PANEL-EDITED {{data}}', 'a node field edited in the panel survived the reload');

// ── T4: an EDGE field edited through the panel persists across save→reload ────
S.select('edge', edge);
const gainInp = findById(panel, fieldId('gain', edge));
gainInp.value = '7';
gainInp.fire('input');
const json2 = JSON.parse(JSON.stringify(S.toJSON()));
const S3 = C.canvas(stubCanvasEl(), { autoloop: false });
S3.fromJSON(json2);
ok(S3.links[0] && S3.links[0].gain === 7, 'an edge field edited in the panel survived the reload');

// ── T5: teeth — a panel edit whose commit event NEVER fires must NOT persist ──
// (proves T3/T4's persistence is caused by the input→commit wiring, not a side effect)
S.select('node', lm);
const promptInp2 = findById(panel, fieldId('prompt', lm));
const committed = lm.prompt;                      // what is on the node right now
promptInp2.value = 'TYPED-BUT-NEVER-FIRED';       // typed into the box, but no event fired
const json3 = JSON.parse(JSON.stringify(S.toJSON()));
const S4 = C.canvas(stubCanvasEl(), { autoloop: false });
S4.fromJSON(json3);
const lm4 = S4.nodes.find(n => n.label === lm.label);
ok(lm4 && lm4.prompt === committed && lm4.prompt !== 'TYPED-BUT-NEVER-FIRED',
   'negative control: an uncommitted edit does NOT persist (the test has teeth)');

if (fails) { console.error(`\nFAILED — ${fails} check(s)`); process.exit(1); }
console.log('\nPASSED — the inspector edits per node and per edge, and edits persist (with teeth)');
