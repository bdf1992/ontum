# Report 0069 — The harvest line: a stopping point becomes a harvest, not a halt

## What this is

bdo, 2026-06-16: "if a loop maker hits a stopping point they should be creative."
That correction landed after I went idle at the run's convergence. This report
closes the harvest line that answers it — built live, in conversation with bdo,
who sharpened the design at each step.

## The idea, as bdo shaped it

- A stopping point is not a halt; it is a trigger to **farm** the system for
  signals and potential, based on the operation of its **teeth** (the §10
  refusals). A tooth firing is a sensor reading of negative space.
- The harvest is **named** into **seed** and **grain** — but these are not two
  buckets. They are **states of one harvested signal**, named by the process it
  has passed through (meteor vs meteorite): a **grain** is seed through another
  process (a *grain of insight*, consumed now); a **seed is not automatically
  planted** — planting is a deliberate, separate hand.
- The cut is **generativity**: grain *ends when used*; seed *generates when
  planted*. Recurrence is the tell, not the definition.

## The audit (against what exists and is possible today)

Before building, audited the three states against the repo — and it changed the
build order. `plant` (admission, D-4) and `thresh` (the gaps.py grain) already
existed to reuse. The real gaps: **no Pattern Commons is homed in ontum**, and —
the headline — **the teeth refused but recorded nothing.** "The refusal is the
signal" is empty if the signal does not land. So the first buildable piece was
not `harvest`; it was making the teeth leave a mark.

## What landed (the harvest line, on PR #153)

- **Step 1 — signal-mark (done-line 0092).** `loop/signals.py` lands each
  teeth-firing as a foldable signal (state `seed`) on `.ai-native/log/
  signals.jsonl`, reusing the one append path (content-hashed, torn-tail
  tolerant, absent-empty). The three teeth (loopmaker Stop, cited_sensor ghost,
  reversibility_gate block) now mark at an `operate()` seam; the pure folds stay
  pure. 9/9, and the 22 teeth tests unchanged.
- **Step 2 — seed-bank (done-line 0093).** `loop/seedbank.py` banks a harvested
  shape as a **proposed** pattern; planting is a deliberate second hand, reusing
  the proposed→admitted grain. Teeth (8/8): planting is refused unsigned (not
  automatic), unbanked, and by the proposer (no one plants their own seed, D-4).
- **Step 3 — harvest (done-line 0094).** `loop/harvest.py` folds the recorded
  signals on a `Stop` and sorts by generativity: one-off → grain (consumed),
  recurring → seed (banked proposed). It composes signals + seedbank + loopmaker;
  it **never plants** (5/5; the full bank→plant lifecycle proven). 44/44 across
  the whole harvest line + teeth; full suite green.

## The horizon, recorded not built

**Autonomous planting** — bdo: "eventually we want autonomous planting but of
course we need the loop prepared for such tasks." Recorded as a fenced horizon:
an in-fence seed self-plants once the loop is trusted, the **PR #163 bounded
auto-admit fence** applied to the Commons; out-of-fence still needs a gesture.
Not built; named as the next probe.

## A real seed already in the bank, unplanted

The harvest's first true crop: the **absence-refusal** pattern — *refuse on
absence; the refusal is the signal* — recurred across all four original nodes.
It sits in the seed bank as **proposed**, unplanted, because I have not bdo's
stamp for it. That is the discipline working: the bank fills on its own; the
field is planted by choice.

## needs-you

One gesture, unchanged: **confirm the arc `epic.digital-experience`** — it now
carries probes P1–P8 (the slice + the harvest line). One stamp authorizes the
whole arc; the merge-node then lands PR #153.

## End-state

`report` — the harvest line is built and green on PR #153: a stopping point is
now a harvest (teeth leave a foldable mark → seed-bank holds proposed patterns →
harvest sorts grain/seed on a Stop), planting stays a deliberate hand, autonomous
planting is a recorded fenced horizon. The braid carried it (loop-maker derived
each piece); 44/44 + full suite green; one gesture pending: arc-confirm.
