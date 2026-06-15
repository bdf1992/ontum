# Report 0064 — Anima's energy/tempo taste — energy-per-act folded from the log (done-line 0080)

## What landed

Done-line 0080 — anima's **energy/tempo** dimension, its first taste. bdo asked for the cheap, cool/dusk-fitting cut: a read-only fold over compute already on the log (`latency_ms`, `tokens` on receipts), zero new capture. Built, tested, opened as PR #147 on `claude/anima-energy-fold`.

- **`loop/energy.py`** — a pure read-only fold (the `loop.gaps`/`loop.temporal` grain, stdlib only). An *act* is any receipt carrying a numeric `latency_ms` (the beat); `tokens` is the yield. Renders **energy-per-act**: each act's beat and yield, aggregate pulse (count, total/mean/median latency) and **tempo** (tokens/sec over yielding acts only), grouped by mind and outcome, every measure citing the receipt ids it folds. Zero new capture.
- **§10 teeth — a `strain` fold:** energy spent without yield. *burned* acts (beat spent, outcome≠ok or no tokens) and *fallback* acts (`fallback_from` set: a second act's energy for one answer), with wasted latency reported. Tempo excludes burned acts, so a jam can never masquerade as throughput; an absent `tokens` stays absence (never a fabricated zero).
- **`tests/test_energy.py`** (16 cases): clean/burned/fallback separated; tempo excludes a burned giant and can't divide by zero; absent-tokens-is-not-zero; bool-is-not-latency; empty/missing log folds to no acts; and a controlled literal on the real committed log — qwen3 timeout `rcp.eacd7effeb7b` reads burned forever. Full suite green (762).

**The first taste (real, not a fixture):** over the repo's own log the fold finds the two inference acts from the day the gateway jammed (issues #95/#96): qwen3 timeout (182.1s, zero tokens, error) reads **burned**, the mistral retry reads **fallback**. 182.1s of the loop's 241.8s of thinking-time bought no meaning — and the fold says so. That strain is the first flavor to name the sauce by.

## needs-you

- **Name agenda [[anima]]'s converging arcs (your layer, not blocking the build).** PR #147 is merge-node-eligible only after an arc is confirmed; the fold serves the energy/metabolism arc, which has no name yet. The done-line's `> **Arc:**` line is honest-empty; the tie firms (and the SessionStart reminder fills) the moment you name it. That is the one decision that lands #147.

Scope held: did **not** re-derive heat/cool (anima's *rhythm* dimension, already sensed by `loop/temporal`); did **not** capture new timing (folded what's on the log, per the cheap-cut instruction); did **not** touch #142 (deadlocked, not this thread); did **not** edit `loop/CLAUDE.md`'s module list (it already omits the recent sibling folds — adding only this one is inconsistent, adding all three is §12 polish).

## End-state

`report` — done-line 0080 built, tested (suite green, 762), opened as PR #147; clean, awaiting one decision from bdo (name the energy arc) before the merge-node lands it.
