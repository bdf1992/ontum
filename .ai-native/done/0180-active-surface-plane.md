# Done-line 0180 — The active-surface control plane (CTA-1): a live fold, not a prerender

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/surface.py` is the active-surface control plane (CTA-1 of
> `.ai-native/proposals/active-surface-control-plane.proposal.md`): a read-only
> fold that, on every call, folds the log FRESH and condenses the in-flight field
> a session is handed at blink-in. It COMPOSES the existing folds — `digest()` for
> the per-arc cells and field behaviour, `gaps()` for the parked pieces and the
> top gap, the setpoint read for the dial in play — re-deriving no truth (no
> second truth, §10). A SAFE DEFAULT LENS (default-safe-WHEN-UNSET, the setpoints
> law) makes a bare `python -m loop.surface` answer with no config: group by arc,
> surface a cell only at a stamp or a refusal, fold the quiet arcs and the noisy
> ambient channels to a tail, name the vitals. Teeth (`tests/test_surface.py`,
> joined to the suite, 5/5, non-vacuous): the NON-PRERENDER invariant — the
> plane's answer MUST change when the log changes (it fails if the plane ever
> caches a stale read) — plus the cell counts equalling digest's arc counts (no
> second truth) and the surfacing transition firing on a refusal; an unknown
> `--dimension` is named, not faked. Dogfooded live: 17 arcs / 62 inflight
> condensed to the 3 confirmed arcs harbouring refusals. Backed by
> `atom.active-surface-plane.v0` with an independent value-gate accept; the suite
> is green.

## Why

bdo, 2026-06-21: *"you're handed a rendered surface, not a control plane — I don't
want prerendering"* and *"a safe default so you don't have to fiddle every time."*
The SessionStart dump is a PRERENDER — a view computed ahead, frozen to text, and
pushed at the session; dead to any question it did not anticipate, and not
steerable. This is the opposite: the live measure-and-steer layer over the log,
the data/control-plane split ontum already has for one dial (orchestrate's
setpoint) generalized to the whole active surface. CTA-1 is the queried-live plane
+ the safe default, read-only; CTA-2 (the admitted governance dial), CTA-3 (the
prerender retirement), and CTA-4 (the propose-a-dial loop) are later increments
named in the proposal. The design is the AI's own (it is the primary reader, every
wake); bdo confirms the arc and holds the override dials — not the drafting table.
