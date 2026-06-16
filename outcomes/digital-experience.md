# Outcome — ontum as the new digital experience

> Arc/epic home: **`epic.digital-experience`** — named by bdo in the working
> session of 2026-06-15 ("I want ontum to be the new digital experience… it's
> like a 20-year goal") and recorded here so sessions inherit it from the record,
> not from chat (his standing rule). Authorization to reach `main` stays bdo's,
> reached through his arc-confirm gesture; this file is the desired-reality pole,
> the epic is the arc, and neither is the other's substitute. Drafted by the
> Claude operator, 2026-06-15.

## Maximal outcome (the horizon)

ontum becomes a person's **control plane to the digital world**. The information
already on a machine is treated as the truth (the log); a skill plus the Pattern
Commons **folds** over it and re-derives that person's world as a **holographic,
evidence-cited knowledge graph** — every node tracing a route back to the byte it
came from. The world is read as a tree of **bounded runs** (a "company" bound, a
"games" bound, an "orchestration" bound — every directory and file able to be
AI-native), each bound carrying its own **declared purpose** (mission / vision /
values), its own **anima** (expected rhythm of engagement), its own **control
surface** and **gestures**. Reality is *folded*; purpose is *declared* and never
inferred. Their tension produces the **agenda** (arcs / epics / stories / tasks /
goals / dones). An **orchestration run** at the root is the only place cross-bound
balance is judged, and only against an allocation the person declared — never a
verdict the machine invents. The system **anticipates**: it pre-stages reversible
surfaces from inferred context autonomously, and gates every irreversible or
outward act behind a gesture. The person declares the *why*; the controller — the
agenda — **assembles itself** from the fold ("control theory without being a
control engineer"). The result: a governed map of one's digital life, so the
person lives in the physical one and worries only about the real.

This is a desired reality across many sessions — a ~20-year horizon. No single
document, audit, or first build completes it. It is carried, not met.

## Why (the desire, in plain terms)

A person's digital life sprawls into tools learned, projects half-built, and
context that lives only in their head. ontum's substrate already runs as a tree
of bounded, composing, AI-native directories with an orchestrator at the root
(this repo is the existence proof). Pointed at any person's data, the same
machinery gives them one world instead of many, one control plane instead of a
hundred skills to tend — and because it is a *fold* over what already exists
(read-only, re-derivable, deletable, local-first by construction), it is a
projection of what is already theirs, not a new secret dossier it accumulates.

## The teeth (why this is sound and not slop)

The loop's fold is byte-deterministic. A fold over a raw machine is **inference**
— probabilistic, format-soup, no provenance baked in. The discipline that keeps
"AI generates your knowledge graph" from becoming confident hallucination is the
one Causality already enforces on the term economy: **every inferred node cites
the byte it came from, or it is a `ghost`.** The inference may be fuzzy; the
citation may not. That citation is also the holographic property — every
projection carries a traceable route to source.

## Probe-set (evidence-bearing; each resolves met / partial / unmet)

**P1 — the sound braid / loop-maker (capability).** A deterministic Plan step
derives the next done-line from the live fold (state → next work) and braids
iterations through the append-only log (the MAPE-K Knowledge base), not session
memory.
- Check: a §10 fixture — given a fixture log/probe-state the maker emits the
  expected next done-line; given a *converged-or-stuck* fixture it refuses to
  advance (returns the stop signal, not a fabricated next step); and after a
  synthetic receipt lands, a re-run's derivation changes accordingly (the braid
  is via the log, provably).
- Evidence: the maker module + passing fixture test in `tests/`.
- Non-example: a pre-scripted queue dressed up as derivation; a maker that always
  emits a next step even when state says converged.
- Today: **unmet**.
- Depends on: nothing. Blessing: pending bdo's arc-confirm to land.

**P2 — cited sensor (capability).** A read-only sensor reads a real data surface
(downloads / file types / headers / metadata) into **citable evidence** —
`path` + header/timestamp substring — never prose.
- Check: run the sensor → evidence records each carrying a resolvable citation;
  a record whose citation points to nothing is refused as a `ghost` (the term
  economy's refusal, reused).
- Evidence: sensor module + sample evidence with resolvable citations + a test
  that an unresolvable citation is a ghost.
- Non-example: a "summary of your files" with no per-claim citation.
- Today: **unmet**.
- Depends on: nothing.

**P3 — bounded-run fold, proposed not minted (capability).** A fold clusters
cited evidence into a **proposed** bounded-run candidate carrying its slots:
declared-purpose, anima/tempo, control-surface — marked `proposed`, never minted.
- Check: fold over sample evidence → ≥1 bounded-run candidate marked `proposed`;
  a candidate with no resolvable backing is refused; purpose/anima slots are
  *declared-input* placeholders, not inferred values.
- Evidence: fold output + test.
- Non-example: the fold writing a `purpose` value it inferred from file metadata
  (the machine telling the person who they are).
- Today: **unmet**.
- Depends on: P2.

**P4 — the reversibility line (capability).** Given a bounded-run candidate, the
system pre-stages a **reversible** control surface autonomously (no gesture) and
**gates every irreversible/outward act** behind a gesture.
- Check: a reversible pre-stage runs with no gesture; an irreversible act is
  blocked by a reversibility/blast-radius classifier (test: reversible passes,
  irreversible is gated with a legible reason).
- Evidence: pre-stager + reversibility classifier (the Risk/blast-radius assay
  grain) + the passing test.
- Non-example: autonomy granted on everything ("don't make me worry" read as
  "act irreversibly without me"); permissions-on-everything that contradicts the
  product's own thesis.
- Today: **unmet**.
- Depends on: P3.

**P5 — adoption (realization; dormant until P1–P4).** A pre-staged surface is
actually **used in preference to the alternative** — a use-trace on the log shows
the guess was adopted, and an ignored guess registers as a miss that bends the
model.
- Check: a use-trace record shows adoption; an ignored pre-stage records a miss.
- Evidence: use-trace records on the log.
- Non-example: counting that a surface was *rendered* as if it were *used*.
- Today: **unmet / dormant**.
- Depends on: P1, P2, P3, P4.

## Milestones (probe groupings across sessions)

- **M1 — the loop braids itself** (P1): the loop-maker + its §10 test. *The first
  done-line lives here.*
- **M2 — the cited fold** (P2, P3): sensor → cited evidence → proposed
  bounded-run candidate.
- **M3 — anticipation, safely** (P4, P5): reversible pre-stage, gated
  irreversible act, graded by adoption — the first whole vertical slice of the
  thesis.

## What remains / continuing pressure

Three standing edges, surfaced in discussion, carried as pressure (not yet
probes, named so they are not lost):

- **Divergence-as-mirror.** Once purpose is declared and reality folded, the
  system can compute where stated values and actual data refuse to fit. It is the
  most powerful and most dangerous feature — a mirror that can judge. It must be
  *shown, never enforced*; the agenda proposes a reconciliation, the person
  confirms or does not. The machine never decides a value diverged "wrongly."
- **Boundary-drawing.** Directories give natural bounds, but a "company" spans
  many folders and a folder can serve two purposes. Resolution is in the grammar:
  the fold *proposes* bounds (D-4 confirms), and a file serving two bounds is
  shared **by reference, not ownership** (location ≠ identity).
- **Self-application.** The thesis is "stop building so many things." If this
  becomes one more platform to tend, it failed its own thesis. The test it must
  keep passing: does it *reduce* the person's surface, or add one? "One agent,
  one skill" is the thesis made structural.

A session never declares this outcome done because one increment landed. It
reduces the gap and leaves the unresolved probes visible as continuing pressure.
