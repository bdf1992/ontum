// mentions.test.js — proof for parity-checklist row 12.
//
// "@-mentions / IDE selection context."
//
// Normal Claude Code lets you (a) type `@path/to/file` to pull a workspace file
// into the turn's context, and (b) carry the active editor selection (the file +
// the highlighted line range) into the turn automatically. Both are CONTEXT the
// surface attaches to the prompt that rides the SAME stream-json channel row 5
// drives — the engine reads `@file` and the selection note; the surface does not
// re-implement file reading. So the ontum surface owns only the SURFACE of
// mentions + selection: it (1) RECOGNISES an @-mention and the partial token at
// the caret, (2) DISCOVERS the workspace files to offer as a completion palette
// (a bounded fold of the same tree the editor sees), and (3) ATTACHES the IDE
// selection as a marked, deterministic context preamble. This test proves all of
// it host-free (no billed model call, no VS Code host):
//   - mentions.isMention / parseMentions recognise + extract @-mentions and
//     leave an email's '@' / a bare '/' alone;
//   - mentions.mentionQuery returns the partial token being typed at the caret;
//   - mentions.discoverFiles folds a fake workspace tree, BOUNDED (limit) and
//     skipping the noise dirs (.git/node_modules) + dotfiles, missing -> [];
//   - mentions.selectionContext / withSelectionContext fold a selection record
//     into a marked preamble and leave a no-selection prompt UNCHANGED;
//   - shell.renderMentionMenu / renderShell paint the palette + carry the
//     filter/replace wiring;
//   - extension.readMentionTargets discovers a fake workspace's files;
//   - the round-trip: a webview send WITH an injected selection drives a turn
//     whose stdin carries the selection-context preamble + the prompt, and a
//     send with NO selection sends the typed text (incl. an @-mention) verbatim
//     (proven by a fake spawn — no model call).
// HONEST SCOPE: the engine remains authoritative on what an @-mention pulls in;
// the surface recognises + discovers + offers + attaches, and an unlisted path
// still sends. A live editor selection comes from the VS Code host
// (window.activeTextEditor); the fold is proven host-free against a record. A
// real billed turn is a human's to run.
//
// Run: node vscode/ontum-surface/test/mentions.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Module = require('module');
const { EventEmitter } = require('events');

let passed = 0;
let _lastHandler = null;
let _lastOpen = null;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

