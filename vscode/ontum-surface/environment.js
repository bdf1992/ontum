// environment.js — discover + surface the inherited environment: the settings
// layers, the configured hooks, and the available skills (pure data + fs layer,
// no `vscode`).
//
// Row 14 of the parity checklist: "Hooks / skills / settings inherited (the
// environment)." The bridge spike (SPIKE-FINDINGS.md) resolved this row to
// `inherit`: the engine is the SAME `claude` binary reading the SAME cwd
// config, so the hooks, skills, and settings configured on disk are LOADED by
// the engine for free — the init event proves the environment is loaded
// (cwd-scoped, the full tool list present). The surface does NOT re-implement
// hook execution or skill loading (the engine runs them); it owns only the
// SURFACE of the environment:
//   1. DISCOVER the settings layers the CLI reads (`<cwd>/.claude/settings.json`
//      + `<cwd>/.claude/settings.local.json` + `~/.claude/settings.json`), each
//      surfaced with which top-level keys it carries (the search path the CLI
//      merges, so a cold reader sees what governs the turn),
//   2. DISCOVER the configured hooks by folding the `hooks` object across those
//      same settings layers into a flat, ordered list (event + matcher +
//      command + scope) — what the engine will run on PreToolUse / Stop / …,
//   3. DISCOVER the available skills by folding `<cwd>/.claude/skills/*/SKILL.md`
//      + `~/.claude/skills/*/SKILL.md` (name + description from each SKILL.md's
//      front-matter), project shadowing user.
//
// Discovery is a FOLD of the same on-disk config the CLI itself reads (the
// blueprint §The law: paint what is there, invent nothing), so it is proven
// host-free against a fake config — exactly as mcp.js folds the MCP config and
// slash.js folds the command store. The engine remains the authority on what a
// hook DOES and on whether a skill actually loads; the surface discovers +
// displays the inherited environment, and a real billed turn that fires a hook
// or invokes a skill is a human's to run.

'use strict';

const fs = require('fs');
const path = require('path');

// sortByKeys(...keys) -> a stable comparator over several string keys in order
// (so a hook list is deterministic: event, then matcher, then command).
function sortByKeys() {
  const keys = Array.prototype.slice.call(arguments);
  return (a, b) => {
    for (const k of keys) {
      const x = a && a[k] != null ? String(a[k]) : '';
      const y = b && b[k] != null ? String(b[k]) : '';
      if (x < y) return -1;
      if (x > y) return 1;
    }
    return 0;
  };
}

// readJson(file) -> the parsed object, or undefined when the file is MISSING
// (the layer simply does not exist), or null when it is present but TORN (bad
// JSON — present, but contributes no folded keys; never throws).
function readJson(file) {
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (_) {
    return undefined; // missing
  }
  try {
    return JSON.parse(raw);
  } catch (_) {
    return null; // present but torn
  }
}

// settingsPathsFor({ projectDir, userDir }) -> the settings layers the CLI
// reads, in increasing precedence: the user `~/.claude/settings.json`, the
// project shared `<cwd>/.claude/settings.json`, then the project-local
// `<cwd>/.claude/settings.local.json`. Pure path joins (no fs touch). A layer
// is included only when its base dir is supplied.
function settingsPathsFor(opts) {
  const o = opts || {};
  const out = [];
  if (o.userDir) {
    out.push({ scope: 'user', file: path.join(o.userDir, '.claude', 'settings.json') });
  }
  if (o.projectDir) {
    out.push({ scope: 'project', file: path.join(o.projectDir, '.claude', 'settings.json') });
    out.push({ scope: 'local', file: path.join(o.projectDir, '.claude', 'settings.local.json') });
  }
  return out;
}

