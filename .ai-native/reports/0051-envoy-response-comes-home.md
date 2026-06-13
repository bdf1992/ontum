# Report 0051 — the envoy's response comes home; the dependency rule lifts; the return seam is the blocker

## What landed

This session sealed an envoy package on the testing infrastructure —
`exports/qa-metabolism/`, framing QA here as a three-layer metabolism
(deterministic tests · the runtime gate-pipeline · the self-sensing
organs), sent to a foreign reviewer with the challenge *"is this real
validation or receipt-theater?"* (receipt on `exports/log.jsonl`,
package_hash `8538e3ef…`).

A response came back: `docs/sources/epic.test-metabolism.v2.md` — a
reviewer-shaped critique that dual-keys every QA handle to its
standard-practice name (the log-is-truth → event sourcing/CQRS, atom =
sha256 → content-addressed storage, §10 → negative-path testing) and
lands three corrections. The sharpest is a direct hit on the envoy we
just shipped: the `refuse`-token count (370) it featured is a **vanity
metric** in the precise sense coverage% is — it counts a proxy, not the
property — and assertion density without per-assertion messages is
**Assertion Roulette**, an empirically-measured debugging smell. The
correction is fair and is recorded here rather than quietly edited out
of the sealed snapshot (the snapshot stands as history).

Verifying the review's load-bearing claims against the live repo (the
reviewer saw a frozen snapshot, so its claims are checked before any
are acted on): the 370 count **is** a proxy, confirmed; done-line pin
coverage **47/49**, confirmed by measurement; 0 disabled/`xfail`,
0 tautological tests, confirmed; the "zero-dependency repo" premise it
leans on **was** true (no `pyproject`/`requirements`) — and is the one
premise this session deliberately changed.

**bdo lifted the dependency rule (2026-06-12).** The blanket
no-dependency ban is gone, replaced by a common-sense bar: *stdlib-first;
a third-party dependency is admissible when it creates real value —
don't hand-roll what a mature library does right — provided it stays
offline and named.* A repo-wide audit reconciled every statement of the
old rule, split three ways:

- **rule statements** (a prohibition) → amended in every canonical home:
  `loop/CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`,
  `fence/CLAUDE.md`, the glyph-knolling skill, and two justification
  lines in the gate pen (now citing *no-network*, the real reason reach
  stays out of `loop/`, instead of *stdlib-only*).
- **module purity facts** (`loop/*.py` docstrings, the fold tests'
  "no subprocess, no network, no git") → **kept untouched**: they
  describe what a module *is* and are tested contracts; rewriting them
  would make true statements false.
- **preserved invariants** → `no broker / no daemon / no network at
  runtime` remains a hard rule. The lift is *only* the dependency ban;
  local-first is whole.

What this unblocks: the test-metabolism arc's piece 2 can now stand up a
real mutation lane for an actual oracle-gap score (the review's
Correction 1) instead of laundering a one-mutant grep — though a pure
stdlib `ast`-mutate-and-rerun lane remains the cheaper first reach.

The dep-rule edits are in the working tree on the main viewport,
uncommitted — they want a branch + PR to land as a stamped increment
(authored by this session, so an independent merge-node lands them).

## needs-you

- **The blocker, named: the envoy is one-way.** Its pen verbs are all
  outbound (`new → plan → build → check → seal → list`); there is no
  `respond`/`intake`/`import`. So a returned review has nowhere to land
  as *work* — only read-only `docs/sources/` (context, not material) or
  a hand-written report (a record the queue never sees). That is why
  this response stranded in `docs/sources/`. To **place an envoy
  response in the queue**, it must become value-gated atoms on the log,
  surfaced by `gaps.py` as pressure-ordered backlog. Closing that
  inbound seam is the candidate next work — your steer on whether to
  queue it.
- **The QA/test pattern this response carries** (for consideration, not
  yet actioned): `epic.test-metabolism.v2` proposes a repeatable
  `test-organ` skill — a definition-of-done for tests + a type-dispatched
  review rubric + a non-bypassable gate + a self-surfacing backlog. It
  is a **draft arc**, not yet an epic in `.ai-native/epics/`, awaiting
  your confirm-gesture. Two structural notes from this session before it
  is confirmable: piece 2's mutation lane should weigh a stdlib
  `ast`-based lane against a third-party dep now that the rule allows
  either; and piece 6 (orthogonality), which the draft itself flags as
  maybe-not-buildable, belongs as the report that *closes* the arc, not
  inside the build order.
- **Whether to publish the arc.** Recommendation: yes, but after it is
  built — a sealed envoy of an unbuilt arc is a promise, not a result,
  and publishing the plan today repeats the vanity-metric mistake the
  reviewer just caught.

## End-state

`report` — the response is home as this record; the dependency rule is
lifted and audited repo-wide; the envoy's missing return seam is the
named blocker to queuing it, and the test-metabolism arc waits on bdo's
confirm — nothing external built, nothing committed, nothing actioned
past the rule lift.
