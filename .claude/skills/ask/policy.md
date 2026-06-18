# ask — the policy (governed rules, with references)

The law behind the [skill](SKILL.md). Each rule is a record: the rule, and
the doctrine clause or bdo-frame it enforces. The policy's job is not to
describe good asks — the skill does that — but to **refuse** bad ones. An
ask that fails the refusal check is a generic menu and must not be sent.

This is config-as-code (§7): versioned, landed as a stamped increment,
never hand-tuned silently. A new rule is a new entry here, referenced.

## Rules

- **R1 — Recommendation-first.** Every ask leads with the recommended
  option, first, `(Recommended)` in the label, the *reasoning* in the
  description.
  *Refs:* [bdo-surface — inference-construct, not tickets](../../../../.claude/projects/c--Users-bdf19-ontum/memory/bdo-surface-inference-construct-not-tickets.md)
  ("a list of options is still a queue"); [owner-asks arrive spoon-fed](../../../../.claude/projects/c--Users-bdf19-ontum/memory/claude-owner-asks-arrive-spoon-fed.md).
  The 2026-06-18 *Other → "whats recommended?"* breakout is the failure
  this rule exists to prevent.

- **R2 — Routes are narrated, not labelled.** When the options are
  routes (not a plain preference), each carries a `preview` telling it as
  a concrete story — what happens, the cost, the risk.
  *Refs:* the projection principle (the question is a fold of the
  session's gesture, not a list); display-system narration over labels.

- **R3 — Configuring is a panel, not a menu.** When bdo is composing the
  next move rather than picking one option, raise a multi-question panel
  (Q1 = route, Q2–Q3 = dials). One degree of freedom per question.
  *Refs:* bdo, 2026-06-18 — "more often than not I want BOTH multichoice
  configuration… I'm configuring your next move."

- **R4 — Ask only at a genuine fork (the refusal).** Raise the surface
  only for a decision that is truly bdo's — unresolvable from the
  request, the code, or a sensible default. A call a session can make is
  the session's to make; fronting it as a question is **offloading**.
  *Refs:* the **offloading hard rule** (CLAUDE.md: "Support the owner;
  never offload onto him… never manufacture an 'only you can do' list");
  D-4 (the owner is the last stop — at arc scale, not for every call).

- **R5 — The mirror is one-way.** The ask surfaces a fork and carries
  back an answer; it never *executes* bdo's authority itself. A confirm,
  a stamp, an arc still land through their own pens.
  *Refs:* D-4; the reflect mirror (log → surface, never back).

- **R6 — Name the honest limit.** The modal chrome is harness-owned. Do
  not promise to reskin it; the brandable surface is content, affordances,
  memory, and audit.
  *Refs:* done-line 0119 non-example.

## The refusal check (the teeth)

Before sending any `AskUserQuestion`, an ask is **refused** — do not send
it, reshape or proceed instead — if **any** of these is true:

1. **No recommendation.** No option leads with a reasoned recommendation
   (violates R1). → The reshape: add it, or make the call yourself.
2. **Bare labels where routes are offered.** Options are routes but none
   narrates (violates R2). → Add `preview` narration.
3. **Offloaded call.** The decision is one a session could resolve from
   the request, code, or a sensible default (violates R4). → Make it,
   name what you chose, proceed. **This is the most common failure** and
   the one the audit fold (next increment) will read for: every *Other*
   breakout and every ask that should never have been raised.

A policy that can refuse none would be decoration. This one says *no*.

## What the audit fold will measure (named, next increment)

The companion audit (done-line 0119, out-of-scope/next) logs every ask +
answer and folds the pattern: genuine-fork asks vs offloaded/menu asks,
with *Other*-breakouts as highest-signal. It is the sensor that turns "am
I obeying this policy" from willpower into a reading — the same move the
watcher makes for tool use. The learnings land in the registered memory
`ontum-ask-surface-discipline`.