// readSettingsSource(file, scope) -> { scope, file, present, keys } describing
// one settings layer. present:false when the file is MISSING; keys is the
// sorted list of its top-level setting keys (hooks, permissions, env, model, …)
// so the surface shows what each layer governs. A present-but-torn file is
// present:true with keys:[] (it exists but cannot be folded — honest, never
// invented).
function readSettingsSource(file, scope) {
  const obj = readJson(file);
  if (obj === undefined) return { scope: scope || 'project', file, present: false, keys: [] };
  if (!obj || typeof obj !== 'object') {
    return { scope: scope || 'project', file, present: true, keys: [] };
  }
  return { scope: scope || 'project', file, present: true, keys: Object.keys(obj).sort() };
}

// discoverSettings(opts) -> [settingsSource] for every layer the CLI reads
// (always all the shapes its base dirs imply, so the surface shows the full
// search path; `present` flags which actually exist on disk).
function discoverSettings(opts) {
  return settingsPathsFor(opts).map((s) => readSettingsSource(s.file, s.scope));
}

// hooksFromSettings(settings, scope) -> the flat list of configured hooks in
// one settings object's `hooks` key, folded from the CLI's shape:
//   hooks: { <Event>: [ { matcher?, hooks: [ { type, command }, … ] }, … ] }
// to [{ event, matcher, type, command, scope }]. Tolerant of odd shapes: a
// missing matcher -> '' (the event-wide hook), a hook entry with no command ->
// its type only. A non-object / no `hooks` -> [].
function hooksFromSettings(settings, scope) {
  const hooks =
    settings && settings.hooks && typeof settings.hooks === 'object'
      ? settings.hooks
      : null;
  if (!hooks) return [];
  const out = [];
  for (const event of Object.keys(hooks)) {
    const groups = Array.isArray(hooks[event]) ? hooks[event] : [];
    for (const g of groups) {
      const matcher = g && typeof g.matcher === 'string' ? g.matcher : '';
      const entries = g && Array.isArray(g.hooks) ? g.hooks : [];
      for (const h of entries) {
        out.push({
          event,
          matcher,
          type: h && h.type ? String(h.type) : 'command',
          command: h && h.command ? String(h.command) : '',
          scope: scope || 'project',
        });
      }
    }
  }
  return out;
}

// discoverHooks(opts) -> the merged list of configured hooks across the settings
// layers (user + project + local), each tagged with its scope, sorted by
// (event, matcher, command) so the order is deterministic. This is the
// CONFIGURED view (what is on disk); the engine actually runs them mid-turn
// (inherit). Missing/torn layers contribute none (never throws).
function discoverHooks(opts) {
  const sources = settingsPathsFor(opts);
  const out = [];
  for (const s of sources) {
    const obj = readJson(s.file);
    if (obj && typeof obj === 'object') {
      for (const h of hooksFromSettings(obj, s.scope)) out.push(h);
    }
  }
  out.sort(sortByKeys('event', 'matcher', 'command'));
  return out;
}

// skillsDirFor(base) -> the `<base>/.claude/skills` directory the CLI reads
// skills from (each skill is a subdir holding a SKILL.md). Pure path join.
function skillsDirFor(base) {
  return path.join(String(base || ''), '.claude', 'skills');
}

