// environment.test.js — proof for parity-checklist row 14.
//
// "Hooks / skills / settings inherited (the environment)."
//
// Normal Claude Code, on each turn, reads its on-disk config — the settings
// layers (`<cwd>/.claude/settings.json` + `.local.json` + `~/.claude/
// settings.json`), the hooks declared there, and the skills under
// `.claude/skills/*/SKILL.md` — and RUNS the hooks + LOADS the skills mid-turn.
// The bridge spike (SPIKE-FINDINGS.md) resolved this row to `inherit`: the
// engine is the SAME `claude` binary reading the SAME cwd config, so the hooks,
// skills, and settings configured on disk are loaded by the engine for free —
// the init event proves the environment is loaded. The surface does NOT
// re-implement hook execution or skill loading (the engine runs them); it owns
// only the SURFACE of the environment: (1) DISCOVER the settings LAYERS the CLI
// reads (each with its top-level keys), (2) DISCOVER the configured HOOKS by
// folding the `hooks` object across those layers, and (3) DISCOVER the
// available SKILLS by folding the skills dirs (project shadowing user). This
// test proves all three host-free (no billed model call):
//   - environment.settingsPathsFor / discoverSettings fold the layer search
//     path, present-flagged, missing/torn tolerant;
//   - environment.hooksFromSettings folds the CLI hooks shape to a flat list;
//   - environment.discoverHooks merges hooks across layers, sorted + scoped;
//   - environment.frontMatterValue reads an inline scalar AND a folded block
//     scalar (`description: >`) from a SKILL.md front-matter;
//   - environment.readSkillMeta / discoverSkills / listSkills fold the skills
//     dirs with project shadowing user;
//   - environment.listEnvironment combines the three folds;
//   - shell.renderEnvPanel / renderShell paint the region + ship it;
//   - extension.readEnvironment discovers a fake project + user config;
//   - a READ-ONLY live smoke folds the real ~/.claude + project .claude without
//     throwing.
// HONEST SCOPE: the engine remains authoritative on what a hook DOES and on
// whether a skill actually loads; the surface discovers + displays the
// inherited environment, and a real billed turn that fires a hook or invokes a
// skill is a human's to run.
//
// Run: node vscode/ontum-surface/test/environment.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Module = require('module');

let passed = 0;
let _lastOpen = null;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

const env = require(path.join(__dirname, '..', 'environment.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 14 — hooks / skills / settings inherited (the environment)');

// ---- a fake on-disk config (the same shape the CLI reads) ------------------
// <tmp>/.claude/settings.json         -> project: hooks (PreToolUse, Stop) + a
//                                        permissions key
// <tmp>/.claude/settings.local.json   -> local: hooks (PostToolUse) + env key
// <tmp>/.claude/skills/<name>/SKILL.md -> project skills (arc, shared)
// <tmp>/home/.claude/settings.json    -> user: hooks (SessionStart)
// <tmp>/home/.claude/skills/<name>/   -> user skills (breather, shared — the
//                                        last must be shadowed by project)
const STORE = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-env-'));
const HOME = path.join(STORE, 'home');
const PROJ_CLAUDE = path.join(STORE, '.claude');
const USER_CLAUDE = path.join(HOME, '.claude');
fs.mkdirSync(PROJ_CLAUDE, { recursive: true });
fs.mkdirSync(USER_CLAUDE, { recursive: true });

fs.writeFileSync(
  path.join(PROJ_CLAUDE, 'settings.json'),
  JSON.stringify({
    permissions: { allow: ['Read'] },
    hooks: {
      PreToolUse: [
        { matcher: 'Bash', hooks: [{ type: 'command', command: 'guard.sh' }] },
      ],
      Stop: [{ hooks: [{ type: 'command', command: 'done.sh' }] }],
    },
  })
);
fs.writeFileSync(
  path.join(PROJ_CLAUDE, 'settings.local.json'),
  JSON.stringify({
    env: { FOO: 'bar' },
    hooks: {
      PostToolUse: [
        { matcher: 'Edit', hooks: [{ type: 'command', command: 'fmt.sh' }] },
      ],
    },
  })
);
fs.writeFileSync(
  path.join(USER_CLAUDE, 'settings.json'),
  JSON.stringify({
    hooks: {
      SessionStart: [{ hooks: [{ type: 'command', command: 'hello.sh' }] }],
    },
  })
);

// project skills: `arc` (inline desc) + `shared` (block-scalar desc, must
// shadow the user `shared`).
function writeSkill(base, name, frontMatter) {
  const dir = path.join(base, 'skills', name);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'SKILL.md'), frontMatter);
}
writeSkill(
  PROJ_CLAUDE,
  'arc',
  '---\nname: arc\ndescription: Inline one-line description.\n---\nbody\n'
);
writeSkill(
  PROJ_CLAUDE,
  'shared',
  '---\nname: shared\ndescription: >\n  A folded block scalar that spans\n  two lines into one description.\n---\nbody\n'
);
// user skills: `breather` + `shared` (the user def — project must shadow it).
writeSkill(
  USER_CLAUDE,
  'breather',
  '---\nname: breather\ndescription: A user-scope skill.\n---\nbody\n'
);
writeSkill(
  USER_CLAUDE,
  'shared',
  '---\nname: shared\ndescription: THE USER VERSION (should be shadowed).\n---\nbody\n'
);

