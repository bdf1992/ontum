'use strict';
/* tier.test.js — the §10 check for done-line 0190: the pure tier classifier is
 * real and discriminating. Plain `node`, no framework, no `vscode` (mirrors
 * causality/canvas.persist.test.js). Run: node vscode/forest-mask/tier.test.js
 * (exit 0 = passed). The teeth: a CONSTANT classifier (always "read") must fail
 * at least one assertion — proven explicitly at the end. */

const { classify } = require('./tier.js');

let fails = 0;
const ok = (cond, msg) => {
  if (!cond) { console.error('  ✗ ' + msg); fails++; }
  else console.log('  ✓ ' + msg);
};

const NOW = Date.parse('2026-06-23T12:00:00Z');
const HOUR = 60 * 60 * 1000;
const RECENCY = 30 * 60 * 1000; // 30-minute in-context window

const iso = (msAgo) => new Date(NOW - msAgo).toISOString();

// a realistic log: several paths, several sessions, read + edit, old + fresh
const log = [
  { ts: iso(2 * HOUR), session: 's1', action: 'read', path: 'loop/reconcile.py' },
  { ts: iso(2 * HOUR), session: 's1', action: 'edit', path: 'loop/orchestrate.py' },
  { ts: iso(5 * 60 * 1000), session: 's2', action: 'read', path: 'loop/summon.py' },
  { ts: iso(5 * 60 * 1000), session: 's2', action: 'edit', path: 'loop/node.py' },
  // a path read long ago AND edited fresh — recency overlay should win
  { ts: iso(3 * HOUR), session: 's1', action: 'read', path: 'loop/web.py' },
  { ts: iso(60 * 1000), session: 's3', action: 'edit', path: 'loop/web.py' },
];

// --- the four core tiers ---------------------------------------------------
ok(classify(log, 'README.md', NOW, RECENCY) === 'undiscovered',
   'a never-seen path -> undiscovered');
ok(classify(log, 'loop/reconcile.py', NOW, RECENCY) === 'read',
   'an old read-only path -> read (not in-context: 2h > 30m window)');
ok(classify(log, 'loop/orchestrate.py', NOW, RECENCY) === 'written',
   'an old edited path -> written (edit outranks read; 2h ago, not in-context)');
ok(classify(log, 'loop/summon.py', NOW, RECENCY) === 'in-context',
   'a just-now read (5m) -> in-context (overlay)');
ok(classify(log, 'loop/node.py', NOW, RECENCY) === 'in-context',
   'a just-now edit (5m) -> in-context (overlay wins over written)');

// --- precedence & proxy edges ----------------------------------------------
ok(classify(log, 'loop/web.py', NOW, RECENCY) === 'in-context',
   'read long ago + edited fresh -> in-context (recency from the latest touch)');
ok(classify(log, 'loop/orchestrate.py', NOW, 0) === 'written',
   'recency window 0 disables the overlay -> falls back to written');
ok(classify(log, 'loop/summon.py', NOW, 0) === 'read',
   'recency window 0 -> a recent read reads as plain read');
ok(classify([], 'loop/node.py', NOW, RECENCY) === 'undiscovered',
   'an empty log -> every path undiscovered (fail-soft default)');
ok(classify(log, 'loop/orchestrate.py', NOW, 10 * HOUR) === 'in-context',
   'a wide window pulls the old edit into in-context (the dial works)');
// a future ts (clock skew) must not be counted as recent
ok(classify([{ ts: iso(-HOUR), action: 'read', path: 'x' }], 'x', NOW, RECENCY) === 'read',
   'a future-dated touch is not in-context (only the window behind now counts)');
// a malformed ts must not throw and must not be recent
ok(classify([{ ts: 'not-a-date', action: 'edit', path: 'y' }], 'y', NOW, RECENCY) === 'written',
   'a malformed ts -> still classified (written), never thrown, never recent');

// --- TEETH: a constant classifier must be caught ---------------------------
// If `classify` always returned "read", these real cases would disagree.
const constantRead = () => 'read';
let constantWrong = 0;
const cases = [
  ['README.md', 'undiscovered'],
  ['loop/orchestrate.py', 'written'],
  ['loop/node.py', 'in-context'],
];
for (const [p, expected] of cases) {
  if (constantRead(log, p, NOW, RECENCY) !== expected) constantWrong++;
}
ok(constantWrong >= 3,
   `negative control: a constant "read" classifier is caught (${constantWrong} of 3 cases wrong) — the test has teeth`);

if (fails) {
  console.error(`\nFAILED: ${fails} assertion(s)`);
  process.exit(1);
}
console.log('\nPASSED: tier classifier is non-vacuous and discriminating');
process.exit(0);
