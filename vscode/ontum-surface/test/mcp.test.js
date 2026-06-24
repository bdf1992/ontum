// mcp.test.js — proof for parity-checklist row 13.
//
// "MCP tools available + invocable."
//
// Normal Claude Code lets a configured MCP server's tools (named
// `mcp__<server>__<tool>`) be listed and called mid-turn. The bridge spike
// (SPIKE-FINDINGS.md) resolved this row to `inherit`: MCP is provided by the
// SAME `claude` binary reading the SAME cwd config, so a configured server is
// LOADED by the engine and its tools ride along in the init event's `tools`
// list exactly as the built-ins do; the engine invokes them (pass-through),
// authorizable by name via the row-9 allow-list. So the surface owns only the
// SURFACE of MCP: (1) RECOGNISE an `mcp__server__tool` name + split it,
// (2) group the engine's LIVE tools list by server (the proof of what loaded),
// (3) DISCOVER the CONFIGURED servers from the same on-disk config the CLI reads
// (`<cwd>/.mcp.json` + the user `~/.claude.json` mcpServers), and (4) MERGE the
// two into the surface's view (configured servers annotated with the live tools
// they expose). This test proves all four host-free (no billed model call):
//   - mcp.parseMcpTool / isMcpTool / mcpToolName recognise + split + join;
//   - mcp.mcpServersFromTools groups a live tools list by server (the LIVE view);
//   - mcp.transportOf / readMcpServerNames fold a fake config's mcpServers,
//     torn/missing tolerant;
//   - mcp.discoverMcpServers merges project + user with project shadowing user;
//   - mcp.listMcpServers annotates each configured server with the live tools +
//     an honest `available` flag (configured-not-loaded => available:false);
//   - shell.renderMcpPanel / renderShell paint the panel + ship the region;
//   - extension.readMcpServers discovers a fake project `.mcp.json` and, after a
//     turn whose init event named an MCP tool, marks that server available;
//   - engine.engineArgs threads --mcp-config / --strict-mcp-config (additive);
//   - a READ-ONLY live smoke folds the real `~/.claude.json` without throwing.
// HONEST SCOPE: the engine remains authoritative on what an MCP tool DOES and on
// whether a server actually connects; the surface recognises + discovers +
// offers + annotates, and a real billed turn that invokes an MCP tool is a
// human's to run.
//
// Run: node vscode/ontum-surface/test/mcp.test.js
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

