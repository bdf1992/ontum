# Judgment as a narrative, told over rounds (PROPOSED — bdo's, 2026-06-21): the gate is a fold, not a verdict

**Status:** PROPOSED. **Naming and the arc are bdo's (D-4); a session may only
propose.** Born from the 2026-06-21 design conversation: *"make the judgement
call progressive and iterative … a narrative told over time, built up … so it
can be audited, a review we can enhance and recover … the first judgement is
harsh … they have to provide evidence to be judged and that takes work … like
the DMV … the information you bring back might trigger another round because we
didn't HAVE that information — and that's a judgement call."* Companion proposal:
[`consequence-graph.proposal.md`](consequence-graph.proposal.md) (the propagation
engine this rides) and `gate-policy-facts` (PR #343, the deterministic/judgment
seam this names). This file is the spine; the per-piece tools land later, one at
a time, each citing it.

## The reframe: judgment is a point function today; this makes it a fold

Today `loop.node judge` writes **one verdict** per `(node, artifact_hash)`.
Write-twice is a no-op by design. Editing an atom mints a new `artifact_hash`
and **restarts the pipeline from scratch**; the old receipts become disconnected
history. So judgment today is **single, terminal, and amnesiac across versions** —
a v1 harsh-refuse and a v0 loose-pass are two unrelated facts, not one story.

This proposal inverts that shape. **A judgment is a fold over an accreting,
evidence-bearing round-lineage** — exactly the way atom-state is already a fold
over the log. The pipeline still acts on one *current standing* (the derived
verdict), but the standing is computed from the whole narrative, and the
narrative is the audit. No second truth: the rounds are the record, the verdict
is the fold.

This is not new machinery. `herald.py` already does judgment-as-narrative for
*agents* — "exemplars net against notorieties … standing only ever earned
forward, recomputed from records, never asserted." This generalizes that fold
from credentials to **work**.

## Harsh-first is emergent, not configured

The first round is the harshest — but nobody sets a "severity = high" dial. It
falls out of two facts:

- **The requester carries the burden of evidence** (proof-carrying: producing
  the proof is expensive, *checking* it is cheap and deterministic). This is the
  asymmetry the whole repo already lives by — `no receipt, no version bump`,
  `no evidence, no mint` (term-economy), the off-log gate demanding a backed
  atom, the phrasing door that *proves* prose-only. We generalize the receipt
  discipline to the front door of every request.
- **Thin or defective evidence honestly fails.** At first contact a requester has
  shown almost nothing, and with the bulk of a real submission it is *statistically
  near-certain* that one piece is wrong. So the deterministic check truthfully
  rejects. The same check **passes** once the evidence thickens. Harshness is the
  honest read of thin evidence, not a configured cruelty.

The bar itself is **inferred from the requester's situation against a bounded
policy set** (inference-as-composition; the load-bearing word is **bounded** —
the policy set is the leash that keeps the inferred bar auditable, not
hallucinated). Inference *composes* which requirements apply; a deterministic
check *applies* them. That is exactly the seam PR #343 names — "deterministically-
composed policy facts; judgment non-deterministic, the data is."

## The DMV: a round is a whole round, and a round is an atom version

Rejection is a **whole new round**, not a patch at the counter. That cost is the
teeth — it front-loads diligence. A counter-patch (the gate fixes it for you)
would collapse the requester's burden back onto the gate and kill the pressure.
Whole-round is deliberate expense.

And it grounds in mechanics that already exist: **a round is an atom version.**
Editing an atom restarts its pipeline — that is whole-round, today, in code. What
this proposal adds is making the **version lineage a coherent narrative of
rounds** (round 1 rejected for X → round 2 fixed X, Y surfaced → round 3 cleared)
instead of the amnesiac disconnected receipts it is now. The lineage **is** the
"told over time."

## The anti-DMV tooth: every round returns the complete gap *given current knowledge*

The DMV's actual cruelty is **serial defect discovery** — it flags one problem,
you fix it and drive back, and *now* it flags the next one it could have told you
the first time. Rounds spent on the gate dribbling out what it already knew are
pure waste. So a new round splits two ways, and the split matters:

- **Withholding (a bug).** Same information, the gate flags something it could
  have flagged last round. This is deterministic to catch — it is `heal.py`'s
  **flapping-gate** detector, a gate contradicting its earlier self. A round of
  this kind is illegitimate.
- **Latent-activation (legitimate).** The evidence you brought back carried
  information you **didn't have** before, and that information crosses a threshold
  / triggers a policy that requires another document. The bar genuinely could not
  be computed until your evidence revealed your situation. Even a perfect,
  maximally-diligent requester trips these — which is what *rescues the fairness*:
  harsh-first is not punishing ignorance of the knowable, the requirement was
  latent in facts not yet surfaced.

