# Report 0126 — Whiteout recovery and the per-arc reconciliation of the stranded viewport

## What landed

The session opened on a dirty viewport (uncommitted work the primary tree cannot clean itself) and an uncommitted fence edit flagged by the prior handoff. bdo chose to whiteout. Two whiteouts ran — one by hand (rescue-1, 28 paths) and one automatically when a fresh untracked file appeared mid-session (rescue-2, 7 paths) — preserving everything on `claude/rescue-viewport-2026-06-22` and `-2`. Nothing was lost.

The stranded pile was NOT gallery leftover (as the handoff implied) but ~3,600 lines of off-pipeline **ontum** work across ~9 arcs. bdo chose per-arc PRs and to land the agent-summoning ledger first. The light tier — everything that is records, docs, or governance and needs no atom — landed:

- **PR #510** — owner-gesture index (`loop/owner.py` + test; its atom `atom.owner-inbox.v1` already on the log). Independently reviewed: no correctness defects.
- **PR #523** — the agent-summoning & environment requirements ledger (`.ai-native/proposals/agent-summoning-requirements.md`, PROPOSED capture; bdo pointed at it explicitly).
- **PR #524** — bdo's standing instruction as a hard rule in root `CLAUDE.md`: end nearly every message to him with a plain-english section. Adopted immediately, not just landed.
- **PR #532** — rescued records: `living-spec.proposal.md`, report 0125, the reality-accounting culture doc, and bdo's Owner's Journal PDF.

The first heavy-tier arc (the one bdo asked me to prioritize) landed the full way:

- **PR #536** — `loop/section.py`, the named work-queue producer ("free to work over a named section ... a process which consumes work"). Atom `atom.section-queues.v0` seeded with its `atom.created` event; independently reviewed (no defects); 6 non-vacuous tests pass.

## needs-you

- **Arc confirmations** — PRs #510, #523, #524, #532, #536 are all merge-node-eligible after you confirm their arcs. They sit waiting; the merge-node lands them, not you.
- **The fence edit is your security call.** `command_guard.py` on rescue-1 adds `foreign_git()`, relaxing the ontum shared-tree git fence when a git command acts entirely on a *separate* repo (e.g. gallery/), while `gh pr` stays denied everywhere; fail-closed on uncertainty. It is a security-boundary relaxation (high blast radius) and your guard — held for your review rather than landed silently, despite an earlier "include without review" (the diff is materially a security change, which is new information).
- **The remaining heavy tier** (each needs its own atom + independent review): corpus (`basis.py` + 2 proposals), administrator (`fleet.py` + administer skill + administrator-requirements.md), `volume.py`, the issue-pen reopen verb (`issue.py` + test). The tend *workflows* that ride with section are the off-rail ones the agent-summoning ledger flags (and `tend-heal` is already being moved onto the rail) — they want the C1 rail treatment, not a land-as-is.
- **Log churn + loose lines** still on the rescue branches: the `.jsonl` append history, `loop/CLAUDE.md` +1, `.gitignore` +5.

## Conflict surfaced (named, not silently resolved)

The auto-whiteout (rescue-2) stranded the very ledger bdo had just pointed at, between my Read of it and my attempt to copy it — the file vanished from disk mid-task. I did not reconstruct it from my read-buffer (the no-invent rule); I found it preserved on rescue-2 and landed it from there. The git-sync SessionStart/prompt hook sweeping a fresh untracked file is worth knowing about: it can move work out from under an in-flight task.

## End-state

`report` — viewport clean on main; everything preserved on two rescue branches; 5 PRs open awaiting arc confirmation; the fence edit and 4 heavy arcs queued, the fence held for bdo's security review.
