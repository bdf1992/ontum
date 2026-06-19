/* compare.test.js — §10 teeth for the comparator + synthesis (the bake-off fold).
   Proves: consensus across chefs sources a claim (robust), a lone chef's claim is a flavor
   (divergent), the SEED IS NOT PRIVILEGED, and synthesis takes the robust core + only the
   flavors explicitly adopted. Run: node causality/compare.test.js */
'use strict';
const C = require('./compare.js');

let pass = 0, fail = 0;
function ok(name, cond) { if (cond) { pass++; console.log('  ✓ ' + name); } else { fail++; console.log('  ✗ ' + name); } }
const has = (arr, el) => arr.some((x) => x.el === el);
const findEl = (arr, el) => arr.find((x) => x.el === el);

// two chefs: a robust core they agree on + a distinctive flavor each
const chefA = { glyphs: [{ word: 'cat', facets: ['actor', 'objective'] }, { word: 'warmth', facets: ['state'] }],
  relations: [{ from: 'warmth.state', to: 'cat.objective' }, { from: 'cat.actor', to: 'warmth.state' }] };
const chefB = { glyphs: [{ word: 'cat', facets: ['actor', 'objective'] }, { word: 'warmth', facets: ['state', 'signal'] }],
  relations: [{ from: 'warmth.state', to: 'cat.objective' }, { from: 'warmth.signal', to: 'cat.objective' }] };

const cmp = C.compareReadings([{ label: 'A', mesh: chefA }, { label: 'B', mesh: chefB }]);

// ── consensus sources a claim (robust) ──
ok('a facet both chefs assign is robust', has(cmp.facets.robust, 'cat.actor') && has(cmp.facets.robust, 'warmth.state'));
ok('an edge both chefs draw is robust', has(cmp.edges.robust, 'warmth.state→cat.objective'));

// ── a lone chef's claim is a flavor (divergent), not robust ──
ok('a facet only one chef assigns is divergent', has(cmp.facets.divergent, 'warmth.signal') && !has(cmp.facets.robust, 'warmth.signal'));
ok('an edge only one chef draws is divergent', has(cmp.edges.divergent, 'cat.actor→warmth.state') && has(cmp.edges.divergent, 'warmth.signal→cat.objective'));
ok('a divergent claim names which chef made it', (findEl(cmp.edges.divergent, 'cat.actor→warmth.state') || {}).readers.join() === 'A');

// ── the SEED IS NOT PRIVILEGED — its solo claim is a flavor, never crowned ──
const withSeed = C.compareReadings([{ label: 'seed', mesh: chefA }, { label: 'claude', mesh: chefB }]);
ok('a claim ONLY the seed makes is divergent (seed not crowned)', has(withSeed.edges.divergent, 'cat.actor→warmth.state') && (findEl(withSeed.edges.divergent, 'cat.actor→warmth.state') || {}).readers.join() === 'seed');

// ── consensus needs >= 2 — a single chef alone sources nothing as robust ──
const lone = C.compareReadings([{ label: 'only', mesh: chefA }]);
ok('one chef alone makes nothing robust (consensus needs >= 2)', lone.facets.robust.length === 0 && lone.edges.robust.length === 0);

// ── identical chefs — everything robust, no flavors ──
const same = C.compareReadings([{ label: 'X', mesh: chefA }, { label: 'X2', mesh: chefA }]);
ok('identical chefs: all robust, zero divergent', same.facets.divergent.length === 0 && same.edges.divergent.length === 0 && same.facets.robust.length > 0);

// ── synthesize: default = the robust core only (no flavors adopted) ──
const core = C.synthesize(cmp);
const coreEdges = core.relations.map((r) => r.from + '→' + r.to);
ok('synthesis default = robust core only (a flavor is excluded)', coreEdges.indexOf('warmth.state→cat.objective') >= 0 && coreEdges.indexOf('cat.actor→warmth.state') < 0);
ok('synthesis winner reconstructs valid glyphs + relations', core.glyphs.every((g) => g.word && Array.isArray(g.facets)) && core.relations.every((r) => r.from && r.to));

// ── synthesize: adopt a chosen flavor → it joins the winner ──
const withFlavor = C.synthesize(cmp, { adopt: ['cat.actor→warmth.state'] });
const wf = withFlavor.relations.map((r) => r.from + '→' + r.to);
ok('best-of-all-flavors: an ADOPTED flavor joins the winner', wf.indexOf('cat.actor→warmth.state') >= 0 && wf.indexOf('warmth.state→cat.objective') >= 0);
ok('an UN-adopted flavor stays out of the winner', wf.indexOf('warmth.signal→cat.objective') < 0);
ok('provenance records robust vs adopted counts', withFlavor.provenance.adoptedFlavors === 1 && withFlavor.provenance.robustElements > 0);

// ── trap: the comparator names which chefs took a watched edge, crowns nothing ──
const trapCmp = C.compareReadings([{ label: 'A', mesh: chefA }, { label: 'B', mesh: chefB }], { trapEdge: 'cat.actor→warmth.state' });
ok('trap edge: the comparator names who took it', trapCmp.trap && trapCmp.trap.takenBy.join() === 'A');

console.log((fail === 0 ? '\nPASSED' : '\nFAILED') + ' — ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
