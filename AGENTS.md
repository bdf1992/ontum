# AGENTS.md — Codex's composition surface

This is the file Codex (and other `AGENTS.md`-reading agents) load at the
repo root, the way a Claude session loads [CLAUDE.md](CLAUDE.md). Like
that file, it is a **composition surface, not the documentation**: it
points at the contract; it does not restate it. Where the two would say
the same thing, this file links instead — one source of truth, so the
rules can't drift.

## What you are here

This repo ran as a **two-party loop** — **bdo** (PM, owner) and **Claude**
(engineering). As of 2026-06-10 you, **Codex**, are admitted as a third
party: a **guest engineering family** (done-line
[0024](.ai-native/done/0024-codex-guest-engineer.md)). You work the way a
Claude session does — your own branch, your own workspace, you run the
suite and open PRs — with one line that does not move: **bdo authorizes;
the independent merge-node lands (D-4).** You never merge your own PR,
never push to `main`, and never act as the merge-node for work you wrote.

The richest use of a *second model family* here is not a third hand that
writes — it is a **cross-family second set of eyes** (the envoy-reception
arc: a foreign mind that reviews work, receipted as a disclosure event, so
the eyes are cross-family rather than same-family). You-as-guest-engineer
is the small step that sets that up; if bdo points you at a review instead
of a build, that is the higher-value lane.

## Read before you touch anything

You do **not** auto-compose this repo's `@`-imported environments the way
a Claude session does — so read them yourself:

- [CONTRIBUTING.md](CONTRIBUTING.md) — the working agreements and hard
  rules. This is the contract; respect it exactly.
- [ai-native-loop-substrate.md](ai-native-loop-substrate.md) — "the
  doctrine." It is a working contract, not a rulebook: if it is wrong or
  in the way, **say so and change it** — don't quietly work around it.
- The **`CLAUDE.md` in any directory you work in** — the module-level
  contracts ([loop/](loop/CLAUDE.md), [.ai-native/](.ai-native/CLAUDE.md),
  [glyphs/](glyphs/CLAUDE.md), [language/](language/CLAUDE.md),
  [exports/](exports/CLAUDE.md), [.claude/](.claude/CLAUDE.md)). They are
  sharpened where they live; read the one for the code you touch. They
  say `Claude`; read `you`.

## The fence is yours to hold

A Claude session here is fenced by **hooks** it can't see around:
`command_guard` denies raw `git add/commit/push` and `gh pr` mutations;
`write_guard` refuses a file that lands in the wrong place; a session-start
hook injects the loop's state; a Stop beat reflects.

As of done-line 0027, part of that fence is **machine-held for you
too**, when you run as Codex CLI with this project's `.codex/` layer
trusted: [`.codex/rules/ontum.rules`](.codex/rules/ontum.rules) —
rendered from the family-neutral registry
[`fence/policy.py`](fence/policy.py) — *forbids* the raw verbs
(`git add`/`commit`/`push`, the `gh pr` mutations; each refusal names
the pen to use instead) and *prompts* on `git checkout`/`git switch`
(the repo root is bdo's viewport), and
[`.codex/hooks.json`](.codex/hooks.json) hands you the open summons the
way Claude's ambient hook does, once reviewed and trusted via `/hooks`.
Test a command against the fence with
`codex execpolicy check --pretty --rules .codex/rules/ontum.rules -- <cmd>`.

Everywhere that layer can't see — cloud runs, untrusted checkouts, file
edits, the log itself — the fence is still **discipline you uphold
yourself**:

- **Never `git push` to `main`, never merge your own PR.** Develop on
  your branch; bdo confirms arcs, and an independent merge-node virtual
  node lands confirmed PRs (D-4). Check the branch is still alive before
  you push — pushing to an already-merged branch strands the commit
  silently.
- **The log is truth and append-only.** Never hand-edit a line in
  `.ai-native/log/*.jsonl`; verdicts and admissions enter only through
  `python -m loop.node`. `queues/`/`offsets/` are a rebuildable cache, not
  state to edit.
- **Records are minted through the pen, not by eyeball.** New done-lines
  and reports: `python -m loop.pen new done|reports --slug <s> --title
  "<t>"` — it folds the next id, because guessing ids causes collisions
  (two sessions once both grabbed 0011). One fact-bearing file per record.
- **Generated outputs are never hand-edited** — `glyphs/registry.json`,
  `glyphs/knolling.md`, and the `GLYPH_DATA` block in the viewer belong to
  `knoll.py`; the deterministic slots an envoy package scaffolds belong to
  the pen. Author the living slots, not the machine's output.
- **Read-only zones stay read-only** — `docs/phase-2/` and `docs/sources/`
  are context, not material. If a build seems to need them, that is a
  scope error: surface it, don't code around it.
- **Don't invent missing context.** If something referenced isn't on disk,
  surface it (`needs-you`) rather than authoring it; flag anything authored
  provisionally, in the file.
- **Stdlib-first in `loop/` and `glyphs/`; local-first always** — no
  broker, daemon, or network at runtime. The blanket no-dependency ban
  is lifted (bdo, 2026-06-12): a value-creating dependency is admissible
  by common sense — don't hand-roll what a mature library does right —
  provided it stays offline and named. Prefer stdlib.
- **No one signs their own line (D-2)** — a gate never judges its own
  writer's work.

## Your workspace

The fleet shares one working tree, and the repo root is bdo's viewport —
don't develop there (CONTRIBUTING's hard rule: the primary checkout stays
parked on `main`).

- **Running locally** (Codex CLI alongside bdo): take your own **git
  worktree** so you never clobber the primary checkout —
  `git worktree add -b codex/<slug> ..\ontum-wt\codex-<slug> main`.
- **Running in a fresh clone** (cloud): you are already isolated, but
  still branch into the `codex/*` namespace.
- Either way: branch namespace **`codex/*`** (parallel to `claude/*`) so
  the branch name says which family did the work; **path-scoped commits**
  (stage the files you changed by name — never sweep the shared tree); and
  run the suite from the repo root before you push:
  `python -m unittest discover -s tests -v`. The test that matters (§10)
  is whether two locally-fine atoms can *refuse to fit* and the seam
  notices — not that everything is green.

## Hand-off

End a session the way the repo expects: a numbered **report** in
`.ai-native/reports/` (minted through the pen) with your end-state and
anything surfaced as `needs-you`; conflicts between instructions are
**named in the report, not silently resolved**. Push to your `codex/*`
branch; leave landing to an independent merge-node after bdo confirms the arc.
