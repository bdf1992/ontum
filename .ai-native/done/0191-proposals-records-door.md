# Done-line 0191 — The records door widens to proposals: a blueprint lands as a record

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the off-log gate (`loop.pr_audit` + the `pr.py audit` reach)
> treats a **proposals-only** PR the same way it already treats reports and
> done-lines (done-line 0172) — `.ai-native/proposals/` joins `RECORD_DIRS`,
> so `records_only(paths)` is True for a branch whose every changed path is a
> proposal `.md` (and nothing else), and `orphan_reason(..., records_only)`
> returns None for it. The door's teeth are unchanged: any non-record change —
> code, atom, log, config — still closes it, recomputed by the reach from the
> diff so it cannot be lied to. Proven by `tests/test_pr_audit.py` and
> **non-vacuous**: a proposals-only set is records-only, a proposal + a `.py`
> file is NOT, and the older record/teeth cases still pass. Backed by
> `atom.proposals-records-door.v0`; the suite is green (1571 tests OK).

## Why

bdo, 2026-06-23: *"land blueprints as proposal-records."* A proposal is design
captured ahead of a build — the bundle a non-trivial arc owes first ("blueprint
before build", #348/CTA-3). Unlike a report (a record of work *done*), a proposal
records work *proposed*, so it has no atom to carry — the build comes later. That
left a blueprint-only PR reading as an off-log orphan, stranding off main on the
proposal-landing friction (#355), where the foundation work the owner steers from
accreted off-trunk out of his sight. The fix is the same shape as the records door
it extends: one entry in `RECORD_DIRS`, narrow and proof-carrying — a proposal
cannot smuggle code, atoms, or log lines in under the exemption.
