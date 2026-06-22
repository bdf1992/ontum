# Report 0124 — Administering the issue/PR board: a governed cleanup pass

**Session:** board administration. bdo pointed at the GitHub board (18 issues,
17 PRs) and asked for help "administering and operating the work required by
these items," then — the load-bearing instruction — to **"sequence the work and
administrate over it."** This session acted as the administrator: it triaged the
whole board against the log (not by title), did the session-doable work, served
bdo only the genuine forks, and left the rest as an ordered backlog.

## End-state — what changed

**Landed on main** (via the independent merge-node, arcs already confirmed):
- `#383` placement fold (`rcp.merge.383`), `#343` gate policy facts (`rcp.merge.343`).
- `#440` two stranded blueprint proposals (`rcp.merge.440`) — `change-management.proposal.md`
  (the file `CLAUDE.md` already cited: **#348 ghost citation resolved**) and
  `platform-brokerage.proposal.md` (bdo's platform blueprint), extracted from the
  stale `#354` branch and re-landed clean. Pure prose, phrasing-clean.
- `#441` the **general-issue pen (#412)** (`rcp.merge.441`, under `epic.substrate`):
  `.claude/skills/issue/issue.py` (`close`/`comment`, each recording log provenance)
  + the **prompt-parity hole closed** — `fence/policy.py`'s `gh-issue-mutate` rule
  flipped `decision="prompt"` (a silent no-op on the Claude surface — that was the
  hole) -> `"forbidden"`, so `command_guard` now routes raw `gh issue` mutations to
  the pen. Backed by `atom.issue-pen.v0` with an **independent value-gate accept**
  (`rcp.7735ab13f126`); behavioral fence test has teeth (1325-test suite green).

**Issues closed** (9; the cruft 8 through the new pen, dogfooded, each with a
reason-comment + log provenance): `#415` whiteout (landed #419), `#345` authorship
(landed #376), `#290` stale digest, `#325`/`#390`/`#391`/`#393`/`#396` dead
headless runs (no verdict ever landed — the #411 hang), and `#412` itself
(resolved by the pen it asked for).

**Retired:** `#354` (superseded by #430; landing it would have reverted #430).

**Board:** issues 18 -> 9, PRs 17 -> 14 (a concurrent session also landed the
records door `#443` and opened `#446`).

## The keystone finding — the pipeline is clogged

`orchestrate --status`: **inflight 57 against a cap of 8.** 57 atoms are stuck at
`value_accepted -> derive:value.accepted` — the ambient loop cannot advance them,
and no new atom can be born. This is the digest's `atom.guaranteed-review-queue.v0`
divergence (the contested settle-on-landing -> review-queue rework, done-lines
0133/0150/0154). Consequence: **real-code work cannot flow** — only prose lands
(via the phrasing door / now the records door), which is how everything this
session landed. Individual pieces still land via the manual independent-judge path
(that is how the issue pen landed), but the clog gates the consequence-graph merge
and any ambient progress. **It is the deepest item on the board.** It was not
cowboyed here — it is contested substrate and belongs to a focused piece.

## Conflicts named (section 9)

1. **I mis-framed an owner question.** I told bdo "epic.consequence-graph-response
   is NOT confirmed" — inferred from `loop.node arcs` (which lists only arcs whose
   epic *file* is landed), missing the confirm admission `adm.6a176eb59681` on the
   log. The arc *was* confirmed (file-not-landed: the epic-introducing-PR case). I
   caught it before acting, surfaced the correction, and re-asked on the true state.
   bdo: **"merge with the root for a stronger trunk"** — keep the arc, consolidate
   into the trunk; the merge is clog-gated (above).
2. **Offloading vs governance.** The board's cruft was closeable only via raw
   `gh issue close` — the ungoverned hole bdo has flagged twice. Rather than
   raw-close (expedient, offloads the hole) or punt the cleanup (offloads the work),
   bdo chose **build the pen first**: the rule that forced the choice *was* the bug,
   so the fix was to build the governed door (#412) and close the cruft through it.

## needs-you — the genuine owner items left

- **The clog** (`atom.guaranteed-review-queue.v0`): the keystone. Its fix is
  contested (settle-on-landing retirement). A focused piece, your steer on shape.
- **Blueprints** `#416`/`#397`/`#387`/`#153` (draft): your steering surface —
  land-as-doc or keep open. Not blocking anything.
- **Owner-asks** `#247` (stamp portability — law landed, mechanism = #245), `#245`
  (env parity for web/mobile pens), `#355` (landing friction — partly chipped:
  phrasing + records doors now cover prose/reports), `#344` (`--training` tag),
  `#433`/`#434` (reflect-drift duplicates — reflect is double-opening; a reflect
  dedup is its own small fix).

## Sequenced backlog (the administration, ordered)

1. **Land the 3 reports** `#427`/`#417`/`#292` — now easy: `#427`/`#417` are
   records-only (the records door #443 exempts them); `#292` carries a log change
   (needs the manual path).
2. **Rebuild `#389`** — carries the `#411` headless-gate stdin fix (a real stranded
   bug; the gate rail still hangs on main without it).
3. **Rebuild gate PRs** `#358`/`#338`; **retire** `#324` (subset of #338) and `#308`
   (stale rescue — payload mostly on main).
4. **The clog fix** (keystone) -> then **consequence-graph merge** (`#388`, clog-gated).
5. **`#431` receipt discrepancy** — it reached main with no `rcp.merge.431` (landed
   off-pen); the per-atom<->per-PR join should account for it.
6. **Rescue-branch churn** — 6 `claude/rescue-viewport-*` branches today; the
   whiteout cycle is accruing cleanup debt (the deeper #415 fix).

_The board is yours to read (D-4); this pass shrank it and named what remains._
