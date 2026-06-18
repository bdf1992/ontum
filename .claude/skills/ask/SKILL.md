---
name: ask
description: >-
  The ontum way to ask bdo a question — the AskUserQuestion surface as a
  faithful projection of the session's gesture, never a generic menu. Use
  EVERY time you raise an AskUserQuestion, when about to surface a fork to
  bdo, or on "/ask". It shapes the call so the question leads with a
  reasoned recommendation, narrates genuine routes in the `preview` field
  rather than labelling them, and becomes a multi-question config panel
  when there are dials to set — and it refuses the generic menu (a list of
  options with no recommendation is still a queue; an ask that offloads a
  call the session could make itself violates the offloading hard rule).
  The governed rules with references are policy.md beside this file; the
  living discipline and its accumulated learnings persist in the
  registered memory `ontum-ask-surface-discipline`.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form (done-line 0119). bdo, 2026-06-18: the AskUserQuestion
      surface is "poorly used when generic" — he had to break out to
      *Other* to type "whats recommended?". He chose to make the
      ontum-ask shape STRUCTURAL (a skill), with a registered memory
      location and a policy with references, rather than leave it to a
      session's willpower. The companion audit fold (a hook + a
      pattern-reading fold over how the surface is used) is the named
      next increment.
---

# /ask — the question is a projection of your gesture

When you raise an `AskUserQuestion`, you are not opening a menu. You are
**projecting your decision-state onto a surface bdo steers from** — the
synchronous twin of the [bdo-brief node](../../../loop/brief.py)'s async
digest. Each axis you expose is a real degree of freedom you are holding
open; each option is a route you have actually weighed. The question is a
*fold of where you are genuinely torn* — and when it stops being that, it
degrades into the generic menu bdo named as the failure.

The tell, from his own words (2026-06-18): a question that makes him break
out to *Other* to ask "what's recommended?" withheld the one thing he
wanted. A list of options is still a queue ([bdo-surface](../../../../.claude/projects/c--Users-bdf19-ontum/memory/bdo-surface-inference-construct-not-tickets.md)).

## The honest limit

The AskUserQuestion **modal chrome** — its skin, fonts, layout — is the
harness's, rendered by Claude Code. It is **not ours to reskin** into the
ontum look-and-feel. Do not try; say so if asked. The lever is everything
*inside* the call: the content, the affordances the tool already gives
(recommendation-first, `preview`, multiSelect, 1–4 questions), the
registered memory, and the audit. Branding lives there, not in CSS.

## The shape (every ask)

1. **Recommendation-first.** Lead with the option you recommend, as the
   first option, with `(Recommended)` in its label, and put *the reasoning*
   in its description — the why, not just the what. bdo should never have
   to ask for your pick; it is already there, with the divergence seam to
   set beside his own judgment.
2. **Narrate routes, don't label them.** Use the `preview` field to tell
   each route as a short, concrete story (what happens, the cost, the
   risk) — markdown/ASCII in a monospace box. A bare label is a menu; a
   narrated route is a projection.
3. **Config panel, not a single menu, when there are dials.** The tool
   takes **1–4 questions** in one call. When bdo is *configuring your next
   move* (not just picking one), raise a panel: Q1 = the route, Q2–Q3 =
   the dials on it. He composes the move; he does not pick from it.
4. **Ask only at a genuine fork.** Raise the surface only for a decision
   that is truly bdo's — one you cannot resolve from the request, the
   code, or a sensible default. If a session could make the call itself,
   making it *is* the work; asking is offloading. This is the refusal —
   see [policy.md](policy.md).

## The refusal (the teeth)

Before you ask, run the policy's refusal check ([policy.md](policy.md)):
if the question carries no recommendation, narrates nothing, or fronts a
call you could make yourself, **it is a generic menu — do not send it.**
Either shape it into a projection or make the call and proceed (naming
what you chose). The policy can say *no* to an ask, not only describe good
ones.

## The registered memory

The living discipline and everything learned about asking well — which
asks landed, where bdo broke to *Other*, what shapes work — persist in the
registered memory **`ontum-ask-surface-discipline`** (indexed in
`MEMORY.md`). When an ask teaches you something (a breakout, a praised
shape, a refusal you should have made), write it there. That file is the
durable home; this skill is the ritual; the policy is the law.

## Compose, don't double-build (§10)

The ontum-ask shape **is** the inference-construct shape
([bdo-brief node](../../../loop/brief.py)) applied to the synchronous
question. Do not re-derive it. The async owner-bound work folds into the
digest; the synchronous fork folds into the ask. One shape, two render
targets. The audit fold (next increment) will read *how* the surface is
used, the same way the watcher reads tool use — a sensor, not a second
truth.
