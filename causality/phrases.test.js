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

// TEETH: a negative control — a deliberately dangling relation must be caught
const probe = ref({ glyphs: [{ word: 'cat', facets: ['actor'] }] }, 'cat.flying');
ok(!probe.ok, 'negative control: a relation to an undeclared facet is caught (teeth)');

// portfolio covers the systemic vocabulary (variety check)
const kinds = new Set(P.phrases.map(p => p.kind));
ok(kinds.size >= 6, `phrases cover varied system kinds (${kinds.size} distinct)`);

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
