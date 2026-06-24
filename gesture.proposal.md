# Gesture (PROPOSED — bdo's, 2026-06-20): lift the gesture into a typed, consequence-scaled act

**Status:** PROPOSED. **The definition, naming, and arc are bdo's (D-4); a
session may only propose.** Born from the 2026-06-20 design conversation that
asked "what *is* a gesture, truly?" — alongside the consequence-policy thesis
(`change-management.proposal.md`), the Taster's Clause (D-14), and the ask /
recommend surface discipline. The companion memory is `ontum-gesture-definition`.

## The diagnosis — ontum records the wrong half of a gesture

Every gesture seam has two artifacts:

- the **solicitation** — the material offered to gesture toward;
- the **gesture** — the act back (a stamp, a verdict, a closed issue, a note).

Ontum treats the *gesture* as first-class — `confirm-arc` is an admission, a
verdict is a receipt, an `admit-real` is signed `--by`. The **solicitation is
nowhere**: it lives ad-hoc in whoever happened to ask, in whatever shape they
happened to use. So the response is on the record and the request that earned it
is vapor.

The cost is bdo's, stated in his words: *"everyone asks for a gesture and I just
say something because I want it to happen … the note itself is a gesture I offer,
but it would be better if that authoring was more informational and structured."*
Today the clarity is pushed **into the gesture** — a prose note carrying intent
that someone then has to interpret (this is exactly what `arc-intake` does:
reads bdo's closing comment, judges confirm / decline / **unclear**). That is
lossy, un-foldable, and unscalable.

**The conservation law:** clarity has to live somewhere — either up-front in a
rich solicitation, or after the fact in prose that must be interrogated. It
cannot be absent from both. This proposal pushes the clarity up-front, so the
gesture comes out as **data**, not intent-to-be-interpreted.

## The definition — gesture, three legs

> **A gesture is the typed act by which a peer licenses a consequence.** It is
> not the effect (the bit that flips, the record that appends) — it is the
> *license* for a relational consequence to become true in the environment.

Three legs, each drawn by a non-example below:

1. **Typed.** A gesture is data, not prose to interpret — simple clicks across
   simple tabs, where each tab is a typed dimension and each click sets a typed
   value. The richness lives in the type bound to the work, not in the effort of
   the click; the cheap click yields rich, queryable, **inference-able** data.
2. **Licenses a consequence, to a peer, as a real choice.** A gesture lets
   something *become* (relational consequence); it is not the action that *does*
   the work (local effect). It is received by a peer — never self-cast — and it
   must be genuinely free (it could have gone the other way).
3. **A misunderstanding surfaces — it never hides.** An untypeable or
   underspecified gesture raises an *open interrogation*: the receiver takes
   note, replies with how it read the gesture, and asks — it is never buried
   behind a silent interpretation or a quiet workaround. (Already the law in
   `arc-intake`: "reply with how I read you, never land on a guess.")

## The grip set — examples and non-examples

Read as: act · local effect · relational consequence · obligation discharged.

| gesture | effect (local) | consequence (relational) | obligation discharged |
|---|---|---|---|
| `confirm-arc --by bdo` | a confirm admission appends | the arc's pieces may cross the owner-stamp gate → work may **become main** | the owner-authorization landing raises |
| value-gate verdict `{confirmed\|missed}` | a receipt appends | the atom advances, or parks | the second-set-of-eyes D-2 raises |
| `admit-real --by bdo` | a `node_real` admission appends | a stage stops mocking → a kind of meaning **becomes sensed** | the trust realness raises |
| `admit-fence --by bdo` | a fence admission appends | the disposer may self-admit in-fence dial moves **without bdo** | the standing-authorization auto-disposition raises |
| an AskUserQuestion click | a typed selection records | the session's next move is licensed down a route | the fork-resolution a real fork raises |

Non-examples, each drawing one edge:

- **"I want this to happen" — untyped prose.** Licenses no *specific*
  consequence; nothing folds; "unclear" can't be machine-checked. → A
  **pre-gesture**: raw material that still needs typing.
- **The merge-node running `git merge`.** Real effect (main moves) but licenses
  nothing new — it *executes* a consequence `confirm-arc` already licensed. →
  *An action carries an effect; a gesture licenses — action ≠ gesture.*
- **A mock stage's constant verdict.** Couldn't have gone the other way. → *No
  degree of freedom = no gesture* (the §10 rubber-stamp test).
- **A node judging its own announcement** (D-2 refuses it). → *Received by a
  peer, never self-cast.*
- **The orchestrator cooling at queue-cap.** Real consequence, no author, no
  choice — a fold reacting to a setpoint. → *A gesture has an author who could
  have chosen otherwise.*

## The architecture — a closed loop, self-similar with the rest of the substrate

The gesture-types are not a fixed code alphabet and not hand-admitted one by
one. They are **generated against a standard, and the standard is a configured
setpoint** — the `inference-as-composition` pattern, where the load-bearing word
is *bounded*:

1. **bdo configures the setpoint** — the standard a gesture-type must meet. His
   governed dial, `--by bdo`, withdrawable, like every setpoint. *This is where
   his hand stays.* The governance is over the standard, not over each type: one
   dial, many bounded types.
2. **Inference generates the gesture-type** for the specific work, against that
   standard (the `loop/tags.py` grain — a closed core, generated extensions, an
   unmet type reading as `proposed`).
3. **Validation refuses a type that misses the standard** — the teeth, the same
   shape as the canvas authoring door (generate → validate against the schema →
   a malformed spec is refused, never rendered). The standard is both what bdo
   dials *and* what the validator checks.
4. **The click produces the typed instance** — data.
5. **The data folds back** as the signal inference generates the *next* type
   against. Closed loop: setpoint → generate → gesture → fold → generate.

## Consequence grounding — the standard is consequence magnitude

The setpoint a gesture is generated against is **required typedness scaled to
consequence magnitude** — reversibility × uncertainty × blast-radius, the same
teeth-placement law. High-blast, irreversible work demands a richly-typed
gesture (more tabs, tighter constraints, must-resolve-against-the-work); small,
reversible work permits a bare click.

This is why the gesture design and the consequence-policy model are the **same
design**: the gesture is what discharges an obligation a consequence raises, and
the bar it must clear is set by that consequence's magnitude — which the policy
model already measures. The constraints on a gesture-type are two things at
once: a **gate** (this gesture is well-formed for *this* work) and a **query
surface** (every confirm-gesture where a piece later refused = the digest's
divergences, now driven by the gesture's own typed fields).

## Why typed makes "seek clarity, never hide" structural

Because a gesture is typed and validated against the standard, an unclear gesture
**fails validation** — and that failure *is* the take-note. It surfaces on the
record and routes back to the gesturer to refine. Hiding becomes impossible by
construction: the system cannot proceed on a gesture it couldn't type. "Seek
clarity rather than hide" stops depending on a node's diligence and becomes a
property of the seam.

## Where it lands

- **Definition home:** `language/pragmatics.md` — the pragmatics stratum is
  **OPEN** today, holding its question. "A gesture is the minimal typed act that
  turns shaped meaning into a licensed consequence" is the pragmatics answer:
  how meaning is *used to act*. The mark graduates only through the
  glyph-knolling ritual and bdo's admission (the stratum's own rule).
- **This blueprint:** the three-layer build (setpoint/standard · generation +
  validation · typed instance), with *inference over the field of gestures* as
  the horizon it serves.

## What stays bdo's (the open dials)

- The **setpoint's contents** — is "typedness scaled to consequence magnitude"
  the right standard, or a different bar?
- The **arc** this rides (its own epic, or under an existing gateway/owner-harness
  family).
- Whether the **pragmatics-stratum** mark is the right home for the definition,
  and when it graduates past PROPOSED.

A session may build toward this only on bdo's confirmation; until then it is a
blueprint, not a buildable.
