# The autonomy dial — your owner's manual

**In one line: this is the switch that lets AI carry out whole initiatives on
your behalf while you keep control — by bounding *what the world is allowed to
become* without you, not by listing every action it may take.**

> **Status: PROVISIONAL** — built and working, authored by an AI session
> 2026-06-21, awaiting bdo's stamp. The settings below are **defaults I chose**
> so it works out of the box; every one is a knob you can move (see *Your
> knobs*). This manual is a telling of a real part — the dial is
> [`loop/authority.py`](../../loop/authority.py), and you can read its live
> settings any time with `python -m loop.authority`. Where this page and the
> code disagree, the code wins and this page is the bug.

---

## The idea, plainly

You don't want to approve every step an AI takes — that defeats the point. But
you also can't hand it a blank cheque. The usual fixes both fail: a giant
allow-list of permitted *actions* can never be complete (a capable agent has
endless ways to act), and "just trust it" is how you get surprised.

So the dial governs the one thing that *is* finite and that you actually care
about: **consequences.** Not "may the AI run this command?" but "**what may the
world look like afterward, and can that be undone?**" Most of what a worker does
is small and reversible — it should just happen, and tell you afterward. A few
things are not — those stop and wait for you. The dial draws that line, and
draws it **safely by default.**

This is the difference between *automation* (a fixed rule fires) and *autonomy*
(an agent pursues a goal you approved, inside a bound you set). The dial is the
bound.

## The one rule

An act proceeds **without asking you** — it acts, leaves a receipt, and surfaces
to you as an after-the-fact *FYI* — only when it is **all four** of:

| | What it means |
|---|---|
| **Observable** | its effect can be traced home to whoever did it (no anonymous changes) |
| **Reversible** | it declares a real undo — it can be rolled back |
| **Low-blast** | its reach touches only its own corner, nothing shared or yours |
| **On an approved arc** | you already greenlit this direction (a confirmed arc) |

**Anything else asks you first.** A new, half-declared, irreversible, far-reaching,
or off-the-plan act stops and requests your stamp before it runs. When in doubt,
it asks — never the other way around.

That's the whole policy. It's deliberately strict: it would rather ask twice than
act once where it shouldn't.

## What that means in practice (the defaults I set)

**Runs on its own, tells you after** — e.g. drafting a proposed unit of work in
its own workspace, reorganizing notes with every original preserved, anything it
can cleanly undo within its own scope, on work you already approved.

**Always stops and asks you first** — anything that:

- can't be undone (sending an email, a payment, a deletion),
- reaches a **shared or owner-critical surface**: the trunk (`main`), your
  reading surface (the viewport), the outside world (network, email), **money**,
  your **identity or voice** (speaking *as* you), or another worker's workspace,
- isn't on an arc you've confirmed, or
- can't fully describe itself (if it can't say what it touches and how to undo
  it, it doesn't run).

You never have to assemble this. It's configured and on.

## Your knobs

Three settings, each moved with one command (only you can — it's your authority):

```sh
# see the current policy in plain words, any time
python -m loop.authority

# loosen: let reversible, low-blast work proceed even off a confirmed arc
python -m loop.authority admit-tiers --by bdo --value '{"require_arc": false}'

# tighten further: keep asking even for reversible acts (maximum caution)
python -m loop.authority admit-tiers --by bdo --value '{"require_reversible": true}'

# change what counts as "high-blast" (the surfaces that always ask first)
python -m loop.authority admit-tiers --by bdo --value '{"high_blast": ["main","viewport","money","identity","delete", ...]}'
```

| Knob | Default | What moving it does |
|---|---|---|
| `require_arc` | **on** | off → reversible, low-blast acts may proceed even without a confirmed arc |
| `require_reversible` | **on** | the floor — keep it on unless you truly want irreversible acts to ever run unattended |
| `high_blast` | the list above | the surfaces that *always* ask first; widen or narrow it |

Your setting is remembered on the record and used from then on; until you set
one, my safe defaults hold. You can always change your mind — it's one command,
and the change is logged like every other decision.

## What's real today, and what's next

- **Real and working now:** the dial itself — the decision that routes any
  declared act to *proceed* or *ask*, default-safe, tested, and tunable by you.
  It composes the consequence-gate ([`loop/observe.py`](../../loop/observe.py)),
  which already forces every autonomous act to declare what it touches and how
  to undo it.
- **Next (named, not built):** the **Administrator** — the part that watches the
  whole fleet of workers, runs each proposed act past this dial, lets the safe
  ones through, and brings only the *ask-first* ones to you as a short, shaped
  briefing rather than a queue. The dial is the keystone it needs; this is its
  first piece. The blueprint is
  [`authoring-platform.proposal.md`](../../.ai-native/proposals/authoring-platform.proposal.md).

---

*Where this comes from: the autonomy-dial design is bdo's direction (2026-06-21,
"ask-forgiveness = a risk-tiered authority dial; set the default and give me an
owner's manual"); the consequence-over-action framing is the consequence-policy
model on the record; the part is `loop/authority.py` with its tests in
`tests/test_authority.py`. The owner-harness horizon it serves — "you steer by
decisions, not labor" — is the engine's own (`python -m loop.node arcs`).*
