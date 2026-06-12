# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

It is a **composition surface**, not the documentation (doctrine §8,
D-9): module environments live next to their modules and are pulled in
here with `@`-imports — sharpen them where they live, not here. The
scope stack composes too: your user-global `~/.claude/CLAUDE.md` loads
beneath this file, and nested `CLAUDE.md` files load when working in
their directories — local folder and global directories compose (bdo's
@/@@ directive, 2026-06-10; done-line 0010).

A module is `@`-imported here when its environment binds a session
*wherever it works* — governance that travels (the harness config, the
fence). A module whose knowledge only matters while you're inside it
(`tests/`, `pivot/`) is left to nested loading and not imported here;
promoting it would bloat every session for no carried rule. When a new
module's `CLAUDE.md` is born, that is the test for whether it joins this
surface.

@loop/CLAUDE.md
@glyphs/CLAUDE.md
@language/CLAUDE.md
@.ai-native/CLAUDE.md
@exports/CLAUDE.md
@.claude/CLAUDE.md
@fence/CLAUDE.md

## What this repo is

An AI-native loop substrate: work moves through a versioned,
file-defined environment; sessions are mortal; the files stay. The
canonical spec is [`ai-native-loop-substrate.md`](ai-native-loop-substrate.md)
— "the doctrine." Code comments and commit messages cite it constantly
(D-5, I-2, §14…); those references resolve there. The doctrine is a
working contract: if it's wrong or in the way, say so and change it —
don't quietly work around it.

The repo runs as an owner-and-engineering loop: **bdo** (PM, owner) and
an engineering family — **Claude**, and (done-line 0024) **Codex** as an
admitted *guest engineer*, whose composition surface is
[AGENTS.md](AGENTS.md). The party that engineers can vary; the owner does
not — bdo is the last stop (D-4). See [CONTRIBUTING.md](CONTRIBUTING.md)
before changing anything.

## The horizon (what the substrate is for)

The substrate is the harness, never the building. **Ontum** — the
fabric described in `docs/phase-2/` (a living system of named, bounded,
provenance-carrying units of meaning) — is what the loop exists to
build; the loop is its metabolism: durability, second-set-of-eyes,
receipts, ambient control. A previous session described the substrate
as "what ontum is trying to be" and bdo flagged it as a category error
— [report 0004](.ai-native/reports/0004-the-frame-harness-and-fabric.md)
records the correction; don't repeat it.

Current direction lives in `.ai-native/epics/` — each epic carries an
`arc` and a `horizon` (what done looks like at epic scale). As of
mid-2026 the horizons are: all five gates real (only L0 is today), the
slow loop re-admitting its own dials from outcomes, corpus-to-system (a
corpus pointed at the machine becomes *proposed* atoms), and a served,
authenticated phone inbox where bdo steers arcs — not tickets — with
one stamp. Making a node real is not just de-mocking: each real node is
the system's first sensor of a given kind of meaning (report 0004 §3).

Orientation reading order for a fresh session (report 0004 §5): the
doctrine → `docs/phase-2/` (read-only) → report 0004 (the bridge
between them) → the most recent reports.

## Hard rules

- **`docs/phase-2/` and `docs/sources/` are read-only.** Context, not
  material. If a build seems to need them, that's a scope error —
  report it, don't code around it.
- **Don't invent missing context; absence is information.** If the
  doctrine references something not on disk, surface it (`needs-you`)
  rather than authoring it. Anything authored provisionally is flagged
  as provisional in the file itself.
- **Support the owner; never offload onto him (bdo, 2026-06-11).** A
  session does the work and supports bdo — it does not shove mechanical
  or janitorial tasks onto him, and it never feigns incapacity to dodge
  them. The owner *authorizes* (confirms arcs, activates changes) by a
  gesture on a surface, when he chooses; he does not run commands, clean
  stranded state, commit loose files, or do a session's cleanup. Never
  manufacture an "only you can do" list; never hide behind a rule (e.g.
  "a session never re-points the viewport") to avoid a safe, reversible
  action whose work is already preserved. **A rule that forces
  offloading is a bug in the rule — fix the rule, don't punt the work.**
  (`needs-you` stays for genuine missing context and authorizations, not
  for work a session can do itself.)
- **The merge-node lands; bdo confirms arcs (amended 2026-06-11, his
  stamp).** bdo no longer performs PR merges — he named it performative,
  twice. An independent **merge-node** agent lands work to `main`: it
  merges a *confirmed-arc* PR it did **not** author, once the suite is
  green. D-4 is preserved at arc scale (done-line 0028): bdo's
  `confirm-arc` is the authorization the merge-node *executes* — a node
  propels work, it never authorizes it (§… D-4). No one signs their own
  line: the merge-node never lands its own author's PR. Sessions still
  develop on `claude/*` branches and never push to `main` directly; they
  open a PR as the *unit the merge-node lands*, never as a thing for bdo
  to merge. **Do not run the branch-ritual hand-off to route bdo into a
  merge, and never tell him work is "at the stamp" — that loop is
  retired.** bdo's only surfaces are **arc confirmation** and the **daily
  arc digest**. The merge-node lands through the PR pen's `land` verb
  (`.claude/skills/branch-ritual/pr.py land --epic <id> --by <node>`);
  its eyes are `loop/merge.py`.

## Working method (doctrine §9)

- **Write the definition of "done" before starting**, in `.ai-native/done/`
  (numbered). When it's met, stop.
- **No receipt, no version bump.** One real node at a time — no second
  one until the first has a passing receipt.
- Out of room means shrink the scope and ship the smaller thing.
- Each session ends with a numbered report in `.ai-native/reports/`,
  including end-state and anything surfaced as `needs-you`. Conflicts
  between instructions get named in the report, not silently resolved.
- The test that matters (§10): can two locally-fine atoms *refuse to
  fit*, and does the gate notice? If everything passes on the first
  try, the check isn't doing its job yet.
- The tripwire (§12): editing the doctrine or polishing repo structure
  instead of building the next step is the signal to close the file and
  go build.
