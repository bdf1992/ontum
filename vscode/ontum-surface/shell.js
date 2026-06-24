// shell.js — the branded ontum surface shell (pure, no `vscode` dependency).
//
// Row 1 of the parity checklist: "Open a branded ontum window (webview),
// standalone of the official panel." This module owns only the *markup* of
// that window — a pure function from options to an HTML string — so it can be
// rendered by the extension at runtime AND asserted by a plain `node` test
// without a VS Code host (the `vscode/` law: plain-JS, no toolchain).
//
// The shell is a FOLD, never a second source (blueprint §The law): it paints
// chrome and named regions for the session list, transcript, and composer, but
// it computes no conversation state — those regions are filled by later
// increments (rows 2–4) that read the transcript store. Here they are honest,
// labelled placeholders so a cold reader is not misled into thinking they work
// yet.

'use strict';

const { diffFromToolUse } = require('./diff');
const {
  PERMISSION_MODES,
  normalizePermissionMode,
  normalizeResumeTarget,
} = require('./engine');
const { planFromToolUse, isPlanMode } = require('./plan');

// A small, dependency-free nonce for the webview Content-Security-Policy.
// (Webview scripts must carry a nonce the CSP whitelists; without one the
// host refuses to run them.)
function makeNonce() {
  const alphabet =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let out = '';
  for (let i = 0; i < 32; i++) {
    out += alphabet[Math.floor(Math.random() * alphabet.length)];
  }
  return out;
}

// Minimal HTML-escape for any caller-supplied text dropped into the markup.
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// renderSessionList(sessions) -> the inner HTML of the Sessions aside (row 2).
//
// Each session is rendered as a selectable button carrying `data-session-id`;
// clicking it posts `{ type: 'ontum:select-session', id }` to the host (the
// script at the foot of the shell). The data comes from sessions.js
// (listSessions) — this function only paints it, so it stays a pure fold and is
// asserted by a host-free test. An empty store paints an honest empty note, not
// a fake row.
function renderSessionList(sessions) {
  const list = Array.isArray(sessions) ? sessions : [];
  if (list.length === 0) {
    return (
      '<p class="ontum-empty">No local sessions for this folder yet. ' +
      'Start a turn and it appears here.</p>'
    );
  }
  const items = list
    .map((s) => {
      const id = escapeHtml(s && s.id ? s.id : '');
      const title = escapeHtml(s && s.title ? s.title : '(untitled)');
      const count =
        s && typeof s.messageCount === 'number' ? s.messageCount : 0;
      const branch = s && s.gitBranch ? escapeHtml(s.gitBranch) : '';
      const meta =
        `${count} msg` + (branch ? ` · ${branch}` : '');
      return (
        `<button class="ontum-session" type="button" ` +
        `data-session-id="${id}" title="${id}">` +
        `<span class="ontum-session-title">${title}</span>` +
        `<span class="ontum-session-meta">${meta}</span>` +
        `</button>`
      );
    })
    .join('\n      ');
  return (
    `<ul class="ontum-session-list" data-count="${list.length}">\n      ` +
    items +
    `\n    </ul>`
  );
}

// renderTranscript(entries) -> the inner HTML of the Transcript section (row 3).
//
// Each entry comes from transcript.foldTranscript (a pure fold of the engine's
// own records). This function only paints them — escaped, in order — so it
// stays a pure fold asserted by a host-free test. Kinds map to labelled blocks:
//   user-text / assistant-text -> a role-tagged prose bubble;
//   assistant-thinking         -> a dimmed "thinking" block;
//   tool-use                   -> the tool name + its JSON input (a <pre>);
//   tool-result                -> the result text (a <pre>), error-flagged.
// An empty/absent list paints an honest empty note, never a fake turn.
//
// renderTranscriptRow(e) -> the HTML of ONE entry block (no wrapper). Shared by
// the full render below AND by the live-tail append path (row 4), which renders
// only the newly-arrived entries and inserts them into the existing list — so
// both paths paint a turn identically and stay one source of truth.
// renderDiffLines(lines) -> the joined HTML of a diff's line list (row 8). Each
// line is a `data-diff="add|del|context|hunk"` row with a +/-/space gutter and
// its escaped text; a 'hunk' row is a blank separator between a MultiEdit's
// edits. Escaped here, so the fragment is no less trusted than the document.
function renderDiffLines(lines) {
  const list = Array.isArray(lines) ? lines : [];
  return list
    .map((l) => {
      const tag = l && l.tag ? l.tag : 'context';
      if (tag === 'hunk') {
        return '<div class="ontum-diff-line" data-diff="hunk"></div>';
      }
      const gutter = tag === 'add' ? '+' : tag === 'del' ? '\u2212' : ' ';
      const text = escapeHtml(l && l.text ? l.text : '');
      return (
        `<div class="ontum-diff-line" data-diff="${escapeHtml(tag)}">` +
        `<span class="ontum-diff-gutter">${gutter}</span>` +
        `<span class="ontum-diff-text">${text}</span>` +
        '</div>'
      );
    })
    .join('');
}

// renderDiffBlock(d) -> the HTML of an edit tool-call rendered as a DIFF with
// accept/reject controls (row 8). `d` comes from diff.diffFromToolUse (a pure
// fold of the engine's own tool_use record). The block is still a tool-use
// (data-kind="tool-use") so row 7's structure/CSS holds, but is flagged
// data-diff-tool="true" and carries: a header (file path + +adds/-dels stat),
// the diff lines, and two decision buttons (data-decision accept|reject)
// carrying the tool id. The buttons post `ontum:diff-decision` to the host (the
// delegated handler in the shell script). HONEST SCOPE: this renders the diff
// and the accept/reject AFFORDANCE and proves the decision round-trip; actually
// applying or reverting the edit on disk is a real side effect left to the host
// permission flow (row 9) / a human — the surface does not fake it.
function renderDiffBlock(d) {
  const name = escapeHtml(d.name || 'Edit');
  const path = escapeHtml(d.filePath || '');
  const toolId = escapeHtml(d.toolId || '');
  const adds = typeof d.adds === 'number' ? d.adds : 0;
  const dels = typeof d.dels === 'number' ? d.dels : 0;
  return (
    '<div class="ontum-msg" data-kind="tool-use" data-diff-tool="true" ' +
    `data-tool-name="${name}" data-tool-id="${toolId}">` +
    `<span class="ontum-role">edit &#9656; ${name}</span>` +
    `<div class="ontum-diff" data-file="${path}" data-adds="${adds}" data-dels="${dels}">` +
    '<div class="ontum-diff-head">' +
    `<span class="ontum-diff-path">${path || '(no path)'}</span>` +
    `<span class="ontum-diff-stat">+${adds} &#8722;${dels}</span>` +
    '</div>' +
    `<div class="ontum-diff-lines">${renderDiffLines(d.lines)}</div>` +
    '<div class="ontum-diff-actions" data-decision-state="pending">' +
    `<button class="ontum-diff-decision" type="button" data-decision="accept" data-tool-id="${toolId}">Accept</button>` +
    `<button class="ontum-diff-decision" type="button" data-decision="reject" data-tool-id="${toolId}">Reject</button>` +
    '</div>' +
    '</div>' +
    '</div>'
  );
}

// renderPlanBlock(p) -> the HTML of an ExitPlanMode tool-call rendered as a
// PLAN CARD with approve/keep-planning controls (row 11). `p` comes from
// plan.planFromToolUse (a pure fold of the engine's own ExitPlanMode tool_use
// record). The block is still a tool-use (data-kind="tool-use", so row 7's
// structure/CSS holds) but is flagged data-plan-tool="true" and carries: a
// header, the proposed plan text (escaped), and two decision buttons
// (data-plan-decision approve|keep) carrying the tool id. The buttons post
// `ontum:plan-decision` to the host (the delegated handler in the shell
// script), which records the decision and — on approve — EXITS plan mode so the
// work can proceed. HONEST SCOPE: this renders the plan and the approve/keep
// AFFORDANCE and proves the decision round-trip + the mode transition; actually
// running the approved work is the engine's job under the exited mode.
function renderPlanBlock(p) {
  const name = escapeHtml(p.name || 'ExitPlanMode');
  const toolId = escapeHtml(p.toolId || '');
  const plan = escapeHtml(p.plan || '');
  return (
    '<div class="ontum-msg" data-kind="tool-use" data-plan-tool="true" ' +
    `data-tool-name="${name}" data-tool-id="${toolId}">` +
    '<span class="ontum-role">plan &#9656; proposed</span>' +
    '<div class="ontum-plan">' +
    `<pre class="ontum-plan-text">${plan || '(no plan text)'}</pre>` +
    '<div class="ontum-plan-actions" data-plan-state="pending">' +
    `<button class="ontum-plan-decision" type="button" data-plan-decision="approve" data-tool-id="${toolId}">Approve &amp; proceed</button>` +
    `<button class="ontum-plan-decision" type="button" data-plan-decision="keep" data-tool-id="${toolId}">Keep planning</button>` +
    '</div>' +
    '</div>' +
    '</div>'
  );
}