const mcp = require(path.join(__dirname, '..', 'mcp.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 13 — MCP tools available + invocable');

// ---- a fake on-disk MCP config (the same shape the CLI reads) --------------
// <tmp>/.mcp.json                       -> project: server `weather` (http)
//                                          + server `db` (stdio, command)
// <tmp>/home/.claude.json mcpServers    -> user: `weather` (a DIFFERENT def —
//                                          project must shadow it) + `notes`
const STORE = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-mcp-'));
const HOME = path.join(STORE, 'home');
fs.mkdirSync(HOME, { recursive: true });
fs.writeFileSync(
  path.join(STORE, '.mcp.json'),
  JSON.stringify({
    mcpServers: {
      weather: { type: 'http', url: 'https://example.com/mcp' },
      db: { command: 'db-mcp', args: ['--port', '5432'] },
    },
  })
);
fs.writeFileSync(
  path.join(HOME, '.claude.json'),
  JSON.stringify({
    mcpServers: {
      weather: { command: 'should-be-shadowed' },
      notes: { url: 'https://notes.example.com/sse', type: 'sse' },
    },
  })
);

// ---- 1. parseMcpTool / isMcpTool / mcpToolName recognise + split + join ----
check('parseMcpTool splits mcp__server__tool, rejects plain/odd names', () => {
  assert.deepStrictEqual(mcp.parseMcpTool('mcp__weather__forecast'), {
    name: 'mcp__weather__forecast',
    server: 'weather',
    tool: 'forecast',
  });
  // a tool name may itself contain '__' (split on the FIRST separator)
  assert.deepStrictEqual(mcp.parseMcpTool('mcp__db__list__tables'), {
    name: 'mcp__db__list__tables',
    server: 'db',
    tool: 'list__tables',
  });
  ['Bash', 'Read', 'mcp__', 'mcp__noserver', 'mcp____tool', '', null, 42].forEach(
    (s) => assert.strictEqual(mcp.parseMcpTool(s), null, JSON.stringify(s) + ' is not an MCP tool')
  );
});
check('isMcpTool / mcpToolName recognise + round-trip the identifier', () => {
  assert.strictEqual(mcp.isMcpTool('mcp__weather__forecast'), true);
  assert.strictEqual(mcp.isMcpTool('Bash'), false);
  assert.strictEqual(mcp.mcpToolName('weather', 'forecast'), 'mcp__weather__forecast');
  // round-trip: join then parse gives back the parts
  const id = mcp.mcpToolName('db', 'query');
  assert.deepStrictEqual(mcp.parseMcpTool(id), { name: id, server: 'db', tool: 'query' });
});

// ---- 2. mcpServersFromTools groups the LIVE init tools list by server ------
check('mcpServersFromTools groups a live tools list by server (sorted, deduped)', () => {
  const live = mcp.mcpServersFromTools([
    'Read',
    'mcp__weather__forecast',
    'Bash',
    'mcp__weather__alerts',
    'mcp__db__query',
    'mcp__weather__forecast', // dup
  ]);
  assert.deepStrictEqual(live, [
    { server: 'db', tools: ['query'] },
    { server: 'weather', tools: ['alerts', 'forecast'] },
  ]);
  assert.deepStrictEqual(mcpEmpty(), []);
  function mcpEmpty() {
    return mcp.mcpServersFromTools(['Read', 'Bash']).concat(mcp.mcpServersFromTools(null));
  }
});

// ---- 3. transportOf / readMcpServerNames fold a config's mcpServers --------
check('transportOf reads the CLI config shape (type | url | command | unknown)', () => {
  assert.strictEqual(mcp.transportOf({ type: 'sse' }), 'sse');
  assert.strictEqual(mcp.transportOf({ url: 'https://x' }), 'http');
  assert.strictEqual(mcp.transportOf({ command: 'foo' }), 'stdio');
  assert.strictEqual(mcp.transportOf({}), 'unknown');
  assert.strictEqual(mcp.transportOf(null), 'unknown');
});
check('readMcpServerNames folds a config; missing/torn tolerant (-> [])', () => {
  const got = mcp.readMcpServerNames(path.join(STORE, '.mcp.json'), 'project');
  const byName = {};
  got.forEach((s) => (byName[s.name] = s));
  assert.ok(byName.weather && byName.weather.transport === 'http', 'weather -> http');
  assert.ok(byName.db && byName.db.transport === 'stdio', 'db -> stdio (command)');
  got.forEach((s) => assert.strictEqual(s.scope, 'project', 'scope tagged'));
  // missing file, and a torn (bad JSON) file both -> []
  assert.deepStrictEqual(mcp.readMcpServerNames(path.join(STORE, 'nope.json'), 'project'), []);
  const torn = path.join(STORE, 'torn.json');
  fs.writeFileSync(torn, '{ not json');
  assert.deepStrictEqual(mcp.readMcpServerNames(torn, 'project'), []);
});

// ---- 4. discoverMcpServers merges project + user, project shadows user -----
check('discoverMcpServers merges project + user; project shadows a shared name', () => {
  const list = mcp.discoverMcpServers({
    projectDir: STORE,
    userConfig: path.join(HOME, '.claude.json'),
  });
  const byName = {};
  list.forEach((s) => (byName[s.name] = s));
  assert.ok(byName.db && byName.db.scope === 'project', 'project-only db present');
  assert.ok(byName.notes && byName.notes.scope === 'user', 'user-only notes present');
  // `weather` is in BOTH -> project wins (http def, scope project)
  assert.strictEqual(byName.weather.scope, 'project', 'project weather shadows the user one');
  assert.strictEqual(byName.weather.transport, 'http', 'the project def (http) is the one kept');
  const names = list.map((s) => s.name);
  assert.strictEqual(new Set(names).size, names.length, 'deduped');
  assert.deepStrictEqual(names, names.slice().sort(), 'sorted');
});
check('discoverMcpServers with no config sources -> []', () => {
  assert.deepStrictEqual(mcp.discoverMcpServers({}), []);
});

// ---- 5. listMcpServers annotates configured servers with the live tools ----
check('listMcpServers marks a server available once the live env exposes its tools', () => {
  const list = mcp.listMcpServers({
    projectDir: STORE,
    userConfig: path.join(HOME, '.claude.json'),
    // the live env loaded weather's tools but NOT db's nor notes'
    tools: ['Read', 'mcp__weather__forecast', 'mcp__weather__alerts'],
  });
  const byName = {};
  list.forEach((s) => (byName[s.name] = s));
  assert.strictEqual(byName.weather.available, true, 'weather is available (live tools present)');
  assert.deepStrictEqual(byName.weather.tools, ['alerts', 'forecast'], 'its live tools, sorted');
  assert.strictEqual(byName.db.available, false, 'db configured but not loaded -> not available');
  assert.deepStrictEqual(byName.db.tools, [], 'no live tools for db');
  assert.strictEqual(byName.notes.available, false, 'notes configured but not loaded');
});
check('listMcpServers surfaces a live-only server (named by the env, no config)', () => {
  const list = mcp.listMcpServers({
    projectDir: STORE,
    userConfig: path.join(HOME, '.claude.json'),
    tools: ['mcp__ghost__do'], // a server in NO config file we read
  });
  const ghost = list.find((s) => s.name === 'ghost');
  assert.ok(ghost, 'the env-named server is surfaced');
  assert.strictEqual(ghost.scope, 'live', 'tagged scope live (the engine named it)');
  assert.strictEqual(ghost.available, true, 'its tool is live -> available');
});

// ---- 6. shell.renderMcpPanel + renderShell paint + ship the region ---------
check('renderMcpPanel paints escaped server blocks + mcp__server__tool ids', () => {
  const html = shell.renderMcpPanel([
    { name: 'weather', scope: 'project', transport: 'http', tools: ['forecast'], available: true },
    { name: 'db', scope: 'project', transport: 'stdio', tools: [], available: false },
  ]);
  assert.ok(/data-mcp-server="weather"/.test(html), 'server carries data-mcp-server');
  assert.ok(/data-available="true"/.test(html), 'available flag painted');
  assert.ok(/data-available="false"/.test(html), 'a not-loaded server is honestly false');
  assert.ok(/data-mcp-tool="mcp__weather__forecast"/.test(html), 'the exact engine tool id');
  assert.ok(/data-count="2"/.test(html), 'the count is honest');
});
check('renderMcpPanel escapes a hostile server name (a fold, not a second source)', () => {
  const html = shell.renderMcpPanel([
    { name: '<script>x', scope: 'live', transport: 'unknown', tools: [], available: false },
  ]);
  assert.ok(!/<script>x/.test(html), 'the raw tag is not emitted');
  assert.ok(/&lt;script&gt;x/.test(html), 'it is HTML-escaped');
});
check('renderMcpPanel on an empty list paints an honest note (no fake server)', () => {
  assert.ok(/ontum-empty/.test(shell.renderMcpPanel([])), 'empty note, not a fake row');
});
check('renderShell carries the MCP region (ships even with no servers)', () => {
  const withServers = shell.renderShell({
    mcpServers: [{ name: 'weather', scope: 'project', transport: 'http', tools: ['forecast'], available: true }],
  });
  assert.ok(/data-region="mcp"/.test(withServers), 'the MCP region is in the aside');
  assert.ok(/data-mcp-server="weather"/.test(withServers), 'the passed server is rendered');
  const bare = shell.renderShell({});
  assert.ok(/data-region="mcp"/.test(bare), 'the region ships even with no servers (no regression)');
});

// ---- 7. engine.engineArgs threads --mcp-config / --strict-mcp-config -------
check('engineArgs adds --mcp-config / --strict-mcp-config only when supplied', () => {
  const base = engine.engineArgs({ cwd: '/tmp' });
  assert.ok(!base.includes('--mcp-config'), 'no MCP flag by default (inherits cwd config)');
  const withCfg = engine.engineArgs({ cwd: '/tmp', mcpConfig: ['/a.json', '/b.json'], strictMcpConfig: true });
  const i = withCfg.indexOf('--mcp-config');
  assert.ok(i >= 0, '--mcp-config present');
  assert.strictEqual(withCfg[i + 1], '/a.json', 'first config follows the flag');
  assert.strictEqual(withCfg[i + 2], '/b.json', 'second config follows');
  assert.ok(withCfg.includes('--strict-mcp-config'), '--strict-mcp-config present when asked');
  // not strict unless asked
  const notStrict = engine.engineArgs({ cwd: '/tmp', mcpConfig: ['/a.json'] });
  assert.ok(!notStrict.includes('--strict-mcp-config'), 'strict is opt-in');
});

// ---- 8. extension.readMcpServers: discover + annotate after a live turn ----
function emit(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-mcp-1';
// The init event names an MCP tool for `weather` — proof the inherited env
// LOADED that configured server, so after this turn readMcpServers marks it
// available (the engine can invoke `mcp__weather__forecast`).
const STREAM = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read', 'mcp__weather__forecast'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'The forecast is sunny.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0001,
    result: 'The forecast is sunny.',
  },
].map(emit);