// ---- 1. settingsPathsFor / discoverSettings fold the layer search path -----
check('settingsPathsFor lists user, project, local in increasing precedence', () => {
  const paths = env.settingsPathsFor({ projectDir: STORE, userDir: HOME });
  assert.deepStrictEqual(paths.map((p) => p.scope), ['user', 'project', 'local']);
  assert.ok(paths[0].file.indexOf(path.join('home', '.claude', 'settings.json')) >= 0);
  assert.ok(/settings\.local\.json$/.test(paths[2].file), 'local layer is settings.local.json');
});
check('discoverSettings flags present layers + lists each layer top-level keys', () => {
  const got = env.discoverSettings({ projectDir: STORE, userDir: HOME });
  const byScope = {};
  got.forEach((s) => (byScope[s.scope] = s));
  assert.strictEqual(byScope.project.present, true, 'project settings present');
  assert.deepStrictEqual(byScope.project.keys, ['hooks', 'permissions'], 'sorted top-level keys');
  assert.strictEqual(byScope.local.present, true, 'local settings present');
  assert.deepStrictEqual(byScope.local.keys, ['env', 'hooks']);
  assert.strictEqual(byScope.user.present, true, 'user settings present');
  assert.deepStrictEqual(byScope.user.keys, ['hooks']);
});
check('discoverSettings: a missing layer is present:false, a torn one is present:true keys:[]', () => {
  const noLocal = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-env2-'));
  fs.mkdirSync(path.join(noLocal, '.claude'), { recursive: true });
  fs.writeFileSync(path.join(noLocal, '.claude', 'settings.json'), '{ not json');
  const got = env.discoverSettings({ projectDir: noLocal });
  const byScope = {};
  got.forEach((s) => (byScope[s.scope] = s));
  assert.strictEqual(byScope.local.present, false, 'a missing local layer -> present:false');
  assert.deepStrictEqual(byScope.local.keys, [], 'missing layer has no keys');
  assert.strictEqual(byScope.project.present, true, 'a torn-but-existing file is present:true');
  assert.deepStrictEqual(byScope.project.keys, [], 'torn file folds no keys (honest)');
  fs.rmSync(noLocal, { recursive: true, force: true });
});

