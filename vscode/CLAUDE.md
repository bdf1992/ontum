# vscode/ — VS Code surfaces over the loop

The home of editor-side surfaces that *read the loop's records and paint
them* where bdo already works — the IDE Explorer, the gutter, the status
bar. These are **surfaces**, never a second source: a surface here reads
the same append-only logs and folds the rest of the repo treats as truth
(`.ai-native/log/`), and it computes nothing the loop does not already
know. If a surface seems to need a fact no record carries, that is a
sensor gap to surface (`needs-you`), not a thing to derive privately here.

Rules of this directory:

- **Plain JavaScript, no toolchain.** Extensions here are loadable by
  dropping the folder into a VS Code extensions directory — no
  TypeScript, no npm build step, no bundler. Just `package.json` +
  `extension.js` using the host-provided `vscode` API and node's built-in
  `fs`/`path`. The local-first, stdlib-by-default law of `loop/` applies:
  no runtime dependency, no network.
- **The log is truth; the surface is a fold.** A surface reads
  `.ai-native/log/*.jsonl` (e.g. the file-touch sensor's
  `file-touch.jsonl`) exactly as the Python folds do — it never keeps a
  second store of the same fact, and editing the log is never its job.
  When the data is missing, the surface fails soft and shows the honest
  empty state (absence is information).
- **The pure logic is testable without VS Code.** The classification a
  surface paints lives in a pure module (no `vscode` import) tested by
  plain `node` — the §10 tooth must be non-vacuous (a constant classifier
  is caught), in the grain of `causality/canvas.persist.test.js`. The
  `vscode`-touching shell (`extension.js`) stays thin.

First resident: `forest-mask/` — the per-file Explorer mask that tags
each file read / written / in-context / undiscovered from the file-touch
sensor's log, the painting half of the coverage sensor
(`loop/coverage.py`).
