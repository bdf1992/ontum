# The autonomy dial — your owner's manual

**In one line: this is the switch that lets AI carry out work on your behalf
without asking you each step — by drawing one line you control between what
runs on its own and what stops for your stamp.**

> **Status: PROVISIONAL** — the classifier is built, tested, and working;
> authored/assembled by AI sessions 2026-06-21, awaiting bdo's stamp. It governs
> by *consequence*, and — by design — it **does nothing on its own until you
> draw the fence** (one command, below). This page is a telling of a real part:
> the engine is [`loop/act_fence.py`](../../loop/act_fence.py), and you can see
> the live cut any time with `python -m loop.act_fence`. Where this page and the
> code disagree, the code wins and this page is the bug.

---

## The idea, plainly

You don't want to approve every step an AI takes — that defeats the point. But
a blank cheque is how you get surprised. So this governs the one thing that is
finite and that you actually care about: **consequences.** Not *"may the AI run
this command?"* but *"what may the world become afterward, and can it be
undone?"*

Every act an AI worker proposes falls into one of **three tiers**:

| Tier | What it means | What happens |
|---|---|---|
| **Forgiveness** | reversible **and** contained to its own corner (a read-only fold, a branch draft) | runs on its own, leaves a receipt, tells you after (FYI) |
| **Permission** | reversible but *wide*, or anything genuinely weigh-worthy (landing to main with no confirmed arc) | **stops and asks you first** |
| **Forbidden** | irreversible, reaches outside the repo, acts *as* you, or *is* your authorization (confirm an arc, draw this fence) | **never** — no setting lifts it |

The cut is keyed to *real ontum gestures*, not abstract "risk": the same act
(landing a PR) is *forgiveness* under an arc you already confirmed and
*permission* without one — it reads the authorization context, not the verb.
And anything unobservable — an act whose effect can't be traced home — halts
*before* its tier is even read.

## The one thing only you can do

Here's the deliberate safety: out of the box, **the dial is inert.** It
classifies every act and shows you the cut, but nothing self-admits — every
forgiveness act still asks. That's not a missing default; it's the law. The
authority to let acts run unattended *is your stamp* — so the system forbids
itself from drawing that line. Only you draw it.

You draw it with **one command** (I've picked the safe starting cut for you —
a worker's own reversible, contained work; nothing wider):

```sh
python -m loop.act_fence draw-fence --forgivable read-fold draft --by bdo
```

That turns on ask-forgiveness for exactly those scopes. The moment you run it,
reversible read-folds and branch drafts run on their own and report after;
everything else still asks. You never assembled anything — you stamped one line.

## Your knobs

```sh
# see the whole cut + what each kind of act would do right now, any time
python -m loop.act_fence

# widen later: also let the merge-node self-admit landings under confirmed arcs
python -m loop.act_fence draw-fence --forgivable read-fold draft land-main --by bdo

# narrow back to just read-only folds
python -m loop.act_fence draw-fence --forgivable read-fold --by bdo
```

| Knob | Recommended start | What it does |
|---|---|---|
| `--forgivable` scopes | `read-fold draft` | which reversible, contained scopes may run unattended; widen or narrow at will |
| (no fence drawn) | the default | inert — everything asks; the safest setting, and where you begin |

Each draw is logged like every decision; the latest wins, and you can always
re-draw or pull it back. Forbidden acts stay forbidden no matter what you
draw — that floor is not a knob.

## What's real today, and what's next

- **Real and working now:** the classifier — the three-tier cut over any
  declared act, keyed to real gestures, composing the consequence-gate
  ([`loop/observe.py`](../../loop/observe.py), which forces every act to declare
  what it touches and how to undo it) — plus the `draw-fence` gesture and the
  live `python -m loop.act_fence` witness.
- **Next (named, not built):** the **Administrator** — the part that watches the
  whole fleet of workers, runs each proposed act through this cut, lets the
  forgiveness ones (under your fence) through, and brings only the *ask-first*
  ones to you as a short, shaped briefing instead of a queue. This dial is the
  keystone it stands on. The blueprint is
  [`authoring-platform.proposal.md`](../../.ai-native/proposals/authoring-platform.proposal.md).

---

*Where this comes from: the three-tier ask-forgiveness cut is bdo's direction
(2026-06-21, "install ask-for-forgiveness on some risk levels" / "the
ask-forgiveness authority dial is the keystone to the autonomous-authorship
button"); the delivery — set the default, give an owner's manual, "this isn't
ikea, it's apple" — is his too. The engine is `loop/act_fence.py` (the disposer's
standing-fence pattern lifted onto acts), tested in `tests/test_act_fence.py`.
The owner-harness horizon it serves — "you steer by decisions, not labor" — is
the engine's own (`python -m loop.node arcs`).*