// ---- 2. hooksFromSettings folds the CLI hooks shape to a flat list ---------
check('hooksFromSettings folds {Event:[{matcher,hooks:[{type,command}]}]} flat', () => {
  const list = env.hooksFromSettings(
    {
      hooks: {
        PreToolUse: [
          { matcher: 'Bash', hooks: [{ type: 'command', command: 'a.sh' }, { command: 'b.sh' }] },
        ],
        Stop: [{ hooks: [{ type: 'command', command: 'c.sh' }] }],
      },
    },
    'project'
  );
  // 2 entries under PreToolUse/Bash + 1 under Stop (no matcher -> '')
  assert.strictEqual(list.length, 3, 'every hook entry folded');
  const bash = list.filter((h) => h.event === 'PreToolUse');
  assert.deepStrictEqual(bash.map((h) => h.command).sort(), ['a.sh', 'b.sh']);
  bash.forEach((h) => assert.strictEqual(h.matcher, 'Bash', 'matcher carried'));
  const stop = list.find((h) => h.event === 'Stop');
  assert.strictEqual(stop.matcher, '', 'an event-wide hook has an empty matcher');
  assert.strictEqual(stop.command, 'c.sh');
  list.forEach((h) => assert.strictEqual(h.scope, 'project', 'scope tagged'));
});
check('hooksFromSettings tolerates non-objects / no hooks (-> [])', () => {
  assert.deepStrictEqual(env.hooksFromSettings(null, 'project'), []);
  assert.deepStrictEqual(env.hooksFromSettings({}, 'project'), []);
  assert.deepStrictEqual(env.hooksFromSettings({ hooks: 'nope' }, 'project'), []);
});

// ---- 3. discoverHooks merges across layers, sorted + scoped ----------------
check('discoverHooks merges hooks across user + project + local, scoped + sorted', () => {
  const list = env.discoverHooks({ projectDir: STORE, userDir: HOME });
  const events = list.map((h) => h.event);
  assert.deepStrictEqual(
    events.slice().sort(),
    events,
    'sorted by (event, matcher, command)'
  );
  const byEvent = {};
  list.forEach((h) => (byEvent[h.event] = h));
  assert.ok(byEvent.PreToolUse && byEvent.PreToolUse.scope === 'project', 'project PreToolUse hook');
  assert.ok(byEvent.PostToolUse && byEvent.PostToolUse.scope === 'local', 'local PostToolUse hook');
  assert.ok(byEvent.SessionStart && byEvent.SessionStart.scope === 'user', 'user SessionStart hook');
  assert.ok(byEvent.Stop && byEvent.Stop.scope === 'project', 'project Stop hook');
  assert.strictEqual(list.length, 4, 'all four layers folded their hooks');
});
check('discoverHooks with no sources -> []', () => {
  assert.deepStrictEqual(env.discoverHooks({}), []);
});

// ---- 4. frontMatterValue reads inline + folded block scalars ---------------
check('frontMatterValue reads an inline scalar, stripping quotes', () => {
  assert.strictEqual(env.frontMatterValue('name: arc\ndescription: hello', 'name'), 'arc');
  assert.strictEqual(env.frontMatterValue("description: 'quoted text'", 'description'), 'quoted text');
});
check('frontMatterValue folds a `>` block scalar into one space-joined line', () => {
  const fm = 'name: shared\ndescription: >\n  A folded block scalar that spans\n  two lines.\n';
  assert.strictEqual(
    env.frontMatterValue(fm, 'description'),
    'A folded block scalar that spans two lines.'
  );
});
check('frontMatterValue returns "" for an absent key', () => {
  assert.strictEqual(env.frontMatterValue('name: x', 'description'), '');
});

