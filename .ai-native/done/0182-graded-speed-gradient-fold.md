# Done-line 0182 — The speed-gradient fold — names the respond/retune/author bands, bites untraced-band-crossing

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/gradient.py` is a read-only, stdlib, propose-only fold (the
> `gaps`/`census`/`heal` grain) that makes the doctrine's binary two-time-scale
> (§14, D-12) legible as **one three-band graded gradient** read off the shared
> log. It classifies each log record into exactly one speed band by **act-verb**
> — **respond** (fast: `tick` ticks, pipeline verdict receipts, atom events),
> **retune** (medium: `setpoint` and `auto_admit_fence` admissions), **author**
> (slow: `workflow_armed`, `node_real`, `surface`, `herald_introduction`, `tag`
> admissions) — carrying fast/medium/slow only as the gradient label (the naming
> reconciliation: bdo's "medium" is the doctrine's "slow loop", so bands are named
> by verb, not by speed). It emits a band **profile** (per-band count + kinds + an
> honest **unbanded** count for record types it does not yet place — absence is
> information) and the §10 tooth **untraced-band-crossing**: every authored
> machinery artifact under `.claude/workflows/*.js` whose current bytes carry no
> enabled `workflow_armed` admission is a slow act the ledger cannot see — flagged
> with kind · subject · why · the one move (`review.py arm`), composing
> `review.is_armed`/`_hash_bytes` (no second arming definition, I-4). `--json`
> emits the dataset; the CLI ends `done | report` (D-6). Proven by
> `tests/test_gradient.py` joining the suite and **non-vacuous**: (a) a workflow
> file with no arm admission is flagged untraced; (b) the same file with an enabled
> `workflow_armed` for its exact current bytes is NOT flagged; (c) editing the
> bytes after arming flags it again (stale arm) — the test FAILS on a fold that
> skips the bytes-binding or vacuously refuses everything. Read-only: it names the
> band and the one move, it moves and judges nothing (D-4). The work is
> atom-backed under epic.graded-speed with the suite green.

## Why

bdo's "multiple speeds, a gradient not binary; thresholds binary, state graded"
(2026-06-21), grounded by the `graded-speed-foundation` workflow:
`graded-speed.proposal.md`. The double-build check found speed is **not** a new
organ — the fast↔medium bands already slide in code (`orchestrate` ↔
`slowloop`/`disposer`), so building a new control loop would double-build §14.
The genuinely-new, non-double-building first node is this **read-only witness**:
name the dimension, and make the one disconnected band — `author`, the slow act of
writing new machinery — **visible on the ledger**. That band is the highest-
leverage and least-governed (it authors what every fast act then runs), so seeing
it untraced is the point: witness before actuator.

## In scope (one increment)

- `loop/gradient.py` — the read-only fold: band classification + profile +
  the `untraced-band-crossing` tooth (composing `review.is_armed`), `--json` + prose.
- `tests/test_gradient.py` — the non-vacuous tooth test (untraced / armed-clean /
  stale-arm).
- A `loop/CLAUDE.md` module-layering line for the new fold.
- The backing atom under epic.graded-speed.

## Not in scope (named, not invented away)

- **The session record / attribute schema** — the attribute-bearing root minted at
  the gateway; higher blast (touches hooks), a later piece (graded-speed.proposal.md).
- **The A4 run rail and faithful `lint.py`** — the other findings from running it;
  separate pieces under the arc.
- **Any actuator** — the fold clears no park, arms nothing, slides no act between
  bands. Read-only, propose-only.
- **The oversight (admin/operator/worker) axis** — orthogonal to speed; the
  authoring-platform tier model carries it, this fold reads only the speed axis.
