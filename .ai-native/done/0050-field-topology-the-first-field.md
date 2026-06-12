# Done-line 0050 — The first Field: a deterministic fold maps an arc's work-topology

@
Written before code, per §9.4. When this line is met, stop.

> **Done when:** a pure, read-only fold in `loop/` (e.g. `loop/field.py`, run as
> `python -m loop.field --arc <epic-id>`) takes one arc and produces its
> **decomposition ladder** — arc -> epic -> story -> task -> environment -> node
> -> occupant — where each rung carries **state**, **evidence** (record ids on
> the log, never prose), and **next_safe_move** (an existing pen's verb, or
> "needs bdo" when the move is his). It is the first real Field: the proof that
> work has address, scale, parentage, authority, and occupancy. It is **not**
> animation, UI, or the portal — those are later projections of this map.
>
> The discipline that makes it honest:
> - **A pure fold over the log** (the substrate's law): it writes nothing, and
>   every next_safe_move it names routes through an existing pen — `loop.gaps`
>   is its proof-of-shape and the fold reuses that vocabulary (gap / drift /
>   refusal / parked / pulse / owner-work).
> - **Absence is information.** Where a rung is not first-class on disk today —
>   `arc`, `epic`, `story`, and `node` are real; `task`, `environment`, and
>   `occupant` are partial or implicit — the fold **surfaces the rung as a named
>   gap, never invents it**. A field that fabricates a clean ladder is a mock
>   with a bigger bill.
> - **Occupancy carries authority.** An occupant whose identity has no
>   `node_real` admission (today: `merge-node.claude.v0/v1`,
>   `value-loop.story-author.mock.v0`) renders as an **un-authorised occupant** —
>   the field shows who is standing on a node and whether bdo ever stamped them
>   there.
>
> Exercised by a test (§10) that **fails on a fabricated/constant ladder**: given
> a real arc on the trunk, the fold returns the real rungs populated with
> evidence ids, the not-yet-first-class rungs named as gaps (not faked), and at
> least one un-authorised occupant flagged where one exists. Serves
> `epic.the-field` as its first piece (`atom.field-topology.v0`).

## Out of scope, named

- **The portal, the flow, the projective links, the session-field** — every
  *projection* of the map (later pieces of epic.the-field). This line builds the
  map, not its renderings.
- **Making the lower rungs first-class** (a real `task`/`environment`/`occupant`
  schema). This line *surfaces their absence*; promoting them to first-class is
  its own later line, and bdo's to steer.
- **Admitting the un-authorised occupants real** — bdo's realness gesture, never
  forged here; the field only shows the gap.
@
