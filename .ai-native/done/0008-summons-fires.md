# Done-line 0008 — the summons fires: sessions wired in as virtual nodes

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the open summons are a pure read-only fold
> (`loop/summon.py`): every atom parked awaiting an admitted-real node
> that isn't the owner's stamp renders as a briefing — who is summoned,
> at which seam, the terminal verdict set, and the one judge line that
> clears it — and `.claude/settings.json` (config-as-code, this repo's
> first hook wiring) injects that briefing into any session that starts
> or prompts here (§8: hooks are how summoned nodes fire, D-10); the
> hook never writes, never judges, never blocks the owner (exit 0
> always — I-3, D-2); and tests prove: an awaiting atom appears, the
> owner's stamp never appears as a session summons, a settled field
> summons nobody, hook mode survives garbage stdin and a missing root,
> and rendering leaves the log bytes untouched.

Context: every report since 0005 names the same gap — "summoning
hand-routed, not yet wired to hooks §8." An atom parks awaiting
`value-gate.claude.v1` and nothing fires; a human notices, starts a
session, pastes context by hand. This wires the trigger half of D-10:
the session that blinks in *is* the virtual node — the hook hands it
its summons, it judges through the one pen (`loop.node judge`), and it
dissolves. The surface holds no judgement and adds no second write
path; the stamp queue stays the owner's inbox, not a session's summons
(D-4).
