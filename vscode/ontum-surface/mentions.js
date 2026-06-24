// mentions.js — recognize, discover, and attach @-mentions / IDE selection
// context (pure data + fs layer, no `vscode`).
//
// Row 12 of the parity checklist: "@-mentions / IDE selection context." Normal
// Claude Code lets you (a) type `@path/to/file` to pull a workspace file into the
// turn's context, and (b) carry the active editor selection (the file + line
// range you have highlighted) into the turn automatically. Both are CONTEXT the
// surface attaches to the prompt that rides the SAME stream-json channel row 5
// drives — the engine reads `@file` and the selection note as context; the
// surface does not re-implement file reading. So this module owns only the
// SURFACE of mentions + selection:
//   1. RECOGNISE that a composed prompt carries an @-mention (isMention /
//      parseMentions) and, while typing, the partial token at the caret
//      (mentionQuery) so the surface can offer a completion palette;
//   2. DISCOVER the workspace files to offer — a bounded fold of the same tree
//      the CLI/editor see (discoverFiles / listMentionTargets), skipping the
//      noise dirs (.git, node_modules, …) and capped so a huge repo never hangs
//      the palette;
//   3. ATTACH the IDE selection as a marked, deterministic context preamble
//      (selectionContext / withSelectionContext) the engine reads before the
//      prompt — proven host-free against a selection record (a live selection
//      comes from the VS Code host's window.activeTextEditor).
//
// Discovery is a FOLD of the on-disk tree (blueprint §The law: paint what is
// there, invent nothing), so it is proven host-free against a fake workspace —
// exactly as slash.js folds the command store and sessions.js the transcript
// store. The engine remains the authority on what an @-mention pulls in; the
// surface recognises + discovers + offers + attaches, and an unlisted path is
// still sent (the surface never blocks a mention it does not happen to list).

'use strict';

const fs = require('fs');
const path = require('path');

// The directory names a workspace fold skips: VCS metadata, dependency trees,
// and build output — the same noise the editor's quick-open hides. Not a
// security boundary (a path under one is still sendable if typed by hand); just
// keeps the offered palette signal-rich and the walk bounded.
const IGNORE_DIRS = new Set([
  '.git',
  '.hg',
  '.svn',
  'node_modules',
  'dist',
  'out',
  'build',
  'coverage',
  '.cache',
  '.next',
  '.nuxt',
  '__pycache__',
]);

// The character class a mention path is made of: letters, digits, and the path
// punctuation `_ . / \ -`. Conservative by construction — whitespace ends the
// token, so a stray '@' in prose or an email's '@' (which is NOT preceded by a
// start/space) is never mistaken for a mention.
const MENTION_CHARS = 'A-Za-z0-9_./\\\\-';
const MENTION_RE = new RegExp(
  '(^|\\s)@([' + MENTION_CHARS + ']+)',
  'g'
);
// The trailing partial being typed at the caret: an '@' token at end-of-string
// (the char class may be empty, so a bare trailing '@' opens the full palette).
const MENTION_TAIL_RE = new RegExp(
  '(^|\\s)@([' + MENTION_CHARS + ']*)$'
);

// trimTrailingPunct(s) -> a captured path with a trailing run of sentence
// punctuation (`. , : ; ! ?`) stripped, so "see @foo.js." mentions `foo.js`,
// not `foo.js.`. A path that legitimately ends in a dot is vanishingly rare;
// the readable-prose case wins.
function trimTrailingPunct(s) {
  return String(s).replace(/[.,:;!?]+$/, '');
}

// isMention(text) -> true when the text carries at least one @-mention token.
function isMention(text) {
  if (text == null) return false;
  MENTION_RE.lastIndex = 0;
  return MENTION_RE.test(String(text));
}

// parseMentions(text) -> [{ raw, path, index }] for every @-mention in the text,
// in order. `raw` is the '@path' as typed; `path` is the bare path (separators
// kept as typed); `index` is the offset of the '@'. '' / non-string -> []. A
// torn trailing token with no path (a bare '@') is not a mention.
function parseMentions(text) {
  if (text == null) return [];
  const s = String(text);
  const out = [];
  MENTION_RE.lastIndex = 0;
  let m;
  while ((m = MENTION_RE.exec(s))) {
    const lead = m[1] || '';
    const at = m.index + lead.length; // offset of the '@'
    const raw = trimTrailingPunct('@' + m[2]);
    const p = trimTrailingPunct(m[2]);
    if (p) out.push({ raw, path: p, index: at });
  }
  return out;
}

