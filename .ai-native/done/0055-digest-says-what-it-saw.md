# Done-line 0055 — The digest's end line says what the span saw

﻿Written before code, per §9.4. When this line is met, stop.

> **Done when:** the digest's end line can no longer claim cleaner than the
> dataset it just printed (the contradiction report 0038 named, left open by
> done-line 0041's wording repair): a span that contains any refusal receipt
> ends `report`, never `done — clean span: nothing refused`, and a loose
> atom's awaiting/parked standing counts toward "anything still open" exactly
> as an arc piece's does (today the end line sums only arcs, so a parked
> loose atom vanishes from the verdict). The decision is a pure function over
> the digest dataset (`open_count`), hit directly by tests with the §10 pair:
> a refusal on an unconfirmed arc's piece — which feeds no divergence — must
> still end `report`, and a genuinely refusal-free, nothing-open span still
> ends `done` (the fix must not make the digest cry wolf).

## Out of scope, named

- **The divergence folds themselves** — refusal-under-confirmed-arc and
  queue-over-cap are correct; this repairs only the end-line verdict.
- **PR #61's colliding report ids** (its 0038/0039 vs main's) — already
  committed history on its branch; the record-id fence (done-line 0053)
  prevents the next one, and erasure is not how this repo fixes history.
- **A new digest section** — the refusals count already prints; the lie was
  only in the closing verdict.
