# outcomes/ — durable desired realities, carried across sessions

The **desired-reality pole** of the outcome-pressure fold (proposal:
`outcome-pressure-fold.proposal.md`). An *outcome* is a desired reality that
**persists across many sessions** and is **not** completed by any single
session's doc, audit, or partial build. This directory is where an outcome is
held *in full* — its maximal statement, its **evidence-bearing probe-set**,
its milestones, and the pressure that remains — so the system can carry it
across mortal sessions instead of the continuity living in bdo's head.

Distinct from its neighbours:

- `.ai-native/epics/` — **arcs** (strategic frontiers, horizon + pieces).
- `.ai-native/done/` — **session done-lines** (frozen, "when met, stop"). A
  done-line is *one increment toward an outcome*, never the outcome.
- `outcomes/` (here) — the **multi-session outcome** between them: the thing
  many done-lines serve, expressed so a fold can measure progress against it.

## The one hard rule

**Desired reality is evidence-bearing, never aspirational prose.** Every probe
carries a check that resolves **met / partial / unmet** against committed
evidence — the same refusal `causality/term_economy.py` makes (no evidence, no
mint) and `loop/gaps.py` lives by (a finding names its own check). Aspiration
is allowed as the *horizon* line; it is **not** allowed as a probe. A probe
that cannot be checked is refused at the door — otherwise the pressure channel
degrades into narrative (the failure this directory exists to prevent).

## Probe classes (from the proposal)

- **capability** probe — *can the system do X?* Resolves against the
  **artifact** (a test is green, a file exists, a browser shows it works). You
  can build your way to passing it.
- **outcome** probe — *does the system behave as intended?* Resolves against a
  **use-trace on the log** (a session/agent/owner actually used it, in
  preference to the alternative). You cannot build your way to passing it; it
  goes green only when the capability is adopted. Outcome probes stay
  **dormant** until their capability preconditions are met — dependencies
  control nagging.

The three measures the fold reads over a probe-set — **coverage** (do the
probes cover the outcome?), **capability** (can-do probes met), **realization**
(use-trace probes met) — give the phase (**discover / build / realize**) and
the **top leverage move**. Discovery (raising coverage by defining probes) is
real progress, not stalling.

## Form of an outcome file

One markdown file per outcome: **Maximal outcome** (the horizon line),
**Probe-set** (each probe: id, statement, class, check + evidence source,
depends-on, today's state, non-example, owner-blessing), **Milestones**
(probe groupings spanning sessions), and **What remains / continuing
pressure**. The fold (`loop/pressure.py`, when built) reads the probe-set; this
file is its desired-reality input and the human-legible outcome.

A session never declares an outcome done because one increment landed. It
reduces the gap and leaves the unresolved probes **visible** as continuing
outcome-pressure.
