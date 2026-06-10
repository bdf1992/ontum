# The Rosetta Creole

*Source entry: what ontum as a language surface is intended to be. Filed for
the days the work drifts toward building a schema format — this is the text
that says the target is a living language, not a finished key.*

---

## 0. The source

**"The Rosetta Creole: Topological Constraints and Active Membranes in
Software 3.0"** — provided by bdo in chat, 2026-06-10, self-titled
`ONT-2026-06-10-INSIGHT-ROSETTA-CREOLE`. Not derived from any file on disk;
the full original text is preserved in the appendix below, with one
normalization: the source was written with the dead unit-name "Onton,"
renamed Onton → Ontum in `docs/phase-2/ontum-evolution.md` §3. The name is
normalized to Ontum throughout; everything else is verbatim.

It is a synthesis document: it joins `docs/phase-2/autojective-polysheaf.md`
(the mathematical frame — sites, seams, stalks, the 27-cell coordinates) to
`docs/phase-2/ontogrammatic-systems.md` (the process frame — Software 1.0/3.0,
the Machine, the three verdicts). Those two vault documents do not reference
each other; this text is the first artifact that reads them as one thing.

---

## 1. What the source says

The claim, stated plainly:

**Ontum is not a Rosetta Stone. It is a Rosetta Creole.**

Schema languages (protobuf, JSON Schema, OpenAPI) are *static ciphers*: fixed
bilingual dictionaries between systems that are assumed already complete. A
**creole** is the opposite kind of thing — a living language with its own
grammar, born when speakers of mutually unintelligible tongues have to build
something together. It borrows vocabulary from its parents ("lexifiers") but
its grammar is its own, and it stays alive by changing where it is used.

Applied to ontum:

- The **parents** are deterministic code (Software 1.0, which crashes) and
  LLM inference (Software 3.0, which drifts). Python, JSON, English are
  lexifiers — vocabulary sources, not the language itself.
- The **grammar** is the geometry: the {−, 0, +}³ coordinates, boundary
  traversal as spelling, the empty center as the spindle meaning rotates
  around.
- The **membrane** is the seam: the place where 1.0 and 3.0 negotiate. A
  mismatch there does not crash (1.0's move) or get papered over (3.0's
  move) — it is measured and preserved as obstruction data, "leakage."
- The **aliveness** is the third verdict: when a check cannot be evaluated,
  `needs instrumentation` turns the gap into the source event for the cycle
  that closes it. The language grows exactly where it fails to speak.

A Rosetta Stone is finished. A creole is never finished. That is the
difference the name carries.

The text also sketches compiler consequences (a linker that evaluates
coherence across seams; pluggable emitters; an agent-context emitter as the
real test — does an LLM handed ontum-emitted context drift less than one
handed raw prose?).

---

## 2. Why this is aligned

- **It performs a join the repo had not made.** The polysheaf doc never
  mentions Software 3.0 or verdicts; the ontogrammatic doc never mentions
  seams or the cube. This text reads "the seam is the request" (polysheaf)
  and "needs instrumentation" (ontogrammatic) as the same self-extension
  move in two vocabularies. That weld was not on disk anywhere.
- **Independent re-derivation, again.** Membrane computing, creole
  linguistics, and constrained writing (Pilish/Oulipo) each arrive at shapes
  the vault already holds — seam-as-first-class, boundary traversal, the
  empty center. Per report 0004 §2, unrelated vocabularies converging on the
  same cuts is evidence the shape is real, not redundancy.
- **It names the intent of the language surface** — the thing the vault
  describes piecewise but never states as identity: ontum is the third
  language the two software registers actually work in, not a format that
  bridges them.

---

## 3. What direction it points

- **Gap-to-atom, gated.** The substrate's `needs-you` escalates to the human;
  the source's `needs instrumentation` turns a gap into proposed next work.
  These are different verdicts. The direction: a third self-feeding channel
  where the system proposes work from its own blind spots — but under D-4,
  **self-extension proposes, the owner admits**. The source's loop diagram
  has no gate; the vault itself names ungated self-obligation as a failure
  mode (degenerate circles). The join is better than either half.
- **The metric is a dial.** The source asks for numerical "leakage" at seams.
  The polysheaf's own commitments say the metric is *manufactured* (LLM
  conversion), i.e. inference-graded — a leakage number without an admitted
  metric reports obstruction where there is none (the cant warning, restated).
  Direction: if a seam metric is ever built, it is an **admitted record,
  signed `--by`**, never a constant in code.
