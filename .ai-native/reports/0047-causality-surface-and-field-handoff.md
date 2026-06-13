# Report 0047 — Causality as compositional surface — arc recorded, field-topology missed, the board fold handed off

This session ran long across two threads (an ungoverned UI/UX sandbox and
this repo). It ends mid-arc by design — bdo asked for the next build (the
real Field fold) to be handed off to a fresh session. This report is that
handoff: a fresh session should be able to pick up the build from here
with no other context.

## What landed (on the record)

- **`atom.field-topology.v0` judged twice this session, honestly:**
  - value-gate (`value-gate.claude.v1`) → `accept` was a **no-op**
    (`rcp.460a2559520e` already existed for that node+version, I-2).
  - value-confirm (`value-confirm.claude.v1`) → **`missed`**
    (`rcp.3e08d1446381`). This is value-confirm's **first real light**: the
    atom passed value/stamp/placement/handoff, but `loop/field.py` was
    **never built** — no module in the tree, no merge receipt, no
    `atom.landed`. The gate caught a genuine claim/delivery gap. The atom
    now **parks for bdo (D-4)**; the gap fold names the move: amend the
    atom (new version restarts its pipeline) once the work exists, or bdo
    surfaces retirement.
- **`epic.causality-surface` recorded** at
  `.ai-native/epics/epic.causality-surface.json` (owner bdo) — bdo's
  2026-06-12 arc "Causality as an AI-native compositional surface,"
  written to the record so it isn't lost to chat. **NOT yet landed** —
  it is an untracked file in the working tree awaiting bdo's structural
  call (see needs-you). It is a **composing** epic: its glue cites
  `epic.the-field` and `epic.experience-layer` and refuses to double-build
  (§10).

## What exists in the foundry (ungoverned sandbox, OUTSIDE this repo)

At `c:\Users\bdf19\experience-foundry\` (not in ontum git): a working
**typed pulse machine** — `lib/causality.js` (the engine: typed nodes
stock/source/sink/code/inference/gate/pointer/pen/card/readout; routes
that refuse incompatible wires; pulses carrying data; per-node latency vs
expectation; a stats fold), `canvas.html` (gesture+template authoring,
live stats), `infer-bridge.py` (a localhost CORS endpoint on :8378 doing
**real local inference** — ollama `mistral:latest` default, or `claude -p`
— never a cloud API). The success story is **proven**: user input → code
(build query) → inference (local) → pen (receipt), end-to-end. The whole
thing is disclosed in the **sealed envoy package** `exports/causality-envoy/`
(7 files, receipt on `exports/log.jsonl`, framing: Causality as ontum's
live visualization lens, assist-not-take-over).

## The next work (the handoff's point) — build `loop/field.py`

bdo said yes: build the real Field fold and render it locally. The
contract is **frozen done-line 0050** (read it verbatim). In short:

- A **pure, read-only fold** in `loop/`, run as
  `python -m loop.field --arc <epic-id>`, producing one arc's
  **decomposition ladder**: arc → epic → story → task → environment →
  node → occupant, each rung carrying **state**, **evidence** (record ids
  on the log, never prose), and **next_safe_move** (an existing pen's
  verb, or "needs bdo").
- **Absence is information**: `arc/epic/story/node` are real on disk;
  `task/environment/occupant` are partial/implicit — the fold **surfaces
  the missing rung as a named gap, never invents it**.
- **Occupancy carries authority**: an occupant with no `node_real`
  admission (today `merge-node.claude.v0/v1`,
  `value-loop.story-author.mock.v0`) renders **un-authorised**.
- **§10 test required** that **fails on a fabricated/constant ladder**:
  real rungs populated with evidence ids, not-yet-first-class rungs named
  as gaps, ≥1 un-authorised occupant flagged.
- **`loop/gaps.py` is the proof-of-shape** — reuse its vocabulary (gap /
  drift / refusal / parked / pulse / owner-work) and its read-only,
  routes-through-an-existing-pen discipline.
- A **working proof-of-shape already exists**: I folded
  `.ai-native/epics/*.json` + the log into the current board this session
  (8 epics, every piece, each piece's latest log state) — a ~30-line
  read-only fold. `loop/field.py` is that, productionized to the ladder +
  evidence + next_safe_move + the §10 test.

Then **render it locally** (NOT GitHub — see the tension below): a
Mermaid diagram, a served page extending `loop/web.py`, or the Causality
canvas. This is `epic.the-field`'s `atom.field-portal.v0` /
`epic.causality-surface`'s workstream B — a later piece; the fold (this
done-line) comes first.

Governed-work reminders for the building session: develop on a `claude/*`
branch, land through the PR pen → merge-node (never push to main),
tests pass first, end with a report.

## The board question, resolved for the next session

- **GitHub today = gestures, not a board.** Closing an issue is how bdo
  confirms an arc / grants realness / grants a rung; `gate.py` opens a
  trust-rail issue per run; the reflect pen mirrors his stamp-queue. A
  work-item issue board would **collide** with "close = confirm." So:
- **Local diagram first** (read-only, safe, the Causality lens). A
  **GitHub board is a later, governed mirror** through the reflect pen —
  label-separated issue kinds, strictly one-way (the log stays truth;
  closing a board issue must not mutate the log).

## needs-you (bdo's queue)

1. **Confirm the structure of `epic.causality-surface`** — keep it as a
   composing epic over `the-field` + `experience-layer`, or fold its new
   pieces into those two? Until you say, it sits uncommitted in the
   working tree; on your word a session lands it (branch → PR →
   merge-node) and sets up its arc-confirm issue so you confirm by
   gesture.
2. **`epic.the-field` confirmation.** `atom.field-topology.v0` is
   value-confirmed worth building and parks on your standing arc-confirm
   of `epic.the-field` (done-line 0028). Confirming the-field lets its
   pieces flow.
3. **`field-topology` is parked `missed` (D-4).** Once `loop/field.py` is
   built and landed, the atom is amended to a new version to restart its
   pipeline. The `missed` stands as history either way.
4. **Projection target:** local diagram (recommended), GitHub board
   (later/governed), or both?
5. **The `causality-envoy` package** is sealed and unsent — whether to
   send it for outside review, and to which model family, is your call.

## Conflicts / notes

- The foundry Causality is an **ungoverned prototype**; bringing it into
  ontum is the governed step (the inference node would become a branded
  `ontum-node` behind a trust rung — same seam as `gate.py`). No fabric
  was touched; the boundary held.
- `epic.causality-surface.json` is **loose in the working tree** (not
  stranded silently — surfaced here in needs-you #1, awaiting your
  structural call before it lands).

## End-state

`report` — Causality's arc is on the record (`epic.causality-surface`, unlanded pending bdo's structure call); the Field's first piece is honestly `missed` (`loop/field.py` never built); the next session builds that fold against done-line 0050, renders it locally, and lands it — five owner taps wait above.
