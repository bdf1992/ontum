# The living spec — growing meaning instead of writing it down

> **Status: PROPOSED** · owner **bdo** · 2026-06-22. The refined consolidation of
> a long design conversation and the proposals it composes —
> [`authoring-platform.proposal.md`](authoring-platform.proposal.md),
> [`generative-basis-membrane.proposal.md`](generative-basis-membrane.proposal.md),
> and [`causality/display-system.md`](../../causality/display-system.md). It does
> not replace them; it is the plain-language front-of-house they sit beneath, and
> the place the scattered pieces finally say one thing. Nothing minted (D-4).
>
> **One line:** API documentation is a *photograph* of how something should work.
> This is the *organism* that keeps taking new photographs of itself and keeps
> the good ones.

---

## Why this is worth building (the wall it's for)

People are right that API docs are now often *good enough* — hand an AI a clear
document and it can implement against it. But a document is a handoff: a picture
of how something should work, passed from one mind to another. A picture has hard
limits baked into what it is. It can't tell you when it's gone out of date. It
can't notice that two things it quietly lumped together have turned out to need
separating. It can't watch whether the thing built from it actually *behaves*
right once it's in the world. It scales exactly as far as one handoff, and then
it freezes. **That is the "can't scale" — not that docs are bad, but that a
photograph is dead the moment it's taken.**

What scales is the loop *around* the spec, and it needs four things:

- **Observation** — watch what really happens when the spec is used, not only
  what the spec promised.
- **Cutting** — when reality shows the spec blurring two things into one, make
  the new distinction, so the spec gets *sharper* with age instead of staler.
- **A controlled place to run** — deterministic and fenced, where you can run the
  same thing a thousand times and trust the result, and nothing leaks out and
  breaks the real world.
- **Healthy drift you mine exemplars from** — and this is the point. You don't
  *write* the next, better spec. You let the system vary, safely, inside the
  fence, and the variations that actually worked become the new standard. The
  best examples are **harvested, not authored.**

That last move is the whole reason to go AI-native. A human-written spec is only
ever as good as the person who wrote it on the day they wrote it. A system that
mines its own best results from bounded, observed variation gets **better than
its authors, and keeps getting better** — because the standard is continuously
re-cut from what actually worked, not from what someone once guessed would work.

So this isn't a nicer way to write API docs. It's **the one thing a doc can never
be: a spec that's alive.** The doc still exists — it's the fast, cheap,
deterministic floor you can trust. The AI-native part is the slow loop wrapped
around it that observes, cuts, and harvests, so the floor keeps rising on its own.

**The honest line, so this isn't a religion:** if the domain is small and stable,
the photograph is fine — don't build the organism. You build the living version
exactly when the thing is too big and moving too fast for any single author to
keep the spec current. The justification *is* the scaling wall.

## What it is, from the seat

You sit at a blank canvas and type a word — *creole*. Against a body of knowledge
it's pointed at, the canvas grows a web in front of you: the parts of the idea,
how they hang together, branching the way a thought branches. You click a piece
and fall into it, type again, and that corner deepens. Where you put the words
matters — something above the word, below it, before or after it, shifts the
meaning — because position is part of what you're saying, not decoration.

That's the surface. The thing underneath that makes it more than a diagram tool:
**typing isn't always asking.** Sometimes you want to *understand* something.
Sometimes you're asking for *work* to be done. Sometimes you're setting something
up to *run on its own*. Sometimes you're standing over a crew of workers and
*steering*. Those feel like four tools. They're not. It's the same canvas and the
same act of typing — what changes is **the kind of weight your purpose puts on
it.** The same way one band of light is "three colors" on a screen but "four
inks" on paper: one spectrum underneath, shown differently by what you're doing
with it.

## How it stays honest

**Nothing is taken on faith.** Every "this means that" has to point back to
something that actually exists. If it points at nothing, it's a ghost, and it's
refused. The only thing that's free — that needs no justification — is the bare
fact that *something happened*. Everything above that bare record is an
interpretation, and interpretations earn their keep or get cut. (This is already
the repo's spine: `causality/term_economy.py` and `loop/gaps.py` refuse a claim
with no resolvable evidence; the append-only log is the one free layer.)

The controlled environment is what makes healthy drift *safe* rather than
chaotic: the fence, the deterministic record, the gates that judge work, the
marks that flag what bit wrong. That's not overhead — **that's the gym.** It's the
place where variation can happen without escaping into the real world, and where
the good results can be picked out and kept. The pieces of the gym already exist:
`fence/barrier.py`, the append-only log, the judging gates, `loop/heal.py`,
`loop/herald.py`'s exemplar-vs-notoriety reputation.

