# Done-line 0029 — the organ census — liveness from the log and the wiring

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `python -m loop.census` is a read-only, stdlib-only fold that
> ranks every repo organ (loop/*.py, .claude/hooks/*.py, .claude/skills/*/*.py,
> glyphs/*.py) by two pure signals — **wired** (reachable by import/reference
> from a live entrypoint, not only its own test) and **exercised** (its source
> speaks at least one record word the runtime log actually holds) — and names
> the dormant ones (built and tested but neither wired nor exercised) so
> pruning is evidence, not vibes. It ends with `result: done | report |
> needs-you` like its siblings. §10 proof: a planted organ that is built and
> tested but neither wired nor exercised is flagged dormant, while a live organ
> (reconcile) is not — the test fails if the census flags everything or nothing.

## Why (bdo, 2026-06-10)

bdo: "nearing a turning point ... pruning [what] didn't quite land right, and
giving specific care to the pieces that did, and monitoring over the signals we
have encoded in our working process to find what needs more attention and how."
The chosen movement: build the usage lens first, so the prune is evidence-based.
The signals already on disk confirmed the need — minds.py is built, tested, and
referenced by zero non-test files, with no admission of its kind in the log;
trust and placement are wired but leave no runtime trace. The census makes that
readable on demand.

## Out of scope, named (later increments)

- **Git recency.** Last-touched would need subprocess; the loop is
  stdlib-and-no-subprocess (hard rule). Liveness here is wiring + log-vocabulary,
  both pure. Recency, if wanted, lives outside the pure module.
- **Acting on the verdict.** The census reports; it never prunes or edits. What
  to delete or de-mock stays bdo's call (D-4).
- **Branded wrappers for poor collection.** The census *finds* the blind spots
  (organs that act without leaving a recorded story); minting their wrappers is
  the watcher-decides-next-wrapper move, its own stamped increment.
