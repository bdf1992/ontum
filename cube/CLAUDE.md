# cube/ — CNEX: the conal–axial frame

A clean-slate fork (2026-06-22) of the glyph viewer, reworked from a
Cartesian Rubik's cube into the **conal–axial topology** of
`conal_axial_topological_surfaces_README.md`. Decoupled from the governed
glyph pipeline on purpose, so it can be hacked on freely.

## The geometry (bdo's structure)

The core is **not** six independent face-cones. It is **three
double-cones (bicones)** — one per axis (region / flow / reach) — that all
share **one central locus: the neck, where polarity inverts** (the −1 cone
meets the +1 cone tip-to-tip at the setpoint 0).

- 3 double-cones → **6 outer tips = the 6 faces** (typed surfaces)
- + the shared neck → the **7th meeting point** (6 faces + 1 neck = 7)
- **8 corners = triads** (one landmark drawn from each of the three axes)
- **12 edges = chiral seams**, drawn as **tori** (the aperture rings)

Cubes, cones, and tori align everything: the cube hull frames it, the
bicones generate the axes, the tori ring the seams.

## Separation of concerns (the whole point of the fork)

The old `viewer.html` was one 14k-line file (12.5k of it inlined data).
This is split so each layer talks to the next through one interface:

- `model/` — **pure, no DOM, no Three.js** (node-testable; the §10 teeth):
  `axis.js` (signed bounded axis), `cube-topology.js` (the 3-bicone /
  7-point frame + invariants), `address.js` ((R,F,H) and cone-field
  state + the state-fold).
- `geometry/` — pure Three.js shape factories: `bicone.js` (double-cone),
  `seams.js` (edge tori + corner triads + neck).
- `render/` — pixels: `scene.js` (scene/camera/lights/orbit), `style.js`
  (the only place that knows hex codes).
- `interaction/` — `inspect.js` (raycaster pick → panel).
- `data/primitives.json` — the glossary, **fetched at runtime, never
  inlined**.
- `vendor/` — local Three.js + OrbitControls (no runtime network).
- `main.js` — the wiring (the only module that touches all layers).
- `tests/topology.test.mjs` — the teeth, with a non-vacuous failing case.
- `viewer.html` — the original monolith, kept as **reference only**.

When you add a primitive (region/flow/reach axis behaviour, portals,
frames, shrinking bound), put the rule in `model/`, the shape in
`geometry/`, and wire it in `main.js`. Never grow `main.js` into a new
monolith.

## Run

```sh
python cube/serve.py              # from the repo root, then open http://localhost:8087/cube/
node --test cube/tests/topology.test.mjs   # the model-layer teeth
```

Use `cube/serve.py`, **not** `python -m http.server`: stdlib's server reads
MIME types from the Windows registry and serves `.js` as `text/plain`, which
makes the browser refuse the ES modules and the page comes up blank.
