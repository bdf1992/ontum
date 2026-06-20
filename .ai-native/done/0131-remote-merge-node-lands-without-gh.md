# Done-line 0131 — The merge-node lands a confirmed-arc PR from a gh-less remote session

Written before code, per §9.4. When this line is met, stop.

bdo asked (2026-06-19, the ask surface): the landing logjam — confirmed,
green, atom-backed PRs pile up because the merge-node's `land` verb shells
out to `gh`, and the web/remote execution environment has no `gh` and no
REST token in-process (git reaches origin only through a local auth proxy).
He chose: build the gh-less land path now. The honest shape, found at the
seam: a standalone pen *cannot* perform the merge mutation itself here (no
token), but it owns the two parts that must not leave the loop — the **land
decision** (the guards) and the **merge receipt** (the record on the trunk).
Only the merge mutation needs the auth the agent holds (the GitHub MCP tool).
So the gh-less land splits the pen's pure halves from the transport: the
agent's authenticated merge slots between the pen's decision and its receipt,
and the identical `land_refusal` guards still gate the trunk (D-4, done-line
0049 — the merge-node still lands only a confirmed arc, as an admitted node,
and never its own author's PR).

> **Done when:** `pr.py land` accepts a `--via-api PATH` mode that needs no
> `gh`: a pure `info_from_api(api_pr, check_runs)` adapter normalizes the
> GitHub REST/MCP PR shape into the exact `info` dict `land_refusal` already
> consumes (state-cased, draft, base/head, body/title, the check rollup, and
> `mergeable_state: dirty -> CONFLICTING`), so the *same* guards decide; the
> decide phase refuses anything `land_refusal` refuses and otherwise computes
> the PR's `landed_atoms` (the D-13 write-through) and prints the
> merge-then-record instruction without mutating anything; the record phase
> (`--record`) refuses to write a `landed` receipt unless the supplied
> post-merge blob shows the PR actually merged, then builds the receipt with
> the existing `_merge_receipt` (carrying the landed atoms) and pushes it to
> the trunk through the existing pure-git `_push_receipt_to_trunk` (no `gh`);
> and the §10 teeth in `tests/test_merge_land.py` pin that the adapter cannot
> launder a non-landable PR — a `dirty` mergeable_state still refuses
> (CONFLICTING), a failing/pending check still refuses (not green), and an
> already-merged blob is refused by the decide phase (only an OPEN PR is
> decided). Proof on the record: PR #246 (epic.owner-harness, confirmed)
> landed to main through this path with rcp.merge.246 on the trunk.
