# Done-line 0034 — the merge-node's hand: agents land, bdo confirms arcs

Written during the work, not before — bdo's directive arrived mid-build and
reframed it (named in report 0034). When this line is met, stop.

> **Done when:** `pr.py land <pr> --epic <id> --by <node>` lands a
> *confirmed-arc* PR on `main`, and only then — refusing by default any PR
> that is unconfirmed (bdo's `confirm-arc`, read from the **trunk**, is the
> authorization the node executes, D-4), red or pending, draft, conflicting,
> story-less, or not based on main. It records a merge receipt citing the
> authorization, and `--dry-run` prints the decision without merging. The
> `bdo merges` hard rule is amended in CLAUDE.md (he confirms arcs and reads
> the digest; the merge-node lands), the branch-ritual hand-off no longer
> routes him into a merge or says "at the stamp," and the merge-node SKILL
> makes the lander a *fresh agent* that never lands its own line. §10: a PR
> perfect on every mechanical axis but whose arc bdo has not confirmed must
> refuse to land — mechanical readiness is not authorization. bdo is never
> asked to merge.

## Why (bdo, 2026-06-11)

"I do not want to do it anymore, I only want to get daily ARC digests, my
doing PR is becoming performative and agents should be doing that ... make it
the fuck happen." Said twice. The two enabling stamps given: the rule is
amended, the merge-node is built. His remaining surfaces are arc confirmation
and the daily digest — nothing mechanical.

## Out of scope, named

- **Daily arc-digest delivery.** The digest exists (`loop.digest`); a
  *scheduled* daily push of the arc-level digest to bdo is the next piece.
- **A formal `merge_node_real` admission.** Not needed to operate: each land
  is authorized per-arc by bdo's `confirm-arc`, not a standing node_real
  record. If a standing "the node is live" record is wanted, it is one line.
- **Deep suite re-run on the PR's own tree.** The pen checks the PR's status
  rollup and metadata; checking out the PR to re-run its suite is the lander
  agent's step (SKILL), heavier machinery later.
