# Done-line 0117 — The phrasing backdoor: low-impact prose edits land without the atom mantra

Written before code, per §9.4. When this line is met, stop.

bdo, 2026-06-18: fixing a few pedantic English phrases ('on his phone' ->
'wherever he is') cost a branch, an atom, a value-gate summons, and a
spawned judge — the full work-particle mantra (§15/D-5) for a change the
machine never reads as logic. He named the fix: 'a backdoor route for
quick edit ... to edit semantic and pedantic phrases, not syntax or
schema', packaged the same way as whiteout (done-line 0064) and policy —
a session-usable pen with computable teeth that refuses the moment the
change leaves its low-impact bounds and names the escalation.

A phrasing edit is one the machine cannot branch on: human-readable prose
only. The door is safe precisely because it PROVES this rather than
trusting a label (the carbon-copy / whiteout shape) — and the same pure
proof the route runs is re-run by the off-log gate server-side, so a code
or schema change can never slip through the prose door.

> **Done when:** a pure, stdlib checker (loop/phrasing.py) decides per
> file whether an edit is PHRASING-ONLY and returns the reason when it is
> not — .md/.txt: body prose free, but a change to YAML frontmatter keys
> or the name/version values is NOT phrasing; .py: tokenized, every
> non-comment, non-string token byte-identical (only comment text and
> string/docstring contents may differ); .json: parsed, identical
> structure (keys, nesting, types) and identical non-string values, and
> only string values under a prose-field allowlist (horizon, value, arc,
> context, glue, story.text, briefing.*, description, headline, why_now,
> if_accepted, if_rejected, cost_of_wrong_call, mechanism) may differ —
> anything else REFUSES with the offending token/key/path named and the
> escalation stated (route it through the atom pipeline). A route pen
> verb runs that checker over the working-tree edit, and on a clean pass
> appends one marked phrasing admission (the files, their before/after
> content hashes, the reason, --by) so the act is on the log and
> recoverable, refusing to mark anything the checker rejects. The off-log
> gate gains a SECOND way to be backed (loop.pr_audit.orphan_reason): a
> branch whose every non-log changed file the checker proves phrasing-only
> is on-log without an atom — the fact gathered by pr.py audit (the
> reach with git, diffing base..head) and RE-VERIFIED by the same pure
> checker, so the client pen and the server CI inherit the door together
> and neither can be lied to. Proven by test (the §10 teeth): a wording
> edit across all three file kinds passes and the gate calls its branch
> backed with no atom; a one-token code change in a .py, a renamed JSON
> key, and a changed verdict/id value each REFUSE and name why, and the
> gate still calls that branch an off-log orphan. Scope held to v0: the
> three file kinds above; widening the prose-field allowlist or adding a
> file kind is a later increment, named not silently grown.
