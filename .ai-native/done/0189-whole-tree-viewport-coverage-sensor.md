# Done-line 0189 — File-touch coverage sensor: discovered vs undiscovered per file

Written before code, per §9.4. When this line is met, stop.

> **Done when:** A PostToolUse file-touch sensor (`.claude/hooks/file_touch.py` on
> `Read|Edit|MultiEdit|NotebookEdit`) records which files each session touches to
> `.ai-native/log/file-touch.jsonl` — the activity-accounting runtime witness on
> the file tools, DECLARED in `activity-register.json` so the §10 teeth pass — and
> `loop/coverage.py` folds it into the discovered/undiscovered set per directory
> (`--json` for the step-2 consumer). §10 tooth: a tracked file never touched reads
> 'undiscovered'; a read/edited file reads 'discovered'; the fold is proven
> non-vacuous (a constant 'all discovered' is caught). Hook fails open, exit 0.
> Out of scope (named): the VS Code extension that PAINTS the mask (step 2);
> edited/red decorations (native VS Code).

## Why

bdo, 2026-06-22 wants his VS Code viewport to show a per-file *mask*: which files
agents have NOT discovered yet (undiscovered), plus edited/red which VS Code
already paints natively. Step 1 (this build) is the SENSOR + a coverage fold:
record which files each session reads/edits so "discovered vs undiscovered"
becomes computable data. This is the activity-accounting runtime witness
("organ 2", loop/activity.py done-line 0143) turned on the file tools.

## In scope (one increment)

- `.claude/hooks/file_touch.py` — a PostToolUse sensor on the file tools: one
  `{ts, session, action, path}` record per Read/Edit to a gitignored sink. Stdlib,
  fail-open, exit 0 always; skips a tool-use with no concrete file_path.
- `.claude/settings.json` — the PostToolUse wiring (`Read|Edit|MultiEdit|NotebookEdit`).
- `.claude/activity-register.json` — the declared data-practice for the sensor, so
  loop.activity's §10 teeth pass (an undeclared collector is refused).
- `.gitignore` — `.ai-native/log/file-touch.jsonl` (telemetry, not truth).
- `loop/coverage.py` — the pure read-only fold: discovered (touched) vs
  undiscovered (a tracked file never touched), per-directory counts, `--json`.
- `tests/test_coverage.py` — the non-vacuous §10 tooth.
- The backing atom `atom.whole-tree-viewport-coverage-sensor.v0` (no arc claimed).

## Not in scope (named, not invented away)

- **The VS Code extension that PAINTS the mask** — step 2; this build is the
  sensor + data only.
- **edited/red decorations** — native VS Code already gives those; this fold owns
  only the "discovered" axis.
