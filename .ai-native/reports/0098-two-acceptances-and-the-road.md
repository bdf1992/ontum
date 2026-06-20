# Report 0098 — Two acceptances: the D-2 reframe and the work-closes-in-the-wild road

﻿## What landed

bdo's thread reframed D-2 and asked to both make the prose edit and fix the landing plane ? practicing what we preach. Both forged and driven to the independent stage; one PR (#273), one coherent idea.

- **The rule (prose, phrasing-clean):** D-2 reframed into *two acceptances* ? earn your own first (the case, the conviction, the slop filter); you still cannot cast the deciding acceptance (independent reader, owner last stop); and when no independent judge exists, **forge one within policy** (toward the second set of eyes, never around them, never one you control). Reworded across `ai-native-loop-substrate.md` D-2, `loop/CLAUDE.md`, `CONTRIBUTING.md`, `AGENTS.md`. No code branches on the text (node.py/merge-node already enforce no-self-judge); proven prose-only and marked through the phrasing door (`adm.7cd2a14688bd`).

- **The road (code, atom-backed ? done-line 0133):** `orchestrate.next_action` now settles an atom whose work the independent merge-node landed ? the merge-node lands a PR it did NOT author, so its `landed` receipt IS the deciding acceptance. Keyed on the D-13 join (`digest.atoms_on_main`) AND a SEED event for THIS hash. Drains the inflight clog (landed-but-abandoned atoms past the value-gate) so the cap stops cooling new births. Threaded through `sense`/`control` (join computed once). ?10 teeth: an un-landed in-place edit (no seed for the new hash) refuses to ride its sibling's landing ? `tests/test_orchestrate.py::SettleOnMainTest`, full suite green.

- **Dogfooded under the new rule:** earned my own acceptance (suite + ?10 tests), then requisitioned an independent one ? the spawn guard forced the branded rail, so `ontum-node:value-gate.claude.v1` judged `atom.work-closes-in-the-wild.v0` and accepted (`rcp.ae25ad533fe4`, D-2). Prose phrasing-marked, code atom-backed; the PR is fully accounted on the log.

- **Diagnosis recorded:** the clog cause is two terminals that never reconciled ? the git-merge (work on main) vs the pipeline terminal (`value_confirmed`). The off-log gate requires only the value-gate, so sessions dogfood to that minimum and abandon; the road closes the gap forward (the pre-D-13 merges stay lossy history).

## needs-you

- **Confirm `epic.landing-throughput-response`** (`loop.node confirm-arc --epic epic.landing-throughput-response --by bdo`). The road (and PR #273) land under it; the merge-node executes your confirmation. Your arc to steer ? not a chore routed to you.
- Process note (not yours to fix): the fleet id collision (`0132` taken on a sibling branch ? re-minted `0133`) and the shared-worktree branch race recurred this session; both were handled, surfaced here as a recurring friction.

## End-state

`report` ? both halves on PR #273 (worktree-two-acceptances), suite green, dogfooded D-2-faithfully; awaits bdo's `confirm-arc` on epic.landing-throughput-response for the merge-node to land.
