# Done-line 0027 — Codex fenced by machine, from one registry

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a Codex CLI session in this repo is fenced by machine,
> not prose alone — the firm denials live **once**, in a family-neutral
> fence registry (`fence/policy.py`: argv prefix, decision,
> justification-as-story, inline match/not-match examples, and the
> `command_guard` rule ids each mirrors); a deterministic renderer
> (`fence/render_codex.py`) emits the committed repo-local `.codex/`
> layer (`rules/ontum.rules` forbidding raw `git add`/`commit`/`push`
> and the `gh pr` mutations, prompting on `git checkout`/`switch`;
> `hooks.json` wiring `SessionStart`/`UserPromptSubmit` to
> `python -m loop.summon --hook`); a parity test refuses drift in three
> directions (registry ↔ command_guard behavior, registry ↔ rendered
> bytes on disk, examples ↔ prefix semantics); and `AGENTS.md` is
> amended on the record to say which lines of the fence are now
> machine-held and which remain self-discipline.

## Direction (bdo, chat, 2026-06-10)

Done-line 0024 named "hook-equivalent enforcement for Codex" as a later
piece — the fence graduating from prose in `AGENTS.md` to an actual
guard. bdo green-lit it today with the shape researched against the
local Codex manual (codex-cli 0.137.0-alpha.4): repo-local `.codex/`
layer, **rules** (`prefix_rule`, Starlark, native `forbidden` decisions
with load-time-validated examples) for hard command blocking, **hooks**
(`hooks.json`, same event names as Claude's) for the ambient summons; no
fork of Codex, no plugin unless it must travel across repos.

The deeper intent, lifted to the record: **Claude Code is a working
surface, not the system itself.** The fence policy becomes
family-neutral data with a governed home — a commons both harness
surfaces render from — so that, eventually, entire operations can lift
into other systems by writing a renderer, not by re-authoring the rules.

## Out of scope, named (later pieces)

- **Converging `command_guard.py` to read the registry directly.** The
  Claude guard keeps its own `DENY_RULES` today; the parity test holds
  the seam. Folding it onto `fence/policy.py` is a separate increment —
  it touches the live fence every Claude session runs behind.
- **A Codex PreToolUse watcher.** The local manual documents hook
  config shape but not the hook stdin/stdout contract, so the
  watch-log/deny half of `command_guard` has no verified Codex port
  yet. Rules carry the blocking job; the watcher waits for the
  documented contract.
- **A `write_guard` equivalent for Codex** (`apply_patch` matcher
  exists) — same blocker, same answer.
