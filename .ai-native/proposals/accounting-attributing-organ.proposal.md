# The accounting-and-attributing organ — ontum derives its own primaries (PROPOSED)

> **Status: PROPOSED** — bdo's direction, 2026-06-21 (this design conversation),
> his to steer. The first installable component of the authoring platform
> ([`authoring-platform.proposal.md`](authoring-platform.proposal.md)): the
> layer we start with. Captured here so the shape stops living only in bdo's
> head and he never has to re-state it. Holes are named, not papered over.

---

## The one idea, plainly

We don't hand the system a list of categories. We point it at a body of work,
let it **measure the pattern**, and the words/types come out the far end **as
consequences of inference over that pattern** — never as a list we bring.

The analogy bdo gave, and it's the whole thing: **RGB and CMYK.** There is no
universal set of primaries. RGB is right *for screens* (light, additive); CMYK
is right *for print* (ink, subtractive). The primaries are not chosen — they
**fall out of the medium and its constraints.** So this organ defines, for
whatever it is pointed at, **that medium's own primaries** — its RGB — derived
from local and global factors and constraints (its "framing").

Two consequences of that analogy:

- **A term is not in a box. It is a mix of primaries — a coordinate.** bdo's
  earlier example *is* this: `call-to-action = Action ⊕ Notification` is a
  two-primary mix, the way orange is red ⊕ green. `needs-you` is Notification-
  heavy with Action mixed in. The vocabulary is points in a colour space, not
  items in a list. (This corrects an earlier dead end: a fixed grammar of ~10
  containers freezes a generative thing.)
- **Deriving (not picking) is what makes it general.** A fixed primary set fits
  only ontum. A *method that derives* the right primaries fits any medium — the
  method travels, the fixed set doesn't. This is not a nicety; it is the reason
  the platform can be pointed at work that isn't ontum (below).

## Accounting, then attributing

We **start with accounting and attributing** (bdo's ordering).

- **Accounting** — measure the raw signal: what is actually present in the body
  of work. *(This half already runs: [`causality/corpus_terms.py`](../../causality/corpus_terms.py)
  — a pure read-only fold that counts every term by the formatting signal that
  declared it, plus the id-citation grammar. The spectrometer reading.)*
- **Attributing** — two attributions at once:
  1. **onto the primaries** — decompose each unit into its mix (its coordinates
     in the derived colour space); and
  2. **onto its cause** — who made it, what it leads to, on the record. This is
     the *consequence* attribution (governed by ontum's consequence model: a
     thing is accounted for by what it becomes and who caused it, not just what
     it is).

## Two requirements that shape everything (bdo, this conversation)

These are not features; they are why the design is what it is.

### 1. It works on work we're pointed at — when bdo is not the owner

The platform generalises past instance-1 (ontum pointed at itself). When it is
pointed at *someone else's* work, **bdo is not the owner of that work** — someone
else is. So:

- **The owner is a parameter, never hardwired to bdo.** Attribution records the
  cause *and the owner of that instance*. The three A's (authenticated ·
  authorized · attributed) generalise — attributed-to-whoever, authorized-by-
  that-owner — exactly the portable-stamp principle, generalised from "any
  surface" to "any instance."
- This is **why derive-not-pick**: only a derivation can fit a medium and an
  owner the system has never seen.

### 2. It is installed, not a one-shot

It cannot be a session running a script once and handing over an answer. It is
**installed** — a standing organ wired into the substrate that keeps accounting
and attributing **as the work changes, over iterations.** A one-shot dies with
the session; an installed organ lives and re-derives. This is required by the
living/dynamical nature of the thing (below) and by serving many targets over
time.

## The closed loop it lives in

This organ is one half of a **closed loop**, not a stage in a line (correcting
an earlier "A then B" read):

- **the generative-language layer** — ontum as the dimensional language that
  identifies glyphs, structures them, composes them across axes, and makes a
  physical object from the relationships. *(Real, partly: [`glyphs/knoll.py`](../../glyphs/knoll.py)
  + the cube + incidence laws + the 3D viewer already do this — but pointed at
  the phase-2 vault, and it already ingests outside sources as PROPOSED under a
  structural gate, so the accounted work-corpus is a source it can eat.)*
- **the accounting-and-attributing organ** — this proposal.

The two **feed each other**, with topology between them: the accounting surfaces
the pattern the generative language structures; the structures it makes change
what the next accounting measures. Underneath both: **model-free exploration**
(try without a fixed model) pulled forward by the **pressure system** (what is
needed drives what gets made). A **change model** and a **prediction model** sit
over the living model to support operating against it.

## What's real vs what's a hole (honest inventory)

- ✅ **Accounting** — `corpus_terms.py` runs (literal, deterministic, any
  `.md`/`.json` corpus).
- ✅ **Classification seed** — `causality/term_economy.py` resolves + classifies
  a hand-authored seed; this organ generalises it from a 5-term seed to a
  derive-the-primaries engine.
- ◐ **Generative-language layer** — `glyphs/` is real but pointed at the vault,
  not the work.
- ❌ **Derive-the-primaries-by-inference** — the core hole: inference over the
  accounting that surfaces a medium's primaries.
- ❌ **Attribute onto primaries** — express each unit as a mix (coordinates).
- ❌ **Generalise to non-ontum targets + non-bdo owners** — the owner-as-parameter.
- ❌ **Install + the closed loop** — wire it as a standing organ, not a script;
  the feedback topology with the generative-language layer.

## The first installable increment (when bdo says build)

Not a one-shot, and not the whole loop at once. The smallest *installed* piece:
the **attributing step on top of the accounting that already runs** — a standing
fold that, for a pointed-at corpus, derives a candidate primary basis by
inference and expresses the corpus's real terms as **mixes** of those primaries,
recording each attribution (the coordinates + the cause + the instance's owner)
on the log. Read-only on truth, propose-grain; the owner of that instance is the
last stop (D-4), whoever they are.

## Composition note (no second truth — §10)

This composes the organs that exist (`corpus_terms`, `term_economy`, `glyphs`,
the log) into one installed loop; it does not re-derive them. When bdo names it,
it graduates into `epic.accounting-attributing` (or a slice of the authoring-
platform epic) and this proposal stays as the record of where the arc was born.
