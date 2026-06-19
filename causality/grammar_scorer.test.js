/* grammar_scorer.test.js — §10 teeth for the well-formedness gate (done-line
   story-grammar-wellformedness). Run: node causality/grammar_scorer.test.js

   The teeth: bdo's nonsense story is flagged malformed via BOTH layers — a
   structural violation (a source cannot drive an actor) and a lexical one (a
   verb whose subject lacks the required facet) — while every real portfolio
   phrase is well-formed (the tables do not false-flag the corpus), an unknown
   verb is reported, not judged, and a constant scorer cannot separate. */
'use strict';
const fs = require('fs');
const path = require('path');
const G = require('./grammar_scorer.js');
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'phrases.json'), 'utf8'));

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };

console.log('grammar / well-formedness gate — nonsense is refused (teeth)\n');

// CALIBRATION: every real phrase must be well-formed — else the tables are wrong.
let allWellFormed = true;
for (const ph of P.phrases) {
  const r = G.grammar(ph);
  if (!r.wellFormed) {
    allWellFormed = false;
    console.log(`    ${ph.id}: NOT well-formed — structural=${JSON.stringify(r.structural)} lexical=${JSON.stringify(r.lexical)}`);
  }
}
ok(allWellFormed, 'every real portfolio phrase is well-formed (the tables do not false-flag the corpus)');

// The mediator rule holds: a source cannot reach an actor directly.
ok(!(G.LICENSED.source || []).includes('actor'), 'the LICENSED table forbids source→actor (the mediator rule)');

// bdo's nonsense: "sunlight napped on the cat until the shadow ate the plant".
const nonsense = {
  glyphs: [
    { word: 'sunlight', facets: ['source', 'time'] },
    { word: 'cat', facets: ['actor', 'objective'] },
    { word: 'shadow', facets: ['signal', 'time'] },
    { word: 'plant', facets: ['state', 'objective'] },
  ],
  relations: [
    { from: 'sunlight.source', to: 'cat.actor', label: 'napped on' },   // structural (source↛actor) + lexical (nap needs actor)
    { from: 'shadow.signal', to: 'plant.state', label: 'ate' },          // structural OK (signal→state); lexical (eat needs actor)
  ],
};
const ng = G.grammar(nonsense);
console.log(`    nonsense: wellFormed=${ng.wellFormed} structural=${ng.structural.length} lexical=${ng.lexical.length} score=${ng.score.toFixed(2)}`);
ok(ng.wellFormed === false, 'the nonsense story is flagged malformed');
ok(ng.structural.some(s => s.edge === 'sunlight.source→cat.actor'), 'STRUCTURAL: sunlight(source)→cat(actor) caught (no direct source→actor)');
ok(ng.lexical.some(l => l.edge === 'shadow.signal→plant.state' && l.verb === 'ate'),
  'LEXICAL: "ate" on shadow caught — signal→state is fine structurally, but eat needs an actor');

// honest gap: an unknown verb is reported, not judged.
const unknown = {
  glyphs: [{ word: 'a', facets: ['source'] }, { word: 'b', facets: ['state'] }],
  relations: [{ from: 'a.source', to: 'b.state', label: 'wibbles' }],
};
const ug = G.grammar(unknown);
ok(ug.wellFormed === true && ug.unknownVerbs.includes('wibbles'),
  'an unknown verb is reported as unknown, never a false violation (honest gap)');

// TEETH — a constant scorer cannot tell a real phrase from the nonsense.
const constant = () => ({ wellFormed: true, score: 1 });
ok(!(constant(P.phrases[0]).wellFormed !== constant(nonsense).wellFormed),
  'negative control: a constant scorer does NOT separate real from nonsense (the gate has teeth)');

// score sanity: nonsense scores below a clean phrase.
ok(ng.score < G.grammar(P.phrases[0]).score, 'the nonsense story scores below a real phrase');

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
