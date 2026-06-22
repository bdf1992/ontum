# Proposal — the corpus-derivation organ (PROPOSED)

**Status:** PROPOSED · owner **bdo** · authored by a session, his to steer
(D-4). Nothing here is minted; the panel *proposes*, the owner disposes.

**What this is.** The blueprint bdo deferred when he chose "run the panel
now" — written *after* the evidence, so it is grounded, not predicted. It
captures one live run of a local SME panel that derived the corpus's own
**primaries** and generated a first **typed ontum**, and it names the
layers above it (skill · fabric · shared experience) as an arc.

**Provenance.** Workflow `wf_22d65bda-585` (the `corpus-derivation-panel`,
9 agents, ~850k tokens, 21 min, 2026-06-21). Input: the sealed envoy
package `exports/ontum-grammar-derivation/` + the live ontum and gallery
corpora. Full result: the task output for `w50m6nu0o`. Two adversarial
critics signed the result (below); citation locations corrected per the
ghost-catcher before landing here.

---

## 1. The purpose (what this serves)

bdo's intent, on the record: *"create a skill capable of creating a
model, defining its primaries, generating over its primaries — all from
model-free consequence mapping through exploration and discovery over a
corpus … a layer of supporting fabric, so AI systems could use it
natively … something capable of supporting a shared experience within
those rule sets through natural language and generative interfaces."*

The purpose is **not** "review this corpus once." It is to build a
reusable capability that derives a generative grammar from any corpus,
plus the fabric that lets AI systems stand on the result natively. The
panel run is the **proof the loop works**, and its shape **is** the
skill's spec.

---

## 2. What the panel derived (the evidence)

### 2.1 The six primaries — the corpus's own RGB

Derived from a consequence map (what *using* each term causes), not
picked. Each is irreducible, generative, and grounded by a distinct §10
refusal-tooth (what breaks if you remove it). gallery (an independent
corpus) converges on five of the six — the cross-system test that says
this is a grammar, not one repo's idiolect.

| primary | what it is | distinct tooth | evidence |
|---|---|---|---|
| **APPEND** | the one irreversible write — how a fact is laid down | a torn tail line is dropped on read ("it never happened") → hard-kill safe | `loop/reconcile.py:81-116`; `gallery/lib/ledger.py:36-57` |
| **FOLD** | state/force is never cached, only re-derived by replay | trusting a cache instead of the fold breaks the design | `loop/reconcile.py:129-165`; `gallery/lib/forces.py` |
| **HASH-IDENTITY** | content *is* identity; idempotence by `(node, hash)` | re-judge of same `(node, hash)` is a permanent no-op; editing bytes mints new identity, detaches receipts | `loop/reconcile.py:231-234,146-150`; `node.py:79-83`; `gallery/lib/ledger.py:31-33` |
| **CITE** | a claim counts only if its citation resolves | a citation naming an absent/empty record is refused as a gap → "no machinery = poetic, not a type" | `loop/consequence_graph.py:114-120,186-194`; `causality classify.py:24-29` |
| **VERDICT** | an independent, bounded judgment at a named seam | the announcer may not judge (D-2); a verdict outside the seam's set is refused | `loop/node.py:104-110` |
| **POSTURE** | governance is itself a superseding record read at runtime | realness / arc-confirm / rung are bdo-only data, never a code literal | `loop/reconcile.py:154-181`; `node.py:97-100` |

**Mixing rule.** Every operational term is an *ordered subset* of the six
along the path a fact travels:
`identity(HASH) → written(APPEND) → read-by(FOLD) → advances-by(VERDICT)
→ right-to-judge-set-by(POSTURE) → admissible-iff(CITE) resolves`.
A term touching fewer primaries is partial/derived; touching none, it is
poetic. Worked: `atom = VERDICT-walk ∘ APPEND(seed) ∘ HASH`;
`gateway/crossing = VERDICT(default-deny) ∘ APPEND(crossing) over
POSTURE(registration)`; `ghost = ¬CITE`; `witness = APPEND made
observable by FOLD` (decomposes → not a primary).

### 2.2 ontum.v0 — the generated typed object

**"A fact travelling a path through the six primaries, observable only as
a FOLD."** Not a schema you fill in: born with a hash identity, never
stored, re-derived each pass.

**Two-triples ruling: SPLIT** — and neither triple is the real 3D taken
whole. The **cube coordinate** (x,y,z ∈ {−,0,+}) is three positional axes
that live only in the read-only vault — *no live record carries one*
(verified directly). The **canvas strata** {fundamental, derived,
learned} is *one* epistemic-depth ladder, not three axes. The object's
real, enforced 3D is the three axes the corpus bites on but never named:

- **known-depth** — `fundamental(address) → derived(fold) → learned(model)`
  (the strata ladder, salvaged; rungs 1-2 enforced, rung 3 declared at
  zero records).
