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

// renderShell(opts) -> string of branded, standalone HTML.
//
//   opts.nonce      — CSP nonce (one is generated if absent).
//   opts.cspSource  — webview.cspSource for the host (img/style origin);
//                     defaults to a self-only policy when absent.
//   opts.brand      — wordmark text (default "ontum").
//
// The returned document is *standalone*: it references no resource from, and
// names no dependency on, the official Claude Code panel. It declares itself
// with `<html data-surface="ontum" data-standalone="true">` so the contract is
// machine-checkable.
function renderShell(opts) {
  const o = opts || {};
  const nonce = o.nonce || makeNonce();
  const brand = escapeHtml(o.brand || 'ontum');
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
    footer.ontum-composer {
      border-top: 1px solid var(--ontum-edge);
      padding: 0.6rem 0.9rem;
      background: var(--ontum-panel);
      color: var(--ontum-dim);
      font-size: 0.85rem;
    }
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
      <div class="ontum-placeholder">
        Session list lands in row&nbsp;2 — reads the local transcript store.
      </div>
    </aside>
    <section class="ontum-transcript" data-region="transcript">
      <p class="ontum-region-title">Transcript</p>
      <div class="ontum-placeholder">
        Transcript render + live-tail land in rows&nbsp;3–4. This window is the
        branded front door; it folds the engine's truth, it stores none of its own.
      </div>
    </section>
  </main>
  <footer class="ontum-composer" data-region="composer">
    Composer (drive a turn) lands in rows&nbsp;5–6 via the inherited engine bridge.
  </footer>
  <script nonce="${nonce}">
    // Acquire the webview API when hosted; a no-op outside VS Code so the same
    // document renders in a plain browser during tests.
    const vscode = (typeof acquireVsCodeApi === 'function') ? acquireVsCodeApi() : null;
    if (vscode) { vscode.postMessage({ type: 'ontum:surface-ready' }); }
  </script>
</body>
</html>`;
}

module.exports = { renderShell, makeNonce, escapeHtml };