function renderTranscriptRow(e) {
  const kind = e && e.kind ? e.kind : '';
  if (kind === 'tool-use') {
    // Row 11 — the ExitPlanMode tool renders as a plan card with approve/keep,
    // not a raw JSON dump (checked before the diff/JSON paths below).
    const plan = planFromToolUse(e);
    if (plan) return renderPlanBlock(plan);
    // Row 8 — an edit tool (Edit/Write/MultiEdit/NotebookEdit) renders as a
    // diff with accept/reject instead of a raw JSON input dump.
    const diff = diffFromToolUse(e);
    if (diff) return renderDiffBlock(diff);
    const name = escapeHtml(e.name || 'tool');
    const raw =
      typeof e.input === 'string'
        ? e.input
        : JSON.stringify(e.input === undefined ? null : e.input, null, 2);
    const input = escapeHtml(raw);
    return (
      '<div class="ontum-msg" data-kind="tool-use">' +
      `<span class="ontum-role">tool &#9656; ${name}</span>` +
      `<pre class="ontum-tool-input">${input}</pre>` +
      '</div>'
    );
  }
  if (kind === 'tool-result') {
    const err = e.isError ? ' data-error="true"' : '';
    const label = e.isError ? 'result (error)' : 'result';
    const text = escapeHtml(e.text || '');
    return (
      `<div class="ontum-msg" data-kind="tool-result"${err}>` +
      `<span class="ontum-role">${label}</span>` +
      `<pre class="ontum-tool-result">${text}</pre>` +
      '</div>'
    );
  }
  const roleLabel =
    kind === 'assistant-thinking' ? 'thinking' : e && e.role ? e.role : '';
  const text = escapeHtml(e && e.text ? e.text : '');
  return (
    `<div class="ontum-msg" data-kind="${escapeHtml(kind)}">` +
    `<span class="ontum-role">${escapeHtml(roleLabel)}</span>` +
    `<div class="ontum-text">${text}</div>` +
    '</div>'
  );
}

// renderTranscriptRows(entries) -> the joined block HTML for a list of entries,
// WITHOUT the `.ontum-transcript-list` wrapper. The live-tail append message
// (row 4) carries exactly this fragment so the webview can `insertAdjacentHTML`
// it onto the end of the already-rendered list. Each block is escaped here, so
// the fragment is no less trusted than the initial document.
function renderTranscriptRows(entries) {
  const list = Array.isArray(entries) ? entries : [];
  return list.map(renderTranscriptRow).join('\n      ');
}

function renderTranscript(entries) {
  const list = Array.isArray(entries) ? entries : [];
  if (list.length === 0) {
    return (
      '<p class="ontum-empty">No transcript yet. Pick a session on the left ' +
      'to read it here.</p>'
    );
  }
  return (
    `<div class="ontum-transcript-list" data-count="${list.length}">\n      ` +
    renderTranscriptRows(list) +
    `\n    </div>`
  );
}

// renderPermissionControl(mode) -> the inner HTML of the composer's permission
// surface (row 9): a labelled <select> offering the four permission modes the
// engine accepts (default / acceptEdits / plan / bypassPermissions — the exact
// list `claude --help` advertises, sourced from engine.PERMISSION_MODES so the
// surface and the argv never drift). The current mode is normalized
// (conservative: an unknown value shows 'default', it never escalates) and
// marked `selected`. Changing it posts `{ type:'ontum:set-permission-mode',
// mode }` to the host, which threads it into the NEXT turn's engineArgs — so a
// turn actually runs under the human's chosen policy. A short human label per
// mode tells a cold reader what each one does (no fake "Allow once" button that
// the --print channel cannot honour).
const PERMISSION_MODE_LABELS = {
  default: 'default — ask before risky tools',
  acceptEdits: 'acceptEdits — auto-accept file edits',
  plan: 'plan — read-only, propose a plan',
  bypassPermissions: 'bypassPermissions — run without prompts',
};
function renderPermissionControl(mode) {
  const current = normalizePermissionMode(mode);
  const options = PERMISSION_MODES.map((m) => {
    const sel = m === current ? ' selected' : '';
    const label = escapeHtml(PERMISSION_MODE_LABELS[m] || m);
    return `<option value="${escapeHtml(m)}"${sel}>${label}</option>`;
  }).join('');
  return (
    '<div class="ontum-permission" data-region="permission">' +
    '<label class="ontum-permission-label" for="ontum-permission-mode">Permission</label>' +
    `<select class="ontum-permission-mode" id="ontum-permission-mode" ` +
    `data-mode="${escapeHtml(current)}" aria-label="Permission mode">` +
    options +
    '</select>' +
    '</div>'
  );
}

// renderResumeControl(target, selectedId) -> the inner HTML of the composer's
// session-continuity surface (row 16). Normal Claude Code can start a fresh
// session, CONTINUE the most recent conversation, or RESUME a specific one;
// --fork-session branches a new id off either. The control offers those three
// modes as buttons (the in-force one flagged aria-pressed), reflects the
// in-force mode on a `data-resume-mode` mirror a cold reader / test can read,
// and posts `{ type:'ontum:set-resume', mode, id }` to the host on click. The
// "Resume selected" button carries the currently-selected session's id
// (data-session-id from row 2) and is disabled when nothing is selected (there
// is nothing to resume). Conservative by construction: the engine's
// normalizeResumeTarget defaults an unknown mode / an id-less resume to 'new'.
const RESUME_MODE_LABELS = {
  new: 'New session',
  continue: 'Continue recent',
  resume: 'Resume selected',
};
function renderResumeControl(target, selectedId) {
  const t = normalizeResumeTarget(
    target && typeof target === 'object' ? target : { mode: target }
  );
  const selId = typeof selectedId === 'string' && selectedId ? selectedId : '';
  // The in-force resume target: its session id is the one being resumed (resume
  // mode) so a cold reader sees exactly which conversation the next turn joins.
  const mirrorId = t.mode === 'resume' && t.sessionId ? t.sessionId : selId;
  const btn = (mode) => {
    const pressed = mode === t.mode ? ' aria-pressed="true"' : '';
    // "Resume selected" needs a selected session to point at; without one it is
    // disabled (nothing to resume) and carries no id.
    const disabled = mode === 'resume' && !selId ? ' disabled' : '';
    const idAttr =
      mode === 'resume' && selId ? ` data-session-id="${escapeHtml(selId)}"` : '';
    const label = escapeHtml(RESUME_MODE_LABELS[mode] || mode);
    return (
      `<button class="ontum-resume-btn" type="button" ` +
      `data-resume="${escapeHtml(mode)}"${idAttr}${pressed}${disabled}>` +
      `${label}</button>`
    );
  };
  return (
    '<div class="ontum-resume" data-region="resume" ' +
    `data-resume-mode="${escapeHtml(t.mode)}" ` +
    `data-resume-session="${escapeHtml(mirrorId || '')}">` +
    '<span class="ontum-resume-label">Session</span>' +
    btn('new') +
    btn('continue') +
    btn('resume') +
    '</div>'
  );
}

// renderSlashMenu(commands) -> the inner HTML of the composer's slash-command
// palette (row 10). Each command from slash.listSlashCommands (a pure fold of
// the on-disk command store + the built-ins) is a selectable button carrying
// `data-command="<name>"`; clicking it fills the composer with `/<name> ` so
// the human can finish + send it down the SAME engine channel row 5 drives
// (a slash command is pass-through to the engine — the spike's `inherit`). The
// menu is hidden until the composer's text starts with '/', and the shell
// script filters it by the partial command being typed. An empty store still
// renders the built-ins; a truly empty list paints an honest note.
function renderSlashMenu(commands) {
  const list = Array.isArray(commands) ? commands : [];
  if (list.length === 0) {
    return '<p class="ontum-empty">No slash commands found.</p>';
  }
  const items = list
    .map((c) => {
      const name = escapeHtml(c && c.name ? c.name : '');
      const scope = escapeHtml(c && c.scope ? c.scope : 'builtin');
      const desc = escapeHtml(c && c.description ? c.description : '');
      return (
        `<li><button class="ontum-slash-item" type="button" ` +
        `data-command="${name}" data-scope="${scope}">` +
        `<span class="ontum-slash-name">/${name}</span>` +
        `<span class="ontum-slash-scope">${scope}</span>` +
        `<span class="ontum-slash-desc">${desc}</span>` +
        `</button></li>`
      );
    })
    .join('\n        ');
  return (
    `<ul class="ontum-slash-list" data-count="${list.length}">\n        ` +
    items +
    `\n      </ul>`
  );
}

