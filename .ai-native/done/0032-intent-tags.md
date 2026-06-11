# Done-line 0032 — intent tags: the watcher learns read from mutate, governed by a pool

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/tags.py` holds a governed tag pool — dimension `intent`
> with a small closed core `{read, mutate}` and the one shared verb→intent
> classifier the watcher and the git pen both import (I-4, no second copy) —
> plus a proposed-tier: a value outside the admitted pool is recorded and
> surfaces as drift (`python -m loop.tags`), never blocks, and is promotable by
> an admitted `tag` record (`--by`). The watcher (`command_guard.py`) records a
> derived `intent` and a `branded` flag on every watched command, fail-open
> (a classifier error never gates the owner); `command_guard.py --report`
> splits raw **mutations** (the real next-wrapper candidates) from raw **reads**
> (raw-by-design) and lists commands the classifier doesn't yet know. The git
> pen (`git.py`) records its verb's intent and refuses an `--intent`
> declaration that contradicts the verb. §10 proof: `--intent read` on
> `git commit` refuses; a value outside the pool lands `proposed`, surfaced,
> not silently core; and the report ranks a raw mutation above a raw read.

## Why (bdo, 2026-06-10)

bdo, after the organ census answered "the watcher can't tell read from mutate,
so it can't nominate the next wrapper": "we wrap the tool with a dropdown of
data points based on intent ... add Tag type and tag pool to the tools and
require basic usage and suggest pattern which leave us data rich rather than
confused and noisy." The fix the census found, pushed upstream to the write
seam: stop inferring intent from raw capture; have the tool emit a typed,
governed tag. He chose proposed-tier governance and a one-dimension/one-pen
first slice.

## Out of scope, named (later increments)

- **The `arc` dimension (require-declaration on non-derivable tags).** Intent
  is derivable from a git verb, so this slice derives it; the require-a-tag
  pattern earns its keep where the tool *can't* derive — which epic an action
  serves. That dimension feeds arc-confirmation and is the natural next slice.
- **Other pens and the `surface` dimension.** One pen (git) proves the seam;
  generalizing to the PR/records/envoy pens follows once the shape holds.
- **Promoting a proposed value to core.** The admit path records it; whether a
  promoted value edits the code core or rides as an admitted extra is settled
  when the first real proposed value arrives, not pre-built.