// ---- 5. readSkillMeta / discoverSkills / listSkills fold the skills dirs ----
check('readSkillMeta reads name + description from a SKILL.md front-matter', () => {
  const meta = env.readSkillMeta(path.join(PROJ_CLAUDE, 'skills', 'arc'), 'arc', 'project');
  assert.strictEqual(meta.name, 'arc');
  assert.strictEqual(meta.description, 'Inline one-line description.');
  assert.strictEqual(meta.scope, 'project');
});
check('readSkillMeta surfaces a skill with no SKILL.md under its dir name (honest empty desc)', () => {
  const dir = path.join(STORE, 'noskillmd');
  fs.mkdirSync(dir, { recursive: true });
  const meta = env.readSkillMeta(dir, 'noskillmd', 'project');
  assert.strictEqual(meta.name, 'noskillmd', 'still surfaced by dir name');
  assert.strictEqual(meta.description, '', 'empty description, never invented');
});
check('discoverSkills folds each immediate subdir, sorted by name', () => {
  const list = env.discoverSkills({ dir: env.skillsDirFor(STORE), scope: 'project' });
  const names = list.map((s) => s.name);
  assert.deepStrictEqual(names, ['arc', 'shared'], 'both project skills, sorted');
  const shared = list.find((s) => s.name === 'shared');
  assert.strictEqual(shared.description, 'A folded block scalar that spans two lines into one description.');
});
check('discoverSkills on a missing dir -> []', () => {
  assert.deepStrictEqual(env.discoverSkills({ dir: path.join(STORE, 'nope') }), []);
});
check('listSkills merges project + user; project shadows a shared skill name', () => {
  const list = env.listSkills({ projectDir: STORE, userDir: HOME });
  const byName = {};
  list.forEach((s) => (byName[s.name] = s));
  assert.ok(byName.arc && byName.arc.scope === 'project', 'project-only arc present');
  assert.ok(byName.breather && byName.breather.scope === 'user', 'user-only breather present');
  // `shared` is in BOTH -> project wins
  assert.strictEqual(byName.shared.scope, 'project', 'project shared shadows the user one');
  assert.ok(/folded block scalar/.test(byName.shared.description), 'the project def is kept');
  const names = list.map((s) => s.name);
  assert.strictEqual(new Set(names).size, names.length, 'deduped');
  assert.deepStrictEqual(names, names.slice().sort(), 'sorted');
});

// ---- 6. listEnvironment combines the three folds ---------------------------
check('listEnvironment returns { settings, hooks, skills } all folded', () => {
  const e = env.listEnvironment({ projectDir: STORE, userDir: HOME });
  assert.ok(Array.isArray(e.settings) && e.settings.length === 3, 'three settings layers');
  assert.ok(Array.isArray(e.hooks) && e.hooks.length === 4, 'four hooks');
  assert.ok(Array.isArray(e.skills) && e.skills.length === 3, 'three skills (arc, breather, shared)');
});

// ---- 7. shell.renderEnvPanel + renderShell paint + ship the region ---------
check('renderEnvPanel paints escaped settings/hooks/skills groups', () => {
  const html = shell.renderEnvPanel({
    settings: [{ scope: 'project', present: true, keys: ['hooks', 'permissions'] }],
    hooks: [{ event: 'PreToolUse', matcher: 'Bash', scope: 'project' }],
    skills: [{ name: 'arc', description: 'desc', scope: 'project' }],
  });
  assert.ok(/data-env-group="settings"/.test(html), 'settings group present');
  assert.ok(/data-env-settings="project"/.test(html), 'settings layer carries scope');
  assert.ok(/data-present="true"/.test(html), 'present flag painted');
  assert.ok(/data-env-hook="PreToolUse"/.test(html), 'hook carries its event');
  assert.ok(/data-env-skill="arc"/.test(html), 'skill carries its name');
});
check('renderEnvPanel escapes a hostile skill name (a fold, not a second source)', () => {
  const html = shell.renderEnvPanel({
    settings: [],
    hooks: [],
    skills: [{ name: '<script>x', description: '<b>y', scope: 'project' }],
  });
  assert.ok(!/<script>x/.test(html), 'the raw tag is not emitted');
  assert.ok(/&lt;script&gt;x/.test(html), 'it is HTML-escaped');
});
check('renderEnvPanel on empty groups paints honest notes (no fake rows)', () => {
  const html = shell.renderEnvPanel({ settings: [], hooks: [], skills: [] });
  assert.ok(/No settings layers/.test(html), 'empty settings note');
  assert.ok(/No hooks configured/.test(html), 'empty hooks note');
  assert.ok(/No skills available/.test(html), 'empty skills note');
});
check('renderShell carries the Environment region (ships even with no environment)', () => {
  const withEnv = shell.renderShell({
    environment: {
      settings: [{ scope: 'project', present: true, keys: ['hooks'] }],
      hooks: [{ event: 'Stop', matcher: '', scope: 'project' }],
      skills: [{ name: 'arc', description: 'd', scope: 'project' }],
    },
  });
  assert.ok(/data-region="environment"/.test(withEnv), 'the Environment region is in the aside');
  assert.ok(/data-env-skill="arc"/.test(withEnv), 'the passed skill is rendered');
  const bare = shell.renderShell({});
  assert.ok(/data-region="environment"/.test(bare), 'the region ships even with no environment (no regression)');
});

