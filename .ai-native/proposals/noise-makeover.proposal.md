# The noise make-over — the blueprint bundle (PROPOSED)

> Status: **PROPOSED** — a blueprint for bdo to address, authored 2026-06-22 at
> his direction. This is the *bundle* (blueprint-before-build, the hard rule
> #348/CTA-3): full shape → categorized concept-list → calls-to-action against a
> purpose. The mechanism is built under this bundle (waves 1–2); the **standing
> permission that lets it act on its own is bdo's stamp** and is NOT taken here.

## bdo's words (2026-06-22)

> "make more beautiful elaborate fold and large inferences to make over more
> useful sounds and permission to silence noise by upgrading the system
> producing it."

Confirmed via a comprehension checklist, with two corrections:

- **CONFIRMED — emit useful signal, don't just hush.** The upgraded surface must
  *produce* something genuinely useful, not quietly close issues.
- **CONFIRMED — standing permission to auto-silence.** A bounded standing
  authorization to silence noise on its own — but only what the record proves,
  escalating the genuinely-unresolved.
- **DESELECTED (a correction, not a rejection)** — "a self-closing fold not a
  sweep" and "inference as a resolution-judge+cite". The corrected reading: the
  **large inference is a TRANSFORMER that makes the noise *over* into a useful
  sound** — not a minimal close-gate. The *outcome* (useful synthesized signal +
  bounded auto-silence) is the point; do not be dogmatic about the mechanism.

## The why (the target)

bdo's GitHub inbox accretes. Two surfaces have an **automated OPEN path and a
manual / in-process-only CLOSE path**, so they only ever grow:

- **owner-ask mirror issues** (`loop/owner_asks.py` → `reflect.owner_ask_drift`):
  one issue per report's `needs-you` section. Open-only by construction — a
  free-text ask carries no log-backed "answered" signal, so the mirror never
  closes itself. Nine stale ones stand today.
- **gate-run tracker issues** (`.claude/skills/gate/gate.py`): one per headless
  run, opened at the process's *birth* (bdo's trust rail). It closes only from
  *inside the producing process* — so if that process dies after the verdict
  lands, the tracker **strands open** though the work is settled on the log.

Root cause, one sentence: **a surface with an automated open and no automated,
record-backed close can only accrete.** Related, on the record: **#628** —
"unresolved work should iterate to a named conclusion, not silently park."

