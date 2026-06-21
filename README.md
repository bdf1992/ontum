# Ontum

**Ontum is a governed gateway for autonomous AI work — a controlled layer
between what a person wants and the sprawl of their digital life (email,
files, repos, accounts, calendars), where AI can carry out whole initiatives
on their behalf without losing track of where facts came from, overstepping
what it is allowed to do, or dissolving into chat no one can replay.**

Most AI is trapped in one session: it answers, forgets, and grades its own
work. Ontum gives AI a *lawful body* to act through — durable files instead
of fading memory, an independent check on every claim, an append-only record
you can replay, and one owner who steers by approving directions. You stop
governing **prompts** and start governing **initiatives**.

The aim is to **raise the floor and remove the ceiling**: anyone who can hold
a conversation should be able to deal with the digital world more safely, and
the same system should scale up to serious AI-native work.
**→ [Read the full idea](docs/culture/the-idea.md).**

---

This repository is the **engine** that makes that possible — the durable,
checkable substrate the gateway is built on. Its working idea: **the files
are the environment, the agent is a temporary process, and the records are
the memory.** Work moves through a versioned, file-defined environment;
sessions come and go; the files stay.

The repo runs as an **owner-and-engineering loop**: **bdo** (PM, owner, the
last stop) and an engineering family — **Claude**, and Codex as an admitted
*guest engineer* (working to [AGENTS.md](AGENTS.md)). The party that engineers
can vary; the owner does not.

## Where things live

