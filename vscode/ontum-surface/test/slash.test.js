// slash.test.js — proof for parity-checklist row 10.
//
// "Slash commands."
//
// Normal Claude Code lets you type `/help`, `/clear`, `/compact`, or a project's
// own custom `/foo` and have the engine act on it. The bridge spike
// (SPIKE-FINDINGS.md) resolved this row to `inherit`: a slash command is
// PASS-THROUGH to the engine — sent as the turn's prompt text down the SAME
// stream-json channel row 5 drives. So the ontum surface does not re-implement
// what each command does; it (1) RECOGNISES a composed slash command, (2) PARSES
// it, (3) DISCOVERS the available commands from the same on-disk store the CLI
// reads (`<cwd>/.claude/commands/*.md` + `~/.claude/commands/*.md`, namespaced by
// subdir) merged with the common built-ins, and (4) offers them as a palette
// that fills the composer, routing the chosen command through the engine. This
// test proves all four host-free (no billed model call):
//   - slash.isSlashCommand / parseSlashCommand recognise + split a command;
//   - slash.discoverCommands folds a fake `.claude/commands` store (namespaced
//     subdir + front-matter description), torn/missing tolerant;
//   - slash.listSlashCommands merges built-ins + user + project with project
//     winning (the same shadowing the CLI honours), sorted + deduped;
//   - shell.renderSlashMenu / renderShell paint the palette + carry the filter
//     + fill wiring;
//   - extension.readSlashCommands discovers a fake project command;
//   - the pass-through: encodeUserMessage carries the raw `/command` text, and a
//     webview send of a slash command drives a turn whose stdin got that exact
//     text (proven by a fake spawn — no model call).
// HONEST SCOPE: the engine remains authoritative on what each command does and
// on the full built-in set; the surface recognises + discovers + offers +
// routes, and never blocks an unlisted command. A real billed turn that runs a
// live `/command` is a human's to run.
//
// Run: node vscode/ontum-surface/test/slash.test.js
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

