# LOOP — the iterative agent environment (SDLC, same sessions)

*bdo's instruction, 2026-06-16: a working loop and environment the agents
iterate against, reusing the same agent sessions across feedback rounds,
following the SDLC patterns you'd expect. Built on ontum's grain: the
files here are truth; agent sessions are mortal; the rubric is the gate;
ISSUES.md is the feedback channel.*

## The environment (what the agents work against)

```
evolution/
  RUBRIC.md            the acceptance gate (the "tests")
  LOOP.md              this file — the process + the agent roster
  ISSUES.md            the feedback log agents iterate against
  current-commons.json frozen copy of v0 — the source every agent reads
  families/
    <family-id>.evolved.json   one file per agent — its owned artifact
```

**Files are truth.** An agent session can die; its `families/<id>.evolved.json`
survives and the re-spawned agent picks up exactly where it left off. No
continuity lives only in an agent's context — the same property that lets
ontum point disposable sessions at real work.

## The cycle (SDLC)

```
 BACKLOG ─▶ DRAFT ─▶ REVIEW ─▶ ISSUES ─▶ ITERATE ─▶ ACCEPT ─▶ MERGE ─▶ VERSION
            (agent)  (vs RUBRIC) (logged)  (same       (bdo)   (into    (commons
                                            session)            commons)  v0→v1)
                        ▲                                 │
                        └─────────── re-review ◀──────────┘
```

1. **Backlog** — the 10 work-items below + the landmark refresh.
2. **Draft** — each agent writes its `families/<id>.evolved.json`.
3. **Review** — Claude scores each draft against RUBRIC.md, files findings.
4. **Issues** — written to ISSUES.md, keyed by family and severity.
5. **Iterate** — a per-family agent is handed its open issues and revises
   its own file. Continuity is the FILE, not the agent's context
   (SendMessage session-reuse is unavailable in this harness, so the
   durable `families/<id>.evolved.json` IS the session — a re-spawned
   agent reads its file + open issues and continues exactly where the
   last one stopped. This is ontum's mortality model, not a workaround).
6. **Accept** — bdo blesses (praise is the deposit gesture, D-4).
7. **Merge** — accepted families fold into the evolved commons.
8. **Version** — `pattern-commons.json` v0 → v1 when the set is accepted.

## The roster (agent = family owner; ids filled on spawn)

| Item | Family | File | Task | Agent id (round 0) | Status |
| --- | --- | --- | --- | --- | --- |
| F1 | Living Data Maps | living.evolved.json | re-tag + evolve | ad88ba9ce59838ddd | running |
| F2 | Curated Topologies | topo.evolved.json | re-tag + evolve | ab546828162a5473a | running |
| F3 | Spatial Navigation | spatial.evolved.json | re-tag + evolve | a2a0f5bc3def5af43 | running |
| F4 | Playable Systems | play.evolved.json | re-tag + evolve | aa2b4256ae8759416 | running |
| F5 | Generative Instruments | instr.evolved.json | re-tag + evolve | a24a3706b62a02fb8 | running |
| F6 | Ambient HUD Craft | hud.evolved.json | re-tag + evolve | aebed68dee52c0ef8 | running |
| F7 | Editorial Craft | edit.evolved.json | re-tag + evolve | adeb2cab5a85fdcc6 | running |
| F8 | Register & Provenance (NEW) | register.evolved.json | author | af372dc3cc3f2490e | running |
| F9 | Interface as AI (NEW) | interface-ai.evolved.json | author | a540926e401157304 | running |
| F10 | Honest Async (NEW) | async.evolved.json | author | ab4f05ba6638247c9 | running |

*Round 0 launched 2026-06-16. Iteration handle: SendMessage to the agent
id above while alive; else re-spawn against the family's file + open issues.*

### Round 1 — review-driven revision (re-spawned against file + ISSUES.md + RECONCILIATION.md)

living accepted at round 0 (clean). The other 9 re-spawned on the
reconciled commitment model:

| Family | Round-1 agent id | Driver |
| --- | --- | --- |
| topo | ad51827656710b7fd | de-conflate commitment vs strata |
| register | a5cbf02a8c77732f6 | re-ground on lifecycle/C4, drop ghost cite (keystone) |
| async | a83ff6da3bf6ddb80 | runtime≠register; waiting-on-owner→commitment |
| play | aa86730d752522ce8 | dedup poke-to-route / simulate-before-commit |
| hud | a9f259304f19c5afa | dedup provenance-tooltip; legend renders canon |
| edit | abb318719c54d9882 | dedup authored-finish → cite schema gate |
| interface-ai | ad5e8146c92b49a9d | honest axes on virtual-request-node |
| spatial | a5127e2d1a4915de5 | altitude-breadcrumb axis honesty |
| instr | a7926441479a9de0c | narrow provisional-take → keep-gesture |

**Round 1 complete (2026-06-16).** All 9 revised; `merge.py` folded the 10
family files into `pattern-commons.v1.json`. Final gate: **0 verdict/axis
mismatches** — no inflation survived. v1 = 10 families, 53 patterns
(15 decoration · 12 truth-capable · 26 ai-native), 237 kin links.
Status: PROPOSED — awaits bdo's bless (D-4).

Held for bdo's stamp: the C19·RegisterFacet amendment to
causality/display-system.md (proposed PR, not landed).

## The contract every agent gets

- Read `current-commons.json` and `RUBRIC.md` before writing.
- Own exactly one file: `families/<id>.evolved.json`. Never touch another's.
- Score every pattern on all three axes; assign the derived verdict honestly.
- Decoration is a valid verdict — do not inflate a pretty pattern to ai-native.
- Each run ends by writing its file AND returning a short status (what
  changed, open questions) so the review can file issues.
