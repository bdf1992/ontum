'use strict';
// engine-fixes.test.js — the three peer-review bugs (GRADES.md), each with a
// test that FAILS on the pre-fix code and passes on the fix (the §10 grain):
//   1. multibyte UTF-8 split across stdout chunks must not corrupt the reply.
//   2. an async stdin 'error' (EPIPE) must reject the turn, never crash the host.
//   3. a child that never closes must time out (kill + honest timedOut reply),
//      not hang the turn forever.
// Plus the assembleStream guard: a 'stop' for an unstarted index makes no block.
// Pure: every "engine" here is a fake (no real `claude`, no billed call).

const assert = require('assert');
const { EventEmitter } = require('events');
const engine = require('../engine.js');

let passed = 0;
function check(name, fn) {
  try { fn(); console.log('  ok  ' + name); passed++; }
  catch (e) { console.error('  FAIL ' + name + '\n      ' + e.message); process.exitCode = 1; }
}
async function checkAsync(name, fn) {
  try { await fn(); console.log('  ok  ' + name); passed++; }
  catch (e) { console.error('  FAIL ' + name + '\n      ' + e.message); process.exitCode = 1; }
}

// --- Fix 1: multibyte UTF-8 split across chunk boundaries -------------------
// A result event whose text holds non-ASCII ('café ☕'), emitted as two Buffers
// split INSIDE the 'é' (0xC3 | 0xA9). Pre-fix, each chunk.toString('utf8')
// decoded its half-char to U+FFFD and the reply read 'caf��…'.
function splitMultibyteSpawn() {
  const child = new EventEmitter();
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.stdin = { write() {}, end() {} };
  child.kill = () => {};
  const line = JSON.stringify({
    type: 'result', subtype: 'success', is_error: false, result: 'café ☕',
  }) + '\n';
  const buf = Buffer.from(line, 'utf8');
  const cut = buf.indexOf(0xC3) + 1; // between the two bytes of 'é'
  setImmediate(() => {
    child.stdout.emit('data', buf.slice(0, cut)); // …"caf" + 0xC3
    child.stdout.emit('data', buf.slice(cut));    // 0xA9 + ' ☕"}' + \n
    child.emit('close', 0);
  });
  return { spawn: () => child };
}

checkAsync('1. multibyte UTF-8 split across stdout chunks is not corrupted', async () => {
  const reply = await engine.driveTurn({ prompt: 'x', spawn: splitMultibyteSpawn().spawn });
  const text = reply.text || reply.result || '';
  assert.ok(text.indexOf('café ☕') >= 0,
    'expected the reply to carry "café ☕" intact, got: ' + JSON.stringify(text));
  assert.ok(text.indexOf('�') < 0, 'reply must hold no U+FFFD replacement char');
});

// --- Fix 2: async stdin 'error' (EPIPE) rejects, never crashes --------------
// The engine exits before the prompt is written; stdin emits 'error'
// asynchronously (the try/catch around write() never sees it). Pre-fix: with no
// 'error' listener Node escalates to an uncaught exception (host crash). Post-fix
// the turn rejects. timeoutMs:0 isolates the stdin path from the watchdog.
function epipeSpawn() {
  const child = new EventEmitter();
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.stdin = new EventEmitter();
  child.stdin.write = () => {
    setImmediate(() => child.stdin.emit('error',
      Object.assign(new Error('write EPIPE'), { code: 'EPIPE' })));
    return false;
  };
  child.stdin.end = () => {};
  child.kill = () => {};
  // never emits 'close' — the rejection must come from the stdin error
  return { spawn: () => child };
}

checkAsync('2. an async stdin EPIPE rejects the turn (no unhandled crash)', async () => {
  await assert.rejects(
    engine.driveTurn({ prompt: 'x', spawn: epipeSpawn().spawn, timeoutMs: 0 }),
    (err) => err && err.code === 'EPIPE',
    'driveTurn should reject with the EPIPE error');
});

// --- Fix 3: a child that never closes times out (kill + honest reply) -------
function hangSpawn() {
  const state = { killed: false };
  const child = new EventEmitter();
  child.stdout = new EventEmitter();
  child.stderr = new EventEmitter();
  child.stdin = { write() {}, end() {} };
  child.kill = () => { state.killed = true; };
  setImmediate(() => child.stdout.emit('data',
    Buffer.from(JSON.stringify({ type: 'system', subtype: 'init', session_id: 's', tools: [] }) + '\n', 'utf8')));
  // never emits 'close'
  return { spawn: () => child, state };
}

checkAsync('3. a never-closing turn times out: timedOut + isError + child killed', async () => {
  const h = hangSpawn();
  const t0 = Date.now();
  const reply = await engine.driveTurn({ prompt: 'x', spawn: h.spawn, timeoutMs: 60 });
  const dt = Date.now() - t0;
  assert.strictEqual(reply.timedOut, true, 'reply.timedOut must be true');
  assert.strictEqual(reply.isError, true, 'a timeout is an error');
  assert.ok(/timed out/i.test(reply.error || ''), 'reply.error names the timeout');
  assert.strictEqual(h.state.killed, true, 'the wedged child must be killed');
  assert.ok(dt < 2000, 'must settle promptly after the ' + 60 + 'ms budget, not hang (took ' + dt + 'ms)');
});

checkAsync('3b. timeoutMs:0 disables the watchdog (a normal turn still closes)', async () => {
  const reply = await engine.driveTurn({ prompt: 'x', spawn: splitMultibyteSpawn().spawn, timeoutMs: 0 });
  assert.ok(!reply.timedOut, 'a turn that closes normally is not timedOut');
});

// --- Bonus: assembleStream makes no spurious block for an orphan 'stop' ------
check('4. assembleStream ignores a stop for an index that never started', () => {
  // a bare content_block_stop for index 0 with no preceding start/delta
  const events = [{ type: 'content_block_stop', index: 0 }];
  const blocks = engine.assembleStream(events);
  assert.deepStrictEqual(blocks, [], 'no block should be materialized from a lone stop');
});

setTimeout(() => {
  console.log('\n' + passed + ' checks passed — engine fixes (UTF-8, EPIPE, timeout, stream-stop).');
}, 200);
