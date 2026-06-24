// slash.js — recognize, parse, and discover slash commands (pure data + fs
// layer, no `vscode`).
//
// Row 10 of the parity checklist: "Slash commands." The bridge spike
// (SPIKE-FINDINGS.md) resolved this row to `inherit`: a slash command is
// PASS-THROUGH to the engine — sent as the turn's prompt text down the same
// stream-json channel row 5 drives, the engine interprets `/help`, `/clear`,
// `/compact`, a project's custom `/foo`, etc. (the engine is authoritative;
// the surface does not re-implement what each command does). So this module
// owns only the SURFACE of slash commands:
//   1. recognize that a composed prompt IS a slash command (isSlashCommand),
//   2. parse it into { name, args, raw } (parseSlashCommand),
//   3. DISCOVER the available commands so the surface can offer a palette —
//      the user/project custom commands live on disk exactly where the CLI
//      reads them (`<cwd>/.claude/commands/*.md` and `~/.claude/commands/*.md`,
//      namespaced by subdir), plus a small set of common built-ins.
//
// Discovery is a FOLD of the same on-disk store the CLI itself reads (the
// blueprint §The law: paint what is there, invent nothing), so it is proven
// host-free against a fake commands dir — exactly as sessions.js folds the
// transcript store. The engine remains the authority on what a command does and
// on the full built-in set; an unknown `/foo` is still passed through (the
// surface never blocks a command it does not happen to list).

'use strict';

const fs = require('fs');
const path = require('path');

// A small, honest set of common built-in slash commands to seed the palette.
// This is NOT a claim to be the engine's full command list — the engine is
// authoritative and an unrecognised command is still passed through. These are
// the widely-present built-ins, marked scope 'builtin'; a project/user custom
// command of the same name overrides the entry (see listSlashCommands).
const BUILTIN_COMMANDS = [
  { name: 'help', description: 'List available commands' },
  { name: 'clear', description: 'Clear the conversation history' },
  { name: 'compact', description: 'Summarise the conversation to free context' },
  { name: 'cost', description: 'Show token usage and cost for this session' },
  { name: 'config', description: 'Open the config / settings surface' },
  { name: 'review', description: 'Review a pull request' },
];

// isSlashCommand(text) -> true when the (trimmed) text is a slash command: a
// leading '/' immediately followed by a word character. Conservative by
// construction — a bare '/', a path-ish '//' or '/ ' is NOT a command (so a
// stray slash in prose is never mistaken for one).
function isSlashCommand(text) {
  if (text == null) return false;
  return /^\/[A-Za-z0-9_]/.test(String(text).trim());
}

// parseSlashCommand(text) -> { name, args, raw } for a slash command, else null.
//   name — the command token after '/', allowing ':' namespacing and -/_ (e.g.
//          'help', 'git:commit'); never carries the leading slash.
//   args — the remainder of the line (trimmed), '' when there are none.
//   raw  — the trimmed original text (what is actually sent to the engine —
//          pass-through, unaltered, so the engine sees exactly what was typed).
function parseSlashCommand(text) {
  if (!isSlashCommand(text)) return null;
  const raw = String(text).trim();
  const m = /^\/([A-Za-z0-9_:-]+)\s*([\s\S]*)$/.exec(raw);
  if (!m) return null;
  return { name: m[1], args: m[2].trim(), raw };
}

// commandsDirFor(base) -> the `<base>/.claude/commands` directory the CLI reads
// custom slash commands from. Pure path join (no fs touch).
function commandsDirFor(base) {
  return path.join(String(base || ''), '.claude', 'commands');
}

// fileToName(relPath) -> the command name a custom command file maps to: its
// path under the commands dir, '.md' stripped, separators folded to ':' (so a
// namespaced `git/commit.md` becomes `git:commit`, matching the CLI's scheme).
function fileToName(relPath) {
  return String(relPath)
    .replace(/\.md$/i, '')
    .split(/[\\/]/)
    .filter(Boolean)
    .join(':');
}

// readDescription(file) -> a one-line description for a custom command: the
// front-matter `description:` when present, else the first non-empty body line
// (a leading markdown '#' is stripped). '' when the file cannot be read or is
// empty. Torn/missing tolerant — discovery never throws on a bad file.
function readDescription(file) {
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (_) {
    return '';
  }
  let body = raw;
  const fm = /^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?/.exec(raw);
  if (fm) {
    const desc = /(?:^|\n)description:\s*(.+)/i.exec(fm[1]);
    if (desc) return desc[1].trim();
    body = raw.slice(fm[0].length);
  }
  const first = body
    .split('\n')
    .map((l) => l.trim())
    .find((l) => l);
  return first ? first.replace(/^#+\s*/, '').trim() : '';
}

// discoverCommands({ dir, scope }) -> [{ name, scope, description }] for every
// `*.md` file under `dir` (recursively, for namespaced subdirs), newest concern
// aside. A missing/unreadable dir yields [] (not an error) — the store simply
// has none yet. Deterministic order: sorted by name.
function discoverCommands(opts) {
  const o = opts || {};
  const root = o.dir;
  const scope = o.scope || 'project';
  const out = [];
  if (!root) return out;
  const stack = [''];
  while (stack.length) {
    const rel = stack.pop();
    const abs = rel ? path.join(root, rel) : root;
    let entries;
    try {
      entries = fs.readdirSync(abs, { withFileTypes: true });
    } catch (_) {
      continue; // a missing/unreadable dir contributes nothing
    }
    for (const ent of entries) {
      const childRel = rel ? path.join(rel, ent.name) : ent.name;
      if (ent.isDirectory()) {
        stack.push(childRel);
      } else if (ent.isFile() && /\.md$/i.test(ent.name)) {
        out.push({
          name: fileToName(childRel),
          scope,
          description: readDescription(path.join(root, childRel)),
        });
      }
    }
  }
  out.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  return out;
}

// listSlashCommands({ projectDir, userDir, builtins }) -> the merged, deduped,
// sorted palette of available slash commands: [{ name, scope, description }].
// Precedence when a name appears more than once: a PROJECT custom command wins
// over a USER one, which wins over a BUILTIN (a project can override a built-in
// name — the same shadowing the CLI honours). The engine is still authoritative
// on what each command does and on the full built-in set; this is the offered
// surface, not a gate.
function listSlashCommands(opts) {
  const o = opts || {};
  const builtins = (o.builtins || BUILTIN_COMMANDS).map((b) => ({
    name: b.name,
    scope: 'builtin',
    description: b.description || '',
  }));
  const user = o.userDir
    ? discoverCommands({ dir: commandsDirFor(o.userDir), scope: 'user' })
    : [];
  const project = o.projectDir
    ? discoverCommands({ dir: commandsDirFor(o.projectDir), scope: 'project' })
    : [];
  // Lowest precedence first; later writes shadow earlier ones by name.
  const byName = new Map();
  for (const c of builtins) byName.set(c.name, c);
  for (const c of user) byName.set(c.name, c);
  for (const c of project) byName.set(c.name, c);
  const merged = Array.from(byName.values());
  merged.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  return merged;
}

module.exports = {
  BUILTIN_COMMANDS,
  isSlashCommand,
  parseSlashCommand,
  commandsDirFor,
  fileToName,
  readDescription,
  discoverCommands,
  listSlashCommands,
};
