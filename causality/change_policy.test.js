/* change_policy.test.js — §10 teeth for the change-management policy node.
   The dogfood: the node must CATCH the real regression (compare.html forked feature-poor
   from experience.html) and must NOT fire on a surface that holds its invariants. Run:
   node causality/change_policy.test.js */
'use strict';
const fs = require('fs');
const path = require('path');
const P = require('./change_policy.js');

let pass = 0, fail = 0;
const ok = (name, cond) => { if (cond) { pass++; console.log('  ✓ ' + name); } else { fail++; console.log('  ✗ ' + name); } };
const read = (f) => fs.readFileSync(path.join(__dirname, f), 'utf8');

const experience = read('experience.html');     // the baseline — carries every invariant
const compare = read('compare.html');           // the fork — dropped them all

// ── the baseline carries the full feature set ──
const baseCheck = P.checkSurface(experience);
ok('the experience surface holds every required invariant', baseCheck.missing.length === 0 && baseCheck.present.length === P.REQUIRED.length);

// ── the dogfood: the node CATCHES the real regression ──
const v = P.judge(experience, compare);
ok('compare.html is judged a REGRESSION', v.verdict === 'regressed');
ok('it names the lost invariants (slider, skin, hover, gestures, honest-magenta)', v.regressed.length === P.REQUIRED.length);
ok('the regression detail explains WHY each matters', v.detail.every((d) => d.indexOf('—') >= 0));

// ── a surface that holds its invariants is HELD (no false alarm) ──
const held = P.judge(experience, experience);
ok('an unchanged surface is held, not refused', held.verdict === 'held' && held.regressed.length === 0);

// ── the node actually READS the surface (negative control — not a constant) ──
const empty = P.judge(experience, '<html>nothing</html>');
ok('an empty surface regresses everything (the check is real, not constant)', empty.verdict === 'regressed' && empty.regressed.length === P.REQUIRED.length);
ok('a verdict distinguishes held from regressed (discriminates)', held.verdict !== empty.verdict);

// ── amplified: a candidate that adds a required feature the baseline lacked ──
const REQ2 = [{ id: 'x', markers: ['FEATURE_X'], why: 'x' }];
const amp = P.judge('<html>plain</html>', '<html>FEATURE_X here</html>', REQ2);
ok('a surface that GAINS a feature is amplified', amp.verdict === 'amplified' && amp.gained.indexOf('x') >= 0);

console.log((fail === 0 ? '\nPASSED' : '\nFAILED') + ' — ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
