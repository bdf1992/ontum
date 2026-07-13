# tabletop/ — the Tabletop Simulator object forge

The paper-play kit for **Catalyst Core: The 13th Hour** (the RiftRealms
compendium is canon; bdo's concept notes are the gameplay input). This
module turns one declared spec into Tabletop Simulator–importable
objects and their Lua scripts: generic tinted shapes, the eight element
grain bags, tiered hourglasses, the global clock, biome tiles, persona
pawns, timecoin, and an in-game spawner console. Done-line 0198.

```sh
python tabletop/forge.py check     # validate the spec against the canon laws
python tabletop/forge.py build     # regenerate tabletop/build/ (objects, save, lua)
python tabletop/forge.py list      # what the forge would emit
python -m unittest tests.test_tabletop -v
```

## Layout

- [game.spec.json](game.spec.json) — **declared input**: the eight
  elements on the F₂³ cube (addr, color, opposite), the five tiers
  (grain capacity, timecoin value), races, classes, sample biomes and
  personas, and the clock defaults. Edit THIS to change the kit.
- [forge.py](forge.py) — the pen: stdlib, deterministic (GUIDs are
  content-hash), reads the spec, injects it into the Lua templates,
  and writes `build/`. It **refuses** a spec that breaks the canon
  laws: not exactly 8 elements, opposition that is not XOR 7,
  non-monotonic tier capacities/values (§10 teeth,
  `tests/test_tabletop.py` proves the refusal non-vacuous).
- [lua/](lua/) — authored Lua templates. `{{FORGE:*}}` placeholders are
  filled by the forge; an unresolved placeholder in `build/` is a bug.
- `build/` — **generated output, never hand-edit** (the
  `glyphs/registry.json` rule). Committed so bdo can download straight
  from GitHub:
  - `build/save/CatalystCore-PaperPlay.json` — a full TTS save (table
    laid out + Global chat commands). Drop into
    `Documents/My Games/Tabletop Simulator/Saves/`.
  - `build/objects/*.json` — individual Saved Objects. Drop into
    `.../Saves/Saved Objects/`.
  - `build/lua/*.ttslua` — the scripts standalone, for pasting onto
    any object in-game.

## Rules of this directory

- **The spec is the one truth; build/ is a fold.** Behaviour changes
  land in `game.spec.json` or `lua/`, then `forge.py build` — never in
  `build/` bytes directly.
- **Objects are generic and flexible by GM Notes**: every scripted
  object reads its config (element, tier, rate, pool…) from its GM
  Notes JSON at load, so any object can be repurposed in-game without
  touching Lua. The scripts default sanely when notes are absent.
- **Physical-play affordances only.** The Lua runs inside Tabletop
  Simulator: counters, spawners, broadcasts, a census. No game AI, no
  network, nothing that decides for the players.
- The compendium sources live outside the repo (bdo's upload); the
  spec carries what the kit needs and cites the canon in its `_meta`.
