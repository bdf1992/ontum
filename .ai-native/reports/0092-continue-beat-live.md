# Report 0092 — The continue-beat — built, dogfooded, detached onto main (#242)

## What landed

**Done-line 0127 — the continue-beat** (PR #242 → main; supersedes the retired #236). bdo asked for an ambient trigger so that when he is here but AFK, a session keeps working without being re-prompted, stopping when it actually needs him and going silent the moment it escalates. The shape was confirmed through the `/ask` panel before any code: in-session `Stop`-hook beat now (it continues a *live* session — it cannot wake an exited one; the timed cloud-wake is a deferred layer); silence on needs-you / parked-at-stamp / explicit-escalate plus a ceiling; an empty backlog does **not** silence the patrol.

- `loop/patrol.py` — a pure `decide(state, session_id, gap, owner_present)` fold + a write-once `escalate` verb. Composes `loop.gaps.top_gap` and `loop.summon.owner_backlog` (imports, never re-derives — I-4). CONTINUE on self-serviceable work with no escalation; SILENT on escalate-marker / ceiling(12) / parked-at-stamp (gap absent **and** owner backlog non-empty). Marker is gitignored nag-state (`.ai-native/continue-beat.json`), never the truth log.
- `.claude/hooks/continue_beat.py` — the `Stop` hook beside `reflect_auto`, **fail-SAFE-to-STOP**: any error or malformed payload lets the session stop (opposite of the other beats' fail-open), so a bug can never trap an AFK session burning tokens.
- `tests/test_patrol.py` — §10 teeth: a constant decider fails (continue AND silent both reachable; ceiling, parked-at-stamp, new-session-reset, and the hook's fail-safe each pinned, two by subprocess). Full suite green.
- Backed by `atom.continue-beat.v0` + an **independent** value-gate receipt `rcp.04a1f8626170` (D-2): a separate branded agent read the work, ran the tests itself, accepted.

**Also this session:** requisitioned a merge-node — it landed **#232** (landing-contract intent rule, `epic.owner-harness`, `rcp.merge.232`) and correctly skipped the rest (red CI / draft / conflicting / unconfirmed-arc), dry-running each first.

**Conflict named (not silently resolved):** done-line 0127's prose names the arc as `epic.landing-throughput-response` (the principle's origin). That epic is **not committed/confirmed**, so the atom serves `epic.owner-harness` — confirmed, and the precise fit. The principle lineage is real; the committed, confirmed arc is owner-harness.

**Detach (#236 → #242):** the first PR (#236) was stacked on #226 only as an artifact of the worktree hook-path workaround (bug #235). Since the continue-beat serves owner-harness, not landing-throughput, I reconstructed it byte-identical on a branch off `origin/main` (atom hash `036bc1de…` verified equal, so the value-gate receipt stays valid), opened #242 → main (MERGEABLE/CLEAN), and retired #236.

## needs-you

- **Nothing to confirm for this piece.** `epic.owner-harness` is already confirmed (adm.728a87a9ca48); #242 is merge-node-eligible. A merge-node is being requisitioned to land it.
- **Harness bug #235** (cwd-relative hook paths break worktree sessions) — the actual fix is already in flight as **PR #240** (`claude/hook-path-rooting`), rooting hook paths at `$CLAUDE_PROJECT_DIR`. Once #240 lands, this whole detach dance is no longer forced for future worktree builds.
- **Two named next increments** (each its own done-line, per 0127's out-of-scope): (1) the **timed cloud-wake layer** — a scheduled routine that wakes a *fresh* session, the only thing that covers genuine AFK gaps a `Stop` hook cannot (it never resurrects an exited process); (2) graduate the beat **ceiling** from a code constant (12) to an **admitted dial** (`--by bdo`, the setpoint shape).
- **Note:** the beat activates only in a **new** session whose `settings.json` carries the wiring — i.e., after #242 lands to main and a fresh session opens. It is not firing in this session.

## End-state

`report` — the continue-beat is built, tested green, dogfooded (atom + independent value-gate `rcp.04a1f8626170`), and open as **PR #242 → main** (MERGEABLE/CLEAN, merge-node-eligible under the confirmed `epic.owner-harness`), with the stacked #236 retired in its favour. The in-session layer of bdo's "I don't need to prompt and prompt" is done and on a clean path to main; the timed AFK-wake layer and the ceiling-as-dial are named for next.
