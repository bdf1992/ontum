# Report 0058 — landing handoff: the consolidated pile, for a fresh session

A long session built six things and the landing piled up; bdo asked to
hand the pile to a fresh session with un-maxed context. This report is
that handoff — a cold-start landing checklist. Everything below is
built, tested, and committed somewhere; what remains is *landing* under
an arc, which is bdo's gesture, plus clearing one id collision.

## What landed (durably, this session)

- Report [0049](0049-envoy-response-comes-home.md) + [0050](0050-inbound-seam-built.md):
  the envoy QA package, bdo's dependency-rule lift + repo-wide audit, the
  inbound envoy seam, and Whiteout's design/build narrative.

## The pile (four pieces, each built+verified, all waiting on an arc)

The merge-node only lands **confirmed-arc** PRs, and none of these is
under an epic. bdo's lean (his to confirm): file all four under
`epic.owner-harness` so his standing confirmation lands them; or he
names a fresh small arc.

1. **PR #111** (open on GitHub) — inbound envoy seam + dep-rule lift +
   the routed qa-metabolism review (6 proposed atoms under
   `epic.qa-metabolism-response`). Backed by `atom.inbound-envoy-seam.v0`
   (value-accepted, `rcp.1ead8915a9bd`). Needs: an arc → merge-node lands.

2. **pen fleet-safe allocator** — branch `claude/pen-fleet-safe-id`. The
   records pen now claims a *fleet-safe* id (delegates to `placement.py`,
   fail-open to local), closing the cross-branch renumber saga this
   session kept hitting. **BLOCKER: its done-line `0062` collides
   fleet-wide** with bdo's *authorized, frozen* `0062-governed-inference-plane`
   (the /goal session). bdo's stays; **this branch's 0062 yields** —
   renumber it to a fleet-safe id (`placement.py next .ai-native/done`),
   updating the references in `loop/pen.py` (the `next_id` docstring),
   `tests/test_pen.py`, and the done-line file (recreate, since done/ is
   frozen). Then atom-back + arc.

3. **Whiteout** — worktree branch `worktree-agent-a5921151c4f7ebe48`
   (worktree at `.claude/worktrees/agent-a5921151c4f7ebe48`), commit
   `dd490bd`. The `loop.pen whiteout` correction mode: marked, recoverable
   underneath, refuses a *consumed* target (stage-aware off the live
   PIPELINE). done-line `0064`. Built by an orchestrated build node,
   adversarially verified (erasure + frozen-contract boundaries
   unbreakable; one critical consumed-bypass found and fixed), suite green
   (610 at fix time). Needs: atom-back + arc + land.

4. **spawn-rail floor** — branch `claude/spawn-rail-floor`, commit
   `bef87c7`. Closes the gap this very session exposed: the rail let an
   unbranded *plain helper* run untraced (three Whiteout nodes did). Now
   every Agent/headless-claude spawn must declare `ontum-node:<id>`
   (judging seat, prompt-pinned + rung-checked) or `ontum-helper:<name>`
   (recorded build work, traced, not rung-gated); bare unbranded refuses;
   fail-open so a rail bug never blocks the fleet. Suite 637 green. **Its
   done-line collided at 0069** — re-mint fleet-safe; its bar is in the
   needs-you below. **Land this FIRST** — every future orchestration
   depends on it for provenance.

## The landing recipe (per PR, the non-bypass path)

- **Atom-back it:** `pr.py create` refuses a PR with no atom carrying a
  *real* (non-mock) gate receipt (the atom-invariant). For each piece
  without one (pen-fix, Whiteout, spawn-rail), create `atom.<name>.v0`,
  let `orchestrate` birth it to the value gate, then have an **independent
  branded judge** value-judge it — *now branded* `ontum-node:value-gate.claude.v1`
  (the floor in piece 4 requires it; no one signs their own line, D-4).
- **Fleet-safe ids always:** the done/report id space is hot-contended
  across many sibling branches; use `placement.py next <dir>` and expect
  to renumber. (Once piece 2 lands, the pen does this for you.)
- **One arc → merge-node:** bdo confirms the arc; the merge-node (a fresh
  session that did not author the PRs) lands each via `pr.py land`.

## needs-you

- **bdo: name the arc** for the four pieces (lean: `epic.owner-harness`).
  One confirmation lands the pile.
- **bdo: the governed inference plane** (built by the /goal session,
  report 0054) is **inert until you register its minds** — `loop.minds`
  / `route` / `policy` are all `--by bdo` (config is governance, D-4). No
  session can sign it. Surfaced here plainly: **I did not push these to
  the GitHub mirror** — that needs your one-time rule enable
  (`loop.reflect rule --kind owner-ask-backlog --surface github-issues
  --on --by bdo`). Said plainly per the owner-ask floor, not parked
  invisibly.
- **Do NOT touch the sibling WIP on the viewport:** `loop/reflect.py` +
  `0063-owner-ask-discharge.md` are another session's live, uncommitted
  build (the owner-ask *discharge* feature — a cousin of Whiteout). It
  blocks the viewport fast-forward; leave it for its owner.
- **The spawn-rail done-line bar** (re-mint fleet-safe): *the
  `spawn_guard` PreToolUse hook refuses (exit 2) an unbranded `Agent` or
  headless-`claude` spawn; every spawn declares `ontum-node:<id>`
  (prompt-pinned + rung-checked) or `ontum-helper:<name>` (recorded, not
  rung-gated); both leave true provenance; the refusal names both brands;
  fail-open on the rail's own error; proven by test that a bare
  general-purpose spawn now refuses to fit (§10).*

## End-state

`report` — six pieces built; two recorded as landed (reports 0049/0050);
four committed and waiting on bdo's one arc gesture (lean owner-harness)
plus the pen-fix's 0062 renumber and a fleet-safe re-mint of the
spawn-rail done-line. The viewport carries a sibling's WIP that is not
ours to move. Nothing was pushed past the branches named above; no arc
was confirmed; the inference-plane mind registration and the mirror
enable remain bdo's alone.
