# Ontum

A working repo for an AI-native loop substrate — and, through it, the wider
Ontum system it exists to build.

One idea we're building around: **the files are the environment, the agent is
the (mortal) process, and the console just routes between them.** Work moves
through a versioned, file-defined environment; sessions come and go; the files
stay. The longer-range bet (phase 2) is a self-similar architecture for
prediction and compression over **glyphs and structure** — typed, oriented,
geometrically adjacent pieces — rather than flat token streams, navigating
syntax, semiotics, and semantics at once.

## Where things live

| Path | What it is |
|---|---|
| `ai-native-loop-substrate.md` | **The doctrine.** The working harness: decisions, invariants, seams, the build rule. Start here. |
| `loop/` | Phase-1 loop skeleton (doctrine §11): a re-runnable reconcile pass over a file log. Stdlib only — no broker, no daemon, no network. |
| `tests/` | Tests against the done-line: goal reached over passes; SIGKILL mid-run loses nothing; cache replayed from log is byte-identical. |
| `.ai-native/` | The loop's own ground: `log/` (truth), `atoms/`, `done/` (done-lines, written before code), `reports/` (session reports). |
| `docs/phase-2/` | **Read-only context.** The wider system the loop exists to build: the cellular language, the 27-cell sheaf, the Ontum unit system, the ontogrammatic typing discipline. |
| `docs/sources/` | **Read-only inspiration.** External sources aligned with the work, for when we hit walls or question our sanity. |
| `.claude/skills/` | **Our rituals.** Versioned prompts-as-code (doctrine §7) for repeatable repo operations — start with [branch-ritual](.claude/skills/branch-ritual/SKILL.md). |

## Quickstart

The loop is pure stdlib — nothing to install.

```sh
# read-only summary of the current fold over the log
python loop/reconcile.py --status

# run reconcile passes until the atom reaches its desired state (or sticks)
python loop/reconcile.py --until-done

# run the tests
python -m unittest discover -s tests -v
```

Every invocation ends with a clear result on stdout: `done` | `report` |
`needs-you`. The log is truth; `queues/` and `offsets/` are a cache — a pure
fold over `log/` — and can be deleted and rebuilt at any time
(`--rebuild-cache-only`).

## Status

Phase 1. The mocked loop skeleton is built and its done-line is met: one atom
reaches its goal state through reconcile passes, a SIGKILL mid-run loses
nothing, and re-runs never double-act. Next per doctrine §11: make exactly one
node real, and no second one until the first has a passing receipt.

## Working method

This repo runs on a specific discipline — done-lines before code, receipts
before version bumps, read-only zones that stay read-only. See
[CONTRIBUTING.md](CONTRIBUTING.md) before changing anything.

## License

Copyright © 2026. All rights reserved — see [LICENSE](LICENSE). The repo is
viewable for reference; no reuse rights are granted yet.