So the rule on the wall: **return the complete currently-detectable gap, every
round.** The only legitimate new defect in round N+1 is one that became checkable
*because round N's evidence unlocked it.*

## Where determinism ends and judgment begins (the keystone)

Deciding which of the two a new round is — did the new information genuinely
cross the threshold, or did the gate just withhold — **is the irreducible
judgment call.** This names the precise seam:

- **Deterministic:** does this evidence satisfy this slot? does this fact match
  this policy literal?
- **Judgment (non-deterministic):** did the new information **cross the
  threshold** that activates a latent requirement?

The gate is mechanical on slot-checks and literal-matches; it is a *judgment
call* on threshold-crossing. Everything else can be deterministic, which is what
makes the whole thing buildable instead of hand-wavy.

## Propagation is signed: documents tighten *or* relax — harshness is the emergent envelope

The threshold-crossing cuts **both ways**, by the same latent mechanism. A
document can **activate** a latent requirement (it reveals you are in a stricter
branch -> tighten) *or* **obviate** one (it proves an exemption -> a whole class
of downstream documents drops away -> relax). The framing above leaned on
activation, the ratchet-up; the symmetry is the point -- *bringing a document
mostly lessens the policy.* Harshness scales **back** as evidence arrives, by the
very latent structure that could also raise it.

