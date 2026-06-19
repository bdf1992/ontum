/* canvas-system.test.js — §10 teeth for the canvas design system (done-line 0103).
   Run: node causality/canvas-system.test.js
   The teeth: validate() must REFUSE a primitive absent from the tables (a
   fabricated/hand-rolled one fails), every facet must be fully specified, and
   every animation must name a real easing curve — no dangling references. */
'use strict';
const fs = require('fs');
const path = require('path');
const { TOKENS, TABLE, validate, ascii, RELATION, composeRelation, flipRelation } = require('./canvas-system.js');

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };

console.log('canvas design system — tokens + the refusal teeth\n');

// declared primitives validate
ok(validate('facet', 'actor').ok, 'a declared facet (actor) validates');
ok(validate('line', 'feedback').ok, 'a declared line type (feedback) validates');
ok(validate('anim', 'membrane-breath').ok, 'a declared animation validates');
ok(validate('interact', 'lasso').ok, 'a declared interaction (lasso) validates');
ok(validate('build', 'mock').ok, 'a declared construction state (mock) validates');

// THE TEETH: a fabricated primitive is refused, with a reason
const bogus = validate('facet', 'sparkleblaster');
ok(!bogus.ok && /not a declared/.test(bogus.reason), 'a fabricated facet is REFUSED with a reason (teeth)');
ok(!validate('line', 'rainbow-laser').ok, 'a fabricated line type is refused');
ok(!validate('build', 'shipped').ok, 'a fabricated construction state is refused (teeth)');
ok(!validate('nonsense', 'x').ok, 'an unknown table is refused');

// the construction-state (game-dev missing-texture) rule is fully specified:
// `real` is the only un-flagged state; every FLAGGED state carries a glaring
// color + a tag so it cannot be mistaken for finished (the whole point of the rule)
ok(TOKENS.BUILD.real && TOKENS.BUILD.real.flag === false, 'BUILD.real is the one un-flagged (renders normally) state');
let buildFlagsComplete = true;
for (const [k, b] of Object.entries(TOKENS.BUILD)) {
  if (b.flag && (!b.color || !b.tag)) { buildFlagsComplete = false; console.log('    flagged build state ' + k + ' lacks a color or tag'); }
}
ok(buildFlagsComplete, 'every flagged construction state wears a hazard color + a tag (cannot be mistaken for finished)');

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
const need = ['color', 'facet', 'shape', 'line', 'ease', 'anim', 'physics', 'interact', 'lens', 'build'];
ok(need.every(t => t in TABLE), 'all named capability tables exist (color/shape/line/anim/easing/physics/interact/lens/facet/build)');

// ── RELATION — type-by-composition for EDGES (iterations 0008). The teeth: a
//    relation's label is GENERATED from (fromFacet, toFacet, valence), never
//    hand-authored; the flip is a generative involution (flip(flip(r)) == r);
//    an undeclared triple is REFUSED; and a constant/fabricated generator fails. ──
console.log('\nrelation composition — generative ends + the perspective flip (teeth)\n');

// a known facet-pair generates its EXPECTED label (not a free string)
ok(composeRelation('signal', 'state', '-').label === 'blocks', "(signal, state, -) generates 'blocks' (a known pair → its expected label)");
ok(composeRelation('state', 'objective', '+').label === 'satisfies', "(state, objective, +) generates 'satisfies'");
ok(composeRelation('source', 'state', '+').label === 'feeds', "(source, state, +) generates 'feeds'");
ok(composeRelation('state', 'actor', 'fades').label === 'wakes', "(state, actor, fades) generates 'wakes' (the corrected cat-chain)");

// THE TEETH: an undeclared triple is REFUSED — a label has no home outside the
// table, so it can never be hand-authored at a call site
const refused = composeRelation('signal', 'state', 'sparkle');
ok(refused === null, 'an undeclared valence is REFUSED (null) — a label is never hand-rolled (teeth)');
ok(composeRelation('blarg', 'state', '+') === null, 'an undeclared from-facet is refused');

// the flip is a GENERATIVE transform producing the typed dual, and an involution
const r = composeRelation('signal', 'state', '-');
const f = flipRelation(r);
ok(f.from === 'state' && f.to === 'signal' && f.label === 'is blocked by', "flip(blocks) is the typed dual 'is blocked by', endpoints swapped");
const ff = flipRelation(f);
ok(JSON.stringify(ff) === JSON.stringify(r), 'flip(flip(r)) deep-equals r (the perspective flip is an involution)');

// NEGATIVE CONTROL: a constant/fabricated generator (same label for everything)
// cannot pass the expected-label assertions above — the separation has teeth
const constantGen = () => ({ type: 'x', label: 'relates', inverse: 'relates' });
ok(!(constantGen('signal', 'state', '-').label === 'blocks'), 'negative control: a constant generator does NOT produce the expected label (teeth)');

// COVERAGE + no-hand-authored-labels: every relation the corpus declares resolves
// through the generator, and NOT ONE carries a hand-authored label or build flag
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'phrases.json'), 'utf8'));
let everyRelComposes = true, noHandLabels = true;
for (const ph of P.phrases) for (const rel of ph.relations) {
  if ('label' in rel || 'build' in rel) { noHandLabels = false; console.log(`    ${ph.id}: relation ${rel.from}→${rel.to} carries a hand-authored label/build flag`); }
  const ff2 = String(rel.from).split('.')[1], tf2 = String(rel.to).split('.')[1];
  const c = composeRelation(ff2, tf2, rel.valence);
  if (!c) { everyRelComposes = false; console.log(`    ${ph.id}: (${ff2}, ${tf2}, ${rel.valence}) has no composed relation`); }
}
ok(noHandLabels, 'no corpus relation carries a hand-authored label or build flag (the generator is the only source)');
ok(everyRelComposes, 'every corpus relation resolves through composeRelation (full coverage — the generator covers the portfolio)');

// every RELATION entry is fully specified (type + label + inverse) — no half-edges
let relsComplete = true;
for (const [k, e] of Object.entries(RELATION)) {
  if (!e.type || !e.label || !e.inverse) { relsComplete = false; console.log('    incomplete relation: ' + k); }
  if (k.split('|').length !== 3) { relsComplete = false; console.log('    malformed relation key (want from|to|valence): ' + k); }
}
ok(relsComplete, 'every RELATION entry is fully specified (type + label + inverse) under a from|to|valence key');

// 'relation' is a declared table, so validate() also gates it
ok(validate('relation', 'signal|state|-').ok, "validate('relation', …) accepts a declared composition");
ok(!validate('relation', 'signal|state|sparkle').ok, 'validate refuses an undeclared composition');

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
