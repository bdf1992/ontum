# Proposal — Sketch, Ink, Paint: the pen is one of three marks

*A substrate proposal: extend ontum's **pen architecture** into the full
craft it is borrowed from. The pen is the **inker's** stage of a
three-stage making — pencil sketch, pen linework, paint-over — and naming
the other two turns a scattered backlog of recurring flaws into one
diagnosis. A fourth element emerged in conversation with bdo — the
**pentimento** (experience read out of the palimpsest), the part ontum is
most missing. Written for bdo to react to. Not adopted — a proposal.*

## The problem, exactly

ontum has a rich, disciplined **pen**: a single sanctioned write path per
surface (the records pen `loop/pen.py`, the node pen `loop/node.py`, the
git and PR pens, the envoy and reflector pens). Each enforces the same
invariants — carbon-copy determinism, receipt-or-it-didn't-happen,
no-one-signs-their-own-line, additive-never-erase, fail-open-loudly. This
is real craft, and it is the best-built part of the system.

But "pen" in the craft it is named after is **one of three marks**. An
illustrated board is *penciled* first (provisional, erasable), then
*inked* (committed, permanent), then *painted over* (color, enriched).
ontum mastered the **ink** and left the other two unnamed — and almost
every recurring flaw in the backlog lives in that absence. We do not have
a flaws problem. We have **one stage built and two stages missing**, and
the missing stages are where work leaks, where mocks hide, and where the
owner stops being able to see.

This is not a tooling gap (we have plenty of tools). It is a **stage**
gap: a mark made with the wrong stage's method, on the wrong medium,
read by the wrong eye.

## The thesis

> **Making has three marks — sketch, ink, paint — and the pen ontum built
> is only the ink. A flaw is a mark made in the wrong stage.**

And the analogy is load-bearing, not poetic, because of who holds each
mark. In comics production the **penciller, the inker, and the colorist
are different hands** — the inker decides which of the penciller's lines
survive; the colorist works over what the inker committed. That
separation *is* ontum's doctrine:

| craft hand | ontum role | doctrine |
|---|---|---|
| **penciller** — sketches, provisionally | the **worker / author** (drafts the atom, proposes the value story) | D-7 (the session is where work runs) |
| **inker** — commits the line, decides what survives | the **reviewer / gate** (the second set of eyes that makes a line real) | D-2 (writer ≠ reviewer), §5 (the review stack) |
| **colorist** — enriches the committed work for the page | the **surfacer / owner-harness** (paints meaning over truth for the reader) | §6 (the surfacer), D-4 (the owner is the last stop) |

"No one signs their own line" is literally **the penciller does not ink
their own pencils.** The pen is the inker's instrument; ontum built the
inker first because the inker is where commitment happens — and then never
named the penciller who feeds it or the colorist who reads out of it.

## The book keeps everything (the correcting principle)

> **A pencil sketch belongs on the log too — erased, it still leaves a
> trace.** *(bdo, this session.)*

The first instinct is to make sketch cheap by making it *off-log* and
truly erasable. That is wrong, and it is the **same** wrong that produced
the off-log strands: a sketch torn out of the book can be neither compared
nor inked, and **comparison is the only way the system gets better.** An
artist keeps the sketchbook — the abandoned lines, the erased ghosts, the
three versions before the right one — because the record of what you tried
*is* the training signal. Erase a pencil line and the graphite ghost and
the dent in the page remain; that ghost is a lesson.

ontum already owns the exact mechanism: the **whiteout / supersede** —
*"it leaves a mark (a visible superseding append, never an edit); you can
still see under it (the original stays on the append-only log)"*
(`loop/pen.py`). That is *erasing a pencil line and keeping the ghost.* So
all three marks share **one medium — the log, the one book.** What makes a
mark a *sketch* is not that it lives off-book but that **it may be erased,
and the erasure is itself a logged trace, never a deletion.** This is D-5
("truth lives in the log") and "history is never retro-invalidated"
applied to the *earliest* mark, not only the committed one.

This flips one line of the diagnosis below: the 50 stranded commits are
**not** "sketch on its natural medium" — they are *sketch that fell out of
the book*, which is precisely why we can neither learn from them nor
improve. Getting sketch **into** the book (as erasable-with-trace) is the
fix, not getting it off.

