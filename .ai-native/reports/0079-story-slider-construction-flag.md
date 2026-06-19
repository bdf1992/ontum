# Report 0079 — The construction flag + the Complexity slider on one three-word phrase

# Report 0079 — The construction flag + the Complexity slider on one three-word phrase

**Session:** done-line 0106 · iterations 0011 · branch `claude/canvas-home-reshape` · 2026-06-17

## What bdo asked

At the Story demo, three things in one breath: *"I need a rule used in game dev.
Anything that is mock or not done, get a special flag so I can see the state of
construction. I want to bring in the slider now, and start with just one phrase,
three words. The Cat Naps."*

## What landed

1. **The game-dev rule = the missing-texture convention.** An unfinished or
   placeholder asset renders in deliberately glaring magenta (the Source-engine
   purple/black checker), so it can never be mistaken for finished or silently
   ship — ontum's mock-shame made visual on the canvas. Now a first-class,
   schema-driven token: `BUILD` in `canvas-system.js` (`real` / `mock` / `wip` /
   `todo`). §10 teeth in `canvas-system.test.js`: a fabricated build state is
   refused; every flagged state must carry a hazard color + a tag.

2. **The Complexity slider, live, on one three-word phrase.** The demo reduces to
   the single cat seed (no phrase-picker) and opens at **"The cat naps"** — one
   glyph. The Complexity slider grows sentence *and* mesh together (3 words →
   `+ sunbeam, warmth` → the full cat·sunbeam·shadow·warmth mesh): glyphs carry a
   `stage`, the slider filters by level, the sentence comes from `stages.texts`.
   First of bdo's five reference sliders (0005) made real, and the perturbation
   axis the story-benchmark wants (matched pairs by complexity).

3. **The flag, applied honestly.** The four not-yet-built sliders (Length, Twists,
   Weirdness, Colors) wear the magenta hatch + a `MOCK` tag — so the construction
   state of the slider feature *itself* is legible. Every relation edge renders
   magenta with a `MOCK` tag, because relations are still hand-authored, not yet
   composition-generated (iterations 0008): glyphs read as built (own colors),
   wiring reads as mock. A legend names the rule on the surface.

## End-state

- Committed `8f7efd1` on `claude/canvas-home-reshape`, pushed to origin.
- Causality node tests green: canvas-system **16**, phrases **11**, scorer **11**.
- Screenshot-verified both slider ends (`?c=0` three words / `?c=2` full mesh) in
  headless Chrome (`.ai-native/shots/story-3words.png`, `story-full.png`).
- Additive fields on `phrases.json` (cat phrase only) — the benchmark mesh is
  untouched; the recovery-scorer corpus still round-trips.
- Not yet on the live URL: only `main` deploys via `pages.yml`. This rides the
  `epic.causality-surface` arc; the merge-node lands it once the arc is confirmed.

## needs-you

- **Fleet id-collision on the prior session's done-line 0105.** This branch
  carried uncommitted story-benchmark work (the deterministic `recovery_scorer` +
  surface_trap teeth) left stranded on the viewport. Its done-line
  `.ai-native/done/0105-story-benchmark-scorer.md` collides with
  `0105-undercut-axis-one-module-two-reasons.md` on
  `origin/claude/decomposition-change-axes-a57frr` — the git pen refused to commit
  the colliding id (the 0020 incident guard). I committed the benchmark **code**
  (so the suite stays green and `phrases.json` is coherent) but **held back the
  0105 done-line record and report 0076**; both remain stranded on the viewport.
  A done-line is frozen and re-minting another session's is not a session's move
  (supersede is `--by bdo`). The clean resolution is to re-mint the benchmark
  done-line at the next free fleet id (true fleet max, not local) — either bdo
  supersedes 0105, or the next session re-mints it through `loop.pen` after a
  fetch so the fold sees the colliding id.
