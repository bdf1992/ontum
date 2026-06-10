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

The `glyph-knolling` skill in `.claude/skills/` is the full ritual: run
it when `docs/phase-2/` changes, when a term or glyph is minted, or
when asked to review or create glyphs.
