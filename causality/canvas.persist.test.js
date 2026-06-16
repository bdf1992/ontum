/* canvas.persist.test.js — the §10 check for done-line 0082: a config edit AND a
   newly added node survive a save→reload round-trip through toJSON/fromJSON.
   Headless: stubs just enough DOM to construct the engine (autoloop off, never
   renders), then proves persistence with teeth (a negative control that must fail).

   Run: node causality/canvas.persist.test.js   (exit 0 = passed) */
'use strict';

// minimal globals the engine touches at construction (no rendering happens)
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

const C = require('./canvas.js');
let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('  ✗ ' + msg); fails++; } else console.log('  ✓ ' + msg); };

// build a graph, edit config, add a node
const S = C.canvas(stubEl(), { autoloop: false });
C.templates['search agent'](S);
const before = S.nodes.length;
const lm = S.nodes.find(n => n.type === 'inference');
lm.prompt = 'EDITED PROMPT {{data}}';                       // a typed-config edit
C.setPath(lm, 'anima.strength', 0.8);                       // a holonic field edit
C.setPath(lm, 'strata.derived', 'loop/energy.py:fold');
const added = S.node(10, 20, 'fresh node', { type: 'gate' });
C.setPath(added, 'gate.mode', 'reject');

// round-trip: serialize, wipe into a second engine, restore
const json = JSON.parse(JSON.stringify(S.toJSON()));
const S2 = C.canvas(stubEl(), { autoloop: false });
ok(S2.fromJSON(json), 'fromJSON restored the graph');

const lm2 = S2.nodes.find(n => n.label === 'search (local LM)');
const added2 = S2.nodes.find(n => n.label === 'fresh node');
ok(S2.nodes.length === before + 1, `node count survived (${S2.nodes.length} === ${before + 1})`);
ok(lm2 && lm2.prompt === 'EDITED PROMPT {{data}}', 'edited prompt survived the reload');
ok(lm2 && lm2.anima && lm2.anima.strength === 0.8, 'anima.strength survived the reload');
ok(lm2 && lm2.strata && lm2.strata.derived === 'loop/energy.py:fold', 'strata.derived survived the reload');
ok(added2 && added2.type === 'gate', 'newly added node survived with its type');
ok(added2 && C.getPath(added2, 'gate.mode') === 'reject', 'added node gate.mode survived');
ok(S2.links.length === S.links.length, `routes survived (${S2.links.length})`);

// teeth: a negative control — drop the prompt before saving, the assert MUST fail to catch it
const S3 = C.canvas(stubEl(), { autoloop: false });
C.templates['search agent'](S3);
const broken = JSON.parse(JSON.stringify(S3.toJSON()));
for (const n of broken.nodes) delete n.prompt;             // simulate a serializer that forgets prompt
const S4 = C.canvas(stubEl(), { autoloop: false }); S4.fromJSON(broken);
const lm4 = S4.nodes.find(n => n.label === 'search (local LM)');
ok(lm4 && lm4.prompt !== 'You are a research assistant. Give 3 concise bullet leads for this search, no preamble:\n{{data}}',
   'negative control: a dropped field is detectably lost (the test has teeth)');

if (fails) { console.error(`\nFAILED — ${fails} check(s)`); process.exit(1); }
console.log('\nPASSED — persistence round-trip holds, with teeth');
