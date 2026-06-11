# Report 0027 — the ontabet transfer zip comes home as source

﻿## What landed

No done-line ? archival housekeeping, not build work; named here
instead. Two things happened this session:

1. The primary checkout (bdo's viewport) was fast-forwarded to
   origin/main ? it was 4 commits behind; `.codex/` arrived with the
   codex-native-fence merge (PR #26), which is why it was missing
   locally.
2. The untracked `docs/sources/files.zip` bdo flagged turned out to be
   the ontabet session's transfer vehicle (report 0025): six files,
   of which only two are landed in the repo (`language/basin.md`,
   `language/s-frame-placements.json`). The other four exist nowhere
   else ? `landing-map.md` and `handoff-ontabet-session.md` (the seven
   pins; PIN-1/PIN-2 load-bearing for waves 2+),
   `memo-creole-glyph-language-claude.md` (the 15 proposals awaiting a
   return route), and `viewer.html` (the BUILD-3 spec). An untracked
   zip on one machine is a fragile home for material the epic depends
   on. bdo said commit it; this PR carries the zip byte-identical
   (61,528 bytes) into `docs/sources/`.

## Conflict named

`docs/sources/` is read-only to sessions (hard rule). The zip was
already sitting there, left by the wave-1 landing session; this commit
preserves it where it lay rather than authoring anything into the
vault. bdo's go-ahead (2026-06-10) is the authorization; his stamp on
this PR makes it the record.

## needs-you

- Stamp this PR ? the zip is then durable on `main`.
- Report 0025's open items still stand (the seven pins, the unsealed
  export, the missing envoy return route); this PR changes none of
  them ? it only stops the source material from being one delete away
  from gone.

## End-state

`report` ? primary checkout current on main; the ontabet transfer zip
committed as source; nothing built.
