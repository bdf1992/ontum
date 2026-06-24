// stream.test.js — proof for parity-checklist row 6.
//
// "Stream the assistant turn (text + thinking) as it arrives."
//
// The channel is INHERITED (SPIKE-FINDINGS.md): with --include-partial-messages
// the engine emits `stream_event` partials wrapping the Anthropic streaming
// events (content_block_start / _delta / _stop) for text AND thinking. This test
// proves the surface consumes them incrementally WITHOUT a real billed model
// call: it feeds a FAKE engine process canned partials (the exact shapes the
// spike's flags produce) and asserts:
//   - partialDelta folds ONE event into ONE tiny render instruction
//     (start/delta/stop · index · kind · text), tolerant of the wrapped and the
//     bare forms, deriving kind from the delta itself, ignoring non-partials;
//   - assembleStream folds the partial stream into the ordered live blocks, and
//     the reconstructed prose equals what foldReply yields from the final
//     message event (the preview and the fold never disagree — one source of
//     truth);
//   - driveTurn fires onEvent for every event (buffered across torn stdout
//     chunks), so the partials reach the surface as they arrive;
//   - the extension wiring streams the turn: sendPrompt posts an
//     `ontum:turn-delta` per partial (in order, before the terminal
//     `ontum:turn-reply`), and non-partial events post nothing;
//   - the shell renders an `ontum:turn-delta` handler that paints per-index
//     `data-streaming` blocks and a turn-reply path that drops the preview
//     before splicing the folded reply.
// Honest scope: this proves the partial-stream PLUMBING + the host message
// protocol (host-free, deterministic). Pixel-level incremental DOM mutation
// needs a webview host; a real billed streaming turn is left to a human at the
// surface.
//
// Run: node vscode/ontum-surface/test/stream.test.js
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
async function check_async(label, fn) {
  await fn();
  passed++;
  console.log('  ok  ' + label);
}

const engine = require(path.join(__dirname, '..', 'engine.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 6 — stream the assistant turn (text + thinking) as it arrives');

// ---- the captured partial stream (the shapes --include-partial-messages emits)
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-stream-1';
const init = {
  type: 'system',
  subtype: 'init',
  session_id: SESSION,
  tools: ['Task', 'Bash', 'Read'],
};
// A thinking block (index 0) streamed in two deltas.
const tStart = {
  type: 'stream_event',
  session_id: SESSION,
  event: { type: 'content_block_start', index: 0, content_block: { type: 'thinking', thinking: '' } },
};
const tD1 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 0, delta: { type: 'thinking_delta', thinking: 'Let me ' } },
};
const tD2 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 0, delta: { type: 'thinking_delta', thinking: 'think.' } },
};
const tStop = { type: 'stream_event', event: { type: 'content_block_stop', index: 0 } };
// A text block (index 1) streamed in two deltas.
const xStart = {
  type: 'stream_event',
  event: { type: 'content_block_start', index: 1, content_block: { type: 'text', text: '' } },
};
const xD1 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 1, delta: { type: 'text_delta', text: 'Hello ' } },
};
const xD2 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 1, delta: { type: 'text_delta', text: 'world.' } },
};
const xStop = { type: 'stream_event', event: { type: 'content_block_stop', index: 1 } };
// The final, authoritative message event + result (what foldReply folds).
const assistant = {
  type: 'assistant',
  session_id: SESSION,
  message: {
    role: 'assistant',
    content: [
      { type: 'thinking', thinking: 'Let me think.' },
      { type: 'text', text: 'Hello world.' },
    ],
  },
};
const result = {
  type: 'result',
  subtype: 'success',
  is_error: false,
  session_id: SESSION,
  total_cost_usd: 0.001,
  result: 'Hello world.',
};
const EVENTS = [init, tStart, tD1, tD2, tStop, xStart, xD1, xD2, xStop, assistant, result];
const STREAM = EVENTS.map(line);