| Path | What it is |
|---|---|
| `ai-native-loop-substrate.md` | **The doctrine.** The working harness: decisions, invariants, seams, the build rule. Start here. |
| `loop/` | The loop substrate — pure stdlib. The fold (`reconcile`), ambient control (`orchestrate`), the one pen for verdicts (`node`), the summons (`summon`), reflection onto external surfaces (`reflect`), the owner inbox (`web`), the part census (`census`), the owner digest (`digest`), the merge-node's land-readiness eyes (`merge`), and the folds the loop runs on itself — gaps, retro, pressure, energy, impact, the slow loop (`slowloop`/`disposer`), and more. |
| `causality/` | The Causality surface (epic.causality-surface, served live): the term-economy witness (`term_economy.py`, a read-only fold that classifies ontum's own vocabulary against committed bytes) and the agnostic graph canvas (`canvas.html`). A projection, never a second source of truth. |
| `outcomes/` | Durable desired-realities carried across mortal sessions — the desired-reality pole of the outcome-pressure fold (`loop/pressure.py`). Each outcome is an evidence-bearing probe-set the fold reads met/partial/unmet; aspiration is refused at the door. |
| `.ai-native/` | The loop's own ground: `log/` (the append-only truth), `atoms/` (units of work, identity = content hash), `nodes/` (versioned node prompts), `epics/` (the arcs), `done/` (done-lines, written before code), `reports/` (session reports). |
| `fence/` | The family-neutral fence registry (done-line 0027): one home for the firm denials every engineering family meets; each harness (Claude, Codex) renders the rules into its native enforcement shape. |
| `pivot/` | The recoverability instrument (epic.pivot): does deliberately-hidden structure, encoded as a placement on the glyph cube, survive recovery by model inference — and how much? A deterministic harness, cold-agent inference, a calibrated random↔ceiling scale. |
| `glyphs/` | Phase-2 semiotics: `knoll.py` derives the glyph systems from the read-only vault into `registry.json`, `knolling.md`, and a 3D `viewer.html`. Generated outputs are never hand-edited. |
| `language/` | Ontum as a language surface — the four strata (syntax, semantics, semiotics, pragmatics) and the surveyed creole artifacts (`basin.md`, `s-frame-placements.json`). Pins cite the vault; marks are proposed, not minted. |
| `exports/` | The envoy surface: sealed ≤10-file packages sent out for review by other model families, each receipted on a committed disclosure ledger. |
| `.claude/` | The harness config-as-code: hook wiring (`settings.json`), guards (`hooks/`), and versioned rituals (`skills/` — start with [branch-ritual](.claude/skills/branch-ritual/SKILL.md)). |
| `tests/` | Tests against the done-lines: goals reached over passes; SIGKILL mid-run loses nothing; cache replayed from log is byte-identical; locally-fine atoms can refuse to fit. |
| `docs/culture/` | The authored telling of the goal — `the-idea.md`, the complete narrative of what Ontum is and why this loop exists to build it (the home the doctrine points to). A synthesis of the record, never a second source of truth. |
| `docs/phase-2/`, `docs/sources/` | **Read-only context** (not material): the wider system the loop exists to build, and external inspiration. |

## Quickstart

The loop is stdlib-first — nothing to install today. Run everything from the repo root.

```sh
# the fold over the log
python loop/reconcile.py --status          # read-only summary
python loop/reconcile.py --until-done       # reconcile passes until done or stuck

# the ambient loop and the pen
python -m loop.orchestrate --status         # field state: pressure vs setpoint
python -m loop.node inbox                    # the owner's open items
python -m loop.node arcs                     # the arcs and which are confirmed
python -m loop.summon                        # open summons (read-only)
python -m loop.census                        # which parts carry weight, which are dormant
python -m loop.digest --today                # the owner's daily arc-first digest
python -m loop.merge                         # per-arc land-readiness (read-only)

# the tests
python -m unittest discover -s tests -v
```

Gotcha: only `reconcile.py` runs as a plain script. `orchestrate`, `node`,
`summon`, `reflect`, `web`, `census`, `digest`, `merge` import from the `loop`
package and run as modules (`python -m loop.<name>`).

Every invocation ends with a clear result on stdout: `done` | `report` |
`needs-you`. Treat `needs-you` as an escalation to surface, not an error to
code around. The log is truth; `queues/` and `offsets/` are a cache — a pure
fold over `log/` — deletable and rebuilt at any time (`--rebuild-cache-only`).

## How the loop works (the short version)

- **The log is truth; everything else is a fold.** `.ai-native/log/` holds
  three append-only JSONL files. The state of any atom is computed by folding
  over them — nothing keeps authoritative state in memory. Appends are
  line-atomic with torn-tail tolerance, which is what makes a hard kill mid-run
  safe.
- **Identity is content hash.** An atom's pipeline identity is the `sha256` of
  its file bytes; editing the file starts a new version from scratch while old
  receipts stand as history. Re-runs never double-act.
- **Stages become real one at a time.** The pipeline (value gate → owner stamp
  → placement → handoff → confirm) starts as mocks with fixed verdicts. A stage
  becomes real via an admission read from the log at runtime, never a code
  literal — and once real, the loop *parks* the atom and waits for the summoned
  node to write its verdict through the one pen.
- **The owner steers arcs, not tickets.** bdo confirms an *arc* once
  (`loop.node confirm-arc`), and the loop then carries every piece under that
  epic — escalating to him only a gate's refusal or the arc's completion. The
  merge-node lands those confirmed pieces on `main`; bdo no longer operates the
  merge.

## Status

The skeleton is built and the substrate is real and running. All five pipeline
gates (value, owner stamp, placement, handoff, confirm) judge for real and have
each refused a piece on `main` — mock temperature 0/5 (done-line 0047) — the
discipline that got there was no second real node until the first had a passing
receipt. Around
the core, the ambient control loop, the summons, the one pen, reflection onto
GitHub Issues, the served owner inbox, arc confirmation, the merge-node (the
hand that lands confirmed-arc work so bdo steps out of the merge seat), the
part census, the owner digest, the family-neutral fence, the glyph knoller and
3D viewer, the language strata, the envoy export surface, and the pivot
recoverability instrument all exist.

Direction lives in `.ai-native/epics/` — eighteen arcs (seventeen confirmed),
each with a horizon for what done looks like at epic scale
(`python -m loop.node arcs`); the complete telling of where they point is
[docs/culture/the-idea.md](docs/culture/the-idea.md). Among them: the substrate
trustworthy enough to point disposable sessions at, the experience layer and the
virtual fleet where agents launch, judge, and staff themselves, the owner
harness and the environments arc that keep one stamp as leverage from any
device, the Causality and diagram surfaces that make the system communicable
without a second truth, the inference gateway, the field, the strategy organs for
lawful pre-evidence motion, the ontabet language harness with machine-verified
laws, and the pivot instrument measuring how much structure an encoding carries.

## Working method

This repo runs on a specific discipline — done-lines before code, receipts
before version bumps, read-only zones that stay read-only, and the owner steers
at arc scale. See [CONTRIBUTING.md](CONTRIBUTING.md) before changing anything.

## License

Copyright © 2026. All rights reserved — see [LICENSE](LICENSE). The repo is
viewable for reference; no reuse rights are granted yet.