## The knowledge it draws on

The canvas isn't pre-loaded. You *point* it at a body of information — a corpus —
and that corpus has to come in through a door (the gateway) and get **translated
into the canvas's own way of recording things.** That translation is the real
work, and it's easy to get wrong: it isn't "import their data," it's "re-record
their facts as *our* facts, so we can reason over them and **catch ourselves when
we're wrong about them.**" A source that can't be re-grounded can't be reasoned
over honestly. (Closes the open hole in `display-system.md`: corpus-from-outside
was unmodeled — it's modeled here as a registered, translated source.)

## Two systems studying each other (the horizon)

Stand two of these systems facing each other. Each opens its door, and each sees
only what it's allowed to see, at the level of detail it's allowed. They don't
just swap files — **they study each other**, building a picture of what's inside
the other and what it's *for*. Out of that, a shared language grows between them:
a creole. And the test that keeps it real instead of two systems flattering each
other: **my picture of you has to predict what you actually do.** When my guess
about your next move comes true, the shared language is earned. When it doesn't,
we throw it out. The floor of getting two systems to talk is **translating each
other's records, not agreeing on words** — the shared language rides on top of
that, never under it.

This is the horizon, not the first build — and it may start with the system
federating *with itself across time*, where the other side's real history is a
perfect thing to predict against, before any outside peer exists.

## Code that behaves (the cleanest case)

A piece of code isn't only something to run. It can be read as **instructions for
how to behave** — *act like this*. That case is the cleanest one in the whole
system, because you can always *also just run the code* and compare. It's the one
place where "did it understand what it read?" has a perfect answer — and
everything fuzzier (understanding a corpus, understanding another system's
purpose) borrows its honesty from that one clean case. (This is the dual of what
ontum already does — versioned prompts are source; here, source is read as a
prompt.)

## What's real, what isn't

**Mostly built — the floor:** the recording, the checking, the growing of a typed
graph, even a first "describe it and get a web back" (`causality/text_to_system.js`,
`causality/authoring.js`, the validated-before-it-draws rule), the propagation
graph (`loop/consequence_graph.py`), a working model of how distinctions get cut
(`loop/basis.py`), reputation and trust (`loop/herald.py`, `loop/trust.py`), the
fence and gates.

**The unbuilt heart:** the web growing *differently depending on the frame you're
in and the angle you're looking from*. Today the part that grows the web
deliberately *ignores* your context — that's how it stays honest
(`text_to_system.js` is context-free by design). **Teaching it to use your
context without starting to lie is the real unsolved problem.** Everything else
here is either built or composes something built; this is the genuine new work.

**Named holes (open, not invented):**
- the grammar of position (above / below / before / after as parts of meaning) —
  unmapped;
- *how* two languages actually negotiate into a third — asserted, not shown;
- whether translating a corpus in is a fixed, repeatable step or an AI judgment
  that itself needs checking (probably both, and it has to carry its own grade).

## The one decision that simplifies everything

Is "what kind of work you're doing" really just "how hard you're leaning on one
engine"? If understanding, asking-for-work, running, and steering are one surface
under four pressures — not four surfaces — then **there is one thing to build, and
it only looks like four because we've been making them separately.** This is the
first thing to test, because the answer reorganizes everything above it.

## What's yours to steer (the knobs)

1. **Is the center right** — one living engine, the mode is the pressure, the spec
   is alive? Or is the center somewhere this still walks past?
2. **The bounded-drift dial** — how much variation counts as *healthy* before it's
   chaos. This is the dial that makes the gym safe; it's yours to set.
3. **Self first or peer first** — does the two-systems horizon start with the
   system studying its own history, or wait for a real outside peer?
4. **Graduate or hold** — does this become `epic.living-spec` (with pieces), or
   stay a captured map a while longer?

## Composition note (so this doesn't re-scatter)

This consolidates; it does not copy or supersede. The technical detail lives in
the cited proposals — the membrane that cuts distinctions, the component board,
the agent-authoring tiers. This document adds the one thing none of them held: the
plain account of **why** (the scaling wall) and the single shape that ties the
canvas, the membrane, the federation, and the honesty discipline into one
sentence — *a spec that's alive*. When bdo names it, it graduates to an epic and
these fold beneath it.