const slash = require(path.join(__dirname, '..', 'slash.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 10 — slash commands');

// ---- a fake on-disk command store (the same shape the CLI reads) -----------
// <tmp>/.claude/commands/help.md         -> overrides the `help` built-in
// <tmp>/.claude/commands/deploy.md       -> a plain project command (frontmatter)
// <tmp>/.claude/commands/git/commit.md   -> a namespaced command -> git:commit
// <tmp>/.claude/commands/notes.txt       -> a non-.md file, ignored
const STORE = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-slash-'));
const CMDS = path.join(STORE, '.claude', 'commands');
fs.mkdirSync(path.join(CMDS, 'git'), { recursive: true });
fs.writeFileSync(
  path.join(CMDS, 'help.md'),
  '---\ndescription: Project help override\n---\nThe body.\n'
);
fs.writeFileSync(
  path.join(CMDS, 'deploy.md'),
  '# Deploy the app\nSteps to deploy.\n'
);
fs.writeFileSync(
  path.join(CMDS, 'git', 'commit.md'),
  'Craft a commit message from the staged diff.\n'
);
fs.writeFileSync(path.join(CMDS, 'notes.txt'), 'not a command\n');

// ---- 1. isSlashCommand recognises a command, rejects prose -----------------
check('isSlashCommand: true for /name, false for prose/bare slash', () => {
  ['/help', '  /clear', '/git:commit', '/foo bar'].forEach((s) =>
    assert.strictEqual(slash.isSlashCommand(s), true, JSON.stringify(s) + ' is a command')
  );
  ['', '/', '// a comment', '/ space', 'hello /help', null, undefined, 42].forEach((s) =>
    assert.strictEqual(slash.isSlashCommand(s), false, JSON.stringify(s) + ' is NOT a command')
  );
});

// ---- 2. parseSlashCommand splits name / args / raw -------------------------
check('parseSlashCommand splits name + args, keeps the raw pass-through text', () => {
  assert.deepStrictEqual(slash.parseSlashCommand('/help'), {
    name: 'help',
    args: '',
    raw: '/help',
  });
  assert.deepStrictEqual(slash.parseSlashCommand('  /review 123  '), {
    name: 'review',
    args: '123',
    raw: '/review 123',
  });
  assert.deepStrictEqual(slash.parseSlashCommand('/git:commit tidy up'), {
    name: 'git:commit',
    args: 'tidy up',
    raw: '/git:commit tidy up',
  });
  assert.strictEqual(slash.parseSlashCommand('not a command'), null);
});

// ---- 3. discoverCommands folds the on-disk command store -------------------
check('discoverCommands reads *.md (namespaced + frontmatter), ignores non-md', () => {
  const found = slash.discoverCommands({ dir: CMDS, scope: 'project' });
  const byName = {};
  found.forEach((c) => (byName[c.name] = c));
  assert.ok(byName.help, 'help.md discovered');
  assert.strictEqual(byName.help.description, 'Project help override', 'frontmatter description');
  assert.ok(byName.deploy, 'deploy.md discovered');
  assert.strictEqual(byName.deploy.description, 'Deploy the app', 'first body line (# stripped)');
  assert.ok(byName['git:commit'], 'namespaced git/commit.md -> git:commit');
  assert.ok(!byName.notes, 'the .txt file is ignored');
  found.forEach((c) => assert.strictEqual(c.scope, 'project', 'scope tagged project'));
  // sorted by name
  const names = found.map((c) => c.name);
  assert.deepStrictEqual(names, names.slice().sort(), 'deterministic sorted order');
});
check('discoverCommands tolerates a missing dir (-> [])', () => {
  assert.deepStrictEqual(
    slash.discoverCommands({ dir: path.join(STORE, 'nope', 'commands'), scope: 'project' }),
    []
  );
  assert.deepStrictEqual(slash.discoverCommands({}), []);
});

// ---- 4. listSlashCommands merges with project-over-builtin precedence ------
check('listSlashCommands merges built-ins + project, project shadows a built-in', () => {
  const list = slash.listSlashCommands({ projectDir: STORE });
  const byName = {};
  list.forEach((c) => (byName[c.name] = c));
  // built-ins present
  assert.ok(byName.clear && byName.clear.scope === 'builtin', 'a built-in survives');
  // project custom present
  assert.ok(byName.deploy && byName.deploy.scope === 'project', 'a project command appears');
  assert.ok(byName['git:commit'], 'the namespaced project command appears');
  // `help` exists in BOTH built-ins and the project store -> project wins
  assert.strictEqual(byName.help.scope, 'project', 'project /help shadows the built-in');
  assert.strictEqual(byName.help.description, 'Project help override');
  // no duplicate names
  const names = list.map((c) => c.name);
  assert.strictEqual(new Set(names).size, names.length, 'names are deduped');
  assert.deepStrictEqual(names, names.slice().sort(), 'sorted');
});
check('listSlashCommands with no dirs still offers the built-ins', () => {
  const list = slash.listSlashCommands({});
  assert.ok(list.length >= 1, 'built-ins are offered');
  list.forEach((c) => assert.strictEqual(c.scope, 'builtin'));
});

// ---- 5. shell.renderSlashMenu + renderShell paint + wire the palette -------
check('renderSlashMenu paints selectable, escaped command items', () => {
  const html = shell.renderSlashMenu([
    { name: 'help', scope: 'builtin', description: 'List <commands>' },
    { name: 'git:commit', scope: 'project', description: 'Commit' },
  ]);
  assert.ok(/data-command="help"/.test(html), 'help item carries data-command');
  assert.ok(/data-command="git:commit"/.test(html), 'namespaced item present');
  assert.ok(/data-count="2"/.test(html), 'the count is honest');
  assert.ok(/&lt;commands&gt;/.test(html), 'the description is HTML-escaped');
  assert.ok(/>\/help</.test(html), 'the command renders with its leading slash');
});
check('renderSlashMenu on an empty list paints an honest note', () => {
  const html = shell.renderSlashMenu([]);
  assert.ok(/ontum-empty/.test(html), 'an empty note, not a fake row');
});
check('renderShell carries the slash palette + its filter/fill wiring', () => {
  const html = shell.renderShell({
    slashCommands: [{ name: 'compact', scope: 'builtin', description: 'Compact' }],
  });
  assert.ok(/class="ontum-slash"/.test(html), 'the palette container is in the composer');
  assert.ok(/data-command="compact"/.test(html), 'the passed command is rendered');
  assert.ok(/function refreshSlash/.test(html), 'the filter-as-you-type wiring is present');
  assert.ok(/input\.value = '\/' \+ name \+ ' '/.test(html), 'picking a command fills the composer');
});
check('renderShell with no slashCommands still ships the palette container (no regression)', () => {
  const html = shell.renderShell({});
  assert.ok(/class="ontum-slash"/.test(html), 'the container ships even with no commands');
  assert.ok(/function refreshSlash/.test(html), 'the wiring ships too');
});

// ---- 6. extension.readSlashCommands discovers the project store ------------
check('extension.readSlashCommands discovers the project commands for the cwd', () => {
  const { ext } = loadExtension(STORE);
  const list = ext.readSlashCommands();
  const byName = {};
  list.forEach((c) => (byName[c.name] = c));
  assert.ok(byName.deploy && byName.deploy.scope === 'project', 'the project /deploy is offered');
  assert.ok(byName['git:commit'], 'the namespaced project command is offered');
  assert.ok(byName.clear && byName.clear.scope === 'builtin', 'built-ins are still offered');
});

// ---- 7. the pass-through: a slash command rides the engine prompt channel --
check('encodeUserMessage carries the raw /command text unaltered (pass-through)', () => {
  const line = engine.encodeUserMessage('/compact please');
  const obj = JSON.parse(line);
  assert.strictEqual(obj.type, 'user');
  assert.strictEqual(obj.message.content[0].text, '/compact please', 'the slash text is sent verbatim');
});

function emit(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-slash-1';
const STREAM = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Compacted.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0001,
    result: 'Compacted.',
  },
].map(emit);

(async function passthrough() {
  const { ext } = loadExtension(STORE);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  // open the panel via the registered command (captured in loadExtension)
  const opened = lastOpen();
  opened();
  const onMessage = lastHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  const fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  // The webview sends a slash command exactly as the composer would.
  onMessage({ type: 'ontum:send-prompt', text: '/compact' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('a webview-sent slash command drives a turn whose stdin got the /command', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    assert.ok(fake.stdin.length >= 1, 'something was written to stdin');
    const sent = fake.stdin.join('');
    const obj = JSON.parse(sent.trim().split('\n')[0]);
    assert.strictEqual(obj.message.content[0].text, '/compact', 'the slash command reached the engine verbatim');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  try {
    fs.rmSync(STORE, { recursive: true, force: true });
  } catch (_) {
    /* best-effort cleanup */
  }

  console.log('\n' + passed + ' checks passed — row 10 evidence is green.');
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
// workspace folder is `cwd` (so readSlashCommands discovers that folder's
// `.claude/commands`). Cache-busted each call so state does not leak.
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
// assert the slash command reached the engine prompt channel verbatim.
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
