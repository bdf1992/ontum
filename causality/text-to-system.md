# text-to-system — the generative instruction set

> **The instructions that design a system from raw text.** Given a plain phrase
> ("The cat naps"), generate the causal-mechanism mesh — glyphs typed by
> composition, relations connecting them — using *only* the raw text and our
> vocabulary. The seed mesh in `phrases.json` is the **held-out benchmark label**:
> it is the oracle the generation is *scored against*, **never** an input. A node's
> meaning that is read from the seed is a **ghost** (AIM I1/F5) — it claims
> understanding the model never did. This file is the prompt-as-code; the executable
> rendering is `text_to_system.js` (`buildMeshPrompt`), which injects the live
> vocabulary from `canvas-system.js` so the two never drift.
>
> **Version 0.1.0** (§7: a patch is wording; a minor adds a rule; a major changes
> what the generation may emit). Status **PROPOSED** — the use-case fit and the
> calibration band are bdo's to bless. Authored 2026-06-18 for arc.aim, the M2
> inference layer the benchmark was built to grade.

## The one rule (anti-poison)

The generator receives **only**: (1) the raw text, and (2) the vocabulary below.
It never receives the seed mesh, the facets, the relations, the trap, or any prior
context about the phrase. The seed is fetched *separately*, *after* generation,
*only* to score. `buildMeshPrompt` physically cannot be handed the seed — that
separation is the guarantee, not a discipline.

## The task

Design the **causal mechanism** the text describes, as a typed graph:

1. **Find the key words** — the few words that carry the mechanism (not every word).
   Each becomes a **glyph**. Use the word as it appears in the text.
2. **Type each glyph by composition** — assign the **facets** (below) that name what
   the word *does in the mechanism*, not what part of speech it is. A word may carry
   more than one facet (the cat both *acts* and *wants*: `actor + objective`).
3. **Connect with relations** — each relation is a declared composition
   `(fromGlyph.facet → toGlyph.facet, valence)`; the label is **derived**, never
   written. Build the real causal chain **and its feedback**.
4. **Do not collapse the mediator** — if the surface says "the shadow steals its
   warmth," the true mechanism routes through the mediating *state* (shadow blocks
   *warmth*; the fading *warmth* wakes the cat). Recovering the mediator is the work;
   the direct shortcut is the trap a careless reader draws.

## The vocabulary (the only legal pieces)

**Facets** (from `canvas-system.js` `FACET` — the live source):
`actor` (does — initiates), `objective` (wants — a desired state), `source`
(emits — a supply), `sink` (absorbs — a drain), `signal` (marks a change — fires),
`state` (holds — a level), `place` (locates — a where), `action` (transforms —
computes), `memory` (records — a trace), `time` (clocks — marks passing), `gate`
(admits or refuses).

**Relations** — only the composition triples declared in `canvas-system.js`
`RELATION` are legal (e.g. `source|state|+` = "feeds", `state|objective|+` =
"satisfies", `signal|state|-` = "blocks", `state|actor|fades` = "wakes"). The
`valence` is `+` (reinforcing), `-` (opposing), or a named transform (`fades`). **If
no declared triple fits a connection you want to make, that is a gap — leave it out.
Never invent a label or a triple.** (`composeRelation` refuses an undeclared triple;
the harness drops it and the recovery score reflects the miss — an honest gap, the
`grammar_scorer` discipline.)

## Output (schema — the contract)

A single JSON object, no prose, no code fence:

```json
{
  "glyphs":    [ { "word": "cat", "facets": ["actor", "objective"] } ],
  "relations": [ { "from": "sunbeam.source", "to": "warmth.state", "valence": "+" } ]
}
```

- `glyphs[].word` **must appear in the raw text** (verbatim, case-insensitive).
- `glyphs[].facets[]` **must be facet keys above**.
- `relations[].from` / `.to` are `"word.facet"`; the word must be a declared glyph and
  the facet one it carries; the triple `(fromFacet, toFacet, valence)` **must resolve
  in `RELATION`**.

## The teeth (what the harness refuses — `validateMesh`)

A generation is **refused, nothing rendered** (no slop, the `authoring.js` rule) when:
- a glyph word is not in the text (a hallucinated entity);
- a facet is not in `FACET`;
- a relation references a word/facet a glyph does not carry, **or** its triple is not
  declared in `RELATION` (an invented edge).

Refusal is honest output, not failure — a refused edge is a gap the score shows.

## Use-case fit (the system we want)

Not any graph — a **causal mechanism in our vocabulary**: who acts, what they want,
what supplies and what drains, the signal that fires, the state that mediates, the
feedback that closes the loop. Mechanism-**correct** (the cat/shadow chain routes
through warmth, never shadow→cat). This is what "appropriate for our use case" means:
the generation that recovers *this* shape scores well; a fluent-but-wrong reading
(the trap) is penalized.

## How exemplars are created (the benchmark's purpose)

The instructions are **graded, not trusted**:

1. **Generate** a mesh from the raw text alone (these instructions + the vocabulary).
2. **Validate** against the teeth (refuse hallucinations).
3. **Score** the validated mesh against the held-out seed with `recovery_scorer`
   (`facet` f1, `relation` f1, `trap` avoided → `composite`, `reads_mechanism`).
4. **Calibrate** — run across the corpus; the strong generations (high `composite`,
   `reads_mechanism: true`) become the **exemplars** (the calibration band, the
   floor/ceiling). A weak or trap-taking generation is a finding, not an exemplar.

The benchmark shape exists for exactly this: it is the only way to know the
generative instructions *design the system* rather than *parrot the answer*.
