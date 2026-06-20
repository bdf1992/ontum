# Report 0100 — epic.diagram wave 1, and the friction that named the registration-and-repair gateway activity

## What landed

On the record this session:

- **epic.diagram** — new composing arc (`.ai-native/epics/epic.diagram.json`), **CONFIRMED by bdo** (adm.399f90e086fd). Ports the SubProtocol `diagram-author` skill into ontum, turned up: the diagrammer built *as* the membrane architecture (generative pole -> gate-with-teeth -> deterministic render -> truth).
- **done-line 0139** (`0139-diagram-floor-and-gate.md`, frozen) — the wave-1 bar.
- **Wave 1 — built, green, independently verified** — new `diagrams/` module:
  - `diagrams/CLAUDE.md` (module land + rules: stdlib, explicit-position, no double-build, canon governs).
  - `diagrams/canon.md` — the named SME: Moody's *Physics of Notations* + graph-drawing aesthetics (Purchase) + C4, each principle mapped to a gate refusal with a non-example.
  - `diagrams/compose.py` — deterministic explicit-position SVG renderer, ported (CRLF-determinism bug fixed by writing bytes not write_text).
  - `diagrams/qa.py` — the checker **promoted to a refusing gate** (exit 2 + cited principle on stderr, fail-open on its own error).
  - `diagrams/examples/` — honest pipeline state-machine diagram (+ SVG) and a dishonest orphan-node variant.
  - `tests/test_diagram.py` — 16 tests; the §10 pair holds (honest passes exit 0; dishonest refused exit 2 citing `[graph-drawing: no orphans]`).
  - `.gitattributes` — pinned `diagrams/examples/*.svg -text` (done-line 0060 precedent for byte-deterministic artifacts).
- **session-gateway.proposal.md §14** — "The registration-and-repair gateway activity": the session's root-cause fix, PROPOSED. Register (claim binding) -> alert-on-wrong-env -> investigate+repair (heal/sync/gardener), MAPE-K at the session seam; the **bounded-repair fence** is bdo's open decision.

Design captured (some chat-only, see needs-you): the membrane/interstitium architecture (surfaces vs spaces, ingress/egress, internal/external, the generative pole); the diagram-organ vision corrected by an independent three-reviewer repo pass — data-visualizer is the WRONG SME (it's the charts canon) -> a *named architecture canon*; auto-layout REFUSED (taste + diff-stability) -> tier-declaration grid-snap only; no double-build -> `diagrams/` is a sibling of `causality/`, projections fold INTO `term_economy.py`.

## needs-you

- **The clean land.** Everything above is **uncommitted on the stranded primary viewport** (branch `claude/terminal-pull-gateway`, a closed arc). It needs one clean operation: a **fresh workbench off main + an independent merge-node** (this session authored it; D-2 forbids self-land). The pile: `diagrams/`, `tests/test_diagram.py`, `epic.diagram.json`, `0139-...md`, `.gitattributes`, `session-gateway.proposal.md`. Each `diagrams/` piece needs its atom + value-gate receipt (off-log gate) at land time. The arc is already confirmed, so the merge-node may land once the PR is up.
- **The bounded-repair fence (§14).** When you want the gateway activity built, your one stamp draws the fence (auto-repair the reversible, escalate the work-bearing — the disposer shape). Until then §14 is proposed-only.
- **Viewport stranded.** It auto-restores to `main` next session *once this pile is committed/pushed*; it stays stranded while the work is uncommitted. The land resolves it.
- **architecture.md was never written** — the early cwd/hook bug (#235) blocked the Write; it lives only in this chat transcript. Re-author on request, or let wave 3's projection-from-truth regenerate it from the repo.

## End-state

`report` — epic.diagram confirmed; wave 1 built, green, verified — but **unlanded**, sitting on a stranded viewport. Next session: take a clean workbench off main, land the pile as the confirmed arc's first PR via an independent merge-node (which also restores the viewport). The session's own friction is diagnosed and farmed as session-gateway §14 — the registration-and-repair gateway activity, awaiting bdo's bounded-repair fence.