So harshness is not a ratchet. It is the **emergent net field** of activations and
obviations over the current evidence -- *mark-to-market for the bar*: continuously
re-valued, up or down, by what the evidence connects to *now* (the consequence
graph's propagated field, [`consequence-graph.proposal.md`](consequence-graph.proposal.md)).

This sharpens *why* harsh-first, cleanly:

> At first contact nothing has been obviated yet, so the **strictest applicable
> envelope applies.** The bar is harsh because the situation is maximally
> under-determined -- and each document *narrows* which policy branch truly
> governs, usually relaxing it. **Default-strict-under-uncertainty, relaxed by
> proof.**

That is the same shape as the inference-gateway's default-deny and the
trust-ladder's deny-until-granted -- a conservative envelope that evidence opens.
And it is load-bearing, not merely elegant: **a policy that could only tighten
would reject everything -- the over-containment failure** (`over_containment.py`:
stable because never relaxed reads as *trivial*, not *predictive*). The obviation
direction is what keeps the harsh gate predictive, and therefore honest; the
relaxation is not a kindness bolted on, it is what makes the harshness
legitimate.

**Latent structure creates emergence:** the bar is emergent from latent policy x
evidence, never predetermined and never configured -- judgment's instance of the
self-assembling controller (bdo's control-theory framing). This is also why the
"setting" dial (above) tunes *how much evidence the situation requires*, never the
harshness directly: harshness is an output of the propagation, not an input to it.

## The engine already landed: bounded propagation through the policy mesh

What "your document reveals a fact that lights up a requirement a few hops away"
describes **is** bounded BFS propagation through a consequence graph. The atoms
landed this week under `epic.consequence-graph-response` — `bounded-bfs-
propagation`, `no-superspreader-no-lateral-smear`, `money-splits-before-
propagating`, `nonvacuous-acceptance-fixture` — are the *mechanism* for exactly
this. A document is not a slot-filler; it is an event that propagates through the
requirement mesh and may activate downstream obligations. *Judgment = run the
propagation, and judge the threshold-crossings it hits.*

This is why the proposal is mostly composition, not new code: the propagation
engine ([`consequence-graph.proposal.md`](consequence-graph.proposal.md)) and the
flapping sensor (`heal.py`) already exist.

## Evidence is two-tier — and it maps onto D-2 exactly

Determinism only holds if evidence is **typed and checkable**. "I tested it" is
prose; the gate cannot deterministically check it. So evidence splits:

- **artifact-evidence** — a test result, a file, a log record, a receipt.
  Checkable, cheap, deterministic. The harsh first wall checks *this*.
- **judgment-as-evidence** — for requirements an artifact cannot settle ("is this
  sound / well-designed?"), the only evidence is *another judgment*: the
  independent node's verdict, which then becomes a record on the narrative.

This is **D-2 (two acceptances), made concrete**: *earn your own acceptance
first* = assemble the artifact-evidence and clear the deterministic wall; *the
independent acceptance* = the judgment-evidence the wall cannot produce. Two
gates, yours then theirs — the first is now an evidence wall, the second is the
judgment.

And the wall cannot merely check *that* evidence is attached; it must check the
evidence is **non-vacuous** — real, not theater — or it falls to the prose-facade
/ over-containment failure mode (the §10 `nonvacuous-acceptance-fixture` the
consequence-graph atoms just landed; the over-containment counter-test in
`over_containment.py`).

## What matures over time (the "progressive" that isn't severity)

Severity does not escalate over rounds — *evidence accretes* until the bar is
met, and two slower things mature alongside it:

1. **The requirements-model is validated.** Was an inferred requirement
   **predictive** (its rejections correlate with what actually gets accepted
   later) or **trivial** (it just rejects everything)? That is the model-free-mode
   coherence machinery (`relation_ledger.py`, `over_containment.py`) pointed at
   requirements instead of representations. Harsh-first is the **data generator**
   that feeds it. A harsh gate that rejects everything is *trivial, not
   predictive*, and the coherence fold catches it — this is the answer to
   over-containment.
2. **Per-actor trust loosens the bar.** A requester who keeps clearing the harsh
   bar earns standing (`herald` reputation, `trust.py` ladder), so the gate can
   relax *for them*. The loosening exists — it is just earned forward, per-actor,
   not configured by round.

## The space this opens — setting, observation, dimension (bdo's three)

The point of the reframe was to "create the space" for these. Each becomes
first-class once judgment is a fold:

- **Setting** — the dial is not "how mean is the gate" but **how much evidence
  this situation requires** (the bounded inferred bar). An admitted record, like a
  setpoint, never a code constant — and consequence-scaled (higher blast-radius
  demands more evidence).
- **Observation** — a round can record *"evidence present but insufficient"*
  without a hard reject: a note in the narrative that is not a gate decision.
  Observable gates first (the model-free-mode invariant) — the gate can *witness*
  before it *verdicts*.
- **Dimension** — a verdict is no longer scalar. Evidence is per-requirement, so
  judgment is naturally multi-axis: each inferred requirement is a dimension with
  its own evidence and pass/fail, and the consequence-policy chain
  (Root→Cause→Effect→Consequence→Obligation→Policy) is how they relate.

## What this is NOT — the don't-double-build guard (§10, `parity`'s `dont-double-build`)

- not a new propagation **engine** — [`consequence-graph.proposal.md`](consequence-graph.proposal.md)
  owns the graph + marks + bounded BFS; this *judges over* it.
- not a new **truth** — rounds are the existing version lineage; the verdict is a
  fold; inferred requirements are PROPOSED and cite the policy they derive from; a
  citation that resolves to nothing is a `ghost` and is refused (the term-economy
  / parity tooth).
- not a new **withholding sensor** — `heal.py`'s flapping-gate already senses a
  gate contradicting its earlier self; this *uses* it as the anti-DMV tooth.
- not a removal of D-2/D-4 — your own evidence-assembly is your case and your
  standing; the independent acceptance still lands it; the owner is still the
  last stop.

## Open seams for bdo (the steer)

1. **The evidence-wall: artifact-only, or both?** Default (my lean): the harsh
   first wall checks **artifact-evidence only** and stays deterministic; the
   requirements an artifact cannot settle escalate to the independent node (D-2's
   second acceptance). Wave off if you want the wall to attempt judgment-evidence
   itself.
2. **Select vs Generate the bar.** Default: **Select** — published bounded policy,
   deterministic check, inference only picks which existing rules apply (#343's
   current shape, auditable from day one). *Generate* (inference composes the
   per-situation bar itself) arrives only once the coherence fold can tell a
   predictive composed-requirement from a hallucinated one.
3. **Advisory → actuating.** Default: the narrative-fold is **read-only first** (it
   reads judgment as a round-lineage and names the withholding bug); only later
   does the gate itself become round-based and consequence-scaled, behind the
   disposer fence (propose-first is the repo's law).

## The smallest real first piece (§9.4, when met, stop)

Not the harsh wall, not evidence-typing, not the threshold-judgment — the
**narrative fold**, in its weakest-but-real tier:

> A read-only fold that **materializes a judgment as a coherent round-lineage**
> from the existing version lineage + receipts (turning the amnesiac disconnected
> history into one story per atom-lineage), and **detects the withholding
> failure** — a round that re-rejects for something detectable the prior round —
> by reusing `heal.py`'s flapping-gate detector. No new write path, no inference,
> no harsh wall yet: prove that judgment *is* a fold over rounds and that the
> anti-DMV tooth bites, on records that already exist. Then grow the harsh
> evidence-wall, evidence-typing, the threshold-judgment seam, and trust-
> loosening as named pieces, each citing this spine.

This makes the keystone — *judgment is a narrative, told over rounds* — real on
day one without a single new source of truth, and everything else hangs off it.