// renderMentionMenu(targets) -> the inner HTML of the composer's @-mention
// palette (row 12). Each target from mentions.listMentionTargets (a bounded
// pure fold of the workspace file tree) is a selectable button carrying
// `data-mention="<path>"`; clicking it replaces the @-token being typed with
// `@<path> ` so the human can finish + send it down the SAME engine channel
// row 5 drives (an @-mention is context the engine reads — pass-through). The
// menu is hidden until the composer's caret is inside an '@' token, and the
// shell script filters it by the partial path being typed. An empty/absent
// workspace fold paints an honest note (no fake row).
function renderMentionMenu(targets) {
  const list = Array.isArray(targets) ? targets : [];
  if (list.length === 0) {
    return '<p class="ontum-empty">No workspace files to mention yet.</p>';
  }
  const items = list
    .map((t) => {
      const p = escapeHtml(t && t.path ? t.path : '');
      const name = escapeHtml(t && t.name ? t.name : '');
      return (
        `<li><button class="ontum-mention-item" type="button" ` +
        `data-mention="${p}">` +
        `<span class="ontum-mention-path">@${p}</span>` +
        `<span class="ontum-mention-name">${name}</span>` +
        `</button></li>`
      );
    })
    .join('\n        ');
  return (
    `<ul class="ontum-mention-list" data-count="${list.length}">\n        ` +
    items +
    `\n      </ul>`
  );
}

// renderAttachTray(attachments) -> the inner HTML of the composer's attachment
// tray (row 15). Each attachment from attach.displayAttachment (a data-free
// view — name/kind/bytes/error, never the base64 payload) is a chip carrying
// `data-attachment="<name>"` + `data-kind` + a Remove button (`data-attach-name`
// for the delegated remove handler). An errored attachment (missing/too large)
// shows its honest error, not a fake success. The tray is hidden until at least
// one attachment is staged; the attachments ride the NEXT turn as content blocks
// ahead of the typed text (engine.encodeUserMessage folds them in). An empty
// list paints nothing (the container + wiring still ship). All escaped.
function renderAttachTray(attachments) {
  const list = Array.isArray(attachments) ? attachments : [];
  if (list.length === 0) return '';
  const items = list
    .map((a) => {
      const name = escapeHtml(a && a.name ? a.name : 'attachment');
      const kind = escapeHtml(a && a.kind ? a.kind : 'text');
      const bytes = a && typeof a.bytes === 'number' ? a.bytes : 0;
      const err = a && a.error ? escapeHtml(a.error) : '';
      const meta = err ? 'error: ' + err : kind + ' · ' + formatBytes(bytes);
      return (
        `<li class="ontum-attach-chip" data-attachment="${name}" ` +
        `data-kind="${kind}"${err ? ' data-error="true"' : ''}>` +
        `<span class="ontum-attach-name">${name}</span>` +
        `<span class="ontum-attach-meta">${escapeHtml(meta)}</span>` +
        `<button class="ontum-attach-remove" type="button" ` +
        `data-attach-name="${name}" aria-label="Remove ${name}">&times;</button>` +
        `</li>`
      );
    })
    .join('\n        ');
  return (
    `<ul class="ontum-attach-list" data-count="${list.length}">\n        ` +
    items +
    `\n      </ul>`
  );
}

// formatBytes(n) -> a short human size for an attachment chip (B / KB / MB).
function formatBytes(n) {
  const b = typeof n === 'number' && n >= 0 ? n : 0;
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / (1024 * 1024)).toFixed(1) + ' MB';
}

// renderMcpPanel(servers) -> the inner HTML of the Sessions aside's MCP region
// (row 13). Each server from mcp.listMcpServers (a fold of the on-disk MCP
// config the CLI reads, annotated with the LIVE engine tools list) is a
// labelled block carrying `data-mcp-server="<name>"`, its scope + transport, an
// `data-available` flag (true once the live env exposes its tools so the engine
// can invoke them), and its tools as `data-mcp-tool="mcp__server__tool"` items
// (the exact identifier the engine names + the row-9 allow-list authorizes).
// All escaped — a fold, never a second source. An empty/absent config paints an
// honest note (no fake server). The engine remains authoritative on what each
// MCP tool does; this is the available-tools surface, not an MCP client.
function renderMcpPanel(servers) {
  const list = Array.isArray(servers) ? servers : [];
  if (list.length === 0) {
    return '<p class="ontum-empty">No MCP servers configured for this folder.</p>';
  }
  const items = list
    .map((s) => {
      const name = escapeHtml(s && s.name ? s.name : '');
      const scope = escapeHtml(s && s.scope ? s.scope : 'project');
      const transport = escapeHtml(s && s.transport ? s.transport : 'unknown');
      const tools = Array.isArray(s && s.tools) ? s.tools : [];
      const available = s && s.available ? 'true' : 'false';
      const count = tools.length;
      const meta = available === 'true'
        ? `${transport} · ${count} tool${count === 1 ? '' : 's'}`
        : `${transport} · not loaded`;
      const toolsHtml = count
        ? tools
            .map((t) => {
              const tn = escapeHtml(t);
              const id = escapeHtml('mcp__' + (s && s.name ? s.name : '') + '__' + t);
              return (
                `<li class="ontum-mcp-tool" data-mcp-tool="${id}">${tn}</li>`
              );
            })
            .join('')
        : '<li class="ontum-mcp-tool ontum-mcp-none">tools load when the engine connects</li>';
      return (
        `<li class="ontum-mcp-server" data-mcp-server="${name}" ` +
        `data-scope="${scope}" data-available="${available}">` +
        `<span class="ontum-mcp-name">${name}</span>` +
        `<span class="ontum-mcp-meta">${escapeHtml(meta)}</span>` +
        `<ul class="ontum-mcp-tools">${toolsHtml}</ul>` +
        `</li>`
      );
    })
    .join('\n      ');
  return (
    `<ul class="ontum-mcp-list" data-count="${list.length}">\n      ` +
    items +
    `\n    </ul>`
  );
}

// renderEnvPanel(env) -> the inner HTML of the Sessions aside's Environment
// region (row 14). `env` comes from environment.listEnvironment (a fold of the
// same on-disk config the CLI reads): the settings LAYERS, the configured
// HOOKS, and the available SKILLS the engine inherits. Three labelled groups,
// all escaped (a fold, never a second source):
//   · settings — each layer as `data-env-settings="<scope>"` with a
//     `data-present` flag + its top-level keys (the search path the CLI merges);
//   · hooks    — each as `data-env-hook="<event>"` carrying its matcher + scope
//     (what the engine runs on PreToolUse / Stop / …);
//   · skills   — each as `data-env-skill="<name>"` with its description + scope
//     (what the engine can call).
// An absent/empty environment paints an honest note per group (no fake row).
// The engine remains authoritative on what a hook DOES and whether a skill
// loads; this is the inherited-environment surface, not a re-implementation.
function renderEnvPanel(env) {
  const e = env && typeof env === 'object' ? env : {};
  const settings = Array.isArray(e.settings) ? e.settings : [];
  const hooks = Array.isArray(e.hooks) ? e.hooks : [];
  const skills = Array.isArray(e.skills) ? e.skills : [];

  const settingsHtml = settings.length
    ? settings
        .map((s) => {
          const scope = escapeHtml(s && s.scope ? s.scope : 'project');
          const present = s && s.present ? 'true' : 'false';
          const keys = Array.isArray(s && s.keys) ? s.keys : [];
          const meta = present === 'true'
            ? (keys.length ? keys.map(escapeHtml).join(', ') : '(no keys)')
            : 'not present';
          return (
            `<li class="ontum-env-settings" data-env-settings="${scope}" ` +
            `data-present="${present}">` +
            `<span class="ontum-env-scope">${scope}</span>` +
            `<span class="ontum-env-meta">${escapeHtml(meta)}</span>` +
            `</li>`
          );
        })
        .join('')
    : '<li class="ontum-empty">No settings layers.</li>';

  const hooksHtml = hooks.length
    ? hooks
        .map((h) => {
          const event = escapeHtml(h && h.event ? h.event : '');
          const matcher = escapeHtml(h && h.matcher ? h.matcher : '*');
          const scope = escapeHtml(h && h.scope ? h.scope : 'project');
          return (
            `<li class="ontum-env-hook" data-env-hook="${event}" ` +
            `data-scope="${scope}">` +
            `<span class="ontum-env-hook-event">${event}</span>` +
            `<span class="ontum-env-hook-matcher">${matcher}</span>` +
            `<span class="ontum-env-scope">${scope}</span>` +
            `</li>`
          );
        })
        .join('')
    : '<li class="ontum-empty">No hooks configured.</li>';

  const skillsHtml = skills.length
    ? skills
        .map((s) => {
          const name = escapeHtml(s && s.name ? s.name : '');
          const scope = escapeHtml(s && s.scope ? s.scope : 'project');
          const desc = escapeHtml(s && s.description ? s.description : '');
          return (
            `<li class="ontum-env-skill" data-env-skill="${name}" ` +
            `data-scope="${scope}">` +
            `<span class="ontum-env-skill-name">${name}</span>` +
            `<span class="ontum-env-skill-desc">${desc}</span>` +
            `</li>`
          );
        })
        .join('')
    : '<li class="ontum-empty">No skills available.</li>';

  return (
    `<div class="ontum-env-group" data-env-group="settings">` +
    `<p class="ontum-env-subtitle">Settings (${settings.filter((s) => s && s.present).length} present)</p>` +
    `<ul class="ontum-env-list" data-count="${settings.length}">${settingsHtml}</ul>` +
    `</div>` +
    `<div class="ontum-env-group" data-env-group="hooks">` +
    `<p class="ontum-env-subtitle">Hooks (${hooks.length})</p>` +
    `<ul class="ontum-env-list" data-count="${hooks.length}">${hooksHtml}</ul>` +
    `</div>` +
    `<div class="ontum-env-group" data-env-group="skills">` +
    `<p class="ontum-env-subtitle">Skills (${skills.length})</p>` +
    `<ul class="ontum-env-list" data-count="${skills.length}">${skillsHtml}</ul>` +
    `</div>`
  );
}

