# Ontum Forest Mask — a per-file agent-attention mask for VS Code

A plain-JavaScript VS Code extension that puts a **mask** on the Explorer:
every file is tagged by how much agent attention it has received, and files
no agent has discovered are **dimmed**.

## The four tiers

| badge | tier           | meaning                                                        |
|-------|----------------|---------------------------------------------------------------|
| `·`   | undiscovered   | no agent has read or edited this file (dimmed — the mask)      |
| `r`   | read           | an agent has read it, none has edited it                       |
| `✎`   | written        | an agent has edited it (edit outranks read)                    |
| `●`   | in-context     | touched recently — a **proxy** for "in the context window now" |

The colours track the active theme (read = blue, written = green,
in-context = yellow, undiscovered = the muted/disabled foreground so it dims).
Hover any file for the full label.

## Where the data comes from

The mask reads `.ai-native/log/file-touch.jsonl` — the **same** log
`loop/coverage.py` folds, written by the file-touch sensor
(`.claude/hooks/file_touch.py`). There is no second source: the extension only
*reads and classifies* records the sensor already produced
(`{ts, session, action, path}`). It re-reads the log live whenever it changes,
so the mask updates as agents work.

**The mask is empty until the sensor is live.** The file-touch sensor lands
with `loop/coverage.py` on branch `claude/whole-tree-viewport` (PR #662). Until
that sensor is wired and has recorded some touches, the log does not exist and
**every file reads `undiscovered`** — which is correct (nothing has been
discovered yet), not a bug. Once the sensor is live the mask populates as
sessions read and edit files.

## The "in-context" proxy (be honest about it)

`in-context` does **not** measure what is actually in a model's context window.
True context membership and eviction are unobservable from outside the model —
the harness can only record that a file *tool* touched a path, never whether
those bytes still sit in the live context. This extension uses **recency of the
last touch** (default: within 30 minutes) as the best available signal that a
file is "in context right now". A file read an hour ago and long since evicted
correctly falls back to `read`. The window is a dial in `extension.js`
(`RECENCY_MS`).

## Install (drop-the-folder, no build)

This is a plain-JS extension — no TypeScript, no npm install, no bundler. To
load it into a VS Code (including a portable VS Code):

1. Copy the `forest-mask/` folder into your VS Code extensions directory:
   - **Portable VS Code:** `<vscode>/data/extensions/forest-mask/`
   - **Stable install:** `~/.vscode/extensions/forest-mask/`
   - **Insiders:** `~/.vscode-insiders/extensions/forest-mask/`
   (so that `extensions/forest-mask/package.json` exists).
2. Reload the window (`Developer: Reload Window`) or restart VS Code.
3. Open the ontum repo as a workspace folder. The Explorer file badges appear
   once the touch log has records.

No marketplace, no `.vsix` packaging, and no install action are part of this
build — copying the folder and reloading is the whole install. (Installing it
into your editor is a machine action; this repo only ships the files.)

## Tests

The pure tier logic is tested without VS Code:

```sh
node vscode/forest-mask/tier.test.js
```

The test is non-vacuous (§10): a constant classifier is caught.
