# Real-turn proof — the fake-engine caveat, closed for the drive path

The headline risk in `GRADES.md` was: *"rows 5–10 are green against a FAKE engine
— no real billed turn has ever run."* This is the record of driving a **real**
`claude` turn through the actual `engine.js` code (2026-06-24, closing the gap).

## What was run (and the result)

```
node -e 'require("./engine.js").driveTurn({ prompt: "Reply with exactly: OK", cwd: "/tmp", timeoutMs: 90000 }).then(...)'
→ text="OK"   isError=false   cost=$0.39873   entries=1
```

A real, billed model call, driven by the same `driveTurn` the surface uses, over
the real CLI stream-json channel — returning the expected reply. **The engine
path works end-to-end against the real engine, not just a fake.** Row 5 ("drive a
turn") is no longer fake-only.

## Two real bugs the real turn caught (that fakes could not)

1. **Model-alias 404 (fixed).** `engineArgs` passed no `--model`, so the CLI's
   bare default resolved the alias `opus`, which the API rejects with
   `404 not_found_error: model: opus` in headless stream-json mode. Fixed:
   `engineArgs` now pins `--model` (caller's value wins, else `DEFAULT_MODEL =
   claude-opus-4-8`). This is the **same** bug that 404'd the overnight scheduler
   — now fixed at the source. A fake engine never sees it.

2. **The repo's own hooks suppress a nested headless turn (environmental, not an
   engine bug).** Driving the turn with `cwd` = the **ontum repo** returns an
   EMPTY completion (`result: ''`, `num_turns: 0`) even though it bills — because
   the repo's `UserPromptSubmit` hooks (`loop.summon`, `mock_shame`) inject into
   every prompt of the nested session and derail the one-shot turn. The SAME
   invocation with `cwd: /tmp` (no ontum hooks) returns `OK` cleanly. So:
   - `engine.js` is **correct** — proven by the clean-cwd run above.
   - **Implication for the surface:** when driving a turn for a project that
     carries `UserPromptSubmit` hooks, the surface must drive in a way that does
     not re-trigger those hooks (e.g. an isolated/!-hooked invocation, or honor
     the project's hooks deliberately). Tracked as a Phase-1 finding; the
     mechanism is row 14's territory (how the environment is inherited).

## Honest remaining scope (still open)

- **Pixel rendering** in a real VS Code webview host is still unproven (all render
  tests are on HTML strings). The first `code --extensionDevelopmentPath` load is
  the next real test.
- **Streaming partials** (`--include-partial-messages`) against a real turn: the
  drive is proven; the live partial-by-partial DOM mutation in a host is not.
- The **in-repo hook-suppression** above must be handled before the surface can
  drive turns for a hooked project.

The drive path is real now. The surface-in-a-host and the hook-handling are the
next closes.
