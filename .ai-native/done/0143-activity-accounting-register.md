# Done-line 0143 — Account for hook activity — a data-practices register the gateway audits

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a read-only fold (`loop/activity.py`) accounts for every wired
> Claude hook by reconciling a declared data-practices register — per hook: what
> it **collects**, what it **uses** that for, where the data **goes**, and
> whether its own firing is **witnessed** — against the live
> `.claude/settings.json` wiring, and it REFUSES (§10 teeth) both an *undeclared
> collector* (a wired hook with no register entry) and a *ghost* (a register
> entry no longer wired); proven by a test that a fabricated undeclared hook is
> caught (the check is not vacuous), with the full suite green and the work
> atom-backed so the PR is a landable unit.

## Why

bdo, 2026-06-20: *"account for all activity, even Claude hooks like session
start and tool call, and start auditing their data collection and usage for a
shared gateway."* The harness's own hooks are the gateway's sensors — but their
**own** data collection is the one activity the gateway never accounts for.
Today 15 hook scripts collect data (command strings, spawn prompts, full raw
stdin/argv/env via the codex probe, gh poll results) mostly **silently into
gitignored sinks**, and most hooks do not record that they fired at all. There
is no register, no fold, no teeth — nothing that could ever say "this hook
collects data it never declared." Who watches the watchers.

This is the accounting layer the git-gh-gateway proposal deferred (*"the
witness-log home and its fold"*), widened from git/gh reads to all activity. It
extends the gateway's standing asymmetry (reads get witnessed, not authorized)
to the harness's own metabolism.

## In scope (organ 1 — register first, bdo's choice)

- The declared data-practices register (data, version-controlled, human-legible).
- `loop/activity.py` — the read-only reconciling fold, sibling of
  `census`/`gaps`/`heal`: read-only, propose-grain, the cut stays bdo's (D-4).
- The §10 teeth + a test proving the undeclared-collector catch is not vacuous.

## Not in scope (named, the next piece — not invented away)

- **Organ 2: the runtime witness** — every hook firing emits a first-class
  attributed receipt (who fired, what it collected, where it went), the sibling
  of `tool-use.jsonl` the proposal deferred. bdo chose "both, register first";
  the witness is the next done-line, once this one carries a passing receipt.
- The shared-gateway PDP unification across all seams (arc-level, bdo's, D-4).
- The Codex layer's own hooks (`.codex/hooks.json`) reconciled as a second
  wiring source — folded if present, but the Claude layer is this organ's floor.