// renderShell(opts) -> string of branded, standalone HTML.
//
//   opts.nonce      — CSP nonce (one is generated if absent).
//   opts.cspSource  — webview.cspSource for the host (img/style origin);
//                     defaults to a self-only policy when absent.
//   opts.brand      — wordmark text (default "ontum").
//   opts.sessions   — [session] from sessions.listSessions(); fills the
//                     Sessions aside (row 2). Absent/empty -> an honest empty
//                     note (the row-1 build passed none, so it still works).
//   opts.transcript — [entry] from transcript.readTranscript().entries; fills
//                     the Transcript section (row 3). Absent -> an honest
//                     "pick a session" note (no session selected yet).
//   opts.environment — { settings, hooks, skills } from
//                     environment.listEnvironment(); fills the Environment
//                     region in the Sessions aside (row 14). Absent -> honest
//                     empty notes per group (the region + wiring still ship).
//
// The returned document is *standalone*: it references no resource from, and
// names no dependency on, the official Claude Code panel. It declares itself
// with `<html data-surface="ontum" data-standalone="true">` so the contract is
// machine-checkable.
function renderShell(opts) {
  const o = opts || {};
  const nonce = o.nonce || makeNonce();
  const brand = escapeHtml(o.brand || 'ontum');
  const sessionsHtml = renderSessionList(o.sessions);
  // When a session is selected the host passes its folded entries; otherwise we
  // show an honest "pick a session" note (no transcript loaded yet).
  const transcriptHtml =
    o.transcript === undefined
      ? '<p class="ontum-empty">Pick a session on the left to read it here.</p>'
      : renderTranscript(o.transcript);
  // Row 9 — the permission-mode surface in the composer. Defaults to 'default'
  // (conservative) when the host passes none.
  const permissionHtml = renderPermissionControl(o.permissionMode);
  // Row 16 — the session-continuity surface in the composer. The host passes the
  // in-force resume target (new / continue / resume) + the currently-selected
  // session id (row 2) so the "Resume selected" button points at it. Absent ->
  // a 'new' target (a fresh session — the conservative default).
  const resumeHtml = renderResumeControl(o.resumeTarget, o.selectedSessionId);
  // Row 11 — a read-only plan-mode banner shows when the in-force permission
  // mode is 'plan', so the human sees the engine is researching + proposing a
  // plan (no edits) before the ExitPlanMode card offers approve/keep.
  const planBadge = isPlanMode(o.permissionMode)
    ? '<span class="ontum-plan-badge" data-region="plan-mode">' +
      '&#9656; plan mode · read-only — the engine proposes a plan to approve' +
      '</span>'
    : '';
  // Row 10 — the slash-command palette. The host passes the discovered command
  // list (slash.listSlashCommands); absent -> an empty palette (the container +
  // wiring still ship, so a later render with commands lights up).
  const slashHtml = renderSlashMenu(o.slashCommands);
  // Row 12 — the @-mention palette. The host passes the discovered workspace
  // file list (mentions.listMentionTargets); absent -> an empty palette (the
  // container + wiring still ship, so a later render with files lights up).
  const mentionHtml = renderMentionMenu(o.mentionTargets);
  // Row 15 — the attachment tray. The host passes the staged attachments
  // (data-free views from attach.displayAttachment); absent/empty -> no chips
  // (the tray container + the attach button + the wiring still ship, so a later
  // render with attachments lights up). The attachments ride the next turn as
  // content blocks ahead of the typed text (engine.encodeUserMessage folds them).
  const attachHtml = renderAttachTray(o.attachments);
  // Row 13 — the MCP servers + tools panel. The host passes the discovered MCP
  // servers (mcp.listMcpServers — the on-disk config folded + annotated with the
  // live engine tools); absent -> an honest "no MCP servers" note (the region +
  // wiring still ship, so a later render with servers lights up).
  const mcpHtml = renderMcpPanel(o.mcpServers);
  // Row 14 — the inherited Environment region (settings layers / hooks /
  // skills). The host passes the discovered environment (environment.list-
  // Environment — the same on-disk config the CLI folds); absent -> honest
  // empty notes (the region + wiring still ship, so a later render lights up).
  const envHtml = renderEnvPanel(o.environment);
  // When a real webview.cspSource is supplied, allow styles/images from it;
  // otherwise lock to 'self' + the nonce. Scripts are nonce-gated either way.
  const styleSrc = o.cspSource ? `'self' ${o.cspSource}` : "'self'";
  const imgSrc = o.cspSource ? `'self' ${o.cspSource} data:` : "'self' data:";
  const csp =
    `default-src 'none'; ` +
    `style-src ${styleSrc} 'unsafe-inline'; ` +
    `img-src ${imgSrc}; ` +
    `script-src 'nonce-${nonce}';`;

  return `<!DOCTYPE html>
<html lang="en" data-surface="ontum" data-standalone="true">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="${csp}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${brand} — surface</title>
  <style nonce="${nonce}">
    :root {
      --ontum-bg: #0d0f12;
      --ontum-panel: #14171c;
      --ontum-edge: #232830;
      --ontum-ink: #e6e9ef;
      --ontum-dim: #8b93a1;
      --ontum-accent: #d7a86e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr auto;
      font-family: var(--vscode-font-family, system-ui, sans-serif);
      color: var(--ontum-ink);
      background: var(--ontum-bg);
    }
    header.ontum-bar {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.55rem 0.9rem;
      border-bottom: 1px solid var(--ontum-edge);
      background: var(--ontum-panel);
    }
    .ontum-mark {
      font-weight: 600;
      letter-spacing: 0.04em;
      color: var(--ontum-accent);
    }
    .ontum-mark::before { content: "◆ "; color: var(--ontum-accent); }
    .ontum-sub { color: var(--ontum-dim); font-size: 0.8rem; }
    main.ontum-body { display: grid; grid-template-columns: 16rem 1fr; min-height: 0; }
    aside.ontum-sessions {
      border-right: 1px solid var(--ontum-edge);
      padding: 0.75rem;
      overflow: auto;
      background: var(--ontum-panel);
    }
    section.ontum-transcript { padding: 1rem; overflow: auto; }
    .ontum-region-title {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--ontum-dim);
      margin: 0 0 0.5rem;
    }
    .ontum-placeholder {
      border: 1px dashed var(--ontum-edge);
      border-radius: 6px;
      padding: 0.75rem;
      color: var(--ontum-dim);
      font-size: 0.85rem;
    }
    .ontum-empty { color: var(--ontum-dim); font-size: 0.85rem; margin: 0; }
    .ontum-transcript-list { display: grid; gap: 0.6rem; }
    .ontum-msg {
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.5rem 0.65rem;
      background: var(--ontum-panel);
    }
    .ontum-msg .ontum-role {
      display: block;
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--ontum-dim);
      margin-bottom: 0.3rem;
    }
    .ontum-msg[data-kind="user-text"] { border-left: 2px solid var(--ontum-accent); }
    .ontum-msg[data-kind="assistant-text"] { border-left: 2px solid #5a82c2; }
    .ontum-msg[data-kind="assistant-thinking"] { opacity: 0.72; font-style: italic; }
    .ontum-msg[data-kind="tool-use"] { border-left: 2px solid #6fae8f; }
    .ontum-msg[data-kind="tool-result"] { border-left: 2px solid #6f7a8f; }
    .ontum-msg[data-error="true"] { border-left-color: #c2685a; }
    .ontum-msg[data-streaming="true"] { border-style: dashed; }
    .ontum-msg[data-streaming="true"] .ontum-text::after {
      content: "▍";
      color: var(--ontum-accent);
      animation: ontum-blink 1s step-start infinite;
    }
    @keyframes ontum-blink { 50% { opacity: 0; } }
    .ontum-text { white-space: pre-wrap; word-break: break-word; font-size: 0.86rem; line-height: 1.45; }
    .ontum-msg pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      font-size: 0.8rem;
      color: var(--ontum-ink);
    }
    /* Row 8 — edit-tool diffs with accept/reject. */
    .ontum-msg[data-diff-tool="true"] { border-left: 2px solid #6fae8f; }
    .ontum-diff {
      margin-top: 0.35rem;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      overflow: hidden;
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      font-size: 0.78rem;
    }
    .ontum-diff-head {
      display: flex;
      justify-content: space-between;
      gap: 0.5rem;
      padding: 0.3rem 0.5rem;
      background: var(--ontum-bg);
      border-bottom: 1px solid var(--ontum-edge);
    }
    .ontum-diff-path { color: var(--ontum-ink); word-break: break-all; }
    .ontum-diff-stat { color: var(--ontum-dim); white-space: nowrap; }
    .ontum-diff-lines { display: block; }
    .ontum-diff-line { display: flex; gap: 0.4rem; padding: 0 0.5rem; white-space: pre-wrap; word-break: break-word; }
    .ontum-diff-gutter { width: 1ch; flex: none; text-align: center; color: var(--ontum-dim); user-select: none; }
    .ontum-diff-text { flex: 1; }
    .ontum-diff-line[data-diff="add"] { background: rgba(111, 174, 143, 0.16); }
    .ontum-diff-line[data-diff="add"] .ontum-diff-gutter { color: #6fae8f; }
    .ontum-diff-line[data-diff="del"] { background: rgba(194, 104, 90, 0.16); }
    .ontum-diff-line[data-diff="del"] .ontum-diff-gutter { color: #c2685a; }
    .ontum-diff-line[data-diff="hunk"] { height: 0.4rem; background: var(--ontum-bg); border-top: 1px dashed var(--ontum-edge); }
    .ontum-diff-actions {
      display: flex;
      gap: 0.4rem;
      padding: 0.4rem 0.5rem;
      background: var(--ontum-bg);
      border-top: 1px solid var(--ontum-edge);
    }
    button.ontum-diff-decision {
      cursor: pointer;
      border: 1px solid var(--ontum-edge);
      border-radius: 5px;
      padding: 0.25rem 0.7rem;
      background: var(--ontum-panel);
      color: var(--ontum-ink);
      font: inherit;
      font-size: 0.76rem;
    }
    button.ontum-diff-decision[data-decision="accept"]:hover { border-color: #6fae8f; color: #6fae8f; }
    button.ontum-diff-decision[data-decision="reject"]:hover { border-color: #c2685a; color: #c2685a; }
    button.ontum-diff-decision:disabled { opacity: 0.5; cursor: default; }
    .ontum-diff-actions[data-decision-state="accept"] { color: #6fae8f; }
    .ontum-diff-actions[data-decision-state="reject"] { color: #c2685a; }
    .ontum-diff-decision-note { padding: 0 0.2rem; align-self: center; font-size: 0.74rem; }
    /* Row 11 — plan mode: the ExitPlanMode plan card + the read-only banner. */
    .ontum-msg[data-plan-tool="true"] { border-left: 2px solid var(--ontum-accent); }
    .ontum-plan {
      margin-top: 0.35rem;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      overflow: hidden;
    }
    .ontum-plan-text {
      margin: 0;
      padding: 0.5rem 0.6rem;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.82rem;
      line-height: 1.45;
      color: var(--ontum-ink);
      background: var(--ontum-bg);
    }
    .ontum-plan-actions {
      display: flex;
      gap: 0.4rem;
      padding: 0.4rem 0.5rem;
      background: var(--ontum-bg);
      border-top: 1px solid var(--ontum-edge);
    }
    button.ontum-plan-decision {
      cursor: pointer;
      border: 1px solid var(--ontum-edge);
      border-radius: 5px;
      padding: 0.25rem 0.7rem;
      background: var(--ontum-panel);
      color: var(--ontum-ink);
      font: inherit;
      font-size: 0.76rem;
    }
    button.ontum-plan-decision[data-plan-decision="approve"]:hover { border-color: var(--ontum-accent); color: var(--ontum-accent); }
    button.ontum-plan-decision[data-plan-decision="keep"]:hover { border-color: #5a82c2; color: #5a82c2; }
    button.ontum-plan-decision:disabled { opacity: 0.5; cursor: default; }
    .ontum-plan-actions[data-plan-state="approve"] { color: var(--ontum-accent); }
    .ontum-plan-actions[data-plan-state="keep"] { color: #5a82c2; }
    .ontum-plan-decision-note { padding: 0 0.2rem; align-self: center; font-size: 0.74rem; }
    .ontum-plan-badge {
      font-size: 0.72rem;
      color: var(--ontum-accent);
      border: 1px solid var(--ontum-accent);
      border-radius: 5px;
      padding: 0.15rem 0.45rem;
    }
    .ontum-session-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.3rem; }
    button.ontum-session {
      display: grid;
      gap: 0.15rem;
      width: 100%;
      text-align: left;
      cursor: pointer;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.45rem 0.55rem;
      background: var(--ontum-bg);
      color: var(--ontum-ink);
      font: inherit;
    }
    button.ontum-session:hover { border-color: var(--ontum-accent); }
    button.ontum-session[aria-selected="true"] {
      border-color: var(--ontum-accent);
      background: var(--ontum-panel);
    }
    .ontum-session-title {
      font-size: 0.82rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ontum-session-meta { color: var(--ontum-dim); font-size: 0.7rem; }
    footer.ontum-composer {
      border-top: 1px solid var(--ontum-edge);
      padding: 0.6rem 0.9rem;
      background: var(--ontum-panel);
      color: var(--ontum-dim);
      font-size: 0.85rem;
    }
    .ontum-compose-row { display: flex; gap: 0.5rem; align-items: flex-end; }
    .ontum-compose-input {
      flex: 1;
      resize: vertical;
      min-height: 2.2rem;
      max-height: 12rem;
      padding: 0.45rem 0.55rem;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      background: var(--ontum-bg);
      color: var(--ontum-ink);
      font: inherit;
      line-height: 1.4;
    }
    .ontum-compose-input:focus { outline: none; border-color: var(--ontum-accent); }
    button.ontum-compose-send {
      cursor: pointer;
      border: 1px solid var(--ontum-accent);
      border-radius: 6px;
      padding: 0.45rem 0.9rem;
      background: var(--ontum-accent);
      color: #1a1206;
      font: inherit;
      font-weight: 600;
    }
    button.ontum-compose-send:disabled { opacity: 0.55; cursor: progress; }
    .ontum-compose-status { margin: 0; font-size: 0.76rem; }
    .ontum-compose-status[data-status="error"] { color: #c2685a; }
    .ontum-compose-status[data-status="done"] { color: var(--ontum-dim); }
    .ontum-compose-status[data-status="sending"] { color: var(--ontum-accent); }
    /* Row 9 — the permission-mode surface. */
    .ontum-compose-foot {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-top: 0.4rem;
    }
    .ontum-permission { display: flex; align-items: center; gap: 0.35rem; }
    .ontum-permission-label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--ontum-dim);
    }
    select.ontum-permission-mode {
      cursor: pointer;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.25rem 0.4rem;
      background: var(--ontum-bg);
      color: var(--ontum-ink);
      font: inherit;
      font-size: 0.76rem;
    }
    select.ontum-permission-mode:focus { outline: none; border-color: var(--ontum-accent); }
    select.ontum-permission-mode[data-mode="bypassPermissions"] { border-color: #c2685a; color: #c2685a; }
    /* Row 16 — the session-continuity surface (new / continue / resume). */
    .ontum-resume { display: flex; align-items: center; gap: 0.3rem; }
    .ontum-resume-label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--ontum-dim);
    }
    button.ontum-resume-btn {
      cursor: pointer;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.25rem 0.45rem;
      background: var(--ontum-bg);
      color: var(--ontum-dim);
      font: inherit;
      font-size: 0.74rem;
    }
    button.ontum-resume-btn:hover:not([disabled]) { border-color: var(--ontum-accent); }
    button.ontum-resume-btn[aria-pressed="true"] {
      border-color: var(--ontum-accent);
      color: var(--ontum-accent);
    }
    button.ontum-resume-btn[disabled] { opacity: 0.45; cursor: default; }
    /* Row 10 — the slash-command palette. */
    .ontum-slash {
      margin-bottom: 0.5rem;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      background: var(--ontum-bg);
      max-height: 14rem;
      overflow: auto;
    }
    .ontum-slash[hidden] { display: none; }
    .ontum-slash-list { list-style: none; margin: 0; padding: 0.25rem; display: grid; gap: 0.15rem; }
    button.ontum-slash-item {
      display: grid;
      grid-template-columns: auto auto 1fr;
      align-items: baseline;
      gap: 0.5rem;
      width: 100%;
      text-align: left;
      cursor: pointer;
      border: 1px solid transparent;
      border-radius: 5px;
      padding: 0.3rem 0.5rem;
      background: transparent;
      color: var(--ontum-ink);
      font: inherit;
    }
    button.ontum-slash-item:hover,
    button.ontum-slash-item[data-active="true"] {
      border-color: var(--ontum-accent);
      background: var(--ontum-panel);
    }
    .ontum-slash-name { color: var(--ontum-accent); font-size: 0.82rem; }
    .ontum-slash-scope {
      font-size: 0.64rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--ontum-dim);
    }
    .ontum-slash-desc {
      color: var(--ontum-dim);
      font-size: 0.76rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    /* Row 12 — the @-mention palette (workspace file completion). */
    .ontum-mention {
      margin-bottom: 0.5rem;
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      background: var(--ontum-bg);
      max-height: 14rem;
      overflow: auto;
    }
    .ontum-mention[hidden] { display: none; }
    .ontum-mention-list { list-style: none; margin: 0; padding: 0.25rem; display: grid; gap: 0.15rem; }
    button.ontum-mention-item {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: baseline;
      gap: 0.5rem;
      width: 100%;
      text-align: left;
      cursor: pointer;
      border: 1px solid transparent;
      border-radius: 5px;
      padding: 0.3rem 0.5rem;
      background: transparent;
      color: var(--ontum-ink);
      font: inherit;
    }
    button.ontum-mention-item:hover,
    button.ontum-mention-item[data-active="true"] {
      border-color: var(--ontum-accent);
      background: var(--ontum-panel);
    }
    .ontum-mention-path {
      color: var(--ontum-accent);
      font-size: 0.8rem;
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ontum-mention-name { color: var(--ontum-dim); font-size: 0.72rem; }
    /* Row 13 — the MCP servers + tools panel (in the Sessions aside). */
    .ontum-mcp-region-title { margin-top: 1rem; }
    .ontum-mcp-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.3rem; }
    .ontum-mcp-server {
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.4rem 0.5rem;
      background: var(--ontum-bg);
      display: grid;
      gap: 0.1rem;
    }
    .ontum-mcp-server[data-available="true"] { border-left: 2px solid #6fae8f; }
    .ontum-mcp-server[data-available="false"] { border-left: 2px solid var(--ontum-edge); }
    .ontum-mcp-name { color: var(--ontum-accent); font-size: 0.82rem; }
    .ontum-mcp-meta { color: var(--ontum-dim); font-size: 0.7rem; }
    .ontum-mcp-tools { list-style: none; margin: 0.25rem 0 0; padding: 0; display: grid; gap: 0.1rem; }
    .ontum-mcp-tool {
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      font-size: 0.72rem;
      color: var(--ontum-ink);
      padding-left: 0.5rem;
    }
    .ontum-mcp-tool::before { content: "\\25b8 "; color: var(--ontum-dim); }
    .ontum-mcp-none { color: var(--ontum-dim); font-style: italic; }
    .ontum-mcp-none::before { content: ""; }
    /* Row 14 — the inherited Environment region (settings / hooks / skills). */
    .ontum-env-region-title { margin-top: 1rem; }
    .ontum-env-group { margin-bottom: 0.6rem; }
    .ontum-env-subtitle {
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--ontum-dim);
      margin: 0 0 0.3rem;
    }
    .ontum-env-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.25rem; }
    .ontum-env-settings,
    .ontum-env-hook,
    .ontum-env-skill {
      border: 1px solid var(--ontum-edge);
      border-radius: 6px;
      padding: 0.35rem 0.5rem;
      background: var(--ontum-bg);
      display: grid;
      gap: 0.1rem;
    }
    .ontum-env-settings[data-present="true"] { border-left: 2px solid #6fae8f; }
    .ontum-env-settings[data-present="false"] { border-left: 2px solid var(--ontum-edge); opacity: 0.7; }
    .ontum-env-hook { border-left: 2px solid #5a82c2; }
    .ontum-env-skill { border-left: 2px solid var(--ontum-accent); }
    .ontum-env-scope {
      font-size: 0.64rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--ontum-dim);
    }
    .ontum-env-meta { color: var(--ontum-dim); font-size: 0.72rem; word-break: break-word; }
    .ontum-env-hook-event { color: var(--ontum-accent); font-size: 0.8rem; }
    .ontum-env-hook-matcher {
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      font-size: 0.72rem;
      color: var(--ontum-ink);
    }
    .ontum-env-skill-name { color: var(--ontum-accent); font-size: 0.8rem; }
    .ontum-env-skill-desc {
      color: var(--ontum-dim);
      font-size: 0.72rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ontum-env-list .ontum-empty { padding: 0.2rem 0.1rem; }
  </style>
</head>
<body>
  <header class="ontum-bar">
    <span class="ontum-mark">${brand}</span>
    <span class="ontum-sub">surface · Phase 1 (parity) · standalone of the official panel</span>
  </header>
  <main class="ontum-body">
    <aside class="ontum-sessions" data-region="sessions">
      <p class="ontum-region-title">Sessions</p>
      ${sessionsHtml}
      <p class="ontum-region-title ontum-mcp-region-title">MCP servers</p>
      <div class="ontum-mcp" data-region="mcp">
        ${mcpHtml}
      </div>
      <p class="ontum-region-title ontum-env-region-title">Environment</p>
      <div class="ontum-env" data-region="environment">
        ${envHtml}
      </div>
    </aside>
    <section class="ontum-transcript" data-region="transcript">
      <p class="ontum-region-title">Transcript</p>
      ${transcriptHtml}
    </section>
  </main>
  <footer class="ontum-composer" data-region="composer">
    <div class="ontum-slash" data-region="slash" hidden>
      ${slashHtml}
    </div>
    <div class="ontum-mention" data-region="mention" hidden>
      ${mentionHtml}
    </div>
    <div class="ontum-attach" data-region="attach">
      ${attachHtml}
    </div>
    <div class="ontum-compose-row">
      <button class="ontum-attach-add" type="button" aria-label="Attach an image or file" title="Attach an image or file">&#128206;</button>
      <textarea
        class="ontum-compose-input"
        rows="1"
        placeholder="Send a prompt to drive a turn… (Enter to send, Shift+Enter for newline)"
        aria-label="Send a prompt"></textarea>
      <button class="ontum-compose-send" type="button">Send</button>
    </div>
    <div class="ontum-compose-foot">
      ${permissionHtml}
      ${resumeHtml}
      ${planBadge}
      <p class="ontum-compose-status" data-status="idle" hidden></p>
    </div>
  </footer>
  <script nonce="${nonce}">
    // Acquire the webview API when hosted; a no-op outside VS Code so the same
    // document renders in a plain browser during tests.
    const vscode = (typeof acquireVsCodeApi === 'function') ? acquireVsCodeApi() : null;
    if (vscode) { vscode.postMessage({ type: 'ontum:surface-ready' }); }

    // Row 2 — select a session. Clicking a session button marks it selected and
    // tells the host which transcript to open (row 3 reads + renders it).
    document.querySelectorAll('button.ontum-session').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('button.ontum-session[aria-selected="true"]')
          .forEach(function (b) { b.removeAttribute('aria-selected'); });
        btn.setAttribute('aria-selected', 'true');
        if (vscode) {
          vscode.postMessage({
            type: 'ontum:select-session',
            id: btn.getAttribute('data-session-id'),
          });
        }
      });
    });

    // Row 9 — the permission-mode surface. Changing the composer's permission
    // <select> tells the host which mode the NEXT turn runs under; the host
    // threads it into engineArgs (--permission-mode), so the turn actually runs
    // under the human's chosen policy. We also reflect the choice on the element
    // (data-mode) so a cold reader / test can see what is in force.
    (function wirePermission() {
      var sel = document.querySelector('.ontum-permission-mode');
      if (!sel) return;
      sel.addEventListener('change', function () {
        var mode = sel.value;
        sel.setAttribute('data-mode', mode);
        if (vscode) {
          vscode.postMessage({ type: 'ontum:set-permission-mode', mode: mode });
        }
      });
    })();

    // Row 16 — the session-continuity surface. Clicking New / Continue recent /
    // Resume selected tells the host which session the NEXT turn joins; the host
    // threads it into engineArgs (--continue / --resume <id>), so the turn
    // actually resumes/continues the chosen conversation. Delegation on the
    // resume region (not per-button) keeps it wired across re-renders. The
    // "Resume selected" button carries the selected session's id (row 2). We
    // reflect the choice on the region (data-resume-mode + aria-pressed) so a
    // cold reader / test can see what is in force. A disabled (no-selection)
    // resume button posts nothing.
    (function wireResume() {
      var region = document.querySelector('.ontum-resume');
      if (!region) return;
      region.addEventListener('click', function (ev) {
        var btn = ev.target && ev.target.closest
          ? ev.target.closest('button.ontum-resume-btn')
          : null;
        if (!btn || btn.disabled) return;
        var mode = btn.getAttribute('data-resume') || 'new';
        var id = btn.getAttribute('data-session-id') || '';
        region.setAttribute('data-resume-mode', mode);
        region.querySelectorAll('button.ontum-resume-btn').forEach(function (b) {
          if (b === btn) b.setAttribute('aria-pressed', 'true');
          else b.removeAttribute('aria-pressed');
        });
        if (vscode) {
          vscode.postMessage({ type: 'ontum:set-resume', mode: mode, id: id });
        }
      });
    })();

    // Row 8 — diff accept/reject. An edit tool-call (Edit/Write/MultiEdit/…)
    // renders as a diff with Accept + Reject buttons. Delegation on document is
    // used (not per-button listeners) so diffs spliced in LATER by the live-tail
    // (row 4) and turn-reply (rows 5–7) paths are wired too. A click posts
    // { type:'ontum:diff-decision', decision, toolId } to the host, then locks
    // the controls and records the decision on the block so the human sees what
    // they chose. (Applying/reverting on disk is the host permission flow's job,
    // row 9 — the surface renders the decision, it does not fake the effect.)
    document.addEventListener('click', function (ev) {
      var btn = ev.target && ev.target.closest
        ? ev.target.closest('button.ontum-diff-decision')
        : null;
      if (!btn) return;
      var decision = btn.getAttribute('data-decision');
      var toolId = btn.getAttribute('data-tool-id');
      var actions = btn.closest('.ontum-diff-actions');
      if (actions) {
        if (actions.getAttribute('data-decision-state') !== 'pending') return;
        actions.setAttribute('data-decision-state', decision);
        actions.querySelectorAll('button.ontum-diff-decision')
          .forEach(function (b) { b.disabled = true; });
        var note = document.createElement('span');
        note.className = 'ontum-diff-decision-note';
        note.textContent = decision === 'accept' ? 'Accepted' : 'Rejected';
        actions.appendChild(note);
      }
      if (vscode) {
        vscode.postMessage({
          type: 'ontum:diff-decision',
          decision: decision,
          toolId: toolId,
        });
      }
    });

    // Row 11 — plan-mode approve/keep. An ExitPlanMode tool-call renders as a
    // plan card with Approve & proceed + Keep planning buttons. Delegation on
    // document (not per-button listeners) so plan cards spliced in LATER by the
    // live-tail (row 4) and turn-reply (rows 5–7) paths are wired too. A click
    // posts { type:'ontum:plan-decision', decision, toolId } to the host, then
    // locks the controls and records the choice on the block. The host records
    // the decision and — on approve — EXITS plan mode so the work can proceed
    // (the surface renders the decision; the engine runs the approved work).
    document.addEventListener('click', function (ev) {
      var btn = ev.target && ev.target.closest
        ? ev.target.closest('button.ontum-plan-decision')
        : null;
      if (!btn) return;
      var decision = btn.getAttribute('data-plan-decision');
      var toolId = btn.getAttribute('data-tool-id');
      var actions = btn.closest('.ontum-plan-actions');
      if (actions) {
        if (actions.getAttribute('data-plan-state') !== 'pending') return;
        actions.setAttribute('data-plan-state', decision);
        actions.querySelectorAll('button.ontum-plan-decision')
          .forEach(function (b) { b.disabled = true; });
        var note = document.createElement('span');
        note.className = 'ontum-plan-decision-note';
        note.textContent = decision === 'approve'
          ? 'Approved — proceeding' : 'Keep planning';
        actions.appendChild(note);
      }
      if (vscode) {
        vscode.postMessage({
          type: 'ontum:plan-decision',
          decision: decision,
          toolId: toolId,
        });
      }
    });

    // Row 15 — image / file attach. The composer's attach button asks the host
    // to open its file picker (the live picker is a VS Code host dialog); the
    // host reads + classifies the chosen file (attach.readAttachment) and
    // re-renders the tray with the staged chip. A chip's Remove button (delegated
    // on document so chips rendered LATER are wired too) posts
    // { type:'ontum:remove-attachment', name } so the host drops it from the
    // staged set. The staged attachments ride the NEXT turn as content blocks
    // ahead of the typed text (the host threads them into driveTurn).
    (function wireAttach() {
      var add = document.querySelector('.ontum-attach-add');
      if (add) {
        add.addEventListener('click', function () {
          if (vscode) vscode.postMessage({ type: 'ontum:attach-file' });
        });
      }
    })();
    document.addEventListener('click', function (ev) {
      var btn = ev.target && ev.target.closest
        ? ev.target.closest('button.ontum-attach-remove')
        : null;
      if (!btn) return;
      var name = btn.getAttribute('data-attach-name');
      var chip = btn.closest('.ontum-attach-chip');
      if (chip && chip.parentElement) chip.parentElement.removeChild(chip);
      if (vscode) {
        vscode.postMessage({ type: 'ontum:remove-attachment', name: name });
      }
    });

    // Row 4 — live-tail. The host watches the selected session's file and, as
    // the engine appends, posts { type:'ontum:append-entries', html } carrying
    // the already-escaped block HTML for ONLY the new entries. We splice it onto
    // the end of the rendered list (creating the list if the panel was on the
    // empty-state note), keep data-count honest, mark the list live, and follow
    // the tail by scrolling the transcript region to the bottom.
    window.addEventListener('message', function (ev) {
      var m = ev && ev.data;
      if (!m || m.type !== 'ontum:append-entries' || !m.html) return;
      var section = document.querySelector('section.ontum-transcript');
      var list = document.querySelector('.ontum-transcript-list');
      if (!list && section) {
        var note = section.querySelector('.ontum-empty');
        if (note) note.remove();
        list = document.createElement('div');
        list.className = 'ontum-transcript-list';
        list.setAttribute('data-count', '0');
        section.appendChild(list);
      }
      if (!list) return;
      list.insertAdjacentHTML('beforeend', m.html);
      list.setAttribute('data-count', String(list.querySelectorAll('.ontum-msg').length));
      list.setAttribute('data-live', 'true');
      if (section) section.scrollTop = section.scrollHeight;
    });

    // Row 5 — drive a turn. The composer posts { type:'ontum:send-prompt', text }
    // to the host, which drives the inherited engine and posts back
    // { type:'ontum:turn-reply', html, isError, subtype, cost }. We disable the
    // send button while a turn is in flight, splice the reply's rendered blocks
    // onto the transcript list (reusing the row-4 append path's list), and show
    // an honest status line (cost/subtype, or the error).
    (function wireComposer() {
      var input = document.querySelector('.ontum-compose-input');
      var send = document.querySelector('.ontum-compose-send');
      var status = document.querySelector('.ontum-compose-status');
      if (!input || !send) return;

      function setStatus(state, text) {
        if (!status) return;
        status.setAttribute('data-status', state);
        status.textContent = text;
        status.hidden = !text;
      }

      function submit() {
        var text = (input.value || '').trim();
        if (!text) return;
        if (vscode) vscode.postMessage({ type: 'ontum:send-prompt', text: text });
        input.value = '';
        send.disabled = true;
        setStatus('sending', 'Driving a turn…');
      }

      send.addEventListener('click', submit);
      input.addEventListener('keydown', function (e) {
        // Rows 10/12 — Escape closes the slash + mention palettes without sending.
        if (e.key === 'Escape') { hideSlash(); hideMention(); return; }
        // Enter sends; Shift+Enter inserts a newline (the chat convention).
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submit();
        }
      });

      // Row 10 — the slash-command palette. As the human types, if the prompt
      // starts with '/' and the command token is still being typed (no space
      // yet), show the palette filtered by the partial token; picking an item
      // fills the composer with '/<name> ' so they can finish + send it down
      // the SAME engine channel (a slash command is pass-through to the engine).
      // The palette never blocks: an unlisted '/foo' just sends as typed.
      var slashMenu = document.querySelector('.ontum-slash');
      function hideSlash() { if (slashMenu) slashMenu.hidden = true; }
      function refreshSlash() {
        if (!slashMenu) return;
        var val = input.value || '';
        if (val.charAt(0) !== '/' || /\s/.test(val)) { hideSlash(); return; }
        var token = val.slice(1).toLowerCase();
        var any = false;
        slashMenu.querySelectorAll('.ontum-slash-item').forEach(function (btn) {
          var name = (btn.getAttribute('data-command') || '').toLowerCase();
          var match = name.indexOf(token) === 0;
          var li = btn.parentElement;
          if (li) li.hidden = !match;
          if (match) any = true;
        });
        slashMenu.hidden = !any;
      }
      input.addEventListener('input', refreshSlash);
      if (slashMenu) {
        slashMenu.addEventListener('click', function (ev) {
          var btn = ev.target && ev.target.closest
            ? ev.target.closest('.ontum-slash-item')
            : null;
          if (!btn) return;
          var name = btn.getAttribute('data-command') || '';
          input.value = '/' + name + ' ';
          hideSlash();
          input.focus();
        });
      }

      // Row 12 — the @-mention palette. As the human types, if the caret is
      // inside an '@' token (an '@' at start/after-space, no whitespace since),
      // show the palette filtered by the partial path; picking an item REPLACES
      // that token with '@<path> ' so the prompt carries the mention down the
      // SAME engine channel (an @-mention is context the engine reads —
      // pass-through). The palette never blocks: an unlisted '@path' just sends
      // as typed. The regex mirrors mentions.mentionQuery / mentions.MENTION_RE
      // (the host-side source of truth) so the surface and the fold agree.
      var mentionMenu = document.querySelector('.ontum-mention');
      var MENTION_TAIL = /(^|\s)@([A-Za-z0-9_./\\-]*)$/;
      function hideMention() { if (mentionMenu) mentionMenu.hidden = true; }
      function refreshMention() {
        if (!mentionMenu) return;
        var val = input.value || '';
        var m = MENTION_TAIL.exec(val);
        if (!m) { hideMention(); return; }
        var token = (m[2] || '').toLowerCase();
        var any = false;
        mentionMenu.querySelectorAll('.ontum-mention-item').forEach(function (btn) {
          var p = (btn.getAttribute('data-mention') || '').toLowerCase();
          // Match on any path segment containing the partial (so '@app' finds
          // 'src/app.js'); an empty token (bare '@') shows everything.
          var match = token === '' || p.indexOf(token) >= 0;
          var li = btn.parentElement;
          if (li) li.hidden = !match;
          if (match) any = true;
        });
        mentionMenu.hidden = !any;
      }
      input.addEventListener('input', refreshMention);
      if (mentionMenu) {
        mentionMenu.addEventListener('click', function (ev) {
          var btn = ev.target && ev.target.closest
            ? ev.target.closest('.ontum-mention-item')
            : null;
          if (!btn) return;
          var pathv = btn.getAttribute('data-mention') || '';
          // Replace the @-token being typed (the tail) with the chosen path.
          input.value = input.value.replace(MENTION_TAIL, function (_m, pre) {
            return pre + '@' + pathv + ' ';
          });
          hideMention();
          input.focus();
        });
      }

      // ensureList() -> the transcript list element, creating it (and clearing
      // the empty-state note) if the panel was on the "pick a session" note.
      // Shared by the streaming-delta and turn-reply paths below.
      function ensureList() {
        var section = document.querySelector('section.ontum-transcript');
        var list = document.querySelector('.ontum-transcript-list');
        if (!list && section) {
          var note = section.querySelector('.ontum-empty');
          if (note) note.remove();
          list = document.createElement('div');
          list.className = 'ontum-transcript-list';
          list.setAttribute('data-count', '0');
          section.appendChild(list);
        }
        return list;
      }

      // Row 6 — stream the live turn. As the engine emits partials the host
      // posts { type:'ontum:turn-delta', phase, index, kind, text }. We paint a
      // per-index "streaming" block (data-streaming="true") and append text as
      // it arrives — using textContent, so the live preview is no less escaped
      // than the folded render — so the assistant's text + thinking show AS THEY
      // ARRIVE. The terminal ontum:turn-reply removes these preview blocks and
      // splices the authoritative folded reply (the partials are a preview, the
      // fold is the source of truth).
      window.addEventListener('message', function (ev) {
        var m = ev && ev.data;
        if (!m || m.type !== 'ontum:turn-delta') return;
        var section = document.querySelector('section.ontum-transcript');
        var list = ensureList();
        if (!list) return;
        var idx = (typeof m.index === 'number') ? m.index : 0;
        var sel = '.ontum-msg[data-streaming="true"][data-stream-index="' + idx + '"]';
        var block = list.querySelector(sel);
        if (!block) {
          block = document.createElement('div');
          block.className = 'ontum-msg';
          block.setAttribute('data-kind', m.kind || 'assistant-text');
          block.setAttribute('data-streaming', 'true');
          block.setAttribute('data-stream-index', String(idx));
          var role = document.createElement('span');
          role.className = 'ontum-role';
          var body = document.createElement('div');
          body.className = 'ontum-text';
          block.appendChild(role);
          block.appendChild(body);
          list.appendChild(block);
        }
        var kind = m.kind || block.getAttribute('data-kind') || 'assistant-text';
        block.setAttribute('data-kind', kind);
        // Row 7 — a tool-use preview carries the tool name on its start; keep it
        // on the block so deltas (raw input JSON) keep the "tool ▸ name" label.
        if (kind === 'tool-use' && m.name) block.setAttribute('data-tool-name', m.name);
        var roleEl = block.querySelector('.ontum-role');
        if (roleEl) {
          if (kind === 'assistant-thinking') roleEl.textContent = 'thinking';
          else if (kind === 'tool-use') roleEl.textContent = 'tool \u25b8 ' + (block.getAttribute('data-tool-name') || 'tool');
          else roleEl.textContent = 'assistant';
        }
        if (m.phase === 'delta' && m.text) {
          var bodyEl = block.querySelector('.ontum-text');
          if (bodyEl) bodyEl.textContent += m.text;
          setStatus('sending', 'Streaming…');
        }
        list.setAttribute('data-live', 'true');
        if (section) section.scrollTop = section.scrollHeight;
      });

      window.addEventListener('message', function (ev) {
        var m = ev && ev.data;
        if (!m || m.type !== 'ontum:turn-reply') return;
        send.disabled = false;
        // Row 6 — drop the live streaming preview before splicing the folded
        // reply, so the authoritative fold replaces it (no double render).
        document.querySelectorAll('.ontum-msg[data-streaming="true"]')
          .forEach(function (b) { b.remove(); });
        if (m.html) {
          var section = document.querySelector('section.ontum-transcript');
          var list = ensureList();
          if (list) {
            list.insertAdjacentHTML('beforeend', m.html);
            list.setAttribute('data-count', String(list.querySelectorAll('.ontum-msg').length));
            if (section) section.scrollTop = section.scrollHeight;
          }
        }
        if (m.isError) {
          setStatus('error', 'Turn failed' + (m.subtype ? ' (' + m.subtype + ')' : '') + '.');
        } else {
          var cost = (typeof m.cost === 'number') ? ' · $' + m.cost.toFixed(4) : '';
          setStatus('done', 'Turn complete' + cost + '.');
        }
      });
    })();
  </script>
</body>
</html>`;
}

module.exports = {
  renderShell,
  renderSessionList,
  renderTranscript,
  renderTranscriptRows,
  renderTranscriptRow,
  renderDiffBlock,
  renderDiffLines,
  renderPlanBlock,
  renderPermissionControl,
  renderResumeControl,
  renderSlashMenu,
  renderMentionMenu,
  renderAttachTray,
  renderMcpPanel,
  renderEnvPanel,
  makeNonce,
  escapeHtml,
};
