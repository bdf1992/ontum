# Proposal — the owner meeting: a prepared, time-boxed 30-minute session, not a pile of issues

**Status:** PROPOSED (bdo to steer). Blueprint-first per the hard rule;
no build past the agreed deterministic prep until the meeting shape (the
"link") is stamped.

**Purpose (bdo, 2026-06-22):** *"I of course need a digest over these owner
asks, at most a 30 minutes daily meeting."* Refined the same day to the
meeting's true shape: *"an active 30-minute session over a prepared meeting
that I get — a meeting link I hand to an agent, and they have 30 minutes with
me"* — plus the ranked prep below. The deliverable is **not a document he
reads**; it is a **live, time-boxed meeting** an agent runs *for* him, where
the ranked owner-asks are the prepared agenda and his decisions are taken in
real time.

## Root causes (bdo: "find root causes too") — evidence-backed

The 14 standing `[owner-ask]` issues are the visible tip. The full census
(`gh issue list --state all`) shows **each of 6 reports opened as a brand-new
GitHub issue NINE times** — e.g. report `0114` → issues #454, #462, #479,
#490, #501, #511, #512, #525, #539. The group id is *stable*
(`ask.<hash(report_id)>`), so the dedup should have caught every repeat. It
didn't. Three causes, compounding:

- **RC1 — the dedup ack is branch-local, not global.** `owner_ask_drift`
  decides "already opened?" purely from the local-log reflection record
  (`(g["id"], "open") not in seen`). That ack is written to the *session's*
  working-tree log and only becomes visible to other sessions once its PR
  **lands on main**. Cloud couriers and stranded worktrees never land their
  log, so their ack never publishes — every subsequent session folds an
  ack-less main and believes nothing was opened. (Same family as the
  stranded-viewport and the "22 unadmitted landings": state written to an
  off-main log other sessions can't see.)

- **RC2 — the open is not idempotent against GitHub.** `_gh_open`
  (`.claude/skills/reflect/reflect.py`) is a **blind `gh issue create`** — it
  never searches the surface for an existing issue carrying the group id. So a
  missing ack (RC1) *always* mints a NEW duplicate issue instead of
  re-discovering the existing one. Nine sessions × blind-create = nine issues.
  Contrast `digest_drift`, built to dodge exactly this: one perennial issue,
  content-hash keyed, **edited in place** (done-line 0166).

- **RC3 — the grain is a pile, not a meeting.** One-issue-per-report is the
  wrong unit. It contradicts the standing hard rule (*bdo's only surfaces are
  arc-confirmation and the daily arc digest*) and the one-gateway directive,
  and it multiplies RC2 (every report is a fresh create-surface). A pile is the
  opposite of a 30-minute meeting.

**Why the meeting shape fixes the root, not the symptom:** a *single perennial
prepared surface* that finds itself by a **GitHub-side marker** (not the local
ack) and **edits in place** is structurally immune to RC1+RC2 — a missing ack
re-edits the same surface instead of minting a duplicate. The hardening
requirement this exposes: the perennial finder must key off the surface, not
only the log (digest_drift today still reads `opened` from the local ack —
same latent hole, lucky so far).

## The full shape (the meeting)

```
  reports/*.md ──fold──▶ owner_ask_groups ──rank──▶ budget cut (~30 min)
   (the asks)            (deduped by report)        (the thing he said)
                                                          │
                                                          ▼
                                              PREPARED AGENDA  (deterministic)
                                                          │
                                       ┌──────────────────┼───────────────┐
                                       ▼                  ▼               ▼
                                 a MEETING LINK   ──▶  an AGENT  ──▶  30 ACTIVE MIN
                                 (bdo opens)        (has the agenda)  (his gestures,
                                                                       recorded live)
                                                          │
                                                          ▼
                                          discharges / confirms / defers on the LOG
```

- **The prep (deterministic, agreed).** A pure fold ranks the owner-asks
  (freshness + unresolved + item-count) and applies the **budget**: ~3 min/ask
  → ~10 above the fold as *today's agenda*, the rest a deferred count. Each ask
  shaped as a Taster's-Clause read (organized, the pick named, the riskiest
  flagged — D-14). This is "the thing you said," and every meeting variant
  needs it.
- **The link (the open fork).** What bdo opens to enter the live session.
  Local-first ontum constrains this — candidates: a served localhost meeting
  page (`loop.web` extended, the served-inbox horizon), a resumable agent
  session he joins (`continue-probe` rail), or a scheduled cloud agent. This is
  the load-bearing unknown and is **his to steer** (CTA-2).
- **The agent (the 30 active minutes).** A summoned meeting-node holds the
  prepared agenda and paces it to fit 30 minutes — walks each ask, takes his
  decision, and records it. Time-boxed by construction.
- **The output (recorded gestures).** Each decision lands as a real record —
  a `reflect discharge-owner-ask` (cite the closing record), an arc confirm, or
  a dial set. The meeting *produces* the discharges; the floor goes quiet
  because the ask is genuinely answered, not dismissed.
- **The surface (his choice).** A **separate "Daily owner meeting"** perennial
  artifact, distinct from the #410 arc digest (bdo's pick).

## Concept-list (categorized · labelled)

**[FOLD] meeting.prep** — pure fold: rank owner-asks, apply the budget, shape
each as a Taster read; return structured agenda data (a doc-render and an
agent-agenda both consume it). Read-only.

**[DIAL] meeting.budget** — the admitted 30-min policy (per-ask minutes →
above-fold count). A setpoint record (`--by bdo`), never a code constant.

**[LINK] meeting.entry** — the mechanism bdo opens to join the live session.
The open fork (CTA-2).

**[NODE] meeting.agent** — the summoned meeting-node that runs the 30 minutes
off the prepared agenda and records his gestures.

**[HARDEN] perennial.find-by-surface** — the perennial finder keys off a
GitHub-side marker, not the local ack (closes RC1+RC2 for the meeting *and*
back-fixes the latent hole in `digest_drift`).

**[RETIRE] owner-ask-backlog rule** — turn off the per-report blind-create rule
(`reflect rule --kind owner-ask-backlog --off --by bdo`) once the meeting prep
is live. The asks still surface — through the one prepared meeting.

**[CLEANUP] dup-close** — close the 13 standing report-mirror `[owner-ask]`
issues through the **issue pen** (recorded act), each pointing at this
proposal. (#348 is a distinct target-misalignment ask — kept, not a dup.)

**[FLOOR] shame unchanged** — `owner_ask_shame.py` keeps screaming any ask no
surface has acked; "surfaced" now means "in the prepared meeting."

## CTAs (against the purpose)

- **CTA-1 — confirm the meeting shape** (prep → link → agent → 30 active min →
  recorded gestures, on a separate "Daily owner meeting" surface).
- **CTA-2 — pick the link mechanism** (served page · resumable session ·
  scheduled agent). The load-bearing fork; bdo's to steer.
- **CTA-3 — set the budget dial** (recommended: ~3 min/ask, ~10 above fold).
- **CTA-4 — sequencing** (authorized): close the 13 dupes now; retire the
  per-report rule when the meeting prep lands, so the close sticks. NB: the
  acks for these groups are now on main, so the beat stays quiet — the close
  holds even before the retire.

## Out of scope (named, not done)

Full temporal/outcome-pressure (OP3) re-ranking is a later increment; v0 rank
is freshness + unresolved + count. The general off-main-ack hardening across
*all* reflect kinds (not just the meeting) is its own arc — named here, built
later.
