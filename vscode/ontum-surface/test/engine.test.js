// engine.test.js — proof for parity-checklist row 5.
//
// "Drive a new turn through the engine (send a prompt, get a reply)."
//
// The bridge is INHERITED (SPIKE-FINDINGS.md): the same `claude` CLI exposes a
// stream-json drive channel (`--print --input-format stream-json
// --output-format stream-json --include-partial-messages`). This test proves the
// driver speaks that channel end-to-end WITHOUT a real billed model call: it
// feeds a FAKE engine process canned stream-json (the exact event shapes the
// spike observed) and asserts:
//   - encodeUserMessage emits the newline-terminated user envelope the channel
//     reads on stdin;
//   - engineArgs opens the channel with the flags `claude --help` advertises
//     (verified live on this machine — see the row-5 evidence);
//   - foldReply folds the output event stream into ONE turn's reply (session id,
//     assistant text, cost/usage, error state) — reusing the same foldTranscript
//     a read transcript uses, so a driven turn renders identically to a read one;
//   - driveTurn runs the round-trip: the prompt is written to the engine's
//     stdin, and the folded reply comes back (buffered across torn stdout
//     chunks, tolerant of a torn tail);
//   - the extension wiring drives a turn from the surface: __setSpawnForTest
//     injects the fake engine, sendPrompt resolves the reply, and an
//     `ontum:turn-reply` message carrying the rendered reply + cost is posted to
//     the webview; the `ontum:send-prompt` message handler triggers the same;
//   - the shell renders a composer that posts `ontum:send-prompt` and handles
//     `ontum:turn-reply`.
// Honest scope: this proves the DRIVE + REPLY plumbing (row 5). A real billed
// turn is left to a human at the surface; incremental partial streaming is row 6.
//
// Run: node vscode/ontum-surface/test/engine.test.js
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

console.log('row 5 — drive a new turn through the engine (send a prompt, get a reply)');

// ---- the captured stream-json event stream (the shapes the spike observed) ---
// One newline-delimited JSON line per array element (the channel's wire form).
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-abc-123';
const initEvent = {
  type: 'system',
  subtype: 'init',
  cwd: '/fake/ontum-overnight',
  session_id: SESSION,
  tools: ['Task', 'Bash', 'Glob', 'Read', 'Edit'],
};
const assistantEvent = {
  type: 'assistant',
  message: {
    role: 'assistant',
    content: [{ type: 'text', text: 'Hello from the engine.' }],
  },
  session_id: SESSION,
};
const resultEvent = {
  type: 'result',
  subtype: 'success',
  is_error: false,
  duration_ms: 1234,
  num_turns: 1,
  session_id: SESSION,
  total_cost_usd: 0.0021,
  usage: { input_tokens: 10, output_tokens: 5 },
  result: 'Hello from the engine.',
};
const STREAM = [line(initEvent), line(assistantEvent), line(resultEvent)];

// ---- a fake engine process (no real model call, no key, no cost) ------------
// Mirrors child_process.spawn's contract: returns a child EventEmitter with
// stdin (a write sink), stdout/stderr (emitters), and 'error'/'close' events.
function makeFakeEngine(lines, opts) {
  const o = opts || {};
  const stdinChunks = [];
  const calls = [];
  function spawn(bin, args, options) {
    calls.push({ bin, args, options });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write(chunk) {
        stdinChunks.push(chunk.toString('utf8'));
        return true;
      },
      end() {},
    };
    // Emit asynchronously, after driveTurn has attached its listeners + written
    // stdin — exactly as a real child streams back after it is fed.
    setImmediate(function () {
      const blob = lines.join('');
      if (o.split) {
        // Split mid-line to prove the line-buffering across torn stdout chunks.
        const mid = Math.floor(blob.length / 2);
        child.stdout.emit('data', Buffer.from(blob.slice(0, mid), 'utf8'));
        child.stdout.emit('data', Buffer.from(blob.slice(mid), 'utf8'));
      } else {
        child.stdout.emit('data', Buffer.from(blob, 'utf8'));
      }
      if (o.stderr) child.stderr.emit('data', Buffer.from(o.stderr, 'utf8'));
      child.emit('close', typeof o.code === 'number' ? o.code : 0);
    });
    return child;
  }
  return { spawn, stdinChunks, calls };
}

// 1. encodeUserMessage — the stdin envelope the channel reads.
check('encodeUserMessage emits a newline-terminated user envelope', () => {
  const wire = engine.encodeUserMessage('drive this');
  assert.ok(wire.endsWith('\n'), 'newline-terminated (one NDJSON line)');
  const obj = JSON.parse(wire.trim());
  assert.strictEqual(obj.type, 'user');
  assert.strictEqual(obj.message.role, 'user');
  assert.deepStrictEqual(obj.message.content, [
    { type: 'text', text: 'drive this' },
  ]);
});

