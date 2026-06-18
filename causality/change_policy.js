/* change_policy.js — the change-management policy node (arc.aim). Turns the pinned
   exemplar's DON'T-REGRESS invariants (aim-exemplars.md) into a checkable gate: a
   candidate surface that LOST a feature the baseline carried is a REGRESSION, refused.
   This is the missing sensor — the shame beat senses stalling, retro senses churn,
   nothing sensed a good surface QUIETLY LOSING what it had. It is the AIM gate shape
   (a change -> judged against the exemplar -> held / amplified / regressed), and it
   was born catching a real one: compare.html forked feature-poor from experience.html.

   Pure judge + a CLI guard (exit 2 on regression, the hooks/*.py convention). Node. */
'use strict';

// the DON'T-REGRESS feature set (aim-exemplars.md) — each present iff ALL its markers
// appear in the surface text. Greppable signatures, not prose: the grip rule. Loaded
// from the shared registry so the JS judge and the Python guard never drift (one table,
// two surfaces — the fence-registry pattern). Inline fallback keeps it browser-safe.
const FALLBACK = [
  { id: 'complexity-slider', markers: ['Complexity'], why: 'the one live growth dial — cute nucleus -> real loop' },
  { id: 'phrase-skin',       markers: ['drawSentence'], why: 'the sentence-as-skin (its loss was a prior regression — never again)' },
  { id: 'hover-unfold',      markers: ['_facetLayout'], why: 'hover-to-unfold the facets' },
  { id: 'gestures',          markers: ['lasso', 'COMMAND'], why: 'gesture-native interaction (lasso/GATHER, hold/COMMAND)' },
  { id: 'honest-magenta',    markers: ['admissions.jsonl', 'composeRel'], why: 'realness read from the log + relations generated (AIM I1/F5)' },
];
let REQUIRED = FALLBACK;
try {
  if (typeof require !== 'undefined') {
    const reg = require('./change-policy.invariants.json');
    if (reg && Array.isArray(reg.required) && reg.required.length) REQUIRED = reg.required;
  }
} catch (e) { /* registry absent — fall back to the inline set */ }

// checkSurface(text) -> which required features are present / missing in this surface.
function checkSurface(text, required) {
  const set = required || REQUIRED;
  const present = [], missing = [];
  for (const f of set) (f.markers.every((m) => String(text).indexOf(m) >= 0) ? present : missing).push(f.id);
  return { present, missing };
}

// judge(baselineText, candidateText) -> the verdict. A feature the BASELINE carries
// that the CANDIDATE lost is a regression; a candidate that holds all of them is held;
// a candidate that adds required features the baseline lacked is amplified.
function judge(baselineText, candidateText, required) {
  const set = required || REQUIRED;
  const base = checkSurface(baselineText, set), cand = checkSurface(candidateText, set);
  const regressed = base.present.filter((id) => cand.missing.indexOf(id) >= 0);
  const gained = cand.present.filter((id) => base.missing.indexOf(id) >= 0);
  const verdict = regressed.length ? 'regressed' : (gained.length ? 'amplified' : 'held');
  return {
    verdict, regressed, gained,
    held: cand.present.filter((id) => base.present.indexOf(id) >= 0),
    detail: regressed.map((id) => { const f = set.find((x) => x.id === id); return id + ' — ' + (f ? f.why : ''); }),
    note: 'A regression refuses the change: a surface may not quietly lose a pinned invariant. Fix the surface (do not fork a poorer one); a deliberate retirement is bdo\'s, on the record.',
  };
}

module.exports = { REQUIRED, checkSurface, judge };

// CLI guard: `node change_policy.js <baseline> <candidate>` — exit 2 (refuse) on regression.
if (require.main === module) {
  const fs = require('fs');
  const [bp, cp] = process.argv.slice(2);
  if (!bp || !cp) { console.error('usage: node change_policy.js <baseline-surface> <candidate-surface>'); process.exit(1); }
  const v = judge(fs.readFileSync(bp, 'utf8'), fs.readFileSync(cp, 'utf8'));
  console.log('change-policy verdict: ' + v.verdict.toUpperCase());
  console.log('  held     :', v.held.join(', ') || '—');
  if (v.gained.length) console.log('  amplified:', v.gained.join(', '));
  if (v.regressed.length) { console.log('  REGRESSED:'); v.detail.forEach((d) => console.log('    ✗ ' + d)); console.error('\nREFUSED — ' + cp + ' lost ' + v.regressed.length + ' invariant(s) ' + bp + ' carried. ' + v.note); process.exit(2); }
  console.log('  ' + v.note);
  process.exit(0);
}
