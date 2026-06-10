# Report 0015 — the envoy: the repo tells its arc to foreign reviewers

## What landed

By done-line 0015, all of it:

- **The envoy skill** (`.claude/skills/envoy/SKILL.md`, v0.1.0): the
  ritual for turning a natural-language export request into a sealed
  package of at most ten flat files for review by another model
  family. The skill carries the request grammar — six knobs (subject,
  audience, framing, questions, feedback shape, depth) the session
  resolves on purpose instead of silently — a framings table, and the
  authoring voice rules (zero shared context, arc as story, tensions
  as the gift).
- **The export pen** (`envoy.py` beside it, stdlib only): verbs
  `new / plan / build / check / seal / render / list`. One slot table
  (`SLOTS`, the `PIPELINE` pattern) with three modes: pen-built
  deterministic (architecture with live Mermaid from the pipeline
  table and an AST-derived import graph; repo map over `git ls-files`;
  history digest with cadence charts; code/doc embedding; log-fold
  data; metrics), session-authored (briefing, synthesis, excerpt,
  tensions), and hybrid (arc: authored narrative over a marker-fenced
  deterministic timeline — the knoll.py pattern). The gate refuses:
  an eleventh file, stray files the spec never named, unfilled stubs,
  empty files, budget overruns (≈120k total / 40k per file by
  default), a briefing missing its manifest block, sources that
  escape the repo. Rebuilds never clobber authored prose.
- **The disclosure ledger**: packages under `exports/` are gitignored
  artifacts; every seal appends a receipt (per-file sha256 + token
  estimates, framing, `--by`, package hash) to the committed
  `exports/log.jsonl` (union-merge, `-text`). Re-sealing unchanged
  bytes is a no-op; changed bytes accrete a new receipt. `list`
  reports drift between disk and ledger.
- **Governance wiring**: `exports/CLAUDE.md` founds the surface (the
  write guard now governs session writes there), root `CLAUDE.md`
  @-imports it, `.claude/CLAUDE.md` names the new pen.
- **Tests** (`tests/test_envoy.py`, 16 tests; suite 117 OK): the §10
  set — stray locally-fine file refused, eleventh slot refused,
  source escaping the repo refused, unfilled stub and empty file
  refused, budget overruns refused, seal-while-red refused — plus
  byte-determinism of pen slots across rebuilds, authored prose
  surviving rebuild, timeline landing only between markers, receipt
  shape, re-seal no-op, and the CLI result protocol. One real bug was
  found by the failing test and fixed in the pen (unknown slot kinds
  hid duplicate-slug detection).
- **The proving package** (`exports/loop-substrate-review/`, sealed,
  receipt 1 on the ledger): a real fresh-eyes architecture review
  package — 8 files, ≈16.7k tokens — briefing, authored arc over the
  deterministic timeline, architecture, repo map, history, loop core
  + tests embedded, and seven authored tensions. Ready to hand to a
  foreign model as-is.

## Conflicts and findings, named

- The deterministic timeline surfaced parallel-session scars worth
  knowing: **two `Session report 0003` files** exist on disk
  (duplicate id, pre-pen era), and done-lines 0014/0016/0017 landed
  from sibling branches during this session — the pens' id-from-fold
  discipline is earning its keep. No action taken; recorded here and
  used as live evidence in the proving package's tensions file.
- Tension 7 in the proving package names a real invariant bend: the
  envoy's authored files are a session's testimony sealed by the same
  party that wrote them — no second party judges package *content*
  (the receipt only records the act). If that bend matters, the fix
  shape is a summons (a second node judging packages before seal);
  flagged below rather than built unbidden.

## needs-you

- **The proving package awaits your call**: `exports/
  loop-substrate-review/` is sealed and sendable. Paste its files to
  a foreign model when ready — and whatever returns should come home
  through a report (SKILL.md §"What returns").
- **No renderer on this machine**: `render` extracts `.mmd` sources
  and degrades cleanly; if you want SVGs, `npm i -g
  @mermaid-js/mermaid-cli` makes the same verb produce them.
- **Should sealing require a second set of eyes?** (Tension 7 above.)
  Today: any session seals with `--by`. If you want the stamp in the
  path before anything is actually sent, say so and the seal verb
  grows an owner gate.

## End-state

`report` — done-line 0015 is met: the envoy skill + pen landed with
its gate, ledger, and tests (suite 117 OK), proven end-to-end by a
sealed real package; nothing red, three items queued for bdo above.