const mentions = require(path.join(__dirname, '..', 'mentions.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 12 — @-mentions / IDE selection context');

// ---- a fake workspace tree (the same shape the editor walks) ---------------
// <tmp>/README.md
// <tmp>/src/app.js
// <tmp>/src/util/strings.js
// <tmp>/.git/HEAD                 -> a noise dir, skipped
// <tmp>/node_modules/dep/index.js -> a noise dir, skipped
// <tmp>/.env                      -> a dotfile, skipped
const WS = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-mention-'));
fs.mkdirSync(path.join(WS, 'src', 'util'), { recursive: true });
fs.mkdirSync(path.join(WS, '.git'), { recursive: true });
fs.mkdirSync(path.join(WS, 'node_modules', 'dep'), { recursive: true });
fs.writeFileSync(path.join(WS, 'README.md'), '# readme\n');
fs.writeFileSync(path.join(WS, 'src', 'app.js'), 'console.log(1)\n');
fs.writeFileSync(path.join(WS, 'src', 'util', 'strings.js'), 'module.exports={}\n');
fs.writeFileSync(path.join(WS, '.git', 'HEAD'), 'ref: refs/heads/main\n');
fs.writeFileSync(path.join(WS, 'node_modules', 'dep', 'index.js'), 'x\n');
fs.writeFileSync(path.join(WS, '.env'), 'SECRET=1\n');

// ---- 1. isMention / parseMentions recognise + extract ----------------------
check('isMention: true for an @path, false for prose / email / bare slash', () => {
  ['@README.md', 'see @src/app.js please', '@src/util/strings.js'].forEach((s) =>
    assert.strictEqual(mentions.isMention(s), true, JSON.stringify(s) + ' has a mention')
  );
  ['', 'hello world', 'email me at a@b.com', 'a/b/c', null, undefined, 42].forEach((s) =>
    assert.strictEqual(mentions.isMention(s), false, JSON.stringify(s) + ' has NO mention')
  );
});
check('parseMentions extracts every @path in order with its offset', () => {
  const got = mentions.parseMentions('compare @src/app.js with @README.md now');
  assert.strictEqual(got.length, 2, 'two mentions found');
  assert.strictEqual(got[0].path, 'src/app.js');
  assert.strictEqual(got[0].raw, '@src/app.js');
  assert.strictEqual(got[1].path, 'README.md');
  // the offsets point at the '@'
  assert.strictEqual('compare @src/app.js with @README.md now'.charAt(got[0].index), '@');
  assert.strictEqual('compare @src/app.js with @README.md now'.charAt(got[1].index), '@');
  // an email's '@' is NOT preceded by start/space -> not a mention
  assert.deepStrictEqual(mentions.parseMentions('mail a@b.com'), []);
  // a trailing sentence dot is trimmed off the path
  assert.strictEqual(mentions.parseMentions('open @app.js.')[0].path, 'app.js');
  // a bare '@' is not a mention
  assert.deepStrictEqual(mentions.parseMentions('look @ this'), []);
});

// ---- 2. mentionQuery returns the partial token at the caret ----------------
check('mentionQuery returns the partial being typed, null outside a token', () => {
  assert.strictEqual(mentions.mentionQuery('hey @src/ap'), 'src/ap', 'partial path');
  assert.strictEqual(mentions.mentionQuery('@'), '', 'bare @ opens the whole palette');
  assert.strictEqual(mentions.mentionQuery('@README.md '), null, 'a space closed the token');
  assert.strictEqual(mentions.mentionQuery('no token here'), null, 'no @ -> null');
  assert.strictEqual(mentions.mentionQuery(null), null);
});

// ---- 3. discoverFiles folds the workspace tree, bounded + noise-skipping ----
check('discoverFiles folds the tree, skips .git/node_modules + dotfiles', () => {
  const found = mentions.discoverFiles({ dir: WS });
  const paths = found.map((f) => f.path);
  assert.ok(paths.indexOf('README.md') >= 0, 'README.md found');
  assert.ok(paths.indexOf('src/app.js') >= 0, 'src/app.js found (posix separators)');
  assert.ok(paths.indexOf('src/util/strings.js') >= 0, 'a nested file found');
  assert.ok(!paths.some((p) => p.indexOf('.git') >= 0), '.git is skipped');
  assert.ok(!paths.some((p) => p.indexOf('node_modules') >= 0), 'node_modules is skipped');
  assert.ok(paths.indexOf('.env') < 0, 'a dotfile is skipped');
  // each carries its base name + deterministic sorted order
  const app = found.find((f) => f.path === 'src/app.js');
  assert.strictEqual(app.name, 'app.js', 'the base name is carried');
  assert.deepStrictEqual(paths, paths.slice().sort(), 'deterministic sorted order');
});
check('discoverFiles honours the limit (bounded fold)', () => {
  const found = mentions.discoverFiles({ dir: WS, limit: 1 });
  assert.strictEqual(found.length, 1, 'capped at the limit');
});
check('discoverFiles tolerates a missing dir (-> []) and no dir (-> [])', () => {
  assert.deepStrictEqual(mentions.discoverFiles({ dir: path.join(WS, 'nope') }), []);
  assert.deepStrictEqual(mentions.discoverFiles({}), []);
  assert.deepStrictEqual(mentions.listMentionTargets({}), []);
});

// ---- 4. selectionContext / withSelectionContext fold a selection -----------
check('selectionContext folds a record into a marked preamble', () => {
  const ctx = mentions.selectionContext({
    file: 'src/app.js',
    startLine: 10,
    endLine: 20,
    text: 'const x = 1;',
  });
  assert.ok(/^\[selection src\/app\.js:10-20\]/.test(ctx), 'header has file + 1-based range');
  assert.ok(/const x = 1;/.test(ctx), 'the selected text is carried');
  // a single-line range degrades to :N (no fake range)
  const one = mentions.selectionContext({ file: 'a.js', startLine: 7, endLine: 7, text: 'y' });
  assert.ok(/^\[selection a\.js:7\]/.test(one), 'single line -> :N');
  // nothing to attach -> ''
  assert.strictEqual(mentions.selectionContext(null), '');
  assert.strictEqual(mentions.selectionContext({}), '');
});
check('withSelectionContext prepends a selection, leaves a no-selection prompt unchanged', () => {
  const sel = { file: 'a.js', startLine: 1, endLine: 2, text: 'hi' };
  const out = mentions.withSelectionContext('explain this', sel);
  assert.ok(out.indexOf('[selection a.js:1-2]') === 0, 'the preamble leads');
  assert.ok(/explain this$/.test(out), 'the prompt follows');
  // no selection -> the prompt is sent EXACTLY as typed (pass-through preserved)
  assert.strictEqual(mentions.withSelectionContext('explain this', null), 'explain this');
  assert.strictEqual(mentions.withSelectionContext('@README.md summarise', null),
    '@README.md summarise', 'an @-mention rides through verbatim');
});

// ---- 5. shell.renderMentionMenu + renderShell paint + wire the palette -----
check('renderMentionMenu paints selectable, escaped file items', () => {
  const html = shell.renderMentionMenu([
    { path: 'src/app.js', name: 'app.js' },
    { path: 'a<b>.js', name: 'a<b>.js' },
  ]);
  assert.ok(/data-mention="src\/app\.js"/.test(html), 'item carries data-mention');
  assert.ok(/data-count="2"/.test(html), 'the count is honest');
  assert.ok(/&lt;b&gt;/.test(html), 'the path is HTML-escaped');
  assert.ok(/>@src\/app\.js</.test(html), 'the path renders with its leading @');
});
check('renderMentionMenu on an empty list paints an honest note', () => {
  const html = shell.renderMentionMenu([]);
  assert.ok(/ontum-empty/.test(html), 'an empty note, not a fake row');
});
check('renderShell carries the mention palette + its filter/replace wiring', () => {
  const html = shell.renderShell({ mentionTargets: [{ path: 'src/app.js', name: 'app.js' }] });
  assert.ok(/class="ontum-mention"/.test(html), 'the palette container is in the composer');
  assert.ok(/data-mention="src\/app\.js"/.test(html), 'the passed file is rendered');
  assert.ok(/function refreshMention/.test(html), 'the filter-as-you-type wiring is present');
  assert.ok(/MENTION_TAIL/.test(html), 'the token-replace wiring is present');
});
check('renderShell with no mentionTargets still ships the palette container (no regression)', () => {
  const html = shell.renderShell({});
  assert.ok(/class="ontum-mention"/.test(html), 'the container ships even with no files');
  assert.ok(/function refreshMention/.test(html), 'the wiring ships too');
});

// ---- 6. extension.readMentionTargets discovers the workspace files ---------
check('extension.readMentionTargets discovers the workspace files for the cwd', () => {
  const { ext } = loadExtension(WS);
  const list = ext.readMentionTargets();
  const paths = list.map((f) => f.path);
  assert.ok(paths.indexOf('README.md') >= 0, 'README.md is offered');
  assert.ok(paths.indexOf('src/app.js') >= 0, 'src/app.js is offered');
  assert.ok(!paths.some((p) => p.indexOf('node_modules') >= 0), 'node_modules stays out');
});

// ---- 7. the round-trip: a driven turn carries the selection context --------
function emit(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-mention-1';
const STREAM = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Looked.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0001,
    result: 'Looked.',
  },
].map(emit);

