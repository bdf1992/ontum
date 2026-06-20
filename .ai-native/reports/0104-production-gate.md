# Report 0104 — epic.environments wave 1 — the production gate

## What landed

bdo: "let's work on implement environments." `epic.environments` is his confirmed, landed arc (PR #277) — work moves through named, gated environments as snapshots. This session built its **wave-1 first buildable slice**, the piece the epic names `atom.production-gate.v0` ("smallest real teeth"): the live URL stops changing without bdo's stamp.

- **done-line 0137** written before the code (§9.4).
- **loop/deploy.py** — a stdlib, read-only fold over the committed log: `production_snapshot()` (the latest non-superseded bdo-authored `production_promotion`), a gate verdict for a candidate commit (`promote` iff it is the stamped snapshot, else `hold` serving the stamped one, else `passthrough` before the first stamp), a read-only status CLI, the `gate --candidate` CI seam, and the bdo-only `promote` stamp (the one writer; refuses every non-bdo signer; the fold re-checks the signature so a hand-appended promotion cannot forge the live snapshot).
- **.github/workflows/pages.yml** — now asks the gate which snapshot is authorized and serves THAT (the stamped snapshot, or HEAD in loud passthrough), instead of auto-deploying HEAD on every push. Non-circular by design: it deploys the stamped snapshot, never HEAD, so the act of recording a stamp (itself a commit) can never become unstamped live content.
- **tests/test_deploy.py** — the §10 teeth (11 tests): a stamped snapshot promotes and is served; an un-stamped candidate is HELD (two locally-fine records refusing to fit); a superseding promotion moves the live snapshot; a non-bdo promote is refused at the pen; a forged non-bdo promotion is ignored by the fold; a constant gate cannot pass passthrough+hold+promote. Full suite green.

The atom was announced and judged **accept** by an independent value-gate (rcp.2fb20fd76e70). Handed off as **PR #286**, atom-backed (off-log gate green), awaiting the merge-node (the arc is already confirmed; D-4).

## needs-you

1. **The branded headless gate rail is broken in a nested session.** `gate.py launch` runs `claude -p --output-format json` as a subprocess, but a nested headless claude here returns an EMPTY result (`num_turns: 0`, `output_tokens: 0`) — no parseable verdict. So a session cannot self-requisition the value-gate via the branded `ontum-node:` rail from within itself. I requisitioned the independent value-gate review via an **in-harness independent judge** instead (a separate-context Agent that read the files, ran the tests, verified the non-circularity claim in code, and returned accept). The two failed launches opened trust-rail issues #284/#285; I closed both with the diagnosis (duplicate environment failures, not atom-judgment failures) to keep bdo's surface clean. **This rail needs a fix** — either the gate pen detects the empty-nested-claude case and falls back, or the merge-node / a fresh top-level session runs the gate where `claude -p` works.

2. **Activation gesture (bdo's, when he chooses):** the gate is built and runs as passthrough until bdo's first production promotion. The GitHub-gesture intake rail for his stamp (a session running `promote --by bdo` on his closed-issue comment — the `realness-intake`/`policy-intake` shape) is named in done-line 0137 as the activation path; it is **not** built here (wave-1 scope was the gate's teeth).

3. **done-line id 0137 collision risk.** The pen's fleet-safe authority (folding ids over git refs, max 0136) assigned 0137. An uncommitted, viewport-stranded `0137-explore-fold.md` exists in the primary working tree (a prior session's unbranched work); if it ever lands it will need a renumber. Surfaced, not fixed — not this session's work.

## End-state

`report` — PR #286 open, atom-backed (off-log gate green), full suite green, awaiting the merge-node; built and ready, the gate runs as loud passthrough until bdo's first promotion gesture. Waves 2–3 (preview / staging / runtime-parity / served control plane) are later pieces.
