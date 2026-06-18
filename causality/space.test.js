/* space.test.js — §10 teeth for the coordinate volume + grid routing (iterations 0010).
   Run: node causality/space.test.js
   Teeth: a routed path REACHES its goal, NEVER passes through an occupied cell
   (except endpoints), the projection is deterministic, and when the straight line
   is blocked the path DETOURS (longer than Manhattan) — proving it routes around. */
'use strict';
const { Space } = require('./space.js');

let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } };
const manh = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);

console.log('coordinate volume + grid routing — the teeth\n');

let S = Space({ nx: 10, ny: 10, nz: 10 });

// addresses are discrete; occupancy is data
S.place('cat', 1, 5).place('sun', 5, 5).place('shadow', 8, 5);
ok(S.isOcc(5, 5) && !S.isOcc(5, 6), 'occupancy is recorded by address');

// projection is deterministic (same address → same surface point)
S.fit(1200, 800);
const p1 = S.center(5, 5), p2 = S.center(5, 5);
ok(p1.x === p2.x && p1.y === p2.y, 'projection (center) is deterministic');
ok(S.center(6, 5).x > S.center(5, 5).x, 'x increases rightward on the surface');

// a route reaches its goal
const a = { x: 1, y: 5 }, b = { x: 8, y: 5 };
const path = S.route(a, b);
ok(path[path.length - 1].x === b.x && path[path.length - 1].y === b.y, 'a route reaches its goal cell');
ok(path[0].x === a.x && path[0].y === a.y, 'a route starts at its source cell');

// TEETH: the path never passes through an occupied cell (except the endpoints)
const occHit = path.slice(1, -1).some(c => S.isOcc(c.x, c.y));
ok(!occHit, 'the route never crosses an occupied cell (goes around nodes)');

// TEETH: with a node blocking the straight line, the path DETOURS (> Manhattan)
// a=(1,5) -> b=(8,5) straight passes through sun(5,5); must detour
ok(path.length - 1 > manh(a, b), 'a blocked straight line forces a detour (longer than Manhattan)');

// a clear straight line is taken at Manhattan length (no needless wandering)
const S2 = Space({ nx: 10, ny: 10 }); S2.fit(1200, 800);
const clear = S2.route({ x: 0, y: 0 }, { x: 0, y: 6 });
ok(clear.length - 1 === 6, 'a clear line routes at Manhattan length (no wandering)');

// lane reservation: a second edge prefers cells the first did not use
const S3 = Space({ nx: 12, ny: 6 }); S3.fit(1200, 800);
const e1 = S3.route({ x: 0, y: 2 }, { x: 11, y: 2 });
const e2 = S3.route({ x: 0, y: 2 }, { x: 11, y: 2 });   // same endpoints, should divert
const overlap = e2.slice(1, -1).filter(c => e1.some(d => d.x === c.x && d.y === c.y)).length;
ok(overlap < e1.length - 2, 'a second edge diverts off the first edge\'s reserved lane');

console.log('\n' + (fail === 0 ? 'PASSED' : 'FAILED') + ` — ${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
