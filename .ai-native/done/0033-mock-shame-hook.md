# Done-line 0033 — the mock count screams, and the shame grows until a stage goes real

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a `UserPromptSubmit` hook names every still-mock pipeline
> stage into context on every turn, carries a tally of turns since the
> mock set last shrank, escalates its volume as that tally grows, and
> resets to silence the moment a stage is admitted real — with a test
> that proves the tally rises while mocks sit, falls when one goes real,
> and that the hook fails open (exit 0) on a broken log.
