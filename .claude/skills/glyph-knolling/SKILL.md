---
name: glyph-knolling
description: >-
  Re-knoll the ontum semiotics: derive and validate the two letter systems
  from the docs/phase-2 vault, refresh glyphs/registry.json, knolling.md and
  the 3D viewer, and review any new or changed terms under the grip
  discipline (pin, non-example, provenance status). Use when docs/phase-2
  changes, when a new term or glyph is minted, when asked to review or
  create glyphs, or when the user asks to "knoll" the vocabulary.
---

# Glyph Knolling

Knolling: everything out of the drawer, sorted by kind, laid at right
angles, labeled. Applied here to the project's semiotics — the letters,
cells, and minted terms of the ontum system — so that every glyph has an
address, every term has a referent (or is an honest hole), and every value
carries its provenance.

## The discipline (non-negotiable)

1. **The vault is read-only.** `docs/phase-2/` is quoted, cited, and
   validated against — never edited, "fixed", or paraphrased in place.
   An inconsistency found in the vault becomes a **finding** (a seam that
   does not close), recorded in `FINDINGS` in `glyphs/knoll.py`. Per the
   polysheaf doctrine: a failure to seam is data, not an error.
2. **Every entry carries a provenance status** (etymontoken style):
   - `PINNED` — quoted verbatim from a doc; source `path:line` cited and
     re-checked mechanically on every run.
   - `DERIVED` — produced by a stated rule from pinned anchors; the rule is
     recorded beside the values it produces.
   - `MINTED` — coined in a knolling session; provisional until bdo pins it
     **with a non-example** (a stated thing that does *not* count).
   - `OPEN` — a named hole; the slot exists, the referent does not yet.
   Grip-ledger statuses (`SETTLED`, `DEAD`) pass through as parsed.
3. **A grip needs a non-example.** Never promote MINTED → SETTLED yourself;
   that is bdo's cut. Your job is to lay the candidate readings side by
   side so the cut is easy to make.
4. **Generated files are never hand-edited:** `glyphs/registry.json`,
   `glyphs/knolling.md`, and the data block between the `GLYPH_DATA`
   markers in `glyphs/viewer.html` all come from `glyphs/knoll.py`. The
   viewer app *around* the markers is authored and may be edited.
5. **Stdlib only, no network, no dependencies** — same rules as the rest of
   the repo. The viewer stays a single zero-dependency HTML file that works
   from `file://`.

## The pass

Run this like a reconcile pass: re-read, move one step, end with a clear
result.

1. **Diff the vault.** `git log -p --follow docs/phase-2/` or compare
   against the last knolling commit. Note new terms, changed tables,
   changed wording near any pinned anchor.
