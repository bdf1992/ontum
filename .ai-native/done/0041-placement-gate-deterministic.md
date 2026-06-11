# Done-line 0041 — Placement: the deterministic gate refuses a collision (the second kind of real gate)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the L1 placement gate has a real, deterministic backing that
> can refuse. A pure-stdlib fold in `loop/` reads each atom's
> `incidence.touches` and `incidence.must_not_collide_with` across the field
> and returns **`collision`** when the atom under judgment overlaps an address
> a sibling atom declared off-limits (either direction), **`sound`** otherwise
> — the *second kind* of real gate: law, where the value gate (first light) is
> judgment. It is exercised §10 by a test where two atoms each valid **alone**
> refuse to fit **together**: the gate returns `collision` on the colliding
> pair and `sound` on a clean field, and that test **fails on a fixed-verdict
> mock** (the §10 teeth — a check that cannot refuse is not a check). The
> verdict reaches the log only through `loop.node judge` (no second write
> path, D-4), carrying the `prompt_hash` of a versioned law spec at
> `.ai-native/nodes/placement-gate.det.v1.md` (§7 — the law it applies is
> versioned source, hashed onto the receipt).

## Out of scope, named (bdo's stamp, not this session's)

- **The `node_real` admission that makes it the live gate.** Both real gates
  to date (`value-gate`, `owner-stamp`) were admitted `--by bdo` directly, and
  done-line 0028 scopes arc-confirmation to satisfying the *owner-stamp* stage
  — it does **not** cover `node_real`. So flipping `placement-gate.mock.v0 ->
  placement-gate.det.v1` live is bdo's realness stamp, named in the report,
  never forged here. This session builds and proves the backing; the gate goes
  live when he stamps. (If a gesture path for `admit-real` is wanted — the way
  arc-intake turned arc-confirmation into a GitHub gesture — that is its own
  done-line.)
- **`wrong_seam` / `halt_for_human`.** The seam's terminal set carries four
  verdicts; this line proves the `sound`/`collision` axis (the cheapest real
  refusal). The other two are deterministic extensions for a later line.
