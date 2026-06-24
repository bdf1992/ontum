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
function renderTranscriptRow(e) {
  const kind = e && e.kind ? e.kind : '';
  if (kind === 'tool-use') {
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
    .ontum-text { white-space: pre-wrap; word-break: break-word; font-size: 0.86rem; line-height: 1.45; }
    .ontum-msg pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: var(--vscode-editor-font-family, ui-monospace, monospace);
      font-size: 0.8rem;
      color: var(--ontum-ink);
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
    .ontum-compose-status { margin: 0.4rem 0 0; font-size: 0.76rem; }
    .ontum-compose-status[data-status="error"] { color: #c2685a; }
    .ontum-compose-status[data-status="done"] { color: var(--ontum-dim); }
    .ontum-compose-status[data-status="sending"] { color: var(--ontum-accent); }
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
    </aside>
    <section class="ontum-transcript" data-region="transcript">
      <p class="ontum-region-title">Transcript</p>
      ${transcriptHtml}
    </section>
  </main>
  <footer class="ontum-composer" data-region="composer">
    <div class="ontum-compose-row">
      <textarea
        class="ontum-compose-input"
        rows="1"
        placeholder="Send a prompt to drive a turn… (Enter to send, Shift+Enter for newline)"
        aria-label="Send a prompt"></textarea>
      <button class="ontum-compose-send" type="button">Send</button>
    </div>
    <p class="ontum-compose-status" data-status="idle" hidden></p>
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
        // Enter sends; Shift+Enter inserts a newline (the chat convention).
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submit();
        }
      });

      window.addEventListener('message', function (ev) {
        var m = ev && ev.data;
        if (!m || m.type !== 'ontum:turn-reply') return;
        send.disabled = false;
        if (m.html) {
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
  makeNonce,
  escapeHtml,
};
