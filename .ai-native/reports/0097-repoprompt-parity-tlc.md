# Report 0097 — repoprompt-parity TLC: parity teeth that prove the claim

bdo: 'repoprompt-parity might need some TLC repair and work against it.' Both halves done.

## What was wrong (the repair)
`epic.repoprompt-parity`'s wave-1 boundedness parity matrix (`loop/parity.py`) validated clean and its suite was green — but its §10 teeth were soft. `validate()` proved only that a `have` row's cited *file exists*, never that the file does the claimed thing. One row stood on a false claim: `multi-root workspaces -> have -> field.py --all`, noted as folding 'ontum + odysseus + holonsearch'. In fact `field.py --all` composes every *arc within ontum* into one ladder-graph and reaches none of the three sibling working dirs — `field.py` contains zero `odysseus`/`holonsearch` references. A `have` citing a real file with a false claim is a ghost-in-spirit the file-exists check cannot see — exactly the locally-fine record §10 says a gate must learn to refuse.

## What I built (work against it)
- **Sharper tooth:** every `have` row now carries an `evidence` substring its cited file must contain; `_resolves`/`validate` refuse a `have` whose evidence is absent (or missing), with a distinct ghost-in-spirit message. The grip rule moved from *existence* to *claim*.
- **The false row, re-verdicted honestly:** multi-root flips `have -> build`, citing a new genuine gap `atom.multi-root-fold.v0`, added to the epic as a wave-2 piece (a cross-repo working-set fold; DON'T double-build `field.py` — reuse its per-repo ladder). Matrix is now 2 have, 7 build, 2 dont-double-build, every citation honest.
- **Non-vacuous teeth-tests:** an evidence-free `have` and a present-file-but-absent-evidence `have` are both caught (the latter reconstructs the exact multi-root shape and asserts the message). Positive control now carries evidence. `loop/CLAUDE.md` records the tooth.

## End-state
- Done-line **0132**; atom **atom.parity-claim-teeth.v0**, announced and independently judged **accept** by `value-gate.claude.v1` (receipt **rcp.34c707ab2c00** — the judge ran the parity fold + full suite and verified `field.py`'s missing refs before accepting). The independent judge served as the independent review of substance (low-blast-radius, additive, read-only change).
- PR **#274** open on `claude/repoprompt-parity-wave2`; `epic.repoprompt-parity` is **CONFIRMED** (adm.e96e5650de81), so the PR is merge-node-eligible once CI is green. Not landed by me — left to the merge-node.
- `python -m loop.parity` green; full parity suite (11 tests) green.

## needs-you
None. The repair and one wave-2 requirement are on the record; landing is the merge-node's.

## Surfaced for the next session (not a block)
- **Pipeline clog:** orchestrate is jammed — 24 inflight, 21 atoms awaiting `value-confirm.claude.v1` (the owner-stamp/confirm seam) over the inflight cap, so new atoms can't be born through the loop (I announced mine directly via the sanctioned make_event/append_line path). Running `python -m loop.orchestrate` in a worktree also writes mock-gate receipts for the whole inflight set into that worktree's logs — I restored the three log files and re-announced only my atom; a future session driving orchestrate must watch for the same pollution.
- **Soft-tooth pattern beyond parity:** any 'cites a file' check that doesn't verify the file does the thing has this same blind spot (census 'wired', the term-economy 'have'-equivalents). The evidence-substring shape here is a reusable fix.