// frontMatterValue(fm, key) -> the value of `key:` in a YAML-ish front-matter
// block, handling the two shapes a SKILL.md uses: an inline scalar
// (`description: text`) and a folded/literal block scalar (`description: >` or
// `description: |` followed by more-indented continuation lines). The folded
// lines are joined with single spaces (a fold, not a verbatim copy). '' when
// the key is absent. Never throws.
function frontMatterValue(fm, key) {
  const lines = String(fm).split(/\r?\n/);
  const re = new RegExp('^(\\s*)' + key + ':\\s*(.*)$', 'i');
  for (let i = 0; i < lines.length; i++) {
    const m = re.exec(lines[i]);
    if (!m) continue;
    const indent = m[1].length;
    const inline = m[2].trim();
    if (inline && inline !== '>' && inline !== '|' && inline !== '>-' && inline !== '|-') {
      return inline.replace(/^["']|["']$/g, '').trim();
    }
    // A block scalar: gather the following lines indented MORE than the key.
    const parts = [];
    for (let j = i + 1; j < lines.length; j++) {
      const ln = lines[j];
      if (!ln.trim()) {
        // a blank line inside a block scalar is a paragraph break; stop if the
        // block has already ended (next non-blank is less-indented) — simplest
        // honest behaviour: keep the first paragraph.
        if (parts.length) break;
        continue;
      }
      const lead = (ln.match(/^\s*/) || [''])[0].length;
      if (lead <= indent) break; // dedented — the block ended
      parts.push(ln.trim());
    }
    return parts.join(' ').trim();
  }
  return '';
}

// readSkillMeta(dir, name, scope) -> { name, description, scope } for one skill
// directory. The display name + description come from the SKILL.md front-matter
// (`name:` / `description:`) when present; a skill with no/torn SKILL.md is
// STILL surfaced under its directory name (the engine loads a skill by its
// directory, so the surface must not hide one just because its SKILL.md is
// unreadable — honest: an empty description, never invented). Never throws.
function readSkillMeta(dir, name, scope) {
  const file = path.join(dir, 'SKILL.md');
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (_) {
    return { name, description: '', scope: scope || 'project' };
  }
  const fm = /^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?/.exec(raw);
  if (!fm) return { name, description: '', scope: scope || 'project' };
  const declared = frontMatterValue(fm[1], 'name');
  const description = frontMatterValue(fm[1], 'description');
  return {
    name: declared || name,
    description,
    scope: scope || 'project',
  };
}

// discoverSkills({ dir, scope }) -> [{ name, description, scope }] for every
// immediate subdirectory of a skills dir (each is one skill). A missing/
// unreadable dir yields [] (the store simply has none). Sorted by name.
function discoverSkills(opts) {
  const o = opts || {};
  const root = o.dir;
  const scope = o.scope || 'project';
  const out = [];
  if (!root) return out;
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch (_) {
    return out; // a missing/unreadable skills dir contributes nothing
  }
  for (const ent of entries) {
    if (!ent.isDirectory()) continue;
    out.push(readSkillMeta(path.join(root, ent.name), ent.name, scope));
  }
  out.sort(sortByKeys('name'));
  return out;
}

// listSkills({ projectDir, userDir }) -> the merged, deduped, sorted skills
// the engine inherits: project `<cwd>/.claude/skills` over user
// `~/.claude/skills`. PROJECT shadows USER when a skill name appears in both
// (the same precedence the CLI honours for an overriding project skill).
function listSkills(opts) {
  const o = opts || {};
  const user = o.userDir
    ? discoverSkills({ dir: skillsDirFor(o.userDir), scope: 'user' })
    : [];
  const project = o.projectDir
    ? discoverSkills({ dir: skillsDirFor(o.projectDir), scope: 'project' })
    : [];
  const byName = new Map();
  for (const s of user) byName.set(s.name, s);
  for (const s of project) byName.set(s.name, s); // project shadows user
  const merged = Array.from(byName.values());
  merged.sort(sortByKeys('name'));
  return merged;
}

// listEnvironment({ projectDir, userDir }) -> the surface's inherited-
// environment view in one fold:
//   { settings:[settingsSource], hooks:[hook], skills:[skill] }
// the three faces of "the environment the engine inherits" — the settings
// layers (the search path), the configured hooks (what runs on each event), and
// the available skills (what the engine can call). All three are folds of the
// same on-disk config the CLI reads; the engine runs them, the surface shows
// them. Never throws (each fold degrades to []).
function listEnvironment(opts) {
  const o = opts || {};
  return {
    settings: discoverSettings(o),
    hooks: discoverHooks(o),
    skills: listSkills(o),
  };
}

module.exports = {
  settingsPathsFor,
  readSettingsSource,
  discoverSettings,
  hooksFromSettings,
  discoverHooks,
  skillsDirFor,
  frontMatterValue,
  readSkillMeta,
  discoverSkills,
  listSkills,
  listEnvironment,
};
