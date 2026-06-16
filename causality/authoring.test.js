/* authoring.test.js — the §10 check for done-line 0083: a schema-valid generated
   spec instantiates; every malformed spec is REFUSED before anything renders.
   Deterministic, no inference (the live describe→generate step is browser-wired).
   Run: node causality/authoring.test.js   (exit 0 = passed) */
'use strict';

// minimal globals so the engine constructs for the instantiate check (never renders)
global.devicePixelRatio = 1; global.performance = { now: () => 0 }; global.addEventListener = () => {};
function stubEl() { const ctx = new Proxy({}, { get: () => () => {} });
  return { getContext: () => ctx, clientWidth: 1280, clientHeight: 720, parentElement: { clientWidth: 1280, clientHeight: 720 }, addEventListener: () => {}, getBoundingClientRect: () => ({ left: 0, top: 0 }), style: {}, width: 0, height: 0 }; }

const C = require('./canvas.js');
const A = require('./authoring.js');
let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('  ✗ ' + msg); fails++; } else console.log('  ✓ ' + msg); };

// 1 — a valid spec passes and instantiates to exactly what it declared (positive control)
const valid = { nodes: [
  { id: 1, type: 'source', label: 'in', x: 100, y: 100, data: 'hi' },
  { id: 2, type: 'code', label: 'shape', x: 300, y: 100, fn: 'uppercase' },
  { id: 3, type: 'inference', label: 'think', x: 500, y: 100, prompt: 'do {{data}}' },
], links: [ { a: 1, b: 2, sign: 1, kind: 'impulse' }, { a: 2, b: 3, sign: 1, kind: 'impulse' } ] };
const vres = A.validateSpec(valid);
ok(vres.ok, 'valid spec validates (' + (vres.errors.join('; ') || 'no errors') + ')');
const S = C.canvas(stubEl(), { autoloop: false });
ok(A.validateSpec(valid).ok && S.fromJSON(valid), 'valid spec instantiates');
ok(S.nodes.length === 3 && S.links.length === 2, `instantiated 3 nodes / 2 links (got ${S.nodes.length}/${S.links.length})`);
ok(S.byId(3) && S.byId(3).prompt === 'do {{data}}', 'a generated config field landed on the node');

// 2..5 — malformed specs are REFUSED (the teeth: each negative control must fail validation)
const bad = {
  'unknown type': { nodes: [{ id: 1, type: 'wizard', label: 'x', x: 1, y: 1 }], links: [] },
  'dangling edge': { nodes: [{ id: 1, type: 'source', label: 'a', x: 1, y: 1 }], links: [{ a: 1, b: 99 }] },
  'non-schema field': { nodes: [{ id: 1, type: 'source', label: 'a', x: 1, y: 1, bogus: 5 }], links: [] },
  'incompatible ports': { nodes: [{ id: 1, type: 'pen', label: 'p', x: 1, y: 1 }, { id: 2, type: 'inference', label: 'i', x: 2, y: 2 }], links: [{ a: 1, b: 2 }] },
  'not an object': 'a graph please',
  'nodes not array': { nodes: 'two' },
};
for (const [name, spec] of Object.entries(bad)) {
  const r = A.validateSpec(spec);
  ok(!r.ok && r.errors.length > 0, `refused: ${name} (${r.errors[0] || 'no reason!'})`);
}

// teeth check — the validator is not a constant: it accepts the valid and rejects the bad
ok(A.validateSpec(valid).ok && !A.validateSpec(bad['unknown type']).ok, 'validator discriminates (not a constant pass/fail)');

// prompt + extractor sanity
ok(/source|inference|pen/.test(A.buildPrompt('a search agent')), 'buildPrompt carries the type vocabulary');
ok(A.extractJSON('sure! {"nodes":[],"links":[]} done')  && A.extractJSON('nope') === null, 'extractJSON pulls JSON from prose, null on none');

if (fails) { console.error(`\nFAILED — ${fails} check(s)`); process.exit(1); }
console.log('\nPASSED — NL→graph authoring validates with teeth: valid instantiates, malformed refused');
