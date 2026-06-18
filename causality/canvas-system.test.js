/* canvas-system.test.js — §10 teeth for the canvas design system (done-line 0103).
   Run: node causality/canvas-system.test.js
   The teeth: validate() must REFUSE a primitive absent from the tables (a
   fabricated/hand-rolled one fails), every facet must be fully specified, and
   every animation must name a real easing curve — no dangling references. */
'use strict';
const { TOKENS, TABLE, validate, ascii } = require('./canvas-system.js');

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };

console.log('canvas design system — tokens + the refusal teeth\n');

// declared primitives validate
ok(validate('facet', 'actor').ok, 'a declared facet (actor) validates');
ok(validate('line', 'feedback').ok, 'a declared line type (feedback) validates');
ok(validate('anim', 'membrane-breath').ok, 'a declared animation validates');
ok(validate('interact', 'lasso').ok, 'a declared interaction (lasso) validates');

// THE TEETH: a fabricated primitive is refused, with a reason
const bogus = validate('facet', 'sparkleblaster');
ok(!bogus.ok && /not a declared/.test(bogus.reason), 'a fabricated facet is REFUSED with a reason (teeth)');
ok(!validate('line', 'rainbow-laser').ok, 'a fabricated line type is refused');
ok(!validate('nonsense', 'x').ok, 'an unknown table is refused');

// every facet is fully specified (icon + ascii + role + read) — no half-glyphs
let facetsComplete = true;
for (const [k, f] of Object.entries(TOKENS.FACET)) {
  if (!f.icon || !f.ascii || !f.role || !f.read) { facetsComplete = false; console.log('    incomplete facet: ' + k); }
  if (f.role !== 'pigment' && !(f.role in TOKENS.COLOR)) { facetsComplete = false; console.log('    facet ' + k + ' names an undeclared color role: ' + f.role); }
}
ok(facetsComplete, 'every facet is fully specified and names a real color role');

// every animation names a real easing curve (no dangling ease reference)
let animsResolve = true;
for (const [k, a] of Object.entries(TOKENS.ANIM)) {
  if (!(a.ease in TOKENS.EASE)) { animsResolve = false; console.log('    anim ' + k + ' names an undeclared ease: ' + a.ease); }
}
ok(animsResolve, 'every animation names a declared easing curve');

// easing curves are real functions mapping 0..1 sanely
ok(typeof TOKENS.EASE.easeInOut === 'function' && Math.abs(TOKENS.EASE.easeInOut(0)) < 1e-9 && Math.abs(TOKENS.EASE.easeInOut(1) - 1) < 1e-9,
   'easeInOut maps 0->0 and 1->1');

// ASCII fallback exists for every facet (the no-graphics render path)
let asciiComplete = Object.keys(TOKENS.FACET).every(k => ascii(k) && ascii(k) !== '?');
ok(asciiComplete, 'every facet has an ASCII fallback glyph');

// coverage: the capability list bdo named is all present as tables
const need = ['color', 'facet', 'shape', 'line', 'ease', 'anim', 'physics', 'interact', 'lens'];
ok(need.every(t => t in TABLE), 'all named capability tables exist (color/shape/line/anim/easing/physics/interact/lens/facet)');

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
