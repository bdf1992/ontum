# Report 0113 — Activity accounting: organ 1 of the shared gateway (data-practices register)

## What landed

**PR #339** (`claude/activity-accounting-register`), **done-line 0143**, atom
`atom.activity-accounting.v0` (serves `epic.substrate`), independent value-gate
**accept** `rcp.5927d8904843`, full suite **green at 1110**.

bdo's direction (2026-06-20): *"account for all activity, even Claude hooks like
session start and tool call, and start auditing their data collection and usage
for a shared gateway."* Asked which first organ, he chose **"both, register
first."** This is organ 1.

- `.claude/activity-register.json` — the declared data-practices register: per
  wired hook, what it **collects**, what it **uses** that for, where the data
  **goes**, and whether its firing is **witnessed**.
- `loop/activity.py` — a pure read-only fold (sibling of `census`/`gaps`/`heal`,
  stdlib, no network, no git) that derives live wiring from
  `.claude/settings.json` and reconciles the register against it. §10 teeth:
  an **undeclared collector** (a wired hook accounted nowhere) and a **ghost**
  (a declared entry no longer wired) both refuse; codex entries verified vs
  `.codex/hooks.json` when present.
- `tests/test_activity.py` (12, green) — proves the committed register is honest
  and the check is not vacuous.

**The teeth proved themselves on real drift.** Merging `origin/main` into this
branch immediately surfaced the just-landed session-lifecycle hooks
(`session_register`, `idle_reminder`) as undeclared collectors and the retired
`continue_beat` as a ghost — the organ catching live, landed change — and the
register was reconciled to match (now 15 accounted, 13 unwitnessed).

## The diagnosis (for the record)

The harness's own hooks are the gateway's sensors, but their own data collection
is the one activity the gateway never accounts for: 15 hooks collect command
strings, spawn prompts, full raw stdin/argv/env (the codex probe) and gh poll
results, mostly **silently into gitignored sinks**, and most never record that
they fired. This is the witness-fold `git-gh-gateway.proposal.md` deferred,
widened from git/gh reads to all activity, keeping the asymmetry: reads get
witnessed, not authorized.

## needs-you

1. **Arc naming (D-4).** Is "shared gateway" its own epic, or does this
   accounting ride `epic.owner-harness`/`epic.substrate`? I landed organ 1 under
   `epic.substrate` (the self-sensing-substrate family) as the honest existing
   home; the wider arc is yours to name.
2. **Go for organ 2 — the runtime witness.** Every hook firing → a first-class
   attributed receipt (who fired, what it collected, where it went), the sibling
   of `tool-use.jsonl` the proposal deferred. Built only on your go; "register
   first" means it follows this organ's landing.
3. PR #339 is merge-node eligible after arc confirmation; trust-rail issue #326
   (the first, pre-merge gate-launch that failed on the old rail) can be closed —
   the re-run on the merged-in fixed rail (#331) produced the accept.

## End-state

`report` — organ 1 of the shared-gateway activity accounting is built, green,
independently accepted, and PR'd (#339); the teeth already caught real landed
drift; organ 2 and the arc naming are bdo's.
