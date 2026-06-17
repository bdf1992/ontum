/* ingest.test.js — the §10 check for done-line 0096: the canvas ingests the REAL
   committed term-economy projection, and an edge to a term the projection never
   named is REFUSED (no dangling node invented), with teeth.

   Headless and real: it reads the actual committed bytes of
   examples/ontum-terms.projection.json (no fixture, no fabricated data) and
   round-trips the produced graph through the real canvas.js fromJSON/toJSON.

   Run: node causality/ingest.test.js   (exit 0 = passed) */
'use strict';

const fs = require('fs');
const path = require('path');

// minimal globals the canvas engine touches at construction (no rendering)
global.devicePixelRatio = 1;
global.performance = { now: () => 0 };
global.addEventListener = () => {};
function stubEl() {
  const ctx = new Proxy({}, { get: () => () => {} });
  return { getContext: () => ctx, clientWidth: 1280, clientHeight: 720,
           parentElement: { clientWidth: 1280, clientHeight: 720 },
           addEventListener: () => {}, getBoundingClientRect: () => ({ left: 0, top: 0 }),
           style: {}, width: 0, height: 0 };
}

const { projectionToGraph } = require('./ingest.js');
const C = require('./canvas.js');

let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('  ✗ ' + msg); fails++; } else console.log('  ✓ ' + msg); };

// ── the real, committed projection bytes — the arbitrary-but-genuine dataset ──
const PROJ = path.join(__dirname, 'examples', 'ontum-terms.projection.json');
const projection = JSON.parse(fs.readFileSync(PROJ, 'utf8'));
ok(Array.isArray(projection.terms) && projection.terms.length > 0, `read ${projection.terms.length} real terms from committed projection`);

const res = projectionToGraph(projection);
ok(res.ok, 'adapter accepted the real projection');

// every real term became a node carrying its REAL class
const termNames = projection.terms.map(t => t.term).sort();
const sourceNodes = res.graph.nodes.filter(n => n.type === 'source');
ok(sourceNodes.length === projection.terms.length, `one node per real term (${sourceNodes.length} === ${projection.terms.length})`);
const byLabel = new Map(sourceNodes.map(n => [n.label, n]));
let classesMatch = true;
for (const t of projection.terms) { const n = byLabel.get(t.term); if (!n || n.data !== t.class) classesMatch = false; }
ok(classesMatch, 'each term node carries its real class (e.g. arc=overloaded, atom=minted-runtime)');
ok(byLabel.has('arc') && byLabel.get('arc').data === 'overloaded', 'spot-check: real term `arc` ingested as overloaded');

// every resolvable evidence_edge became a link; refused ones did NOT become nodes
const resolvableEdges = projection.evidence_edges.filter(e =>
  projection.terms.some(t => t.id === e.from) && String(e.to).startsWith('evidence:'));
ok(res.graph.links.length === resolvableEdges.length, `links = resolvable evidence edges (${res.graph.links.length} === ${resolvableEdges.length})`);
ok(res.counts.refused === 0, 'the real projection ingests clean (no refusals on honest data)');

// ── the canvas actually loads it: round-trip through the real engine ──
const S = C.canvas(stubEl(), { autoloop: false });
ok(S.fromJSON(res.graph), 'the real canvas engine loaded the ingested graph');
ok(S.nodes.length === res.graph.nodes.length, `engine holds every ingested node (${S.nodes.length})`);
const json = JSON.parse(JSON.stringify(S.toJSON()));
const S2 = C.canvas(stubEl(), { autoloop: false }); S2.fromJSON(json);
const arc2 = S2.nodes.find(n => n.label === 'arc');
ok(arc2 && arc2.data === 'overloaded', 'the real class survived a toJSON/fromJSON reload (persistence holds)');

// ── the teeth (§10): an edge to a term the projection never named is REFUSED ──
// Two locally-fine records — a term list and an edge — that refuse to fit.
const tampered = JSON.parse(JSON.stringify(projection));
const ghostEdge = { id: 'edge:ghost:0', from: 'term:does-not-exist', to: 'evidence:loop/reconcile.py' };
tampered.evidence_edges = tampered.evidence_edges.concat([ghostEdge]);
const tamperedRes = projectionToGraph(tampered);
const drewGhostNode = tamperedRes.graph.nodes.some(n => n.label === 'does-not-exist');
ok(!drewGhostNode, 'teeth: an edge from an absent term invents NO dangling node');
const noticed = tamperedRes.refusals.some(r => r.kind === 'dangling-term' && r.term === 'term:does-not-exist');
ok(noticed, 'teeth: the adapter NOTICES and reports the refusal (it does not pass silently)');
ok(tamperedRes.graph.links.length === res.graph.links.length, 'teeth: the ghost edge produced no link (count unchanged)');

if (fails) { console.error(`\nFAILED — ${fails} check(s)`); process.exit(1); }
console.log('\nPASSED — the canvas ingests real Ontum evidence, with teeth');