(async function roundTrip() {
  const { ext } = loadExtension(WS);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  lastOpen()();
  const onMessage = lastHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  // (a) WITH an injected selection: the driven turn's stdin carries the marked
  // selection-context preamble ahead of the typed prompt.
  let fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  ext.__setSelectionForTest(function () {
    return { file: 'src/app.js', startLine: 3, endLine: 5, text: 'const y = 2;' };
  });
  onMessage({ type: 'ontum:send-prompt', text: 'explain @src/app.js' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('a turn driven with an editor selection carries it as context on stdin', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    const obj = JSON.parse(fake.stdin.join('').trim().split('\n')[0]);
    const sent = obj.message.content[0].text;
    assert.ok(sent.indexOf('[selection src/app.js:3-5]') === 0, 'the selection preamble leads');
    assert.ok(/const y = 2;/.test(sent), 'the selected text is carried');
    assert.ok(/explain @src\/app\.js$/.test(sent), 'the typed prompt (with its @-mention) follows verbatim');
  });

  // (b) WITHOUT a selection: the typed text (incl. the @-mention) is sent
  // EXACTLY as typed — the row-5/10 pass-through is preserved.
  fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  ext.__setSelectionForTest(function () { return null; });
  onMessage({ type: 'ontum:send-prompt', text: 'summarise @README.md' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('a turn driven with NO selection sends the typed @-mention verbatim', () => {
    const obj = JSON.parse(fake.stdin.join('').trim().split('\n')[0]);
    assert.strictEqual(obj.message.content[0].text, 'summarise @README.md',
      'no preamble — the prompt is sent exactly as typed');
  });

  ext.__setSpawnForTest(null);
  ext.__setSelectionForTest(null);
  ext.stopTail();
  ext.deactivate();

  try {
    fs.rmSync(WS, { recursive: true, force: true });
  } catch (_) {
    /* best-effort cleanup */
  }

  console.log('\n' + passed + ' checks passed — row 12 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// ---- helpers ---------------------------------------------------------------

function lastHandler() {
  return _lastHandler;
}
function lastOpen() {
  return _lastOpen;
}

// loadExtension(cwd) -> require extension.js under a fake `vscode` whose
// workspace folder is `cwd` (so readMentionTargets discovers that folder's
// files). The fake window has no activeTextEditor — the row-12 selection comes
// from the injected __setSelectionForTest seam, not a host. Cache-busted each
// call so state does not leak.
function loadExtension(cwd) {
  let messageHandler = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: cwd } }] },
    window: {
      createWebviewPanel() {
        return {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) {
              messageHandler = cb;
              _lastHandler = cb;
            },
            postMessage() {
              return true;
            },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
    },
    commands: {
      registerCommand(id, cb) {
        registered[id] = cb;
        if (id === 'ontum.surface.open') _lastOpen = cb;
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
  return { ext, registered, getHandler: () => messageHandler };
}

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call)
// AND records each spawn's argv + everything written to stdin, so the test can
// assert the selection context reached the engine prompt channel.
function makeFakeEngine(lines) {
  const calls = [];
  const stdin = [];
  function spawn(bin, args) {
    calls.push({ bin, args });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write(chunk) {
        stdin.push(chunk.toString());
        return true;
      },
      end() {},
    };
    setImmediate(function () {
      child.stdout.emit('data', Buffer.from(lines.join(''), 'utf8'));
      child.emit('close', 0);
    });
    return child;
  }
  return { spawn, calls, stdin };
}
