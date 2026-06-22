# Exemplar: the production-provenance ladder — freehand as a first-class observation target

> **Status: PROPOSED** · owner **bdo** · 2026-06-22. Logged at bdo's request as an
> **exemplar for studying the repo and mining improvements** — the shape worked out
> in conversation. It captures a lens, a worked example (this session), and a small
> build. Nothing minted (D-4).
>
> **One line:** *how an act was produced* — freehand, generic utensil, branded
> utensil, tool, or workflow — is a first-class observable; the least-governed rungs
> (freehand / handmade) are the richest mining targets, because that is where the
> next instrument wants to be built.

## The seed insight

Free-handing — producing an artifact (a format, a summary, a judgment) ad-hoc, with
no instrument — is not only a failure to delete. It is the **generative frontier**:
the place a new format or tool is first improvised. So instead of forbidding it,
make it **observable**, watch where it recurs and where it fails, harvest the good
improvisations into governed instruments, and name the rest. This is the
Exemplar-Spec gym applied to *how the system produces things*: freehand is the
bounded drift; observation is the grading; promotion up the ladder is the harvest.

## The production-provenance ladder

| rung | what made the act | governed? | observed today? |
|---|---|---|---|
| **freehand / handmade** | prose typed, a format invented | none | **no — invisible (not a command)** |
| **generic utensil** | raw git/gh, an unbranded helper/spawn | watched | yes (`command_guard` watch-log) |
| **branded utensil** | a pen / branded node (`pr.py`, `ontum-node:merge-node.claude.v1`) | pinned §7 prompt + trust rung | yes |
| **tool** | a deterministic fold/script (`loop.gaps`, `term_economy.py`) | reproducible | partial |
| **workflow** | an orchestrated multi-agent run | fully | partial |

`command_guard --report` already splits **generic vs branded** for shell commands and
names *"which wrapper is worth building next."* That is the rung-2→3 promotion signal —
for commands only. The lens widens it: make **production-provenance a first-class
dimension on every act**, and the same "which instrument next" logic falls out for the
whole ladder.

## The mining loop (the improvement engine)

1. **Observe** each act's rung. A freehand act is detectable *structurally*: it cites
   no instrument (the `term_economy` ghost grain — no resolvable backing).
2. **Monitor** (the `activity.py` / `census` grain): **recurrence** (a freehand/generic
   act-shape that keeps happening = a gap pointing at the next instrument) and
   **failure** (a freehand output that drifts from or contradicts the record it claims
   to summarize).
3. **Harvest** (the gym / `epic.strategy` scout→claim→prune): a recurrent *successful*
   freehand is a Claim → a candidate Commons pattern or pen. Instruments grow from
   observed improvisation, not from authoring in a vacuum.
4. **Name** its usage (`activity-accounting`): freehand usage is on the record, never
   silent.

## The format application (where it began)

The conversation started here: read out working artifacts (issues, PRs, commits, the
digest) and derive **formats generated from the Pattern Commons**
(`causality/patterns/pattern-commons.v1.json` — 53 patterns; axes register=commitment
ink/pencil, strata=colour, anima=size/motion), **sized to each artifact's scope**
(`semantic-zoom` / `derived-altitude` + the anima size channel): a commit as a
`ticker-feed` mote, a PR as a `glass-panel` card, the digest as `ambient-telemetry`,
each carrying `backing-bound-topology` (a route home). A **freehanded format is a
format with no Commons-pattern citation** — the same structural detector.

## What it composes (no new engine)

`tags.py` (production = a natural new dimension beside `intent`) · `command_guard
--report` (the rung-2/3 observer already running) · `activity.py` (accounting) · the
Pattern Commons register (ink/pencil) · `retro.py` / `gaps.py` (the mining folds) ·
`epic.strategy` (scout→claim→prune).

## The load-bearing tooth

**Freehand is the one rung nothing watches** — it is not a command, so the watcher
never sees it. Detection must be **structural** (no instrument-citation ⇒ freehand),
not confessional (the producer is un-self-aware by nature). That structural detector
is the genuine new work.

## This session as the worked example (the dogfood)

The rescue-and-landing wave that preceded this capture climbed the ladder visibly:
the **read-outs to bdo were freehand** (rung 1 — hand-built scorecards and
plain-English blocks, re-invented each turn); the **generic Agent spawns were pushed
to branded** by the spawn-guard (rung 2→3); the **merge-node and value-gate ran as
branded nodes** (rung 3); the **lands rode pens and folds** (rung 3–4). The contrast
— *governed where it acted on the trunk, freehand where it spoke to the owner* — is
the first finding this lens would mine.

## Meta-honesty

This exemplar's *content* was authored **freehand** (rung 1 — the appropriate rung for
a captured design shape), but it was **captured and landed through branded utensils**
(the phrasing door, the PR pen, the merge-node). It demonstrates the pattern it
describes: freehand content is fine; un-governed *production into the void* is the
failure — so the improvisation is harvested through the governed seam.

## The first build cut

A `production` dimension in `tags.py` + a read-only fold that classifies each act's
rung and surfaces the freehand/generic **recurrences** as a promotion backlog (the
"which instrument next" signal, generalized from commands to all production). Seed it
on this session's own acts.

## Knobs for bdo

1. Are the ladder's rungs right (freehand / generic / branded / tool / workflow)?
2. Is freehand-detection structural-only, or also self-declared where possible?
3. Graduate to `epic.production-provenance` (with pieces), or hold as a captured lens?