// ---- a fake engine process (no real model call) -----------------------------
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
    setImmediate(function () {
      const blob = lines.join('');
      if (o.split) {
        const mid = Math.floor(blob.length / 2);
        child.stdout.emit('data', Buffer.from(blob.slice(0, mid), 'utf8'));
        child.stdout.emit('data', Buffer.from(blob.slice(mid), 'utf8'));
      } else {
        child.stdout.emit('data', Buffer.from(blob, 'utf8'));
      }
      child.emit('close', typeof o.code === 'number' ? o.code : 0);
    });
    return child;
  }
  return { spawn, stdinChunks, calls };
}

// 1. partialDelta — one event -> one tiny render instruction (or null).
check('partialDelta reads a thinking block start/delta/stop', () => {
  assert.deepStrictEqual(engine.partialDelta(tStart), {
    phase: 'start', index: 0, kind: 'assistant-thinking',
  });
  assert.deepStrictEqual(engine.partialDelta(tD1), {
    phase: 'delta', index: 0, kind: 'assistant-thinking', text: 'Let me ',
  });
  assert.deepStrictEqual(engine.partialDelta(tStop), { phase: 'stop', index: 0 });
});
check('partialDelta reads a text block delta', () => {
  assert.deepStrictEqual(engine.partialDelta(xD1), {
    phase: 'delta', index: 1, kind: 'assistant-text', text: 'Hello ',
  });
});
check('partialDelta ignores non-partial events (init, assistant, result)', () => {
  assert.strictEqual(engine.partialDelta(init), null);
  assert.strictEqual(engine.partialDelta(assistant), null);
  assert.strictEqual(engine.partialDelta(result), null);
  assert.strictEqual(engine.partialDelta(null), null);
  assert.strictEqual(engine.partialDelta({ type: 'whatever' }), null);
});
check('partialDelta accepts the bare (unwrapped) content_block form', () => {
  const bare = { type: 'content_block_delta', index: 2, delta: { type: 'text_delta', text: 'x' } };
  assert.deepStrictEqual(engine.partialDelta(bare), {
    phase: 'delta', index: 2, kind: 'assistant-text', text: 'x',
  });
});
check('partialDelta does not stream a tool_use block start (row 7 territory)', () => {
  const tool = {
    type: 'stream_event',
    event: { type: 'content_block_start', index: 0, content_block: { type: 'tool_use', name: 'Bash' } },
  };
  assert.strictEqual(engine.partialDelta(tool), null);
});

// 2. assembleStream — fold the partials into ordered live blocks, and prove the
//    preview equals the authoritative final fold (one source of truth).
check('assembleStream folds the partials into ordered blocks', () => {
  const blocks = engine.assembleStream(EVENTS);
  assert.strictEqual(blocks.length, 2, 'two blocks: thinking then text');
  assert.deepStrictEqual(blocks[0], { index: 0, kind: 'assistant-thinking', text: 'Let me think.' });
  assert.deepStrictEqual(blocks[1], { index: 1, kind: 'assistant-text', text: 'Hello world.' });
});
check('the streamed preview equals the final folded reply (no disagreement)', () => {
  const blocks = engine.assembleStream(EVENTS);
  const reply = engine.foldReply(EVENTS);
  // Same kinds, same order, same text — the partials previewed exactly the fold.
  assert.deepStrictEqual(
    blocks.map((b) => b.kind),
    reply.entries.map((e) => e.kind),
    'preview kinds match the folded entry kinds'
  );
  assert.deepStrictEqual(
    blocks.map((b) => b.text),
    reply.entries.map((e) => e.text),
    'preview text matches the folded entry text'
  );
});

