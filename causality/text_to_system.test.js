/* text_to_system.test.js — §10 teeth for the generative-instruction harness.
   The point of the benchmark shape: prove the instructions DESIGN the system from
   raw text and REFUSE hallucination — never parrot the seed. Run: node causality/text_to_system.test.js */
'use strict';
const fs = require('fs');
const path = require('path');
const T = require('./text_to_system.js');

let pass = 0, fail = 0;
function ok(name, cond) { if (cond) { pass++; console.log('  ✓ ' + name); } else { fail++; console.log('  ✗ ' + name); } }

// the held-out seed — loaded ONLY to score against, never fed to generation
const PH = JSON.parse(fs.readFileSync(path.join(__dirname, 'phrases.json'), 'utf8'));
const phrases = PH.phrases || PH;
const cat = phrases.find(p => p.id === 'cat-sunbeam');
const truth = T.truthFromPhrase(cat);

// a text that contains the mechanism's words (a stand-in for the grown phrase)
const TEXT = 'The cat in the sunbeam — its warmth fades when a shadow falls, and the cat wakes.';

// ── anti-poison: the prompt is built from text + vocabulary, and CANNOT carry the seed ──
const prompt = T.buildMeshPrompt('The cat naps.');
ok('prompt carries the raw text', prompt.indexOf('The cat naps.') >= 0);
ok('prompt carries the facet vocabulary', prompt.indexOf('actor') >= 0 && prompt.indexOf('state') >= 0);
ok('prompt carries the legal relation triples', prompt.indexOf('state|objective|+') >= 0);
ok('prompt does NOT leak the phrase id (no seed)', prompt.indexOf('cat-sunbeam') < 0);
ok('prompt does NOT leak the seed bindings (word.facet)', prompt.indexOf('cat.objective') < 0 && prompt.indexOf('sunbeam.source') < 0);
ok('buildMeshPrompt takes ONLY text — no parameter for the seed', T.buildMeshPrompt.length === 1);

// ── a faithful recovery validates and reads the mechanism ──
const good = {
  glyphs: [
    { word: 'cat', facets: ['actor', 'objective'] },
    { word: 'sunbeam', facets: ['source'] },
    { word: 'warmth', facets: ['state'] },
    { word: 'shadow', facets: ['signal'] },
  ],
  relations: [
    { from: 'sunbeam.source', to: 'warmth.state', valence: '+' },
    { from: 'warmth.state', to: 'cat.objective', valence: '+' },
    { from: 'shadow.signal', to: 'warmth.state', valence: '-' },
    { from: 'warmth.state', to: 'cat.actor', valence: 'fades' },
  ],
};
const vg = T.validateMesh(good, TEXT);
ok('a faithful recovery validates', vg.ok === true);
const sg = T.grade(good, truth);
ok('a faithful recovery reads the mechanism (composite high, no trap)', sg.reads_mechanism === true && sg.trap.hit === false && sg.composite > 0.8);

// ── teeth: hallucinated word refused ──
const halluc = { glyphs: [{ word: 'dragon', facets: ['actor'] }], relations: [] };
ok('a hallucinated word (not in text) is refused', T.validateMesh(halluc, TEXT).ok === false);

// ── teeth: unknown facet refused ──
const badFacet = { glyphs: [{ word: 'cat', facets: ['wizard'] }], relations: [] };
ok('an unknown facet is refused', T.validateMesh(badFacet, TEXT).ok === false);

// ── teeth: an undeclared relation triple (invented edge) refused ──
const invented = {
  glyphs: [{ word: 'cat', facets: ['actor'] }, { word: 'sunbeam', facets: ['source'] }],
  relations: [{ from: 'cat.actor', to: 'sunbeam.source', valence: '+' }],  // actor|source|+ is not in RELATION
};
ok('an invented (undeclared) relation triple is refused', T.validateMesh(invented, TEXT).ok === false);

// ── teeth: an edge over a facet the glyph does not carry is refused ──
const uncarried = {
  glyphs: [{ word: 'cat', facets: ['actor'] }, { word: 'warmth', facets: ['state'] }],
  relations: [{ from: 'warmth.state', to: 'cat.objective', valence: '+' }],  // cat does not carry objective here
};
ok('an edge over an uncarried facet is refused', T.validateMesh(uncarried, TEXT).ok === false);

// ── the trap-taker: locally valid, but takes the surface trap and scores WORSE ──
const trapTaker = {
  glyphs: good.glyphs,
  relations: good.relations.concat([{ from: 'shadow.signal', to: 'cat.actor', valence: '+' }]),  // signal|actor|+ = "alerts": the elided-mediator shortcut
};
const vt = T.validateMesh(trapTaker, TEXT);
const st = T.grade(trapTaker, truth);
ok('the trap-taker is locally valid (it passes the teeth)', vt.ok === true);
ok('the trap-taker HITS the surface trap', st.trap.hit === true);
ok('the trap penalty makes the faithful recovery score strictly higher', sg.composite > st.composite);

// ── the scorer is real, not constant (the §10 negative control) ──
ok('two different recoveries get two different verdicts (scorer discriminates)', sg.composite !== st.composite);

console.log((fail === 0 ? '\nPASSED' : '\nFAILED') + ' — ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
