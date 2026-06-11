# glyphs/ — phase-2 semiotics

```sh
python glyphs/knoll.py        # regenerate the glyph inventory
```

[knoll.py](knoll.py) derives the glyph systems from `docs/phase-2/` and
regenerates `glyphs/registry.json`, `glyphs/knolling.md`, and the data
block between `GLYPH_DATA` markers in `glyphs/viewer.html`. **Never
hand-edit those generated outputs** (the viewer app *around* the
markers is authored and editable). Pins are re-validated against the
live doc text on every run; an inconsistency in the vault becomes a
recorded finding, not a fix — `docs/phase-2/` stays read-only.

Since done-line 0027 the generator also parses two surveyed sources
outside the vault, live like the grip ledger: `language/basin.md` (the
recursive-pilish lexicon — measured census, density, collisions) and
`language/s-frame-placements.json` (loaded as PROPOSED under a
structural gate that refuses address collisions and kind mismatches —
loading is not stamping). It verifies the incidence laws (closure =
3^dim, star = 2^codim, Σ = 125 both ways) on every run and demotes any
MINTED term without a non-example to OPEN, visibly.

The viewer (done-line 0029) navigates frames: descend re-labels the
one cube from a frame stack (S's placed words [PROPOSED], a letter's
term frame with its basin pivot candidate, ⊘'s interstitial frame),
ascent is the breadcrumb — and every operation (turns, scramble,
explode, x-ray) stays live at every level, words riding pieces so
turns displace the pairing visibly. Experience only: nothing the
viewer does writes a record or decides a pin. Two pure blocks carry
the testable math — `CUBE_MATH` (group laws) and `FRAME_MATH` (frame
vocabulary) — both extracted and run under node by
`tests/test_viewer_cube.py`.

The `glyph-knolling` skill in `.claude/skills/` is the full ritual: run
it when `docs/phase-2/` changes, when a term or glyph is minted, or
when asked to review or create glyphs.