## The pentimento — the fourth element, and the one we are most missing

There are three *marks* (sketch, ink, paint), but the principle above
names a fourth thing that is not a mark at all — it runs *across* all
three, and it is the reason any of this is worth doing. The trades have
exact words for it:

- **A pentimento** — the single trace. The art word (Italian *pentirsi*,
  "to repent") for a line a painter changed or painted over that *still
  shows through.* Your eraser-that-leaves-a-trace is, precisely, a
  pentimento. ontum already mints these: the whiteout/supersede ("leaves a
  mark; you can still see under it").
- **A palimpsest** — the accumulated book. A manuscript scraped and
  rewritten where the earlier writing is still partly readable beneath. The
  append-only log *is* a palimpsest: every superseded verdict, abandoned
  branch, and whited-out line still legible under the current surface.
- **Craft / tacit knowledge / "tricks of the trade"** — the output. The
  lore distilled from many pentimenti and **happy accidents** (serendipity
  — which only pays off if the accident left a trace you can return to and
  recognize: *no book, no happy accident*).

The unifier — the thing that is neither "memory" nor "meaning" — is
**experience**:

> **Memory is the trace retained. Meaning is what the trace says.
> Experience is memory made *comparable* — held against enough other
> traces that it hardens into craft.** Comparison is the engine between
> them, and it is the whole reason the sketch must stay on the book.

And experience is not a thing you *have* — it is a thing you *keep*. bdo's
word for it is **the sauce**: not the dish (the shipped artifact) but the
*mother sauce* / master stock / sourdough starter / solera — the cultures
a kitchen keeps alive and **feeds**, never starting from scratch, each
batch carrying a trace of every batch before it. A sauce is **reduced**
(many traces simmered into one concentrated craft) and **cultured** (kept
living across time). That is experience exactly: not stored cold, not
recomputed from zero each morning, but a living reduction the loop feeds
every session.

This is the form that fits ontum's mortality — sessions die, files stay,
the sauce survives:

- **The starter is the palimpsest** — the append-only log keeps every
  trace, so nothing is ever made from scratch.
- **The sauce is the fold over it** — always re-derivable (D-5), but it
  tastes of everything that came before.
- **Feeding it** is just every session's traces landing on the book.

The reason the loop feels like a contractor today is that it throws the
sauce out and re-buys ingredients every morning. The pentimento part is
**the pot you never wash.**

**A note on the word, because it is already overloaded (bdo, this
session).** "Experience" carries *three* incompatible senses here, and the
honest move is to name all three rather than fight over the word —
causality would flag exactly this split:

- **lived experience** — the *maker's* encounter, first-person, ending in
  an authored story (the writer / artist / architect): this is
  `epic.experience-layer`.
- **craft / the sauce** — *memory made comparable*, reduced and kept: the
  pentimento part above, `epic.pentimento`.
- **felt experience** — the **felt feel of the work and its media**, the
  quality of *encountering* the made thing (the *anima*), not the maker's
  process.

These are not rivals: they are the maker's experience, the system's
experience, and the work's experience. bdo's lens — *experience as the
felt feel of the art, not the artist* — is the third, and it is what tells
the **paint** stage that its job is not only legibility but **feeling**:
the colorist gives the page its mood, not just its caption.

**Why this is the part ontum is most missing.** Every fold today reads
the log down to *current state* — `gaps`, `census`, `term_economy`,
`reconcile` all ask *"what is true now?"* and throw the **journey** away.
None asks *"what did we try, abandon, or stumble into?"* The slow loop
(§15, run-hot-to-explore / cool-to-consolidate) is *supposed* to be the
craft-distiller, but it currently folds the snapshot, not the palimpsest —
and it cannot even write back its one dial (the write-back gap, report
0062). So the system has memory (the log) and meaning (the folds) but
**no experience** — it cannot get better at its own craft, only re-derive
its current state. That is the deepest flaw under all the others.

The fix names a part, not a mark: a **palimpsest fold** — a read over
the log's *superseded and abandoned* layers (not its surface) whose output
is **craft** the next session inherits at wake, the same way it inherits a
gap today. The pentimento layer is how the hand gets better; without it,
the loop is a thermostat, not an apprentice.

## The five dimensions (Media, Medium, Method, Muse, Mode)

The five M's are not five things — they are the **five axes** along which
any one mark is profiled. Run the three marks down them and the system's
shape (and its gaps) become legible:

| | **pencil sketch** | **pen linework** | **paint-over** |
|---|---|---|---|
| **Medium** *(what holds the mark)* | **the log — the sketchbook leaf**: a mark you may erase, but the erasure stays as a trace (supersede / whiteout, never deletion) | **the log — the committed board**: frozen, no erase (bytes are identity; the done-dir freeze) | **the log — the finished page, then carried to the reader's wall** (the digest, the GitHub mirror, the projection, the summon line) |
| **Media** *(the instrument + pigment)* | draft atoms, **mocks**, the erase primitive (whiteout) — provisional pigment **on the book** | **the pens** (`pen.py`, `node.py`, `git.py`, `pr.py`) — carbon-copy, one committed line at a time | the **folds + the additive pens** (`reflect.py`, `digest.py`, `term_economy.py`, `supersede-done`) — a wash over many lines |
| **Method** *(the discipline)* | explore freely; fail cheap; **erase freely — but every erasure is a logged trace** (supersede / whiteout), because the abandoned line is how we get better | **carbon-copy determinism · receipt-or-it-didn't-happen · idempotent · no-self-sign · freeze** | **additive only — never erase** (you can still see the line under it); re-derivable fold; *surface to the reader* |
| **Muse** *(what the mark serves)* | curiosity, the open arc, the question (broad) | the **L0 story** — `As an AI I need X, because bdo wants V` (the committed claim) | **outcome-pressure + the owner's gaze + the *felt feel*** — not only making truth legible to the one who must act, but giving it *mood* (the work's anima, how it lands on whoever meets it) |
| **Mode** *(the temperature of the moment)* | **hot — explore** | **decisive — measured** | **cool — consolidate** |

