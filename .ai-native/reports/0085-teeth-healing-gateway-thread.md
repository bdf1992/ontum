# Report 0085 — Teeth, healing, and the session-gateway thread — what shipped and how to pick it up

- **Date:** 2026-06-18
- **Session:** a long design+build arc with bdo, from an /insights crawl through three shipped increments and one architecture proposal.

## End-state

`report` — three PRs open and merge-node-eligible (none self-landed), one proposal captured (landed with this report), the design converged. Pickup instructions at the bottom.

## What landed

- **PR #203 — `loop/heal.py`, the healing fold** (done-line 0114). Read-only, propose-only; senses where the loop's own teeth bit too sharp or stale. Detectors: stale-park (fires today — the field-topology phantom), flapping-gate + owner-override (0-live sensors-before-load). Ambient via `summon`'s heal line. A ts-ordering false-positive was caught by the real log mid-build and fixed.
- **PR #213 — `loop/gate_eval.py`, the value-gate eval** (done-line 0116). bdo's charades frame: matched-variant atoms judged by a panel ("the room"). First live run: `value-gate.claude.v1` bit the no-value case on all three turns including the dressed-up surface_trap (unanimous) and accepted the control — catch-rate 1.00, coverage 2/4. The 3.4% historical refusal rate is a gate fed announce-late work, not a toothless gate. A not-run-vs-soft-gate scorer flaw was exposed by the live run and fixed.
- **PR #219 — the HEAD-intent guard** (done-line 0118). `git.py commit --on <branch>` refuses if live HEAD differs from the branch the session asserts — the structural fix for the branch collision that happened this session. Built in an isolated worktree and dogfooded on its own landing commit. Proposal increment #1.

## The architecture thread (`session-gateway.proposal.md`, landed with this report)

Triggered by a real collision: a session committed onto a parallel session's branch in the shared worktree. Root cause: a git worktree has one HEAD, so "the current branch" is shared mutable global state — the one place ontum's no-shared-state discipline never reached git. The proposal (co-designed with bdo) covers: **insulated-not-isolated** (routes, not severance); **branch belongs to the work, not the mortal session** (bounded by `max_inflight_atoms`); the **session gateway** (`inference.py`'s PEP pattern at the session seam — fold senses on the summon pulse, pen acts at write, git-pen enforces); **folding as a verb** producing a hash-named, composition-typed Fold; **surfaces have fold-capacity** (the setpoints are these); **governance (authority + attribution)** as the spine the fold-physics hangs on; and the **Anthology** — the arc-tier fold that re-derives overlapping arcs into one body of work (the cure for the WIP sprawl this session opened on: 10 confirmed arcs, 5 with zero landings). This work is a **chapter of an Anthology**, not an 11th arc.

## needs-you (verify before acting on any)

- **Land the three PRs** (#203, #213, #219) — the merge-node's, once their arc is confirmed (#219/#203 serve confirmed arcs).
- **The proposal awaits your read** — react to `session-gateway.proposal.md` as a unit, and **name the Anthology** it homes under (re-deriving owner-harness/substrate/inference-gateway/virtual-fleet/the-field).
- **A stray commit** (`bcd6bad`) sits local-only/unpushed on `claude/causality-experience` from the collision — low-harm (origin is clean; identical content if it ever double-lands). Left for that session/the gardener; not safe to rewrite an active branch.

## Pickup — how to resume

- **Robust (the loop hands it out):** atomize proposal increment #2 (the claim↔workspace binding) as an announced atom; then any session that blinks in is handed "build the binding" by gaps/summon, with full context from memory and the proposal. You don't pick it up — the loop does. *Not yet done — the next move on your go.*
- **Manual (works today):** open a session and say "continue the session-gateway work / build increment #2." Memory auto-loads the thread; `session-gateway.proposal.md` §11 is the ordered increment list (#2 binding → #3 gateway fold → #4 provisioning pen + reclaim → #5 typed-fold algebra); §12b records the closed forks.
