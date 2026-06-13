# Proposal — The Outcome-Pressure Fold

*A substrate proposal: give ontum a way to carry the **tension of an
outcome** across mortal sessions, so a waking session inhabits a world
instead of visiting a repository. Written for bdo to react to, from the
discussion of 2026-06-13. Not adopted — a proposal.*

## The problem, exactly

ontum represents **work** well and **outcomes** poorly. It expresses atoms,
receipts, done-lines, reports, arcs, sessions — every one a unit of work that
*completes*. It has no object for an outcome that **persists while work
completes underneath it**. So every session behaves like a contractor: read
context, pick a task, finish it, leave. The continuity — the pressure, the
unfinished reality, the tensions, the next leverage point — lives in the
owner's head, not in the environment.

This is not a planning-hierarchy gap (Goal vs Session vs Epic). It is a
**pressure** gap. The thing that makes an agent feel it is *inhabiting* a
world rather than *visiting* a repository is waking up already inside the
outcome's tension.

ontum already has the **channel** for this: `loop.summon` fires at
SessionStart and UserPromptSubmit and hands a waking session the single top
pressure point from `loop.gaps`. But the pressure it carries is
**work-hygiene** — mock stages, surface drift, dormant organs. (Every turn of
the discussion that produced this proposal, the hook screamed `loop/census.py
— connected but never exercised — needs attention`: real pressure, wrong
kind.) The channel is right; the content is janitorial. **No fold measures the
gap between current and desired reality, so nothing delivers it at wake.**

## The thesis

> **Outcome Pressure = Fold(Current Reality, Desired Reality)**

A **fold, not a record** — because in ontum the things that persist are folds
(state is a fold over the log; queue-pressure and gap-pressure are folds). A
record would need a session to maintain it, and continuity-by-diligence is
exactly the contractor failure. A fold is un-fakeable and always current: a
session can no more skip inheriting it than skip the mock-shame scream.

And the planning-tier confusion dissolves: **"Goal" is not a new tier — it is
the desired-reality pole of the fold.** Sessions are whatever reduces the gap.

## The dock requirement: desired reality must be evidence-bearing

bdo's condition, and the make-or-break: *if desired reality is aspirational
prose, the fold cannot measure progress and the pressure channel degrades into
narrative.* "Causality becomes an operational knowledge surface" is unfoldable
as prose.

The fix, and it is the spine of the whole proposal:

**Desired reality is expressed as a set of falsifiable PROBES.** A probe is a
predicate that resolves against evidence — **met / partial / unmet** — exactly
the way `causality/term_economy.py` resolves a term's citations against
committed bytes, or the feature-audit checked "does a graph survive reload."
Each probe carries its own check.

The discipline that keeps the channel from rotting, borrowed from the whole
repo's grain:

> **No probe that cannot be checked is admitted.** An aspiration with no
> evidence-resolution path is refused at the door — the same refusal
> `term_economy` makes when it won't mint a term with no evidence, the same
> the done-dir makes when it freezes a bar. Narrative literally cannot enter
> the desired-reality set, because a thing the fold can't check is not a probe.

This makes three things one continuous idea:

- a **done-line** is ONE probe, scoped to a session ("when met, stop");
- an **outcome** is a probe-SET, scoped across sessions ("the gap is these
  unmet probes");
- a **horizon / agenda** is *why* the probe-set is worth closing.

Desired reality = the probe-set. Current reality = which probes resolve today
(a fold over evidence). **Pressure = the unmet and partial probes, ranked by
leverage.**

## The object, in ontum's grammar

A fold (`loop/pressure.py`, say), composing per outcome:

- **Inputs:** the outcome's probe-set (authored, each probe carrying its
  check), and evidence (the log, the repo, what is built — read the way
  `gaps.py` / `census.py` read structural evidence; the way a probe's check
  runs).
- **Output:** for each outcome, `{ met[], partial[], unmet[] }`, the **top
  leverage point** (the unmet probe whose closing moves the outcome most), and
  a **trend** (is the gap closing across recent receipts?).
- **Decay is automatic:** a probe flips unmet→met the moment its evidence
  resolves. No session marks anything done; the fold re-derives. Pressure
  falls as reality moves. *This is the inheritance* — the next session sees a
  smaller gap without being told.

## Pressure is composed, and the owner is a source

bdo: *"all of my session starts should also be summons. I am also pressure."*

Pressure is not one outcome's property — it is **composed** across sources,
all riding the one summon channel:

- **outcome-gap** pressure (new: this fold),
- **work-hygiene** pressure (exists: `gaps.py` — mocks, drift, dormancy),
- **owner** pressure (exists in part: the owner-asks fold, done-line 0058 — it
  fired this very session: "2 owner-asks parked on bdo").

The **owner is a first-class pressure source**, two-way:

- *Inbound:* bdo's intent injects desired-reality probes; his open asks and
  pending confirmations are pressure that must be carried across sessions and
  surfaced to agents at wake ("this needs him").
- *Outbound:* his arrival **is** a summons — the digest is his pressure
  delivery; the system hands *him* the leverage that is his (an arc to
  confirm, a probe to bless), the same way it hands an agent the top gap.

So: **Pressure(t) = rank_by_leverage( compose( outcome-gaps, work-gaps,
owner-pressure ) )**, delivered through `loop.summon` to whoever wakes — agent
or owner.

## What a session inherits at wake (the inhabitation)

Today summon hands: *"the next gap is X, the move is Y."* A work-order.

Under this proposal summon hands a **situation**:

> *Outcome: Causality is an operational knowledge surface. Current reality: 2
> of 6 probes met. Top unmet leverage: persistence — a graph does not survive
> reload (evidence: feature-audit; the engine API has no save verb). Trend:
> flat — no receipt moved it in 3 sessions. Next move: the save/load fold.
> Also: bdo has 2 asks parked, and probe P4 awaits his blessing.*

That is the kitchen already hot. The session does not ask "what task?"; it
stands inside *"what is preventing the outcome from existing?"* — because the
fold already answered it.

## Worked example — the Causality outcome

**Desired reality:** *Causality is the operational knowledge surface for
ontum* — expressed as probes, each checkable:

| Probe | Check (evidence) | Today |
|---|---|---|
| P1 · a graph persists across reload | browser drive: add node, reload, it survives | **unmet** (feature-audit proved it wipes) |
| P2 · a node's prompt/backend is editable in-UI | DOM has a config panel; a field change persists to the node | **unmet** (no config panel) |
| P3 · the editable canvas ingests the real ontum log | the canvas loads `loop-log` / searches atoms | **unmet** (only the essay loads it) |
| P4 · ≥5 ontum terms project with resolved evidence | `term_economy.py audit` ≥5 terms, evidence resolves | **met** (3 minted + 2 overloaded) |
| P5 · the projection reproduces byte-for-byte | `tests/test_term_economy` green | **met** |
| P6 · a managing session can search real atoms from the canvas | an API call returns atoms; a Playwright assertion | **unmet** |

- **Current reality (fold):** met {P4, P5}; unmet {P1, P2, P3, P6}. (P4/P5 are
  *met-pending-land* — they live on PR #114, not on main; the fold must
  distinguish "met in evidence" from "met on trunk" — see open question 4.)
- **Pressure:** {P1, P2, P3, P6}, ranked — **P1 (persistence) is top
  leverage**: it flips the whole surface from toy to tool and unblocks P2/P6.
- **Trend:** the last sessions *moved current-reality measurement* but moved no
  probe from unmet→met — an honest signal that they **instrumented, they did
  not build**.

**What this makes of the work already done:** 0060 (term-economy) and the
feature-audit are *not the goal and not waste* — they are the **first probes
and first probe-results** for this outcome. They measured current reality.
P4/P5 are their pass; P1/P2/P3 are their findings. The pressure fold ingests
them. The audits were early, hand-built instruments of the very fold this
proposal formalizes.

## Open questions (for bdo)

1. **Probe admission.** A probe is desired-reality. Who admits one —
   owner-only (like an arc confirmation), or session-proposes / owner-blesses
   (like everything else)? *My lean:* a session may *propose* a probe (it must
   carry a check, or it is refused), and the owner *blesses* it into the
   outcome — desired reality can't be quietly rewritten, but instruments can be
   proposed from the floor.
2. **Leverage ranking.** Top-leverage by what — hand-ranked priority,
   dependency (P1 unblocks P2/P6), or cheap-win-first? *My lean:*
   dependency-first with an owner override.
3. **First build scope.** Smallest real version: ONE outcome (Causality), its
   probe-set, a `loop/pressure.py` fold that resolves probes + ranks leverage +
   reads trend, and one new summon line that delivers the top unmet probe. Does
   that become an epic with a done-line series?
4. **Met-on-evidence vs met-on-trunk.** Should pressure count built-but-unlanded
   work as met, or only `main`? (The Causality example shows why it matters —
   P4/P5 are "done" only on a branch.)

## What this touches, and what it does not

- **Composes with, does not replace** `gaps.py` and `orchestrate` —
  work-pressure stays; outcome-pressure is added; summon ranks across both.
- **Invents no planning tier** — Goal is the desired-reality pole of the fold.
- **Extends the doctrine's** "state is a fold over the log" to "**outcome-
  pressure is a fold over evidence-versus-intent**." That is the one new
  sentence the doctrine would gain.

---

*Next, if you take it: pick the four open questions, and the first build is a
`loop/pressure.py` over the Causality probe-set with a summon line — the
smallest thing that makes one waking session inherit the outcome's gap instead
of a janitorial nag.*
