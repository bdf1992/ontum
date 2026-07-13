# Report 0133 — Tabletop object forge — the Catalyst Core paper-play kit, forged, reviewed, pushed

## What landed

Done-line 0198, met. bdo asked (2026-07-13, with the RiftRealms compendium upload) for generic flexible shape/color objects for Tabletop Simulator and a script generator, carrying his paper-play concept notes (global clock, hourglass grains, timelessness, Timecoin, AP, biome generation, fog-of-war personas).

Built: the governed `tabletop/` module. One declared spec (`game.spec.json` — 8 elements on the F2^3 cube with XOR-7 opposition, 5 monotonic tiers, races/classes from the compendium, bdo's samples) is forged by `forge.py` (stdlib, byte-deterministic, content-hash GUIDs) into TTS-importable Saved Objects, a full laid-out save with `!cc` chat commands, and standalone .ttslua scripts. The kit: tiered hourglasses (time/timeless pools), the Global Clock (deletable/doublable hours; a skipped deleted hour costs a turn), biome tiles generating on End Turn, fog-of-war persona pawns, element grain bags, Timecoin mints, AP, and the spawner console — the in-game script generator — whose census reproduces bdo's worked example (Region A 5 Fire + Region B 10 Fire + Herald 5 Fire in A = region 10, world 20). The forge REFUSES an unlawful spec; `tests/test_tabletop.py` (14 tests) proves the refusals non-vacuous and the build deterministic; all six generated Lua files parse clean (checked with a local Lua parser).

The independent review was requisitioned and processed on the branch (six finder passes): 12 findings fixed — clock 12-hour desync + missing clock law, persona GUID collisions, fog-of-war name leak in the census, persona tier-capacity parity, edge-triggered timelessness broadcasts, console spawn reload, turn cost for skipped hours, provisional-AP flag carried into artifacts, refused-spec wording, bag-recipe dedup. One finding deliberately skipped (overlapping-biome region double-count — a table-layout choice; world totals stay correct).

## Conflicts named (not silently resolved)

- **PR-as-landing-unit vs no-PR instruction.** The repo's hard rule says a session opens a PR as the unit the merge-node lands; this remote session's platform instructions say (twice) not to create a PR unless explicitly asked, and bdo's ask named none. The tiebreaker was mechanical: `pr.py create` shells to `gh`, which does not exist in this environment (GitHub is MCP-only here), and opening the PR through raw MCP would bypass the PR pen's fence and the off-log atom gate. The branch is pushed and hand-off-ready; the PR needs a gh-bearing environment or the MCP-backed pen (#245 is the named mechanism; this is a live instance of that gap).
- **Suite red in the viewport, by design.** `test_git_pen.TestGitGuard.test_local_mutating_git_is_now_watched` fails whenever the suite runs inside the primary viewport tree: the workstation fence (correctly) denies `git checkout -b` there, but the test asserts watch-only. In a remote session the only checkout IS the viewport, so every push had to declare red for a failure that is the fence working as intended. The test (or guard) should account for the remote-session case; until then remote sessions push `--red-ok` with this exact declaration.

## needs-you

- **AP per turn = 3 is provisional** (flagged in the spec and in the shipped artifacts): your notes name AP but no amount — set it and the forge re-renders.
- **Keeper / Weaver / Mercer abilities are open** in `game.spec.json` (absence marked, not invented): fill them when the paper play finds them.
- **The PR**, when you want this carried to main: from a gh-bearing seat, `python .claude/skills/branch-ritual/pr.py create --rolling` on `claude/tabletop-game-objects-scripts-7yg82x`; the story text is ready in this session's transcript.

## End-state

`report` — two commits pushed on `claude/tabletop-game-objects-scripts-7yg82x` (kit + review fixes; red declared for the pre-existing viewport-environment failure); no PR (gh absent in this environment); done-line 0198 met.
