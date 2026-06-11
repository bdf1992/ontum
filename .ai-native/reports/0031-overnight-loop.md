# Report 0031 — overnight-loop skill

## What landed

Done-line 0031 adds the first repeatable overnight-loop capability:

- `.claude/skills/overnight-loop/SKILL.md` defines when to use the ritual and how a long autonomous run starts, stops, tests, and hands off.
- `.claude/skills/overnight-loop/overnight.py` adds the read-only `brief` command. It refuses owner-viewport branches, non-session branches, dirty trees unless explicitly inherited, and unknown arc ids.
- `tests/test_overnight_loop.py` pins the refusal cases and the valid brief contract.
- `.claude/CLAUDE.md` indexes the skill with the other versioned rituals.

Validation run:

- `python -m unittest tests.test_overnight_loop -v` -> 6 tests OK.
- `python .claude\skills\overnight-loop\overnight.py brief --arc epic.substrate --objective "build the first repeatable overnight-loop capability"` -> refused dirty tree as expected.
- Same brief with `--allow-dirty` -> emitted the run contract for `epic.substrate` on `codex/overnight-loop`.
- `python .claude\skills\overnight-loop\overnight.py brief --arc epic.nope --objective "prove unknown arc refusal" --allow-dirty` -> refused unknown arc as expected.
- `python -m unittest discover -s tests -v` -> 270 tests OK.

## needs-you

Nothing blocks the landed capability. Arc-level sign-off remains bdo's call: this increment treats `epic.substrate` as the carrying arc for overnight-loop infrastructure, not as permission for a session to stamp owner-only decisions.

## End-state

`report` - repeatable overnight-loop preflight skill exists, is tested, and is ready for review on branch `codex/overnight-loop`.
