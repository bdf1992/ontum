# recommend — the policy (the branching-tree rules)

The law behind the [skill](SKILL.md). recommend is `/ask` **expanded into
a generative branching tree**, so it **inherits `/ask`'s whole law as its
floor** — [`../ask/policy.md`](../ask/policy.md), R1–R7 and the refusal
check apply to *every panel* unchanged. This file adds only what the tree
needs: the rules for routing, generation, and the bound.

This is config-as-code (§7): versioned, landed as a stamped increment,
never hand-tuned silently. A new rule is a new entry here, referenced.

## The inherited floor (from /ask, per panel)

R1 (recommendation-first), R2 (routes narrated, not labelled), R3
(configuring is a panel), R4 (ask only at a genuine fork), R5 (the mirror
is one-way), R6 (name the honest limit), R7 (a design ask carries a
comprehension checklist) all hold for **each panel** in the tree.
recommend does not weaken any of them.

## The recommend-only rules

- **RC1 — A compositum is a routed tree, not a flat menu.** recommend
  composes a *sequence of panels* (each ≤4 tabs × ≤4 options), connected
  by routing edges. The ~20 options are the tree's leaves reached by
  walking branches — never crammed into one modal.
  *Refs:* bdo, 2026-06-18 — "multiple tabs of 4 options with routing"; the
  AskUserQuestion 4×4 cap (`ontum-ask-surface-discipline`).

- **RC2 — Routing generates the next panel.** A route selected in a tab
  *prompts a second set of checkboxes* — the next panel, composed live
  from the route taken + the gesture. The branch the session generates
  must be a faithful consequence of the route, not a non-sequitur.
  *Refs:* bdo, 2026-06-18 — "one route might prompt a second set of
  checkboxes".

- **RC3 — Generation is bounded; the bound runs before render.** Each
  generated panel passes [`compose.py`](compose.py)'s refusal check — the
  deterministic floor of `/ask`'s law — *before* it is shown. A panel
  that fails is refused and recomposed; an unbounded panel never reaches
  bdo. The bound is the settled-safe part; the composition is the fresh
  part.
  *Refs:* `ontum-inference-as-composition-layer` (bounded inference);
  the gateway-policy-spine fail-mode tier (deterministic floor gets hard
  teeth, judgment gets discipline + audit).

- **RC4 — The composer is the session (prompt-as-code).**
  `AskUserQuestion` is a session tool; only the live session can render a
  panel. recommend's generative step lives in the skill instructing the
  session, which calls the code only for the bound and the trace — never a
  headless pen rendering panels.
  *Refs:* the architectural note in [SKILL.md](SKILL.md).

- **RC5 — A tree is for a real decision-space, not a dump.** A routed
  pile of trivial or session-resolvable options is the offloading failure
  (R4) at tree scale. recommend is admissible only when the space is
  genuinely owner-bearing — a direction or design where bdo's walk and
  correction matter. If the session can just resolve it, resolve it.
  *Refs:* R4 and the **offloading hard rule** (CLAUDE.md).

## The refusal check (the teeth)

Before rendering any panel, recommend is **refused** — reshape/recompose,
or make the call yourself instead — if **any** of these is true:

1. **The inherited per-panel check fails.** Any of `/ask`'s three
   refusals fires on the panel (no recommendation, bare labels where
   routes are offered, an offloaded call). The floor is the floor.
2. **The bound bites (violates RC3).** `compose.py` reports a refusal on
   the generated panel (over the 4×4 cap, a route tab with no
   `(Recommended)` option or an unnarrated route, an over-long header). →
   Recompose; never render the unbounded panel.
3. **A branch is a non-sequitur (violates RC2).** The next panel is not a
   faithful consequence of the route taken. → Recompose from the route.
4. **It is a dump, not a decision-space (violates RC5).** → Make the
   calls yourself, name what you chose, proceed.

`compose.py` enforces refusal #2 deterministically (it is testable, with
teeth — §10). Refusals #1, #3, #4 are judgment rules applied by the
session and read by the audit fold (the R7 split: bright-line in code,
judgment in discipline + audit).

## Audit (shared with /ask, next increment)

recommend rides the **same** audit fold `/ask` named (done-line 0119,
next increment): every panel + answer logged, the pattern folded for
genuine shape-transfer vs offloaded/menu use. recommend's distinct
reading: a route that, once walked, *generated a branch bdo abandoned*
(broke to *Other*, or unchecked the whole generated set) is a
generation miss — the composer's next-panel did not follow the route —
and is the signal the generative step must learn from. Learnings land in
the shared registered memory `ontum-ask-surface-discipline`.
