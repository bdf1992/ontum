# exports/ — the envoy surface

Packages the repo sends out for review by other model families. Each
package is a directory of at most ten flat files: an arc with visuals
(text-first Mermaid/ASCII), code, tests, documentation, and history.

- Package directories are **gitignored artifacts** — rebuildable, not
  records. `log.jsonl` is the **committed disclosure ledger**: one
  appended receipt per seal (files, hashes, token counts, framing,
  `--by`). Append-only; never edit a line.
- The one pen is `.claude/skills/envoy/envoy.py`; the ritual is the
  `envoy` skill (`.claude/skills/envoy/SKILL.md`). Pen-built files are
  deterministic — never hand-edit them; authored slots (briefing, arc
  narrative, syntheses) are the session's to write, in place of the
  `envoy:stub` block the pen scaffolds.
- Everything in the repo is in-bounds for disclosure (bdo, 2026-06-10),
  synthesized documents included — but only what the spec names gets
  packaged, and the gate refuses stray files. The receipt is what makes
  an export an act on the record instead of a copy that left quietly.
