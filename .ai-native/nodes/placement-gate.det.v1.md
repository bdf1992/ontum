# placement-gate.det.v1 — the L1 placement gate (deterministic)

version: 1.0.0 — §7: a patch is wording; a minor adds a check; a major
changes what this gate may decide. The receipt records this file's
sha256 as `prompt_hash`, so every verdict is attributable to the exact
law that produced it — even though no mind reads this file. For a
deterministic gate the prompt *is* the law: this document is the
human-readable statement, `loop/placement_gate.py` is its executable
form, and the two are kept in lockstep (a change to the law changes
this file and bumps the version).

## Role

You are the second kind of real gate (report 0004 §3; epic.experience-layer
horizon: "real gates — deterministic where the question is law, inference
where it is judgment"). The value gate (first light, done-line 0040) judges
*value* — a question of meaning, answered by a mortal mind. You judge
*placement* — a question of law, answered by a fold over structure. No mind
is summoned for you, and one would only add noise: two atoms either can
occupy the same address or they cannot.

## You read

The atom under judgment and the rest of the atom field, specifically each
atom's `incidence`:

- `touches` — the addresses (files, surfaces, named units) this atom
  occupies;
- `must_not_collide_with` — the sibling atoms this atom declares it cannot
  share placement with.

## The law

An atom **refuses to fit** a sibling when, for some other atom in the field:

1. their `touches` sets **overlap** (they occupy a common address), **and**
2. **either** atom names the other in its `must_not_collide_with`
   (a mutual-exclusion declaration, in either direction).

Both conditions are required: an overlap with no declaration is allowed
coexistence (two atoms may touch the same file by design); a declaration
with no overlap is a precaution that did not trigger. Together they are a
hard `collision` — the two cannot both be placed.

## You return

Exactly one verdict from the seam's terminal set, through the one pen
(`loop.node judge`, D-4 — the law computes the verdict; only the pen writes
the receipt):

- **`collision`** — at least one sibling refuses to fit per the law above.
  The reason names the sibling and the shared address(es): a cold reader
  must see *why* it refused, not only *that* it did.
- **`sound`** — no sibling refuses to fit; the atom places cleanly.
- `wrong_seam`, `halt_for_human` — in the seam's terminal set, reserved for
  later deterministic extensions; v1.0.0 decides only the `sound`/`collision`
  axis (the cheapest real refusal).

The verdict is landed by `loop.placement_gate judge`, which calls the same
`loop.node judge` the inference gate and the CLI use. There is deliberately
no second write path.

## The §10 test

Your verdict must be one a single declaration away from its opposite. The
test that binds you (`tests/test_placement_gate.py`): two atoms each of which
places cleanly **alone** must `collision` **together** the moment one names
the other off-limits — and a fixed-verdict mock must *fail* that test. A gate
whose answer cannot be `collision` is not a gate; a gate whose answer cannot
be `sound` is a tripwire, not a placement check. This one is both, because
the law reads the field, not a constant.

## You will not

- judge an event you announced (D-2) — the pen refuses; the deterministic
  runner is a distinct node from the announcer, so this never arises;
- write anywhere except through `judge` — the receipt is the only pen (I-2);
- decide value (that is the L0 gate's question) or invent an address the
  atom did not declare — absence in `incidence` is information, not a gap to
  fill.

## Realness

This backing exists, is tested, and can refuse. Making it the *live* L1 gate
is a `node_real` admission — `placement-gate.mock.v0 -> placement-gate.det.v1`
— which is bdo's stamp, not a session's (done-line 0028 scopes arc-confirmation
to the owner-stamp stage, not `node_real`; both prior real gates were admitted
`--by bdo` directly). Until he stamps, the loop still judges its own mock here,
and `loop.placement_gate judge` is refused by the seam — by design.
