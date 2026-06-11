# Report 0039 — Merge authority virtual node repair

## End-state

Repaired the live merge-authority wording found in report 0038: current contracts, fence messages, branch ritual text, overnight-loop summary, merge-node ritual, and `loop.merge` output now say bdo confirms arcs while an independent merge-node virtual node lands confirmed PRs through the PR pen.

## What changed

- `AGENTS.md` and `CONTRIBUTING.md` now describe D-4 as owner authorization plus merge-node landing, not manual owner merge.
- `fence/policy.py` was updated and `.codex/rules/ontum.rules` regenerated so raw `git push`/`gh pr merge` refusals point to the merge-node model.
- `loop.merge` no longer prints the stale pre-admission land-is-yours message; it reports the current confirmation/merge-node split.
- Branch/merge/overnight ritual docs were tightened so non-draft PRs are landable after arc confirmation, and the merge-node skill matches the actual `pr.py land` behavior around branch cleanup.
- `tests/test_pr_ritual.py` was updated for the new raw-merge refusal wording.

## Verification

- `python -m unittest tests.test_pr_ritual tests.test_merge tests.test_merge_node tests.test_merge_land -v` — 92 tests passed.
- `python -m unittest discover -s tests -v` — 413 tests passed.
- `codex execpolicy check --pretty --rules .codex\rules\ontum.rules -- gh pr merge 12 --squash` — forbidden with the corrected merge-node justification.

## Needs-you

None.
