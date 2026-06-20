# Done-line 0130 — confirm --from-ref: an epic-introducing PR can confirm its own arc

> **Done when:** `pr.py confirm --from-ref <branch>` validates the arc's epic
> from the named ref when that epic lives only on an unlanded PR (not yet on the
> trunk), and refuses a ref that does not actually carry the epic — with a §10
> test proving the refusal, the full suite green, and the work atom-backed on
> the log so the PR is a landable unit.

## Why

Issue #245's triggering bug: `confirm` validates the epic against
`origin/main`, but an epic-INTRODUCING PR keeps its epic record only on the PR
branch. To confirm the arc you need the epic on main; to land the PR you need
the arc confirmed — deadlock. The arc-confirm gate's first real end-to-end use
(zero `arc_confirmed` admissions on main) caught a real bug — the §10 catch
epic.three-marks is about.

## The fix

`--from-ref REF` reads the epic file from the PR branch for validation only; the
confirmation admission still lands on the trunk (the epic record lands with its
own PR). The teeth: `epic_id_in_blob` refuses a ref that does not declare the
epic — --from-ref relocates where the epic is read, it is never a bypass, and
the epic is read from the branch, never invented.

## Not in scope (surfaced, not done here)

- Confirming epic.three-marks and epic.owner-harness is bdo's stamp (D-4).
- PR #244's wave-1 code is not atom-backed (its CI is red); landing it needs
  an atom on its branch — a separate piece, on a branch this session does not
  own.
- The broader environment-parity decision (#245: gh-in-env vs MCP-backed pens)
  stays bdo's.
