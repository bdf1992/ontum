# The ledger verb family — record-grain and book-grain operations (PROPOSED)

> Status: **CONFIRMED → `epic.ledger-verb-family`** — bdo named it official in chat
> (2026-06-24). The arc is `.ai-native/epics/epic.ledger-verb-family.json`; this
> proposal stays as the record of where the arc was born. His confirmation greenlit
> the safe-foundation pieces; the two invariant-touching CTAs (CTA-2 Mend actuator,
> CTA-3 Rotate epoch) are held as the epic's gating decisions, awaiting his explicit
> further stamp.
>
> Authored 2026-06-24 from his chat ("Append / Mend / Amend … what else do people do
> to ledgers? … produce receipt about their ledger, and handle and audit over it").
> This is the *bundle*,
> not an increment: full shape → categorized → labelled → a generative concept-list
> → calls-to-action against a purpose. Nothing here is built. It composes existing
> parts (§10) — it names them, it does not rebuild them.

## The why (the frame)

The substrate has exactly one write — `append_line` — and a firm law over it:
**superseding, never erasure; history is never retro-invalidated.** That law is
not a constraint to work around; it is the *anti-cooking-the-books guarantee* —
the reason byte-identity, torn-tail safety, and receipts-as-history all hold.

bdo named a set of things "people do to ledgers" that the system cannot do today.
Read against the law, they sort into two grains and one governing triangle:

- **record-grain verbs** — operations on a single *line* (Append · Mend · Amend).
- **book-grain verbs** — operations on the *whole book as an object* (Cool · Fork ·
  Bookmark · Highlight · Rotate · Carry-forward).
- **the governing triangle** — each operation must **produce a receipt**, the book
  must be reachable by a **handle**, and an **audit** fold must re-derive the chain.

The insight that makes this buildable: the record-grain already lives by that
triangle (act → receipt, atom → sha256 identity, census/digest/heal → audit fold).
The book-grain *inherits the same discipline one level up*. **The ledger becomes an
atom** — a whole that is also a part of the chain of books. It is the holon, and it
is the same physics fractally, not new physics.

The purpose every CTA serves: **the books can grow, change, close, and reopen
without ever being cookable — and every such move carries its own proof.**

## The full shape — two grains, one triangle

```
  RECORD-GRAIN (a line)                 BOOK-GRAIN (the whole book)
  ─────────────────────                 ──────────────────────────
  Append  add a fact          ┐         Cool        quiet a book
  Amend   revise a prior      ├─ all    Fork        copy a book (recorded)
  Mend    repair a bad bite   ┘ appends Bookmark    named anchor at a position
                                        Highlight   decoration lens over records
                                        Rotate      close book N, open N+1 (new template)
                                        Carry-fwd   closing fold → opening record

  THE TRIANGLE (governs both grains)
  ──────────────────────────────────
        receipt ──proves──► the op was faithful (carries the hashes)
           │
        handle  ──identifies──► the book (sha; book N's handle named in N+1)
           │
        audit   ──re-derives──► the chain; a cooked book fails because hashes don't chain
```

Everything in both grains is still an **append**. The verbs differ only in their
*back-reference* and *blast radius* — and that difference is exactly what policy
gates (who-may) and inference estimates (what-it-touches, via the consequence
graph). Append is forward-only and safe by construction; amend, mend, rotate, and
carry-forward propagate backward into things already decided, and the triangle is
how that propagation stays witnessed, bounded, and reversible.

## The categories (label · description · today · the gap)

### Record-grain

**V1 — Append.** *Add a fact.*
- Today: the floor. `append_line`, three logs, fold picks it up next pass.
- Gap: none — this is what is. It is named only to measure the others against it.

**V2 — Amend.** *Revise what a prior record means, without erasing it.*
- Today: exists **unevenly, per-pen** — `confirm-arc --off`, `node_real --off`,
  `done_superseded`, surface superseding; atoms version by editing bytes (pipeline
  restarts, old receipts stand as history).
- Gap: no *uniform* amend record (what it revises · why · who · what cascades). The
  danger if generalized carelessly: in-place edit = erasure. `freeze_guard` and the
  carbon-copy `write_guard` already refuse the in-place form — amend must stay a
  **typed forward append carrying a back-pointer**.

**V3 — Mend.** *Repair where a tooth bit wrong.*
- Today: `heal.py` **senses** the over-bites (stale-park, flapping-gate,
  owner-override) but is **propose-only by design** (D-4): "it never clears a park."
  The actuator was explicitly deferred — "a bounded actuator, if it ever comes,
  rides the disposer fence."
- Gap: the actuator heal points at does not exist. `disposer.py` is its template (a
  bounded standing auto-admit inside a fence bdo draws). **Whether Mend gets an
  actuator at all is the one real change to the "loop never clears its own park"
  stance** — bdo's call.

### Book-grain

**V4 — Cool.** *Quiet a book — slow or still its activity.*
- Today: half — `orchestrate`'s cool valve cools the *rate* (steps per tick), not
  the *book*. (`retro.py` notes cool ran 0 of 91 ticks — a declared-but-untaken
  valve.)
- Gap: no notion of a book *being in a cooled/quiet state* as a recorded fact.

**V5 — Fork.** *Copy a book as a recorded act.*
- Today: physically yes (git branches/worktrees; `forest.py` senses the forest),
  but the *meaning* "I forked this ledger, here, for this purpose" is a side effect,
  not a record.
- Gap: a fork is not on the books. The handle (V-triangle) is what would make a fork
  a first-class, traceable act.

**V6 — Bookmark.** *A named, durable anchor at a position.*
- Today: no. `offsets/` are cache (a fold position), not named records; an atom id
  is a content handle, not a position handle.
- Gap: no "remember this point, I'll refer back to it" record. A bookmark = an
  admission naming a log position (or an atom set) for later reference.

**V7 — Highlight.** *A non-mutating decoration lens over records.*
- Today: half — `forest.py` and the forest-mask (PR #693, a FileDecorationProvider)
  tag *files* by attention; the highlight idea applied at *record* grain is absent.
- Gap: no lens that marks records salient without touching them. By design
  non-mutating — the cheapest verb, pure read-side.

**V8 — Rotate.** *Close book N, open book N+1 — possibly with a new template.* **— the load-bearing one.**
- Today: **no.** The entire design folds over *all* of history as one continuous
  log. There is no epoch boundary and no schema-migration path.
- Gap: this is the only verb that touches the deepest invariant ("fold over all
  history"). It introduces **epochs**: seal book N as immutable archive, open N+1,
  and the "new template" is a real **schema migration** — the thing that cannot be
  done today without rewriting bytes (which `.gitattributes`/byte-identity forbid).

**V9 — Carry-forward.** *The closing balance becomes the opening balance.*
- Today: no — but `reconcile.py --rebuild-cache-only` is the shape (fold to a
  state), and the digest's `atoms_on_main` (D-13) is the join-by-id precedent.
- Gap: the accountant's trick that makes Rotate safe — **the closing fold becomes
  the opening record.** You fold book N to its closing state *once*, write that as
  the opening balances of N+1 (a real recorded fact, not a throwaway cache), and the
  archive stands as immutable, re-derivable history. This bounds the unbounded log
  and lets the template evolve **without erasing a line.**

### The governing triangle

**T1 — Receipt about the ledger.** *The proof a book-op was faithful.*
- Today: receipts are about *atoms* (`(node, artifact_hash)`). No receipt kind is
  about the *book*.
- Gap: a `ledger_rotated` / `ledger_forked` / `ledger_mended` receipt that carries
  the *closing-fold hash* + *archive hash* + *back-pointer* — the receipt *is* the
  "proof you didn't cook the books," re-derivable by anyone.

**T2 — Handle.** *The book's identity, the way sha256 is an atom's.*
- Today: no — the log is "the three files at this path," nameless.
- Gap: a content-addressed handle per book; **book N's handle is carried into N+1 as
  its parent → a hash chain.** Carry-forward stops being "trust me" and becomes
  tamper-evident by construction. (The structure of a hash-chained ledger — named
  for what gives the audit teeth, not for the buzzword.)

**T3 — Audit over it.** *The fold that re-derives the chain.*
- Today: the *grain* exists — `census`/`digest`/`heal`/`parity` are read-only audit
  folds, and "audit" is already a word here (`pr.py audit`,
  `pr_audit.orphan_reason`). None audits the *book chain*.
- Gap: `loop/audit.py` (sibling of census/digest/heal) walks the handle chain and
  re-derives each claim — does book N's closing-fold hash to what its rotation
  receipt says? does N+1's opening match? does every amend resolve its back-pointer?
  The §10 teeth: **a cooked book fails the audit because the hashes don't chain**; a
  constant auditor is caught by a fabricated rotation (the term-economy ghost
  refusal, on book-ops).

## Why the triangle is the keystone (the anti-fraud reading)

bdo's "they cook them, lol" is the serious part. Amend, Mend, and Rotate are
*exactly* the operations that, ungoverned, let someone cook the books — erase under
an amend, silently fix under a mend, lose history under a rotation. The append-only
law is the anti-cooking guarantee, and the triangle is what makes it **enforceable**
rather than hoped-for:

- the **receipt** is the claim,
- the **audit** verifies the claim,
- the **handle** ties claim to object.

So the book-grain verbs are not governed one at a time. They are all governed by one
triangle: every book-op produced a receipt, the receipt chains through the handle,
the audit re-derives it. **Every new verb carries the proof it didn't cook the
books, or it doesn't land.**

## The fixed generative concept-list (what to ponder)

1. Is the **revision family** (Append/Amend/Mend) one typed record kind —
   `{verb, targets[], because, by}` — that all pens emit, replacing per-pen
   superseding? (V2 + V3)
2. Does **Mend get an actuator** (a fenced, witnessed repair), or stay propose-only
   forever? The one real change to "the loop never clears its own park." (V3)
3. Is **Rotate** worth the new invariant (epochs + closing-fold-as-opening-record),
   and what triggers a rotation — size, time, or a schema change? (V8 + V9)
4. Does a book get a **handle**, and is the handle a hash chain (each book naming its
   parent)? (T2)
5. Are **Bookmark / Highlight / Fork / Cool** worth being first-class recorded acts,
   or do they stay informal? (V4–V7)
6. Does **inference estimate the propagation** of an amend/mend/rotate *before* it
   lands, by pointing the consequence graph (radius-2, typed, decaying) at its
   targets? (the whole propagation question)
7. Is the **audit over the book chain** a standing fold surfaced ambiently (like
   gaps/heal), or run on demand? (T3)

## Calls to action (against the purpose)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-1 | Define **one typed revision record** — `{verb: append/amend/mend, targets[], because, by}` — that pens emit instead of hand-rolling superseding. The unifying primitive. | bdo decides → build | V2, V3 |
| CTA-2 | Decide whether **Mend gets a bounded actuator** (riding the disposer fence, witnessed), or stays propose-only. The one stance change. | **bdo's stamp** | V3 |
| CTA-3 | Define **Rotate + Carry-forward** as the book-grain spine: epoch boundary, archive-immutable, closing-fold-as-opening-record, new-template = schema migration. The one new invariant. | **bdo's stamp** (doctrine) → build | V8, V9 |
| CTA-4 | Give a book a **handle** (content-addressed), and chain handles (N's handle named in N+1) so carry-forward is tamper-evident. | build | T2 |
| CTA-5 | Add **ledger-op receipts** (`ledger_rotated`/`forked`/`mended`) carrying the closing-fold + archive + back-pointer hashes — the anti-cooking proof. | build | T1 |
| CTA-6 | Build **`loop/audit.py`** — the book-chain audit fold (sibling of census/digest/heal), §10 teeth: a cooked book fails because hashes don't chain. | build | T3 |
| CTA-7 | Make **inference read propagation before a revision lands** — point `consequence_graph` (radius-2, typed, decaying) at the revision's `targets`. | build | concept 6 |
| CTA-8 | Make **Bookmark / Highlight / Fork / Cool** first-class recorded lenses/anchors (cheap, additive, non-invariant-touching). | bdo decides → build | V4–V7 |

## Whose move

- **bdo's stamp** (invariant- or stance-changing, a session won't decide): CTA-2
  (Mend actuator), CTA-3 (the Rotate invariant + doctrine), and naming the arc.
- **Session-buildable** once a decision points the way: CTA-1, CTA-4, CTA-5, CTA-6,
  CTA-7. (CTA-6 audit and CTA-4 handle are pure read/append folds — safe early
  increments that compose existing grain.)
- **bdo decides → build** (additive, low-risk): CTA-8.

The spine, if confirmed: **CTA-3 (Rotate + Carry-forward)** with **CTA-4/5/6 (the
handle/receipt/audit triangle)** as its enforcement; the revision family (CTA-1/2)
and the cheap lenses (CTA-8) hang off the same triangle. It spans two grains, so it
graduates as an **epic**, not a done-line.

## Composition (compose, do not double-build — §10)

ontum already holds the parts under other names; this proposal wires them, it does
not rebuild them:

- `reconcile.py` — `append_line` + `Fold`: the floor every verb appends to.
- `heal.py` — the **Mend sensor** (propose-only); its over-bite detectors are V3's
  input. `disposer.py` — the **fence template** a Mend actuator would ride.
- `consequence_graph.py` — the **propagation engine** (bounded, typed, decaying,
  radius-2) inference points at a revision's `targets` (concept 6 / CTA-7).
- `census`/`digest`/`heal`/`parity` + `pr.py audit` — the **audit-fold grain** and
  the existing "audit" vocabulary `loop/audit.py` joins (T3).
- `atoms_on_main` (D-13) — the **join-by-id precedent** for carry-forward (V9).
- `freeze_guard` / `write_guard` (carbon-copy) — already **refuse in-place edits**,
  the guard that keeps Amend a forward append, not erasure (V2).
- `forest.py` / forest-mask (#693) — the **decoration precedent** for Highlight (V7).
- `tags.py` — the **governed-vocabulary precedent**: the revision `verb` set could be
  a governed dimension (core closed in code, values admitted), not a code literal.
- The **superseding** acts (`confirm-arc --off`, `done_superseded`, surface
  superseding) — the **existing, uneven Amend** that CTA-1 would unify.

---

# Plain English

bdo listed things people do to a ledger: add to it, fix it, revise it, copy it,
bookmark it, highlight it, close an old one and start a fresh one, carry the old
totals into the new book — and on top of all that, leave a receipt for each move,
give the book a name you can point to, and be able to audit the whole thing.

This file sorts those into two sizes. The small ones act on a single *line* (add,
fix, revise). The big ones act on the *whole book* (copy, close-and-reopen, carry
forward). The system today can only do the small ones, and even those messily.

The one that actually matters and is actually hard is **closing a book and opening
a fresh one**: total up the old book, write that total as the first line of the new
book, and file the old one away unchanged. That's how the log stops growing forever
and how the format can change — without ever destroying old records.

And the part that makes it all trustworthy: every move leaves a *receipt* that
proves it was honest, every book has a *fingerprint*, and an *audit* re-checks the
chain of fingerprints. If anyone tampered with an old book, the chain breaks and the
audit catches it. The reason the system never erases anything is to make cooking the
books impossible — so each new ability has to come with proof it didn't.

The good news: the system already works exactly this way for single records. This is
the same pattern, one size larger. The two things that are genuinely your call: (1)
should the "fix a bad rule" move be allowed to act on its own, or only ever suggest?
and (2) the "close and reopen the book" move needs a new rule, so it needs your
stamp. Everything else I can build once you point the way. This is written down now
so it survives past this chat.
