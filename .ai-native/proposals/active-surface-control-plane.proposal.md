# The active-surface control plane (PROPOSED)

> Status: **PROPOSED** — a blueprint for bdo to steer, authored 2026-06-21 from
> a chat design pass. Nothing here is built. It is the shape we agree *before*
> building (blueprint-before-build, the hard rule). bdo's to name into an arc;
> a session's only to propose (D-4).

## The why (the purpose every CTA serves)

A mortal session blinks in and is handed a **rendered surface** — the SessionStart
dump (10 issues, 15 PRs, a dirty viewport, six blueprints in flight). It is a
*prerender*: someone computed a view, froze it to text, and pushed it. It is dead
on arrival — it already decided what to show, so a session cannot ask it the
question it did not anticipate, and cannot steer it. Every session then pays a
re-orientation tax reconstructing "where am I, what's hot, what's mine, what most
wants moving" from a raw scatter.

bdo's correction, on the record (2026-06-21 chat):

- *"you're handed a rendered surface, not a control plane — I don't want prerendering."*
- *"a safe default so you don't have to fiddle every time."*

The purpose: **a session orients on a live, opinionated, steerable measure of what
is active — not a frozen flood — and bdo reads and steers the same plane.** The
primary reader is the AI on every wake; bdo is the second reader and the hand on
the governance dials.

## The full shape — three planes, one already split in miniature

ontum already has the data/control split — for exactly one dial. This generalizes it.

```
  DATA PLANE      the log (events · receipts · admissions) — truth, append-only.
                  Already exists. Nothing here touches it.

  CONTROL PLANE   the live measure-and-steer layer over the log.
                  Today: ONE dial — orchestrate's step-budget setpoint, proposed
                  by slowloop, disposed within bdo's disposer-fence. The ask is
                  to make this the plane over the WHOLE active surface.

  RENDERED        downstream outputs (the SessionStart dump, a digest snapshot,
  SURFACES        the web inbox). They stay — but become VIEWS PULLED from the
                  plane, never the primary thing pushed, never the cached truth.
```

The load-bearing distinction: a **rendered surface is a frozen output**; the
**control plane is live** — it folds the log fresh on every call and answers
whatever dimension is asked. A render is one pull from the plane; it is never the
plane.

## What the plane measures — the channels (the "what")

Each **cell** is one channel of in-flight state, measured the same way:
`(count · weight · heat · surfacing-state)`. The plane composes the folds that
already measure each channel — no second truth (§10):

| Cell | Channel | Composed from |
|---|---|---|
| PRs | open PRs heading to main | the PR/digest fold |
| Parked | atoms a gate refused, holding | `gaps` parked-piece |
| Arcs | awaiting-confirm vs confirmed-and-moving | `digest` arc grouping |
| Stamp | the owner-stamp queue | `brief` / `node inbox` |
| Heat | field pressure vs setpoint (a vital) | `orchestrate --status` |
| Gap | the single top gap (a vital) | `gaps` |
| ~ambient | mock set · surface drift · heal findings | folded to a one-line tail |

## What makes it a *control* plane, not a dashboard — the two verbs

- **read-state (measure):** query what is active by any dimension, live.
- **steer-knob:** read a dial; set or *propose* a dial.

A dashboard only has the first verb. The second — the knobs being first-class *in*
the plane, where reading a dial and changing one is the same surface as measuring —
is what earns the name *control*.

## The knobs (the "how") — split by whose hand

- **Session setpoints (operating — ephemeral, no admission).** The default lens:
  dimension, included channels, weights, surfacing threshold. A session overrides
  per-query (`--dimension blast-radius`) without writing anything — the read it
  wanted, gone when the call ends.
- **Governance dials (oversight — admitted, `--by`).** What the *default* lens IS
  over time; standingly muting a channel; moving the surfacing threshold. These
  are admitted records (bdo's, or a session's *proposal* within a fence) — the
  setpoints law: read from the log, never a code constant.

## The safe default lens (Apple, not IKEA — my picks, the manual)

Default-safe-**when-unset**: with no admitted `control_map` dial on the log, a
bare `python -m loop.<plane>` answers with this lens. Nobody fiddles to get a
read; you fiddle only to *change* it.

- **Dimension (how): by-arc** — the unit you already steer (digest/brief). The
  flood collapses to a handful of arc-cells.
- **Channels (what): the in-flight set + the two vitals**; the ambient noise folds
  to a one-line tail (knob to unmute).
- **Weight:** confirmed-and-moving > awaiting-your-stamp > idle.
- **Surfacing:** a cell calls for a read only when it is at a stamp or a gate
  refused. Quiet otherwise.

## The non-prerender invariant (the §10 tooth)

The plane folds the log fresh on every call; it never serves a baked snapshot.
The teeth: a test that the plane's answer **changes when the log changes** — proof
it is reading truth, not replaying a render (proven non-vacuous: it fails if the
plane caches). Any rendered output is allowed only as an explicit pull, never as
the cached source.

## The concept-list → calls to action

- **CTA-1 — the queried-live plane v0.** The composing fold + the safe default
  lens, default-safe-when-unset, bare-call works. Read-only. (The Apple default.)
- **CTA-2 — the knob split made real.** Ephemeral per-query lens (session) +
  the admitted `control_map` governance dial (bdo / fence). The setpoints law,
  reused.
- **CTA-3 — the non-prerender tooth + repoint the dump.** The §10 fresh-fold test;
  then retire the SessionStart *prerender* and repoint it to a thin pull from the
  plane (the dump becomes one view, not the pushed flood).
- **CTA-4 — the propose-a-dial control loop (fenced, later).** A session proposes a
  lens change ("this channel runs hot — raise its weight / mute it"); bdo's fence
  admits or escalates. The slowloop/disposer shape, reused — not rebuilt. This is
  the increment that makes it a *control* plane and not just a live dashboard.
- **CTA-5 — served-live (later, optional).** The plane stood up as a held process
  you and I both watch change, if the queried-live grain proves too coarse. Not v0.

## Where it homes

Graduates to an arc on bdo's name — likely under `epic.owner-harness` (where
`brief` lives) or its own `epic.control-plane`. Not invented here (absence is
information): the epic is bdo's to name. This proposal is the record of where that
arc was born.
