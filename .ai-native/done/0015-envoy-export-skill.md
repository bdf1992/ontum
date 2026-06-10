# Done-line 0015 — the envoy: the repo tells its arc to foreign reviewers

Written before code, per §9.4. When this line is met, stop.

bdo's ask, on the record (chat, 2026-06-10): a skill that exports the
repo as a structured collection of at most ten flat files — an arc
with visuals, code, tests, documentation, and github history — built
"both deterministically, generated, and on demand," driven by
natural-language requests, for review by other model families through
other perspectives and framings. Shaped answers (same chat): visuals
text-first (Mermaid/ASCII) with rendering optional; everything in the
repo is in-bounds for disclosure, synthesized documents included;
packages are gitignored artifacts but each seal leaves a committed
receipt; the package shape is core slots + flex slots.

> **Done when:** a versioned skill (`.claude/skills/envoy/`) turns a
> natural-language export request into a sealed package of at most ten
> flat files under `exports/` — deterministic slots (repo map, history
> digest, architecture as text-native Mermaid, metrics charts) built
> by a stdlib pen (`envoy.py`), generated slots (briefing, arc
> narrative, syntheses) authored by the session into stubs the pen
> scaffolds and refuses to seal unfilled; the gate refuses more than
> ten files, stray files the spec never named, and token-budget
> overruns; sealing appends a receipt (files, hashes, token counts,
> framing, `--by`) to a committed `exports/log.jsonl` — the disclosure
> ledger — and re-sealing unchanged bytes is a no-op; `render`
> produces SVGs beside the package when a Mermaid renderer exists and
> degrades to a report when none does; rebuilding never clobbers
> authored prose; and tests pin the refusals and the pen-built slots'
> byte-determinism (§10: a locally-fine eleventh file must not fit).
