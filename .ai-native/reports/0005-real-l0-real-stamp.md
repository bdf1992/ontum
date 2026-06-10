# Session report 0005 — the first real node: L0 live, the stamp is yours

- **Date:** 2026-06-10
- **Session:** v-next build (report 0003 §4 / 0004 §3, stamped by bdo via
  chat: "continue as expected")
- **Branch:** `claude/great-faraday-djmq2x` (bdo merges — D-4 applied to git)
- **End-state:** `done` on done-line 0003 — with the field itself
  deliberately at `needs-you`: the last open item is bdo's, by design.
- **Doctrine:** v0.4.0, authoritative, unedited.

---

## 1. Done-line 0003, met clause by clause

- **Realness is admitted, not coded (I-8):** `node_real` admissions map a
  stage to its real node; latest wins; reverting to mock is a superseding
  admission. No realness literal exists in `loop/`.
- **The loop never auto-judges a real stage:** `pass_once` parks the atom
  naming the awaited node; the orchestrator senses `awaiting` pressure and
  schedules around it (D-2, D-10).
- **The summoned pen (`loop/node.py`):** verdict from the stage's terminal
  set only; writer must be the admitted node; a node may not judge an event
  it announced (D-2); idempotent by `(node, artifact_hash)` (I-2). A real
  accept advances next pass; a real reject parks with no suggested next
  event (D-4).
- **No regression:** atoms settled under mock receipts stay settled when
  realness is admitted — receipts are never retro-invalidated (D-5).
  Tested, and proven live (`settled: 2` throughout).
- **Live on the repo's field:** `value-gate.claude.v1` — a summoned session
  with an adversarial brief and its own context — read the doctrine,
  judged `atom.real-value-gate.v0`'s story for real, and accepted *with
  hesitations on the record* (the "summoned leaks mechanism" worry; the
  reflexivity of an AI authoring the story for its own gate). Its receipt
  is `rcp.e283e52d3fdc`. The atom advanced and now sits at
  `owner-stamp.bdo.v1`.

18/18 tests green (phase-1 six and orchestrator six untouched).

## 2. What is genuinely different now

Until this session every judgement in the system was a fixed string. The
L0 receipt on the log is the first **semantic sensor reading** (report
0004 §3): a separate agenda examined a story, checked whose appetite its
because-clause serves, verified the claim against the doctrine, and could
have said no. The flood-test cap (`human_queue_cap`) now protects a real
queue: `human_backlog: 1` currently means *one item waiting on bdo*, not
a mock's bookkeeping.

## 3. Open for bdo — the field is parked on you (D-4)

The owner stamp is yours alone now. To clear the queue:

```bash
python -m loop.node judge --atom atom.real-value-gate.v0 \
  --node owner-stamp.bdo.v1 --verdict accept \
  --reason "<your reason>"          # or reject_no_value / reject_wrong_value / amend
python -m loop.orchestrate          # mocks carry it the rest of the way
```

Or say the verdict in chat and the control session routes it verbatim
(D-3). After that, next stamps to choose from: the L0 second check going
real (`confirmed | missed`), the slow loop, or corpus-to-system ingestion
(report 0004 §4).

## 4. Not done, on purpose

L1/L2/confirm stay mocks (one node at a time, §9.3 — the stamp came along
only because the pipeline mandate orders it first). No slow loop, no
ingestion, no doctrine edit. The summoning is still hand-routed by the
control session; wiring it to hooks (§8) is its own later version.
