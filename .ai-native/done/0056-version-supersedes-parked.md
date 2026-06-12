# Done-line 0056 — A superseded atom version is history, not a live parked piece

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the loop's gap backlog and the Field's story rung both stop
> calling a *superseded* atom version a live parked piece. An atom id parses as
> `<stem>.v<N>`; a parked version is no longer live work the moment a higher-`N`
> sibling of the same stem exists on disk (creating a new version *is* the amend
> — identity is content hash, so old receipts "stay valid history but no longer
> apply", architecture §"Identity is content hash"). The rule is one pure
> function over atom ids, hit directly by the §10 pair: the real divergence —
> `atom.field-topology.v0` parked while `.v1` is confirmed — must *not* surface
> as a gap or read "parked" in the field (it is history), **and** a still-highest
> parked version with no successor (the single-version case the fold serves
> today) must *still* surface, so the fix does not silence a genuinely-held
> piece. History is untouched: v0's `missed` receipt stays on the log; only what
> counts as *live* work changes.

## Out of scope, named

- **Retiring v0 from disk or the log.** The fix changes only what *surfaces* as
  live work; the parked receipt stays as history (the repo never erases
  questions). v0's file remains as the record of the claim/delivery catch.
- **A new admission or record type.** Supersession is read from the version
  suffix already on disk — no `node_real`, no superseded-admission. If bdo later
  wants an explicit retirement record, that is his own line.
- **Cross-stem or semantic supersession.** Only same-stem `.vN` ordering counts.
  An atom that replaces another under a different slug is not version-superseded
  and still surfaces until it terminates on its own.