- **advance** — the verdict-walk life position (value gate → owner stamp →
  placement → handoff → confirm → terminal).
- **standing** — the governance posture under which it counts (mock/real,
  arc-confirmed, registered, rung), folded from admissions.

**Field tiers (honest):** `identity · provenance · incidence ·
advance_state · standing · consequence_marks` = **real**;
`known_depth · position · dimension · anima.strength/tempo` = **declared**;
`anima.pulse/rhythm/breath · territory` = **poetic**.

**Generativity (what makes it a model, not a schema):** a *type* is an
ordered subset of the six primaries — a seam-walk; the generative space is
{ordered subsets of the six}. A fact travelling a new path is a new ontum
the system never pre-authored — discovered by replay, not fitted. (This
is the model-free guarantee: every field is a deterministic fold; the one
learning rung is declared, never filled by a fit.)

---

## 3. The critics (both signed)

- **Ghost-catcher: `sound-with-fixes`.** Every primary/axis/field resolves
  against live code; the negative claim (no live cube coordinate) verified
  by hand; "not the prior panel's confabulated-gateway failure." The only
  defects are **citation-precision** (line-drift, two mis-homed quotes) —
  mechanical, corrected above before landing.
- **Stakeholder / D-4: `SERVES` — strongly, no rubber-stamp.** Model-free
  ✓, derived-not-picked ✓ (refused the cube box; the gallery convergence
  is the proof). Fabric layer **PARTIAL**, with one drift named plainly →
  §5.

---

## 4. The arc (four layers) and the concept list

```
4  shared experience   NL + generative interface over the rulesets   (gallery served surface; causality authoring.js)
3  fabric              AI systems stand on the derived model natively (meaning addressable by consequence, not hash)
2  skill               explore → consequence-map → derive → generate → critique  (THIS run, made reusable)
1  panel               one local SME run that derived the grammar     (DONE — the evidence above)
```

**Concepts, categorized:**

- **Method (real, proven once):** consequence-mapping · primary-derivation
  · the mixing rule · the five-stage panel loop · the two-critic gate
  (ghost-catcher + D-4 proxy).
- **Artifacts (real):** the six primaries · `ontum.v0` · the three enforced
  axes · the field-tier split.
- **Declared-ahead-of-data (honest gaps):** `known_depth=learned`
  (`loop/relation_ledger.py`, zero records) · `anima.strength/tempo`.
- **Deferred (named, unbuilt):** the AI-native read path (meaning
  addressable by similarity/consequence — `causality/contracts/relation-organ-admission.md`)
  · the NL→first-ontum authoring door (point `causality/authoring.js` at
  the ontum schema, not a generic graph).

---

## 5. The one open seam to hold (not collapse)

**Unit-of-work vs unit-of-meaning (seam #4).** The generator built the
first ontum *on the work-atom* and tiered the one meaning-bearing rung
declared-at-zero. But bdo's intent is the **fabric** — ontum as a unit of
*meaning* AI systems use natively. The corpus's own seam says "atom"
(work) and "the first ontum" (meaning) may be two types the harness has
been blurring because the harness is all that exists so far. A model-free
reading should **hold this OPEN** until a meaning record is real, rather
than assert "ontum = atom under six primaries."

---

## 6. Calls to action (against the purpose)

1. **CTA-1 — Make the first *meaning-bearing* ontum real** *(recommended
   first; the smallest honest bridge to the fabric layer).* Mint one
   `relation_claim` whose subject is a unit of **meaning** (not a
   work-atom) + its `consequence_receipt`, so `loop/relation_ledger.py`
   reads it PREDICTIVE vs TRIVIAL. Turns `known_depth=learned` from a
   declared rung into one checked record; stays strictly model-free;
   forces seam #4 to produce a real refusal instead of a prose ruling.
2. **CTA-2 — Extract the skill** from the proven loop (explore →
   consequence-map → derive → generate → critique), parameterized by
   corpus + lenses. The panel run is its reference implementation.
3. **CTA-3 — Build the fabric read path** (deferred until CTA-1 has data):
   meaning addressable by consequence/similarity, the relation-organ
   admission.
4. **CTA-4 — Point the NL/generative door** (`causality/authoring.js`) at
   the first-ontum schema (deferred until the center is non-hollow — do
   not build an interface over a declared-at-zero core).

**Recommended sequence:** CTA-1 → CTA-2, with CTA-3/CTA-4 gated on CTA-1
producing data. The premature move the panel warns against: NL/interfaces
over a hollow meaning center.

---

## 7. The §10 test this proposal must pass

Two locally-fine atoms must be able to *refuse to fit* and the organ must
notice. Here: a candidate "primary" with **no resolving machinery** must
be refused (it is poetic, not a primary) — exactly the `CITE` tooth the
panel derived, turned on the derivation itself. The skill (CTA-2) is not
real until it can reject a fabricated primary the way
`causality/term_economy.py` rejects a ghost term.
