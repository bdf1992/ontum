# Done-line 0030 — A surface kind without a translator refuses to fit

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the reflection service can no longer aim the wrong
> tongue at a surface — surface **kinds** join the kinds-table pattern
> (`SURFACE_KINDS` in `loop/reflect.py`, beside `RULE_KINDS`): the
> `register` CLI refuses a kind no translator speaks (`needs-you`,
> naming the table), `auto_plan` skips — and `status` names —
> historically-admitted surfaces whose kind is untranslatable; and the
> reflector pen dispatches acts through a **translator table keyed by
> kind** (`github-issues` its one entry today, the gh-issue verbs
> behind it), refusing `apply` toward a kind it has no translator for
> instead of speaking gh at it; a test pins the pen's translator keys
> to `SURFACE_KINDS` so the table and the fold can't drift apart.

## Direction (bdo, chat, 2026-06-10)

Queue item 5 after stamping PR #26: "Fix reflection surface-kind
drift: either refuse non-github-issues kinds or add translator
dispatch." Both, in the shape the repo already uses for rule kinds:
dispatch is the extension point, refusal is what happens off the table.
The §10 case this closes: `register --kind slack --address ...` was
accepted, and the pen would have run `gh issue create` against that
address — two locally-fine records, no seam noticing.

## Out of scope, named

- **A second translator** (slack, linear, …) — a new translator is its
  own stamped increment; this done-line builds the socket, not a plug.
