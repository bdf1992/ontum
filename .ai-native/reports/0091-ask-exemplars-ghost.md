# Report 0091 — ask exemplars: killing the dangling ask_guard citation (structured-comms loop)

## What landed

Looping the structured-communication-channel work (the `/recommend` thread,
proposal homed on #234) toward done, this session closed the one concrete loose
end the proposal itself named — its **ghost** — and read the suite + landing
state for the rest.

- **The ghost is killed.** `ask_guard.py:189` and `.claude/skills/ask/SKILL.md`
  both told a *refused* session to "Reshape from an exemplar
  (`.claude/skills/ask/exemplars.md`)" — a remedy pointer that did not resolve
  (the exact ghost failure mode: a named backing that isn't on disk). Authored
  `.claude/skills/ask/exemplars.md` — four worked **before → after** pairs, one
  per refusal-check failure (E1 recommendation-first/R1, E2 route narration/R2,
  E3 the offloading refusal/R4, E4 config panel + comprehension checklist/R3+R7),
  each a copyable `AskUserQuestion` shape. The guard's deny message now points at
  a real gallery. Committed + pushed on `claude/ask-surface` (#222) — the
  earliest carrier of `ask_guard.py`, so the fix lands *with* the floor rather
  than dangling on main until a later stack catches up. (origin: fa24f9e.)
- **Suite is green** (`python -m unittest discover -s tests`, exit 0).
- **No new grammar built — by discipline.** The proposal's "Built now" increment
  is complete on #234; its four deferred slices stay deferred (the grammar is
  PROPOSED until a *second* real render earns it — §12 tripwire). Building them
  top-down this loop would be the exact sprawl the method forbids.

## needs-you

Nothing to stamp — `epic.owner-harness` is already confirmed; the work below is
the merge-node's order, not a new gesture. Surfaced for awareness:

- **Landing order is firm: #222 (ask) → then #234 (recommend).** #234 is branched
  from main (not stacked on #222) and borrows the ask R1/R2 floor fail-open; that
  floor goes live the moment #222 lands. `/recommend`'s own tree + RC7 bounds bite
  regardless.
- **Both PRs need a refresh before the merge-node will land them** (it refuses a
  CONFLICTING PR — `pr.py:743` "rebase it first"). #234's conflict is **log-only**
  (`events/receipts.jsonl`, union-merge-able by `.gitattributes`). #222's also
  carries a **real content conflict in `loop/CLAUDE.md`** (changed on both sides)
  — that one needs hand-resolution, not a mechanical union. I did **not** force
  this: it is the first domino, ordering-dependent (the branded tool for it, the
  `reconcile` verb, is on the **unlanded PR #224**), and #234 re-conflicts against
  the new main once #222 lands anyway. The clean path is: land #224 (reconcile) or
  a dedicated session reconciles #222's `loop/CLAUDE.md` + logs → merge-node lands
  #222 → #234 refreshes against new main → merge-node lands #234.

## End-state

`report` — ghost killed on #222 (exemplars.md, origin fa24f9e); suite green; the
structured-comms channel's build stands done on #234; #222→#234 landing order and
the `loop/CLAUDE.md` refresh surfaced for the merge-node.