// ---- 8. extension.readEnvironment discovers a fake project + user config ---
check('extension.readEnvironment discovers the fake project + user environment', () => {
  const { ext } = loadExtension(STORE, HOME);
  const e = ext.readEnvironment();
  assert.ok(e && Array.isArray(e.settings) && Array.isArray(e.hooks) && Array.isArray(e.skills));
  const skillNames = e.skills.map((s) => s.name);
  assert.ok(skillNames.indexOf('arc') >= 0, 'project skill discovered');
  assert.ok(skillNames.indexOf('breather') >= 0, 'user skill discovered');
  const events = e.hooks.map((h) => h.event);
  assert.ok(events.indexOf('PreToolUse') >= 0, 'project hook discovered');
  assert.ok(events.indexOf('SessionStart') >= 0, 'user hook discovered');
  const presentScopes = e.settings.filter((s) => s.present).map((s) => s.scope).sort();
  assert.deepStrictEqual(presentScopes, ['local', 'project', 'user'], 'all three layers present');
});

// ---- 9. a READ-ONLY live smoke on the real ~/.claude + project .claude -----
// Folds the actual config on this machine without throwing — never writes,
// never spawns a model. Proves the discovery path runs against a real on-disk
// environment (the honest "what is configured here" view).
check('live smoke: listEnvironment folds the real ~/.claude + project .claude without throwing', () => {
  const real = env.listEnvironment({ projectDir: process.cwd(), userDir: os.homedir() });
  assert.ok(real && Array.isArray(real.settings), 'settings is a list — never throws');
  assert.ok(Array.isArray(real.hooks), 'hooks is a list');
  assert.ok(Array.isArray(real.skills), 'skills is a list');
  real.settings.forEach((s) => {
    assert.ok(typeof s.scope === 'string' && s.scope, 'each layer has a scope');
    assert.ok(typeof s.present === 'boolean', 'each carries an honest present flag');
    assert.ok(Array.isArray(s.keys), 'each carries a keys list');
  });
  real.skills.forEach((s) => assert.ok(typeof s.name === 'string' && s.name, 'each skill has a name'));
  real.hooks.forEach((h) => assert.ok(typeof h.event === 'string' && h.event, 'each hook has an event'));
});

try {
  fs.rmSync(STORE, { recursive: true, force: true });
} catch (_) {
  /* best-effort cleanup */
}

console.log('\n' + passed + ' checks passed — row 14 evidence is green.');
process.exit(0);

// ---- helpers ---------------------------------------------------------------

// loadExtension(cwd, home) -> require extension.js under a fake `vscode` whose
// workspace folder is `cwd` (so readEnvironment discovers that folder's
// `.claude`) and a fake `os.homedir()` of `home` (so the user layer is the fake
// one, not the real machine's). Cache-busted each call so state does not leak.
function loadExtension(cwd, home) {
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
            onDidReceiveMessage() {},
            postMessage() { return true; },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
    },
    commands: {
      registerCommand(id, cb) {
        if (id === 'ontum.surface.open') _lastOpen = cb;
        return { dispose() {} };
      },
    },
  };
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
  return { ext };
}
