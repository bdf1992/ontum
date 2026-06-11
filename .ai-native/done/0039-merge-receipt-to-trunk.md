# Done-line 0039 — the merge-node records its land on the trunk, or says loudly it didn't

Written before code, per §9.4. When this line is met, stop.

> **Done when:** every successful `pr.py land` leaves its merge receipt on
> the trunk (`origin/main`), where the digest and the next merge-node read
> it — pushed via a fresh worktree so a held/dirty `main` never blocks it;
> and on a push failure the land prints a loud `needs-you` (merged, but
> unrecorded — reconcile) instead of a false `done`. The three receipts the
> old code dropped to throwaway worktrees (#45/#52/#55) are reconciled onto
> the trunk. Tested: the receipt's authorization field and the torn-tail
> append.