2. **Re-run the generator:** `python3 glyphs/knoll.py`.
   - If it exits with *doc drift*, a pinned anchor moved or vanished. Read
     the doc, update the `POLYSHEAF_PINS` / `CUBE_PINS` anchors (or the
     derivation rule, if the doc's rule itself changed), and re-run. Never
     silence a drift error by deleting the pin.
3. **Run the tests:** `python3 -m unittest tests.test_knoll` (and keep
   `tests.test_loop` green — the loop is out of scope for this skill and
   must stay untouched).
4. **Semantic pass.** New terms in the vault (grip ledger §8 parses
   automatically; prose-defined primitives do not) get added to
   `PRIMITIVES` in `knoll.py` with a verbatim-faithful referent, a
   non-example, and a cited `path:line`. New candidate glyph readings go
   into the trio (or a new section) as `MINTED`/`OPEN`.
5. **Review the diff** of `glyphs/knolling.md` — that file is the flat-lay;
   its diff is the review surface. Confirm nothing PINNED changed without a
   corresponding vault change.
6. **Open questions go to bdo, not into the registry.** Anything needing a
   pin (e.g. the S·I·O trio reading) stays `OPEN` with the candidates laid
   out. List the open pins in your report.
7. **Report.** Sessions that change the knolling land a numbered report in
   `.ai-native/reports/` (next free number), stating: what drifted, what
   was re-derived, what was minted, what stays open, end-state
   `done | report | needs-you`.

## The Core 27 (MINTED, session 0009)

Every glyph of the 27 is the Self/void term of its own local frame —
globally a cell, locally the keystone of its neighborhood. The registry's
`core27` section carries the principle, the coining utterance, the
non-example, and the openness gradient (corner 7/19, edge 11/15, face
17/9, ⊘ 26/0 — in-frame neighbors / open slots). The open slots are the
typed capacity for future term placements; when assigning non-spatial
terms into frames, record the placement as a derived rule in `knoll.py`,
never as hand-edited registry data.

## Extending

- **A new lettering** (a third alphabet over the solid): add a derivation
  + pins in `knoll.py`, a `letterings.<name>` entry, and the viewer picks
  it up from the registry — add one toggle button in the `#bar`.
- **3D viewer:** open `glyphs/viewer.html` in a browser. Toggles:
  addresses/occupants (the two letterings), knolled (flat-lay), S·I·O
  spotlight, cascade (the worked example from the polysheaf doc, animated:
  A → seams I,M,Q → endpoint E → faces → the obscured wildcard ⊘).
- **Cube controls:** the viewer is a working cube over the generative
  minimum {U,D,L,R,F,B} — buttons, keys, or **dragging a facelet** to turn
  its layer (shift/′/right-click for counterclockwise; drag on empty space
  orbits). Scramble (a 20-letter word; God's number), unwind (the word
  read backwards), reset. The live state string follows cube-alphabet.md
  §7 exactly (`edge word | EO bits | corner word | CO trits`). The cube
  mathematics lives in the pure `CUBE_MATH` block inside the viewer;
  `tests/test_viewer_cube.py` extracts it and checks the group laws under
  node (auto-skipped if node is absent). Keep that block free of DOM and
  registry references — the purity is tested. Addresses stay put under
  turns; occupants travel — the two-alphabet split, demonstrated live.
  Solving the cube earns the Pilish line (word lengths spell π).
- **Facelets and colors:** sticker colors are the §7 pinned names
  (white/yellow/orange/red/green/blue), recorded as `face_color` on the
  six center entries in the registry; the hexes are authored in the
  viewer's `FACE_HEX`. Stickers are derived per frame from each piece's
  rotation matrix (`Mᵀ·n` pulls a world normal back to the home frame), so
  flips and twists render truthfully — never repaint them by hand. Letters
  are a toggle (`letters`); sound is synthesized Web Audio (`sound`
  toggle, no assets).
- **Printed letters:** the 26 letters render ON the facelets in per-face
  text frames (`TANG`, chosen so `tu × tv = −n` — never mirrored).
  Occupant letters are *glued*: their home-face frame is transported by
  the piece's rotation, so flips and twists show in the typography.
  Address letters print upright always — labels of fixed space. The void
  ⊘/∅ keeps its billboard glyph; billboards otherwise appear only in the
  knolled flat-lay (where faces go edge-on).
- **Links web (`links` button):** off → *seams* (the incidence skeleton
  from the registry's `seam_of`, drawn between the pieces currently
  occupying related cells — scrambling re-wires it) → *drift* (each
  displaced piece tied to the piece squatting its home cell: permutation
  cycles drawn as chords; solved = no chords). Lines follow pieces live
  through turns and through the knolled flat-lay. "drift" here is a loose
  viewer-level borrow of the ledger's word — flag it for bdo, don't
  promote it.
- **The two alphabets are complementary, not in conflict:** polysheaf
  letters name fixed **cells** (addresses), cube-alphabet letters name
  mobile **pieces** (occupants). Keep that split intact in anything new —
  it is the (position, value) substrate both docs describe.
