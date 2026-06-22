# Done-line 0183 — The prepared owner-meeting agenda: ranked, budget-capped owner-asks as a single fold

# Done-line — the prepared owner-meeting agenda

bdo, 2026-06-22: *"I need a digest over these owner asks, at most a 30-minute
daily meeting"* — refined to a prepared, time-boxed meeting an agent runs for
him. This line covers the **deterministic prep only** (the agenda); the live
link/agent and the perennial surface are later increments
(.ai-native/proposals/owner-ask-digest.proposal.md, CTA-1/2).

> **Done when:** `loop/meeting.py` is a pure, read-only, stdlib fold that
> produces the prepared agenda: the live owner-asks (every `owner_ask_groups`
> entry not discharged and not baselined), **ranked** (report freshness, then
> item-count), and **budget-capped** by an admitted `meeting_budget` setpoint
> (read from the log, default-safe at 3 min/ask over a 30-min meeting -> 10
> above the fold), splitting today/`s agenda from a deferred count. It renders
> a `Daily owner meeting` agenda to stdout and emits `--json`. A budget is
> admitted through one pen verb signed `--by`. `tests/test_meeting.py` proves
> the §10 teeth are non-vacuous: a fresher report outranks an older one, the
> budget cut actually drops the over-budget tail to the deferred count, and a
> discharged ask is absent from the agenda. The suite stays green.