The purpose every CTA serves: **a noisy surface is *made over* into one
synthesized, organized, useful read; the raw noise the record proves resolved is
silenced on a standing authorization; and what is genuinely unresolved iterates
to a named conclusion (#628) instead of stranding.**

## The full shape — open, prove, transform, silence-or-escalate

```
  raw noise (open issues + parked asks)
        │
        ▼
  [W1 resolution reading]  per subject: resolved-by-record?  ──┐
        │  owner-ask → its "confirm epic.X" maps to an         │ TEETH: a close
        │              arc_confirmed admission (a cite)         │ with no provable
        │  gate-tracker→ its atom has a settled value verdict   │ resolution on the
        │              on receipts.jsonl (a cite)               │ log is REFUSED —
        ▼                                                       │ it stays open and
  [W2 transformer]  a free-text ask that maps to no log event  │ ESCALATES to a
        │  → route ask text + log span through the inference   │ named conclusion
        │    gateway → resolved? + the cite + a one-line        │ (#628). The cite
        │    synthesized "useful sound"                         │ must resolve on
        ▼                                                       │ the log or the
  [emit]  ONE synthesized digest line (the useful sound)  ◄────┘ discharge refuses
        │  + close-with-reason each PROVEN-resolved issue
        │    (issue pen) + discharge each resolved owner-ask
        │    (reflect.discharge_owner_ask, its cite teeth)
        ▼
  [silence-or-escalate]  proven → silenced under the fence;
        unproven → named in the digest line, left open (#628)
```

## The categories (label · description · today · the gap)

**N1 — The resolution reading (the fold).** *Per open noise subject, is it
resolved by the record?* Today: nothing reads it; the owner reads each issue by
hand. Gap: there is no fold that crosses the open surfaces with the log and
answers "resolved / not, and by which record." This is the make-over's eyes.

**N2 — The useful sound (the emit).** *What the make-over produces instead of
silence.* Today: closing an issue (when it happens at all) emits nothing
organized — bdo sees a closed issue, never a synthesis. Gap: the make-over must
emit **one synthesized read** — "reconciled N owner-asks (all arc-confirmed),
M settled gate runs closed, K genuinely still need you: «named»" — wired into the
owner digest, so the noise becomes *signal*.

**N3 — The transformer (the large inference).** *A free-text ask that maps to no
single log event still has a meaning in aggregate.* Today: it strands forever
(no log-backed answer). Gap: route the ask text + the relevant log span through
the **inference gateway** (`loop/inference.py`), which returns resolved? + a cite
+ a one-line synthesized description of what these asks *actually meant*. The
teeth hold over the inference output — a hallucinated cite is refused like any
other.

**N4 — The teeth (§10).** *A close that the record does not justify must be
refused.* Today: `reflect.discharge_owner_ask` already refuses a discharge whose
cite is absent from the log — the make-over reuses exactly that. Gap: extend the
same refusal to gate-trackers and to inference output, and prove it non-vacuous
(a fabricated "resolved" claim with no backing record is caught; a
locally-fine-but-unresolvable ask stays open and escalates).

**N5 — The standing permission (the fence, bdo's stamp).** *A bounded standing
authorization to auto-silence what the record proves.* Today: nothing; every
close is manual. Gap: a `noise_silence_fence` admission (the disposer-fence
shape, done-line 0091) — **default-INERT until bdo stamps it `--by bdo`**. Once
drawn, the make-over self-silences proven-resolved noise (cooling — the safe
direction), and anything unproven escalates (never auto-closed). The loop
*executes* bdo's standing stamp; it never signs its own line (the
merge-node / confirm-arc shape).

**N6 — The upgrade to the producer (bdo's "upgrade the system producing it").**
*Close the open-only hole at the source.* The make-over is the reconciler; the
deeper fix is that the gate-tracker's close should not depend on the producing
process surviving. N1's idempotent reading **is** that upgrade for the
tracker: a settled verdict closes the tracker regardless of which process (or
none) produced it. Named here; the owner-ask producer's own close-signal is a
later increment (it has no log-backed "answered" today by design — N3 is its
bridge).

## The fixed generative concept-list (what to ponder)

1. Is "resolved-by-record" the right bar for auto-silence, or should some kinds
   always escalate? (N1 + N5)
2. What is the right grain of the **useful sound** — one digest line, or a
   per-group synthesis? (N2)
3. Should the **transformer** ever propose a cite the human must confirm, or only
   ever a cite that already resolves on the log? (N3 + N4)
4. What does the **fence** bound — a count cap per run, a per-kind on/off, a
   confidence floor on inference output? (N5)
5. Is auto-silence **cooling-only** (silence proven-resolved) with everything
   unproven escalating — the disposer's asymmetry — the right safety shape? (N5)
6. What is the named conclusion an unresolved ask **iterates to** (#628) — a
   re-opened owner-ask, a new atom, an arc? (N4 + N6)

## Calls to action (against the purpose)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-1 | Build the **resolution-reading fold** (`loop/reconcile_noise.py`): per open noise subject, resolved-by-record? with a cite. Read-only. | session-built (W1) | N1 |
| CTA-2 | Build the **useful-sound emit**: one synthesized digest line + close-with-reason through the issue pen + discharge through `reflect.discharge_owner_ask`. | session-built (W1) | N2 |
| CTA-3 | Make the **gate-tracker close idempotent**: a settled verdict closes its tracker regardless of producing process. | session-built (W1) | N1, N6 |
| CTA-4 | Prove the **§10 teeth** non-vacuous (`tests/test_reconcile_noise.py`): a fabricated resolution is refused; a genuine one discharges with its cite. | session-built (W1) | N4 |
| CTA-5 | Build the **transformer** (`transform_unresolved`): route a free-text ask + log span through the inference gateway, gated + degrading; teeth hold over its output. | session-built (W2) | N3, N4 |
| CTA-6 | Draw the **`noise_silence_fence`** (default-inert) and gate auto-silence behind it. Activation is **bdo's stamp**. | **bdo's stamp** | N5 |
| CTA-7 | Admit a **gateway policy** permitting the make-over's caller/surface/mind, so the transformer can reach a live mind. | **bdo's stamp** | N3 |

## Whose move

- **bdo decides / stamps** (not a session's to set): CTA-6 (draw the fence — the
  standing auto-silence authorization), CTA-7 (the gateway policy that lets the
  transformer think). Both are inert/absent until his gesture. A session never
  writes a `--by bdo` admission.
- **Session-built** (the mechanism, landed under this bundle through independent
  review): CTA-1…CTA-5.

## The activation gestures (bdo's, when he chooses)

```sh
# CTA-6 — draw the standing auto-silence fence (default cap 10 closes/run; cooling-only):
python -m loop.reconcile_noise admit-fence --max-closes 10 --by bdo

# CTA-7 — let the transformer reach a mind (default-deny gateway; one permit):
python -m loop.inference policy --caller noise-makeover --surface noise-makeover \
    --mind <mind-id> --by bdo
```

Until CTA-6 is stamped the make-over **reads and proposes only** — it silences
nothing. Until CTA-7 is stamped the transformer **degrades gracefully** —
free-text asks it cannot map are escalated by name, never guessed at.

## Worked inputs

- **#628** — unresolved work should iterate to a named conclusion, not silently
  park. The teeth (N4) and the escalation half (N5) are this rule, made
  mechanical.
- **`epic.owner-harness`** — bdo steering arcs and reading a data-rich surface
  *instead of operating the inbox*. The noise make-over is the inbox-hygiene
  organ that arc was always going to need.
- The nine stale owner-ask issues and the stranded gate-trackers — the standing
  noise this bundle exists to make over.

---

## How this composes (do not double-build — §10)

- **`reflect.discharge_owner_ask`** already holds the owner-ask close teeth (a
  cite must resolve on the log). The make-over *proposes* discharges; the pen
  *re-verifies* — the teeth are enforced on both sides, no second definition.
- **`loop/disposer.py`** is the fence shape (a bounded standing auto-admit citing
  the fence as `authorized_by`). The `noise_silence_fence` is its sibling on the
  silence axis — same asymmetry (cooling always allowed, unproven escalates).
- **`loop/digest.py`** is the owner surface the useful sound rides; the make-over
  contributes one summary line, never a second digest.
- **`.claude/skills/issue/issue.py`** is the only door to GitHub issue mutations;
  the actuator closes through it, never raw `gh`.
- **`loop/inference.py`** is the only model-reaching plane; the transformer goes
  through it, default-deny honoured.
