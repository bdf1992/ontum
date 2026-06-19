# Done-line 0103 — Frame Causality's canvas design system + phrase portfolio

Written before code, per §9.4. When this line is met, stop. Overnight-loop run on
epic.causality-surface; the brief is causality/iterations.md 0001-0005.

The story-demo model is locked (iterations 0001-0004): an NL phrase becomes the
system — text is the skin, important words are glyphs (keyword-importance via
logic/register/learned patterns), each glyph is a holon typed by composition
(facet bundle), a phrase is a mesh in a membrane, paragraphs are networked
membranes; compress-to-enrich (the glyph is the compression, savings reinvested
into relationships). This line frames the *canvas design system* that renders it
and seeds the *phrase portfolio* that feeds it.

> **Done when:** `causality/` carries (1) a **framed canvas design system** — one
> schema-driven source of **tokens + primitives** covering colors, shapes, node
> types, connections, line-types, easing/animation, physics, hover/click/gesture
> interaction, and an **ASCII fallback** — in the established cream/hand-drawn
> look-and-feel, so a new primitive ships as a *spec entry, not new code*;
> documented in a design-system file and pinned by a §10 test that **refuses a
> primitive or phrase token absent from the table** (a fabricated/by-hand
> primitive fails). (2) A **phrase portfolio** — a committed library of at least
> eight cute-but-mechanically-rich phrases, each carrying its glyphs, **facet
> compositions** (type-by-composition), relations, membrane, and cross-membrane
> links, validated by a test that every relation references a **declared facet**
> (no dangling edge) and every highlighted word resolves to a glyph. (3) At least
> **one phrase rendered the full way** on the canvas — sentence skin + highlighted
> glyphs + composed facet sub-nodes + labelled relations + membrane + the **Lens**
> panel (glyph / relation / membrane selection), matching the reference mockup, in
> the deterministic local compiler (no LLM), deployed to the live URL as a
> `claude/*` preview. The full suite green; a numbered report names end-state and
> every `needs-you`.

> **Non-example:** the radial "sentence beside a separate graph" shape (rejected,
> iterations 0003); hardcoding the *illustrative* cat/shadow/warmth chain as if it
> were correct mechanics (bdo flagged it wrong on purpose); an LLM-dependent
> generator that cannot run on the static served site; a primitive added as
> bespoke code instead of a token/spec entry (the agnosticism is the point); a
> phrase whose relation points at an undeclared facet, or a highlighted word with
> no glyph (a dangling skin); inventing a new skin instead of the established
> cream/Fraunces/Caveat/IBM-Plex-Mono system.

> **Arc:** serves the confirmed `epic.causality-surface` (adm.a675cb9d36fb) —
> Causality as the communication surface over a typed system. Realizes
> iterations.md 0001-0005; the welcome→canvas→tools→paint sequence's canvas stage.
