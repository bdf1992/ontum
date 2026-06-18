/* recovery_scorer.test.js — §10 teeth for the deterministic recovery-scorer
   (done-line 0105, outcome causality-story-benchmark). Run: node causality/recovery_scorer.test.js

   The teeth: on the cat-sunbeam case, the scorer must SEPARATE a mechanism-
   reading (warmth as the mediator, no shadow→cat) from a grammar-reading
   (shadow→cat, mediator missing) — higher composite, reads_mechanism true,
   trap not hit. A CONSTANT/fabricated scorer cannot separate them, and this
   test proves it: the same separation assertion applied to a constant scorer
   fails. If everything scored the same, the check would not be doing its job
   (the doctrine §10 tripwire). */
'use strict';
const fs = require('fs');
const path = require('path');
const S = require('./recovery_scorer.js');
const P = JSON.parse(fs.readFileSync(path.join(__dirname, 'phrases.json'), 'utf8'));

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };

console.log('recovery-scorer — the mechanism-vs-grammar separation (teeth)\n');

const cat = P.phrases.find(p => p.id === 'cat-sunbeam');
ok(!!cat, 'cat-sunbeam is in the portfolio');
ok(cat.surface_trap && cat.surface_trap.edge, 'cat-sunbeam declares a surface_trap edge');

// The MECHANISM reading: a model that recovered the true causal structure —
// warmth mediates (sunbeam→warmth, warmth→objective, shadow→warmth, warmth→wakes),
// and crucially never drew the tempting shadow→cat shortcut.
const mechanism = { glyphs: cat.glyphs, relations: cat.relations };

// The GRAMMAR reading: a fluent-but-shallow read off the sentence — the shadow
// "steals the warmth" so shadow→cat directly (the trap), the sun warms the cat
// directly (mediator elided), and the warmth-mediated wake edge is missed.
const grammar = {
  glyphs: cat.glyphs,
  relations: [
    { from: 'sunbeam.source', to: 'cat.objective', label: 'warms' },
    { from: 'shadow.signal', to: 'cat.actor', label: 'steals warmth (wakes)' },
    { from: 'warmth.state', to: 'cat.objective', label: 'is wanted' },
  ],
};

const sm = S.score(mechanism, cat);
const sg = S.score(grammar, cat);

console.log(`    mechanism: composite=${sm.composite.toFixed(3)} relRecall=${sm.relation.recall.toFixed(2)} trapHit=${sm.trap.hit} reads_mechanism=${sm.reads_mechanism}`);
console.log(`    grammar  : composite=${sg.composite.toFixed(3)} relRecall=${sg.relation.recall.toFixed(2)} trapHit=${sg.trap.hit} reads_mechanism=${sg.reads_mechanism}`);

ok(sm.composite > sg.composite, 'mechanism-reading scores strictly higher than grammar-reading (separation)');
ok(sm.trap.hit === false, 'mechanism-reading did NOT draw the trap edge');
ok(sg.trap.hit === true, 'grammar-reading DID draw the trap edge (shadow→cat)');
ok(sm.reads_mechanism === true, 'mechanism-reading is judged to read the mechanism');
ok(sg.reads_mechanism === false, 'grammar-reading is judged NOT to read the mechanism');

// TEETH — a constant/fabricated scorer cannot separate the two readings. This
// is what makes the separation assertion above meaningful: replace the real
// scorer with a constant and the very same assertion fails.
const constantScore = () => ({ composite: 1, trap: { hit: false }, reads_mechanism: true, relation: { recall: 1 } });
const cm = constantScore(mechanism, cat), cg = constantScore(grammar, cat);
ok(!(cm.composite > cg.composite), 'negative control: a constant scorer does NOT separate (the real separation has teeth)');

// A perfect recovery scores ~1, an empty recovery scores ~0 — sanity bounds.
const empty = S.score({ glyphs: [], relations: [] }, cat);
ok(sm.composite > 0.8, 'a faithful recovery scores high (>0.8)');
ok(empty.composite < 0.2, 'an empty recovery scores low (<0.2)');

// The scorer is defined over every trapped phrase, and a faithful recovery of
// each both scores high and dodges its own trap (no trap is self-defeating).
let everyTrapDodgeable = true;
for (const ph of P.phrases.filter(p => p.surface_trap)) {
  const faithful = S.score({ glyphs: ph.glyphs, relations: ph.relations }, ph);
  if (faithful.trap.hit || !faithful.reads_mechanism) {
    everyTrapDodgeable = false;
    console.log(`    ${ph.id}: faithful recovery hits its own trap or fails reads_mechanism — trap edge is a true edge?`);
  }
}
ok(everyTrapDodgeable, 'every trapped phrase: the faithful recovery dodges the trap and reads the mechanism');

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
