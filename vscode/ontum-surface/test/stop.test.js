// stop.test.js — proof for parity-checklist row 17.
//
// "Stop / interrupt a running turn."
//
// Normal Claude Code lets the human STOP an in-flight turn (Esc / the Stop
// button). The bridge spike marked this `inherit` ("stream-json control /
// process signal"); grounded live this tick: `claude --help` advertises NO
// interrupt / abort / control flag for the `--print` headless channel (no
// `--interrupt`/`--abort`/control-request option exists in 2.0.19). So the only
// HONEST way to stop an in-flight headless turn is to TERMINATE the spawned
// engine process — the same `child.kill()` the watchdog uses, here
// user-initiated. The turn then settles via its `close` with whatever events
// arrived, folded by foldReply and LABELLED interrupted (markInterrupted) so the
// surface reports an honest, PARTIAL stop — never a fabricated completion.
//
// This test proves that round-trip host-free, no billed model call:
//   - engine.markInterrupted re-labels a reply as an interrupt, PRESERVING the
//     folded fields (sessionId + the entries/text that streamed before the stop)
//     so a stopped turn shows its honest partial result, not an empty one;
//   - engine.driveTurn hands opts.onStart a control handle { interrupt(), child }
//     synchronously; calling interrupt() kills the engine process and the turn
//     settles as an interrupted reply (subtype 'interrupted'); a second
//     interrupt after the turn settled is a no-op (returns false — idempotent);
//   - engine.engineArgs carries NO interrupt/control flag (the headless channel
//     has none — the honest mechanism is the process signal, not an argv lever);
//   - extension.interruptTurn/isTurnRunning track the in-flight turn: a turn
//     holds the handle (isTurnRunning true), interruptTurn stops it, and after it
//     settles the handle is dropped (a late Stop is a harmless no-op);
//   - the webview round-trip: a real `ontum:interrupt-turn` message (the Stop
//     button) terminates the in-flight turn through onDidReceiveMessage;
//   - shell.renderShell paints the Stop button (hidden by default), posts
//     ontum:interrupt-turn, toggles it with the turn lifecycle, and reports an
//     interrupted reply as a calm "Turn stopped." (not a red "Turn failed.").
// HONEST SCOPE: this proves the stop surface terminates a real driven turn and
// labels the partial result honestly, host-free. Stopping a real billed turn
// mid-flight is a human's to do at the surface.
//
// Run: node vscode/ontum-surface/test/stop.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const path = require('path');
const Module = require('module');
const { EventEmitter } = require('events');

let passed = 0;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

