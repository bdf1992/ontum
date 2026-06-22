# Report 0086 — The terminal-pull gateway, and the namespace gap it made visible

## What landed

**Done-line 0123 — the terminal-pull gateway (`loop/pull.py`).** The
reviewer's top-priority throughput fix, built and opened as **PR #226**
(branch `claude/terminal-pull-gateway`), eligible for the merge-node
once bdo confirms `epic.landing-throughput-response`.

- `loop/pull.py` — `next_landable_slice`: a read-only fold (grain of
  `digest`/`merge`/`census`/`gaps`/`retro`) that names, per **confirmed**
  arc, the **piece-scale** pieces that are receipt-complete, non-superseded,
  integrity-intact, and pullable now — bounded by the admitted
  `max_inflight_atoms` dial into pull-now vs queued-behind-capacity. It
  folds the `digest` dataset and reuses its divergences (§10, no second
  truth). On the live log it surfaces **24 receipt-complete pieces** under
  confirmed arcs that `loop.merge` (arc-scale) reports as "nothing ready".
- `tests/test_pull.py` — 12 tests; the §10 teeth the live log does not
  exercise: a refusal under a confirmed arc **vetoes** the slice (held,
  with a control that pulls clean); the capacity bound honours the dial;
  the namespace-gap finding fires.
- `loop/CLAUDE.md` — the new organ documented.
- Dogfood: the backing atom was announced (seed) and judged by an
  **independent** value-gate (D-2) → `accept`, `rcp.7ceda90bf95b`.

## The finding (the real binding constraint)

The reviewer's guard assumed a **per-piece pull join** exists. It does
not. **All 90 merge `landed` receipts key on `(epic, pr, head)` and carry
no atom id/hash** — the pipeline namespace (per-atom, content-hash) and
the git-merge namespace (per-PR) **do not join per piece**. So the loop
**cannot confirm a single completed piece reached main**. The gateway
refuses to fabricate the join (mercury) and instead surfaces the
**namespace gap** as a named finding. This is why judged-good work does
not visibly reach main; closing the join is a later piece of the epic.

## A second finding (surfaced, not fixed)

The PR pen's suite run flaked twice with `FileNotFoundError` on a temp
`.ai-native/log/receipts.jsonl` — while **other suite runs of mine were
executing concurrently**. Root cause: a **load/concurrency race** in a
test's bare `read_bytes()`/`read_text()` of `receipts.jsonl` without an
`.exists()` guard (candidate: `tests/test_reflect.py:273`
`test_hook_still_writes_nothing`; siblings in `test_summon`/`test_gaps`
already guard with `if p.exists()`). Run alone, the suite is green across
**seven** runs and the PR opened clean. The cheap, correct fix is to guard
those bare reads (absent append-only log == empty) — a separate small
increment, not this done-line's scope. Not fixed on a guess without a
single-suite reproduction.

## needs-you

- **Confirm (or decline) `epic.landing-throughput-response`.** It is still
  PROPOSED — your `confirm-arc` is the one gesture that queues this whole
  foreign review's work and authorises the merge-node to land PR #226 (and
  its siblings as they are built). Nothing of mine waits on you otherwise.

## End-state

`report` — terminal-pull gateway built, tested (suite green, 903), and
opened as PR #226 under the unconfirmed `epic.landing-throughput-response`;
the namespace-gap finding is the session's real discovery, and a
concurrency-race test flake is surfaced for a separate fix.