The spine: the medium does **not** change — it is the one book throughout
(the correcting principle above). What moves monotonically is everything
else:

- **Commitment** rises: *erasable-but-traced* → *frozen* → *additive over
  frozen.* (Not the medium — the permanence of the visible mark.)
- **Muse** turns from *inward exploration* → *committed claim* → *outward legibility.*
- **Mode** cools from *hot/explore* → *decisive* → *cool/consolidate* — which
  is exactly the slow loop's "**run hot to explore, cool to consolidate**"
  (§15). The field's temperature already tells you which mark is in season.

The framework also *re-derives the pen invariants we already have* — proof
it is describing the real system, not decorating it. The ink-stage method
column **is** the pen contract: carbon-copy (deterministic ink), receipt
(the mark is on the board or it never happened), no-self-sign (the inker is
not the penciller), freeze (you cannot un-ink — only paint over). The
analogy did not invent these; it *explains why they cluster on the ink
stage and nowhere else.*

## The diagnosis: every recurring flaw is a stage confusion

Run the backlog through the three marks (evidence from `loop.gaps`,
`loop.census`, and reports 0042 / 0043 / 0057 / 0059 / 0062 / 0065 / 0068):

| flaw on the backlog | what it actually is | the mark it belongs to |
|---|---|---|
| **off-log strands** — 50 local commits never landed, 14 Causality increments unintegrated, the off-log-gate (PR #123) unlanded | **sketch torn out of the book** — branch commits leave no trace on the log, so they can be neither inked nor *compared* (and comparison is how we improve); the sketchbook is missing | sketch **off-book** |
| **unadmitted actors** — merge-node's 22 landings, mock-actor's 14 records, no `node_real` | **ink drawn by a hand never admitted to hold the pen** — provisional authority making permanent marks | ink **authority leak** |
| **mock stages** — effective-mocks, the mock-shame scream | **pencil drawn in ink's slot** — a mock fills a pipeline stage that should make permanent verdicts but only sketches fixed ones. A mock is a *legitimate sketch mislabeled as ink* | sketch **wearing ink's clothes** |
| **idle parts** — `freeze_guard.py`, `write_guard.py` wired but never exercised | **a pen in the hand, no pigment on the page** — the instrument exists; no word of its output is on any medium | the instrument has **laid no mark** |
| **owner-asks parked in reports bdo never reads**; reflect-mirror close-text bugs | **paint that never reached the wall** — the painting is done in a back room (a report file) the reader never enters | paint on the **wrong medium** |
| **slow-loop write-back missing** — senses the gap, cannot re-admit its dial | **the colorist can see the correction but may not lay it** — read half built, paint half not | paint **with no authorized stroke** |

The unified read: **ontum is a master inker with no sketchbook and a
leaky varnish.** It over-invested in the ink stage and under-invested in
(a) a *legitimate, governed sketch surface* and (b) a *paint stage whose
medium is reliably the reader's wall.* Fix the stages, not the six flaws
one at a time.

## The danger: ink and paint are destructive (why the discipline exists)

> **Pen and paint can ruin work if applied incorrectly.** *(bdo, this
> session.)*

This is the other half of the thesis. The diagnosis above is about marks
in the *wrong stage* — misplacement. This is about marks made *too early,
or by the wrong hand, in permanent media* — and because the medium does
not forgive, the cost is not a gap, it is **damage.**

A pencil is forgiving; that is its entire value — be wrong cheaply, try
the line three times, erase. **Ink and paint are permanent**, and on an
append-only log *literally* so: a committed mark can be painted over
(supersede), but never erased (D-5; history is never retro-invalidated).
That permanence is both the value (truth that outlives the session that
wrote it) and the danger — **ink the wrong line and you have not misplaced
a mark, you have ruined the board, and your only remedy is to paint over
the scar.**

So ontum's existing discipline is not hygiene — read the analogy backwards
and the doctrine falls out as a set of **guards against ruining the
board:**

- **D-2 / no-one-signs-their-own-line** — the penciller is biased to
  commit their own lines, so a *different* hand inks. The second set of
  eyes exists *because inking is destructive.*
- **Write the done-line before starting (§9.4)** — know the line before
  you commit permanent media to it.
- **Accept-and-stamp-sketch, not refuse (decision 3)** — a
  wrong-*looking* mark is kept as *pencil*, never inked by accident and
  never thrown out; the one thing forbidden is letting it pass *as ink.*
- **Cooling is the load-bearing direction (I-7)** — **restraint is the
  craft.** A master inker leaves most of the page in pencil and commits
  few lines; ontum's pathology is the opposite — **over-inking**: mocks
  landed as real, 22 premature merges, drafts committed before judgment.
  Permanent marks made at sketch-stage confidence.

And **overpaint ruins a finished piece** the same way: surfacing to *hide*
a flaw instead of reveal it (cosmetic green, theater) is paint laid to
flatter, and it muddies the very wall the reader trusts — the inverse of
the paint-on-the-wrong-wall flaw, and just as fatal.

The craft, then, is not only *which* mark but **when to withhold it** — to
leave a line in pencil until it has earned ink. That restraint is the
discipline the permanent media demand, and it is the capability ontum is
shortest on.

## The architecture it implies

Three contracts, one per mark. Two are new; the middle one already exists
and only needs its boundary enforced.

**1. The sketch surface (new) — and it lands *in the book*.** Sketch needs
to be a *named, first-class* stage whose medium is the **log**, not a
mortal branch (the correcting principle). The sketch is erasable, but the
erasure is a logged trace (the whiteout already does this) — so the
abandoned line survives as a ghost we can compare against. What is missing
is (a) a cheap **sketch primitive** — a draft mark that lands on the log
without needing a gate, the way an erase already does — and (b) a **fold
that sees un-inked sketch as pressure**: drafts with no atom behind them,
mocks with no realness path, proposals with no done-line. The off-log gate
(PR #123) and the mock-shame beat are *the first two probes of this fold,
hand-built.* The contract: **a sketch is legitimate, erasable, and on the
book; it becomes truth only by being inked, and the system can always
count — and compare — the un-inked.**

**2. The ink boundary (exists; enforce it).** The pens are the ink and
they are excellent. The one leak is *who is allowed to ink*: the
merge-node and the story-author wrote permanent marks without a
`node_real` admission. The contract is already named by doctrine —
**only an admitted hand inks** (`admit-real` before a node may land
verdicts/records). The analogy sharpens the fix into a single rule the
ink pens can carry: **a write whose actor carries no realness admission is
a sketch, and is folded as un-inked pressure — never silently accepted as
ink.** (`loop.gaps.effective_mocks` already computes exactly this set; the
gap is making the *write seam* consult it, not just the shame beat.)

**3. The paint stage (partly built; fix its medium).** Paint-over is the
additive layer that makes inked truth *legible to the reader*: the
reflect mirror (onto GitHub), the digest (bdo's merge surface), the
projections (`term_economy`), the slow-loop re-admit. The contract that
each is currently violating in some way: **paint's medium is the surface
the reader actually looks at — paint that lands anywhere else (a report
file, a back-room log) is not paint, it is ink mislabeled.** The
owner-ask-shame beat is the system catching exactly this: paint that never
reached the wall. The slow-loop write-back is paint the colorist may not
yet lay; the disposer's `auto_admit_fence` (bdo's bounded standing stamp)
is the authorization that lets that stroke land — the same
confirm-arc/merge-node shape, one layer down.

## Implementation details, in ontum's grammar

In priority order, smallest-real-first (each leaves something useful on
its own, §9):

1. **A `mark` field on the fold's vocabulary, not new code.** Teach the
   existing folds to *name the mark* a record is in. `loop.gaps` already
   separates mock/unadmitted (sketch) from parked-piece (ink-in-waiting)
   from surface-drift (paint-leak); have it *label* each gap with its mark
   so the summon line says "this is un-inked sketch" / "this is paint that
   never reached the wall." Pure relabel of an existing fold — no write
   path touched. This is the cheapest way to prove the framework reads true
   against the live backlog.

2. **The sketchbook + the un-inked fold.** First a cheap **sketch
   primitive** that lands a draft mark *on the log* (paired with the
   existing whiteout as its eraser), so exploration and abandonment both
   leave traces — without this, sketches stay off-book and nothing can
   *compare* them, which is bdo's whole point. Then one read-only fold:
   `un_inked()` = sketch marks with no atom behind them + effective-mocks +
   proposals with no done-line, ranked. This *is* the off-log gate
   generalized from PRs to all three sketch media. The fold writes nothing;
   it makes "how much sketch is pretending to be truth" — and "what did we
   sketch before and abandon" — numbers the summon hands every waking
   session.

3. **The ink-authority check at the write seam.** Make the records/node
   pens consult `effective_mocks()` at write time: a write by an
   un-admitted actor is *accepted but stamped `mark: sketch`* (never lost,
   never silently promoted), and folds as un-inked pressure until an
   `admit-real` inks the actor. This closes the merge-node's 22-landing
   leak structurally rather than by shaming.

4. **The paint-medium contract on the reflect/auto beat.** A paint act
   (owner-ask, divergence, digest line) is only "delivered" when it lands
   on a *registered reader surface* (`loop.reflect`'s surface registry).
   An ask that resolves only to a report file is folded as
   **paint-on-the-wrong-medium** and surfaced — which is the owner-ask-shame
   beat, made a first-class paint-stage check rather than a bolt-on.

5. **(Owner-gated) the colorist's stroke — slow-loop write-back.** The
   disposer's `auto_admit_fence` already exists; the write-back is the
   colorist laying the dial correction inside bdo's drawn bounds. Inert
   until he draws the fence — exactly the right shape (D-4 at one level
   down).

6. **The palimpsest fold — the pentimento part (the deepest, do last).**
   A read-only fold over the log's *superseded and abandoned* layers — not
   its current surface — that surfaces "what did we try and erase, and what
   keeps recurring" as **craft** the summon hands at wake. The whiteout and
   the un-inked fold (step 2) are its inputs; the slow loop is its natural
   consumer (it would fold the journey, not the snapshot). This is the
   part that turns memory + meaning into experience — the thing that lets
   the hand get better, currently absent. Largest of the six; the first
   five make it possible.

Nothing here is a new subsystem. Every step is *a label, a fold, or a
boundary on an existing pen* — because the ink machinery is already built;
the work is naming the two marks on either side of it.

## What a session (and the owner) inherits at wake

Today summon hands a janitorial gap. Under this framework it hands a
**stage-aware situation**:

> *3 marks of pressure. **Sketch un-inked:** 50 branch commits + 14
> Causality increments carry no atom — exploration that never became truth;
> ink them, or whiteout them so the ghost stays to learn from. **Ink
> leaking:** the merge-node has 22 landings no admission ever named —
> provisional hand, permanent mark. **Paint on the wrong wall:** owner-asks
> sit in report files bdo never opens — done, but unreadable. Top stroke:
> ink the off-log gate (it makes the un-inked countable).*

The owner inherits the same, colored for him: *the un-inked is the
agents' work; the unreadable paint is mine to receive; one fence-stroke
unblocks the colorist.*

## Resolved — the decided path (bdo, 2026-06-19)

The five questions are closed; the calls are recorded here so the build
inherits them from the record, not from chat. They are carried into
`epic.three-marks` (this proposal's arc).

1. **"Mark" status → a *fold label* first, not doctrine.** The folds attach
   the mark; the one-sentence doctrine extension is promoted only after the
   label proves it reads true against the live backlog. (Marks are proposed,
   not minted — language/CLAUDE.md grain.)
2. **Sketch governance → unchanged.** Naming the sketch surface does not
   change *who* may ink: the inker is still the gate (D-2). We only make
   un-inked sketch *countable*, not differently-governed.
3. **Un-admitted writes → accept-and-stamp sketch.** A write by an
   un-admitted actor is accepted, stamped `mark: sketch`, and folded as
   un-inked pressure until an `admit-real` inks the actor — never refused at
   the seam (refusal would strand work the way the merge-node's 22 landings
   were stranded). *This is the call that sets the system's character.*
4. **First build scope → a full epic with a done-line series** (`epic.three-marks`),
   wave-ordered, so all five build steps have a home. (bdo chose the fuller
   frame over a single done-line — the whole frontier visible.)
5. **The pentimento/sauce part → its own arc, after waves 1–2.** It
   graduates out of this epic into `epic.pentimento` (the palimpsest fold →
   craft) once the sketchbook gives it something comparable to read. *Naming
   note:* the existing `epic.experience-layer` already binds the word
   **"experience"** to a different sense (a launched, bounded encounter that
   ends in an authored story). This part's "experience" (memory made
   comparable) is a genuine **overload** to reconcile — which is why its arc
   is named for its mechanism (*pentimento / palimpsest*), not "experience."

## What this touches, and what it does not

- **Composes with, does not replace** the pens, `gaps.py`, `orchestrate`,
  the reflect beat, and the outcome-pressure fold — it *names the stages*
  those already operate in, and ranks across them.
- **Adds exactly one small write path** — the cheap **sketch primitive**
  (a draft mark on the log, paired with the existing whiteout as its
  eraser). Everything else is a label, a read-only fold, or a boundary on
  an existing pen; the ink machinery is untouched. (Earlier drafts of this
  proposal said "no new write path" — that was wrong: the sketchbook needs
  one. It is the only one.)
- **Extends the doctrine by two sentences** if adopted, not one — and the
  second is the larger:
  1. *the marks:* "A pen is the ink of a three-mark making — sketch
     (provisional, erasable), ink (committed, receipted), paint (additive,
     surfaced) — and a flaw is a mark made in the wrong stage."
  2. *the pentimento:* "State is a fold over the log's surface; **experience
     is a fold over its palimpsest** — the superseded and abandoned layers
     — and a loop that keeps no such fold has memory and meaning but cannot
     get better." This is the load-bearing one, and the bigger commitment.

---

*The decisions are closed (above) and carried into `epic.three-marks`. The
line is primed: wave 1 is the mark-label on `loop.gaps` plus a sketch
primitive on the log and an `un_inked()` fold with one summon line — the
smallest thing that puts the sketchbook back in the book, so a waking
session sees the 50 stranded commits as comparable sketch instead of a
silent strand. The session that picks up wave 1 writes its done-line and
builds; bdo confirms the arc (`confirm-arc`) to authorize landing. The
pentimento part that keeps the sauce graduates to `epic.pentimento`,
after.*
