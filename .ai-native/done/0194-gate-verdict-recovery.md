# Done-line 0194 — Harden the value-gate verdict parser + add a saved-trace recovery tool

# Done-line {id} — Harden the value-gate verdict parser + add a saved-trace recovery tool

Written before code, per §9.4. When this line is met, stop.

A real opus panel stream ACCEPTED the diagram-canvas atom but its verdict was
lost: a stray non-JSON preamble on the headless child stdout (a corrupted
`.claude.json` warning) defeated `json.loads(raw)`, so the `claude -p` envelope
never unwrapped, leaving the verdict object double-escaped inside the envelope`s
`result` string where `_verdict_objects` could not decode it. `compile_panel`
counted a failed stream and escalated a clean 2-accept-1-amend, wasting $0.82.
bdo: fix the bug AND be able to recover from the bug without paid re-runs.

> **Done when:** (1) `_verdict_objects` recovers a well-formed verdict the mind
> really emitted even from an un-unwrapped envelope (it recurses into a string
> `result` key), while still yielding nothing when no structured verdict object
> exists (the unconfirmable/refuse path is preserved and never inferred from
> prose); (2) a `recover` subcommand on gate.py re-reads the SAVED gate-run
> traces for an atom id, re-parses each stream`s `parsed_text` with the hardened
> parser, re-runs `compile_panel`, and DRY-RUNS by default (prints the recovered
> per-stream verdicts and the recomputed decision, writes NOTHING to the log);
> (3) both carry non-vacuous §10 tests — the real opus `parsed_text` bytes as a
> fixture now yield `accept` and a no-verdict text still yields nothing (a
> constant `accept` fails the no-verdict case, a constant `none` fails the opus
> case), and the three saved diagram-canvas traces recover {opus: accept,
> haiku: accept, sonnet: amend}; (4) the full suite passes with nothing
> regressed.