const engine = require(path.join(__dirname, '..', 'engine.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 17 — stop / interrupt a running turn');

// ---- 1. the interrupt subtype + the pure labeller --------------------------
check('INTERRUPT_SUBTYPE is the honest "interrupted" tag', () => {
  assert.strictEqual(engine.INTERRUPT_SUBTYPE, 'interrupted');
});
check('markInterrupted labels a reply + PRESERVES the partial fold', () => {
  const partial = {
    sessionId: 'sess-stop',
    entries: [{ kind: 'assistant-text', text: 'Half a thought' }],
    text: 'Half a thought',
    isError: true,
    subtype: 'no-result',
    cost: null,
    exitCode: 143,
  };
  const marked = engine.markInterrupted(partial);
  assert.strictEqual(marked.interrupted, true, 'flagged interrupted');
  assert.strictEqual(marked.isError, true, 'a stop is an error-ish outcome');
  assert.strictEqual(marked.subtype, 'interrupted', 're-tagged from no-result');
  assert.ok(/interrupt/i.test(marked.error), 'an honest error message');
  // the partial result the human saw stream is preserved, not blanked:
  assert.strictEqual(marked.sessionId, 'sess-stop', 'sessionId preserved');
  assert.deepStrictEqual(marked.entries, partial.entries, 'partial entries kept');
  assert.strictEqual(marked.text, 'Half a thought', 'partial text kept');
  assert.strictEqual(marked.exitCode, 143, 'exit code preserved');
});
check('markInterrupted keeps a caller-supplied error + is pure', () => {
  const src = { error: 'engine vanished', entries: [] };
  const marked = engine.markInterrupted(src);
  assert.strictEqual(marked.error, 'engine vanished', 'a prior error is kept');
  assert.notStrictEqual(marked, src, 'returns a new object (does not mutate)');
  assert.strictEqual(src.interrupted, undefined, 'the source is untouched');
});
check('markInterrupted tolerates a non-object reply', () => {
  const marked = engine.markInterrupted(null);
  assert.strictEqual(marked.subtype, 'interrupted');
  assert.strictEqual(marked.isError, true);
});

// ---- 2. engineArgs carries NO interrupt flag (the honest mechanism) --------
check('engineArgs has no interrupt/abort/control flag (headless has none)', () => {
  const args = engine.engineArgs({});
  ['--interrupt', '--abort', '--cancel', '--stop', '--control'].forEach((f) =>
    assert.ok(args.indexOf(f) < 0, f + ' is not a real headless flag')
  );
});

// ---- 3. driveTurn hands a control handle; interrupt stops the turn ----------
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
// The partial events that streamed BEFORE the human pressed Stop. There is no
// `result` event — the turn was killed mid-flight, so the fold is honestly
// partial (subtype 'no-result' -> re-tagged 'interrupted' by markInterrupted).
const PARTIAL = [
  line({ type: 'system', subtype: 'init', session_id: 'sess-stop', tools: ['Read'] }),
  line({
    type: 'assistant',
    session_id: 'sess-stop',
    message: { role: 'assistant', content: [{ type: 'text', text: 'Half a thought' }] },
  }),
];

function tick() {
  return new Promise((r) => setImmediate(() => setImmediate(r)));
}

// makeStallingEngine(lines) -> a fake spawn that emits the partial events then
// STALLS (never closes on its own), so the turn is genuinely "still running"
// until interrupt() calls child.kill() — which then emits 'close' (a terminated
// process), exactly as a real SIGTERM would. No model call.
function makeStallingEngine(lines) {
  const calls = [];
  let lastChild = null;
  function spawn(bin, args) {
    calls.push({ bin, args });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.killed = false;
    child.stdin = { write() { return true; }, end() {} };
    child.kill = function () {
      if (child.killed) return true;
      child.killed = true;
      // a real kill closes the process — settle the turn on the next tick.
      setImmediate(function () { child.emit('close', 143); });
      return true;
    };
    setImmediate(function () {
      // the bytes that arrived before the stop; then the turn stalls (no close).
      child.stdout.emit('data', Buffer.from(lines.join(''), 'utf8'));
    });
    lastChild = child;
    return child;
  }
  return { spawn, calls, getChild: () => lastChild };
}

(async function driveInterrupt() {
  const fake = makeStallingEngine(PARTIAL);
  let handle = null;
  const p = engine.driveTurn({
    prompt: 'a long task',
    spawn: fake.spawn,
    timeoutMs: 0, // no watchdog — prove the STOP settles it, not a timeout
    onStart: (h) => { handle = h; },
  });

  check('driveTurn hands onStart a control handle synchronously', () => {
    assert.ok(handle && typeof handle === 'object', 'a handle arrived');
    assert.strictEqual(typeof handle.interrupt, 'function', 'with interrupt()');
    assert.ok(handle.child, 'and the child process');
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
  });

  await tick(); // let the partial events stream in (the turn is now in flight)

  check('interrupt() stops a live turn (returns true) + kills the process', () => {
    const stopped = handle.interrupt();
    assert.strictEqual(stopped, true, 'a live turn was stopped');
    assert.strictEqual(fake.getChild().killed, true, 'the engine process was killed');
  });

  const reply = await p;

  check('the stopped turn settles as an honest interrupted partial', () => {
    assert.strictEqual(reply.interrupted, true, 'flagged interrupted');
    assert.strictEqual(reply.subtype, 'interrupted', 'not faked as success');
    assert.strictEqual(reply.isError, true, 'a stop is not a clean completion');
    assert.strictEqual(reply.sessionId, 'sess-stop', 'the partial fold is kept');
    assert.ok(
      reply.entries.length >= 1 && reply.text.indexOf('Half a thought') >= 0,
      'the prose that streamed before the stop survives the fold'
    );
  });

  check('a second interrupt after the turn settled is a no-op (idempotent)', () => {
    assert.strictEqual(handle.interrupt(), false, 'nothing left to stop');
  });

  // ---- 4. the extension host round-trip ------------------------------------
  const loaded = loadExtension();
  const ext = loaded.ext;
  const registered = loaded.registered;
  const getHandler = loaded.getHandler;
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  const onMessage = getHandler();

  check('isTurnRunning is false with no turn in flight', () => {
    assert.strictEqual(ext.isTurnRunning(), false, 'idle to start');
    assert.strictEqual(ext.interruptTurn(), false, 'a stop with no turn is a no-op');
  });

  // Drive a turn that stalls; interruptTurn() (the host) stops it.
  let efake = makeStallingEngine(PARTIAL);
  ext.__setSpawnForTest(efake.spawn);
  let pending = ext.sendPrompt('drive a long one');
  await tick();
  check('a turn in flight holds the control handle (isTurnRunning true)', () => {
    assert.strictEqual(ext.isTurnRunning(), true, 'the handle is held');
  });
  check('interruptTurn() stops the in-flight turn (returns true)', () => {
    assert.strictEqual(ext.interruptTurn(), true, 'the live turn was stopped');
  });
  let extReply = await pending;
  await tick();
  check('the host-stopped turn folds an interrupted reply + drops the handle', () => {
    assert.strictEqual(extReply.subtype, 'interrupted', 'honest interrupted reply');
    assert.strictEqual(ext.isTurnRunning(), false, 'the handle is cleared after settle');
    assert.strictEqual(ext.interruptTurn(), false, 'a late Stop is a harmless no-op');
  });

  // The webview round-trip: a real ontum:interrupt-turn message stops the turn.
  efake = makeStallingEngine(PARTIAL);
  ext.__setSpawnForTest(efake.spawn);
  pending = ext.sendPrompt('drive another long one');
  await tick();
  check('a webview ontum:interrupt-turn message stops the turn', () => {
    assert.strictEqual(ext.isTurnRunning(), true, 'a turn is in flight');
    onMessage({ type: 'ontum:interrupt-turn' });
    assert.strictEqual(efake.getChild().killed, true, 'the message killed the engine');
  });
  extReply = await pending;
  await tick();
  check('the message-stopped turn settles interrupted (not failed)', () => {
    assert.strictEqual(extReply.subtype, 'interrupted', 'honest interrupted reply');
    assert.strictEqual(ext.isTurnRunning(), false, 'handle dropped after settle');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  // ---- 5. shell paints + wires the Stop button -----------------------------
  check('renderShell paints the Stop button, hidden by default', () => {
    const html = shell.renderShell({});
    assert.ok(/ontum-compose-stop/.test(html), 'the Stop button is present');
    assert.ok(
      /class="ontum-compose-stop"[^>]*hidden/.test(html),
      'it is hidden until a turn drives'
    );
    assert.ok(/>Stop</.test(html), 'it is labelled Stop');
  });
  check('the composer posts ontum:interrupt-turn on a Stop click', () => {
    const html = shell.renderShell({});
    assert.ok(/ontum:interrupt-turn/.test(html), 'the Stop click posts the interrupt');
  });
  check('the Stop button is toggled with the turn lifecycle', () => {
    const html = shell.renderShell({});
    assert.ok(/function setTurnRunning/.test(html), 'a shared lifecycle toggle');
    // shown on submit, re-hidden on the terminal turn-reply:
    assert.ok(/setTurnRunning\(true\)/.test(html), 'shown when a turn starts');
    assert.ok(/setTurnRunning\(false\)/.test(html), 'hidden when the turn settles');
  });
  check('an interrupted reply renders a calm "Turn stopped.", not "failed"', () => {
    const html = shell.renderShell({});
    assert.ok(
      /subtype === 'interrupted'/.test(html),
      'the turn-reply path branches on the interrupted subtype'
    );
    assert.ok(/Turn stopped\./.test(html), 'and reports it honestly, calmly');
  });

  console.log('\n' + passed + ' checks passed — row 17 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// ---- helpers ---------------------------------------------------------------

// loadExtension() -> require extension.js under a fake `vscode`, returning the
// module plus the captured webview message handler. Mirrors resume.test.js.
function loadExtension() {
  const posted = [];
  let messageHandler = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: '/fake/ontum-overnight' } }] },
    window: {
      createWebviewPanel() {
        return {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) { messageHandler = cb; },
            postMessage(m) { posted.push(m); return true; },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
    },
    commands: {
      registerCommand(id, cb) { registered[id] = cb; return { dispose() {} }; },
    },
  };
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === 'vscode') return fakeVscode;
    return origLoad.call(this, request, parent, isMain);
  };
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;
  return { ext, posted, registered, getHandler: () => messageHandler };
}
