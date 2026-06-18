/* phrases.test.js — §10 teeth for the phrase portfolio (done-line 0103).
   Run: node causality/phrases.test.js
   Teeth: every facet a phrase uses must be DECLARED in the canvas design system;
   every relation endpoint must resolve to a real glyph (and facet, if named) — no
   dangling edge; every line type must be a declared LINE; every highlighted glyph
   word must appear in its sentence; and every cross-membrane link must name a
   real glyph in each phrase that genuinely shares the `via` facet. */
'use strict';
const fs = require('fs');
const path = require('path');
const { TOKENS } = require('./canvas-system.js');
const { TRAP_TYPES } = require('./recovery_scorer.js');
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'phrases.json'), 'utf8'));

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };
const FACET = TOKENS.FACET, LINE = TOKENS.LINE;

console.log('phrase portfolio — structure + the no-dangling teeth\n');

ok(P.phrases.length >= 8, `at least 8 phrases (have ${P.phrases.length})`);

const byId = {};
for (const ph of P.phrases) byId[ph.id] = ph;

let allFacetsDeclared = true, allWordsInText = true, allRelsResolve = true, allLinesDeclared = true;
const ref = (ph, r) => { // resolve 'word' or 'word.facet' against a phrase's glyphs
  const [w, f] = r.split('.');
  const g = ph.glyphs.find(x => x.word === w);
  if (!g) return { ok: false, why: `no glyph "${w}"` };
  if (f && !g.facets.includes(f)) return { ok: false, why: `glyph "${w}" has no facet "${f}"` };
  return { ok: true };
};

for (const ph of P.phrases) {
  for (const g of ph.glyphs) {
    for (const f of g.facets) if (!(f in FACET)) { allFacetsDeclared = false; console.log(`    ${ph.id}: glyph "${g.word}" uses undeclared facet "${f}"`); }
    if (!ph.text.toLowerCase().includes(g.word.toLowerCase())) { allWordsInText = false; console.log(`    ${ph.id}: glyph word "${g.word}" not in its sentence`); }
  }
  for (const r of ph.relations) {
    const a = ref(ph, r.from), b = ref(ph, r.to);
    if (!a.ok) { allRelsResolve = false; console.log(`    ${ph.id}: relation from ${r.from} — ${a.why}`); }
    if (!b.ok) { allRelsResolve = false; console.log(`    ${ph.id}: relation to ${r.to} — ${b.why}`); }
    if (!(r.line in LINE)) { allLinesDeclared = false; console.log(`    ${ph.id}: relation line "${r.line}" not a declared LINE type`); }
  }
}
ok(allFacetsDeclared, 'every glyph composes only DECLARED facets (type-by-composition is grounded)');
ok(allWordsInText, 'every highlighted glyph word appears in its sentence (no dangling skin)');
ok(allRelsResolve, 'every relation endpoint resolves to a real glyph/facet (no dangling edge)');
ok(allLinesDeclared, 'every relation names a declared LINE type');

// cross-membrane links: each names a real glyph in each phrase that shares `via`
let linksValid = true;
for (const l of P.links) {
  const A = byId[l.a], B = byId[l.b];
  if (!A || !B) { linksValid = false; console.log(`    link ${l.a}↔${l.b}: missing phrase`); continue; }
  const ga = A.glyphs.find(g => g.word === l.aGlyph), gb = B.glyphs.find(g => g.word === l.bGlyph);
  if (!ga || !gb) { linksValid = false; console.log(`    link ${l.a}↔${l.b}: glyph not found`); continue; }
  if (!(l.via in FACET)) { linksValid = false; console.log(`    link ${l.a}↔${l.b}: via "${l.via}" not a facet`); continue; }
  if (!ga.facets.includes(l.via) || !gb.facets.includes(l.via)) { linksValid = false; console.log(`    link ${l.a}↔${l.b}: glyphs do not both share facet "${l.via}"`); }
}
ok(linksValid, 'every cross-membrane link joins two real glyphs that share the named facet');

// surface_trap teeth (done-line 0105): a declared trap is a PLAUSIBLE MISREADING,
// not nonsense and not a true edge — type declared, endpoints resolve, edge absent
// from the mesh, with a real 'why'. A trap equal to a true edge is no trap.
const trueEdges = (ph) => new Set(ph.relations.map(r => r.from + '→' + r.to));
let trapsValid = true, trapsSeen = 0;
for (const ph of P.phrases) {
  if (!ph.surface_trap) continue;  // a trap is optional — forcing one is the fake-trap failure
  trapsSeen++;
  const t = ph.surface_trap;
  if (!(t.type in TRAP_TYPES)) { trapsValid = false; console.log(`    ${ph.id}: surface_trap.type "${t.type}" is not a declared TRAP_TYPE`); }
  if (!t.edge || !t.edge.from || !t.edge.to) { trapsValid = false; console.log(`    ${ph.id}: surface_trap has no from→to edge`); continue; }
  const a = ref(ph, t.edge.from), b = ref(ph, t.edge.to);
  if (!a.ok) { trapsValid = false; console.log(`    ${ph.id}: trap from ${t.edge.from} — ${a.why}`); }
  if (!b.ok) { trapsValid = false; console.log(`    ${ph.id}: trap to ${t.edge.to} — ${b.why}`); }
  if (trueEdges(ph).has(t.edge.from + '→' + t.edge.to)) { trapsValid = false; console.log(`    ${ph.id}: trap edge is a TRUE relation — not a trap (a trap is the WRONG reading)`); }
  if (!t.why || t.why.length < 20) { trapsValid = false; console.log(`    ${ph.id}: trap lacks a real 'why'`); }
}
ok(trapsValid, `every declared surface_trap is a plausible-but-wrong reading — type, resolvable endpoints, not a true edge (${trapsSeen} traps)`);
ok(trapsSeen >= 1, 'the portfolio carries at least one calibrated trap (benchmark teeth)');

// TEETH: a negative control — a true relation IS recognized as a true edge, so a
// "trap" equal to it would be refused by the not-a-true-edge check above.
const ctrl = P.phrases.find(p => p.surface_trap);
if (ctrl) ok(trueEdges(ctrl).has(ctrl.relations[0].from + '→' + ctrl.relations[0].to),
  'negative control: a true relation reads as a true edge (a trap equal to it would be refused)');

// TEETH: a negative control — a deliberately dangling relation must be caught
const probe = ref({ glyphs: [{ word: 'cat', facets: ['actor'] }] }, 'cat.flying');
ok(!probe.ok, 'negative control: a relation to an undeclared facet is caught (teeth)');

// portfolio covers the systemic vocabulary (variety check)
const kinds = new Set(P.phrases.map(p => p.kind));
ok(kinds.size >= 6, `phrases cover varied system kinds (${kinds.size} distinct)`);

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
