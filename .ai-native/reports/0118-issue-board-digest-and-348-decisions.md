# Report 0118 — Issue-board digest, the #348 blueprint decisions, and the bench-sequencing pattern

## What landed

- **Issue-board triage (26 → 8).** The GitHub board was almost all auto-generated *mirrors* of log state (`loop/reflect.py` / `loop/owner_asks.py`), not independent work — their own bodies say "acting here does nothing." Validated each against the live log and closed **21** with cited evidence — never blind-dismissed (bdo's correction: *earn* the closure, do not dismiss). Closed: 14 ancient owner-ask mirrors (reports 0071–0109, every item a pointer to a landed PR or a confirmed arc), the dead divergence #293 (digest: 0 divergences), the #289/#307 duplicate stamp pair (atom.mark-label.v0 landed via merged #244), gate-run #326 (value-gate accept on the log), #294 (two micro-stamps declined moot), #296/#297 (anthology bless reaffirmed), and 3 recent owner-ask mirrors #378/#379/#380 (epic.model-free-mode-response CONFIRMED; #351/#372/#339 all MERGED). The remaining 8 are all signal.

- **#348 resolved in substance — the blueprint-first decisions.** bdo's "all yes" (2026-06-20): CTA-3 (blueprint-before-build) and #247 (portable-owner-stamp) minted as **hard rules** in `CLAUDE.md` (this commit); CTA-2 (blueprint = a first-class, digest-visible record) graduates to `epic.change-management`; #294 micro-stamps declined; anthology `anthology.self-governing-loop` reaffirmed; CTA-7 (consequence-policy primitive) endorsed as its own arc. Recorded in the DECISIONS block of `change-management.proposal.md`.

- **The bench-sequencing pattern (bdo: "define a pattern to check against").** A deterministic `grant(branch, session)` fold over claim records — precedence `bdo > landing-ready > FIFO`, plus a **yield gate** that refuses any viewport switch which would strand uncommitted work. Born from a live deadlock this session (below). Homes as CTA-12's ordering half and a consequence-policy. Default tiebreak taken: landing-ready-first.

## needs-you

Nothing blocking. Deferred go-aheads — yours when you want them, none gate other work: name the *shared-gateway* arc · go for *organ 2* (the runtime witness) · *send* the sealed `exports/model-free-mode` envoy package to a 2nd model family or keep it in-house · stand up the *mesh-over-duration* supervisory loop on `observe.py`. Tiebreak: I took **landing-ready-first** unless you correct it.

## Conflict named (the live failure that proves the bundle)

The workstation-write-fence (done-line 0147, #346/#365) vs the **single shared viewport**: mid-session the viewport was switched off my active `platform-brokerage-blueprint` claim onto a parallel `land-authorship-in-code` build, stranding my edits — and the fence then blocked re-homing into a side worktree (the session's Bash cwd resets to the viewport after every command, so the Write/Edit tools cannot reach a worktree; only pens run through Bash can). That is **CTA-12 / "local mark, global bite," proven live** — the exact deadlock the bench-sequencing pattern is designed to refuse. This report and the #348 edits land only because the viewport later freed to `main` and the branch became claimable.

## End-state

`report` — board 26→8 (all signal); #348 decisions captured and landing via PR #354; the bench-sequencing pattern defined and captured; #345 landing live via PR #376; nothing blocking bdo.
