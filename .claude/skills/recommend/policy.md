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
  part. recommend's **own** bounds (the tree cap + RC7 auto-run) always
  bite; the **borrowed** `/ask` floor (R1/R2 via `shape_problems`)
  **fails open** when `/ask` is not yet deployed beside recommend (they
  are a stack heading to the same arc) — it activates the moment `/ask`
  lands. Fail-open here mirrors `ask_guard`'s own philosophy and avoids
  the twin I-4 forbids; it does not weaken recommend's own teeth.
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

- **RC6 — Situational: a tool for the right shapes, not a default.** recommend
  (and the wider structured-input channel it belongs to) is reached for **only
  when the moment fits its shapes** — a real, mostly-known decision-space; a fast
  survey to bound a topic; a multi-dimension input to collect as data; a route to
  a mode of thinking. When the situation does **not** fit — an open problem, a
  single fork, a call the session can make, a fluid conversation — it is the
  wrong tool, and using it anyway is the **form-filling prison**: turning talk
  into data-entry on the one surface the owner is most likely to abandon. The
  instrument's expansiveness is governed *down* by this rule, never *up*.
  *Refs:* bdo, 2026-06-18 — "it's also a tool for those shapes, not if the
  situation doesn't fit"; R4 (ask only at a genuine fork); the adversarial
  review's top risk (the expansion-vs-contraction collision with the ask
  discipline). This is the answer to that risk: the tool stays subordinate to R4.

- **RC7 — A selection auto-runs only read-class; a change proposes -> gates.** A
  picked option may fire deterministic code **only when that code is read-class**
  (a query, a fold). A change/mutating/authority act **must** become a proposal
  with a preview and route through the gate — a pick is evidence of intent, never
  the command itself, and a pick that writes is self-signing. "Other"/NL is never
  a deterministic route: it always proposes (inference reads it), never commits.
  The bound is code: [`compose.py`](compose.py) `autorun_refusals()` refuses any
  route that claims auto-run for a non-read intent, or whose verb classifies as
  mutate while declaring read (reusing the tags.py verb->intent classifier, I-4).
  *Refs:* AIM (`causality/auditable-intent-mesh.md` — a gesture is evidence, not
  a command; the execution table: only read/annotate auto-run); D-4 and
  no-self-sign (loop invariants); the fence (no auto-run of a denied command).

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
5. **The situation doesn't fit (violates RC6).** The moment is an open
   problem, a single fork, a call you can make, or a fluid conversation — not a
   structured-input shape. → Don't raise the instrument; use prose, `/ask`, or
   just act.
6. **A pick would auto-run a change (violates RC7).** A routing table wires a
   non-read option to auto-run. → Recompose so the change proposes -> gates;
   only read-class auto-runs.

`compose.py` enforces refusals #2 and #6 deterministically (both testable, with
teeth — `--selftest`; §10). Refusals #1, #3, #4 are judgment rules applied by the
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