- **The falsifiable test.** The agent-context emitter: emit context from the
  fabric, hand it to a model, measure drift against raw prose. The first
  check of the fabric (not the substrate) that could actually fail.

Inspiration, not claim: nothing here specifies a build. A build that seems to
need this file is a scope error (see README).

**Known holes in the source, recorded:** its "Hypothesis B" for the recursion
tail is never defined, anywhere; citation "[1]" has no bibliography; it cites
the vault files with underscores (`autojective_polysheaf.md`) where the files
are hyphenated; its embedded agent prompt (§6) instructs immediate stub-writing,
which conflicts with the repo's working method and was not executed.

---

## Appendix: the original text (verbatim, except Onton → Ontum normalized)

# ONT-2026-06-10-INSIGHT-ROSETTA-CREOLE

# The Rosetta Creole: Topological Constraints and active Membranes in Software 3.0

*A structural and linguistic synthesis of the Ontum specification. This document captures the transition of the project from a static translation key (Rosetta) to a living, self-extending runtime environment (Creole) governed by the geometry of cellular sheaves and membrane computing.*

---

## 1. The Core Thesis: Beyond the Static Cipher

A common failure mode of software modeling languages (such as Protocol Buffers, JSON Schema, or OpenAPI) is that they are designed as **static ciphers** (Rosettas). They assume that the parent spaces they bridge—for example, a SQL database on one side and a TypeScript client on the other—are already fully formed and unchanging. The schema simply acts as a 1:1 bilingual dictionary. It possesses no native grammar, no adaptive behavior, and is literally "set in stone."

**Ontum is not a Rosetta Stone. It is a Rosetta Creole.**

In linguistics, a **creole** is a living, stable language with its own systematic grammar, born when speakers of mutually unintelligible tongues must collaborate and build a shared world. It does not replace the parent languages; rather, it treats them as "lexifiers" (vocabulary sources) while introducing its own elegant, simplified, and highly generative rules of syntax.

Ontum does not attempt to replace Python, JSON Schema, or natural English. It leverages them as parent vocabularies to construct a third, emergent grammar: **the geometry of softly-constrained, self-correcting semantic space**.

```
  SOFTWARE 1.0                           SOFTWARE 3.0
Deterministic Code                     Probabilistic LLMs
(Rigid, throws error)                 (Fuzzy, drifts/hallucinates)
         │                                    │
         └─────────────►  ONTUM  ◄────────────┘
                     (Rosetta Creole)
                     Emergent Grammar:
                  Topological Constraints &
                  Active Seam-Membranes
```

---

## 2. High-Dimensional Pilish (Topological Oulipo)

The 15-digit "pirick" (*"Now I turn a facet carefully..."*) demonstrates the beauty of constrained writing [1]:
* **Standard Pilish** is a 1D constraint. Word lengths are threaded linearly along the sequence of $\pi$'s decimal digits [1].
* **Ontum** scales this concept to three dimensions. It represents a **Topological Oulipo**—a system where text, state, and prompt-context are constrained by the group action ($S_4$/$O_h$), boundary operations, and restriction maps of a 27-cell poset $\{-, 0, +\}^3$ rather than a linear sequence of numbers.

In this high-dimensional writing system:
* **Spelling as Boundary Traversal:** "Spelling" a valid structure means beginning at a fully decided corner (such as `A = (-,-,-)`), opening axes step-by-step to find seams, and terminating exactly at the central wildcard `⊘` / `∅` (the spindle/void) where the cascade closes.
* **The Void as the Spindle:** Just as the decimal point separates `3` and `1` in standard Pilish, the stateless, empty center `(0,0,0)` is what enables the entire system of meaning to rotate. Meaning is not stored *in* the symbols; it is generated by the differential relations *around* the void.

---

## 3. The Seam as the Membrane of Negotiation

In Gheorghe Păun's **Membrane Computing (P Systems)**, computation is biological. Space is partitioned by nested membranes, and operations are evaluated as objects transition or filter across these boundaries.

