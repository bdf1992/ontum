# Report 0076 — The change-axis gate: the decomposition procedure's teeth

## What landed

**Done-line 0104** — the smallest invariant of bdo's decomposition procedure,
hardened so a bad cut now *costs* something.

bdo named the procedure (anchor → find change-axes → cut one-axis-per-module →
orient into a DAG → contract the seams → verify by the change test) and asked
for the smallest piece of invariant we can start hardening, so decisions start
mattering and change tests harden us against drift. The load-bearing claim —
**modules align with axes of independent change, not categories of thing** — had
no teeth: nothing on disk could refuse a decomposition that violated it.

The fork bdo confirmed this session: **AI-native specialized** — a seam-contract
carries `trust` / `authority` / `change_rate` as first-class required fields.

What is now real:

- `decompose/change_gate.py` — a pure, read-only, stdlib fold (the
  `causality/term_economy.py` grain) that judges a *declared* decomposition
  manifest and refuses five ways, each refusal one hardened invariant:
  **smeared-axis** (two modules, one change-axis — the §10 teeth),
  **incomplete-axis**, **dependency-cycle**, **uncontracted-seam**, and
  **smuggled-seam** (the AI-native contract missing its protocol fields).
  CLI ends in `done | report | needs-you`.
- `decompose/examples/ui-split.manifest.json` — bdo's worked UI split
  (tokens / wiring + an AI-native copy *agent* seam) as the coherent anchor.
- `decompose/CLAUDE.md` — the directory's environment (nested-loaded, not
  pulled onto the root composition surface — its knowledge matters inside it).
- `tests/test_change_gate.py` — the §10 test: the anchor is coherent, each
  broken sibling is derived by ONE mutation of it and refused for its own named
  reason, and the gate is proven non-vacuous (no constant verdict passes).

The teeth bite: the committed anchor reads `coherent`; mutating wiring to share
tokens' reason, or stripping a contract's `change_rate`, is refused with the
finding naming the cut to fix. 848 tests pass (2 skipped).

## needs-you

- **The agnostic-vs-specialized fork is now spent on AI-native.** If you ever
  want the gate to also judge a plain (non-AI) design, the AI-native contract
  fields become optional-by-kind — a schema move, not a rewrite. Flag it if so.
- **The undercut detector is the named next node** (done-line 0104, not in
  scope): catching one module that secretly owns *two* axes (vs. this line's
  two-modules-one-axis overcut) needs the manifest to admit a declared-then-
  refused multi-reason. One real node at a time (§9).
- Wiring the gate into the loop (a `decomposition-drift` gap kind, a summon
  surface) is the next arc — this line hardened the invariant; carrying it
  ambiently is the follow-on.

## End-state

`report` — done-line 0104 met: the change-axis gate refuses a smeared axis, a
cycle, an uncontracted seam, and a smuggled (AI-native) seam, with a §10 test
that a constant gate fails; full suite green. On branch
`claude/decomposition-change-axes-a57frr`, ready to push.
