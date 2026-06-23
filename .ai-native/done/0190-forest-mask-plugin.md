# Done-line 0190 — Forest-mask VS Code plugin: per-file read/written/in-context/undiscovered mask

Written before code, per §9.4. When this line is met, stop.

> **Done when:** A plain-JavaScript VS Code extension (`vscode/forest-mask/`,
> no TypeScript, no npm build, no bundler — loadable by dropping the folder into
> a VS Code extensions dir) registers a `FileDecorationProvider` that tags each
> file by its agent-attention tier read from `.ai-native/log/file-touch.jsonl`
> (the SAME source as `loop/coverage.py` — no second truth): `undiscovered`
> (no agent has opened it), `read`, `written` (any `edit` record), or
> `in-context` (touched within a recency window), live-refreshing when the touch
> log changes. §10 tooth: a PURE tier classifier (`tier.js`) proven non-vacuous
> by a plain-`node` test (`tier.test.js`) — a never-seen path → undiscovered, a
> read-only path → read, an edited path → written, a just-now touch → in-context,
> an old read → read; a constant classifier is caught. `in-context` is an
> explicit recency PROXY (true context-window membership/eviction is
> unobservable; recency is the best available signal — documented in code).
> Extension fails soft: a missing/empty log → every file `undiscovered`, nothing
> throws. Out of scope (named): the side panel, packaging to `.vsix`, and any
> install action (those are the caller's machine acts).

## Why

bdo, 2026-06-23: he wants a per-file MASK on the VS Code Explorer that shows only
what an agent has read, written, or has in context — and DIMS (masks) the files no
agent has discovered. "a masking to show only what the agent has read/written or
is in context window... start simple and label and tag for now" (no side panel).
This is the step-2 PAINTING surface over the file-touch sensor + coverage fold
(`loop/coverage.py`, `.claude/hooks/file_touch.py`, on branch
`claude/whole-tree-viewport`, PR #662). The sensor produces the data; this
extension paints it as Explorer file decorations.

## In scope (one increment)

- `vscode/CLAUDE.md` — the module environment governing the new `vscode/` dir.
- `vscode/forest-mask/package.json` — a minimal extension manifest, no deps.
- `vscode/forest-mask/tier.js` — the PURE classifier (the §10 tooth lives here).
- `vscode/forest-mask/extension.js` — the `FileDecorationProvider`, log read +
  cache + live watch.
- `vscode/forest-mask/tier.test.js` — the non-vacuous node test.
- `vscode/forest-mask/README.md` — install + the data-dependency honest note.

## Not in scope (named, not invented away)

- **A side panel** — bdo said start simple, label and tag only; decorations, not a view.
- **Packaging to `.vsix`** — drop-the-folder install only.
- **The install action** — installing/loading into VS Code is the caller's machine act.
- **edited/red** — native VS Code already paints unsaved edits; this owns the
  agent-attention tiers, not editor dirty-state.