// 3. driveTurn — fires onEvent for every event, buffered across torn chunks.
(async function driveTurnStreams() {
  const collected = [];
  const fake = makeFakeEngine(STREAM, { split: true });
  const reply = await engine.driveTurn({
    prompt: 'say hello',
    spawn: fake.spawn,
    onEvent: (ev) => collected.push(ev),
  });
  check('driveTurn fires onEvent for every event (across torn stdout chunks)', () => {
    assert.strictEqual(collected.length, EVENTS.length, 'every line reached onEvent');
    const blocks = engine.assembleStream(collected);
    assert.deepStrictEqual(blocks.map((b) => b.text), ['Let me think.', 'Hello world.']);
  });
  check('driveTurn still resolves the folded reply alongside the stream', () => {
    assert.strictEqual(reply.text, 'Hello world.');
    assert.strictEqual(reply.isError, false);
  });

  // 4. Extension wiring — stream the turn from the surface (host-free).
  await extensionWiring();

  // 5. Shell markup — the streaming handler + the preview-clear reconcile.
  check('the shell renders an ontum:turn-delta handler with streaming blocks', () => {
    const html = shell.renderShell({});
    assert.ok(/ontum:turn-delta/.test(html), 'it handles the turn-delta message');
    assert.ok(/data-streaming/.test(html), 'it paints a streaming preview block');
    assert.ok(/data-stream-index/.test(html), 'preview blocks are keyed per index');
    assert.ok(
      /querySelectorAll\('\.ontum-msg\[data-streaming="true"\]'\)/.test(html),
      'turn-reply drops the preview before splicing the folded reply'
    );
  });

  console.log('\n' + passed + ' checks passed — row 6 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// Drive a streaming turn through the real extension module with a fake engine.
async function extensionWiring() {
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

  const fake = makeFakeEngine(STREAM);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  ext.__setSpawnForTest(fake.spawn);

  const reply = await ext.sendPrompt('say hello');
  // Let any trailing async settle (the fake closes synchronously via setImmediate).
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  const deltas = posted.filter((m) => m && m.type === 'ontum:turn-delta');
  const replies = posted.filter((m) => m && m.type === 'ontum:turn-reply');

  check('sendPrompt posts an ontum:turn-delta per partial, in order', () => {
    // 8 partials in EVENTS (2 starts + 4 deltas + 2 stops).
    assert.strictEqual(deltas.length, 8, 'one turn-delta per renderable partial');
    assert.strictEqual(deltas[0].phase, 'start', 'first is a block start');
    assert.ok(deltas.some((d) => d.phase === 'stop'), 'a block stop is streamed');
  });
  check('the streamed deltas reconstruct the assistant text + thinking', () => {
    const byIndex = {};
    for (const d of deltas) {
      if (d.phase !== 'delta') continue;
      byIndex[d.index] = (byIndex[d.index] || '') + d.text;
    }
    assert.strictEqual(byIndex[0], 'Let me think.', 'thinking reconstructed from deltas');
    assert.strictEqual(byIndex[1], 'Hello world.', 'text reconstructed from deltas');
  });
  check('every turn-delta is posted BEFORE the terminal turn-reply', () => {
    const firstReply = posted.findIndex((m) => m && m.type === 'ontum:turn-reply');
    const lastDelta = posted.map((m) => m && m.type).lastIndexOf('ontum:turn-delta');
    assert.ok(firstReply >= 0, 'a turn-reply was posted');
    assert.ok(lastDelta >= 0 && lastDelta < firstReply, 'all deltas precede the reply');
  });
  check('the turn-reply still carries the folded reply (row 5 intact)', () => {
    assert.strictEqual(replies.length, 1, 'exactly one turn-reply');
    assert.ok(/Hello world\./.test(replies[0].html), 'folded reply rendered');
    assert.strictEqual(replies[0].isError, false);
    assert.strictEqual(reply.text, 'Hello world.', 'sendPrompt resolved the reply');
  });
  check('postTurnDelta posts nothing for a non-partial event', () => {
    const before = posted.length;
    const out = ext.postTurnDelta(result);
    assert.strictEqual(out, null, 'non-partial folds to null');
    assert.strictEqual(posted.length, before, 'nothing posted');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();
}
