# Done-line 0179 — Gateway projection nodes carry derived ground-truth meaning

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the gateway projection's drawn nodes carry their real ontum meaning DERIVED from the term's cited evidence (not hand-written), so a cold reader cannot map a layer onto a generic-gateway trope; fence/heal/pen read truthfully; the emitted spec still passes diagrams/qa.py; tests/test_diagram.py proves the meaning is derived (changes with the evidence) and non-vacuous. When green and qa-clean, stop.

## Why

A cold reader of the rendered `gateway-topology` diagram (PR #446,
done-line 0173) confabulated three layers, because the bare `name`
labels carry generic API-gateway connotations: **fence** read as "IP
whitelisting / rate limiting" (truth: the actor-blind DENY registry,
`fence/policy.py`), **heal** as "generic state recovery" (truth: the
counterforce that senses where a GATE bit wrong, `loop/heal.py`,
propose-only), **pen** as "sandbox / pre-commit staging" (truth: the one
authorized writer, `loop/node.py def judge`). The shape already carries
realness (rect = minted-runtime); what was missing is the *meaning*. The
fix must be DERIVED from the projection's existing resolved evidence (each
term's first resolving citation `claim`), never prose authored on the
node — otherwise the diagram becomes a second place a meaning can drift
from truth (the projection-not-a-second-truth rule, §10).

## In scope

- A meaning line per drawn node, taken from the `claim` of the term's
  first resolving `evidence_edge` in the projection (the same fold that
  already classifies realness — no re-resolution, no second truth).
- Surfaced through the node `label` (the closed node-type vocabulary and
  schema are untouched: no new node field, no new shape — `label`'s
  `\n` multi-line is the schema-safe carrier), with nodes/regions/canvas
  resized so every wrapped meaning line fits and `diagrams/qa.py` stays
  exit 0.
- Regenerate the committed `gateway-topology.spec.json` / `.spec.svg` /
  `.projection.json` via the `--write` paths; byte-determinism holds.
- A test class in `tests/test_diagram.py` proving the meaning equals the
  projection's resolved claim (derived), that fence/heal/pen carry their
  ground-truth meaning, byte-determinism, qa-clean, and non-vacuity
  (mutate the fixture seed's claim → the node meaning changes with it).

## Not in scope

- Changing the realness classification, the drop/ghost teeth, or the
  `threshold` refusal (done-line 0173 owns those; unchanged).
- Adding a new node type, a node field, a genre, or a third accent.
- Re-pointing the diagram at a non-gateway seed, or any new genre.
