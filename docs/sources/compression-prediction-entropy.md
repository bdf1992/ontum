# Compression, Prediction, Entropy

*Source entry: the information-theoretic spine under the glyph-field direction.
Filed for the days we hit a wall or question our sanity — this is the math that
says the wall is climbable.*

---

## 0. The source

**3Blue1Brown — "On 'Compression is intelligence.'"**
<https://www.youtube.com/watch?v=l6DKRf-fAAM>
First of a trilogy on information theory and machine learning. Covers Shannon's
noiseless coding theorem, the definitions of information and entropy as things
you are *forced into* by asking about the limits of compressing language, and
the equivalence between prediction and compression that underlies LLM
pre-training.

The video's claim, stated carefully: not that compression literally *is*
intelligence, but that **the mathematical theory of compression is bizarrely
relevant to artificial intelligence** — prediction and compression are two
sides of the same coin, and cross-entropy loss is the compression objective
wearing a training-loop costume.

---

## 1. What the source establishes

The path is: **probability → information → entropy → compression limit →
language modeling → cross-entropy loss.**

- **Information** of an event with probability *p* is −log₂ *p* — how many
  binary cuts are needed to isolate the event from possibility-space. Unlikely
  messages carry a lot of information; expected messages carry little.
- **Entropy** is the average information per symbol, and (Shannon, 1948) it is
  the hard lower bound on lossless compression. No encoding beats it; encodings
  can get arbitrarily close.
- **Perfect compression looks like random noise.** A perfectly compressed
  stream has no remaining redundancy — every bit is a fair coin flip from the
  receiver's perspective. Completed structure leaves no slack.
- **Prediction ≡ compression.** A system that predicts the next symbol well can
  encode it in few bits, and vice versa. Information of a full message
  decomposes as the *sum* of the information of each symbol *conditioned on its
  context* — the chain rule, made additive by the logarithm.
- **Language forced Shannon past statistics.** Raw n-gram counting breaks down
  on long contexts, so he probed *intelligent models of language* — human
  guessers (famously his wife Betty) treated as black-box predictors. With
  100+ letters of context he estimated English at **~1 bit per character**.
  That figure already lives in this repo: `docs/phase-2/cube-alphabet.md` §1
  cites ~1.1 bits per English-text letter against ~4.7 for a random one. The
  gap between those two numbers *is* the structure of the language.

The historically resonant part: Shannon could not answer "how compressible is
language?" without engaging a notion of intelligence. The question itself
summons a predictor.

---

## 2. Why this is aligned

The translation table, in this project's settled vocabulary:

| Source concept | Project translation |
|---|---|
| Compression | disciplined reduction without losing reconstructive power |
| Prediction | local expectation over the next glyph / event / change |
| Entropy | uncertainty pressure in a region of the field |
| Cross-entropy | mismatch between the system's model and the field's reality |
| Surprise / information | a **seam event** — something worth witnessing |
| Context dependence | why isolated tokens are weak and field-position matters; the local frame of a Site |
| Perfect compression looks random | completed structure has consumed all its redundancy — no slack left to witness |
| Human guessers as language models | nodes as black-box predictors of field continuation |

The core reframe this source licenses:

> **A corpus is not a pile of documents. It is a compressible field of
> expectations.**

A good system does not merely store the field. It learns where the field is
predictable, where it is surprising, where entropy is unresolved, and where new
structure must be **named** (the grip-minting work of
`docs/phase-2/ontum-evolution.md`).

---

## 3. The usable principle

> **Intelligence appears where a system can compress a field by learning its
> generative expectations, then detect meaningful residue where compression
> fails.**

This is the ambient-witness idea with a mathematical spine. The watcher does
not judge every event. It only notices where the local prediction model
breaks — a changed file, a renamed concept, a contradiction, a drifted
invariant, a Seam that does not close. Witness first; judgment later. That is
already the doctrine's ordering — this source says the ordering is not just
hygienic, it is *information-theoretically correct*: surprise is where the
information is.

---

## 4. What it gives the architecture

1. **Field state is modeled as expectation**, not just content.
2. **Changes are measured by information gain**, not diff size.
3. **Seams are high-surprise boundary events**, not arbitrary alerts. The
   polysheaf already says it: a Seam that does not close is where the system's
   most informative content sits. This source supplies the units.
4. **Compression residue becomes a work queue.** Whatever cannot be cleanly
   compressed needs naming, repair, routing, or versioning.
5. **Nodes function as local compressors/predictors**, each bounded to a region
   of the field — the place composes the environment, and the place also
   bounds the prediction problem.
6. **The routing layer surfaces entropy** rather than pretending every change
   deserves equal attention. Backpressure is entropy made operational.

---

## 5. The direction it points: from tokens to glyphs

LLMs run prediction-as-compression over a **1D stream of fungible tokens**.
The direction here is the same objective over a richer substrate:

- **Glyphs and structure instead of tokens.** Per `cube-alphabet.md`, the
  pieces we care about are typed, oriented, and geometrically adjacent —
  cubies, not stickers; (position, value) over a small alphabet, but on a
  structured manifold rather than a line.
- **Self-similar at every scale.** The onta → ontum recursion (many onta at
  scale *k* settle into one ontum at scale *k+1*) means the *same*
  predictor-compressor shape applies at every scale — a metafinite object:
  finite spec, unbounded generated depth. One ontum, many onta — the unit is
  already named like a quantum of context.
- **Navigation, not lookup.** Prediction over this substrate is travel through
  a high-dimensional field along three strata at once: **syntax** (form and
  adjacency), **semiotics** (sign-relations and typed roles), **semantics**
  (meaning and reference). Context is the position; compression is knowing
  where you are well enough that the next glyph costs almost nothing.

The 1-bit-per-character result is the sanity anchor for all of this: language
that *looks* like a 26-symbol free-for-all is, under a good enough model of
context, almost determined. The structure is real, it is enormous, and a
predictor that inhabits the field can cash it in. That is the bet, stated in
Shannon's currency.

---

## 6. The caution

"Compression is intelligence" is evocative but too broad, and the source itself
is careful about it. The safe claim:

> **Compression is not all of intelligence, but compression exposes the
> mathematical spine of prediction, learning, and model quality.**

Ontum is not only compression. It is compression **plus naming, witnessing,
versioning, obligation, topology, and execution surfaces**. This source backs
the predictive/compressive *substrate* — the pressure that helps the system
decide where meaning has become expensive — not the whole system. When the
substrate is healthy, the residue it surfaces is exactly the queue the rest of
the system exists to work.
