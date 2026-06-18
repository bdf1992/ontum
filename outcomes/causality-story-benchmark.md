# Outcome — Causality's story surface is a self-calibrating benchmark for NL→structure recovery

*Shape co-designed with bdo, 2026-06-17 ("I think I've struck gold — this can be
benchmark-shaped. AKA it's workbuilding"). Design lineage: `causality/iterations.md`
0003-0005 (the story-demo model), `causality/phrases.json` (the corpus), and the
`causality-story-corpus-is-benchmark` memory note. Held in full — decomposed,
never shrunk. "Out of scope for a done-line" does not mean out of scope for this
outcome.*

## Maximal outcome (the horizon line)

> **Causality's story surface is a self-calibrating benchmark: tiny natural-language
> stories are generated from seeds whose latent causal mesh is *known*, and graders
> independent of the generator recover that mesh from the text alone — so the claim
> "natural language is a compressible interface to a working system" (iteration
> 0003) becomes a *measured round-trip score*, not an assertion, and the same
> surface that demos Causality is its own oracle (workbuilding).**

One outcome with two faces that need each other: the **generative surface** (a seed
→ a cute story that *encodes a surface trap*, self-calibrated to sit between a floor
adversary that must fall for the trap and a ceiling reference that must solve it)
and the **grading surface** (text → recovered mesh, scored deterministically,
D-2-independent of whatever authored the story). The rare property that makes it a
benchmark and not a vibes-eval: **the seed mesh is the label** — most reasoning
benchmarks have input/output pairs but no ground-truth latent structure; this has it
by construction.

## Probe-set (evidence-bearing; each carries its own check)

Legend — class: **cap** (capability, resolves against the artifact) · **out**
(outcome, resolves against a use-trace on the log). State as of 2026-06-17.

### The deterministic spine (no inference — proves the grader has teeth)

| Probe | Class | Check / evidence | Depends | Today |
| --- | --- | --- | --- | --- |
| **G1 · the recovery-scorer exists** | cap | `node causality/recovery_scorer.test.js` green: a pure function scores a recovered mesh vs a true mesh (facet-F1 + relation from→to recovery) and flags the trap edge; the §10 test **separates** the mechanism-reading from the grammar-reading of `cat-sunbeam`, and a constant/fabricated scorer fails the separation | — | **unmet** (done-line 0105 builds it) |
| **G2 · phrases carry calibrated traps** | cap | every phrase that has one declares `surface_trap` (type + tempting-but-wrong edge + why); `phrases.test.js` refuses a trap that is a subset of the true mesh (a non-trap) and an undeclared `trap_type`, and requires the trap's endpoints to resolve to real glyphs | — | **unmet** (only `cat-sunbeam` has an implicit trap today; done-line 0105) |

### The generative + grading seam (the agent and inference nodes)

| Probe | Class | Check / evidence | Depends | Today |
| --- | --- | --- | --- | --- |
| **G3 · seed-author proposes a benchmark item** | cap | a `.ai-native/nodes/` inference node returns seed + mesh + `surface_trap` bounded by the `SCHEMA`; `validate()` refuses malformed; a no-trap item is refused at the generation gate | G2 | **unmet** |
| **G4 · skin-author encodes the trap on the surface** | cap | mesh → NL text (deterministic compiler primary; an inference variant allowed offline) whose surface *tempts* the trap; a faithfulness check confirms the true mesh is recoverable by a charitable reader | G2 | **unmet** |
| **B1 · mesh-recovery runs as the subject** | cap | given `text` only, a local mind (qwen/mistral via the gateway) returns a recovered mesh the harness captures and the scorer grades; the subject is *measured*, never trusted | G1 | **unmet** |
| **B2 · items self-calibrate between anchors** | cap | an item enters the corpus only if a **floor** lazy-reader falls for the trap *and* a **ceiling** reference solves it; a test refuses an out-of-band item; bdo stamps the band bounds (his one gesture — confirm-arc shape, D-4) | G1, B1 | **unmet** |

### The benchmark realized (the proof it is real, not merely possible)

| Probe | Class | Check / evidence | Depends | Today |
| --- | --- | --- | --- | --- |
| **OUT1 · the warmth-mediator gap is measured, not asserted** | out | a committed run record shows the scorer separating a mediator-recovering reading from a `shadow→cat` reading on a *live* mind — the discrimination is on the log, not just in a fixture | B1 | **dormant** (activates once B1 lands) |
| **OUT2 · the benchmark grades a model spread** | out | ≥2 model families scored, ranked, reproducible from committed seeds; the scores are a use-trace on the log | B1, B2 | **dormant** |
| **OUT3 · the round-trip evidences the compressibility claim** | out | across the portfolio, ceiling readers recover the mesh above the floor — iteration 0003's "NL is a compressible interface to a working system" carries evidence (the `val_bpb`-on-prose move) | B2 | **unmet** (the whole point) |

**Coverage note (honest):** this set covers the deterministic spine, the generative
+ grading seam, the calibration band, and three realization probes. It is *not*
claimed complete. Named discover-phase work, not yet probes: **the sliders as
controlled perturbation axes** (matched pairs `(seed, seed+Δtwist)` with known
latent deltas — the cheap, grounded version of the spectral/differential-geometry
idea); the **embedding-space differential** itself (whole-book depth — far horizon,
expensive); and an **online-sourced realism axis** (reverse-engineered books test
whether the compiler's prose looks real — useful *only* for realism, never for
recovery scoring, since they carry no ground-truth mesh). Absence here is
information, not omission.

## Milestones (probe groupings that span sessions)

- **M1 · The deterministic spine** — G1 + G2. *The scorer has teeth and the corpus
  carries calibrated traps.* (Done-line 0105 starts and aims to complete this.)
- **M2 · The generative + grading seam** — G3, G4, B1, B2. *Items are generated,
  rendered with their trap, recovered by a measured subject, and self-calibrated
  between floor and ceiling; D-2 independence (generator ≠ grader) enforced by the
  seam.*
- **M3 · The benchmark realized** — OUT1 → OUT3. *Live minds graded; the round-trip
  score evidences the compressibility claim.* (Dormant until M1/M2 unlock it.)

## The node roster M2 builds (the agent + inference design)

Typed by **what is trusted vs what is measured** — the load-bearing distinction:

- **`story-seed-author`** *(inference, bounded)* — proposes seed + true mesh +
  `surface_trap`; the inference-as-composition move (bounded by SCHEMA + a
  trap-type, free in the story). Output passes `validate()` before it is anything.
- **`story-skin-author`** *(deterministic compiler primary; inference variant
  offline)* — mesh → cute NL prose that encodes the trap on the surface.
- **`mesh-recovery`** *(inference — the device under test, NOT trusted)* — text →
  recovered mesh; run per model family; its score is the benchmark output.
- **`recovery-scorer`** *(deterministic code — the spine, G1)* — recovered vs true
  → structural score + the trap boolean; `term_economy.py` grain, §10 teeth.
- **`coherence-judge`** *(inference — quarantined)* — the only fuzzy axis (is the
  story cute/coherent; does the skin realize the mesh). If it carries most of the
  signal, the benchmark has degraded.

The **trap taxonomy** the seed-author generates from (the `trap_type` vocabulary):
*elided-mediator* (A→M→B collapsed to A→B — the canonical `shadow/warmth` case),
*misattributed-agency*, *reversed-causality* (the twists axis), *implicit-prior*,
*decorative-but-load-bearing* (the weirdness axis). The sliders that steer the demo
steer the benchmark's difficulty with known ground-truth deltas — one control
surface, two payoffs.

## First session-sized move (the first done-line)

`.ai-native/done/0105-story-benchmark-scorer.md` builds **M1** — G1 (the scorer +
its §10 separation test) and G2 (calibrated traps on the portfolio). It is
*deterministic on purpose*: it proves the grader can tell mechanism from grammar
before any inference node is written, so the seam (M2) plugs into a spine already
known to have teeth. It is **one increment toward this maximal outcome, not a
replacement** for it.

## What remains after the first move (continuing outcome-pressure)

Everything except M1: the whole seam (G3, G4, B1, B2) and the realized benchmark
(OUT1–OUT3), plus the named discover-phase probes (slider perturbations, the
embedding differential, the realism axis). These are **not "out of scope for the
goal"** — they are the outcome, simply not completed by the first done-line. Once
G1/G2 exist, they are no longer prose bdo holds in his head; they are unresolved
probes the fold surfaces at every wake, ranked by phase and leverage, until they
resolve.

## Owner-blessing

Shape confirmed by bdo, 2026-06-17 ("yeahhh"). Two defaults set on his confirmation:
**band-minting authority** — bdo stamps the calibration *band* once (confirm-arc
shape); in-band items auto-admit, he audits — and **local-subjects-first** — prove
the scorer discriminates on the local minds before widening to cloud families.
Minting an item into the canonical corpus, and the band bounds themselves, stay
bdo's (D-4).
