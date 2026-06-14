# Done-line 0071 — The standing-surface projection: a registered surface's open work, ambient at every wake (the inbound twin of reflect)

# Done-line 0071 — The standing-surface projection: a registered surface's open work, ambient at every wake (the inbound twin of reflect)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a session opening in this repo is handed, ambiently, the open
> work a registered surface holds (issues + PRs for `github-issues`), and a
> *change* to that open set during the session ticks up **once** without
> re-spamming — built as a pub/sub PROJECTION over a registered surface, never
> glued to GitHub: (1) a pure, stdlib, network-free fold (`loop/standing.py`)
> turns a NORMALIZED snapshot of open items into the standing picture and the
> delta against a per-session baseline, naming no vendor; (2) the gh reach lives
> only in an adapter keyed by surface kind (reflect's `SURFACE_KINDS`
> discipline) — a registered surface with no adapter is named not guessed, no
> surface registered falls silent; (3) the hook wires `SessionStart` (full
> picture) + `UserPromptSubmit` (delta only), reuses reflect's
> `registered_surfaces`, is fail-open exit 0, throttles the poll so most turns
> stay network-free, and keeps the baseline in gitignored per-session nag state
> (never the log); and (4) `tests/test_standing.py` proves the projection is
> surface-agnostic (folds a snapshot with no gh), the delta is level-triggered
> (unchanged set → empty, a new/closed item → one delta, re-run after consuming
> → silent), and an unknown surface kind is named not guessed.

> **Non-example:** a hook that calls `gh issue list` in its own body (GitHub
> glued into the projection); a delta that re-prints the whole open set every
> prompt (spam, not tick-up); a fetch on every `UserPromptSubmit` (every turn
> taxed by the network); baseline kept in the log (it is session-ephemeral UI
> state, not truth); or "no surface registered" raising instead of going silent.

> **Pressure reduced:** the open work on bdo's steering surface stops being
> something a session learns only when a human pastes a screenshot — it arrives
> at every wake and its changes tick up, through the *same* registered-surface
> seam reflect already uses, so a second surface (a phone inbox, a local file)
> is a new adapter, never a new system.

> **Evidence expected:** `loop/standing.py` + `tests/test_standing.py` green +
> the hook wired in `.claude/settings.json` + a clean run showing the standing
> picture (1 issue, 8 PRs today) at `SessionStart` and silence on an unchanged
> re-poll, and a merge receipt.
