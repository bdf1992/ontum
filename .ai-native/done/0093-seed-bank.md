# Done-line 0093 — The seed bank — patterns banked as proposed, planted only by a deliberate hand

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.seed-bank.v0
> **Probe:** P7 (the seed bank — proposed, not planted)

bdo, 2026-06-16: "a seed is not automatically planted." Where the harvest banks
its seed. A harvested generative shape is recorded as a PROPOSED pattern — seen,
banked, but not minted into the Commons. Planting (promotion to a real pattern)
is a deliberate, separate hand — an admission (D-4), like `admit_tag`. No Pattern
Commons is homed in ontum today (only the separate experience-foundry); this
homes the seed bank as the proposed pool, reusing tags.py's proposed→admitted
grain over the log (§10, not a new mechanism). Autonomous planting stays the
fenced horizon (PR #163 pattern), not this piece.

> **Done when:** `loop/seedbank.py` provides `bank(root, slug, shape, *,
provenance=None, by)` (records a pattern as PROPOSED — banked, signed `--by`,
never auto-planted), `plant(root, slug, *, by)` (promotes a banked seed to
PLANTED), and `seeds(root)` (folds the bank → each pattern's state
`proposed`|`planted`), all as admissions on the log reusing reconcile.Fold /
append_line and the tags.py proposed→admitted grain; and `tests/test_seedbank.py`
passes under `python -m unittest`, proving the teeth — (1) a banked seed reads
`proposed`; (2) a *different* hand plants it → `planted`; (3) planting is refused
when unsigned (a seed is not automatically planted), when the slug was never
banked, and when the proposer tries to plant their own seed (no one plants their
own seed — D-4; planting is a second deliberate hand, autonomous planting is the
fenced horizon); (4) the fold is idempotent — re-banking a slug folds to one.
