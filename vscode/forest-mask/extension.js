'use strict';
/* extension.js — the forest mask: a VS Code FileDecorationProvider that paints
 * each file in the Explorer with its agent-attention tier, read from the
 * file-touch sensor log (.ai-native/log/file-touch.jsonl — the SAME source
 * loop/coverage.py folds, never a second truth).
 *
 * The pure classification lives in tier.js (testable without vscode). This file
 * is the thin shell: it locates the repo root, reads + caches the touch log,
 * maps a uri to a repo-relative path, asks tier.classify, and returns a
 * FileDecoration (a short badge, a themed colour, a full-label tooltip). It
 * watches the log and fires onDidChangeFileDecorations so the mask updates LIVE
 * as agents read and edit files.
 *
 * Fail-soft everywhere: a missing/empty log -> every file `undiscovered`
 * (correct), and nothing throws. No dependency, only the host `vscode` API and
 * node stdlib.
 */

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const { classify } = require('./tier.js');

const TOUCH_LOG_REL = path.join('.ai-native', 'log', 'file-touch.jsonl');

// In-context recency proxy: a file touched within this window reads `in-context`.
// PROXY — true context membership is unobservable; recency is the best signal.
const RECENCY_MS = 30 * 60 * 1000; // 30 minutes

// One badge (<= 2 chars), themed colour, and label per tier. The colours lean
// on VS Code's own theme tokens so they track light/dark. Undiscovered uses the
// muted/disabled foreground so unreached files DIM (the mask bdo asked for).
const TIER_STYLE = {
  undiscovered: {
    badge: '·',
    color: new vscode.ThemeColor('disabledForeground'),
    label: 'undiscovered — no agent has opened this file',
  },
  read: {
    badge: 'r',
    color: new vscode.ThemeColor('charts.blue'),
    label: 'read — an agent has read this file',
  },
  written: {
    badge: '✎',
    color: new vscode.ThemeColor('charts.green'),
    label: 'written — an agent has edited this file',
  },
  'in-context': {
    badge: '●',
    color: new vscode.ThemeColor('charts.yellow'),
    label: 'in context — touched recently (recency proxy for the context window)',
  },
};

/** Walk up from a starting dir until a directory containing `.ai-native` is
 *  found; that directory is the repo root. Returns null if none is found. */
function findRepoRoot(startDir) {
  let dir = startDir;
  // bound the walk to the filesystem root
  for (let i = 0; i < 64 && dir; i++) {
    try {
      if (fs.existsSync(path.join(dir, '.ai-native'))) return dir;
    } catch (_e) { /* fail-soft */ }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

/** Resolve the repo root: prefer a workspace folder that carries .ai-native,
 *  else walk up from the first workspace folder, else null. */
function resolveRepoRoot() {
  const folders = vscode.workspace.workspaceFolders || [];
  for (const f of folders) {
    const root = findRepoRoot(f.uri.fsPath);
    if (root) return root;
  }
  return null;
}

class ForestMaskProvider {
  constructor() {
    this._emitter = new vscode.EventEmitter();
    this.onDidChangeFileDecorations = this._emitter.event;
    this._repoRoot = resolveRepoRoot();
    this._records = [];     // cached parsed touch records
    this._loaded = false;
    this._load();
  }

  get touchLogPath() {
    return this._repoRoot ? path.join(this._repoRoot, TOUCH_LOG_REL) : null;
  }

  /** Read + parse the touch log into the cache. Torn-tail tolerant (a line that
   *  will not parse never happened). Fail-soft: any error -> empty records. */
  _load() {
    this._records = [];
    this._loaded = true;
    const p = this.touchLogPath;
    if (!p) return;
    let text;
    try {
      text = fs.readFileSync(p, 'utf8');
    } catch (_e) {
      return; // missing/unreadable log -> every file undiscovered (correct)
    }
    for (const line of text.split('\n')) {
      const s = line.trim();
      if (!s) continue;
      try {
        const rec = JSON.parse(s);
        if (rec && typeof rec.path === 'string') this._records.push(rec);
      } catch (_e) { /* torn/partial line — it never happened */ }
    }
  }

  /** Re-read the cache and tell VS Code every decoration may have changed. */
  refresh() {
    this._load();
    this._emitter.fire(undefined); // undefined === "all uris may have changed"
  }

  /** Map a uri to the repo-relative, forward-slash path the log speaks, or null
   *  if the uri is not a file under the repo root. */
  _repoRelPath(uri) {
    if (!this._repoRoot || !uri || uri.scheme !== 'file') return null;
    const rel = path.relative(this._repoRoot, uri.fsPath);
    if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) return null;
    return rel.split(path.sep).join('/');
  }

  provideFileDecoration(uri) {
    try {
      const rel = this._repoRelPath(uri);
      if (rel === null) return undefined; // outside the repo — no decoration
      const tier = classify(this._records, rel, Date.now(), RECENCY_MS);
      const style = TIER_STYLE[tier] || TIER_STYLE.undiscovered;
      return {
        badge: style.badge,
        color: style.color,
        tooltip: 'forest mask: ' + style.label,
        // not propagated to the parent folder: a folder's own tier is its own
      };
    } catch (_e) {
      return undefined; // a bug must never break the Explorer
    }
  }
}

function activate(context) {
  const provider = new ForestMaskProvider();
  context.subscriptions.push(
    vscode.window.registerFileDecorationProvider(provider));

  // Live refresh: watch the touch log and re-fold on any change. The
  // FileSystemWatcher tracks create/change/delete so the mask lights up as the
  // sensor appends, and clears correctly if the log is removed/rebuilt.
  if (provider._repoRoot) {
    const pattern = new vscode.RelativePattern(
      provider._repoRoot, '.ai-native/log/file-touch.jsonl');
    const watcher = vscode.workspace.createFileSystemWatcher(pattern);
    const onChange = () => provider.refresh();
    watcher.onDidCreate(onChange);
    watcher.onDidChange(onChange);
    watcher.onDidDelete(onChange);
    context.subscriptions.push(watcher);
  }
}

function deactivate() { /* nothing to tear down beyond context.subscriptions */ }

module.exports = { activate, deactivate };