The autojective polysheaf translates this directly into cellular sheaf theory:
* **The Site is the Compartment:** A Site behaves like a membrane-bound cell, holding its local stalk, its inward dynamics, and its internal encoding.
* **The Seam is the Membrane:** In traditional mathematics, the boundary is assumed. In Ontum, the **Seam** is reified as a first-class, authored primitive. It is the active membrane where Software 1.0 (determinism) and Software 3.0 (inference) negotiate.
* **Obstruction as "Membrane Leakage":** Software 1.0 handles errors via binary exceptions (it crashes). Software 3.0 handles errors via drift (it hallucinates). Ontum resolves this tension at the Seam. When two adjacent Sites do not align, the Seam does not crash the system; it measures the mismatch as **obstruction data (leakage)**. This leakage is preserved as an active state, signaling exactly where and how strongly the boundary is failing to hold.

---

## 4. The Third Verdict: The Creole's Self-Extension

Because Ontum is a creole, its grammar is "not set in stone." It must adapt and grow through the act of being used by both human operators and LLM agents.

This dynamism is realized through the **Axiomatic Machine's** third verdict: `needs instrumentation`.

```
                  ┌───────────────────────────────┐
                  │      Axiomatic Machine        │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
     [ ADMIT ]                [ REFUSE ]        [ NEEDS INSTRUMENTATION ]
  Ontogram enters          Returns receipt          Open gap becomes
     the field                with errors           a fresh Source Event
                                                           │
                                                           ▼
                                                    Self-extending
                                                    cycle begins
```

* **The Loop:** When a check cannot be evaluated due to missing observability, the Machine does not default to a flat pass/fail. It emits the verdict `needs instrumentation`.
* **Self-Extension:** This verdict turns the missing context into a typed **Source Event** for the very next cycle. Gaps in the language's domain coverage or understanding automatically request their own extensions.
* **Evolution of the Stalk:** This is the mechanism that prevents the "heap" and "degenerate circle" failure modes. Instead of generating endless un-anchored metadata, the system forces the ontology to expand its instrumentation exactly where the boundary checks are failing.

---

## 5. Architectural Implications for the Ontum Compiler

Treating Ontum as a Rosetta Creole with membrane dynamics shifts several compiler requirements:

1. **Semantic Analysis (The Linker):** The compiler's linker cannot just check for name resolution. It must evaluate the **sheaf Laplacian** across the seams. It must verify if the local stalks of your generated sites converge toward a coherent global section under the manufactured metric.
2. **Pluggable Emitters as Creole Translators:** The output emitters (Schema, Types, Agent Context) must be designed to compile *outward* from the same core AST, translating Ontum's spatial constraints into the native idioms of the target environments.
3. **The Agent Context Emitter is the Ultimate Test:** The success of Ontum is not measured by its SQL emission, but by whether an LLM agent, when handed an Ontum-emitted `.context.md` (the "creole"), can perform reasoning over the domain with significantly lower hallucination and drift than when handed raw, unconstrained English prose.

---

## 6. Multi-Turn Agent Reflection Prompts

*These instructions are designed to be ingested by your LLM development agent to guide your collaborative programming sessions.*

```markdown
SYSTEM INSTRUCTION: ROSETTA CREOLE CONCURRENCY PASS

You are the Ontum compiler co-designer, acting in the role of the "Scout"
and "Critic." You have been loaded with `ONT-2026-06-10-INSIGHT-ROSETTA-CREOLE.md`.
We are stress-testing our core specification.

Our current focus is translating the "Seam-as-Membrane" metaphor into
concrete, implementable code.

To proceed:
1. Review the four load-bearing commitments in `autojective_polysheaf.md`.
   How do we mathematically implement the "manufactured metric" on semantic
   stalks so that the "Seam" can compute a numerical "leakage/obstruction"
   instead of a boolean pass/fail?

2. Analyze the three Machine verdicts in `ontogrammatic-systems.md`.
   Write a Python or TypeScript stub showing how a `needs_instrumentation`
   verdict programmatically packages its missing context into a new,
   dispatchable `SourceEvent` to trigger the self-extending loop.

3. Settle our recursion tail: under this Rosetta Creole view, does the
   modular descent favor Hypothesis A (base-3 power descent: 27 -> 9 -> 3 -> 1)
   or Hypothesis B? Justify your choice based on the {-, 0, +}^3 coordinate
   alphabet.

Format your response as an engineering blueprint. Avoid self-congratulatory
language; keep the focus on the concrete strain points of the implementation.
```