// 2. engineArgs — the flags that open the stream-json channel.
check('engineArgs opens the stream-json channel with the advertised flags', () => {
  const args = engine.engineArgs({});
  for (const flag of [
    '--print',
    '--input-format',
    'stream-json',
    '--output-format',
    '--include-partial-messages',
  ]) {
    assert.ok(args.includes(flag), 'args include ' + flag);
  }
  // input AND output are stream-json (the value appears for both flags).
  assert.ok(
    args.filter((a) => a === 'stream-json').length >= 2,
    'both input and output formats are stream-json'
  );
  // conservative default permission mode
  const pm = args.indexOf('--permission-mode');
  assert.ok(pm >= 0 && args[pm + 1] === 'default', 'default permission mode');
});

check('engineArgs forwards resume + fork-session + model', () => {
  const args = engine.engineArgs({
    resume: 'sess-xyz',
    forkSession: true,
    model: 'claude-x',
    permissionMode: 'plan',
  });
  const r = args.indexOf('--resume');
  assert.ok(r >= 0 && args[r + 1] === 'sess-xyz', 'resume id forwarded');
  assert.ok(args.includes('--fork-session'), 'fork-session forwarded');
  const m = args.indexOf('--model');
  assert.ok(m >= 0 && args[m + 1] === 'claude-x', 'model forwarded');
  const pm = args.indexOf('--permission-mode');
  assert.strictEqual(args[pm + 1], 'plan', 'permission mode forwarded');
});

// 3. foldReply — fold the output stream into one turn's reply.
check('foldReply folds the event stream into the turn reply', () => {
  const events = STREAM.map((l) => JSON.parse(l.trim()));
  const reply = engine.foldReply(events);
  assert.strictEqual(reply.sessionId, SESSION, 'session id from init');
  assert.ok(reply.tools.includes('Bash'), 'tools list proves env inherited');
  assert.deepStrictEqual(
    reply.entries.map((e) => e.kind),
    ['assistant-text'],
    'the assistant message folded to a render entry'
  );
  assert.strictEqual(reply.text, 'Hello from the engine.', 'the reply text');
  assert.strictEqual(reply.isError, false, 'success is not an error');
  assert.strictEqual(reply.subtype, 'success');
  assert.strictEqual(reply.cost, 0.0021, 'cost surfaced (row 18 rides here)');
  assert.deepStrictEqual(reply.usage, { input_tokens: 10, output_tokens: 5 });
  assert.strictEqual(reply.durationMs, 1234);
  assert.strictEqual(reply.numTurns, 1);
});

check('foldReply falls back to assistant text when result carries no string', () => {
  const noResultString = Object.assign({}, resultEvent);
  delete noResultString.result;
  const reply = engine.foldReply([initEvent, assistantEvent, noResultString]);
  assert.strictEqual(
    reply.text,
    'Hello from the engine.',
    'fell back to the folded assistant text (never fabricated)'
  );
  assert.strictEqual(reply.isError, false);
});

check('foldReply reports a missing result honestly (no-result, error)', () => {
  const reply = engine.foldReply([initEvent, assistantEvent]);
  assert.strictEqual(reply.subtype, 'no-result', 'absence is reported');
  assert.strictEqual(reply.isError, true, 'an unclosed turn is an error');
  assert.strictEqual(reply.text, 'Hello from the engine.');
});

check('foldReply flags an engine error result', () => {
  const errResult = {
    type: 'result',
    subtype: 'error_during_execution',
    is_error: true,
    session_id: SESSION,
  };
  const reply = engine.foldReply([initEvent, errResult]);
  assert.strictEqual(reply.isError, true);
  assert.strictEqual(reply.subtype, 'error_during_execution');
});

