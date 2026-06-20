# Report 0105 — the headless gate rail launches and leaves a trace

## What landed

bdo, on reading the production-gate report (PR #286): "The headless gate rail is broken inside a session ... shouldn't it have written some file? Let's fix that."

Reproduction found the rail had two root causes, plus the observability gap bdo named:

1. `gate.py` `launch_claude` passed **no `--model`**, so the child `claude -p` defaulted to the alias `opus`, which **404s** headless (`API Error: 404 model: opus`).
2. It ran with **`cwd=ROOT`**, so the repo's `UserPromptSubmit` session hooks loaded in the child and **blocked the prompt** — `num_turns: 0`, empty result, `is_error: false` (the 0-turn vanish). The `compose()` prompt is fully self-contained, so a neutral cwd is the fix.
3. On failure the rail **wrote nothing**, so the cause vanished.

Fix (done-line 0138, confined to the gate pen's launch step — D-4 untouched):
- `_launch_cmd` carries an explicit, configurable `--model` (`ONTUM_GATE_MODEL`, default `claude-opus-4-8`).
- `_launch_cwd` is a neutral temp dir, not the repo root.
- `write_trace` persists the full run (model, argv, prompt, raw stdout, stderr, exit) to a **gitignored** `.ai-native/log/gate-runs/`, on every launch, even on failure, with the path named in the failure report and the open trust-rail issue.
- `tests/test_gate_rail.py` — §10 teeth with an injected fake runner (no live spawn): the command carries a model and a non-repo cwd, and a trace is written on both a parse-success and a parse-failure (the failure still names the path and still raises). Full suite green.

**Proven end-to-end on the now-fixed rail (the dogfood):** the branded `value-gate.claude.v1` judged this PR's own atom `atom.gate-rail-fix.v0` with real inference → **accept** (rcp.9332cdfe72a6); trust-rail issue **#287** opened at birth and closed with the verdict. This is the independent review the hard rule requires, back on the branded spawn rail. Handed off as **PR #288**, atom-backed. The stray issues #284/#285 from the broken rail were closed earlier with the diagnosis.

## needs-you

1. **Awaiting the merge-node** for both #288 (this) and #286 (production-gate). `atom.gate-rail-fix.v0` serves `epic.the-field` (the gates as real perceivers); `atom.production-gate.v0` serves `epic.environments` (confirmed). If `epic.the-field`'s arc is not confirmed, #288 waits on your arc confirmation before the merge-node can land it.
2. **Model default is a buried-no-longer choice:** the gate now judges with `claude-opus-4-8` by default, overridable via `ONTUM_GATE_MODEL`. Flagged in case you want a cheaper default for routine gate runs.

## End-state

`report` — PR #288 open, atom-backed, full suite green; the branded gate rail is fixed and demonstrated live (rcp.9332cdfe72a6, issue #287 closed). Every gate run now leaves a trace file. Awaiting the merge-node (and arc confirmation for epic.the-field if needed).
