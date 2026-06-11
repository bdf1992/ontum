# Done-line 0033 — the merge-node's eyes: read-only land-readiness per arc

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `python -m loop.merge` reports, per confirmed arc, a
> land-readiness verdict — read-only, reusing the digest fold (done-line
> 0032): `ready_to_land` only when the arc is confirmed by bdo, every
> declared piece is present and landed, and no divergence touches it;
> `refuse` when a divergence does (a confirmed arc harbouring a refused
> piece — even one whose atom now reads landed); `not_ready` when the arc
> is unconfirmed or a piece is unbuilt or unlanded — each with its reasons.
> It merges nothing and writes nothing. The actual land, plus the two
> stamps that turn this sensor into the merge-node's *hand* — amending the
> `bdo merges` hard rule and `admit-real --by bdo` — remain his alone
> (D-4). §10 proof: a confirmed arc whose pieces all read landed but whose
> record holds a refusal must report `refuse`, not `ready_to_land` — the
> sensor must never green-light over a gate's no. Recorded in loop/CLAUDE.md.

## Why (bdo, 2026-06-11)

Continuing the move out of the merge seat. The digest (0032) gave bdo eyes
on the whole field; this gives the *merge-node* its eyes on a single arc —
the judgement "is this arc safe to land on main?" that, once he admits it
real and amends the rule, becomes the land itself. The first sensor of a
new kind of meaning (report 0004 §3): land-safety. Eyes before the hand.

## Out of scope, named (the hand, still bdo's)

- **The merging hand.** Actually running the epic→main merge is a separate,
  hard-gated pen built only after bdo amends `bdo merges` and admits the
  node real. This piece decides; it never acts.
- **The arc-scale judging seam.** Today's pipeline judges per atom; a real
  arc-scale node that *parks an arc* awaiting the merge-node's verdict
  through the one pen is later machinery. This is the read-only sensor that
  seam will be built around.
- **Field cap-breaches as a per-arc veto.** A past queue-over-cap is field
  health, surfaced as a global caution, not a block on a specific arc.
