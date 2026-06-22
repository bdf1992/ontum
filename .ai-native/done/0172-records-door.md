# Done-line 0172 — The records door: a records-only PR lands without an atom

# Done-line 0172 — The records door: a records-only PR lands without an atom

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the off-log gate (`loop.pr_audit` + the `pr.py audit` reach)
> recognizes a THIRD way for a PR to be backed — a **records-only** PR, whose
> every changed path is a report or done-line (`.ai-native/reports|done/*.md`)
> and nothing else — and exempts it from needing an atom, the same shape as the
> phrasing door (done-line 0117). `pr_audit.records_only(paths)` is a pure check
> (all paths are reports/done `.md`, non-empty); `orphan_reason(..., records_only)`
> returns None when it holds; `pr.py audit` recomputes it from the diff so it
> cannot be lied to (any non-record change — code, atom, log, config — closes the
> door and the branch falls back to needing an atom). Proven by
> `tests/test_pr_audit.py` (joined to the suite) and **non-vacuous**: a
> records-only set is backed, a records+code / records+atom / records+log set is
> NOT, an empty set is not records-only, and the audit labels a clean records PR
> `backed_by: ["records-door"]` — the test fails if the door lets a code change
> through. Backed by `atom.records-door.v0` with an independent value-gate accept;
> the suite is green.

## Why

A session report is a record OF work, not a work-particle — it carries no atom.
Reports normally bundle into their session's work PR (report 0116 landed via
#373, 0115 via #351), but a report written AFTER its work already landed cannot
bundle retroactively and would strand off main forever: the off-log gate refuses
it ("PR carries an atom on the log" fails), yet the report belongs on main as the
durable record. The merge-node hit exactly this on #417 and #427. bdo's call: fix
the rule — exempt records-only PRs the way prose-only PRs are exempted, narrow
and proof-carrying. The door is deliberately tight: only reports/done-lines, only
`.md`, nothing else — a report PR cannot smuggle code, atoms, or fabricated log
lines in under the exemption.