check('extension.readMcpServers discovers the project .mcp.json (configured view)', () => {
  const { ext } = loadExtension(STORE, HOME);
  const list = ext.readMcpServers();
  const byName = {};
  list.forEach((s) => (byName[s.name] = s));
  assert.ok(byName.weather && byName.weather.scope === 'project', 'project weather discovered');
  assert.ok(byName.db && byName.db.scope === 'project', 'project db discovered');
  // before any turn the live tools list is null -> nothing is "available" yet
  assert.strictEqual(byName.weather.available, false, 'configured-but-not-yet-loaded is honest');
});

(async function liveAnnotate() {
  const { ext } = loadExtension(STORE, HOME);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  const opened = lastOpen();
  opened();
  const onMessage = lastHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  const fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  // Drive a turn; its init event names mcp__weather__forecast.
  const reply = await ext.sendPrompt('what is the weather?');
  assert.ok(reply && Array.isArray(reply.tools), 'the turn reported a live tools list');
  assert.ok(reply.tools.indexOf('mcp__weather__forecast') >= 0, 'the MCP tool was in the live list');

  check('after a turn, readMcpServers marks the loaded server available + invocable', () => {
    const list = ext.readMcpServers();
    const byName = {};
    list.forEach((s) => (byName[s.name] = s));
    assert.strictEqual(byName.weather.available, true, 'weather is now available (live env loaded it)');
    assert.deepStrictEqual(byName.weather.tools, ['forecast'], 'its live tool is surfaced');
    assert.strictEqual(byName.db.available, false, 'db (not in the live list) stays honest: not loaded');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  // ---- 9. a READ-ONLY live smoke on the real ~/.claude.json --------------
  // Folds the user's actual config without throwing — never writes, never
  // spawns a model. Proves the discovery path runs against a real on-disk
  // config (the honest "what is configured on this machine" view).
  check('live smoke: listMcpServers folds the real ~/.claude.json without throwing', () => {
    const real = mcp.listMcpServers({
      projectDir: process.cwd(),
      userConfig: mcp.userConfigPathFor(os.homedir()),
      tools: null,
    });
    assert.ok(Array.isArray(real), 'a list (possibly empty) — never throws');
    real.forEach((s) => {
      assert.ok(typeof s.name === 'string' && s.name, 'each server has a name');
      assert.ok(typeof s.available === 'boolean', 'each carries an honest available flag');
    });
  });

  try {
    fs.rmSync(STORE, { recursive: true, force: true });
  } catch (_) {
    /* best-effort cleanup */
  }

  console.log('\n' + passed + ' checks passed — row 13 evidence is green.');
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

// loadExtension(cwd, home) -> require extension.js under a fake `vscode` whose
// workspace folder is `cwd` (so readMcpServers discovers that folder's
// `.mcp.json`) and a fake `os.homedir()` of `home` (so the user-config path is
// the fake one, not the real machine's). Cache-busted each call so state does
// not leak between checks.
function loadExtension(cwd, home) {
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
  // The extension reads os.homedir() to find the user MCP config; point it at
  // the fake HOME so the test is hermetic (the real ~/.claude.json is only
  // touched by the explicit read-only smoke above).
  const realHomedir = os.homedir;
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === 'vscode') return fakeVscode;
    if (request === 'os') {
      return Object.assign({}, os, { homedir: () => home });
    }
    return origLoad.call(this, request, parent, isMain);
  };
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;
  os.homedir = realHomedir;
  return { ext, registered, getHandler: () => messageHandler };
}

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call)
// AND records each spawn's argv + stdin, so a turn can be driven host-free and
// its init-event tools list (carrying an MCP tool) folded by the surface.
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