// mentionQuery(text) -> the partial mention path being typed at the caret (the
// end of the text), or null when the text is not currently inside a mention
// token. '' when the text ends with a bare '@' (open the whole palette). The
// surface uses this to show + filter the completion palette as the human types
// (mirrors the slash palette's filter-as-you-type).
function mentionQuery(text) {
  if (text == null) return null;
  const m = MENTION_TAIL_RE.exec(String(text));
  return m ? m[2] : null;
}

// fileToMention(relPath) -> the mention path a workspace file maps to: its path
// under the workspace root with separators folded to '/' (so a Windows
// `src\app.js` and a posix `src/app.js` both mention `src/app.js`).
function fileToMention(relPath) {
  return String(relPath)
    .split(/[\\/]/)
    .filter(Boolean)
    .join('/');
}

// discoverFiles({ dir, limit, ignore }) -> [{ path, name }] for the workspace
// files under `dir`, a BOUNDED breadth-first fold (shallow files first) that
// skips the noise dirs (IGNORE_DIRS + any dotdir) and dotfiles, capped at
// `limit` (default 500) so a huge repo never hangs the palette. A missing /
// unreadable dir yields [] (not an error). Deterministic order: sorted by path.
function discoverFiles(opts) {
  const o = opts || {};
  const root = o.dir;
  const limit =
    typeof o.limit === 'number' && o.limit > 0 ? Math.floor(o.limit) : 500;
  const ignore = o.ignore instanceof Set ? o.ignore : IGNORE_DIRS;
  const out = [];
  if (!root) return out;
  const queue = ['']; // breadth-first: shallow files surface before deep ones
  while (queue.length && out.length < limit) {
    const rel = queue.shift();
    const abs = rel ? path.join(root, rel) : root;
    let entries;
    try {
      entries = fs.readdirSync(abs, { withFileTypes: true });
    } catch (_) {
      continue; // a missing/unreadable dir contributes nothing
    }
    entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
    for (const ent of entries) {
      const childRel = rel ? path.join(rel, ent.name) : ent.name;
      if (ent.isDirectory()) {
        if (ent.name.startsWith('.') || ignore.has(ent.name)) continue;
        queue.push(childRel);
      } else if (ent.isFile()) {
        if (ent.name.startsWith('.')) continue; // hidden file — keep the palette clean
        out.push({ path: fileToMention(childRel), name: ent.name });
        if (out.length >= limit) break;
      }
    }
  }
  out.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  return out;
}

// listMentionTargets({ projectDir, limit }) -> the mention completion palette
// for a workspace: the bounded file fold of `projectDir`. A thin wrapper over
// discoverFiles, kept parallel to slash.listSlashCommands so the extension wires
// both the same way.
function listMentionTargets(opts) {
  const o = opts || {};
  if (!o.projectDir) return [];
  return discoverFiles({ dir: o.projectDir, limit: o.limit });
}

// selectionContext(sel) -> a marked, deterministic context preamble for an IDE
// selection, or '' when there is nothing to attach. `sel` is the host's editor
// selection record: { file, startLine, endLine, text }. The preamble is a
// single honest header line (the file + 1-based line range) followed by the
// selected text, so the engine reads exactly what the human highlighted:
//   [selection src/app.js:10-20]
//   <the selected text>
// A missing file AND missing text -> '' (nothing to attach). A zero-length or
// single-line range degrades to `:N` (no fake range).
function selectionContext(sel) {
  if (!sel || typeof sel !== 'object') return '';
  const file = sel.file != null ? String(sel.file) : '';
  const text = sel.text != null ? String(sel.text) : '';
  if (!file && !text) return '';
  const s = Number(sel.startLine);
  const e = Number(sel.endLine);
  let range = '';
  if (Number.isFinite(s)) {
    range = Number.isFinite(e) && e !== s ? ':' + s + '-' + e : ':' + s;
  }
  const head = '[selection ' + file + range + ']';
  return text ? head + '\n' + text : head;
}

// withSelectionContext(prompt, sel) -> the prompt with the IDE selection
// attached as a context preamble (selectionContext) when a selection exists,
// else the prompt UNCHANGED. So a turn driven with no selection sends exactly
// what was typed (the row-5/10 pass-through is preserved), and a turn driven
// with a selection carries it as marked context the engine reads first.
function withSelectionContext(prompt, sel) {
  const p = prompt == null ? '' : String(prompt);
  const ctx = selectionContext(sel);
  if (!ctx) return p;
  return ctx + '\n\n' + p;
}

module.exports = {
  IGNORE_DIRS,
  isMention,
  parseMentions,
  mentionQuery,
  fileToMention,
  discoverFiles,
  listMentionTargets,
  selectionContext,
  withSelectionContext,
};
