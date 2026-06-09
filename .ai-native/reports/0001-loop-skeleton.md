# Session report 0001 — phase-1 loop skeleton

- **Date:** 2026-06-09
- **Session:** Phase 1 worker, first build session (continues session 0's `needs-you`)
- **Branch:** `claude/friendly-allen-occrt3` (bdo merges — D-4 applied to git)
- **End-state:** `done` — the 0001 done-line is met
- **Doctrine:** `ai-native-loop-substrate.md` v0.4.0, provided by bdo after
  report 0000; now at repo root and authoritative.

## Done-line (written first, `.ai-native/done/0001-loop-skeleton.md`) — met

1. **Goal over passes:** `atom.loop-skeleton.v0` reached `value_confirmed`
   through 11 reconcile passes over `.ai-native/log/` (each pass: re-read the
   fold, move one step — seed event, then alternating gate-receipt /
   derived-event steps through value → owner-stamp → placement → handoff →
   confirm).
2. **Kill test:** the committed log is from a live run that was SIGKILL'd
   mid-run at `story_accepted` (2 events, 2 receipts) and restarted. Recovery
   came entirely from the files: final state 6 events, 5 receipts, every
   receipt unique by `(node, artifact_hash)` — nothing lost, nothing doubled.
3. **Cache test:** deleted `queues/` + `offsets/`, replayed from `log/` with
   `--rebuild-cache-only`, sha256-diffed every file: byte-identical. A test
   also poisons a queue file and shows the pass ignores it and rebuilds it
   from the fold — queue membership is never authoritative (the §14.1 rule).
4. **Idempotent rerun:** passes after `done` mutate nothing (`step=none`,
   byte-identical log), and the unit suite covers rerun, torn-tail, and
   recovery paths: `tests/test_loop.py`, 6/6 passing.

## What landed

- `loop/reconcile.py` — stdlib-only, re-runnable CLI pass (no daemon, broker,
  network, or model endpoint — §11's endpoint deferred per the briefing).
  Shapes per §14.2/§14.3; the pass asks §14.4's five questions each time;
  every invocation ends `done | report | needs-you` (D-6).
- Line-atomic appends (whole line + flush + fsync) with torn-tail repair; the
  fold drops unparseable lines — a receipt not fully written didn't happen.
- Mock pipeline per §14.2's subscriber examples: story-author (seed) →
  value-gate (L0) → owner-stamp → placement-gate (L1) → handoff-gate (L2) →
  value-confirm (L0 second check). No mock judges its own writer's output (D-2).
- Phase-2 material vaulted read-only under `docs/phase-2/` (untouched by the
  build, per the briefing).

## Deviations and judgment calls (named, not silent)

- **`owner-stamp.mock-bdo.v0` stands in for bdo.** D-4 says the human is the
  last stop; a mocked loop has no human in it. The mock is a separate node
  (no self-sign) and is flagged in the code as the first mock that must be
  replaced when any node becomes real. The atom file's `owner_stamp` stays
  `pending` — only the log carries the mock's stamp.
- **Fold drops *any* unparseable line, not only the torn final one.** A
  superset of §14.1's torn-tail rule; dropped lines are counted and printed
  every pass so they're visible, never silent.
- **Atom state lives in the fold, never the atom file.** The atom JSON is the
  immutable birth record and the content-hash source; its `verdicts` block is
  authoring-time only. Mutating it would change the artifact hash and break
  receipt idempotence.
- **Branch:** session harness mandates `claude/friendly-allen-occrt3` over the
  briefing's suggested `phase-1/loop-skeleton`; harness wins, named in 0000.
- **`docs/culture/the-idea.md` and `the-ambient-loop.md`** are referenced by
  doctrine §15–§16 but not provided. Absence noted in `docs/phase-2/README.md`,
  not invented.

## Deferred (out of scope, per briefing)

Real nodes, the model endpoint, the surfacer, control session, review
ensembles, restart policy, backpressure, brokers, the language itself,
doctrine edits.

## Next, not now

Make exactly one node real, starting with L0 — needs bdo's input and a fresh
stamp (§9.3: no second real node until the first has a passing receipt).
