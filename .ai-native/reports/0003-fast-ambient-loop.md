# Session report 0003 — the fast ambient loop, built

- **Date:** 2026-06-10
- **Session:** v-next build (report 0002 §6, stamped by bdo via chat:
  "set up a simple working loop")
- **Branch:** `claude/great-faraday-djmq2x` (bdo merges — D-4 applied to git)
- **End-state:** `done` — done-line 0002 met, closing on done (§9.4).
- **Doctrine:** `ai-native-loop-substrate.md` v0.4.0, authoritative, unedited.

---

## 1. The done-line, and that it is met

Written before code (`.ai-native/done/0002-fast-ambient-loop.md`):

> ≥2 atoms reach `desired_state` under a per-tick step budget read from an
> admitted `setpoint` record (I-8), every actual move still `pass_once`
> (D-8); **and** the flood test passes: atoms seeded faster than a
> rate-limited mock human can clear them, the loop sheds its own inflow
> (I-7) so the human queue never exceeds its admitted cap at any tick while
> the field still reaches `done`.

Both clauses are met, each proven twice — by test and by artifact:

- `tests/test_orchestrate.py::test_two_atoms_reach_goal_under_admitted_budget`
  and the live run in `.ai-native/log/` (two atoms settled, 11 admitted ticks).
- `test_flood_cool_path_holds_the_cap_without_stalling`: six atoms against a
  cap of 2 and a 1-stamp-per-tick mock human — max backlog over every tick
  ≤ 2, `cool: inflow shed` on the record, every cool tick still spent
  budget ≥ 1, all six reached `value_confirmed`, no doubled receipts.

12/12 tests green (the phase-1 six untouched and still passing).

## 2. What landed

- **`loop/orchestrate.py`** — the §15 fast loop as a control session (§2,
  D-3): each tick it folds the log, senses pressure (pure folds: backlog,
  inflight, queue depth, parked), reads the setpoint from an admitted record
  in `log/admissions.jsonl` (I-8 — no dial, no run: `needs-you`), derives
  the spend both ways (D-11), and spends it through the existing
  `pass_once`. Ticks are themselves admitted lines. Scheduling drains
  before it feeds (furthest-along first); the valves close on the
  *projected* human queue, before the budget is consulted, so a shed step
  is recorded as shed, not as "budget spent".
- **`loop/reconcile.py`** — only the report 0002 §4 mechanical
  generalizations: `load_atoms` (the field), per-atom `pass_once`,
  multi-atom cache fold, field-wide `--status`. Contract unchanged.
- **CLI** — `python -m loop.orchestrate --admit-setpoint '<json>' --by <who>`
  (refused without `--by`, D-4); `--status` for a read-only field summary;
  `--human-rate` for the mocked slow stage; `--max-ticks`.

## 3. What the build caught (worth keeping)

1. **The §5 test failed first, honestly.** The cap held, but seeds were
   deferred as "budget spent" before the inflow valve was consulted — the
   cool path worked by accident of budget, not by law. Reordered: valves
   close on the projected field first, budget last. The flood test's
   `cool: inflow shed` assertion is what caught it.
2. **Tick ids collided across sessions.** In the first live run, two
   control sessions sensed identical pressure at the same tick number
   within the same second; 2 of 11 tick lines vanished into the fold's
   dedup. A tick id now hashes the decision (scheduled + deferred), not
   just the weather. The resume test asserts raw lines == folded records.

## 4. End-state and what was not done

- **Done, stopped at done:** no slow loop (the dial is admitted, never
  re-admitted by outcomes yet), no real nodes (the owner-stamp mock is
  still first to be replaced), no surfacer ensemble, no control/surfacer
  split, no doctrine edit (§12 respected).
- **Open for bdo, next stamps:** (a) the slow loop — re-admitting the dial
  from accumulated outcomes (D-12); or (b) making exactly one node real,
  L0 first (§11 "Next"). Report 0002 §7 ordered ambient-loop-first because
  the cool path was unproven; it is proven now, so making L0 real is the
  natural next single version.
