/* diagrams/canvas.persist.test.js — the §10 round-trip check for done-line 0192
   (the editable diagram canvas, first cut). A diagram built in-memory survives a
   save→reload through toJSON/fromJSON: a relabel, an attribute edit (holonic),
   the LAYERS, and a MOVED part's explicit x/y all come back identical. Headless:
   the MODEL is pure (no DOM), so this exercises it directly, the same shape as
   causality/canvas.persist.test.js — with teeth (a negative control that must
   fail to catch a dropped field).

   Run: node diagrams/canvas.persist.test.js   (exit 0 = passed) */
'use strict';

const C = require('./canvas.js');
let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('  ✗ ' + msg); fails++; } else console.log('  ✓ ' + msg); };

// build a diagram: two layers, two parts, an edge.
const M = C.createModel({
  size: [900, 360], title: 'persist fixture',
  layers: [
    { id: 'base', label: 'base', z: 0, visible: true, locked: false },
    { id: 'annotations', label: 'annotations', z: 1, visible: true, locked: false },
  ],
  nodes: [
    { id: 'gate', type: 'rhombus', layer: 'base', x: 80, y: 140, w: 180, h: 70, label: 'value gate' },
    { id: 'stamp', type: 'hex', layer: 'base', x: 380, y: 140, w: 180, h: 70, label: 'owner stamp', accent: 'cool' },
  ],
  edges: [{ from: 'gate', to: 'stamp', layer: 'base' }],
});

// edit: relabel, set a holonic attribute (nested), MOVE a part, retype, re-layer, add a part.
M.setField('node', 'gate', 'label', 'value gate v2');
M.setField('node', 'gate', 'strata.derived', 'loop/node.py:judge');
M.setField('node', 'gate', 'anima.strength', 0.8);
M.moveNode('stamp', 512, 222);                            // explicit x/y written by a drag
M.setField('node', 'stamp', 'layer', 'annotations');     // re-layer (declared membership)
M.addNode(700, 240, { id: 'fresh', type: 'pill', label: 'fresh part', layer: 'base' });
M.setLayerVisible('annotations', false);                 // a layer-panel edit

const beforeNodes = M.spec.nodes.length;
const beforeLayers = M.spec.layers.length;

// round-trip: serialize → reload into a second model.
const json = JSON.parse(JSON.stringify(M.toJSON()));
const M2 = C.createModel({});
ok(M2.fromJSON(json), 'fromJSON restored the diagram');

const gate2 = M2.byId('gate');
const stamp2 = M2.byId('stamp');
const fresh2 = M2.byId('fresh');
ok(M2.spec.nodes.length === beforeNodes, `node count survived (${M2.spec.nodes.length} === ${beforeNodes})`);
ok(M2.spec.layers.length === beforeLayers, `layers survived (${M2.spec.layers.length} === ${beforeLayers})`);
ok(gate2 && gate2.label === 'value gate v2', 'relabel survived the reload');
ok(gate2 && C.getPath(gate2, 'strata.derived') === 'loop/node.py:judge', 'holonic strata.derived survived');
ok(gate2 && C.getPath(gate2, 'anima.strength') === 0.8, 'holonic anima.strength survived');
ok(stamp2 && stamp2.x === 512 && stamp2.y === 222, `moved part x/y survived (${stamp2 && stamp2.x},${stamp2 && stamp2.y})`);
ok(stamp2 && stamp2.layer === 'annotations', 're-layered membership survived');
ok(fresh2 && fresh2.type === 'pill', 'newly added part survived with its type');
const annot = M2.spec.layers.find(l => l.id === 'annotations');
ok(annot && annot.visible === false, 'layer hidden-state survived the reload');
ok(M2.spec.edges.length === M.spec.edges.length, `edges survived (${M2.spec.edges.length})`);

// teeth: a negative control — drop x from the moved part before saving; the
// assert MUST fail to catch it (a clone-only round-trip would silently re-default).
const broken = JSON.parse(JSON.stringify(M.toJSON()));
for (const n of broken.nodes) if (n.id === 'stamp') delete n.x;
const M3 = C.createModel({}); M3.fromJSON(broken);
const stamp3 = M3.byId('stamp');
ok(stamp3 && stamp3.x !== 512, 'negative control: a dropped x is detectably lost (the test has teeth)');

// the export preflight refuses a layer-orphan (the gate would too) — its teeth.
const M4 = C.createModel({
  layers: [{ id: 'base', label: 'base', z: 0 }],
  nodes: [
    { id: 'a', type: 'rect', layer: 'base', x: 20, y: 20, w: 100, h: 50, label: 'a' },
    { id: 'b', type: 'rect', layer: 'ghost-band', x: 200, y: 20, w: 100, h: 50, label: 'b' },
  ],
  edges: [{ from: 'a', to: 'b' }],
});
const issues = M4.preflight();
ok(issues.length === 1 && /C4 containment/.test(issues[0].principle), 'preflight refuses a layer-orphan, citing the canon');
ok(C.createModel(C.STARTER).preflight().length === 0, 'an honest diagram passes the preflight (non-vacuous)');

if (fails) { console.error(`\nFAILED — ${fails} check(s)`); process.exit(1); }
console.log('\nPASSED — diagram canvas persistence round-trip holds, with teeth');
