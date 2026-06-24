// diff.js — fold an edit tool-call's input into a render-ready line diff
// (pure data layer, no `vscode`, no `shell`).
//
// Row 8 of the parity checklist: "Render diffs / edits with accept–reject."
// When the assistant edits a file it emits a `tool_use` block whose name is one
// of the edit tools (Edit / Write / MultiEdit / NotebookEdit) and whose input
// carries the change. Claude Code renders that change as a DIFF the human can
// accept or reject. This module owns only the *folding* of such a tool_use into
// the ordered diff lines a viewer paints — it is a FOLD (blueprint §The law):
// it derives the diff from the engine's own tool_use record and stores nothing.
//
// No `vscode`/`shell` dependency, so a plain `node` test can hand it a captured
// tool_use input and assert exactly the diff lines it returns — host-free,
// checkable evidence. The rendering (the +/- gutter, the accept/reject buttons)
// lives in shell.js; the decision round-trip lives in extension.js.
//
// The edit-tool input shapes (the Messages-API tool inputs the engine writes):
//   - Edit:         { file_path, old_string, new_string, replace_all? }
//   - Write:        { file_path, content }            (a whole new/overwritten file)
//   - MultiEdit:    { file_path, edits:[{ old_string, new_string }] }
//   - NotebookEdit: { notebook_path, new_source, edit_mode? }

'use strict';

// The tool names that produce a file diff. Anything else folds to null (it is
// rendered as an ordinary tool-use call, row 7) — absence is information.
const EDIT_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'];

// isEditTool(name) -> true when a tool_use's name produces a file diff.
function isEditTool(name) {
  return EDIT_TOOLS.indexOf(String(name)) !== -1;
}

// splitLines(s) -> the lines of a string, with '' yielding [] (an empty string
// is no lines, not one blank line — so an empty old_string adds nothing to diff
// and a Write of '' is an honest zero-line file).
function splitLines(s) {
  const str = s == null ? '' : String(s);
  if (str === '') return [];
  return str.split('\n');
}

// diffLines(oldStr, newStr) -> ordered [{ tag, text }] where tag is one of
// 'context' | 'del' | 'add'. A small, dependency-free diff: trim the common
// leading + trailing lines as context, mark the differing middle as removed
// (old) then added (new). It is not a minimal LCS — it is honest and
// deterministic: the shown removals reconstruct the old middle and the shown
// additions reconstruct the new middle, so a cold reader can check it by eye.
function diffLines(oldStr, newStr) {
  const a = splitLines(oldStr);
  const b = splitLines(newStr);
  // Common prefix.
  let p = 0;
  while (p < a.length && p < b.length && a[p] === b[p]) p++;
  // Common suffix (not overlapping the prefix already consumed).
  let sa = a.length;
  let sb = b.length;
  while (sa > p && sb > p && a[sa - 1] === b[sb - 1]) {
    sa--;
    sb--;
  }
  const lines = [];
  for (let i = 0; i < p; i++) lines.push({ tag: 'context', text: a[i] });
  for (let i = p; i < sa; i++) lines.push({ tag: 'del', text: a[i] });
  for (let i = p; i < sb; i++) lines.push({ tag: 'add', text: b[i] });
  for (let i = sa; i < a.length; i++) lines.push({ tag: 'context', text: a[i] });
  return lines;
}

// countTags(lines) -> { adds, dels } over a diff-line list.
function countTags(lines) {
  let adds = 0;
  let dels = 0;
  for (const l of lines) {
    if (l.tag === 'add') adds++;
    else if (l.tag === 'del') dels++;
  }
  return { adds, dels };
}

// diffFromToolUse(entry) -> a structured diff for an edit tool_use entry, or
// null when the entry is not an edit tool (so the caller renders it as an
// ordinary tool call, row 7). The entry is a transcript.foldTranscript tool-use
// entry: { kind:'tool-use', name, toolId, input }.
//
// Returns { op, name, filePath, lines:[{tag,text}], adds, dels, toolId } where
// op is 'edit' | 'write' | 'multiedit' | 'notebook'. A 'hunk' tag separates the
// edits of a MultiEdit (a blank separator row; carries no text).
function diffFromToolUse(entry) {
  if (!entry || entry.kind !== 'tool-use') return null;
  const name = entry.name || '';
  if (!isEditTool(name)) return null;
  const input = entry.input && typeof entry.input === 'object' ? entry.input : {};
  const toolId = entry.toolId || '';

  if (name === 'Write') {
    const lines = splitLines(input.content).map((text) => ({ tag: 'add', text }));
    const c = countTags(lines);
    return {
      op: 'write',
      name,
      filePath: input.file_path || '',
      lines,
      adds: c.adds,
      dels: c.dels,
      toolId,
    };
  }

  if (name === 'NotebookEdit') {
    // A notebook cell edit: the new cell source is the addition. A delete
    // edit_mode removes the source instead (shown as removals).
    const isDelete = input.edit_mode === 'delete';
    const lines = splitLines(input.new_source).map((text) => ({
      tag: isDelete ? 'del' : 'add',
      text,
    }));
    const c = countTags(lines);
    return {
      op: 'notebook',
      name,
      filePath: input.notebook_path || '',
      lines,
      adds: c.adds,
      dels: c.dels,
      toolId,
    };
  }

  if (name === 'MultiEdit') {
    const edits = Array.isArray(input.edits) ? input.edits : [];
    const lines = [];
    edits.forEach((ed, i) => {
      if (i > 0) lines.push({ tag: 'hunk', text: '' });
      const sub = diffLines(ed && ed.old_string, ed && ed.new_string);
      for (const l of sub) lines.push(l);
    });
    const c = countTags(lines);
    return {
      op: 'multiedit',
      name,
      filePath: input.file_path || '',
      lines,
      adds: c.adds,
      dels: c.dels,
      toolId,
    };
  }

  // Edit (the default edit tool): a single old→new replacement.
  const lines = diffLines(input.old_string, input.new_string);
  const c = countTags(lines);
  return {
    op: 'edit',
    name,
    filePath: input.file_path || '',
    lines,
    adds: c.adds,
    dels: c.dels,
    toolId,
  };
}

module.exports = {
  EDIT_TOOLS,
  isEditTool,
  splitLines,
  diffLines,
  diffFromToolUse,
};
