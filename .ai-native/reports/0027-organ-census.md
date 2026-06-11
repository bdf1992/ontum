# Report 0027 — the turning point, read by its instruments

## What landed

By done-line 0029: `loop/census.py` — the organ census, a pure stdlib fold
(no subprocess, no git) that takes the loop's measure of its own body. For
every organ (loop modules, hooks, skill pens, glyph generators) it crosses
two signals already on disk: **wired** (reachable from the working system,
not the organ's own test — regex over the real import styles, `from loop
import X` included) and **exercised** (a controlled literal of the organ's
appears as a value on an append-only ledger). The cross gives three
verdicts that are exactly bdo's three movements — **alive** (give care),
**wired·idle** (a writer plumbed in but never fired — needs attention),
**dormant** (disconnected — prune candidate). Read-only: it names, never
cuts (D-4). Tested (`tests/test_census.py`, 7 cases; full suite 256, green)
and recorded in `loop/CLAUDE.md`.

The §10 receipt is real, not ceremonial: the first live run called the
dormant `minds.py` *alive* on the word "local" — a bash keyword captured
in the watcher's raw audit, matching minds' legitimate `DEFAULT_FAMILY`.
A generic word shared between source and prose forged a trace and hid a
dead organ. Fix: the exercise vocabulary is controlled fields only — no
prose, no raw capture, no whitespace values. The test plants that exact
false positive and fails if the lens lets it through.

## What the instruments said (the session's opening assessment)

The signals agree on one pattern: **breadth outran depth.** The substrate
half is healthy (log clean, inbox 0, mirror no drift, 51 ticks steady).
But the spine stalled at L0:

- Only **2 of 5 pipeline stages ever went real** (`node_real` log holds
  value-gate and owner-stamp; placement, handoff, confirm have never been
  admitted real on any atom). The pipeline has never refused past the
  value gate — the §10 test the loop is built to run isn't running.
- **4 arcs, 0 confirmed** — arc-confirmation (0028) was built and has not
  been used once. The mechanism landed; the behavior change didn't.
- The census names the dead spots in the organs: **`minds.py` and
  `trust.py` are writers plumbed into the path that have never once
  fired** — a registry with zero registrations, a ladder no rung was ever
  granted on.

## needs-you

- **The wired·idle organs — `loop/minds.py`, `loop/trust.py`.** Built,
  tested, wired, never exercised. Each is a make-real-or-retire call. The
  census reports; the cut is yours.
- **Your collection question, answered by the evidence.** "Poor
  collection patterns → more branded wrappers?" The census says collection
  of *mutations* is already well-covered: every writer that fires leaves a
  recorded story (node, reconcile, the pens, the guards all show alive on
  their own words). The genuine gaps are not missing wrappers — they are
  *never-fired writers* (minds/trust) and the fact that the watcher's
  `--report` counts read-only calls it can't tell from mutations, so it
  can't cleanly nominate the next wrapper. The honest move is not to spray
  new wrappers now, but to sharpen the watcher to separate mutating from
  read-only and let it name the next one — its own stamped increment.
- **Two of five gates real.** If depth is the next movement, wiring
  0023's already-built placement collision logic in via a `node_real`
  admission is the cheapest first real refusal.
- **Parallel-fleet note:** a concurrent session is on done-line 0030
  (reflect `SURFACE_KINDS`), seen via a primary-tree edit to
  `loop/CLAUDE.md`. This work took 0029 and report 0027 from main's
  state; if the other session also took 0027, renumber on merge (0020/0021
  precedent). bdo merges.

## End-state

`report` — the usage lens is built, tested, and shipped on
`claude/organ-census`; PR opened for bdo's merge. It already named the two
dormant writers and answered the collection question with evidence. The
prune itself, and whether depth or monitoring leads next, stay the owner's
call.
