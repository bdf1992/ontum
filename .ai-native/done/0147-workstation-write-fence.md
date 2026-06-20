# Done-line 0147 — The workstation write-fence

# Done when

> **Done when:** a Write/Edit/MultiEdit/NotebookEdit whose target path lives in a git worktree OTHER than the one the session stands in (its payload cwd) — a sibling worktree or the primary tree (the viewport) of the SAME repo — is REFUSED with exit 2 and the paved path, while a write inside the session's own worktree, or to a path in no git tree (temp, memory) or an unrelated repo, is allowed. Proven by a §10 test that runs the live guard with the same target path judged from two different session cwds: foreign (denied) and own (allowed).

## Why

Tooth #1 (the workstation fence, done-line 0145) stopped a worker FLIPPING the viewport's HEAD via git. The other half of bdo's rule — a worker edits only its OWN workstation — is the FILE dimension: a worker writing or editing files into another worker's worktree or into the viewport's working tree. Seen live (a concurrent session's files appeared inside another session's worktree path) and it is how the viewport gets dirtied even when its HEAD is held. write_guard governs only new-file creation under the project root; a write into a SIBLING worktree falls outside that root and was allowed. This closes the filesystem-path dimension.

## The rule

The session's own workstation = the worktree containing its payload cwd. A write whose target resolves into a different worktree of the same repo (same git common-dir, different toplevel) is foreign and refused. Reads are never affected (this guards only the write/edit tools). The judge is the SESSION's payload cwd, never the process cwd — the hook runs from the project dir for every session.

## The paved path the refusal names

Write inside your own worktree. To move something to another tree, land it through the loop (PR + merge-node) so it arrives on main and every worktree fast-forwards to it — never by reaching into another bench.
