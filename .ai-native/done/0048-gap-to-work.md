# Done-line 0048 — Gap-to-work: the loop's own gaps become the next session's work

@
Written before code, per §9.4. When this line is met, stop.

> **Done when:** the loop converts the gaps it already senses into the work a
> session is handed, ambiently. `loop/gaps.py` is a pure read-only fold
> (stdlib only, no subprocess, no network, no write) that enumerates the open
> gaps derivable from records already on disk and orders them by one fixed
> pressure ranking: **mock-stage** (a PIPELINE stage no `node_real` admission
> has replaced — the same fold the shame beat reads), then **parked-piece**
> (an atom a gate refused, holding, with its held-by receipt as the why), then
> **surface-drift** (acts not yet reflected to a registered surface), then
> **idle-organ** and **dormant-organ** (the census verdicts wired·idle and
> dormant). Every gap carries kind, subject, why, and the one concrete next
> move; the ranking computes lazily in priority order, so the cheap log folds
> answer before the census walks the tree. `python -m loop.gaps` renders the
> whole gap backlog and ends done|report; `python -m loop.summon --hook` hands
> the single highest-pressure gap to every session that blinks in — the idle
> default becomes "work the backlog the harness generated", never "wait for
> direction". Tests pin the contract: the priority ranking is deterministic
> and the §10 case holds (two kinds present and the higher-pressure kind wins
> the hook line — a locally-fine lower gap refuses to lead); each kind renders
> with its move; a clean field prints no gap line in hook mode; the hook stays
> fail-open on a broken root. Full suite green.

## Out of scope, named (its own next lines)

- **Gap-to-atom minting** — a gap auto-proposing itself as an atom into the
  pipeline. Today the session is the converter; the fold only hands it the
  work. The minting rail (and who signs it) is its own line.
- **Git-derived gaps** — stranded worktrees and branches are the garden's land
  (subprocess, git); this fold stays pure over the records.
- **Any write.** gaps.py renders; every move it names belongs to an existing
  pen (node, reflect, the garden). The census cut stays bdo's (D-4).
@