// 4. driveTurn — the full round-trip over the fake engine.
(async function driveTurnRoundTrip() {
  const fake = makeFakeEngine(STREAM);
  const reply = await engine.driveTurn({
    prompt: 'what is 2+2?',
    spawn: fake.spawn,
    bin: 'claude',
    cwd: '/fake/ontum-overnight',
  });
  check('driveTurn writes the encoded prompt to the engine stdin', () => {
    assert.strictEqual(fake.stdinChunks.length, 1, 'exactly one stdin write');
    const sent = JSON.parse(fake.stdinChunks[0].trim());
    assert.strictEqual(sent.type, 'user');
    assert.strictEqual(sent.message.content[0].text, 'what is 2+2?');
  });
  check('driveTurn spawns the engine on the stream-json channel', () => {
    assert.strictEqual(fake.calls.length, 1, 'spawned once');
    assert.strictEqual(fake.calls[0].bin, 'claude');
    assert.ok(fake.calls[0].args.includes('--input-format'));
    assert.strictEqual(fake.calls[0].options.cwd, '/fake/ontum-overnight');
  });
  check('driveTurn resolves the folded reply', () => {
    assert.strictEqual(reply.sessionId, SESSION);
    assert.strictEqual(reply.text, 'Hello from the engine.');
    assert.strictEqual(reply.cost, 0.0021);
    assert.strictEqual(reply.isError, false);
    assert.strictEqual(reply.exitCode, 0, 'process exit code captured');
  });

  // Chunk-split stdout proves the line buffer reassembles torn reads.
  const fake2 = makeFakeEngine(STREAM, { split: true });
  const reply2 = await engine.driveTurn({ prompt: 'x', spawn: fake2.spawn });
  check('driveTurn reassembles stream-json split across stdout chunks', () => {
    assert.strictEqual(reply2.text, 'Hello from the engine.');
    assert.strictEqual(reply2.sessionId, SESSION);
  });

  // A spawn that errors rejects (a real failure is surfaced, not swallowed).
  await check_async('driveTurn rejects when the engine cannot spawn', async () => {
    function badSpawn() {
      const child = new EventEmitter();
      child.stdout = new EventEmitter();
      child.stderr = new EventEmitter();
      child.stdin = { write() {}, end() {} };
      setImmediate(() => child.emit('error', new Error('ENOENT: no claude')));
      return child;
    }
    let threw = null;
    try {
      await engine.driveTurn({ prompt: 'x', spawn: badSpawn });
    } catch (e) {
      threw = e;
    }
    assert.ok(threw && /ENOENT/.test(threw.message), 'the spawn error propagated');
  });

  // 5. Extension wiring — drive a turn from the surface (host-free).
  await extensionWiring();

  // 6. Shell composer markup.
  check('the shell renders a composer that posts ontum:send-prompt', () => {
    const html = shell.renderShell({});
    assert.ok(/ontum-compose-input/.test(html), 'a prompt input exists');
    assert.ok(/ontum-compose-send/.test(html), 'a send button exists');
    assert.ok(/ontum:send-prompt/.test(html), 'it posts a send-prompt message');
    assert.ok(/ontum:turn-reply/.test(html), 'it handles the turn-reply message');
  });

  console.log(
    '\n' + passed + ' checks passed — row 5 evidence is green.'
  );
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// An async-aware check (await the body, then count it).
async function check_async(label, fn) {
  await fn();
  passed++;
  console.log('  ok  ' + label);
}

// Drive a turn through the real extension module with an injected fake engine.
async function extensionWiring() {
  const posted = [];
  let messageHandler = null;
  let capturedPanel = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: '/fake/ontum-overnight' } }] },
    window: {
      createWebviewPanel() {
        capturedPanel = {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) {
              messageHandler = cb;
            },
            postMessage(m) {
              posted.push(m);
              return true;
            },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
        return capturedPanel;
      },
    },
    commands: {
      registerCommand(id, cb) {
        registered[id] = cb;
        return { dispose() {} };
      },
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

  const fake = makeFakeEngine(STREAM);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND](); // open the panel + wire the message handler
  ext.__setSpawnForTest(fake.spawn); // inject the fake engine

  // Direct drive (deterministic await).
  const reply = await ext.sendPrompt('drive from the surface');
  check('sendPrompt drives a turn and resolves the reply', () => {
    assert.ok(reply, 'a reply came back');
    assert.strictEqual(reply.text, 'Hello from the engine.');
    assert.strictEqual(
      JSON.parse(fake.stdinChunks[0].trim()).message.content[0].text,
      'drive from the surface',
      'the prompt was sent down the channel'
    );
  });
  check('sendPrompt posts an ontum:turn-reply carrying the rendered reply', () => {
    const last = posted[posted.length - 1];
    assert.ok(last && last.type === 'ontum:turn-reply', 'turn-reply posted');
    assert.ok(/Hello from the engine\./.test(last.html), 'reply block rendered');
    assert.strictEqual(last.isError, false, 'success surfaced');
    assert.strictEqual(last.cost, 0.0021, 'cost surfaced to the composer');
  });

  // The webview message handler path also drives a turn.
  const before = posted.length;
  messageHandler({ type: 'ontum:send-prompt', text: 'via the handler' });
  // Let the async drive (setImmediate-backed fake) settle.
  await new Promise((r) => setImmediate(() => setImmediate(r)));
  check('the ontum:send-prompt handler drives a turn', () => {
    assert.ok(posted.length > before, 'a new turn-reply was posted');
    const last = posted[posted.length - 1];
    assert.strictEqual(last.type, 'ontum:turn-reply');
  });

  ext.__setSpawnForTest(null); // restore the production default
  ext.stopTail();
  ext.deactivate();
}
